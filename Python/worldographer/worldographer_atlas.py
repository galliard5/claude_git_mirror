"""
worldographer_atlas.py — Generate a visual reference atlas SVG (and PNG).

The atlas is a project-scoped reference sheet that renders every terrain
glyph, every icon, every visibility level, and example linear features —
all with labels — to give an author a quick lookup when writing annotations.

Output: <Project>_<Scale>_Atlas.svg (and optional .png).

Pulls live from:
  - worldographer_palette.py  for authoritative terrain colors
  - projects/<name>.py         for project palette overrides + reskins
  - icons/<scale>.py           for icon vocabulary at the requested scale
  - terrain/<scale>.py         for glyph mapping and decorations

Usage:
    python worldographer_atlas.py output.svg
    python worldographer_atlas.py output.svg --project aethelmark --scale world
    python worldographer_atlas.py output.svg --width 2000
"""
from __future__ import annotations
import os, sys, argparse, datetime, html


# Reuse hex geometry from the renderer — column-layout flat-top hex
HEX_W = 300.0
HEX_H = 300.0
HEX_HALF_W = 150.0
HEX_HALF_H = 150.0
HEX_QUARTER = 75.0


def hex_polygon(cx, cy):
    return [
        (cx - HEX_HALF_W, cy),
        (cx - HEX_QUARTER, cy - HEX_HALF_H),
        (cx + HEX_QUARTER, cy - HEX_HALF_H),
        (cx + HEX_HALF_W, cy),
        (cx + HEX_QUARTER, cy + HEX_HALF_H),
        (cx - HEX_QUARTER, cy + HEX_HALF_H),
    ]


def _setup_imports():
    """Add the worldographer dir to sys.path so siblings are importable."""
    here = os.path.dirname(os.path.abspath(__file__))
    if here not in sys.path:
        sys.path.insert(0, here)


def _load_project(name):
    if not name:
        name = 'default'
    try:
        from projects import load
        return load(name)
    except Exception as e:
        print(f'  WARN: could not load project {name!r}: {e}')
        return None


def _build_palette(project_module):
    try:
        from worldographer_palette import TERRAIN_COLORS
    except ImportError:
        TERRAIN_COLORS = {}
    base = dict(TERRAIN_COLORS)
    if project_module:
        base.update(getattr(project_module, 'PALETTE_OVERRIDES', {}))
    return base


# =============================================================================
# Atlas section builders
# =============================================================================

def _section_header(out, title, x, y, width):
    out.append(f'<rect x="{x}" y="{y - 50}" width="{width}" height="60" '
               f'fill="#3a1410" rx="6"/>')
    out.append(f'<text x="{x + 24}" y="{y - 8}" font-size="36" font-weight="bold" '
               f'fill="#f5ecd2">{html.escape(title)}</text>')


