"""
Cosmic-scale icon library — STUB.

To be filled in when cosmic map samples are produced.

Anticipated categories per spec Appendix D:
  - Stellar Bodies (star, planet, moon, asteroid, comet, gas_giant)
  - Constructed (space_station, jump_gate, derelict, fleet_anchorage)
  - Anomalies (nebula, black_hole, dust_cloud, warp_storm, anomaly)
  - Routes (trade_lane, jump_line, patrol_route, pilgrim_route)
"""


def _placeholder(x, y, scale=1.0, visibility='known', **kw):
    """Star burst placeholder until cosmic icons exist."""
    op = ' opacity="0.35"' if visibility == 'hidden' else ''
    r = 14 * scale
    return (
        f'<g{op}>'
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="#f0d860" '
        f'stroke="#3a2410" stroke-width="2"/>'
        f'<line x1="{x - 22 * scale:.1f}" y1="{y:.1f}" x2="{x + 22 * scale:.1f}" y2="{y:.1f}" '
        f'stroke="#f0d860" stroke-width="1.5"/>'
        f'<line x1="{x:.1f}" y1="{y - 22 * scale:.1f}" x2="{x:.1f}" y2="{y + 22 * scale:.1f}" '
        f'stroke="#f0d860" stroke-width="1.5"/>'
        f'</g>'
    )


_STUB_TYPES = [
    'star', 'planet', 'moon', 'asteroid', 'comet', 'gas_giant',
    'space_station', 'jump_gate', 'derelict', 'fleet_anchorage',
    'nebula', 'black_hole', 'dust_cloud', 'warp_storm', 'anomaly',
    'landmark',
]

ICONS = {name: _placeholder for name in _STUB_TYPES}


def list_types() -> dict:
    return {
        'Stellar Bodies': ['star', 'planet', 'moon', 'asteroid', 'comet', 'gas_giant'],
        'Constructed': ['space_station', 'jump_gate', 'derelict', 'fleet_anchorage'],
        'Anomalies': ['nebula', 'black_hole', 'dust_cloud', 'warp_storm', 'anomaly'],
        'Generic': ['landmark'],
    }
