"""
annotation_model.py — Data backbone for the Worldographer annotation GUI.

Wraps the parsed annotation dict, exposes edit operations, serializes back
to the .md format, and manages render/save lifecycle state.

Consumed by worldographer_editor.py.  Does NOT import any PySide6 widgets so
it can be used headlessly (e.g. from a test or CLI).
"""
from __future__ import annotations
import os
import re
import subprocess
import sys
from typing import Optional

# ---------------------------------------------------------------------------
# We import from sibling modules.  Add the package directory to sys.path so
# this works whether invoked from the package folder or somewhere else.
# ---------------------------------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from wxx_annotations import (
    parse,
    scaffold,
    classify_shape_tag,
    stroke_to_feet,
    _shape_endpoint_cells,
    cells_adjacent_or_equal,
    find_stitch_candidates,
    world_to_hex,
)
from wxx_to_svg import load_wxx, parse_wxx


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fmt_cell(v) -> str:
    """Format a cell (tuple or string) back to `(col, row)` notation."""
    if isinstance(v, tuple):
        return f'({v[0]}, {v[1]})'
    return str(v) if v else ''


def _serialize_conditions(conditions: dict) -> list[str]:
    """Yield annotation-format condition lines for a road/river entry."""
    lines = []
    for cell, kvs in sorted(conditions.items(), key=lambda kv: kv[0]):
        parts = []
        for k, v in kvs.items():
            if k == 'ref':
                refs = v if isinstance(v, list) else [v]
                for r in refs:
                    parts.append(f'ref={r}')
            else:
                parts.append(f'{k}={v}')
        if parts:
            lines.append(f'  {_fmt_cell(cell)}: {", ".join(parts)}')
    return lines


def _parse_conditions_text(text: str) -> dict:
    """Re-parse a raw conditions block (from a QPlainTextEdit) back to dict."""
    conditions = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        m = re.match(r'(\(\s*-?\d+\s*,\s*-?\d+\s*\))\s*:\s*(.+)', stripped)
        if not m:
            continue
        cell_m = re.match(r'\(\s*(-?\d+)\s*,\s*(-?\d+)\s*\)', m.group(1))
        if not cell_m:
            continue
        cell = (int(cell_m.group(1)), int(cell_m.group(2)))
        kvs: dict = {}
        for pair in m.group(2).split(','):
            if '=' in pair:
                pk, pv = pair.split('=', 1)
                pk, pv = pk.strip(), pv.strip()
                if pk == 'ref':
                    kvs.setdefault('ref', []).append(pv)
                else:
                    kvs[pk] = pv
        if cell in conditions:
            for pk, pv in kvs.items():
                if pk == 'ref':
                    conditions[cell].setdefault('ref', []).extend(pv if isinstance(pv, list) else [pv])
                else:
                    conditions[cell][pk] = pv
        else:
            conditions[cell] = kvs
    return conditions


def _count_todos(data: dict) -> int:
    """Count fields still holding a TODO placeholder across all sections."""
    count = 0
    PLACEHOLDER = {'TODO', '', 'TODO  # unspecified surface', 'TODO  # unspecified width, unknown current'}

    def _is_todo(v):
        if v is None:
            return True
        s = str(v).strip()
        return s.upper() == 'TODO' or s.startswith('TODO') or '##' in s

    for section in ('roads', 'rivers'):
        for entry in data.get(section, {}).values():
            if _is_todo(entry.get('name')):
                count += 1
            flow = entry.get('flow', {})
            if _is_todo(flow.get('origin')):
                count += 1
            if _is_todo(flow.get('termination')):
                count += 1

    for poi in data.get('pois', []):
        if _is_todo(poi.get('name')):
            count += 1
        if _is_todo(poi.get('description')):
            count += 1

    for wall in data.get('walls', []):
        if _is_todo(wall.get('name')):
            count += 1

    for district in data.get('districts', []):
        if _is_todo(district.get('description')):
            count += 1

    return count


# ---------------------------------------------------------------------------
# Main model class
# ---------------------------------------------------------------------------

