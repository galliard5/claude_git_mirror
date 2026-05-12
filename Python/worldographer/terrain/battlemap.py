"""
Battlemap-scale terrain library — STUB.

Battlemap maps have all-uniform tile grids; visible terrain comes from
shape elements. This stub exists so the dispatcher doesn't fail when called
with map_type='BATTLEMAT'.
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
