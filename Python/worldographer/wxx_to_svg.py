"""
wxx_to_svg.py — Render Worldographer .wxx files to SVG.

Supports both hex (kingdom-scale) and square (battlemap) maps, auto-detected
from the <map hexOrientation="..."> attribute.

Usage:
    python wxx_to_svg.py input.wxx output.svg
    python wxx_to_svg.py input.wxx output.svg --width 2400      # rasterize PNG too

Reference: see Wxx_Parsing_Reference.md for format details and known gotchas.
"""
from __future__ import annotations
import gzip, re, math, html, sys, os, argparse
from dataclasses import dataclass, field
from typing import Optional


# =============================================================================
# 1. STYLING CONFIGURATION
# =============================================================================
# Edit these to customise output. Project-specific palettes live here.
#
# The base palette comes from the authoritative `worldographer_palette.py` —
# generated from Worldographer's own terrain.properties (480 terrains across
# Classic, Cosmic, ISO, Floor, Full Classic). It's loaded if present.
# Project-specific overrides take precedence.

try:
    from worldographer_palette import TERRAIN_COLORS as _AUTHORITATIVE_PALETTE
except ImportError:
    _AUTHORITATIVE_PALETTE = {}

# Project-specific overrides — these win over the authoritative palette where
# both are present. Use this to retint terrains for a particular map style or
# repurpose terrain IDs (e.g. Aethelmark uses "Underdark Open" as rural).
_PROJECT_OVERRIDES = {
    'Classic/Underdark Open':               '#ead9bc',  # repurposed: rural neighbourhood
    # Aethelmark/Silberbach Valley styling — autumn mountains, bright valley
    'Classic/Mountains Forest Evergreen':   '#8a6a3a',
    'Classic/Hills Forest Evergreen':       '#6a8a4a',
    'Classic/Flat Forest Evergreen':        '#5e8542',
    'Classic/Flat Farmland':                '#a8c878',
    'Classic/Hills Grassland':              '#d4d896',
    'Classic/Mountain Forest Evergreen':    '#7a6a3a',
    'Classic/Flat Farmland Cultivated':     '#e8d870',
    'Classic/Mountains':                    '#b08a55',
    'Classic/Flat Forest Evergreen Heavy':  '#3a5a30',
    'Classic/Water Sea':                    '#7fa9c4',
}

# Final palette: authoritative base, then project overrides on top
HEX_TERRAIN_COLORS = {**_AUTHORITATIVE_PALETTE, **_PROJECT_OVERRIDES}
HEX_DEFAULT_COLOR = '#cccccc'
HEX_DEFAULT_COLOR = '#cccccc'

# Square-map shape rendering: how to colour shapes by their `tags` attribute.
SQUARE_SHAPE_STYLES = {
    'ground':  {'fill': '#7a9a52', 'stroke': '#3a4a2a', 'stroke_width': 1.5},
    'floor':   {'fill': '#c4a878', 'stroke': '#3a2410', 'stroke_width': 1.5},
    'room':    {'fill': '#c4a878', 'stroke': '#3a2410', 'stroke_width': 1.5},
    'wall':    {'fill': 'none',    'stroke': '#1a1410', 'stroke_width': 12.0},
    'road':    {'fill': 'none',    'stroke': '#5a3d1d', 'stroke_width': 8.0},
    'river':   {'fill': 'none',    'stroke': '#6fa9d3', 'stroke_width': 12.0},
    # Fallback for unrecognized tags
    None:      {'fill': 'none',    'stroke': '#444444', 'stroke_width': 4.0},
}

SQUARE_BACKGROUND_COLOR = '#ADD8E6'  # default battlemat backdrop (light blue)


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
    creation_type: str       # 'BASIC' | 'CURVE' | etc.
    is_curve: bool
    fill_color: Optional[str]      # 'r,g,b,a' as floats, or None
    fill_texture: Optional[str]    # texture name or None
    stroke_color: Optional[str]
    stroke_width: float
    map_layer: str
    svg_path_d: str
    points: list = field(default_factory=list)

@dataclass
class WxxMap:
    map_type: str                  # 'WORLD' | 'BATTLEMAT' | etc.
    hex_orientation: str           # 'COLUMNS' | 'ROWS' | 'SQUARE'
    tiles_wide: int
    tiles_high: int
    terrain: dict                  # id -> name
    grid: list                     # grid[col][row] = terrain id (column-major)
    polar: list                    # parallel: polar[col][row] = True if arctic/snow overlay
    features: list
    shapes: list
    layers: list                   # render order (bottom to top)


