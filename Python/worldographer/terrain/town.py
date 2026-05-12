"""
Town-scale terrain library — STUB.

Town maps don't have meaningful tile-grid terrain (similar to battlemaps).
The base terrain comes from shape elements, not the tile grid. This stub
exists so the dispatcher doesn't fail when called with map_type='TOWN'.
"""

GLYPHS = {'Blank': ' '}
UNKNOWN_GLYPH = '?'


def glyph_for(terrain_name: str) -> str:
    if not terrain_name:
        return UNKNOWN_GLYPH
    return GLYPHS.get(terrain_name.split('/', 1)[-1], UNKNOWN_GLYPH)


def decorations_for(terrain_name: str, cx: float, cy: float,
                    col: int, row: int) -> str:
    return ''
