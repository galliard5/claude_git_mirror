"""
Aethelmark project styling — autumn mountains, bright valley palette,
plus the rural-neighbourhood reskin of Underdark Open.

Applied when a map's annotation file declares `project: aethelmark` (or when
the renderer is invoked with `--project aethelmark`).
"""

# Palette overrides — these win over the authoritative Worldographer palette.
# Aethelmark/Silberbach Valley uses warmer, more saturated takes on the
# default Classic colours: autumn brown mountains, bright valley greens.
PALETTE_OVERRIDES = {
    # Repurposed terrain — see TERRAIN_RESKINS below.
    'Classic/Underdark Open':               '#ead9bc',  # rural neighbourhood (cream-pink)

    # Mountain palette — autumn brown family.
    'Classic/Mountains Forest Evergreen':   '#8a6a3a',
    'Classic/Hills Forest Evergreen':       '#6a8a4a',
    'Classic/Mountain Forest Evergreen':    '#7a6a3a',
    'Classic/Mountains':                    '#b08a55',

    # Valley palette — bright greens.
    'Classic/Flat Forest Evergreen':        '#5e8542',
    'Classic/Flat Farmland':                '#a8c878',
    'Classic/Hills Grassland':              '#d4d896',
    'Classic/Flat Farmland Cultivated':     '#e8d870',
    'Classic/Flat Forest Evergreen Heavy':  '#3a5a30',

    # Water — softer than authoritative.
    'Classic/Water Sea':                    '#7fa9c4',
}

# Terrain reskins — semantic remapping. The terrain ID is the same in
# Worldographer, but the project treats it as something different.
#
# Underdark Open is repurposed at world-scale to mean "rural neighbourhood"
# (a small clustered settlement area, typically around major towns). The
# glyph in the description block reflects this rather than the literal
# Worldographer terrain meaning.
TERRAIN_RESKINS = {
    'Classic/Underdark Open': {
        'glyph': 'r',                              # 'r' for rural (replaces default '?')
        'description': 'Rural neighbourhood',      # used in terrain legend
    },
}

# No icon reskins yet — Aethelmark uses the standard world-scale icon library.
ICON_RESKINS = {}

# Aethelmark uses the default backgrounds.
HEX_BACKGROUND_COLOR = '#f0e3c2'
SQUARE_BACKGROUND_COLOR = '#ADD8E6'
