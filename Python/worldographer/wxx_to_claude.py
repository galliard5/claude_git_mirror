"""
wxx_to_claude.py — Generate the v2 markdown description block for embedding in
.svg comment headers (and optionally as a standalone .md file for AI consumption).

Takes a parsed WxxMap and a parsed annotation dict, produces the canonical
Markdown description per Wxx_Map_Format_Spec.md sections 3-15.

The compressed token cost is ~3K for a 50x50 map vs ~430K for the full SVG —
roughly a 140x reduction without losing any spatial reasoning information.
"""
from __future__ import annotations
import re
from collections import defaultdict
from typing import Optional

from wxx_annotations import (
    world_to_hex, world_to_square, cells_adjacent_or_equal,
    classify_shape_tag, stroke_to_feet, sample_path_cells,
)


# =============================================================================
# Path syntax with inheritance
# =============================================================================

def format_path_with_inheritance(cells: list, conditions: dict) -> str:
    """Format a cell sequence as the v2 path syntax.

    cells: [(col, row), ...]
    conditions: {(col, row): {key: value, ...}, ...}

    Returns a single-line pipe-delimited string with optional :key=val,key=val
    annotations on cells that have conditions.
    """
    parts = []
    for cell in cells:
        if cell in conditions:
            kvs = conditions[cell]
            kv_parts = []
            for k, v in kvs.items():
                if k == 'ref':
                    items = v if isinstance(v, list) else [v]
                    kv_parts.extend(f'@{item}' for item in items)
                elif isinstance(v, list):
                    kv_parts.extend(f'{k}={item}' for item in v)
                else:
                    kv_parts.append(f'{k}={v}')
            parts.append(f'({cell[0]},{cell[1]}):{",".join(kv_parts)}')
        else:
            parts.append(f'({cell[0]},{cell[1]})')
    return '|'.join(parts)


# =============================================================================
# Stitching logic
# =============================================================================

def apply_stitches(rivers: dict, river_shapes: list, orientation: str) -> tuple:
    """Process stitch_with declarations across rivers.

    Returns (effective_paths, suppressed_indices) where:
      effective_paths: {ord_idx: [cells, ...]} — final paths to render
      suppressed_indices: set of ord_idx values that got merged into others
    """
    suppressed = set()
    paths = {}

    for ord_idx, entry in rivers.items():
        flow = entry.get('flow', {})
        if 'stitch_with' in flow:
            # Skip — will be handled by the partner
            partner_str = flow.get('stitch_with', '')
            m = re.search(r'(\d+)', str(partner_str))
            if m:
                partner_ord = int(m.group(1))
                if partner_ord < ord_idx:
                    # Already processed by partner; mark this as suppressed
                    suppressed.add(ord_idx)
                    continue
                # Otherwise this entry is the "primary" — concatenate partner's path
                if partner_ord <= len(river_shapes) and ord_idx <= len(river_shapes):
                    a_cells = sample_path_cells(river_shapes[ord_idx - 1].points, orientation)
                    b_cells = sample_path_cells(river_shapes[partner_ord - 1].points, orientation)
                    # Apply direction reversal as needed
                    a_dir = (entry.get('flow', {}).get('direction', 'forward'))
                    b_dir = (rivers.get(partner_ord, {}).get('flow', {}).get('direction', 'forward'))
                    if a_dir == 'reverse':
                        a_cells = list(reversed(a_cells))
                    if b_dir == 'reverse':
                        b_cells = list(reversed(b_cells))
                    # Concatenate, dropping duplicate at join
                    if a_cells and b_cells and a_cells[-1] == b_cells[0]:
                        merged = a_cells + b_cells[1:]
                    else:
                        merged = a_cells + b_cells
                    paths[ord_idx] = merged
                    suppressed.add(partner_ord)
                continue
        # No stitch — apply own direction
        if ord_idx <= len(river_shapes):
            cells = sample_path_cells(river_shapes[ord_idx - 1].points, orientation)
            if entry.get('flow', {}).get('direction', 'forward') == 'reverse':
                cells = list(reversed(cells))
            paths[ord_idx] = cells

    return paths, suppressed


# =============================================================================
# Description block builder
# =============================================================================

