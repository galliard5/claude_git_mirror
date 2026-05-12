"""
wxx_to_svg.py — v2 Worldographer renderer orchestrator.

Reads a .wxx file, optionally merges an annotation sidecar, renders an .svg
with a v2 description block embedded in the leading XML comment.

Three-state generation flow per Wxx_Map_Format_Spec.md §16.3:
  1. No annotation file       → scaffold mode (write annotations + diagnostic render)
  2. Annotation file present  → merge mode (production render with full styling)
  3. --regenerate-annotations → regenerate (back up existing → .previous.md, scaffold new)

Visibility flags govern the visible map (description block always carries everything):
  --player  → hide `hidden` POIs/features; show `local` features unlabeled
  --gm      → render everything (default)

Reference: Core_Rules/Wxx_Map_Format_Spec.md is the canonical format spec.
"""
from __future__ import annotations
import gzip, re, html, sys, os, argparse, datetime
from dataclasses import dataclass, field
from typing import Optional


# =============================================================================
# 1. CONFIGURATION
# =============================================================================

try:
    from worldographer_palette import TERRAIN_COLORS as _AUTHORITATIVE_PALETTE
except ImportError:
    _AUTHORITATIVE_PALETTE = {}

HEX_DEFAULT_COLOR = '#cccccc'

SQUARE_SHAPE_STYLES = {
    'ground':  {'fill': '#7a9a52', 'stroke': '#3a4a2a', 'stroke_width': 1.5},
    'floor':   {'fill': '#c4a878', 'stroke': '#3a2410', 'stroke_width': 1.5},
    'room':    {'fill': '#c4a878', 'stroke': '#3a2410', 'stroke_width': 1.5},
    'wall':    {'fill': 'none',    'stroke': '#1a1410', 'stroke_width': 12.0},
    'road':    {'fill': 'none',    'stroke': '#5a3d1d', 'stroke_width': 8.0},
    'river':   {'fill': 'none',    'stroke': '#6fa9d3', 'stroke_width': 12.0},
    None:      {'fill': 'none',    'stroke': '#444444', 'stroke_width': 4.0},
}


# =============================================================================
# 2. DATA STRUCTURES
# =============================================================================

@dataclass
class WxxFeature:
    type: str
    x: float
    y: float
    label: str = ''
    rotate: float = 0.0
    scale: float = 1.0
    flip_h: bool = False
    flip_v: bool = False

@dataclass
class WxxShape:
    tag: str
    creation_type: str
    is_curve: bool
    fill_color: Optional[str]
    fill_texture: Optional[str]
    stroke_color: Optional[str]
    stroke_width: float
    map_layer: str
    svg_path_d: str
    points: list = field(default_factory=list)

@dataclass
class WxxMap:
    map_type: str
    hex_orientation: str
    tiles_wide: int
    tiles_high: int
    terrain: dict
    grid: list
    polar: list
    features: list
    shapes: list
    layers: list


# =============================================================================
# 3. PARSER
# =============================================================================

def load_wxx(path: str) -> str:
    with gzip.open(path, 'rb') as f:
        raw = f.read()
    return raw.decode('utf-16-be')


def _attr(s, name, default=None):
    m = re.search(rf'\s{name}="([^"]*)"', s)
    return m.group(1) if m else default


def _parse_rgba_to_hex(rgba_str):
    if not rgba_str or rgba_str.strip() in ('null', '-'):
        return None
    try:
        nums = [float(x) for x in rgba_str.split(',')]
        r = max(0, min(255, int(round(nums[0] * 255))))
        g = max(0, min(255, int(round(nums[1] * 255))))
        b = max(0, min(255, int(round(nums[2] * 255))))
        return f'#{r:02x}{g:02x}{b:02x}'
    except (ValueError, IndexError):
        return None


