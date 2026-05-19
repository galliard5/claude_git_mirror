"""
wxx_annotations.py — Scaffold, parse, and merge annotation files for v2 .wxx renders.

The annotation file is the human-authored sidecar that carries everything
the .wxx itself doesn't: real road/river names, base conditions, flow
direction, POIs, intent notes, project markers, feature visibility.

Three operations:

  scaffold(wmap, out_path)         — generate a fresh annotation file from a
                                     parsed map. Writes templates and TODOs.
  parse(annotation_text) -> dict   — read an existing annotation file into
                                     a structured dict for the renderer.
  merge_into_description(...)      — apply parsed annotations to a renderer's
                                     description block, returning the final
                                     section data.

Three-state generation flow (driven by wxx_to_svg.py main loop):

  1. annotation file absent      → call scaffold(), then render in scaffold mode
  2. annotation file present     → call parse() + merge, render in production mode
  3. --regenerate-annotations    → rename existing to .previous.md, call scaffold()
"""
from __future__ import annotations
import os
import re
import math
from datetime import date
from typing import Optional


def classify_shape_tag(raw_tag: str, shape_type: str = 'Path') -> str:
    """Map a Worldographer shape tag to a semantic category.

    Tags are user-defined free text, so we match by keyword.
    Returns one of: 'road', 'river', 'moat', 'wall', 'bridge', 'district', 'other'
    """
    t = raw_tag.lower()
    # Moat before river — a moat is a defensive water feature distinct from a natural river
    if 'moat' in t:
        return 'moat'
    # Water keywords apply to both paths and polygons (polygon = river body, path = flow course)
    if any(w in t for w in ('river', 'stream', 'creek', 'canal', 'brook', 'lake', 'pond')):
        return 'river'
    if shape_type == 'Polygon':
        return 'district'
    if 'bridge' in t:
        return 'bridge'
    if any(w in t for w in ('road', 'street', 'lane', 'alley', 'way', 'track', 'trail')):
        return 'road'
    if any(w in t for w in ('wall', 'rampart', 'palisade', 'fence')):
        return 'wall'
    return 'other'


def stroke_to_feet(stroke_width: float) -> int:
    """Convert Worldographer strokeWidth to approximate feet.
    strokeWidth = in_app_weight / 100; user convention: 1 weight ≈ 1 ft.
    """
    return round(stroke_width * 100)


def sample_path_cells(points: list, orientation: str,
                      samples_per_segment: int = 10) -> list:
    """Walk a shape's point list and return the ordered hex/square cells touched."""
    if not points:
        return []
    cells = []
    last_cell = None
    is_square = orientation == 'SQUARE'
    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]
        for t in range(samples_per_segment + 1):
            s = t / samples_per_segment
            wx = x1 + (x2 - x1) * s
            wy = y1 + (y2 - y1) * s
            cell = world_to_square(wx, wy) if is_square else world_to_hex(wx, wy, orientation)
            if cell != last_cell:
                cells.append(cell)
                last_cell = cell
    deduped = [cells[0]] if cells else []
    for c in cells[1:]:
        if c != deduped[-1]:
            deduped.append(c)
    return deduped


def _wall_feature_cells(wall_shape, wmap, orientation: str) -> tuple[list, list]:
    """Find tower and gatehouse features lying on or adjacent to a wall shape.

    Returns (tower_cells, gate_cells) as lists of (col, row) tuples.
    """
    path_cells = set(sample_path_cells(wall_shape.points, orientation))

    towers, gates = [], []
    for f in wmap.features:
        if 'Coast' in f.type:
            continue
        fcell = world_to_hex(f.x, f.y, orientation)
        ft = f.type.lower()
        near = any(cells_adjacent_or_equal(fcell, wc) for wc in path_cells)
        if not near:
            continue
        if any(w in ft for w in ('tower', 'walltower', 'watchtower')):
            towers.append(fcell)
        elif any(w in ft for w in ('gatehouse', 'gate')):
            gates.append(fcell)
    return towers, gates


# =============================================================================
# Coordinate inversion helpers (duplicated from wxx_to_claude to avoid circular)
# =============================================================================

def world_to_hex(wx: float, wy: float, orientation: str) -> tuple[int, int]:
    """Inverse of hex_center for the given orientation. Returns nearest cell."""
    if orientation == 'ROWS':
        row = round((wy - 150) / 225)
        if row % 2 == 1:
            col = round((wx - 300) / 300)
        else:
            col = round((wx - 150) / 300)
    else:
        col = round((wx - 150) / 225)
        if col % 2 == 0:
            row = round((wy - 150) / 300)
        else:
            row = round((wy - 300) / 300)
    return col, row


