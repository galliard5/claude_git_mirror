"""
Icon library — scale-aware dispatcher.

Each scale-specific submodule (icons.world, icons.town, icons.battlemap, icons.cosmic)
exports the same interface:

  - ICONS: dict mapping type-name → drawing function
  - draw(type, x, y, scale=1.0, **kwargs) -> str    # returns an SVG snippet
  - list_types() -> dict[str, list[str]]            # categorised type list

This module routes calls to the right submodule based on the map type.
"""
from importlib import import_module


# Cache loaded scale modules so we only import each once per session.
_LOADED = {}


def _scale_for_map_type(map_type: str) -> str:
    """Worldographer map type → icon library scale."""
    mt = (map_type or '').upper()
    if mt == 'BATTLEMAT':
        return 'battlemap'
    if mt == 'COSMIC':
        return 'cosmic'
    if mt == 'TOWN':
        return 'town'
    return 'world'   # WORLD or anything else


def _load(scale: str):
    if scale not in _LOADED:
        try:
            _LOADED[scale] = import_module(f'.{scale}', package='icons')
        except ImportError:
            _LOADED[scale] = import_module(f'icons.{scale}')
    return _LOADED[scale]


def draw(icon_type: str, x: float, y: float, scale: float = 1.0,
         map_type: str = 'WORLD', **kwargs) -> str:
    """Render an icon by type name. Hard-fails on unknown types per the spec."""
    module = _load(_scale_for_map_type(map_type))
    if icon_type not in module.ICONS:
        valid = sorted(module.ICONS)
        raise ValueError(
            f"Unknown icon type {icon_type!r} for {map_type} maps. "
            f"Valid types: {', '.join(valid)}. "
            f"Use 'landmark' as a generic fallback if no specific type fits."
        )
    return module.ICONS[icon_type](x, y, scale, **kwargs)


def list_types(map_type: str = 'WORLD') -> dict:
    """Return categorised type list for a given map type's scale."""
    module = _load(_scale_for_map_type(map_type))
    return module.list_types()


def all_types(map_type: str = 'WORLD') -> list:
    """Flat list of all valid type names for a map type."""
    module = _load(_scale_for_map_type(map_type))
    return sorted(module.ICONS.keys())
