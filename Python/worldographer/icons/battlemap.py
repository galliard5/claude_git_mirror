"""
Battlemap-scale icon library — STUB.

To be filled in when battlemap art is decided. The Battlemat namespace in
worldographer_palette.py carries 324 native types; this stub covers the most
common categories with placeholder drawings.

Anticipated categories per spec Appendix C:
  - Architectural (door, window, stairs, ladder, archway, arrow_slit)
  - Furniture (bed, chair, table, bench, throne, desk)
  - Containers (chest, barrel, crate, bookcase, wardrobe, cabinet)
  - Light / Heat (fireplace, brazier, torch_sconce, candle, lantern)
  - Utility (anvil, forge, loom, well, fountain, altar)
  - Hazards (trap, pit, spike_trap, alchemical_hazard)
  - Natural / Outdoor (tree, rock, water_tile, log, stump, bush)
"""


def _placeholder(x, y, scale=1.0, visibility='known', **kw):
    """Lettered marker — placeholder until battlemap icons exist."""
    label = (kw.get('label') or '?')[:3].upper()
    op = ' opacity="0.35"' if visibility == 'hidden' else ''
    r = 22 * scale
    return (
        f'<g{op}>'
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" '
        f'fill="#888080" stroke="#1a1410" stroke-width="2"/>'
        f'<text x="{x:.1f}" y="{y + 6:.1f}" text-anchor="middle" '
        f'font-family="Arial, sans-serif" font-size="{16 * scale:.0f}" font-weight="600" '
        f'fill="#fff">{label}</text>'
        f'</g>'
    )


_STUB_TYPES = [
    # Architectural
    'door', 'window', 'stairs', 'ladder', 'archway', 'arrow_slit',
    # Furniture
    'bed', 'chair', 'table', 'bench', 'throne', 'desk',
    # Containers
    'chest', 'barrel', 'crate', 'bookcase', 'wardrobe', 'cabinet',
    # Light / Heat
    'fireplace', 'brazier', 'torch_sconce', 'candle', 'lantern',
    # Utility
    'anvil', 'forge', 'loom', 'well', 'fountain', 'altar',
    # Hazards
    'trap', 'pit', 'spike_trap', 'alchemical_hazard',
    # Natural / Outdoor
    'tree', 'rock', 'water_tile', 'log', 'stump', 'bush',
    # Generic
    'landmark',
]

ICONS = {name: _placeholder for name in _STUB_TYPES}


def list_types() -> dict:
    return {
        'Architectural': ['door', 'window', 'stairs', 'ladder', 'archway', 'arrow_slit'],
        'Furniture': ['bed', 'chair', 'table', 'bench', 'throne', 'desk'],
        'Containers': ['chest', 'barrel', 'crate', 'bookcase', 'wardrobe', 'cabinet'],
        'Light / Heat': ['fireplace', 'brazier', 'torch_sconce', 'candle', 'lantern'],
        'Utility': ['anvil', 'forge', 'loom', 'well', 'fountain', 'altar'],
        'Hazards': ['trap', 'pit', 'spike_trap', 'alchemical_hazard'],
        'Natural / Outdoor': ['tree', 'rock', 'water_tile', 'log', 'stump', 'bush'],
        'Generic': ['landmark'],
    }