# =============================================================================
# 3. PARSER
# =============================================================================

def load_wxx(path: str) -> str:
    """Decompress + decode a .wxx file to UTF-8 XML text."""
    with gzip.open(path, 'rb') as f:
        raw = f.read()
    # Worldographer writes UTF-16 BE
    return raw.decode('utf-16-be')


def _attr(s: str, name: str, default=None):
    m = re.search(rf'\s{name}="([^"]*)"', s)
    return m.group(1) if m else default


def _parse_rgba_to_hex(rgba_str: str) -> Optional[str]:
    """Worldographer writes colours as 'r,g,b,a' floats 0-1. Convert to '#RRGGBB'."""
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


def parse_shape_path(shape_xml: str) -> tuple[str, list]:
    """Parse a <shape>'s <p> elements into (svg_path_d, [(x, y), ...]).

    Handles the three Worldographer point forms:
      - <p type="m" x y/>           — move-to
      - <p type="c" x y cx1 cy1 cx2 cy2/>  — cubic Bezier
      - <p x y/>                     — typeless: implicit line-to
                                       (BUT first point is always move-to)
    """
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
            # First point is always implicit move-to, regardless of declared type.
            d_parts.append(f'M {x:.2f},{y:.2f}')
        elif ptype == 'c' and cx1 is not None:
            d_parts.append(f'C {cx1:.2f},{cy1:.2f} {cx2:.2f},{cy2:.2f} {x:.2f},{y:.2f}')
        elif ptype == 'm':
            d_parts.append(f'M {x:.2f},{y:.2f}')
        else:
            d_parts.append(f'L {x:.2f},{y:.2f}')
    return ' '.join(d_parts), pts


def parse_wxx(xml: str) -> WxxMap:
    """Parse a Worldographer XML document into a normalised WxxMap."""
    # ------ Map metadata
    map_m = re.search(r'<map\s[^>]*>', xml).group()
    map_type = _attr(map_m, 'type', 'WORLD')
    hex_orient = _attr(map_m, 'hexOrientation', 'COLUMNS')

    # ------ Tile grid metadata
    tiles_m = re.search(r'<tiles\s[^>]*>', xml).group()
    tiles_wide = int(_attr(tiles_m, 'tilesWide', '0'))
    tiles_high = int(_attr(tiles_m, 'tilesHigh', '0'))

    # ------ Layers (render order, bottom-up)
    layers = re.findall(r'<maplayer\s+name="([^"]+)"', xml)
    # Worldographer lists them in the file in DRAW ORDER (top of file = drawn last,
    # which is on top). For SVG we want bottom-up, so reverse.
    layers = list(reversed(layers))

    # ------ Terrain map
    terrain = {}
    tm_m = re.search(r'<terrainmap>([^<]*)</terrainmap>', xml)
    if tm_m:
        parts = tm_m.group(1).split('\t')
        for i in range(0, len(parts) - 1, 2):
            name, tid = parts[i].strip(), parts[i + 1].strip()
            if tid.isdigit():
                terrain[int(tid)] = name

    # ------ Tile grid (column-major: tilerow[i] is column i)
    # Each tile line is tab-separated. Field 0 = terrain id; field 2 = polar/arctic flag.
    # Short tiles end with 'Z' and have 6 fields; full tiles have 11 fields with blend data.
    tilerows = re.findall(r'<tilerow[^>]*>([^<]*)</tilerow>', xml)
    grid = []
    polar = []   # parallel grid: True if this tile has the polar/arctic overlay
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

    # ------ Features
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
        f = WxxFeature(
            type=typ,
            x=float(x), y=float(y),
            label=html.unescape(lbl).strip() if lbl else '',
            rotate=float(_attr(attrs, 'rotate', '0') or 0),
            scale=float(_attr(attrs, 'scale', '1') or 1),
            flip_h=(_attr(attrs, 'isFlipHorizontal', 'false') == 'true'),
            flip_v=(_attr(attrs, 'isFlipVertical', 'false') == 'true'),
        )
        features.append(f)

    # ------ Shapes
    shapes = []
    for s_xml in re.findall(r'<shape\s.*?</shape>', xml, re.DOTALL):
        d, pts = parse_shape_path(s_xml)
        if not d or len(pts) < 2:
            continue
        shape = WxxShape(
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
        )
        shapes.append(shape)

    return WxxMap(
        map_type=map_type,
        hex_orientation=hex_orient,
        tiles_wide=tiles_wide,
        tiles_high=tiles_high,
        terrain=terrain,
        grid=grid,
        polar=polar,
        features=features,
        shapes=shapes,
        layers=layers,
    )