def parse_shape_path(shape_xml):
    raw_points = []
    for m in re.finditer(r'<p\b([^/]*)/>', shape_xml):
        attrs = m.group(1)
        type_m = re.search(r'\stype="([mc])"', attrs)
        x_m = re.search(r'\sx\s*=\s*"([^"]+)"', attrs)
        y_m = re.search(r'\sy\s*=\s*"([^"]+)"', attrs)
        if not (x_m and y_m):
            continue
        ptype = type_m.group(1) if type_m else None
        x, y = float(x_m.group(1)), float(y_m.group(1))
        cx1 = cy1 = cx2 = cy2 = None
        if ptype == 'c':
            for a, b, dest in [('cx1', 'cy1', 0), ('cx2', 'cy2', 1)]:
                am = re.search(rf'{a}="([^"]+)"', attrs)
                bm = re.search(rf'{b}\s*=\s*"([^"]+)"', attrs)
                if am and bm:
                    if dest == 0:
                        cx1, cy1 = float(am.group(1)), float(bm.group(1))
                    else:
                        cx2, cy2 = float(am.group(1)), float(bm.group(1))
        raw_points.append((ptype, x, y, cx1, cy1, cx2, cy2))

    if not raw_points:
        return '', []

    d_parts = []
    pts = []
    for i, (ptype, x, y, cx1, cy1, cx2, cy2) in enumerate(raw_points):
        pts.append((x, y))
        if i == 0:
            d_parts.append(f'M {x:.2f},{y:.2f}')
        elif ptype == 'c' and cx1 is not None:
            d_parts.append(f'C {cx1:.2f},{cy1:.2f} {cx2:.2f},{cy2:.2f} {x:.2f},{y:.2f}')
        elif ptype == 'm':
            d_parts.append(f'M {x:.2f},{y:.2f}')
        else:
            d_parts.append(f'L {x:.2f},{y:.2f}')
    return ' '.join(d_parts), pts


def parse_wxx(xml):
    map_m = re.search(r'<map\s[^>]*>', xml).group()
    map_type = _attr(map_m, 'type', 'WORLD')
    hex_orient = _attr(map_m, 'hexOrientation', 'COLUMNS')
    tiles_m = re.search(r'<tiles\s[^>]*>', xml).group()
    tiles_wide = int(_attr(tiles_m, 'tilesWide', '0'))
    tiles_high = int(_attr(tiles_m, 'tilesHigh', '0'))
    layers = list(reversed(re.findall(r'<maplayer\s+name="([^"]+)"', xml)))

    terrain = {}
    tm_m = re.search(r'<terrainmap>([^<]*)</terrainmap>', xml)
    if tm_m:
        parts = tm_m.group(1).split('\t')
        for i in range(0, len(parts) - 1, 2):
            name, tid = parts[i].strip(), parts[i + 1].strip()
            if tid.lstrip('-').isdigit():
                terrain[int(tid)] = name

    tilerows = re.findall(r'<tilerow[^>]*>([^<]*)</tilerow>', xml)
    grid = []
    polar = []
    for col_text in tilerows:
        col_terrain = []
        col_polar = []
        for line in col_text.strip().split('\n'):
            if not line.strip():
                continue
            fields = line.split('\t')
            col_terrain.append(int(fields[0]))
            col_polar.append(len(fields) > 2 and fields[2] == '1')
        grid.append(col_terrain)
        polar.append(col_polar)

    features = []
    feat_pattern = re.compile(
        r'<feature\s+type="([^"]+)"([^>]*?)>'
        r'.*?<location\s+viewLevel="[^"]*"\s+x="([^"]+)"\s+y="([^"]+)"\s*/>'
        r'(?:.*?<label[^>]*?>.*?<location[^>]*/>([^<]*)</label>)?'
        r'\s*</feature>',
        re.DOTALL
    )
    for m in feat_pattern.finditer(xml):
        typ, attrs, x, y, lbl = m.groups()
        features.append(WxxFeature(
            type=typ, x=float(x), y=float(y),
            label=html.unescape(lbl).strip() if lbl else '',
            rotate=float(_attr(attrs, 'rotate', '0') or 0),
            scale=float(_attr(attrs, 'scale', '1') or 1),
            flip_h=(_attr(attrs, 'isFlipHorizontal', 'false') == 'true'),
            flip_v=(_attr(attrs, 'isFlipVertical', 'false') == 'true'),
        ))

    shapes = []
    for s_xml in re.findall(r'<shape\s.*?</shape>', xml, re.DOTALL):
        d, pts = parse_shape_path(s_xml)
        if not d or len(pts) < 2:
            continue
        shapes.append(WxxShape(
            tag=_attr(s_xml, 'tags', '') or '',
            creation_type=_attr(s_xml, 'creationType', 'BASIC') or 'BASIC',
            is_curve=(_attr(s_xml, 'isCurve', 'false') == 'true'),
            fill_color=_parse_rgba_to_hex(_attr(s_xml, 'fillColor', '') or ''),
            fill_texture=_attr(s_xml, 'fillTexture', '') or None,
            stroke_color=_parse_rgba_to_hex(_attr(s_xml, 'strokeColor', '') or ''),
            stroke_width=float(_attr(s_xml, 'strokeWidth', '1.0') or 1.0),
            map_layer=_attr(s_xml, 'mapLayer', '') or '',
            svg_path_d=d,
            points=pts,
        ))

    return WxxMap(
        map_type=map_type, hex_orientation=hex_orient,
        tiles_wide=tiles_wide, tiles_high=tiles_high,
        terrain=terrain, grid=grid, polar=polar,
        features=features, shapes=shapes, layers=layers,
    )


