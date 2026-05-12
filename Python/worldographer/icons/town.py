"""
Town-scale icon library — STUB.

To be filled in when town map samples are produced. The structure is in place
so the orchestrator's dispatch logic doesn't have to special-case missing
libraries.

Anticipated categories per spec Appendix B:
  - Public / Civic (town hall, courthouse, jail, market hall)
  - Commercial (tavern, inn, smithy, market stall, general store)
  - Residential (townhouse, tenement, mansion, cottage)
  - Industrial (workshop, warehouse, granary, stable)
  - Religious (temple, chapel, shrine)
  - Architectural (wall_section, gate, plaza, fountain, bridge)
"""


def _placeholder(x, y, scale=1.0, visibility='known', **kw):
    """Generic placeholder marker — small filled circle until town icons exist."""
    op = ' opacity="0.35"' if visibility == 'hidden' else ''
    return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{18 * scale:.1f}" '
            f'fill="#888080" stroke="#3a1410" stroke-width="2"{op}/>')


# Minimum viable registry — every type points at the placeholder for now.
# When real icons are added, replace each entry with a proper drawing function.
_STUB_TYPES = [
    'town_hall', 'courthouse', 'jail', 'market_hall',
    'tavern', 'inn', 'smithy', 'market_stall', 'general_store',
    'townhouse', 'tenement', 'mansion', 'cottage',
    'workshop', 'warehouse', 'granary', 'stable',
    'temple', 'chapel', 'shrine',
    'wall_section', 'gate', 'plaza', 'fountain', 'bridge',
    'landmark',
]

ICONS = {name: _placeholder for name in _STUB_TYPES}


def list_types() -> dict:
    return {
        'Public / Civic': ['town_hall', 'courthouse', 'jail', 'market_hall'],
        'Commercial': ['tavern', 'inn', 'smithy', 'market_stall', 'general_store'],
        'Residential': ['townhouse', 'tenement', 'mansion', 'cottage'],
        'Industrial': ['workshop', 'warehouse', 'granary', 'stable'],
        'Religious': ['temple', 'chapel', 'shrine'],
        'Architectural': ['wall_section', 'gate', 'plaza', 'fountain', 'bridge'],
        'Generic': ['landmark'],
    }