# =============================================================================
# 4. HEX GEOMETRY
# =============================================================================
# Worldographer's hex world coords are stretched: each hex spans 300×300 world
# units, regardless of the visual aspect ratio of the rendered hex shape.
#
# Two hex orientations:
#   COLUMNS — flat-top hex; columns line up vertically; ODD COLUMNS offset DOWN
#   ROWS    — pointy-top hex; rows line up horizontally; ODD ROWS offset RIGHT
#
# Both use the same 300×300 world stretching, just with axes swapped.

HEX_W = 300.0
HEX_H = 300.0
HEX_HALF_W = 150.0
HEX_HALF_H = 150.0
HEX_QUARTER = 75.0   # 0.25 × 300; the "shoulder" offset on stretched hexes


# --- COLUMNS orientation (flat-top hex, odd columns shift down) ---
HEX_COL_STRIDE_COLS = 0.75 * HEX_W   # 225
HEX_ROW_STRIDE_COLS = HEX_H          # 300

def hex_center_columns(col: int, row: int) -> tuple[float, float]:
    cx = col * HEX_COL_STRIDE_COLS + HEX_HALF_W
    cy = row * HEX_ROW_STRIDE_COLS + HEX_HALF_H
    if col % 2 == 1:
        cy += HEX_HALF_H        # odd columns shift down
    return cx, cy

def hex_polygon_columns(col: int, row: int) -> list[tuple[float, float]]:
    """Flat-top hex stretched to 300×300 world units."""
    cx, cy = hex_center_columns(col, row)
    return [
        (cx - HEX_HALF_W, cy),                  # left point
        (cx - HEX_QUARTER, cy - HEX_HALF_H),    # upper-left
        (cx + HEX_QUARTER, cy - HEX_HALF_H),    # upper-right
        (cx + HEX_HALF_W, cy),                  # right point
        (cx + HEX_QUARTER, cy + HEX_HALF_H),    # lower-right
        (cx - HEX_QUARTER, cy + HEX_HALF_H),    # lower-left
    ]


# --- ROWS orientation (pointy-top hex, odd rows shift right) ---
HEX_COL_STRIDE_ROWS = HEX_W            # 300
HEX_ROW_STRIDE_ROWS = 0.75 * HEX_H     # 225

def hex_center_rows(col: int, row: int) -> tuple[float, float]:
    cx = col * HEX_COL_STRIDE_ROWS + HEX_HALF_W
    cy = row * HEX_ROW_STRIDE_ROWS + HEX_HALF_H
    if row % 2 == 1:
        cx += HEX_HALF_W        # odd rows shift right
    return cx, cy

def hex_polygon_rows(col: int, row: int) -> list[tuple[float, float]]:
    """Pointy-top hex stretched to 300×300 world units."""
    cx, cy = hex_center_rows(col, row)
    return [
        (cx, cy - HEX_HALF_H),                  # top point
        (cx + HEX_HALF_W, cy - HEX_QUARTER),    # upper-right
        (cx + HEX_HALF_W, cy + HEX_QUARTER),    # lower-right
        (cx, cy + HEX_HALF_H),                  # bottom point
        (cx - HEX_HALF_W, cy + HEX_QUARTER),    # lower-left
        (cx - HEX_HALF_W, cy - HEX_QUARTER),    # upper-left
    ]


# --- Dispatcher: pick the right geometry for a parsed map ---
def hex_geometry_for(orientation: str):
    """Return (center_fn, polygon_fn) for the given hex orientation."""
    if orientation == 'ROWS':
        return hex_center_rows, hex_polygon_rows
    return hex_center_columns, hex_polygon_columns   # default = COLUMNS


def square_center(col: int, row: int, tile_size: float = 300.0) -> tuple[float, float]:
    return col * tile_size + tile_size / 2, row * tile_size + tile_size / 2


# =============================================================================
# 5. RENDERERS
# =============================================================================

