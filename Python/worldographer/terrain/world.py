"""
World-scale terrain library — glyph mapping and per-hex decorations.

Glyph assignment is deliberately compact — single ASCII char so the grid
section in the description block can pack 50+ columns into a readable line.

Decorations are the visible-map adornments (tree triangles, mountain peaks,
hatching) that go on top of the base terrain colour. They use deterministic
RNG seeded by (col, row) so the same hex always produces the same decoration
across renders.
"""
import math


# =============================================================================
# Glyph map — terrain name → single ASCII character for the description grid
# =============================================================================
# Strip "Classic/" prefix when looking up. Mountains uppercase, hills lowercase
# of same letter where it makes sense; water is ~; forests f/F; farmland .;
# grassland ,; desert d; underdark/cave reused for project reskins (r in
# Aethelmark via project override).

GLYPHS = {
    # Water
    'Water Ocean': '~', 'Water Sea': '~', 'Water Shallow': '~',
    'Water River': '~', 'Water Lake': '~',
    'Water Wetlands': '%',
    # Mountains
    'Mountains': '^',
    'Mountains Forest Evergreen': 'M', 'Mountain Forest Evergreen': 'M',
    'Mountains Forest Deciduous': 'M', 'Mountains Forest Mixed': 'M',
    'Mountains Forest Jungle': 'J',
    # Hills
    'Hills': 'h', 'Hills Grassland': 'h', 'Hills Shrubland': 'h',
    'Hills Forest Evergreen': 'H', 'Hills Forest Deciduous': 'H',
    'Hills Forest Mixed': 'H', 'Hills Forest Jungle': 'j',
    # Forests (flat)
    'Flat Forest Evergreen': 'f', 'Flat Forest Evergreen Heavy': 'F',
    'Flat Forest Deciduous': 'f', 'Flat Forest Mixed': 'f',
    'Flat Forest Jungle': 'g',
    'Flat Forest Wetlands': '%',
    # Open / farmland / grassland
    'Flat Farmland': '.', 'Flat Farmland Cultivated': '.',
    'Flat Farmland Varied': '.',
    'Flat Grassland': ',', 'Flat Shrubland': ',', 'Flat Plain': ',',
    # Desert
    'Flat Desert Rocky': 'd', 'Flat Desert Dunes': 'd',
    # Special / repurposed (project files may override)
    'Underdark Open': '?',  # default; Aethelmark project reskin sets this to 'r'
    'Blank': ' ',
}

UNKNOWN_GLYPH = '?'


def glyph_for(terrain_name: str) -> str:
    """Look up the glyph for a terrain. Strips namespace prefix."""
    if not terrain_name:
        return UNKNOWN_GLYPH
    bare = terrain_name.split('/', 1)[-1]
    return GLYPHS.get(bare, UNKNOWN_GLYPH)


# =============================================================================
# Per-hex decorations
# =============================================================================

def _seed_rand(col: int, row: int) -> float:
    """Deterministic pseudo-random in [0, 1) seeded by cell coordinates."""
    h = (col * 73856093) ^ (row * 19349663)
    return (h & 0xFFFF) / 65536.0


def _evergreen_dense(cx, cy, col, row):
    """Heavy evergreen forest — multiple dark fir triangles."""
    out = []
    for i in range(7):
        dx = (_seed_rand(col + i * 17, row) - 0.5) * 200
        dy = (_seed_rand(col, row + i * 17) - 0.5) * 200
        size = 18 + _seed_rand(col + i, row + i) * 8
        x, y = cx + dx, cy + dy
        out.append(f'<polygon points="{x - size:.1f},{y + size * 0.6:.1f} '
                   f'{x:.1f},{y - size:.1f} {x + size:.1f},{y + size * 0.6:.1f}" '
                   f'fill="#2a4520" stroke="#1a2e15" stroke-width="1"/>')
    return ''.join(out)


def _evergreen_light(cx, cy, col, row):
    """Light evergreen forest — fewer, smaller fir triangles."""
    out = []
    for i in range(4):
        dx = (_seed_rand(col + i * 17, row) - 0.5) * 200
        dy = (_seed_rand(col, row + i * 17) - 0.5) * 200
        size = 14 + _seed_rand(col + i, row + i) * 6
        x, y = cx + dx, cy + dy
        out.append(f'<polygon points="{x - size:.1f},{y + size * 0.6:.1f} '
                   f'{x:.1f},{y - size:.1f} {x + size:.1f},{y + size * 0.6:.1f}" '
                   f'fill="#3a6a2a" stroke="#1a3015" stroke-width="0.8"/>')
    return ''.join(out)