def _draw_terrain_palette(out, palette, terrain_glyph_fn, project_reskins,
                           x_origin, y_origin, max_width):
    """Render every terrain in the project palette as a labeled hex tile."""
    _section_header(out, 'TERRAIN PALETTE', x_origin, y_origin, max_width)
    y = y_origin + 40

    # Filter to relevant entries — Classic and project overrides only
    relevant = [(name, color) for name, color in sorted(palette.items())
                if name.startswith('Classic/')]

    cell_w = 460
    cell_h = 200
    cols_per_row = max(1, max_width // cell_w)
    for i, (name, color) in enumerate(relevant):
        col = i % cols_per_row
        row = i // cols_per_row
        cx = x_origin + col * cell_w + cell_w / 2 + 30
        cy = y + row * cell_h + 90
        # Hex
        pts = hex_polygon(cx, cy)
        scale = 0.55
        sx, sy = pts[0]
        # Scale points around center
        scaled = [(cx + (px - cx) * scale, cy + (py - cy) * scale) for px, py in pts]
        pts_str = ' '.join(f'{x:.1f},{y:.1f}' for x, y in scaled)
        out.append(f'<polygon points="{pts_str}" fill="{color}" '
                   f'stroke="#3a1410" stroke-width="2"/>')
        # Glyph
        glyph = terrain_glyph_fn(name) if terrain_glyph_fn else '?'
        if name in project_reskins:
            r = project_reskins[name]
            if isinstance(r, dict) and 'glyph' in r:
                glyph = r['glyph']
        out.append(f'<text x="{cx:.0f}" y="{cy + 12:.0f}" font-size="44" '
                   f'font-family="monospace" font-weight="bold" '
                   f'text-anchor="middle">{html.escape(glyph)}</text>')
        # Star marker for project overrides
        is_override = name in (project_reskins or {}) or '★'
        if name in (project_reskins or {}):
            out.append(f'<text x="{cx + 110:.0f}" y="{cy - 80:.0f}" font-size="32" '
                       f'fill="#a04a2e">★</text>')
        # Label
        bare = name.split('/', 1)[-1]
        out.append(f'<text x="{cx:.0f}" y="{cy + 110:.0f}" font-size="22" '
                   f'text-anchor="middle" fill="#1a0e05">{html.escape(bare[:32])}</text>')

    rows_used = (len(relevant) + cols_per_row - 1) // cols_per_row
    return y_origin + 40 + rows_used * cell_h + 80


def _draw_icon_catalog(out, icon_module, x_origin, y_origin, max_width):
    """Render every icon in the library, organised by category."""
    _section_header(out, 'ICON CATALOG', x_origin, y_origin, max_width)
    y = y_origin + 40

    types_by_cat = icon_module.list_types()
    icon_w = 220
    icon_h = 180
    cols_per_row = max(1, max_width // icon_w)

    for category, names in types_by_cat.items():
        # Category header
        out.append(f'<text x="{x_origin}" y="{y + 30}" font-size="28" '
                   f'font-weight="bold" fill="#3a1410">{html.escape(category)}</text>')
        y += 50
        for i, name in enumerate(names):
            col = i % cols_per_row
            row = i // cols_per_row
            cx = x_origin + col * icon_w + icon_w / 2
            cy = y + row * icon_h + icon_h / 2 - 20
            try:
                snippet = icon_module.ICONS[name](cx, cy, scale=1.6)
                out.append(snippet)
            except Exception as e:
                out.append(f'<text x="{cx}" y="{cy}" text-anchor="middle" '
                           f'font-size="20" fill="#a04a2e">err: {e}</text>')
            out.append(f'<text x="{cx:.0f}" y="{cy + 70:.0f}" font-size="20" '
                       f'text-anchor="middle" fill="#1a0e05" '
                       f'font-family="monospace">{html.escape(name)}</text>')
        rows_used = (len(names) + cols_per_row - 1) // cols_per_row
        y += rows_used * icon_h + 30

    return y + 40


def _draw_visibility_examples(out, icon_module, x_origin, y_origin, max_width):
    """Show the same icon at each visibility level."""
    _section_header(out, 'VISIBILITY LEVELS', x_origin, y_origin, max_width)
    y = y_origin + 100

    sample_icon = 'village' if 'village' in icon_module.ICONS else next(iter(icon_module.ICONS))
    levels = [
        ('known', 'Known: visible everywhere with full label'),
        ('local', 'Local: rendered without label on player maps; full on GM'),
        ('hidden', 'Hidden: GM-only; rendered ghosted with dashed outline on GM'),
    ]
    spacing = max_width // (len(levels) + 1)
    for i, (vis, desc) in enumerate(levels):
        cx = x_origin + spacing * (i + 1)
        cy = y
        snippet = icon_module.ICONS[sample_icon](cx, cy, scale=2.0, visibility=vis)
        out.append(snippet)
        out.append(f'<text x="{cx:.0f}" y="{cy + 80:.0f}" font-size="22" '
                   f'text-anchor="middle" font-weight="bold" '
                   f'fill="#3a1410">{vis}</text>')
        # Description wraps
        words = desc.split()
        line1 = []
        line2 = []
        cur = line1
        char_count = 0
        for w in words:
            if char_count + len(w) > 28 and cur is line1:
                cur = line2
                char_count = 0
            cur.append(w)
            char_count += len(w) + 1
        out.append(f'<text x="{cx:.0f}" y="{cy + 110:.0f}" font-size="18" '
                   f'text-anchor="middle" fill="#1a0e05">{html.escape(" ".join(line1))}</text>')
        if line2:
            out.append(f'<text x="{cx:.0f}" y="{cy + 132:.0f}" font-size="18" '
                       f'text-anchor="middle" fill="#1a0e05">{html.escape(" ".join(line2))}</text>')
    return y + 200


def _draw_linear_samples(out, x_origin, y_origin, max_width):
    """Show a road and a river with a few path conditions on each."""
    _section_header(out, 'LINEAR FEATURE SAMPLES', x_origin, y_origin, max_width)
    y = y_origin + 50

    # Road sample
    out.append(f'<text x="{x_origin}" y="{y + 20}" font-size="20" '
               f'font-family="monospace" fill="#1a0e05">'
               f'### road 1: King\'s High Road</text>')
    y += 30
    out.append(f'<text x="{x_origin}" y="{y + 20}" font-size="18" '
               f'font-family="monospace" fill="#1a0e05">'
               f'base: dirt road, narrow, wagon-passable</text>')
    y += 25
    out.append(f'<text x="{x_origin}" y="{y + 20}" font-size="18" '
               f'font-family="monospace" fill="#1a0e05">'
               f'path: (31,23):surface=stone,width=2|(30,23)|(29,22)|(28,22):surface=gravel,width=1|...</text>')
    y += 50
    # Visual: dashed road line
    out.append(f'<line x1="{x_origin + 80}" y1="{y + 20}" '
               f'x2="{x_origin + max_width - 80}" y2="{y + 20}" '
               f'stroke="#5a3d1d" stroke-width="14" stroke-linecap="round" opacity="0.8"/>')
    out.append(f'<line x1="{x_origin + 80}" y1="{y + 20}" '
               f'x2="{x_origin + max_width - 80}" y2="{y + 20}" '
               f'stroke="#c9a766" stroke-width="8" stroke-linecap="round" '
               f'stroke-dasharray="14 10"/>')
    y += 60

    # River sample
    out.append(f'<text x="{x_origin}" y="{y + 20}" font-size="20" '
               f'font-family="monospace" fill="#1a0e05">'
               f'### river 1: Silberbach River</text>')
    y += 30
    out.append(f'<text x="{x_origin}" y="{y + 20}" font-size="18" '
               f'font-family="monospace" fill="#1a0e05">'
               f'base: navigable, 15-30m wide, moderate current</text>')
    y += 25
    out.append(f'<text x="{x_origin}" y="{y + 20}" font-size="18" '
               f'font-family="monospace" fill="#1a0e05">'
               f'flow: origin=Mt Aldenberg, termination=Northern Sea, direction=forward</text>')
    y += 25
    out.append(f'<text x="{x_origin}" y="{y + 20}" font-size="18" '
               f'font-family="monospace" fill="#1a0e05">'
               f'path: (-1,4)|(0,5)|...|(25,18):ref=bridge#1|...|(32,26):flow=rapids|...</text>')
    y += 50
    # Visual: river line
    out.append(f'<line x1="{x_origin + 80}" y1="{y + 20}" '
               f'x2="{x_origin + max_width - 80}" y2="{y + 20}" '
               f'stroke="#3a6a8a" stroke-width="28" stroke-linecap="round" opacity="0.55"/>')
    out.append(f'<line x1="{x_origin + 80}" y1="{y + 20}" '
               f'x2="{x_origin + max_width - 80}" y2="{y + 20}" '
               f'stroke="#6fa9d3" stroke-width="18" stroke-linecap="round"/>')
    y += 60

    return y + 30


def _draw_polar_sample(out, terrain_glyph_fn, x_origin, y_origin, max_width):
    """Show a hex with and without polar overlay for comparison."""
    _section_header(out, 'POLAR / ARCTIC OVERLAY', x_origin, y_origin, max_width)
    y = y_origin + 110

    cx_left = x_origin + max_width / 4
    cx_right = x_origin + max_width * 3 / 4

    # Normal water hex
    pts_l = hex_polygon(cx_left, y)
    pts_l = [(cx_left + (px - cx_left) * 0.6, y + (py - y) * 0.6) for px, py in pts_l]
    out.append(f'<polygon points="{" ".join(f"{x:.1f},{y2:.1f}" for x, y2 in pts_l)}" '
               f'fill="#1f5a85" stroke="#3a1410" stroke-width="2"/>')
    out.append(f'<text x="{cx_left:.0f}" y="{y + 10:.0f}" font-size="36" '
               f'font-family="monospace" font-weight="bold" text-anchor="middle">~</text>')
    out.append(f'<text x="{cx_left:.0f}" y="{y + 130:.0f}" font-size="22" '
               f'text-anchor="middle">Water Ocean (normal)</text>')

    # Polar-overlaid water hex
    pts_r = hex_polygon(cx_right, y)
    pts_r = [(cx_right + (px - cx_right) * 0.6, y + (py - y) * 0.6) for px, py in pts_r]
    pts_str = ' '.join(f"{x:.1f},{y2:.1f}" for x, y2 in pts_r)
    out.append(f'<polygon points="{pts_str}" fill="#1f5a85" stroke="#3a1410" stroke-width="2"/>')
    out.append(f'<polygon points="{pts_str}" fill="#f4faff" opacity="0.85"/>')
    out.append(f'<text x="{cx_right:.0f}" y="{y + 10:.0f}" font-size="36" '
               f'font-family="monospace" font-weight="bold" text-anchor="middle">*</text>')
    out.append(f'<text x="{cx_right:.0f}" y="{y + 130:.0f}" font-size="22" '
               f'text-anchor="middle">Water Ocean + polar overlay (frozen)</text>')

    return y + 200


def _draw_snippets(out, x_origin, y_origin, max_width):
    """Plain-text annotation reference snippets the author can copy-paste."""
    _section_header(out, 'ANNOTATION REFERENCE SNIPPETS', x_origin, y_origin, max_width)
    y = y_origin + 40

    snippets = [
        ('Empty road:', [
            '### road N',
            'name: Untitled Road',
            'base: dirt road, narrow',
            'flow:',
            '  primary_endpoint: ',
            '  secondary_endpoint: ',
            'conditions: {}',
        ]),
        ('Empty river:', [
            '### river N',
            'name: Untitled River',
            'base: shallow stream, 5m wide',
            'flow:',
            '  origin: ',
            '  origin_cell: (##, ##)',
            '  termination: ',
            '  termination_cell: (##, ##)',
            '  direction: forward',
            'conditions: {}',
        ]),
        ('POI template:', [
            '### poi#N',
            'name: ',
            'type: landmark',
            'cell: (##, ##)',
            'visibility: known',
            'description: ',
            'note: ',
        ]),
    ]

    col_w = max_width // len(snippets)
    for i, (title, lines) in enumerate(snippets):
        cx = x_origin + i * col_w + 20
        cy = y + 30
        out.append(f'<text x="{cx}" y="{cy}" font-size="22" font-weight="bold" '
                   f'fill="#3a1410">{html.escape(title)}</text>')
        for j, line in enumerate(lines):
            out.append(f'<text x="{cx}" y="{cy + 30 + j * 22}" font-size="16" '
                       f'font-family="monospace" fill="#1a0e05">{html.escape(line)}</text>')
    max_lines = max(len(lines) for _, lines in snippets)
    return y + 40 + 30 + max_lines * 22 + 40


# =============================================================================
# Atlas assembly
# =============================================================================

def build_atlas(project_name='default', scale='world'):
    """Build the full atlas SVG. Returns SVG string."""
    _setup_imports()
    project_module = _load_project(project_name)
    palette = _build_palette(project_module)
    project_reskins = (getattr(project_module, 'TERRAIN_RESKINS', {})
                       if project_module else {})

    # Load icon library for the requested scale
    if scale == 'world':
        from icons import world as icon_module
        from terrain.world import glyph_for as terrain_glyph_fn
    elif scale == 'town':
        from icons import town as icon_module
        from terrain.town import glyph_for as terrain_glyph_fn
    elif scale == 'battlemap':
        from icons import battlemap as icon_module
        from terrain.battlemap import glyph_for as terrain_glyph_fn
    elif scale == 'cosmic':
        from icons import cosmic as icon_module
        terrain_glyph_fn = lambda n: '?'
    else:
        raise ValueError(f'Unknown scale: {scale!r}')

    width = 4800
    pad = 60
    today = datetime.date.today().isoformat()

    out = []
    # Reserve viewBox; we'll patch height after we know it
    out.append('<!--PLACEHOLDER_SVG_OPEN-->')
    out.append(f'<rect x="0" y="0" width="{width}" height="100%" fill="#f0e3c2"/>')

    # Title
    out.append(f'<text x="{pad}" y="60" font-size="48" font-weight="bold" '
               f'font-family="Georgia, serif" fill="#3a1410">'
               f'Worldographer Atlas — Project: {html.escape(project_name)}, '
               f'Scale: {html.escape(scale)}</text>')
    out.append(f'<text x="{pad}" y="92" font-size="22" font-family="Georgia, serif" '
               f'fill="#5a3a1f">Generated {today} '
               f'· {len(palette)} terrain entries · {len(icon_module.ICONS)} icon types</text>')

    y = 160
    sec_x = pad
    sec_w = width - 2 * pad

    y = _draw_terrain_palette(out, palette, terrain_glyph_fn, project_reskins,
                              sec_x, y, sec_w)
    y = _draw_icon_catalog(out, icon_module, sec_x, y, sec_w)
    y = _draw_visibility_examples(out, icon_module, sec_x, y, sec_w)
    y = _draw_linear_samples(out, sec_x, y, sec_w)
    y = _draw_polar_sample(out, terrain_glyph_fn, sec_x, y, sec_w)
    y = _draw_snippets(out, sec_x, y, sec_w)

    height = int(y + 100)

    # Patch the SVG opener with the final height
    svg_open = (f'<svg xmlns="http://www.w3.org/2000/svg" '
                f'viewBox="0 0 {width} {height}" '
                f'font-family="Georgia, serif">')
    out[0] = svg_open
    out.append('</svg>')

    return '\n'.join(out)


# =============================================================================
# CLI
# =============================================================================

def main():
    ap = argparse.ArgumentParser(description='Generate a Worldographer atlas reference sheet')
    ap.add_argument('output', help='Path to output .svg')
    ap.add_argument('--project', default='default', help='Project name (default: default)')
    ap.add_argument('--scale', default='world',
                    choices=['world', 'town', 'battlemap', 'cosmic'],
                    help='Map scale (default: world)')
    ap.add_argument('--width', type=int, default=0,
                    help='If >0, also write a PNG at this pixel width (requires cairosvg)')
    args = ap.parse_args()

    print(f'[atlas] project={args.project}, scale={args.scale}')
    svg = build_atlas(project_name=args.project, scale=args.scale)
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(svg)
    print(f'[write] {args.output}: {len(svg):,} bytes')

    if args.width > 0:
        png_path = os.path.splitext(args.output)[0] + '.png'
        try:
            import cairosvg
            cairosvg.svg2png(url=args.output, write_to=png_path, output_width=args.width)
            print(f'[png] {png_path} (width={args.width})')
        except ImportError:
            print('  (cairosvg not installed; skipping PNG output)')


if __name__ == '__main__':
    main()
