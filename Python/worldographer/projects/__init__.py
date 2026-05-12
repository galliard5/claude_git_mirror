"""
Project-specific styling overrides for the Worldographer renderer.

Each module in this package exports:
  - PALETTE_OVERRIDES: dict mapping terrain name → '#rrggbb', wins over the
    authoritative Worldographer palette.
  - TERRAIN_RESKINS: dict mapping terrain name → glyph override (optional —
    use when a project semantically reskins a terrain, e.g. Aethelmark uses
    Underdark Open as rural neighbourhoods).
  - ICON_RESKINS: dict mapping icon name → alternate inline-SVG drawing
    (optional — use when a project wants distinctive art for specific icons).

The renderer loads a project module by name (set via ## Project section in
the annotation file, or --project CLI flag). Defaults to 'default'.
"""
from importlib import import_module


def load(name: str = 'default'):
    """Import and return a project module by name.

    Returns the module so callers can read .PALETTE_OVERRIDES etc directly.
    """
    if name in (None, '', 'none'):
        name = 'default'
    try:
        return import_module(f'.{name}', package='projects')
    except ImportError:
        # Fallback: try as top-level module if package context isn't set up
        return import_module(f'projects.{name}')