def render_hex_map(wmap: WxxMap, terrain_colors: dict = None) -> str:
    """Render a hex/kingdom-scale map with full styling. Returns complete SVG.

    Auto-handles both COLUMNS (flat-top) and ROWS (pointy-top) orientation.
    """
    palette = terrain_colors or HEX_TERRAIN_COLORS
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

    # Parchment background
    out.append(f'<rect x="{min_x:.0f}" y="{min_y:.0f}" width="{max_x-min_x:.0f}" '
               f'height="{max_y-min_y:.0f}" fill="#f0e3c2"/>')

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

    # Polar / arctic overlay — translucent white wash on flagged hexes (field 2 = 1).
    # Worldographer uses this to mark snow/ice over any base terrain (ocean → ice, farmland → frozen tundra, etc.)
    out.append('<g id="polar-overlay">')
    for col in range(cols):
        if col >= len(wmap.polar):
            continue
        for row in range(min(rows, len(wmap.polar[col]))):
            if not wmap.polar[col][row]:
                continue
            pts = hex_polygon(col, row)
            pts_str = ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts)
            # Heavy white overlay — Worldographer's ice rendering is nearly opaque
            out.append(f'<polygon points="{pts_str}" fill="#f4faff" opacity="0.85"/>')
    out.append('</g>')

    # Hex grid lines
    out.append('<g id="hex-grid" stroke="rgba(0,0,0,0.1)" stroke-width="2" fill="none">')
    for col in range(cols):
        for row in range(min(rows, len(wmap.grid[col]) if col < len(wmap.grid) else 0)):
            pts = hex_polygon(col, row)
            pts_str = ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts)
            out.append(f'<polygon points="{pts_str}"/>')
    out.append('</g>')

    # Shapes (rivers, roads, etc.) — coloured by tag
    out.append('<g id="shapes">')
    for s in wmap.shapes:
        if s.tag == 'river':
            out.append(f'<path d="{s.svg_path_d}" fill="none" stroke="#3a6a8a" stroke-width="42" '
                       f'stroke-linecap="round" opacity="0.55"/>')
            out.append(f'<path d="{s.svg_path_d}" fill="none" stroke="#6fa9d3" stroke-width="26" '
                       f'stroke-linecap="round"/>')
        elif s.tag == 'road':
            out.append(f'<path d="{s.svg_path_d}" fill="none" stroke="#5a3d1d" stroke-width="22" '
                       f'stroke-linecap="round" opacity="0.8"/>')
            out.append(f'<path d="{s.svg_path_d}" fill="none" stroke="#c9a766" stroke-width="12" '
                       f'stroke-linecap="round" stroke-dasharray="20 14"/>')
        else:
            stroke = s.stroke_color or '#444444'
            fill = s.fill_color or 'none'
            out.append(f'<path d="{s.svg_path_d}" fill="{fill}" stroke="{stroke}" stroke-width="6"/>')
    out.append('</g>')

    # Features: simple markers
    out.append('<g id="features">')
    for f in wmap.features:
        if 'Coast' in f.type:
            continue   # decorative water-edge tiles, ignore
        out.append(f'<circle cx="{f.x:.0f}" cy="{f.y:.0f}" r="20" fill="#b14a3a" '
                   f'stroke="#3a1410" stroke-width="3"/>')
        if f.label:
            out.append(f'<text x="{f.x:.0f}" y="{f.y + 60:.0f}" font-size="60" '
                       f'fill="#1a0e05" stroke="#f5ecd2" stroke-width="6" paint-order="stroke fill" '
                       f'text-anchor="middle" font-weight="bold">{html.escape(f.label)}</text>')
    out.append('</g>')

    out.append('</svg>')
    return '\n'.join(out)