def _deciduous(cx, cy, col, row):
    """Deciduous forest — round leafy circles."""
    out = []
    for i in range(5):
        dx = (_seed_rand(col + i * 11, row) - 0.5) * 200
        dy = (_seed_rand(col, row + i * 11) - 0.5) * 200
        r = 12 + _seed_rand(col + i, row + i) * 6
        out.append(f'<circle cx="{cx + dx:.1f}" cy="{cy + dy:.1f}" r="{r:.1f}" '
                   f'fill="#5a8a3a" stroke="#1a3a0e" stroke-width="0.8"/>')
    return ''.join(out)


def _mixed_forest(cx, cy, col, row):
    """Mixed forest — alternating triangles and circles."""
    out = []
    for i in range(5):
        dx = (_seed_rand(col + i * 13, row) - 0.5) * 200
        dy = (_seed_rand(col, row + i * 13) - 0.5) * 200
        x, y = cx + dx, cy + dy
        if i % 2 == 0:
            size = 14
            out.append(f'<polygon points="{x - size:.1f},{y + size * 0.6:.1f} '
                       f'{x:.1f},{y - size:.1f} {x + size:.1f},{y + size * 0.6:.1f}" '
                       f'fill="#3a6a2a" stroke="#1a3015" stroke-width="0.8"/>')
        else:
            r = 12
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" '
                       f'fill="#5a8a3a" stroke="#1a3a0e" stroke-width="0.8"/>')
    return ''.join(out)


def _jungle(cx, cy, col, row):
    """Jungle — palm-tree silhouettes."""
    out = []
    for i in range(3):
        dx = (_seed_rand(col + i * 7, row) - 0.5) * 200
        dy = (_seed_rand(col, row + i * 7) - 0.5) * 200
        x, y = cx + dx, cy + dy
        # Trunk
        out.append(f'<line x1="{x:.1f}" y1="{y + 12:.1f}" x2="{x:.1f}" y2="{y - 16:.1f}" '
                   f'stroke="#3a2410" stroke-width="2"/>')
        # Fronds
        for fa in (-2.4, -1.8, -1.2, -0.6, 0.6, 1.2, 1.8, 2.4):
            fx = x + math.cos(fa - math.pi / 2) * 14
            fy = y - 16 + math.sin(fa - math.pi / 2) * 8
            out.append(f'<line x1="{x:.1f}" y1="{y - 16:.1f}" x2="{fx:.1f}" y2="{fy:.1f}" '
                       f'stroke="#2a6a30" stroke-width="2"/>')
    return ''.join(out)


def _mountain_peak(cx, cy, col, row):
    """Mountain peak — single triangle with snow cap."""
    dx = (_seed_rand(col, row) - 0.5) * 60
    dy = (_seed_rand(col + 1, row + 1) - 0.5) * 40
    x, y = cx + dx, cy + dy + 20
    return (f'<polygon points="{x - 80:.1f},{y + 30:.1f} {x:.1f},{y - 90:.1f} '
            f'{x + 80:.1f},{y + 30:.1f}" fill="#5a4a3a" stroke="#2a1a10" stroke-width="2"/>'
            # Snow cap
            f'<polygon points="{x - 30:.1f},{y - 30:.1f} {x:.1f},{y - 90:.1f} '
            f'{x + 30:.1f},{y - 30:.1f} {x + 16:.1f},{y - 22:.1f} {x:.1f},{y - 30:.1f} '
            f'{x - 16:.1f},{y - 22:.1f}" fill="#f4faff" stroke="#2a1a10" stroke-width="1"/>')


def _mountain_forested(cx, cy, col, row):
    """Forested mountain — peak with a few firs at base."""
    out = [_mountain_peak(cx, cy, col, row)]
    # Add trees on the slopes
    for i in range(3):
        dx = (_seed_rand(col + i * 23, row) - 0.5) * 180
        dy = 50 + _seed_rand(col, row + i) * 40
        x, y = cx + dx, cy + dy
        out.append(f'<polygon points="{x - 14:.1f},{y + 8:.1f} '
                   f'{x:.1f},{y - 14:.1f} {x + 14:.1f},{y + 8:.1f}" '
                   f'fill="#2a4520" stroke="#1a2e15" stroke-width="1"/>')
    return ''.join(out)


def _hills(cx, cy, col, row):
    """Hills — small rounded humps."""
    out = []
    for i in range(2):
        dx = (_seed_rand(col + i * 13, row) - 0.5) * 180
        dy = (_seed_rand(col, row + i * 13) - 0.5) * 100
        x, y = cx + dx, cy + dy
        out.append(f'<path d="M {x - 30:.1f},{y + 10:.1f} '
                   f'q 30,-30 60,0" fill="none" '
                   f'stroke="#7a6a4a" stroke-width="3"/>')
    return ''.join(out)