class AnnotationModel:
    """Manages load / edit / save / render for a single .wxx + .annotations.md pair.

    Not a QObject — avoids PySide6 dependency in this module.  Callers that
    need signals should wrap it in a thin QObject adapter.
    """

    def __init__(self):
        self.wxx_path: Optional[str] = None
        self.annot_path: Optional[str] = None
        self.svg_path: Optional[str] = None
        self.wmap = None          # WxxMap parsed from .wxx
        self.data: dict = {}      # parsed annotation dict
        self._dirty: bool = False

    # ------------------------------------------------------------------
    # Load / save
    # ------------------------------------------------------------------

    def load(self, wxx_path: str,
             svg_path: Optional[str] = None) -> list[str]:
        """Load a .wxx file and its sidecar .annotations.md.

        svg_path optionally overrides where the rendered SVG will be written
        (and from which the annotation filename is derived).  If omitted,
        a cleaned variant of the wxx filename is used (spaces → underscores,
        lowercased).

        If the annotation file doesn't exist, a scaffold is generated and
        written automatically.

        Returns a list of warning strings (empty if all clear).
        """
        self.wxx_path = wxx_path
        wxx_dir = os.path.dirname(wxx_path)
        wxx_base = os.path.splitext(os.path.basename(wxx_path))[0]

        if svg_path:
            self.svg_path = svg_path
        else:
            # Clean the base name for a sane default SVG path
            clean_base = wxx_base.lower().replace(' ', '_')
            self.svg_path = os.path.join(wxx_dir, clean_base + '.svg')

        self.annot_path = os.path.splitext(self.svg_path)[0] + '.annotations.md'

        # If the derived annotation path doesn't exist, look for a matching
        # *.annotations.md in the same directory.  Matching rules (best first):
        #   1. Exact match on clean_base
        #   2. Annotation base starts with clean_base (e.g. "silberbach_city_map" when clean="silberbach_city")
        #   3. Annotation base contains clean_base
        #   4. Single candidate fallback
        if not os.path.exists(self.annot_path):
            clean_base = os.path.splitext(os.path.basename(self.svg_path))[0]
            candidates = [
                f for f in os.listdir(wxx_dir)
                if f.endswith('.annotations.md')
            ]
            best = None
            for f in candidates:
                base_f = f.replace('.annotations.md', '').lower()
                if base_f == clean_base.lower():
                    best = f; break
            if best is None:
                for f in candidates:
                    base_f = f.replace('.annotations.md', '').lower()
                    if base_f.startswith(clean_base.lower()):
                        best = f; break
            if best is None:
                for f in candidates:
                    base_f = f.replace('.annotations.md', '').lower()
                    if clean_base.lower() in base_f:
                        best = f; break
            if best is None and len(candidates) == 1:
                best = candidates[0]
            if best:
                self.annot_path = os.path.join(wxx_dir, best)
                self.svg_path = self.annot_path.replace('.annotations.md', '.svg')

        xml = load_wxx(wxx_path)
        self.wmap = parse_wxx(xml)

        warnings = []
        if not os.path.exists(self.annot_path):
            # Generate scaffold
            src_name = os.path.basename(wxx_path)
            scaffold_text = scaffold(self.wmap, src_name)
            with open(self.annot_path, 'w', encoding='utf-8') as fh:
                fh.write(scaffold_text)
            warnings.append(f'Scaffolded new annotation file: {self.annot_path}')
            annot_text = scaffold_text
        else:
            with open(self.annot_path, 'r', encoding='utf-8') as fh:
                annot_text = fh.read()

        self.data = parse(annot_text)
        # parse() skips POIs with placeholder cells; re-add any that have a
        # real name (i.e., the user named them but hasn't placed them yet)
        self._supplement_named_pois(annot_text)
        self._dirty = False
        return warnings

    def _supplement_named_pois(self, annot_text: str) -> None:
        """Re-add POIs that parse() skipped because they had placeholder cells
        but a real (non-default) name.  This preserves user-named POIs that
        haven't been given a map coordinate yet.
        """
        existing_ids = {p.get('id', '') for p in self.data.get('pois', [])}
        # Find all ### poi#N subsections in the raw text
        import re as _re
        for m in _re.finditer(
            r'^### (poi#\w+)\s*\n(.*?)(?=^###|\Z)',
            annot_text, _re.MULTILINE | _re.DOTALL
        ):
            poi_id = m.group(1).strip()
            if poi_id in existing_ids:
                continue
            body = m.group(2)
            entry: dict = {'id': poi_id}
            is_template = False
            for line in body.splitlines():
                s = line.strip()
                if 'TEMPLATE' in s and '===' in s:
                    is_template = True
                    continue
                if not s or s.startswith('#'):
                    continue
                if ':' in s:
                    k, v = s.split(':', 1)
                    entry[k.strip()] = v.strip()
            name = entry.get('name', '')
            # Only keep if user gave it a real name (not the default template)
            if is_template and name in ('', 'Untitled POI'):
                continue
            if name in ('', 'Untitled POI'):
                continue
            self.data.setdefault('pois', []).append(entry)

    def save(self) -> None:
        """Serialize the current data dict back to the annotation .md file."""
        if not self.annot_path:
            raise RuntimeError('No annotation path set — call load() first.')
        text = self.serialize()
        with open(self.annot_path, 'w', encoding='utf-8') as fh:
            fh.write(text)
        self._dirty = False

    @property
    def is_dirty(self) -> bool:
        return self._dirty

    def mark_dirty(self) -> None:
        self._dirty = True

    # ------------------------------------------------------------------
    # Render
    # ------------------------------------------------------------------

    def render(self) -> tuple[bool, str]:
        """Render the .wxx to SVG via wxx_to_svg.

        Tries a direct in-process call first (works in PyInstaller bundles
        where sys.executable is not a plain Python interpreter).  Falls back
        to a subprocess for development/CLI use.

        Returns (success: bool, output: str).
        """
        if not self.wxx_path or not self.svg_path:
            return False, 'No .wxx file loaded.'

        # --- preferred: direct call (no subprocess, works in frozen bundles) ---
        try:
            from wxx_to_svg import render_map
            return render_map(self.wxx_path, self.svg_path)
        except ImportError:
            pass
        except Exception as exc:
            return False, f'Render failed: {exc}'

        # --- fallback: subprocess (development / script mode) ---
        script = os.path.join(_HERE, 'wxx_to_svg.py')
        cmd = [sys.executable, script, self.wxx_path, self.svg_path]
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
            )
            output = result.stdout + result.stderr
            return result.returncode == 0, output
        except subprocess.TimeoutExpired:
            return False, 'Render timed out after 60 s.'
        except Exception as exc:
            return False, f'Render failed: {exc}'

    # ------------------------------------------------------------------
    # River operations
    # ------------------------------------------------------------------

    def get_river_join_candidates(self, river_idx: int) -> list[tuple[int, str]]:
        """Return other rivers that share an endpoint with river_idx.

        Returns [(other_idx, description_str), ...].
        river_idx is the 1-based ordinal key used in self.data['rivers'].
        """
        if not self.wmap:
            return []

        orient = self.wmap.hex_orientation
        rivers_data = self.data.get('rivers', {})
        all_ordinals = sorted(rivers_data.keys())

        # Map ordinal → wmap.shapes index (shape order matches scaffold order)
        # River shapes are those classified as 'river'
        river_shape_idxs = [
            i for i, s in enumerate(self.wmap.shapes)
            if classify_shape_tag(s.tag, getattr(s, 'shape_type', 'Path')) == 'river'
        ]
        # ordinal 1 → river_shape_idxs[0], ordinal 2 → river_shape_idxs[1], etc.
        def _shape_for_ordinal(ord_key: int):
            idx_in_list = all_ordinals.index(ord_key)
            if idx_in_list < len(river_shape_idxs):
                return self.wmap.shapes[river_shape_idxs[idx_in_list]]
            return None

        my_shape = _shape_for_ordinal(river_idx)
        if my_shape is None:
            return []
        my_first, my_last = _shape_endpoint_cells(my_shape, orient)
        if my_first is None:
            return []

        candidates = []
        for other_ord in all_ordinals:
            if other_ord == river_idx:
                continue
            other_shape = _shape_for_ordinal(other_ord)
            if other_shape is None:
                continue
            o_first, o_last = _shape_endpoint_cells(other_shape, orient)
            if o_first is None:
                continue
            # Check if any endpoint pair meets
            for ae in (my_first, my_last):
                for be in (o_first, o_last):
                    if cells_adjacent_or_equal(ae, be):
                        other_name = rivers_data[other_ord].get('name', f'river {other_ord}')
                        desc = (
                            f'river {other_ord}: {other_name}  '
                            f'[meets at {_fmt_cell(ae)} ↔ {_fmt_cell(be)}]'
                        )
                        candidates.append((other_ord, desc))
                        break
                else:
                    continue
                break

        return candidates

    def join_rivers(self, a_idx: int, b_idx: int, reverse_b: bool = False) -> None:
        """Set stitch_with on river a to point at river b.

        If reverse_b is True, set direction: reverse on river b.
        Marks the model as dirty.
        """
        rivers = self.data.get('rivers', {})
        if a_idx not in rivers or b_idx not in rivers:
            raise KeyError(f'River indices {a_idx} and/or {b_idx} not in annotation data.')
        rivers[a_idx].setdefault('flow', {})['stitch_with'] = f'river {b_idx}'
        if reverse_b:
            rivers[b_idx].setdefault('flow', {})['direction'] = 'reverse'
        self._dirty = True

    def flip_river(self, river_idx: int) -> None:
        """Toggle the direction of a river entry between forward and reverse."""
        rivers = self.data.get('rivers', {})
        if river_idx not in rivers:
            return
        flow = rivers[river_idx].setdefault('flow', {})
        current = flow.get('direction', 'forward')
        flow['direction'] = 'reverse' if current == 'forward' else 'forward'
        self._dirty = True

    # ------------------------------------------------------------------
    # Stats
    # ------------------------------------------------------------------

    def get_todo_count(self) -> int:
        return _count_todos(self.data)

    # ------------------------------------------------------------------
    # Serializer
    # ------------------------------------------------------------------

    def serialize(self) -> str:
        """Rebuild the annotation .md text from self.data.

        Produces output that parse() can round-trip back to the same dict.
        """
        data = self.data
        wxx_name = os.path.basename(self.wxx_path) if self.wxx_path else 'map'
        annot_name = os.path.basename(self.annot_path) if self.annot_path else wxx_name
        base_name = annot_name.replace('.annotations.md', '')

        from datetime import date
        out = []

        # --- Frontmatter ---
        out.append('---')
        out.append(f'name: {base_name} Annotations')
        out.append('type: location')
        out.append('keywords: [map, annotations]')
        out.append(f'description: Authorial overlay for {wxx_name}.')
        out.append(f'generated: {date.today().isoformat()}')
        out.append('---')
        out.append('')
        out.append(f'# Annotations for {wxx_name}')
        out.append('')
        out.append('Edit this file to add real names, base conditions, intent notes, POIs,')
        out.append('and other authored content. The renderer merges this into the .svg')
        out.append('description block on the next render.')
        out.append('')

        # --- Project ---
        out.append('## Project')
        out.append('')
        out.append('# Pick the project styling for this map. Options: default, aethelmark.')
        out.append('# Defaults to `default` if absent.')
        out.append(f'project: {data.get("project", "default")}')
        out.append('')

        # --- Intent ---
        out.append('## Intent')
        out.append('')
        out.append('### Format')
        out.append('# Operational hints for tools and AI consumers.')
        for line in data.get('intent_format', []):
            out.append(f'- {line}')
        if not data.get('intent_format'):
            out.append('- Description self-contained in the comment block. Edit this annotation file,')
            out.append('  not the .svg comment block directly (changes will be overwritten on re-render).')
            out.append('- Re-render via `python wxx_to_svg.py <input.wxx> <output.svg>`.')
        out.append('')
        out.append('### Narrative')
        out.append('# Authorial design notes — surfaced to the user when this map is loaded.')
        for line in data.get('intent_narrative', []):
            out.append(f'- {line}')
        if not data.get('intent_narrative'):
            out.append('- TODO: describe the map\'s intended use (campaign hex-crawl, regional reference, etc.)')
            out.append('- TODO: note any settlements with deliberate design pressures.')
        out.append('')

        # --- Elevation Overrides ---
        overrides = data.get('elevation_overrides', {})
        out.append('## Elevation Overrides')
        out.append('')
        out.append('# Per-cell elevation overrides for hexes that meaningfully differ from')
        out.append('# their terrain default. Format: `(col, row): elevation_m`. Optional.')
        out.append('overrides:')
        if overrides:
            for cell, elev in overrides.items():
                out.append(f'  {_fmt_cell(cell)}: {elev}')
        else:
            out.append('  # (15, 12): 1800m   # example: ridge fortress site')
        out.append('')

        # --- Roads ---
        roads = data.get('roads', {})
        if roads:
            out.append('## Roads')
            out.append('')
            for ordinal in sorted(roads.keys()):
                entry = roads[ordinal]
                out.append(f'### road {ordinal}')
                out.append(f'name: {entry.get("name", "TODO")}')
                out.append(f'base: {entry.get("base", "")}')
                out.append('flow:')
                flow = entry.get('flow', {})
                # Output primary/secondary if present, otherwise origin/termination
                if 'primary_endpoint' in flow:
                    out.append(f'  primary_endpoint: {_fmt_cell(flow["primary_endpoint"])}')
                if 'secondary_endpoint' in flow:
                    out.append(f'  secondary_endpoint: {_fmt_cell(flow["secondary_endpoint"])}')
                if 'origin' in flow:
                    out.append(f'  origin: {flow["origin"]}')
                if 'origin_cell' in flow:
                    out.append(f'  origin_cell: {_fmt_cell(flow["origin_cell"])}')
                if 'termination' in flow:
                    out.append(f'  termination: {flow["termination"]}')
                if 'termination_cell' in flow:
                    out.append(f'  termination_cell: {_fmt_cell(flow["termination_cell"])}')
                out.append('conditions:')
                cond_lines = _serialize_conditions(entry.get('conditions', {}))
                out.extend(cond_lines)
                if not cond_lines:
                    out.append('  # (col,row): key=value, key=value')
                    out.append('  # example: (28,22): ref=bridge#1')
                out.append('')

        # --- Rivers ---
        rivers = data.get('rivers', {})
        if rivers:
            out.append('## Rivers')
            out.append('')
            for ordinal in sorted(rivers.keys()):
                entry = rivers[ordinal]
                out.append(f'### river {ordinal}')
                out.append(f'name: {entry.get("name", "TODO")}')
                out.append(f'base: {entry.get("base", "")}')
                out.append('flow:')
                flow = entry.get('flow', {})
                if 'origin' in flow:
                    out.append(f'  origin: {flow["origin"]}')
                if 'origin_cell' in flow:
                    out.append(f'  origin_cell: {_fmt_cell(flow["origin_cell"])}')
                if 'termination' in flow:
                    out.append(f'  termination: {flow["termination"]}')
                if 'termination_cell' in flow:
                    out.append(f'  termination_cell: {_fmt_cell(flow["termination_cell"])}')
                direction = flow.get('direction', 'forward')
                out.append(f'  direction: {direction}')
                if 'stitch_with' in flow:
                    out.append(f'  stitch_with: {flow["stitch_with"]}')
                out.append('conditions:')
                cond_lines = _serialize_conditions(entry.get('conditions', {}))
                out.extend(cond_lines)
                if not cond_lines:
                    out.append('  # example: (25,18): ref=bridge#1')
                out.append('')

        # --- Walls ---
        walls = data.get('walls', [])
        if walls:
            out.append('## Walls')
            out.append('')
            out.append('# type options: palisade | earthwork | stone | brick | ruins')
            out.append('# condition options: intact | damaged | ruined | under_construction')
            out.append('')
            for wall in walls:
                out.append(f'### {wall.get("id", "wall 1")}')
                out.append(f'name: {wall.get("name", "TODO")}')
                out.append(f'type: {wall.get("type", "stone")}')
                out.append(f'height_m: {wall.get("height_m", "")}')
                out.append(f'thickness_m: {wall.get("thickness_m", "")}')
                out.append(f'condition: {wall.get("condition", "intact")}')
                if wall.get('towers'):
                    out.append(f'towers: {wall["towers"]}')
                if wall.get('gates'):
                    out.append(f'gates: {wall["gates"]}')
                out.append(f'note: {wall.get("note", "")}')
                out.append('')

        # --- Moat ---
        moats = data.get('moats', [])
        if moats:
            out.append('## Moat')
            out.append('')
            out.append('# source options: river | dug | dry')
            out.append('')
            for moat in moats:
                out.append(f'### {moat.get("id", "moat 1")}')
                out.append(f'name: {moat.get("name", "TODO")}')
                out.append(f'source: {moat.get("source", "river")}')
                out.append(f'width_m: {moat.get("width_m", "")}')
                out.append(f'depth_m: {moat.get("depth_m", "")}')
                out.append(f'condition: {moat.get("condition", "")}')
                out.append(f'is_river_segment: {moat.get("is_river_segment", "false")}')
                out.append(f'note: {moat.get("note", "")}')
                out.append('')

        # --- Districts ---
        districts = data.get('districts', [])
        if districts:
            out.append('## Districts')
            out.append('')
            out.append('# Named areas drawn as polygons. Add descriptions and visibility.')
            out.append('')
            for dist in districts:
                out.append(f'### {dist.get("id", "district 1")}')
                out.append(f'name: {dist.get("name", "TODO")}')
                out.append(f'visibility: {dist.get("visibility", "known")}')
                out.append(f'description: {dist.get("description", "TODO")}')
                out.append(f'note: {dist.get("note", "")}')
                out.append('')

        # --- Linear Feature Details ---
        linear = data.get('linear_details', {})
        out.append('## Linear Feature Details')
        out.append('')
        out.append('# References used by `ref=` annotations on roads and rivers above.')
        out.append('# Wire up by adding `ref=toll#1` etc to a path condition, then define here.')
        out.append('')
        if linear:
            for ref_id, details in sorted(linear.items()):
                out.append(f'### {ref_id}')
                for k, v in details.items():
                    out.append(f'{k}: {v}')
                out.append('')
        else:
            # Keep templates so the file is usable
            for template_type, template_name in [
                ('toll#1', 'Untitled Toll'), ('bridge#1', 'Untitled Bridge'), ('ford#1', 'Untitled Ford')
            ]:
                out.append(f'### {template_type}')
                out.append('# === TEMPLATE — fill in or delete ===')
                out.append(f'name: {template_name}')
                out.append('note: ')
                out.append('')

        # --- Points of Interest ---
        pois = data.get('pois', [])
        out.append('## Points of Interest')
        out.append('')
        has_real_pois = False
        for poi in pois:
            name = poi.get('name', '')
            # Skip pure blank placeholders (only 'Untitled POI' with no cell)
            if name in ('', 'Untitled POI') and not poi.get('cell'):
                continue
            has_real_pois = True
            cell_val = poi.get('cell', '')
            cell_str = _fmt_cell(cell_val) if cell_val else '(##, ##)'
            out.append(f'### {poi.get("id", "poi#1")}')
            out.append(f'name: {name or "TODO"}')
            out.append(f'type: {poi.get("type", "landmark")}')
            out.append(f'cell: {cell_str}')
            out.append(f'visibility: {poi.get("visibility", "known")}')
            out.append(f'description: {poi.get("description", "")}')
            out.append(f'note: {poi.get("note", "")}')
            out.append('')
        if not has_real_pois:
            # Keep one empty template as a hint
            out.append('### poi#1')
            out.append('# === TEMPLATE — fill in or delete ===')
            out.append('name: Untitled POI')
            out.append('type: landmark')
            out.append('cell: (##, ##)')
            out.append('visibility: known')
            out.append('description: ')
            out.append('note: ')
            out.append('')

        # --- Feature Visibility Overrides ---
        fv = data.get('feature_visibility', {})
        out.append('## Feature Visibility Overrides')
        out.append('')
        out.append('# known | local | hidden.  Format: `(col, row): visibility`')
        if fv:
            for cell, vis in fv.items():
                out.append(f'{_fmt_cell(cell)}: {vis}')
        else:
            out.append('# (1, 38): local')
        out.append('')

        # --- Feature Names ---
        fn = data.get('feature_names', {})
        out.append('## Feature Names')
        out.append('')
        out.append('# Format: `(col, row): Name`')
        if fn:
            for cell, name in fn.items():
                out.append(f'{_fmt_cell(cell)}: {name}')
        else:
            out.append('# (15, 12): Blackrock Pass')
        out.append('')

        return '\n'.join(out)