def world_to_square(wx: float, wy: float, tile_size: float = 300.0) -> tuple[int, int]:
    return int(wx // tile_size), int(wy // tile_size)


def cells_adjacent_or_equal(c1: tuple, c2: tuple) -> bool:
    """Two cells are 'meeting' if same or hex-neighbours."""
    if c1 == c2:
        return True
    dc = c2[0] - c1[0]
    dr = c2[1] - c1[1]
    return (dc, dr) in [(-1, 0), (1, 0), (0, -1), (0, 1),
                         (-1, -1), (1, -1), (-1, 1), (1, 1)]


# =============================================================================
# Stitch detection
# =============================================================================

def _shape_endpoint_cells(shape, orientation: str) -> tuple[tuple, tuple]:
    """Return (first_cell, last_cell) for a shape, or (None, None)."""
    if not shape.points or len(shape.points) < 2:
        return (None, None)
    first = shape.points[0]
    last = shape.points[-1]
    if orientation == 'SQUARE':
        return (world_to_square(*first), world_to_square(*last))
    return (world_to_hex(*first, orientation),
            world_to_hex(*last, orientation))


def find_stitch_candidates(shapes: list, orientation: str) -> list:
    """Find pairs of river shapes whose endpoints meet at the same/adjacent hex.

    Returns a list of (i, j, meeting_cells) for shape index pairs.
    """
    rivers = [(idx, s) for idx, s in enumerate(shapes)
              if classify_shape_tag(s.tag, getattr(s, 'shape_type', 'Path')) == 'river']
    candidates = []
    for ai, (idx_a, sa) in enumerate(rivers):
        a_first, a_last = _shape_endpoint_cells(sa, orientation)
        if a_first is None:
            continue
        for idx_b, sb in rivers[ai + 1:]:
            b_first, b_last = _shape_endpoint_cells(sb, orientation)
            if b_first is None:
                continue
            for ae in (a_first, a_last):
                for be in (b_first, b_last):
                    if cells_adjacent_or_equal(ae, be):
                        candidates.append((idx_a, idx_b, (ae, be)))
                        break
                else:
                    continue
                break
    return candidates


# =============================================================================
# Scaffold generation
# =============================================================================

POI_TYPE_LIST = """# Available POI types (renderer maps these to icon glyphs):
#
#   Settlements:           capital, city, town, village, hamlet, manor, hold
#   Defensive:             fort, watchtower, keep, ruined_keep, palisade
#   Infrastructure:        tollbooth, bridge, ford, ferry, mill, lighthouse,
#                          well, waystation
#   Religious / Cultural:  shrine, temple, monastery, cemetery, gibbet,
#                          monument, standing_stones
#   Resources:             mine, quarry, lumber_camp, fishing_camp, salt_works
#   Wilderness / Adventure: ruin, dungeon, cave, lair, camp, bandit_camp,
#                          ambush_site, battlefield
#   Natural Landmarks:     waterfall, hot_spring, oasis, grove, ancient_tree,
#                          peak, cliff
#   Generic:               landmark
#
# Visibility values: known | local | hidden
# (See Wxx_Map_Format_Spec.md Appendix A for full vocabulary.)"""


def scaffold(wmap, source_filename: str = '') -> str:
    """Generate a fresh annotation file from a parsed map.

    Returns the file content as a string. Caller is responsible for writing
    to disk (typically '<basename>.annotations.md').
    """
    out = []
    today = date.today().isoformat()
    name = source_filename.replace('.wxx', '') if source_filename else 'map'
    is_square = wmap.hex_orientation == 'SQUARE'

    # YAML frontmatter
    out.append('---')
    out.append(f'name: {name} Annotations')
    out.append('keywords: [map, annotations]')
    out.append(f'description: Authorial overlay for {source_filename or "the map"}.')
    out.append(f'generated: {today}')
    out.append('---')
    out.append('')
    out.append(f'# Annotations for {source_filename or name}')
    out.append('')
    out.append('Edit this file to add real names, base conditions, intent notes, POIs,')
    out.append('and other authored content. The renderer merges this into the .svg')
    out.append('description block on the next render.')
    out.append('')
    out.append('Auto-generated TODO placeholders are scattered throughout. Replace them')
    out.append('with real content or delete them. Templates marked `# === TEMPLATE ===`')
    out.append('are skipped at render time until you fill in non-placeholder values.')
    out.append('')

    # ── Project ────────────────────────────────────────────
    out.append('## Project')
    out.append('')
    out.append('# Pick the project styling for this map. Options: default, aethelmark.')
    out.append('# Defaults to `default` if absent.')
    out.append('project: default')
    out.append('')

    # ── Intent ─────────────────────────────────────────────
    out.append('## Intent')
    out.append('')
    out.append('### Format')
    out.append('# Operational hints for tools and AI consumers.')
    out.append(f'- Description self-contained in the comment block. Edit this annotation file,')
    out.append(f'  not the .svg comment block directly (changes will be overwritten on re-render).')
    out.append('- Re-render via `python wxx_to_svg.py <input.wxx> <output.svg>`.')
    out.append('- Use `--regenerate-annotations` if the .wxx geometry changes.')
    out.append('')
    out.append('### Narrative')
    out.append('# Authorial design notes — surfaced to the user when this map is loaded.')
    out.append('# Use `@ambiguous: ...` to flag unresolved authorial decisions.')
    out.append('- TODO: describe the map\'s intended use (campaign hex-crawl, regional reference, etc.)')
    out.append('- TODO: note any settlements with deliberate design pressures.')
    out.append('')

    # ── Elevation Overrides ────────────────────────────────
    if not is_square:
        out.append('## Elevation Overrides')
        out.append('')
        out.append('# Per-cell elevation overrides for hexes that meaningfully differ from')
        out.append('# their terrain default. Format: `(col, row): elevation_m`. Optional.')
        out.append('overrides:')
        out.append('  # (15, 12): 1800m   # example: ridge fortress site')
        out.append('')

    # ── Roads / Rivers / Districts ─────────────────────────
    if not is_square:
        _classify = lambda s: classify_shape_tag(s.tag, getattr(s, 'shape_type', 'Path'))
        road_shapes  = [(i, s) for i, s in enumerate(wmap.shapes) if _classify(s) == 'road']
        river_shapes = [(i, s) for i, s in enumerate(wmap.shapes) if _classify(s) == 'river']
        bridge_shapes = [(i, s) for i, s in enumerate(wmap.shapes) if _classify(s) == 'bridge']
        district_shapes = [(i, s) for i, s in enumerate(wmap.shapes) if _classify(s) == 'district']
        stitch_pairs = find_stitch_candidates(wmap.shapes, wmap.hex_orientation)
        stitch_map = {}
        for ia, ib, (ca, cb) in stitch_pairs:
            stitch_map.setdefault(ia, []).append((ib, ca, cb))
            stitch_map.setdefault(ib, []).append((ia, cb, ca))

        if road_shapes or bridge_shapes:
            out.append('## Roads')
            out.append('')
            all_road_like = road_shapes + bridge_shapes
            all_road_like.sort(key=lambda x: x[0])
            for ord_idx, (shape_idx, s) in enumerate(all_road_like, start=1):
                first_cell, last_cell = _shape_endpoint_cells(s, wmap.hex_orientation)
                width_ft = stroke_to_feet(s.stroke_width)
                base_hint = s.tag if s.tag else 'unspecified surface'
                out.append(f'### road {ord_idx}')
                out.append(f'name: TODO  # {s.tag}')
                out.append(f'base: {base_hint}, width≈{width_ft}ft')
                out.append('flow:')
                out.append(f'  primary_endpoint: {first_cell}')
                out.append(f'  secondary_endpoint: {last_cell}')
                out.append('conditions:')
                out.append('  # (col,row): key=value, key=value')
                out.append('  # example: (28,22): ref=bridge#1')
                out.append('')

        if river_shapes:
            out.append('## Rivers')
            out.append('')
            for ord_idx, (shape_idx, s) in enumerate(river_shapes, start=1):
                first_cell, last_cell = _shape_endpoint_cells(s, wmap.hex_orientation)
                base_hint = s.tag if s.tag else 'unspecified width, unknown current'
                if shape_idx in stitch_map:
                    out.append(f'### river {ord_idx}')
                    out.append('# === STITCH CANDIDATE ===')
                    for partner_idx, my_cell, their_cell in stitch_map[shape_idx]:
                        partner_ord = None
                        for po, (pi, _) in enumerate(river_shapes, start=1):
                            if pi == partner_idx:
                                partner_ord = po
                                break
                        if partner_ord is not None:
                            out.append(f'# Endpoint at {my_cell} is adjacent to river {partner_ord}\'s endpoint at {their_cell}.')
                    out.append('# If these are one logical river drawn in two passes, set')
                    out.append('# `stitch_with: river N` AND mark one as `direction: reverse`.')
                    out.append('# If they\'re a real confluence (different named tributaries),')
                    out.append('# leave them separate and set termination_cell on both.')
                    out.append('# Delete this comment once resolved.')
                else:
                    out.append(f'### river {ord_idx}')
                out.append(f'name: TODO  # {s.tag}')
                out.append(f'base: {base_hint}')
                out.append('flow:')
                out.append('  origin: TODO')
                out.append(f'  origin_cell: {first_cell}')
                out.append('  termination: TODO')
                out.append(f'  termination_cell: {last_cell}')
                out.append('  direction: forward')
                out.append('conditions:')
                out.append('  # example: (25,18): ref=bridge#1')
                out.append('')

        wall_shapes = [(i, s) for i, s in enumerate(wmap.shapes) if _classify(s) == 'wall']
        moat_shapes = [(i, s) for i, s in enumerate(wmap.shapes) if _classify(s) == 'moat']

        if wall_shapes:
            out.append('## Walls')
            out.append('')
            out.append('# Wall segments drawn as paths in the .wxx.')
            out.append('# type options: palisade | earthwork | stone | brick | ruins')
            out.append('# condition options: intact | damaged | ruined | under_construction')
            out.append('# towers/gates are auto-detected from nearby features.')
            out.append('')
            for ord_idx, (shape_idx, s) in enumerate(wall_shapes, start=1):
                first_cell, last_cell = _shape_endpoint_cells(s, wmap.hex_orientation)
                towers, gates = _wall_feature_cells(s, wmap, wmap.hex_orientation)
                out.append(f'### wall {ord_idx}')
                out.append(f'name: TODO  # {s.tag}')
                out.append('type: stone')
                out.append('height_m: ')
                out.append('thickness_m: ')
                out.append('condition: intact')
                if towers:
                    cell_str = ', '.join(f'({c[0]},{c[1]})' for c in towers)
                    out.append(f'towers: {cell_str}')
                if gates:
                    cell_str = ', '.join(f'({c[0]},{c[1]})' for c in gates)
                    out.append(f'gates: {cell_str}')
                out.append('note: ')
                out.append('')

        if moat_shapes:
            out.append('## Moat')
            out.append('')
            out.append('# Defensive water features. source=river means the waterway itself is the barrier.')
            out.append('')
            for ord_idx, (shape_idx, s) in enumerate(moat_shapes, start=1):
                first_cell, last_cell = _shape_endpoint_cells(s, wmap.hex_orientation)
                out.append(f'### moat {ord_idx}')
                out.append(f'name: TODO  # {s.tag}')
                out.append('source: river  # river | dug | dry')
                out.append('width_m: ')
                out.append('depth_m: ')
                out.append('condition: ')
                out.append('is_river_segment: false  # true if the natural river forms this barrier')
                out.append('note: ')
                out.append('')

        if district_shapes:
            out.append('## Districts')
            out.append('')
            out.append('# Named areas drawn as polygons. Add descriptions and visibility.')
            out.append('')
            for ord_idx, (shape_idx, s) in enumerate(district_shapes, start=1):
                out.append(f'### district {ord_idx}')
                out.append(f'name: {s.tag if s.tag else f"district {ord_idx}"}')
                out.append('visibility: known')
                out.append('description: TODO')
                out.append('note: ')
                out.append('')

    # ── Linear Feature Details ─────────────────────────────
    if not is_square:
        out.append('## Linear Feature Details')
        out.append('')
        out.append('# References used by `ref=` annotations on roads and rivers above.')
        out.append('# Wire up by adding `ref=toll#1` etc to a path condition, then define here.')
        out.append('# Templates below are unused — fill in or delete.')
        out.append('')
        out.append('### toll#1')
        out.append('# === TEMPLATE — fill in or delete ===')
        out.append('name: Untitled Toll')
        out.append('type: tollbooth')
        out.append('controlled_by: ')
        out.append('fee: ')
        out.append('note: ')
        out.append('')
        out.append('### bridge#1')
        out.append('# === TEMPLATE — fill in or delete ===')
        out.append('name: Untitled Bridge')
        out.append('type: bridge')
        out.append('material: stone | wood | rope | ferry')
        out.append('length_m: ')
        out.append('note: ')
        out.append('')
        out.append('### ford#1')
        out.append('# === TEMPLATE — fill in or delete ===')
        out.append('name: Untitled Ford')
        out.append('type: ford')
        out.append('difficulty: ')
        out.append('note: ')
        out.append('')

    # ── Points of Interest ─────────────────────────────────
    out.append('## Points of Interest')
    out.append('')
    out.append(POI_TYPE_LIST)
    out.append('')
    out.append('### poi#1')
    out.append('# === TEMPLATE — fill in or delete ===')
    out.append('name: Untitled POI')
    out.append('type: landmark')
    out.append('cell: (##, ##)')
    out.append('visibility: known')
    out.append('description: ')
    out.append('note: ')
    out.append('')
    out.append('### poi#2')
    out.append('# === TEMPLATE — fill in or delete ===')
    out.append('name: Untitled POI')
    out.append('type: landmark')
    out.append('cell: (##, ##)')
    out.append('visibility: known')
    out.append('description: ')
    out.append('note: ')
    out.append('')

    # ── Feature Visibility Overrides ───────────────────────
    real_features = [f for f in wmap.features if 'Coast' not in f.type]
    if real_features:
        out.append('## Feature Visibility Overrides')
        out.append('')
        out.append('# By default, all .wxx features render as `known`. Override here if a')
        out.append('# feature should be `local` (unlabeled to outsiders) or `hidden` (GM only).')
        out.append('# Format: `(col, row): visibility`. Coords must match a real feature.')
        out.append('# Example:')
        out.append('# (1, 38): local')
        out.append('')

    # ── Feature Names ──────────────────────────────────────
    if real_features:
        unlabeled = [f for f in real_features if not f.label.strip()]
        out.append('## Feature Names')
        out.append('')
        if unlabeled:
            out.append('# Worldographer left these features unlabeled. Assign real names below.')
            out.append('# Format: `(col, row): Name`')
            for f in unlabeled:
                if is_square:
                    cell = world_to_square(f.x, f.y)
                else:
                    cell = world_to_hex(f.x, f.y, wmap.hex_orientation)
                short = f.type.split('/', 1)[-1] if '/' in f.type else f.type
                out.append(f'({cell[0]}, {cell[1]}): TODO   # {short}')
        else:
            out.append('# All features in this .wxx have labels. Add overrides below if you want')
            out.append('# to rename any. Format: `(col, row): Name` matches by hex coordinate.')
        out.append('')

    return '\n'.join(out)


# =============================================================================
# Annotation parsing
# =============================================================================

# Regex helpers
SECTION_HEADER_RE = re.compile(r'^##\s+(.+?)\s*$', re.MULTILINE)
SUBSECTION_HEADER_RE = re.compile(r'^###\s+(.+?)\s*$', re.MULTILINE)


def _strip_comments(text: str) -> list:
    """Return list of non-empty, non-comment lines from a text block."""
    out = []
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith('#'):
            continue
        out.append(line)
    return out


def _parse_kv_line(line: str) -> tuple:
    """Parse `key: value` line. Returns (key, value) or (None, None)."""
    if ':' not in line:
        return (None, None)
    k, v = line.split(':', 1)
    return (k.strip(), v.strip())


def _parse_cell(s: str) -> Optional[tuple]:
    """Parse `(col, row)` notation. Returns None if placeholder or unparseable."""
    if not s:
        return None
    s = s.strip().rstrip(',')
    m = re.match(r'\(\s*(-?\d+)\s*,\s*(-?\d+)\s*\)', s)
    if not m:
        return None
    return (int(m.group(1)), int(m.group(2)))


def _is_placeholder(value: str) -> bool:
    """True if value is a known placeholder (not yet filled in)."""
    if not value:
        return True
    s = value.strip()
    return s in ('', 'TODO', '(##, ##)', '##', '?') or '##' in s


def _split_sections(text: str) -> dict:
    """Split a markdown document into a dict of section_name → section_body.

    Sections start with '## Heading'. Sub-sections within ('### ...') are
    preserved in the body text.
    """
    sections = {}
    current_name = None
    current_lines = []
    for line in text.splitlines():
        m = re.match(r'^##\s+(.+?)\s*$', line)
        if m and not line.startswith('###'):
            # Flush previous
            if current_name is not None:
                sections[current_name] = '\n'.join(current_lines)
            current_name = m.group(1).strip()
            current_lines = []
        else:
            if current_name is not None:
                current_lines.append(line)
    if current_name is not None:
        sections[current_name] = '\n'.join(current_lines)
    return sections


def _split_subsections(body: str) -> dict:
    """Within a section body, split by '### Heading'."""
    subs = {}
    current_name = None
    current_lines = []
    for line in body.splitlines():
        m = re.match(r'^###\s+(.+?)\s*$', line)
        if m:
            if current_name is not None:
                subs[current_name] = '\n'.join(current_lines)
            current_name = m.group(1).strip()
            current_lines = []
        else:
            if current_name is not None:
                current_lines.append(line)
    if current_name is not None:
        subs[current_name] = '\n'.join(current_lines)
    return subs


def parse(text: str) -> dict:
    """Parse an annotation file into a structured dict.

    Returns:
      {
        'project': str,
        'intent_format': [str, ...],
        'intent_narrative': [str, ...],
        'elevation_overrides': {(col, row): elevation_string, ...},
        'roads': {ordinal: {name, base, flow:{...}, conditions:{(c,r):{k:v}}}, ...},
        'rivers': {ordinal: {...same...}},
        'linear_details': {ref_id: {key: value, ...}, ...},
        'pois': [{name, type, cell, visibility, description, note}, ...],
        'feature_visibility': {(col, row): 'known'|'local'|'hidden', ...},
        'feature_names': {(col, row): name, ...},
      }
    """
    sections = _split_sections(text)
    result = {
        'project': 'default',
        'intent_format': [],
        'intent_narrative': [],
        'elevation_overrides': {},
        'roads': {},
        'rivers': {},
        'linear_details': {},
        'walls': [],
        'moats': [],
        'districts': [],
        'pois': [],
        'feature_visibility': {},
        'feature_names': {},
    }

    # Project
    if 'Project' in sections:
        for line in _strip_comments(sections['Project']):
            k, v = _parse_kv_line(line)
            if k == 'project' and v:
                result['project'] = v

    # Intent — split by ### Format / ### Narrative
    if 'Intent' in sections:
        subs = _split_subsections(sections['Intent'])
        for line in _strip_comments(subs.get('Format', '')):
            if line.lstrip().startswith('-'):
                result['intent_format'].append(line.lstrip()[1:].strip())
        for line in _strip_comments(subs.get('Narrative', '')):
            if line.lstrip().startswith('-'):
                result['intent_narrative'].append(line.lstrip()[1:].strip())

    # Elevation overrides
    if 'Elevation Overrides' in sections:
        for line in _strip_comments(sections['Elevation Overrides']):
            # Look for `(c, r): value`
            m = re.match(r'\s*(\(\s*-?\d+\s*,\s*-?\d+\s*\))\s*:\s*(.+)', line)
            if m:
                cell = _parse_cell(m.group(1))
                if cell:
                    result['elevation_overrides'][cell] = m.group(2).strip()

    # Roads / Rivers — same parsing structure
    for section_name, target_key in [('Roads', 'roads'), ('Rivers', 'rivers')]:
        if section_name not in sections:
            continue
        subs = _split_subsections(sections[section_name])
        for sub_name, body in subs.items():
            # Sub name is like "road 1" or "river 1"
            m = re.match(r'(?:road|river)\s+(\d+)', sub_name, re.IGNORECASE)
            if not m:
                continue
            ord_idx = int(m.group(1))
            entry = {
                'name': sub_name,
                'base': '',
                'flow': {},
                'conditions': {},
            }
            in_flow = False
            in_conditions = False
            for line in body.splitlines():
                stripped = line.strip()
                if not stripped or stripped.startswith('#'):
                    continue
                if stripped.startswith('flow:'):
                    in_flow = True
                    in_conditions = False
                    continue
                if stripped.startswith('conditions:'):
                    in_conditions = True
                    in_flow = False
                    continue
                if in_flow and line.startswith(('  ', '\t')):
                    k, v = _parse_kv_line(stripped)
                    if k:
                        # Try to parse cell-shaped values
                        cell = _parse_cell(v)
                        entry['flow'][k] = cell if cell else v
                    continue
                if in_conditions and line.startswith(('  ', '\t')):
                    # Format: (c,r): key=val, key=val
                    cm = re.match(r'\s*(\(\s*-?\d+\s*,\s*-?\d+\s*\))\s*:\s*(.+)', line)
                    if cm:
                        cell = _parse_cell(cm.group(1))
                        if cell:
                            kvs = {}
                            for pair in cm.group(2).split(','):
                                if '=' in pair:
                                    pk, pv = pair.split('=', 1)
                                    pk, pv = pk.strip(), pv.strip()
                                    if pk == 'ref':
                                        kvs.setdefault('ref', []).append(pv)
                                    else:
                                        kvs[pk] = pv
                            # Merge into existing cell entry (same cell, multiple lines)
                            if cell in entry['conditions']:
                                existing = entry['conditions'][cell]
                                for pk, pv in kvs.items():
                                    if pk == 'ref':
                                        existing.setdefault('ref', []).extend(pv)
                                    else:
                                        existing[pk] = pv
                            else:
                                entry['conditions'][cell] = kvs
                    continue
                # Top-level fields (not in flow/conditions block)
                k, v = _parse_kv_line(stripped)
                if k in ('name', 'base'):
                    entry[k] = v
                    in_flow = False
                    in_conditions = False
            result[target_key][ord_idx] = entry

    # Linear Feature Details
    if 'Linear Feature Details' in sections:
        subs = _split_subsections(sections['Linear Feature Details'])
        for sub_name, body in subs.items():
            ref_id = sub_name.strip()
            details = {}
            is_template = False
            for line in body.splitlines():
                stripped = line.strip()
                if '=== TEMPLATE ===' in stripped or 'TEMPLATE' in stripped and '===' in stripped:
                    is_template = True
                    continue
                if not stripped or stripped.startswith('#'):
                    continue
                k, v = _parse_kv_line(stripped)
                if k:
                    details[k] = v
            # Skip pure templates (Untitled Toll/Bridge/Ford with no real content)
            name = details.get('name', '')
            if is_template and name.startswith('Untitled '):
                continue
            if details:
                result['linear_details'][ref_id] = details

    # Points of Interest
    if 'Points of Interest' in sections:
        subs = _split_subsections(sections['Points of Interest'])
        for sub_name, body in subs.items():
            entry = {'id': sub_name.strip()}
            is_template = False
            for line in body.splitlines():
                stripped = line.strip()
                if 'TEMPLATE' in stripped and '===' in stripped:
                    is_template = True
                    continue
                if not stripped or stripped.startswith('#'):
                    continue
                k, v = _parse_kv_line(stripped)
                if k:
                    entry[k] = v
            # Skip empty-template POIs
            name = entry.get('name', '')
            cell = entry.get('cell', '')
            if (is_template and name == 'Untitled POI') or _is_placeholder(cell):
                # Skip; warn separately if half-filled (real name + placeholder cell)
                continue
            cell_parsed = _parse_cell(cell)
            if cell_parsed:
                entry['cell'] = cell_parsed
                result['pois'].append(entry)

    # Feature Visibility Overrides
    if 'Feature Visibility Overrides' in sections:
        for line in _strip_comments(sections['Feature Visibility Overrides']):
            m = re.match(r'\s*(\(\s*-?\d+\s*,\s*-?\d+\s*\))\s*:\s*(\w+)', line)
            if m:
                cell = _parse_cell(m.group(1))
                vis = m.group(2).lower().strip()
                if cell and vis in ('known', 'local', 'hidden'):
                    result['feature_visibility'][cell] = vis

    # Feature Names
    if 'Feature Names' in sections:
        for line in _strip_comments(sections['Feature Names']):
            m = re.match(r'\s*(\(\s*-?\d+\s*,\s*-?\d+\s*\))\s*:\s*(.+?)(?:\s+#.*)?$', line)
            if m:
                cell = _parse_cell(m.group(1))
                name = m.group(2).strip()
                if cell and name and name != 'TODO':
                    result['feature_names'][cell] = name

    # Walls
    if 'Walls' in sections:
        subs = _split_subsections(sections['Walls'])
        for sub_name, body in subs.items():
            entry = {'id': sub_name.strip()}
            for line in body.splitlines():
                stripped = line.strip()
                if not stripped or stripped.startswith('#'):
                    continue
                k, v = _parse_kv_line(stripped)
                if k:
                    entry[k] = v
            if entry.get('name', 'TODO') != 'TODO' or any(
                entry.get(f) for f in ('type', 'height_m', 'thickness_m', 'towers', 'gates', 'note')
            ):
                result['walls'].append(entry)

    # Moat
    if 'Moat' in sections:
        subs = _split_subsections(sections['Moat'])
        for sub_name, body in subs.items():
            entry = {'id': sub_name.strip()}
            for line in body.splitlines():
                stripped = line.strip()
                if not stripped or stripped.startswith('#'):
                    continue
                k, v = _parse_kv_line(stripped)
                if k:
                    entry[k] = v
            result['moats'].append(entry)

    # Districts
    if 'Districts' in sections:
        subs = _split_subsections(sections['Districts'])
        for sub_name, body in subs.items():
            entry = {'id': sub_name.strip()}
            for line in body.splitlines():
                stripped = line.strip()
                if not stripped or stripped.startswith('#'):
                    continue
                k, v = _parse_kv_line(stripped)
                if k:
                    entry[k] = v
            name = entry.get('name', '')
            if name and name != 'TODO':
                result['districts'].append(entry)

    return result


# =============================================================================
# Drift warnings
# =============================================================================

def check_drift(annotations: dict, wmap, valid_icon_types: set) -> list:
    """Compare parsed annotations against the current map. Return warning strings."""
    warnings = []

    # Count roads/rivers in current map
    _cat = lambda s: classify_shape_tag(s.tag, getattr(s, 'shape_type', 'Path'))
    n_roads = sum(1 for s in wmap.shapes if _cat(s) in ('road', 'bridge'))
    n_rivers = sum(1 for s in wmap.shapes if _cat(s) == 'river')

    for ord_idx in annotations.get('roads', {}):
        if ord_idx > n_roads:
            warnings.append(
                f"Annotation references road {ord_idx} but current .wxx has only "
                f"{n_roads} roads. Skipping."
            )
    for ord_idx in annotations.get('rivers', {}):
        if ord_idx > n_rivers:
            warnings.append(
                f"Annotation references river {ord_idx} but current .wxx has only "
                f"{n_rivers} rivers. Skipping."
            )

    # POI types must be in vocabulary
    for poi in annotations.get('pois', []):
        ptype = poi.get('type', '')
        if ptype and ptype not in valid_icon_types:
            warnings.append(
                f"POI {poi.get('id', '?')} has type='{ptype}' not in icon vocabulary. "
                f"Will fail at render. Use 'landmark' as fallback."
            )

    # Feature visibility / names referencing non-existent cells
    real_features = [f for f in wmap.features if 'Coast' not in f.type]
    is_square = wmap.hex_orientation == 'SQUARE'
    feature_cells = set()
    for f in real_features:
        if is_square:
            feature_cells.add(world_to_square(f.x, f.y))
        else:
            feature_cells.add(world_to_hex(f.x, f.y, wmap.hex_orientation))
    for cell in annotations.get('feature_visibility', {}):
        if cell not in feature_cells:
            warnings.append(
                f"Feature visibility override at {cell} doesn't match any feature in .wxx."
            )
    for cell in annotations.get('feature_names', {}):
        if cell not in feature_cells:
            warnings.append(
                f"Feature name override at {cell} doesn't match any feature in .wxx."
            )

    # Check for orphan refs (referenced in conditions but not defined in details)
    referenced_refs = set()
    for entries in (annotations.get('roads', {}).values(),
                    annotations.get('rivers', {}).values()):
        for entry in entries:
            for cond in entry.get('conditions', {}).values():
                if 'ref' in cond:
                    refs = cond['ref']
                    if isinstance(refs, str):
                        refs = [refs]
                    referenced_refs.update(refs)
    defined_refs = set(annotations.get('linear_details', {}).keys())
    for ref in referenced_refs - defined_refs:
        warnings.append(f"Reference '{ref}' used in path conditions but no entry in Linear Feature Details.")
    for ref in defined_refs - referenced_refs:
        warnings.append(f"Linear Feature Detail '{ref}' is defined but not referenced by any path. (Unused.)")

    return warnings


# =============================================================================
# Three-state generation flow
# =============================================================================

def annotation_path_for(svg_path: str) -> str:
    """Compute the annotation file path for a given .svg output path."""
    base = os.path.splitext(svg_path)[0]
    return f'{base}.annotations.md'


def previous_annotation_path_for(svg_path: str) -> str:
    base = os.path.splitext(svg_path)[0]
    return f'{base}.annotations.previous.md'


def determine_state(svg_path: str, regenerate: bool = False) -> str:
    """Determine which generation state we're in.

    Returns: 'scaffold' | 'merge' | 'regenerate'
    """
    annot_path = annotation_path_for(svg_path)
    if regenerate:
        return 'regenerate'
    if os.path.exists(annot_path):
        return 'merge'
    return 'scaffold'


def write_scaffold(wmap, svg_path: str, source_filename: str = '') -> str:
    """Generate and write a scaffold annotation file. Returns the path written."""
    annot_path = annotation_path_for(svg_path)
    content = scaffold(wmap, source_filename=source_filename)
    with open(annot_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return annot_path


def regenerate_scaffold(wmap, svg_path: str, source_filename: str = '') -> tuple[str, str]:
    """Move existing annotation to .previous.md, write fresh scaffold.

    Returns (previous_path, new_scaffold_path).
    """
    annot_path = annotation_path_for(svg_path)
    prev_path = previous_annotation_path_for(svg_path)
    if os.path.exists(annot_path):
        # Overwrite .previous if it exists
        if os.path.exists(prev_path):
            os.remove(prev_path)
        os.rename(annot_path, prev_path)
    content = scaffold(wmap, source_filename=source_filename)
    with open(annot_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return prev_path, annot_path


def load_annotations(svg_path: str) -> Optional[dict]:
    """Load and parse the annotation file for a given output path. None if absent."""
    annot_path = annotation_path_for(svg_path)
    if not os.path.exists(annot_path):
        return None
    with open(annot_path, 'r', encoding='utf-8') as f:
        text = f.read()
    return parse(text)