# =============================================================================
# 4. HEX GEOMETRY
# =============================================================================

HEX_W = 300.0
HEX_H = 300.0
HEX_HALF_W = 150.0
HEX_HALF_H = 150.0
HEX_QUARTER = 75.0


def hex_center_columns(col, row):
    cx = col * 0.75 * HEX_W + HEX_HALF_W
    cy = row * HEX_H + HEX_HALF_H
    if col % 2 == 1:
        cy += HEX_HALF_H
    return cx, cy


def hex_polygon_columns(col, row):
    cx, cy = hex_center_columns(col, row)
    return [
        (cx - HEX_HALF_W, cy),
        (cx - HEX_QUARTER, cy - HEX_HALF_H),
        (cx + HEX_QUARTER, cy - HEX_HALF_H),
        (cx + HEX_HALF_W, cy),
        (cx + HEX_QUARTER, cy + HEX_HALF_H),
        (cx - HEX_QUARTER, cy + HEX_HALF_H),
    ]


def hex_center_rows(col, row):
    cx = col * HEX_W + HEX_HALF_W
    cy = row * 0.75 * HEX_H + HEX_HALF_H
    if row % 2 == 1:
        cx += HEX_HALF_W
    return cx, cy


def hex_polygon_rows(col, row):
    cx, cy = hex_center_rows(col, row)
    return [
        (cx, cy - HEX_HALF_H),
        (cx + HEX_HALF_W, cy - HEX_QUARTER),
        (cx + HEX_HALF_W, cy + HEX_QUARTER),
        (cx, cy + HEX_HALF_H),
        (cx - HEX_HALF_W, cy + HEX_QUARTER),
        (cx - HEX_HALF_W, cy - HEX_QUARTER),
    ]


def hex_geometry_for(orientation):
    if orientation == 'ROWS':
        return hex_center_rows, hex_polygon_rows
    return hex_center_columns, hex_polygon_columns


def square_center(col, row, tile_size=300.0):
    return col * tile_size + tile_size / 2, row * tile_size + tile_size / 2