def render_square_map(wmap: WxxMap) -> str:
    """Render a square/battlemap. Returns complete SVG.

    Strategy:
      - Background: SQUARE_BACKGROUND_COLOR
      - Render shapes in layer order (bottom to top), respecting fill/stroke
      - Render features as small markers at their world coords
      - Add a thin grid overlay
    """
    tile_size = 300.0   # world units per tile (Worldographer convention)
    pad = tile_size * 0.5
    width = wmap.tiles_wide * tile_size
    height = wmap.tiles_high * tile_size
    vb_x, vb_y = -pad, -pad
    vb_w, vb_h = width + 2 * pad, height + 2 * pad

    out = []
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" '
               f'viewBox="{vb_x:.0f} {vb_y:.0f} {vb_w:.0f} {vb_h:.0f}" '
               f'font-family="Arial, sans-serif">')

    # Map background (the BATTLEMAT default)
    out.append(f'<rect x="0" y="0" width="{width:.0f}" height="{height:.0f}" '
               f'fill="{SQUARE_BACKGROUND_COLOR}"/>')

    # Sort shapes by layer order. Shapes without a recognised layer go last
    # (rendered on top), since they tend to be ad-hoc walls/features.
    layer_index = {name: i for i, name in enumerate(wmap.layers)}
    sorted_shapes = sorted(
        wmap.shapes,
        key=lambda s: layer_index.get(s.map_layer, len(wmap.layers))
    )

    out.append('<g id="shapes">')
    for s in sorted_shapes:
        # Decide style: prefer the shape's own fill, else fall back to tag style.
        tag_style = SQUARE_SHAPE_STYLES.get(s.tag, SQUARE_SHAPE_STYLES[None])
        fill = s.fill_color or tag_style.get('fill', 'none')
        stroke = s.stroke_color or tag_style.get('stroke', '#444')
        # Wall shapes always get the wall stroke even if they have a stroke colour
        # (their declared strokeWidth in the source is in inches/units, not pixels).
        if s.tag == 'wall':
            stroke_w = tag_style['stroke_width']
        else:
            stroke_w = max(s.stroke_width, tag_style.get('stroke_width', 1))
        # Close the path if it's a polygon-like shape (ground/floor/room) and not curve.
        d = s.svg_path_d
        if s.tag in ('ground', 'floor', 'room') and not s.is_curve and not d.rstrip().endswith('Z'):
            d = d + ' Z'
        out.append(f'<path d="{d}" fill="{fill}" stroke="{stroke}" '
                   f'stroke-width="{stroke_w}" stroke-linejoin="round" stroke-linecap="round"/>')
    out.append('</g>')

    # Grid overlay
    out.append('<g id="grid" stroke="rgba(0,0,0,0.25)" stroke-width="1.5" fill="none">')
    for col in range(wmap.tiles_wide + 1):
        x = col * tile_size
        out.append(f'<line x1="{x:.0f}" y1="0" x2="{x:.0f}" y2="{height:.0f}"/>')
    for row in range(wmap.tiles_high + 1):
        y = row * tile_size
        out.append(f'<line x1="0" y1="{y:.0f}" x2="{width:.0f}" y2="{y:.0f}"/>')
    out.append('</g>')

    # Features as labelled markers (we can't render Worldographer's furniture art,
    # so use small icons + type names)
    out.append('<g id="features" font-size="22" font-weight="600">')
    for f in wmap.features:
        # Strip the "Battlemat/" or "Classic/" prefix for display
        short = f.type.split('/')[-1]
        # Use a colour family per item kind
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


def render(wmap: WxxMap) -> str:
    """Auto-dispatch to the right renderer based on map type."""
    if wmap.hex_orientation == 'SQUARE' or wmap.map_type == 'BATTLEMAT':
        return render_square_map(wmap)
    return render_hex_map(wmap)


# =============================================================================
# 6. CLI
# =============================================================================

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('input', help='Path to .wxx file')
    ap.add_argument('output', help='Path to output .svg')
    ap.add_argument('--width', type=int, default=0,
                    help='If >0, also write a PNG of this pixel width (requires cairosvg)')
    args = ap.parse_args()

    print(f'[parse] {args.input}')
    xml = load_wxx(args.input)
    wmap = parse_wxx(xml)
    print(f'  map_type={wmap.map_type}, hex_orientation={wmap.hex_orientation}, '
          f'size={wmap.tiles_wide}x{wmap.tiles_high}')
    print(f'  terrain ids: {len(wmap.terrain)}')
    print(f'  features: {len(wmap.features)}, shapes: {len(wmap.shapes)}')

    print(f'[render] → {args.output}')
    svg = render(wmap)
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(svg)
    print(f'  {len(svg):,} bytes')

    if args.width > 0:
        png_path = os.path.splitext(args.output)[0] + '.png'
        try:
            import cairosvg
            cairosvg.svg2png(url=args.output, write_to=png_path, output_width=args.width)
            print(f'[png] → {png_path} (width={args.width})')
        except ImportError:
            print('  (cairosvg not installed; skipping PNG output)')


if __name__ == '__main__':
    main()
