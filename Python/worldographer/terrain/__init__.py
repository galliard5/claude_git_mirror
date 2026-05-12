"""
Terrain library — scale-aware dispatcher for terrain glyphs and decorations.

Each scale-specific submodule (terrain.world, terrain.town, terrain.battlemap)
exports:
  - GLYPHS: dict mapping terrain name → single-character glyph
  - decorations_for(terrain_name, cx, cy, col, row) -> str    # SVG snippet for hex decorations
  - glyph_for(terrain_name) -> str
"""
from importlib import import_module


_LOADED = {}


def _scale_for_map_type(map_type: str) -> str:
    mt = (map_type or '').upper()
    if mt == 'BATTLEMAT':
        return 'battlemap'
    if mt == 'TOWN':
        return 'town'
    return 'world'


def _load(scale: str):
    if scale not in _LOADED:
        try:
            _LOADED[scale] = import_module(f'.{scale}', package='terrain')
        except ImportError:
            _LOADED[scale] = import_module(f'terrain.{scale}')
    return _LOADED[scale]


def glyph_for(terrain_name: str, map_type: str = 'WORLD',
              project_reskins: dict = None) -> str:
    """Return the single-character glyph for a terrain name.

    project_reskins lets project files override default glyphs (e.g. Aethelmark
    maps Underdark Open to 'r' for rural neighbourhood).
    """
    if project_reskins and terrain_name in project_reskins:
        reskin = project_reskins[terrain_name]
        if isinstance(reskin, dict) and 'glyph' in reskin:
            return reskin['glyph']
        if isinstance(reskin, str):
            return reskin
    module = _load(_scale_for_map_type(map_type))
    return module.glyph_for(terrain_name)


def decorations_for(terrain_name: str, cx: float, cy: float,
                    col: int, row: int, map_type: str = 'WORLD') -> str:
    module = _load(_scale_for_map_type(map_type))
    return module.decorations_for(terrain_name, cx, cy, col, row)