def _world_to_cell(wx, wy, orientation):
    if orientation == 'ROWS':
        row = round((wy - 150) / 225)
        if row % 2 == 1:
            col = round((wx - 300) / 300)
        else:
            col = round((wx - 150) / 300)
    elif orientation == 'SQUARE':
        col, row = int(wx // 300), int(wy // 300)
    else:
        col = round((wx - 150) / 225)
        if col % 2 == 0:
            row = round((wy - 150) / 300)
        else:
            row = round((wy - 300) / 300)
    return col, row


# =============================================================================
# 5. RENDERING HELPERS
# =============================================================================

def _build_palette(project_module):
    base = dict(_AUTHORITATIVE_PALETTE)
    if project_module:
        base.update(getattr(project_module, 'PALETTE_OVERRIDES', {}))
    return base


def _project_terrain_reskins(project_module):
    if project_module:
        return getattr(project_module, 'TERRAIN_RESKINS', {}) or {}
    return {}


# =============================================================================
# 6. HEX MAP RENDERER
# =============================================================================

def render_hex_map(wmap, *, project_module=None, render_mode='production',
                   visibility_filter='gm', annotations=None):
    """Render a hex map to SVG. Returns SVG string (no embedded comment header)."""
    if annotations is None:
        annotations = {}
    palette = _build_palette(project_module)
    bg_color = '#f0e3c2'
    if project_module:
        bg_color = getattr(project_module, 'HEX_BACKGROUND_COLOR', '#f0e3c2')

    # Lazy imports — circular-safe
    try:
        from icons import draw as draw_icon
    except Exception:
        draw_icon = None
    try:
        from terrain import decorations_for as terrain_decorations
    except Exception:
        terrain_decorations = lambda *a, **kw: ''

    hex_center, hex_polygon = hex_geometry_for(wmap.hex_orientation)
    cols, rows = wmap.tiles_wide, wmap.tiles_high
    all_centers = [hex_center(c, r) for c in range(cols) for r in range(rows)]
    min_x = min(c[0] for c in all_centers) - HEX_W
    max_x = max(c[0] for c in all_centers) + HEX_W
    min_y = min(c[1] for c in all_centers) - HEX_H
    max_y = max(c[1] for c in all_centers) + HEX_H

    out = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" '
               f'viewBox="{min_x:.0f} {min_y:.0f} {max_x-min_x:.0f} {max_y-min_y:.0f}" '
               f'font-family="Georgia, serif">')
    out.append(f'<rect x="{min_x:.0f}" y="{min_y:.0f}" width="{max_x-min_x:.0f}" '
               f'height="{max_y-min_y:.0f}" fill="{bg_color}"/>')

    # Terrain hexes
    out.append('<g id="terrain">')
    for col in range(cols):
        for row in range(min(rows, len(wmap.grid[col]) if col < len(wmap.grid) else 0)):
            tid = wmap.grid[col][row]
            terrain_name = wmap.terrain.get(tid, '')
            color = palette.get(terrain_name, HEX_DEFAULT_COLOR)
            pts = hex_polygon(col, row)
            pts_str = ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts)
            out.append(f'<polygon points="{pts_str}" fill="{color}"/>')
    out.append('</g>')

    # Terrain decorations from library
    out.append('<g id="terrain-decorations">')
    for col in range(cols):
        for row in range(min(rows, len(wmap.grid[col]) if col < len(wmap.grid) else 0)):
            tid = wmap.grid[col][row]
            terrain_name = wmap.terrain.get(tid, '')
            cx, cy = hex_center(col, row)
            try:
                deco = terrain_decorations(terrain_name, cx, cy, col, row,
                                           map_type=wmap.map_type)
            except Exception:
                deco = ''
            if deco:
                out.append(deco)
    out.append('</g>')

    # Polar overlay
    out.append('<g id="polar-overlay">')
    for col in range(cols):
        if col >= len(wmap.polar):
            continue
        for row in range(min(rows, len(wmap.polar[col]))):
            if not wmap.polar[col][row]:
                continue
            pts = hex_polygon(col, row)
            pts_str = ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts)
            out.append(f'<polygon points="{pts_str}" fill="#f4faff" opacity="0.85"/>')
    out.append('</g>')

    # Grid lines
    out.append('<g id="hex-grid" stroke="rgba(0,0,0,0.1)" stroke-width="2" fill="none">')
    for col in range(cols):
        for row in range(min(rows, len(wmap.grid[col]) if col < len(wmap.grid) else 0)):
            pts = hex_polygon(col, row)
            pts_str = ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts)
            out.append(f'<polygon points="{pts_str}"/>')
    out.append('</g>')

    # Per-cell coordinate stamps (scaffold mode)
    if render_mode == 'scaffold':
        out.append('<g id="cell-coords" font-family="monospace" fill="#666666" opacity="0.7">')
        for col in range(cols):
            for row in range(min(rows, len(wmap.grid[col]) if col < len(wmap.grid) else 0)):
                cx, cy = hex_center(col, row)
                out.append(f'<text x="{cx:.0f}" y="{cy + 110:.0f}" font-size="22" '
                           f'text-anchor="middle">({col},{row})</text>')
        out.append('</g>')

    # Edge coordinate labels (both modes; lighter in production)
    if render_mode == 'scaffold':
        edge_color = '#3a1410'
        edge_size = '52'
        edge_weight = 'bold'
    else:
        edge_color = 'rgba(58,20,16,0.5)'
        edge_size = '36'
        edge_weight = 'normal'
    out.append('<g id="edge-coords" font-family="monospace">')
    for col in range(cols):
        cx, _ = hex_center(col, 0)
        out.append(f'<text x="{cx:.0f}" y="{min_y + 80:.0f}" '
                   f'font-size="{edge_size}" font-weight="{edge_weight}" '
                   f'fill="{edge_color}" text-anchor="middle">{col}</text>')
    for row in range(rows):
        _, cy = hex_center(0, row)
        out.append(f'<text x="{min_x + 80:.0f}" y="{cy + 16:.0f}" '
                   f'font-size="{edge_size}" font-weight="{edge_weight}" '
                   f'fill="{edge_color}" text-anchor="middle">{row}</text>')
    out.append('</g>')

    # Shapes (rivers, roads)
    out.append('<g id="shapes">')
    for s in wmap.shapes:
        if s.tag == 'river':
            out.append(f'<path d="{s.svg_path_d}" fill="none" stroke="#3a6a8a" '
                       f'stroke-width="42" stroke-linecap="round" opacity="0.55"/>')
            out.append(f'<path d="{s.svg_path_d}" fill="none" stroke="#6fa9d3" '
                       f'stroke-width="26" stroke-linecap="round"/>')
        elif s.tag == 'road':
            out.append(f'<path d="{s.svg_path_d}" fill="none" stroke="#5a3d1d" '
                       f'stroke-width="22" stroke-linecap="round" opacity="0.8"/>')
            out.append(f'<path d="{s.svg_path_d}" fill="none" stroke="#c9a766" '
                       f'stroke-width="12" stroke-linecap="round" stroke-dasharray="20 14"/>')
        else:
            stroke = s.stroke_color or '#444444'
            fill = s.fill_color or 'none'
            out.append(f'<path d="{s.svg_path_d}" fill="{fill}" stroke="{stroke}" stroke-width="6"/>')
    out.append('</g>')

    # Features with visibility filtering
    feature_visibility = annotations.get('feature_visibility', {})
    feature_names = annotations.get('feature_names', {})
    out.append('<g id="features">')
    for f in wmap.features:
        if 'Coast' in f.type:
            continue
        cell = _world_to_cell(f.x, f.y, wmap.hex_orientation)
        vis = feature_visibility.get(cell, 'known')
        if visibility_filter == 'player' and vis == 'hidden':
            continue
        out.append(f'<circle cx="{f.x:.0f}" cy="{f.y:.0f}" r="20" fill="#b14a3a" '
                   f'stroke="#3a1410" stroke-width="3"/>')
        label = f.label or feature_names.get(cell, '')
        show_label = label and not (visibility_filter == 'player' and vis == 'local')
        if show_label:
            label_text = label
            if render_mode == 'scaffold':
                label_text = f'{label} ({cell[0]},{cell[1]})'
            out.append(f'<text x="{f.x:.0f}" y="{f.y + 60:.0f}" font-size="60" '
                       f'fill="#1a0e05" stroke="#f5ecd2" stroke-width="6" '
                       f'paint-order="stroke fill" text-anchor="middle" '
                       f'font-weight="bold">{html.escape(label_text)}</text>')
            if render_mode == 'production':
                out.append(f'<text x="{f.x:.0f}" y="{f.y + 92:.0f}" font-size="32" '
                           f'fill="#5a3a1f" text-anchor="middle" '
                           f'opacity="0.7">({cell[0]},{cell[1]})</text>')
    out.append('</g>')

    # POIs from annotation file
    pois = annotations.get('pois', [])
    if pois and draw_icon is not None:
        out.append('<g id="pois">')
        for poi in pois:
            cell = poi.get('cell')
            if not isinstance(cell, tuple):
                continue
            vis = poi.get('visibility', 'known')
            if visibility_filter == 'player' and vis == 'hidden':
                continue
            cx, cy = hex_center(cell[0], cell[1])
            ptype = poi.get('type', 'landmark')
            try:
                icon_svg = draw_icon(ptype, cx, cy, scale=2.0,
                                     map_type=wmap.map_type, visibility=vis)
                out.append(icon_svg)
            except ValueError as e:
                print(f'  WARN: POI {poi.get("id")}: {e}')
                continue
            label = poi.get('name', '')
            show_label = label and not (visibility_filter == 'player' and vis == 'local')
            if show_label:
                out.append(f'<text x="{cx:.0f}" y="{cy + 70:.0f}" font-size="48" '
                           f'fill="#1a0e05" stroke="#f5ecd2" stroke-width="5" '
                           f'paint-order="stroke fill" text-anchor="middle" '
                           f'font-weight="bold">{html.escape(label)}</text>')
        out.append('</g>')

    out.append('</svg>')
    return '\n'.join(out)