def build_description(wmap, annotations: dict = None,
                      source_filename: str = '',
                      project_palette_overrides: dict = None,
                      project_terrain_reskins: dict = None,
                      terrain_glyph_fn=None) -> str:
    """Generate the canonical v2 description block.

    Args:
      wmap: parsed WxxMap
      annotations: dict from wxx_annotations.parse(), or None for scaffold mode
      source_filename: original .wxx filename for the title
      project_palette_overrides: project palette overrides (for legend "Project rendering" col)
      project_terrain_reskins: dict mapping terrain name → {glyph, description}
      terrain_glyph_fn: callable(terrain_name) -> char; if None, uses world.py defaults

    Returns the description as a single string (lines joined with \\n).
    """
    if annotations is None:
        annotations = {}
    if project_palette_overrides is None:
        project_palette_overrides = {}
    if project_terrain_reskins is None:
        project_terrain_reskins = {}

    is_square = wmap.hex_orientation == 'SQUARE'
    orientation = wmap.hex_orientation
    cols, rows = wmap.tiles_wide, wmap.tiles_high

    out = []

    # ── Map ────────────────────────────────────────────────
    title = source_filename.replace('.wxx', '') if source_filename else 'map'
    out.append('## Map')
    out.append(f'name: {title}')
    out.append(f'type: {wmap.map_type}')
    out.append(f'orientation: {orientation}')
    out.append(f'size: {cols} cols × {rows} rows')
    out.append('coordinate_system: (col, row), (0,0) at top-left')
    if orientation == 'COLUMNS':
        out.append('hex_layout: flat-top, odd columns shift down')
    elif orientation == 'ROWS':
        out.append('hex_layout: pointy-top, odd rows shift right')
    elif orientation == 'SQUARE':
        out.append('hex_layout: square grid, no offsets')
    out.append('')

    # ── Project ────────────────────────────────────────────
    project = annotations.get('project', 'default')
    out.append('## Project')
    out.append(f'project: {project}')
    out.append('')

    # ── Intent ─────────────────────────────────────────────
    intent_format = annotations.get('intent_format', [])
    intent_narrative = annotations.get('intent_narrative', [])
    if intent_format or intent_narrative:
        out.append('## Intent')
        out.append('')
        if intent_format:
            out.append('### Format')
            for line in intent_format:
                out.append(f'- {line}')
            out.append('')
        if intent_narrative:
            out.append('### Narrative')
            for line in intent_narrative:
                out.append(f'- {line}')
            out.append('')

    # ── Terrain Legend ─────────────────────────────────────
    if not is_square and wmap.terrain:
        used_terrains = set()
        for col in wmap.grid:
            for tid in col:
                used_terrains.add(tid)

        out.append('## Terrain Legend')
        out.append('')
        out.append('| Glyph | Terrain (Worldographer name) | Project rendering |')
        out.append('|=======|==============================|===================|')
        for tid in sorted(used_terrains):
            name = wmap.terrain.get(tid, f'unknown:{tid}')
            glyph = _resolve_glyph(name, project_terrain_reskins, terrain_glyph_fn)
            project_note = ''
            if name in project_terrain_reskins:
                reskin = project_terrain_reskins[name]
                if isinstance(reskin, dict) and 'description' in reskin:
                    project_note = f"**{reskin['description']}** (reskin)"
            elif name in project_palette_overrides:
                project_note = '(palette override)'
            else:
                project_note = '(default)'
            out.append(f'| `{glyph}` | {name} (id {tid}) | {project_note} |')
        out.append('')

    # ── Elevation ──────────────────────────────────────────
    if not is_square:
        elev_overrides = annotations.get('elevation_overrides', {})
        out.append('## Elevation')
        out.append('')
        out.append('defaults_by_terrain:')
        out.append('  Mountains*:        1500-3000m')
        out.append('  Mountain Forest*:  1200-2200m')
        out.append('  Hills*:            300-800m')
        out.append('  Flat Forest*:      50-300m')
        out.append('  Flat Farmland*:    20-150m')
        out.append('  Wetlands*:         0-50m')
        out.append('  Water*:            0m')
        out.append('')
        if elev_overrides:
            out.append('overrides:')
            for cell, val in sorted(elev_overrides.items()):
                out.append(f'  ({cell[0]}, {cell[1]}): {val}')
        else:
            out.append('overrides: (none)')
        out.append('')

    # ── Grid ───────────────────────────────────────────────
    if not is_square:
        out.append('## Grid')
        out.append('')
        if orientation == 'ROWS':
            out.append('Each row is one hex-row; odd rows are visually shifted right by half a hex.')
        elif orientation == 'COLUMNS':
            out.append('Each row is one hex-row; columns are vertical, odd columns shifted down by half a hex.')
        out.append('')
        out.append('```')
        # Column header rulers
        if cols <= 100:
            row_label_width = 4
            tens = ' ' * row_label_width
            ones = ' ' * row_label_width
            for c in range(cols):
                tens += str(c // 10) if c % 10 == 0 else ' '
                ones += str(c % 10)
            out.append(tens)
            out.append(ones)
        # Rows
        for r in range(rows):
            line = []
            for c in range(cols):
                if c < len(wmap.grid) and r < len(wmap.grid[c]):
                    tid = wmap.grid[c][r]
                    name = wmap.terrain.get(tid, '')
                    ch = _resolve_glyph(name, project_terrain_reskins, terrain_glyph_fn)
                    if (c < len(wmap.polar) and r < len(wmap.polar[c])
                            and wmap.polar[c][r]):
                        ch = '*' if ch in (' ', '~', '.', ',') else ch.upper()
                    line.append(ch)
                else:
                    line.append(' ')
            prefix = '  ' if (orientation == 'ROWS' and r % 2 == 1) else ''
            out.append(f'{r:3d} {prefix}{"".join(line)}')
        out.append('```')
        out.append('')
        out.append('Polar/arctic overlay tiles shown uppercase or with `*` for ocean/farmland.')
        out.append('')

    # ── Features ───────────────────────────────────────────
    real_features = [f for f in wmap.features if 'Coast' not in f.type]
    feature_visibility = annotations.get('feature_visibility', {})
    feature_names = annotations.get('feature_names', {})

    if real_features:
        out.append(f'## Features ({len(real_features)})')
        out.append('')
        out.append('| Cell | Type | Label | Visibility |')
        out.append('|======|======|=======|============|')
        for f in sorted(real_features, key=lambda f: (f.y, f.x)):
            if is_square:
                cell = world_to_square(f.x, f.y)
            else:
                cell = world_to_hex(f.x, f.y, orientation)
            short = f.type.split('/', 1)[-1] if '/' in f.type else f.type
            label = f.label or feature_names.get(cell, '')
            if not label:
                label = '(unlabeled)'
            vis = feature_visibility.get(cell, 'known')
            out.append(f'| ({cell[0]},{cell[1]}) | {short} | {label} | {vis} |')
        out.append('')

    # ── Linear Features ────────────────────────────────────
    if not is_square:
        _cat = lambda s: classify_shape_tag(s.tag, getattr(s, 'shape_type', 'Path'))
        road_shapes  = [s for s in wmap.shapes if _cat(s) in ('road', 'bridge')]
        river_shapes = [s for s in wmap.shapes if _cat(s) == 'river']
        wall_shapes  = [s for s in wmap.shapes if _cat(s) == 'wall']
        moat_shapes  = [s for s in wmap.shapes if _cat(s) == 'moat']

        if road_shapes or river_shapes:
            out.append('## Linear Features')
            out.append('# @ref tags on path cells resolve to full definitions in Entity Definitions below.')
            out.append('')

            roads_anno = annotations.get('roads', {})
            for ord_idx, shape in enumerate(road_shapes, start=1):
                entry = roads_anno.get(ord_idx, {})
                name = entry.get('name', shape.tag if shape.tag else f'road {ord_idx}')
                width_ft = stroke_to_feet(shape.stroke_width)
                default_base = f'{shape.tag}, width≈{width_ft}ft' if shape.tag else f'unspecified surface, width≈{width_ft}ft'
                base = entry.get('base', default_base)
                flow = entry.get('flow', {})
                conditions = entry.get('conditions', {})
                cells = sample_path_cells(shape.points, orientation)

                out.append(f'### road {ord_idx}')
                out.append(f'name: {name}')
                out.append(f'base: {base}')
                if flow:
                    out.append('flow:')
                    for k in ('primary_endpoint', 'secondary_endpoint'):
                        if k in flow:
                            out.append(f'  {k}: {flow[k]}')
                if cells:
                    out.append(f'path: {format_path_with_inheritance(cells, conditions)}')
                out.append('')

            rivers_anno = annotations.get('rivers', {})
            stitched_paths, suppressed = apply_stitches(rivers_anno, river_shapes, orientation)
            for ord_idx, shape in enumerate(river_shapes, start=1):
                if ord_idx in suppressed:
                    continue
                entry = rivers_anno.get(ord_idx, {})
                name = entry.get('name', f'river {ord_idx}')
                base = entry.get('base', 'unspecified width, unknown current')
                flow = entry.get('flow', {})
                conditions = entry.get('conditions', {})

                # Use stitched path if applicable, otherwise the shape's own
                if ord_idx in stitched_paths:
                    cells = stitched_paths[ord_idx]
                else:
                    cells = sample_path_cells(shape.points, orientation)
                    # Apply direction reversal even without stitching
                    if flow.get('direction', 'forward') == 'reverse':
                        cells = list(reversed(cells))

                out.append(f'### river {ord_idx}')
                out.append(f'name: {name}')
                out.append(f'base: {base}')
                if flow:
                    out.append('flow:')
                    for k in ('origin', 'origin_cell', 'termination', 'termination_cell',
                              'direction', 'stitch_with'):
                        if k in flow:
                            v = flow[k]
                            if isinstance(v, tuple):
                                v = f'({v[0]}, {v[1]})'
                            out.append(f'  {k}: {v}')
                if cells:
                    out.append(f'path: {format_path_with_inheritance(cells, conditions)}')
                out.append('')

    # ── Entity Definitions ─────────────────────────────────
    linear_details = annotations.get('linear_details', {})
    if linear_details:
        out.append('## Entity Definitions')
        out.append('# Full definitions for all @ref tags used in Linear Features above.')
        out.append('')
        out.append('| Entity | Type | Description |')
        out.append('|========|======|=============|')
        for ref_id in sorted(linear_details.keys()):
            details = linear_details[ref_id]
            ref_type = details.get('type', '')
            desc_parts = []
            if 'name' in details:
                desc_parts.append(details['name'] + '.')
            for k in ('material', 'length_m', 'difficulty', 'fee', 'controlled_by', 'note'):
                if k in details and details[k]:
                    desc_parts.append(f'{k}: {details[k]}.')
            description = ' '.join(desc_parts)
            out.append(f'| @{ref_id} | {ref_type} | {description} |')
        out.append('')

    # ── Walls ──────────────────────────────────────────────
    walls_anno = annotations.get('walls', [])
    if not is_square and (wall_shapes or walls_anno):
        out.append('## Walls')
        out.append('')
        for ord_idx, shape in enumerate(wall_shapes, start=1):
            entry = next((w for w in walls_anno if w.get('id') == f'wall {ord_idx}'), {})
            name = entry.get('name', shape.tag if shape.tag else f'wall {ord_idx}')
            cells = sample_path_cells(shape.points, orientation)
            out.append(f'### wall {ord_idx}')
            out.append(f'name: {name}')
            for k in ('type', 'height_m', 'thickness_m', 'condition'):
                v = entry.get(k, '')
                if v:
                    out.append(f'{k}: {v}')
            for k in ('towers', 'gates'):
                v = entry.get(k, '')
                if v:
                    out.append(f'{k}: {v}')
            note = entry.get('note', '')
            if note:
                out.append(f'note: {note}')
            if cells:
                out.append(f'path: {format_path_with_inheritance(cells, {})}')
            out.append('')

    # ── Moat ───────────────────────────────────────────────
    moats_anno = annotations.get('moats', [])
    if not is_square and (moat_shapes or moats_anno):
        out.append('## Moat')
        out.append('')
        for ord_idx, shape in enumerate(moat_shapes, start=1):
            entry = next((m for m in moats_anno if m.get('id') == f'moat {ord_idx}'), {})
            name = entry.get('name', shape.tag if shape.tag else f'moat {ord_idx}')
            cells = sample_path_cells(shape.points, orientation)
            out.append(f'### moat {ord_idx}')
            out.append(f'name: {name}')
            for k in ('source', 'width_m', 'depth_m', 'condition', 'is_river_segment'):
                v = entry.get(k, '')
                if v:
                    out.append(f'{k}: {v}')
            note = entry.get('note', '')
            if note:
                out.append(f'note: {note}')
            if cells:
                out.append(f'path: {format_path_with_inheritance(cells, {})}')
            out.append('')

    # ── Districts ──────────────────────────────────────────
    districts = annotations.get('districts', [])
    if districts:
        out.append('## Districts')
        out.append('# Named areas delineated as polygons on the map.')
        out.append('')
        out.append('| District | Visibility | Description |')
        out.append('|==========|============|=============|')
        for d in districts:
            name = d.get('name', '(unnamed)')
            vis = d.get('visibility', 'known')
            desc = d.get('description', '')
            if desc == 'TODO':
                desc = ''
            note = d.get('note', '')
            full_desc = '. '.join(x for x in (desc, note) if x and x != 'TODO')
            out.append(f'| {name} | {vis} | {full_desc} |')
        out.append('')

    # ── Points of Interest ─────────────────────────────────
    pois = annotations.get('pois', [])
    if pois:
        out.append(f'## Points of Interest ({len(pois)})')
        out.append('')
        for poi in pois:
            out.append(f"### {poi.get('id', 'poi')}")
            for k in ('name', 'type', 'cell', 'visibility', 'description', 'note'):
                v = poi.get(k, '')
                if isinstance(v, tuple):
                    v = f'({v[0]}, {v[1]})'
                if v:
                    out.append(f'{k}: {v}')
            out.append('')

    # ── Feature Visibility Overrides ───────────────────────
    if feature_visibility:
        out.append('## Feature Visibility Overrides')
        out.append('')
        for cell, vis in sorted(feature_visibility.items()):
            out.append(f'({cell[0]}, {cell[1]}): {vis}')
        out.append('')

    # ── Settlement Connectivity ────────────────────────────
    if not is_square and real_features and (any(s.tag in ('road', 'river') for s in wmap.shapes)):
        out.append('## Settlement Connectivity')
        out.append('')
        # Build cell → list of (tag, ord_idx) ownership map
        cell_owners = defaultdict(list)
        road_shapes = [s for s in wmap.shapes if s.tag == 'road']
        river_shapes = [s for s in wmap.shapes if s.tag == 'river']
        for ord_idx, s in enumerate(road_shapes, start=1):
            for cell in sample_path_cells(s.points, orientation):
                cell_owners[cell].append(('road', ord_idx))
        for ord_idx, s in enumerate(river_shapes, start=1):
            for cell in sample_path_cells(s.points, orientation):
                cell_owners[cell].append(('river', ord_idx))

        out.append('| Settlement | Cell | Touched by |')
        out.append('|============|======|============|')
        # Sort by label
        labeled = []
        for f in real_features:
            if is_square:
                cell = world_to_square(f.x, f.y)
            else:
                cell = world_to_hex(f.x, f.y, orientation)
            label = f.label or feature_names.get(cell, '')
            if label:
                labeled.append((label, cell))
        for label, cell in sorted(labeled):
            owners = list(cell_owners.get(cell, []))
            for dc, dr in [(-1, 0), (1, 0), (0, -1), (0, 1),
                           (-1, -1), (1, -1), (-1, 1), (1, 1)]:
                owners.extend(cell_owners.get((cell[0] + dc, cell[1] + dr), []))
            unique = sorted(set(owners))
            owner_str = ', '.join(f'{t}#{i}' for t, i in unique) or '(none)'
            out.append(f'| {label} | ({cell[0]},{cell[1]}) | {owner_str} |')
        out.append('')

        # ── Reachability ───────────────────────────────────
        out.append('## Reachability')
        out.append('')
        out.append('| Settlement | Cell | Reachable via |')
        out.append('|============|======|===============|')
        # For each settlement, find which other settlements share each road/river
        settlement_cells = {label: cell for label, cell in labeled}
        # Pre-compute which settlements are touched by each (tag, ord)
        feature_per_path = defaultdict(set)
        for label, cell in labeled:
            owners = list(cell_owners.get(cell, []))
            for dc, dr in [(-1, 0), (1, 0), (0, -1), (0, 1),
                           (-1, -1), (1, -1), (-1, 1), (1, 1)]:
                owners.extend(cell_owners.get((cell[0] + dc, cell[1] + dr), []))
            for tag, ord_idx in set(owners):
                feature_per_path[(tag, ord_idx)].add(label)

        for label, cell in sorted(labeled):
            owners = list(cell_owners.get(cell, []))
            for dc, dr in [(-1, 0), (1, 0), (0, -1), (0, 1),
                           (-1, -1), (1, -1), (-1, 1), (1, 1)]:
                owners.extend(cell_owners.get((cell[0] + dc, cell[1] + dr), []))
            unique = sorted(set(owners))
            reach_lines = []
            for tag, ord_idx in unique:
                others = sorted(feature_per_path[(tag, ord_idx)] - {label})
                if others:
                    reach_lines.append(f'{tag}#{ord_idx}: {", ".join(others)}')
                else:
                    reach_lines.append(f'{tag}#{ord_idx}: (no other labelled features)')
            out.append(f'| {label} | ({cell[0]},{cell[1]}) | {"; ".join(reach_lines) or "(none)"} |')
        out.append('')

    return '\n'.join(out)


# =============================================================================
# Helpers
# =============================================================================

def _resolve_glyph(terrain_name: str,
                   project_terrain_reskins: dict,
                   terrain_glyph_fn) -> str:
    """Look up the glyph for a terrain, applying project reskins if any."""
    if not terrain_name:
        return '?'
    if terrain_name in project_terrain_reskins:
        reskin = project_terrain_reskins[terrain_name]
        if isinstance(reskin, dict) and 'glyph' in reskin:
            return reskin['glyph']
    if terrain_glyph_fn:
        return terrain_glyph_fn(terrain_name)
    # Built-in fallback (mirrors terrain/world.py)
    bare = terrain_name.split('/', 1)[-1]
    fallback = {
        'Water Ocean': '~', 'Water Sea': '~', 'Mountains': '^',
        'Mountains Forest Evergreen': 'M', 'Mountain Forest Evergreen': 'M',
        'Hills Forest Evergreen': 'H', 'Hills': 'h',
        'Flat Forest Evergreen': 'f', 'Flat Forest Evergreen Heavy': 'F',
        'Flat Farmland': '.', 'Flat Grassland': ',',
        'Flat Desert Rocky': 'd', 'Flat Desert Dunes': 'd',
        'Underdark Open': '?', 'Blank': ' ',
    }
    return fallback.get(bare, '?')


# =============================================================================
# CLI for standalone .md generation
# =============================================================================

def main():
    import sys
    import argparse
    from wxx_to_svg import load_wxx, parse_wxx
    from wxx_annotations import load_annotations, annotation_path_for

    ap = argparse.ArgumentParser(description='Generate v2 description block from a .wxx')
    ap.add_argument('input', help='Path to .wxx file')
    ap.add_argument('output', help='Path to output .md (the description only, no SVG)')
    ap.add_argument('--annotations', default=None,
                    help='Path to annotation file (default: <output_basename>.annotations.md)')
    args = ap.parse_args()

    xml = load_wxx(args.input)
    wmap = parse_wxx(xml)

    # Try to load annotations
    annot_path = args.annotations or annotation_path_for(args.output)
    annotations = None
    import os
    if os.path.exists(annot_path):
        from wxx_annotations import parse as parse_anno
        with open(annot_path, 'r', encoding='utf-8') as f:
            annotations = parse_anno(f.read())
        print(f'[anno] loaded {annot_path}')

    desc = build_description(
        wmap, annotations,
        source_filename=os.path.basename(args.input),
    )
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(desc)
    print(f'[md] {args.output}: {len(desc):,} chars (~{len(desc)//3.5:.0f} tokens)')


if __name__ == '__main__':
    main()