def _hills_forested(cx, cy, col, row):
    """Forested hills — humps with small trees."""
    out = [_hills(cx, cy, col, row)]
    for i in range(3):
        dx = (_seed_rand(col + i * 17, row) - 0.5) * 180
        dy = (_seed_rand(col, row + i * 17) - 0.5) * 120
        x, y = cx + dx, cy + dy
        out.append(f'<polygon points="{x - 10:.1f},{y + 6:.1f} '
                   f'{x:.1f},{y - 10:.1f} {x + 10:.1f},{y + 6:.1f}" '
                   f'fill="#3a5a2a" stroke="#1a3015" stroke-width="0.8"/>')
    return ''.join(out)


def _farmland_hatch(cx, cy, col, row):
    """Farmland — fine cross-hatching for tilled ground."""
    out = []
    spacing = 22
    for i in range(-3, 4):
        x1 = cx + i * spacing - 60
        y1 = cy - 60
        x2 = x1 + 120
        y2 = y1 + 120
        out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                   f'stroke="#7a8a3a" stroke-width="1" opacity="0.5"/>')
    return ''.join(out)


def _wetlands(cx, cy, col, row):
    """Wetlands — wavy reed lines."""
    out = []
    for i in range(4):
        dx = (_seed_rand(col + i * 11, row) - 0.5) * 180
        dy = (_seed_rand(col, row + i * 11) - 0.5) * 140
        x, y = cx + dx, cy + dy
        out.append(f'<path d="M {x:.1f},{y + 14:.1f} q -3,-7 0,-14 q 3,-7 0,-14" '
                   f'fill="none" stroke="#5a8a5a" stroke-width="1.5"/>')
    return ''.join(out)


def _desert_dunes(cx, cy, col, row):
    """Desert — sweeping dune curves."""
    out = []
    for i in range(2):
        dx = (_seed_rand(col + i * 13, row) - 0.5) * 100
        dy = (_seed_rand(col, row + i * 13) - 0.5) * 80
        x, y = cx + dx, cy + dy
        out.append(f'<path d="M {x - 60:.1f},{y:.1f} q 60,-30 120,0" '
                   f'fill="none" stroke="#c8a050" stroke-width="2" opacity="0.6"/>')
    return ''.join(out)


def _rural_neighbourhood(cx, cy, col, row):
    """Aethelmark project reskin — small cottages on cream-pink hex."""
    out = []
    for i in range(2):
        dx = (_seed_rand(col + i * 19, row) - 0.5) * 100
        dy = (_seed_rand(col, row + i * 19) - 0.5) * 80
        x, y = cx + dx, cy + dy
        out.append(
            f'<rect x="{x - 14:.1f}" y="{y - 4:.1f}" width="28" height="18" '
            f'fill="#cba47a" stroke="#3a1410" stroke-width="1.5"/>'
            f'<polygon points="{x - 16:.1f},{y - 4:.1f} {x:.1f},{y - 16:.1f} '
            f'{x + 16:.1f},{y - 4:.1f}" fill="#7a3a1f" stroke="#3a1410" stroke-width="1.5"/>'
        )
    return ''.join(out)


# Decoration dispatch — match by terrain name (suffix match)
_DECORATION_RULES = [
    ('Mountains Forest', _mountain_forested),
    ('Mountain Forest', _mountain_forested),
    ('Mountains', _mountain_peak),
    ('Hills Forest', _hills_forested),
    ('Hills', _hills),
    ('Flat Forest Evergreen Heavy', _evergreen_dense),
    ('Flat Forest Evergreen', _evergreen_light),
    ('Flat Forest Deciduous', _deciduous),
    ('Flat Forest Mixed', _mixed_forest),
    ('Flat Forest Jungle', _jungle),
    ('Flat Forest Wetlands', _wetlands),
    ('Flat Farmland', _farmland_hatch),
    ('Flat Desert', _desert_dunes),
    ('Underdark Open', _rural_neighbourhood),  # Aethelmark project reskin
    ('Wetlands', _wetlands),
]


def decorations_for(terrain_name: str, cx: float, cy: float,
                    col: int, row: int) -> str:
    """Return SVG snippet for decorations on this hex (or empty string)."""
    if not terrain_name:
        return ''
    bare = terrain_name.split('/', 1)[-1]
    for pattern, fn in _DECORATION_RULES:
        if pattern in bare:
            return fn(cx, cy, col, row)
    return ''