# =============================================================================
# 7. SQUARE / BATTLEMAP RENDERER (mostly v1 logic, project bg color)
# =============================================================================

def render_square_map(wmap, *, project_module=None, **kwargs):
    bg_color = '#ADD8E6'
    if project_module:
        bg_color = getattr(project_module, 'SQUARE_BACKGROUND_COLOR', '#ADD8E6')

    tile_size = 300.0
    pad = tile_size * 0.5
    width = wmap.tiles_wide * tile_size
    height = wmap.tiles_high * tile_size
    vb_x, vb_y = -pad, -pad
    vb_w, vb_h = width + 2 * pad, height + 2 * pad

    out = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" '
               f'viewBox="{vb_x:.0f} {vb_y:.0f} {vb_w:.0f} {vb_h:.0f}" '
               f'font-family="Arial, sans-serif">')
    out.append(f'<rect x="0" y="0" width="{width:.0f}" height="{height:.0f}" '
               f'fill="{bg_color}"/>')

    layer_index = {name: i for i, name in enumerate(wmap.layers)}
    sorted_shapes = sorted(wmap.shapes,
                            key=lambda s: layer_index.get(s.map_layer, len(wmap.layers)))

    out.append('<g id="shapes">')
    for s in sorted_shapes:
        tag_style = SQUARE_SHAPE_STYLES.get(s.tag, SQUARE_SHAPE_STYLES[None])
        fill = s.fill_color or tag_style.get('fill', 'none')
        stroke = s.stroke_color or tag_style.get('stroke', '#444')
        if s.tag == 'wall':
            stroke_w = tag_style['stroke_width']
        else:
            stroke_w = max(s.stroke_width, tag_style.get('stroke_width', 1))
        d = s.svg_path_d
        if s.tag in ('ground', 'floor', 'room') and not s.is_curve and not d.rstrip().endswith('Z'):
            d = d + ' Z'
        out.append(f'<path d="{d}" fill="{fill}" stroke="{stroke}" '
                   f'stroke-width="{stroke_w}" stroke-linejoin="round" stroke-linecap="round"/>')
    out.append('</g>')

    out.append('<g id="grid" stroke="rgba(0,0,0,0.25)" stroke-width="1.5" fill="none">')
    for col in range(wmap.tiles_wide + 1):
        x = col * tile_size
        out.append(f'<line x1="{x:.0f}" y1="0" x2="{x:.0f}" y2="{height:.0f}"/>')
    for row in range(wmap.tiles_high + 1):
        y = row * tile_size
        out.append(f'<line x1="0" y1="{y:.0f}" x2="{width:.0f}" y2="{y:.0f}"/>')
    out.append('</g>')

    out.append('<g id="features" font-size="22" font-weight="600">')
    for f in wmap.features:
        short = f.type.split('/')[-1]
        if 'Door' in short:
            color = '#a06030'
        elif 'Window' in short:
            color = '#7fb8d0'
        elif 'Stairs' in short:
            color = '#8a8478'
        elif 'Bed' in short:
            color = '#5a7a92'
        elif 'Chair' in short or 'Table' in short:
            color = '#6a4a30'
        elif 'Fireplace' in short:
            color = '#b14a3a'
        else:
            color = '#444444'
        out.append(f'<circle cx="{f.x:.0f}" cy="{f.y:.0f}" r="22" '
                   f'fill="{color}" stroke="#1a1410" stroke-width="2.5" opacity="0.85"/>')
        out.append(f'<text x="{f.x:.0f}" y="{f.y + 8:.0f}" text-anchor="middle" '
                   f'fill="white" stroke="black" stroke-width="0.5" paint-order="stroke fill" '
                   f'font-size="20">{html.escape(short[:3].upper())}</text>')
    out.append('</g>')

    out.append('</svg>')
    return '\n'.join(out)


def render(wmap, *, project_module=None, render_mode='production',
           visibility_filter='gm', annotations=None):
    if wmap.hex_orientation == 'SQUARE' or wmap.map_type == 'BATTLEMAT':
        return render_square_map(wmap, project_module=project_module)
    return render_hex_map(wmap,
                          project_module=project_module,
                          render_mode=render_mode,
                          visibility_filter=visibility_filter,
                          annotations=annotations)


# =============================================================================
# 8. EMBED v2 DESCRIPTION HEADER
# =============================================================================

def embed_claude_header(svg_text, claude_doc, source_filename=''):
    today = datetime.date.today().isoformat()

    body = svg_text
    if body.startswith('<?xml'):
        body = body.split('\n', 1)[1] if '\n' in body else body

    # Substitute -- → == in the description body to satisfy XML comment rules.
    safe_doc = claude_doc.replace('--', '==')
    desc_lines = safe_doc.splitlines()

    # Layout (1-indexed):
    #   1: <?xml ?>
    #   2: <!--
    #   3: CLAUDE_MAP_INDEX
    #   4: schema_version: 2
    #   5: source: ...
    #   6: generated: ...
    #   7: claude_section_end: N
    #   8: ==>
    #   9: <!==
    #   10: CLAUDE_MAP_DESCRIPTION
    #   11..(10+len(desc_lines)): description
    #   (11+len(desc_lines)): -->
    desc_block_end_line = 11 + len(desc_lines)
    claude_section_end = desc_block_end_line

    header_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<!--',
        'CLAUDE_MAP_INDEX',
        'schema_version: 2',
        f'source: {source_filename or "(unknown)"}',
        f'generated: {today}',
        f'claude_section_end: {claude_section_end}',
        '==>',
        '<!==',
        'CLAUDE_MAP_DESCRIPTION',
    ]
    header_lines.extend(desc_lines)
    header_lines.append('-->')

    return '\n'.join(header_lines) + '\n' + body


# =============================================================================
# 9. CLI ORCHESTRATOR — three-state generation flow
# =============================================================================

def _load_project(name):
    """Load a project module by name. Returns None on failure (renderer uses defaults)."""
    if not name or name == 'default':
        try:
            from projects import default
            return default
        except Exception:
            return None
    try:
        # Add the worldographer dir to sys.path so 'projects' is importable
        # when invoked as a script
        from projects import load
        return load(name)
    except Exception as e:
        print(f'  WARN: could not load project {name!r}: {e}. Using defaults.')
        return None


def main():
    ap = argparse.ArgumentParser(description='Render Worldographer .wxx → v2 .svg')
    ap.add_argument('input', help='Path to .wxx file')
    ap.add_argument('output', help='Path to output .svg')
    ap.add_argument('--width', type=int, default=0,
                    help='If >0, also write a PNG at this pixel width (requires cairosvg)')
    ap.add_argument('--regenerate-annotations', action='store_true',
                    help='Back up existing annotation file → .previous.md, then scaffold a fresh one')
    ap.add_argument('--player', action='store_true',
                    help='Player render: hide `hidden` POIs, unlabel `local` features')
    ap.add_argument('--gm', action='store_true',
                    help='GM render: show everything (default)')
    ap.add_argument('--no-claude-header', action='store_true',
                    help='Skip embedded v2 description header (emit plain SVG)')
    ap.add_argument('--project', default=None,
                    help='Override project name (default: read from annotation file, fallback to "default")')
    args = ap.parse_args()

    # Make sibling packages importable when running this file directly
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    # Parse map
    print(f'[parse] {args.input}')
    xml = load_wxx(args.input)
    wmap = parse_wxx(xml)
    print(f'  map_type={wmap.map_type}, hex_orientation={wmap.hex_orientation}, '
          f'size={wmap.tiles_wide}x{wmap.tiles_high}')
    print(f'  terrain ids: {len(wmap.terrain)}, '
          f'features: {len(wmap.features)}, shapes: {len(wmap.shapes)}')

    # Determine generation state
    from wxx_annotations import (
        determine_state, write_scaffold, regenerate_scaffold,
        load_annotations, check_drift, annotation_path_for,
    )
    state = determine_state(args.output, regenerate=args.regenerate_annotations)
    annot_path = annotation_path_for(args.output)
    annotations = None

    source_filename = os.path.basename(args.input)
    if state == 'regenerate':
        prev, new = regenerate_scaffold(wmap, args.output, source_filename)
        print(f'[regenerate] Backed up old → {prev}')
        print(f'[regenerate] Wrote fresh scaffold → {new}')
        print(f'  Hand-merge from .previous.md before re-rendering. '
              f'Re-running --regenerate-annotations will overwrite .previous.md.')
        annotations = load_annotations(args.output)
        render_mode = 'scaffold'
    elif state == 'scaffold':
        new_path = write_scaffold(wmap, args.output, source_filename)
        print(f'[scaffold] No existing annotations — wrote {new_path}')
        annotations = load_annotations(args.output)
        render_mode = 'scaffold'
    else:
        annotations = load_annotations(args.output)
        print(f'[merge] Loaded annotations from {annot_path}')
        render_mode = 'production'

    # Drift warnings
    if annotations and state == 'merge':
        try:
            from icons import all_types
            valid_types = set(all_types(wmap.map_type))
        except Exception:
            valid_types = set()
        warnings = check_drift(annotations, wmap, valid_types)
        for w in warnings:
            print(f'  WARN: {w}')

    # Project module — annotation overrides CLI which overrides default
    project_name = args.project
    if not project_name and annotations:
        project_name = annotations.get('project', 'default')
    if not project_name:
        project_name = 'default'
    project_module = _load_project(project_name)
    print(f'  project: {project_name}')

    # Visibility filter
    visibility_filter = 'player' if args.player else 'gm'

    # Render SVG
    print(f'[render] mode={render_mode}, visibility={visibility_filter}')
    svg = render(wmap,
                 project_module=project_module,
                 render_mode=render_mode,
                 visibility_filter=visibility_filter,
                 annotations=annotations)

    # Embed Claude header
    if not args.no_claude_header:
        try:
            from wxx_to_claude import build_description
            try:
                from terrain.world import glyph_for as world_glyph
            except Exception:
                world_glyph = None
            terrain_reskins = _project_terrain_reskins(project_module)
            palette_overrides = (getattr(project_module, 'PALETTE_OVERRIDES', {})
                                  if project_module else {})
            desc = build_description(
                wmap, annotations,
                source_filename=source_filename,
                project_palette_overrides=palette_overrides,
                project_terrain_reskins=terrain_reskins,
                terrain_glyph_fn=world_glyph,
            )
            svg = embed_claude_header(svg, desc, source_filename=source_filename)
            line_count = len(desc.splitlines())
            print(f'  embedded header: {line_count} description lines')
        except Exception as e:
            print(f'  WARN: could not embed Claude header: {e}')

    # Write output
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(svg)
    print(f'[write] {args.output}: {len(svg):,} bytes')

    # Optional PNG
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
