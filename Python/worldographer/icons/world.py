"""
World-scale icon library.

Every icon is a function that returns an SVG snippet placed at (x, y) with
optional scale. Functions follow a uniform signature:

    def icon_name(x: float, y: float, scale: float = 1.0, **kwargs) -> str

Kwargs may include 'visibility' (known | local | hidden), which influences
opacity / outlining. Hidden icons render with a ghost outline; local icons
render normally but the renderer suppresses their label on player maps.

The icons are deliberately stylised line art rather than realistic — they
need to read clearly at small map sizes against a parchment background.

Type vocabulary follows Spec Appendix A.
"""
from __future__ import annotations


# =============================================================================
# Helpers
# =============================================================================

def _opacity(visibility: str) -> float:
    """Hidden icons are ghosted at 35% opacity; local/known fully opaque."""
    return 0.35 if visibility == 'hidden' else 1.0


def _visibility_filter(visibility: str) -> str:
    """SVG attribute string for visibility-driven styling."""
    if visibility == 'hidden':
        return ' opacity="0.35" stroke-dasharray="4 3"'
    return ''


def _wrap(x: float, y: float, scale: float, body: str, visibility: str = 'known') -> str:
    """Wrap an icon body in a transform group with optional visibility filter."""
    op = _visibility_filter(visibility)
    return (f'<g transform="translate({x:.1f},{y:.1f}) scale({scale:.2f})"{op}>'
            f'{body}</g>')


# =============================================================================
# SETTLEMENTS
# =============================================================================

def capital(x, y, scale=1.0, visibility='known', **kw):
    """Walled city with three towers — primary capital marker."""
    body = (
        # City walls (outer)
        '<rect x="-50" y="-30" width="100" height="60" fill="#a04a2e" '
        'stroke="#3a1410" stroke-width="3" rx="4"/>'
        # Three towers
        '<rect x="-55" y="-50" width="20" height="30" fill="#b85a3e" stroke="#3a1410" stroke-width="3"/>'
        '<rect x="-10" y="-58" width="20" height="38" fill="#b85a3e" stroke="#3a1410" stroke-width="3"/>'
        '<rect x="35" y="-50" width="20" height="30" fill="#b85a3e" stroke="#3a1410" stroke-width="3"/>'
        # Crenellations on center tower
        '<rect x="-10" y="-62" width="6" height="6" fill="#3a1410"/>'
        '<rect x="-2" y="-62" width="6" height="6" fill="#3a1410"/>'
        '<rect x="6" y="-62" width="6" height="6" fill="#3a1410"/>'
        # Gate
        '<rect x="-10" y="0" width="20" height="30" fill="#2a1408"/>'
    )
    return _wrap(x, y, scale, body, visibility)


def city(x, y, scale=1.0, visibility='known', **kw):
    """Walled city, smaller than capital — two towers, broader walls."""
    body = (
        '<rect x="-40" y="-22" width="80" height="44" fill="#a26a3a" '
        'stroke="#3a1410" stroke-width="2.5" rx="3"/>'
        '<rect x="-44" y="-38" width="16" height="22" fill="#b87a4a" stroke="#3a1410" stroke-width="2.5"/>'
        '<rect x="28" y="-38" width="16" height="22" fill="#b87a4a" stroke="#3a1410" stroke-width="2.5"/>'
        '<rect x="-7" y="0" width="14" height="22" fill="#2a1408"/>'
    )
    return _wrap(x, y, scale, body, visibility)


def town(x, y, scale=1.0, visibility='known', **kw):
    """Town — clustered houses with a central larger building."""
    body = (
        # Central larger house
        '<rect x="-22" y="-12" width="44" height="28" fill="#c89a5a" stroke="#3a1410" stroke-width="2"/>'
        '<polygon points="-26,-12 0,-30 26,-12" fill="#8a4a2a" stroke="#3a1410" stroke-width="2"/>'
        # Smaller flanking houses
        '<rect x="-50" y="-2" width="22" height="18" fill="#c89a5a" stroke="#3a1410" stroke-width="2"/>'
        '<polygon points="-52,-2 -39,-14 -26,-2" fill="#8a4a2a" stroke="#3a1410" stroke-width="2"/>'
        '<rect x="28" y="-2" width="22" height="18" fill="#c89a5a" stroke="#3a1410" stroke-width="2"/>'
        '<polygon points="26,-2 39,-14 52,-2" fill="#8a4a2a" stroke="#3a1410" stroke-width="2"/>'
    )
    return _wrap(x, y, scale, body, visibility)


def village(x, y, scale=1.0, visibility='known', **kw):
    """Village — pair of houses."""
    body = (
        '<rect x="-30" y="-8" width="24" height="20" fill="#c89a5a" stroke="#3a1410" stroke-width="2"/>'
        '<polygon points="-32,-8 -18,-22 -4,-8" fill="#8a4a2a" stroke="#3a1410" stroke-width="2"/>'
        '<rect x="6" y="-4" width="22" height="16" fill="#c89a5a" stroke="#3a1410" stroke-width="2"/>'
        '<polygon points="4,-4 17,-16 30,-4" fill="#8a4a2a" stroke="#3a1410" stroke-width="2"/>'
    )
    return _wrap(x, y, scale, body, visibility)


def hamlet(x, y, scale=1.0, visibility='known', **kw):
    """Hamlet — single small house with a chimney."""
    body = (
        '<rect x="-14" y="-6" width="28" height="20" fill="#c89a5a" stroke="#3a1410" stroke-width="2"/>'
        '<polygon points="-16,-6 0,-22 16,-6" fill="#8a4a2a" stroke="#3a1410" stroke-width="2"/>'
        '<rect x="6" y="-20" width="6" height="10" fill="#3a1410"/>'   # chimney
    )
    return _wrap(x, y, scale, body, visibility)


def manor(x, y, scale=1.0, visibility='known', **kw):
    """Manor house — single substantial building with two chimneys."""
    body = (
        '<rect x="-26" y="-10" width="52" height="24" fill="#cba47a" stroke="#3a1410" stroke-width="2.5"/>'
        '<polygon points="-28,-10 0,-28 28,-10" fill="#7a3a1f" stroke="#3a1410" stroke-width="2.5"/>'
        '<rect x="-18" y="-26" width="6" height="12" fill="#3a1410"/>'
        '<rect x="12" y="-26" width="6" height="12" fill="#3a1410"/>'
        # Door
        '<rect x="-4" y="0" width="8" height="14" fill="#3a1410"/>'
    )
    return _wrap(x, y, scale, body, visibility)


def hold(x, y, scale=1.0, visibility='known', **kw):
    """Hold — long-house silhouette for clan seats."""
    body = (
        '<polygon points="-44,12 -38,-8 38,-8 44,12" fill="#a06a3a" stroke="#3a1410" stroke-width="2.5"/>'
        '<polygon points="-38,-8 0,-22 38,-8" fill="#5a2a14" stroke="#3a1410" stroke-width="2.5"/>'
        # Door
        '<rect x="-5" y="0" width="10" height="12" fill="#2a1408"/>'
    )
    return _wrap(x, y, scale, body, visibility)


# =============================================================================
# DEFENSIVE
# =============================================================================

def fort(x, y, scale=1.0, visibility='known', **kw):
    """Square fort with corner towers."""
    body = (
        '<rect x="-24" y="-24" width="48" height="48" fill="#888080" stroke="#3a1410" stroke-width="2.5"/>'
        # Corner towers
        '<rect x="-30" y="-30" width="14" height="14" fill="#a09890" stroke="#3a1410" stroke-width="2"/>'
        '<rect x="16" y="-30" width="14" height="14" fill="#a09890" stroke="#3a1410" stroke-width="2"/>'
        '<rect x="-30" y="16" width="14" height="14" fill="#a09890" stroke="#3a1410" stroke-width="2"/>'
        '<rect x="16" y="16" width="14" height="14" fill="#a09890" stroke="#3a1410" stroke-width="2"/>'
        # Gate
        '<rect x="-6" y="14" width="12" height="14" fill="#3a1410"/>'
    )
    return _wrap(x, y, scale, body, visibility)


def watchtower(x, y, scale=1.0, visibility='known', **kw):
    """Single tall tower with crenellations."""
    body = (
        '<rect x="-12" y="-32" width="24" height="44" fill="#a09890" stroke="#3a1410" stroke-width="2"/>'
        # Crenellations
        '<rect x="-14" y="-36" width="6" height="6" fill="#3a1410"/>'
        '<rect x="-4" y="-36" width="6" height="6" fill="#3a1410"/>'
        '<rect x="6" y="-36" width="6" height="6" fill="#3a1410"/>'
        # Window
        '<rect x="-3" y="-18" width="6" height="8" fill="#1a0e05"/>'
    )
    return _wrap(x, y, scale, body, visibility)


def keep(x, y, scale=1.0, visibility='known', **kw):
    """Square keep — single stout structure."""
    body = (
        '<rect x="-22" y="-26" width="44" height="40" fill="#888080" stroke="#3a1410" stroke-width="3"/>'
        # Battlements
        '<rect x="-24" y="-30" width="6" height="6" fill="#3a1410"/>'
        '<rect x="-12" y="-30" width="6" height="6" fill="#3a1410"/>'
        '<rect x="0" y="-30" width="6" height="6" fill="#3a1410"/>'
        '<rect x="12" y="-30" width="6" height="6" fill="#3a1410"/>'
        # Slit windows
        '<rect x="-3" y="-16" width="6" height="10" fill="#1a0e05"/>'
        '<rect x="-3" y="2" width="6" height="10" fill="#1a0e05"/>'
    )
    return _wrap(x, y, scale, body, visibility)


def ruined_keep(x, y, scale=1.0, visibility='known', **kw):
    """Broken-walled keep — irregular silhouette suggesting ruin."""
    body = (
        '<polygon points="-22,14 -22,-22 -10,-22 -10,-12 -2,-12 -2,-26 8,-26 8,-16 22,-16 22,14" '
        'fill="#888080" stroke="#3a1410" stroke-width="2.5"/>'
        # Cracks
        '<line x1="-12" y1="14" x2="-8" y2="-12" stroke="#3a1410" stroke-width="1.5"/>'
        '<line x1="6" y1="14" x2="10" y2="-16" stroke="#3a1410" stroke-width="1.5"/>'
    )
    return _wrap(x, y, scale, body, visibility)


def palisade(x, y, scale=1.0, visibility='known', **kw):
    """Wooden palisade — pointed-top stake fence."""
    body = (
        '<polygon points="-30,12 -26,-8 -22,-12 -18,-8 -14,-12 -10,-8 -6,-12 -2,-8 2,-12 6,-8 10,-12 14,-8 18,-12 22,-8 26,-12 30,-8 30,12" '
        'fill="#8a5a2e" stroke="#3a1410" stroke-width="2"/>'
        # Vertical stake separators
        '<line x1="-22" y1="12" x2="-22" y2="-10" stroke="#3a1410" stroke-width="1"/>'
        '<line x1="-10" y1="12" x2="-10" y2="-10" stroke="#3a1410" stroke-width="1"/>'
        '<line x1="2" y1="12" x2="2" y2="-10" stroke="#3a1410" stroke-width="1"/>'
        '<line x1="14" y1="12" x2="14" y2="-10" stroke="#3a1410" stroke-width="1"/>'
    )
    return _wrap(x, y, scale, body, visibility)


# =============================================================================
# INFRASTRUCTURE
# =============================================================================

def tollbooth(x, y, scale=1.0, visibility='known', **kw):
    """Small gate-like structure spanning a road."""
    body = (
        '<rect x="-22" y="-4" width="6" height="20" fill="#6a4a2a" stroke="#3a1410" stroke-width="2"/>'
        '<rect x="16" y="-4" width="6" height="20" fill="#6a4a2a" stroke="#3a1410" stroke-width="2"/>'
        '<rect x="-22" y="-10" width="44" height="6" fill="#8a6a3a" stroke="#3a1410" stroke-width="2"/>'
        # Sign
        '<rect x="-8" y="-22" width="16" height="10" fill="#d8b878" stroke="#3a1410" stroke-width="1.5"/>'
    )
    return _wrap(x, y, scale, body, visibility)


def bridge(x, y, scale=1.0, visibility='known', **kw):
    """Stone arch bridge — half-circle silhouette over stylised water."""
    body = (
        '<path d="M -28 8 L -28 0 Q 0 -28 28 0 L 28 8 Z" fill="#a89888" stroke="#3a1410" stroke-width="2"/>'
        '<path d="M -22 8 L -22 2 Q 0 -18 22 2 L 22 8 Z" fill="none" stroke="#3a1410" stroke-width="1.5"/>'
        # Water
        '<line x1="-30" y1="12" x2="30" y2="12" stroke="#5a8aa8" stroke-width="2"/>'
        '<path d="M -28 14 q 4 -2 8 0 t 8 0 t 8 0 t 8 0 t 8 0 t 8 0" fill="none" stroke="#5a8aa8" stroke-width="1.5"/>'
    )
    return _wrap(x, y, scale, body, visibility)


def ford(x, y, scale=1.0, visibility='known', **kw):
    """Ford — stones in a stream."""
    body = (
        # Water
        '<rect x="-30" y="-6" width="60" height="14" fill="#9ac0d8" opacity="0.6"/>'
        # Stepping stones
        '<ellipse cx="-18" cy="0" rx="6" ry="4" fill="#a89888" stroke="#3a1410" stroke-width="1.5"/>'
        '<ellipse cx="-4" cy="2" rx="6" ry="4" fill="#a89888" stroke="#3a1410" stroke-width="1.5"/>'
        '<ellipse cx="10" cy="0" rx="6" ry="4" fill="#a89888" stroke="#3a1410" stroke-width="1.5"/>'
        '<ellipse cx="22" cy="2" rx="6" ry="4" fill="#a89888" stroke="#3a1410" stroke-width="1.5"/>'
    )
    return _wrap(x, y, scale, body, visibility)


def ferry(x, y, scale=1.0, visibility='known', **kw):
    """Ferry — small boat with mast over water."""
    body = (
        # Water
        '<line x1="-30" y1="14" x2="30" y2="14" stroke="#5a8aa8" stroke-width="2"/>'
        '<path d="M -28 16 q 4 -2 8 0 t 8 0 t 8 0 t 8 0 t 8 0 t 8 0" fill="none" stroke="#5a8aa8" stroke-width="1.5"/>'
        # Boat hull
        '<path d="M -22 8 L 22 8 L 18 14 L -18 14 Z" fill="#8a5a2e" stroke="#3a1410" stroke-width="2"/>'
        # Mast
        '<line x1="0" y1="8" x2="0" y2="-18" stroke="#3a1410" stroke-width="2"/>'
        # Sail
        '<polygon points="0,-18 14,-4 0,0" fill="#e8d8b8" stroke="#3a1410" stroke-width="1.5"/>'
    )
    return _wrap(x, y, scale, body, visibility)


def mill(x, y, scale=1.0, visibility='known', **kw):
    """Windmill — building with four blades."""
    body = (
        '<rect x="-12" y="-4" width="24" height="20" fill="#cba47a" stroke="#3a1410" stroke-width="2"/>'
        '<polygon points="-14,-4 0,-18 14,-4" fill="#7a3a1f" stroke="#3a1410" stroke-width="2"/>'
        # Blades
        '<line x1="0" y1="-12" x2="0" y2="-30" stroke="#3a1410" stroke-width="2"/>'
        '<line x1="0" y1="-12" x2="-16" y2="-12" stroke="#3a1410" stroke-width="2"/>'
        '<line x1="0" y1="-12" x2="0" y2="6" stroke="#3a1410" stroke-width="2"/>'
        '<line x1="0" y1="-12" x2="16" y2="-12" stroke="#3a1410" stroke-width="2"/>'
        '<circle cx="0" cy="-12" r="3" fill="#3a1410"/>'
    )
    return _wrap(x, y, scale, body, visibility)


def lighthouse(x, y, scale=1.0, visibility='known', **kw):
    """Lighthouse — tapered tower with a beacon at top."""
    body = (
        '<polygon points="-12,16 -8,-22 8,-22 12,16" fill="#e8d8b8" stroke="#3a1410" stroke-width="2.5"/>'
        # Stripes
        '<rect x="-10" y="-10" width="20" height="6" fill="#a04a2e"/>'
        '<rect x="-11" y="6" width="22" height="6" fill="#a04a2e"/>'
        # Beacon
        '<rect x="-6" y="-30" width="12" height="8" fill="#3a1410"/>'
        '<polygon points="-8,-30 0,-38 8,-30" fill="#3a1410"/>'
        # Light rays
        '<line x1="0" y1="-26" x2="-18" y2="-30" stroke="#f0d860" stroke-width="1.5" opacity="0.6"/>'
        '<line x1="0" y1="-26" x2="18" y2="-30" stroke="#f0d860" stroke-width="1.5" opacity="0.6"/>'
    )
    return _wrap(x, y, scale, body, visibility)


def well(x, y, scale=1.0, visibility='known', **kw):
    """Stone well with a small roof."""
    body = (
        '<ellipse cx="0" cy="10" rx="14" ry="5" fill="#888080" stroke="#3a1410" stroke-width="2"/>'
        '<rect x="-14" y="-2" width="28" height="12" fill="#a89888" stroke="#3a1410" stroke-width="2"/>'
        '<ellipse cx="0" cy="-2" rx="14" ry="5" fill="#1a1410"/>'
        # Roof posts
        '<line x1="-10" y1="-2" x2="-10" y2="-22" stroke="#3a1410" stroke-width="2"/>'
        '<line x1="10" y1="-2" x2="10" y2="-22" stroke="#3a1410" stroke-width="2"/>'
        # Roof
        '<polygon points="-14,-22 14,-22 0,-32" fill="#7a3a1f" stroke="#3a1410" stroke-width="2"/>'
    )
    return _wrap(x, y, scale, body, visibility)


def waystation(x, y, scale=1.0, visibility='known', **kw):
    """Waystation — small inn-like building with a sign post."""
    body = (
        '<rect x="-22" y="-6" width="44" height="22" fill="#cba47a" stroke="#3a1410" stroke-width="2"/>'
        '<polygon points="-24,-6 0,-22 24,-6" fill="#7a3a1f" stroke="#3a1410" stroke-width="2"/>'
        # Sign post
        '<line x1="-30" y1="16" x2="-30" y2="-8" stroke="#3a1410" stroke-width="2"/>'
        '<rect x="-38" y="-12" width="16" height="8" fill="#d8b878" stroke="#3a1410" stroke-width="1.5"/>'
        # Door
        '<rect x="-4" y="4" width="8" height="12" fill="#3a1410"/>'
    )
    return _wrap(x, y, scale, body, visibility)


# =============================================================================
# RELIGIOUS / CULTURAL
# =============================================================================

def shrine(x, y, scale=1.0, visibility='known', **kw):
    """Small shrine — pillar with an altar piece."""
    body = (
        '<rect x="-10" y="-2" width="20" height="18" fill="#cba47a" stroke="#3a1410" stroke-width="2"/>'
        '<polygon points="-14,-2 0,-22 14,-2" fill="#a89888" stroke="#3a1410" stroke-width="2"/>'
        # Sacred mark
        '<circle cx="0" cy="6" r="3" fill="#a04a2e" stroke="#3a1410" stroke-width="1"/>'
    )
    return _wrap(x, y, scale, body, visibility)


def temple(x, y, scale=1.0, visibility='known', **kw):
    """Temple — columned facade with a triangular pediment."""
    body = (
        '<polygon points="-30,-6 -24,-18 24,-18 30,-6" fill="#e8d8b8" stroke="#3a1410" stroke-width="2.5"/>'
        '<rect x="-26" y="-6" width="52" height="22" fill="#cba47a" stroke="#3a1410" stroke-width="2.5"/>'
        # Columns
        '<rect x="-22" y="-6" width="4" height="22" fill="#a89888" stroke="#3a1410" stroke-width="1"/>'
        '<rect x="-12" y="-6" width="4" height="22" fill="#a89888" stroke="#3a1410" stroke-width="1"/>'
        '<rect x="-2" y="-6" width="4" height="22" fill="#a89888" stroke="#3a1410" stroke-width="1"/>'
        '<rect x="8" y="-6" width="4" height="22" fill="#a89888" stroke="#3a1410" stroke-width="1"/>'
        '<rect x="18" y="-6" width="4" height="22" fill="#a89888" stroke="#3a1410" stroke-width="1"/>'
    )
    return _wrap(x, y, scale, body, visibility)


def monastery(x, y, scale=1.0, visibility='known', **kw):
    """Monastery — chapel with attached cloister wing."""
    body = (
        '<rect x="-24" y="-2" width="30" height="20" fill="#cba47a" stroke="#3a1410" stroke-width="2"/>'
        '<polygon points="-26,-2 -9,-18 8,-2" fill="#7a3a1f" stroke="#3a1410" stroke-width="2"/>'
        # Bell tower
        '<rect x="6" y="-18" width="14" height="36" fill="#a89888" stroke="#3a1410" stroke-width="2"/>'
        '<polygon points="4,-18 13,-30 22,-18" fill="#7a3a1f" stroke="#3a1410" stroke-width="2"/>'
        # Cross
        '<line x1="13" y1="-30" x2="13" y2="-38" stroke="#3a1410" stroke-width="2"/>'
        '<line x1="9" y1="-34" x2="17" y2="-34" stroke="#3a1410" stroke-width="2"/>'
    )
    return _wrap(x, y, scale, body, visibility)


def cemetery(x, y, scale=1.0, visibility='known', **kw):
    """Cemetery — three tombstones."""
    body = (
        # Ground
        '<rect x="-26" y="10" width="52" height="6" fill="#7a8a5a" stroke="#3a1410" stroke-width="1"/>'
        # Tombstones
        '<path d="M -18 10 L -18 -8 Q -18 -14 -14 -14 Q -10 -14 -10 -8 L -10 10 Z" fill="#a89888" stroke="#3a1410" stroke-width="1.5"/>'
        '<path d="M -4 10 L -4 -12 Q -4 -18 0 -18 Q 4 -18 4 -12 L 4 10 Z" fill="#a89888" stroke="#3a1410" stroke-width="1.5"/>'
        '<path d="M 10 10 L 10 -6 Q 10 -12 14 -12 Q 18 -12 18 -6 L 18 10 Z" fill="#a89888" stroke="#3a1410" stroke-width="1.5"/>'
        # Cross on center
        '<line x1="0" y1="-14" x2="0" y2="-6" stroke="#3a1410" stroke-width="1.5"/>'
        '<line x1="-3" y1="-11" x2="3" y2="-11" stroke="#3a1410" stroke-width="1.5"/>'
    )
    return _wrap(x, y, scale, body, visibility)


def gibbet(x, y, scale=1.0, visibility='known', **kw):
    """Gibbet — execution post with hanging cage."""
    body = (
        # Post
        '<line x1="0" y1="20" x2="0" y2="-26" stroke="#3a1410" stroke-width="3"/>'
        # Crossbeam
        '<line x1="0" y1="-26" x2="14" y2="-26" stroke="#3a1410" stroke-width="3"/>'
        # Rope
        '<line x1="14" y1="-26" x2="14" y2="-16" stroke="#3a1410" stroke-width="1.5"/>'
        # Cage
        '<rect x="9" y="-16" width="10" height="14" fill="none" stroke="#3a1410" stroke-width="1.5"/>'
        '<line x1="9" y1="-12" x2="19" y2="-12" stroke="#3a1410" stroke-width="1"/>'
        '<line x1="9" y1="-7" x2="19" y2="-7" stroke="#3a1410" stroke-width="1"/>'
        '<line x1="14" y1="-16" x2="14" y2="-2" stroke="#3a1410" stroke-width="1"/>'
        # Base (mound)
        '<ellipse cx="0" cy="20" rx="10" ry="3" fill="#7a8a5a" stroke="#3a1410" stroke-width="1"/>'
    )
    return _wrap(x, y, scale, body, visibility)


def monument(x, y, scale=1.0, visibility='known', **kw):
    """Monument — tall obelisk on a base."""
    body = (
        '<rect x="-12" y="14" width="24" height="6" fill="#888080" stroke="#3a1410" stroke-width="2"/>'
        '<polygon points="-7,14 -5,-22 0,-30 5,-22 7,14" fill="#a89888" stroke="#3a1410" stroke-width="2"/>'
    )
    return _wrap(x, y, scale, body, visibility)


def standing_stones(x, y, scale=1.0, visibility='known', **kw):
    """Standing stones — three monoliths in a circle."""
    body = (
        '<ellipse cx="0" cy="14" rx="22" ry="4" fill="#7a8a5a" stroke="#3a1410" stroke-width="1"/>'
        '<rect x="-22" y="-12" width="8" height="24" rx="2" fill="#888080" stroke="#3a1410" stroke-width="1.5"/>'
        '<rect x="-4" y="-18" width="8" height="30" rx="2" fill="#888080" stroke="#3a1410" stroke-width="1.5"/>'
        '<rect x="14" y="-12" width="8" height="24" rx="2" fill="#888080" stroke="#3a1410" stroke-width="1.5"/>'
    )
    return _wrap(x, y, scale, body, visibility)


# =============================================================================
# RESOURCES
# =============================================================================

def mine(x, y, scale=1.0, visibility='known', **kw):
    """Mine — cave mouth with crossed pickaxes."""
    body = (
        # Mountain face
        '<polygon points="-24,16 -16,-12 -2,-22 12,-18 22,16" fill="#888080" stroke="#3a1410" stroke-width="2"/>'
        # Cave mouth
        '<path d="M -8 16 Q -8 -2 0 -4 Q 8 -2 8 16 Z" fill="#1a0e05"/>'
        # Crossed pickaxes
        '<line x1="-12" y1="22" x2="12" y2="-2" stroke="#3a1410" stroke-width="2"/>'
        '<line x1="-12" y1="-2" x2="12" y2="22" stroke="#3a1410" stroke-width="2"/>'
        '<polygon points="-14,22 -10,18 -8,22 -12,26" fill="#a89888" stroke="#3a1410" stroke-width="1"/>'
        '<polygon points="14,22 10,18 8,22 12,26" fill="#a89888" stroke="#3a1410" stroke-width="1"/>'
    )
    return _wrap(x, y, scale, body, visibility)


def quarry(x, y, scale=1.0, visibility='known', **kw):
    """Quarry — terraced cuts in a hillside."""
    body = (
        '<polygon points="-26,16 -22,4 -10,4 -6,-8 6,-8 10,-20 22,-20 26,16" '
        'fill="#a89888" stroke="#3a1410" stroke-width="2"/>'
        '<line x1="-22" y1="4" x2="26" y2="4" stroke="#3a1410" stroke-width="1"/>'
        '<line x1="-6" y1="-8" x2="22" y2="-8" stroke="#3a1410" stroke-width="1"/>'
    )
    return _wrap(x, y, scale, body, visibility)


def lumber_camp(x, y, scale=1.0, visibility='known', **kw):
    """Lumber camp — stacked logs and an axe-stuck stump."""
    body = (
        # Stump
        '<ellipse cx="-14" cy="14" rx="7" ry="3" fill="#5a3a1f" stroke="#3a1410" stroke-width="1.5"/>'
        '<rect x="-21" y="6" width="14" height="8" fill="#8a5a2e" stroke="#3a1410" stroke-width="1.5"/>'
        # Axe in stump
        '<line x1="-16" y1="6" x2="-12" y2="-8" stroke="#3a1410" stroke-width="2"/>'
        '<polygon points="-14,-10 -10,-12 -6,-8 -10,-6" fill="#a89888" stroke="#3a1410" stroke-width="1"/>'
        # Log pile
        '<rect x="2" y="0" width="22" height="6" rx="3" fill="#8a5a2e" stroke="#3a1410" stroke-width="1.5"/>'
        '<rect x="2" y="8" width="22" height="6" rx="3" fill="#8a5a2e" stroke="#3a1410" stroke-width="1.5"/>'
        '<circle cx="2" cy="3" r="3" fill="#5a3a1f" stroke="#3a1410" stroke-width="1"/>'
        '<circle cx="2" cy="11" r="3" fill="#5a3a1f" stroke="#3a1410" stroke-width="1"/>'
    )
    return _wrap(x, y, scale, body, visibility)


def fishing_camp(x, y, scale=1.0, visibility='known', **kw):
    """Fishing camp — small dock with hanging nets."""
    body = (
        # Water
        '<rect x="-26" y="12" width="52" height="6" fill="#7fa9c4" opacity="0.6"/>'
        # Dock
        '<rect x="-20" y="6" width="40" height="6" fill="#8a5a2e" stroke="#3a1410" stroke-width="1.5"/>'
        '<line x1="-16" y1="12" x2="-16" y2="20" stroke="#3a1410" stroke-width="1.5"/>'
        '<line x1="0" y1="12" x2="0" y2="20" stroke="#3a1410" stroke-width="1.5"/>'
        '<line x1="16" y1="12" x2="16" y2="20" stroke="#3a1410" stroke-width="1.5"/>'
        # Drying frame
        '<line x1="-10" y1="6" x2="-10" y2="-14" stroke="#3a1410" stroke-width="1.5"/>'
        '<line x1="10" y1="6" x2="10" y2="-14" stroke="#3a1410" stroke-width="1.5"/>'
        '<line x1="-10" y1="-14" x2="10" y2="-14" stroke="#3a1410" stroke-width="1.5"/>'
        # Net (zigzag)
        '<path d="M -10 -10 L -6 -6 L -2 -10 L 2 -6 L 6 -10 L 10 -6" fill="none" stroke="#3a1410" stroke-width="1"/>'
        '<path d="M -10 -4 L -6 0 L -2 -4 L 2 0 L 6 -4 L 10 0" fill="none" stroke="#3a1410" stroke-width="1"/>'
    )
    return _wrap(x, y, scale, body, visibility)


def salt_works(x, y, scale=1.0, visibility='known', **kw):
    """Salt works — evaporation ponds."""
    body = (
        '<rect x="-24" y="-6" width="20" height="10" fill="#e8d8b8" stroke="#3a1410" stroke-width="1.5"/>'
        '<rect x="4" y="-6" width="20" height="10" fill="#e8d8b8" stroke="#3a1410" stroke-width="1.5"/>'
        '<rect x="-24" y="6" width="20" height="10" fill="#e8d8b8" stroke="#3a1410" stroke-width="1.5"/>'
        '<rect x="4" y="6" width="20" height="10" fill="#e8d8b8" stroke="#3a1410" stroke-width="1.5"/>'
        # Salt crystals
        '<circle cx="-14" cy="-1" r="1.5" fill="#fff"/>'
        '<circle cx="14" cy="-1" r="1.5" fill="#fff"/>'
        '<circle cx="-14" cy="11" r="1.5" fill="#fff"/>'
        '<circle cx="14" cy="11" r="1.5" fill="#fff"/>'
    )
    return _wrap(x, y, scale, body, visibility)


# =============================================================================
# WILDERNESS / ADVENTURE
# =============================================================================

def ruin(x, y, scale=1.0, visibility='known', **kw):
    """Ruin — broken column and partial wall."""
    body = (
        # Broken column
        '<rect x="-16" y="-16" width="8" height="30" fill="#a89888" stroke="#3a1410" stroke-width="1.5"/>'
        '<polygon points="-18,-16 -12,-22 -6,-16" fill="#a89888" stroke="#3a1410" stroke-width="1.5"/>'
        # Fallen blocks
        '<rect x="2" y="6" width="10" height="6" fill="#a89888" stroke="#3a1410" stroke-width="1.5"/>'
        '<rect x="14" y="10" width="8" height="4" fill="#a89888" stroke="#3a1410" stroke-width="1.5"/>'
        # Vines
        '<path d="M -12 -22 q -4 4 -2 8 q -2 4 0 6" fill="none" stroke="#5a8a3a" stroke-width="1.5"/>'
    )
    return _wrap(x, y, scale, body, visibility)


def dungeon(x, y, scale=1.0, visibility='known', **kw):
    """Dungeon — arched doorway in stone."""
    body = (
        '<polygon points="-22,16 -18,-12 -10,-20 10,-20 18,-12 22,16" fill="#888080" stroke="#3a1410" stroke-width="2.5"/>'
        '<path d="M -8 16 L -8 -6 Q -8 -14 0 -14 Q 8 -14 8 -6 L 8 16 Z" fill="#1a0e05"/>'
        # Stone blocks (texture)
        '<line x1="-22" y1="-2" x2="-12" y2="-2" stroke="#3a1410" stroke-width="1" opacity="0.6"/>'
        '<line x1="22" y1="-2" x2="12" y2="-2" stroke="#3a1410" stroke-width="1" opacity="0.6"/>'
        '<line x1="-18" y1="6" x2="-8" y2="6" stroke="#3a1410" stroke-width="1" opacity="0.6"/>'
        '<line x1="18" y1="6" x2="8" y2="6" stroke="#3a1410" stroke-width="1" opacity="0.6"/>'
    )
    return _wrap(x, y, scale, body, visibility)


def cave(x, y, scale=1.0, visibility='known', **kw):
    """Cave — natural opening in rock."""
    body = (
        '<polygon points="-24,16 -20,-4 -10,-14 8,-12 18,-2 22,16" fill="#8a8278" stroke="#3a1410" stroke-width="2"/>'
        '<path d="M -10 16 Q -10 -2 -2 -6 Q 8 -4 10 16 Z" fill="#1a0e05"/>'
    )
    return _wrap(x, y, scale, body, visibility)


def lair(x, y, scale=1.0, visibility='known', **kw):
    """Lair — cave mouth with ominous markings."""
    body = (
        '<polygon points="-24,16 -20,-4 -10,-14 8,-12 18,-2 22,16" fill="#5a4a3a" stroke="#3a1410" stroke-width="2"/>'
        '<path d="M -10 16 Q -10 -2 -2 -6 Q 8 -4 10 16 Z" fill="#1a0e05"/>'
        # Bones at entrance
        '<line x1="-6" y1="14" x2="-2" y2="10" stroke="#e8e0d0" stroke-width="1.5"/>'
        '<line x1="2" y1="14" x2="6" y2="10" stroke="#e8e0d0" stroke-width="1.5"/>'
        '<circle cx="-2" cy="10" r="1.5" fill="#e8e0d0"/>'
        '<circle cx="6" cy="10" r="1.5" fill="#e8e0d0"/>'
    )
    return _wrap(x, y, scale, body, visibility)


def camp(x, y, scale=1.0, visibility='known', **kw):
    """Camp — tent with a small fire."""
    body = (
        # Tent
        '<polygon points="-22,12 0,-18 22,12" fill="#a89878" stroke="#3a1410" stroke-width="2"/>'
        '<line x1="0" y1="-18" x2="0" y2="12" stroke="#3a1410" stroke-width="1.5"/>'
        # Fire
        '<polygon points="-10,16 -6,8 -2,14 0,4 2,14 6,8 10,16" fill="#d8702a" stroke="#3a1410" stroke-width="1"/>'
    )
    return _wrap(x, y, scale, body, visibility)


def bandit_camp(x, y, scale=1.0, visibility='known', **kw):
    """Bandit camp — tent with crossed swords."""
    body = (
        # Tent
        '<polygon points="-20,14 0,-12 20,14" fill="#5a4a3a" stroke="#3a1410" stroke-width="2"/>'
        '<line x1="0" y1="-12" x2="0" y2="14" stroke="#3a1410" stroke-width="1.5"/>'
        # Crossed swords above
        '<line x1="-10" y1="-22" x2="10" y2="-2" stroke="#a89888" stroke-width="2"/>'
        '<line x1="10" y1="-22" x2="-10" y2="-2" stroke="#a89888" stroke-width="2"/>'
        '<line x1="-12" y1="-24" x2="-8" y2="-20" stroke="#3a1410" stroke-width="2"/>'
        '<line x1="8" y1="-24" x2="12" y2="-20" stroke="#3a1410" stroke-width="2"/>'
    )
    return _wrap(x, y, scale, body, visibility)


def ambush_site(x, y, scale=1.0, visibility='known', **kw):
    """Ambush site — crossed arrows pointing inward."""
    body = (
        # Arrows
        '<line x1="-22" y1="0" x2="-4" y2="0" stroke="#3a1410" stroke-width="2"/>'
        '<polygon points="-4,-3 4,0 -4,3" fill="#3a1410"/>'
        '<polygon points="-22,-3 -18,0 -22,3" fill="#a89888"/>'
        '<line x1="22" y1="0" x2="4" y2="0" stroke="#3a1410" stroke-width="2"/>'
        '<polygon points="4,-3 -4,0 4,3" fill="#3a1410"/>'
        '<polygon points="22,-3 18,0 22,3" fill="#a89888"/>'
        # Trees suggesting cover
        '<polygon points="-26,14 -22,-2 -18,14" fill="#3a5a30" stroke="#3a1410" stroke-width="1"/>'
        '<polygon points="18,14 22,-2 26,14" fill="#3a5a30" stroke="#3a1410" stroke-width="1"/>'
    )
    return _wrap(x, y, scale, body, visibility)


def battlefield(x, y, scale=1.0, visibility='known', **kw):
    """Battlefield — broken weapons on the ground."""
    body = (
        # Ground
        '<ellipse cx="0" cy="12" rx="26" ry="6" fill="#7a6a5a" stroke="#3a1410" stroke-width="1.5"/>'
        # Broken sword
        '<line x1="-18" y1="6" x2="-4" y2="14" stroke="#a89888" stroke-width="2"/>'
        '<line x1="-20" y1="4" x2="-16" y2="8" stroke="#3a1410" stroke-width="2"/>'
        # Broken spear
        '<line x1="6" y1="14" x2="22" y2="0" stroke="#3a1410" stroke-width="1.5"/>'
        '<polygon points="22,0 24,-2 26,2 22,4" fill="#a89888" stroke="#3a1410" stroke-width="1"/>'
        # Helmet
        '<path d="M -8 12 Q -8 4 0 4 Q 8 4 8 12 Z" fill="#888080" stroke="#3a1410" stroke-width="1.5"/>'
    )
    return _wrap(x, y, scale, body, visibility)


# =============================================================================
# NATURAL LANDMARKS
# =============================================================================

def waterfall(x, y, scale=1.0, visibility='known', **kw):
    """Waterfall — cascading water with rocks."""
    body = (
        # Cliff face
        '<polygon points="-22,16 -18,-18 -10,-22 -6,-12 -2,-16 22,-16 22,16" fill="#888080" stroke="#3a1410" stroke-width="2"/>'
        # Water falling
        '<rect x="-2" y="-12" width="14" height="28" fill="#7fa9c4" opacity="0.7"/>'
        '<line x1="0" y1="-12" x2="0" y2="14" stroke="#fff" stroke-width="1" opacity="0.7"/>'
        '<line x1="4" y1="-12" x2="4" y2="14" stroke="#fff" stroke-width="1" opacity="0.7"/>'
        '<line x1="8" y1="-12" x2="8" y2="14" stroke="#fff" stroke-width="1" opacity="0.7"/>'
        # Pool foam
        '<ellipse cx="5" cy="16" rx="10" ry="3" fill="#fff" opacity="0.6"/>'
    )
    return _wrap(x, y, scale, body, visibility)


def hot_spring(x, y, scale=1.0, visibility='known', **kw):
    """Hot spring — pool with rising steam wisps."""
    body = (
        # Pool
        '<ellipse cx="0" cy="10" rx="20" ry="8" fill="#9ac0d8" stroke="#3a1410" stroke-width="1.5"/>'
        '<ellipse cx="0" cy="10" rx="14" ry="5" fill="#7fa9c4" opacity="0.8"/>'
        # Steam wisps
        '<path d="M -10 -2 q 2 -4 0 -8 q 2 -4 0 -8" fill="none" stroke="#cccccc" stroke-width="1.5" opacity="0.7"/>'
        '<path d="M 0 -4 q 2 -4 0 -8 q 2 -4 0 -8" fill="none" stroke="#cccccc" stroke-width="1.5" opacity="0.7"/>'
        '<path d="M 10 -2 q 2 -4 0 -8 q 2 -4 0 -8" fill="none" stroke="#cccccc" stroke-width="1.5" opacity="0.7"/>'
    )
    return _wrap(x, y, scale, body, visibility)


def oasis(x, y, scale=1.0, visibility='known', **kw):
    """Oasis — palm trees around water."""
    body = (
        # Pool
        '<ellipse cx="0" cy="14" rx="14" ry="5" fill="#9ac0d8" stroke="#3a1410" stroke-width="1.5"/>'
        # Left palm
        '<line x1="-12" y1="14" x2="-14" y2="-10" stroke="#5a3a1f" stroke-width="2"/>'
        '<path d="M -14 -10 q -8 -2 -14 4" fill="none" stroke="#3a5a30" stroke-width="2"/>'
        '<path d="M -14 -10 q -2 -8 4 -14" fill="none" stroke="#3a5a30" stroke-width="2"/>'
        '<path d="M -14 -10 q 6 -4 12 0" fill="none" stroke="#3a5a30" stroke-width="2"/>'
        # Right palm
        '<line x1="12" y1="14" x2="14" y2="-10" stroke="#5a3a1f" stroke-width="2"/>'
        '<path d="M 14 -10 q 8 -2 14 4" fill="none" stroke="#3a5a30" stroke-width="2"/>'
        '<path d="M 14 -10 q 2 -8 -4 -14" fill="none" stroke="#3a5a30" stroke-width="2"/>'
        '<path d="M 14 -10 q -6 -4 -12 0" fill="none" stroke="#3a5a30" stroke-width="2"/>'
    )
    return _wrap(x, y, scale, body, visibility)


def grove(x, y, scale=1.0, visibility='known', **kw):
    """Grove — small cluster of trees."""
    body = (
        '<circle cx="-10" cy="2" r="9" fill="#5a8a3a" stroke="#3a1410" stroke-width="1.5"/>'
        '<line x1="-10" y1="11" x2="-10" y2="16" stroke="#5a3a1f" stroke-width="2"/>'
        '<circle cx="6" cy="-2" r="11" fill="#5a8a3a" stroke="#3a1410" stroke-width="1.5"/>'
        '<line x1="6" y1="9" x2="6" y2="16" stroke="#5a3a1f" stroke-width="2"/>'
        '<circle cx="14" cy="6" r="7" fill="#5a8a3a" stroke="#3a1410" stroke-width="1.5"/>'
        '<line x1="14" y1="13" x2="14" y2="16" stroke="#5a3a1f" stroke-width="2"/>'
    )
    return _wrap(x, y, scale, body, visibility)


def ancient_tree(x, y, scale=1.0, visibility='known', **kw):
    """Ancient tree — huge gnarled trunk and broad canopy."""
    body = (
        # Canopy
        '<circle cx="0" cy="-10" r="22" fill="#3a6a2a" stroke="#3a1410" stroke-width="2"/>'
        '<circle cx="-10" cy="-4" r="10" fill="#3a6a2a" stroke="#3a1410" stroke-width="1"/>'
        '<circle cx="10" cy="-4" r="10" fill="#3a6a2a" stroke="#3a1410" stroke-width="1"/>'
        # Gnarled trunk
        '<path d="M -8 16 Q -8 6 -4 0 Q -2 -2 0 -2 Q 2 -2 4 0 Q 8 6 8 16 Z" fill="#5a3a1f" stroke="#3a1410" stroke-width="2"/>'
        # Roots
        '<line x1="-8" y1="16" x2="-14" y2="18" stroke="#5a3a1f" stroke-width="2.5"/>'
        '<line x1="8" y1="16" x2="14" y2="18" stroke="#5a3a1f" stroke-width="2.5"/>'
    )
    return _wrap(x, y, scale, body, visibility)


def peak(x, y, scale=1.0, visibility='known', **kw):
    """Peak — sharp prominent mountain top."""
    body = (
        '<polygon points="-22,16 0,-22 22,16" fill="#888080" stroke="#3a1410" stroke-width="2.5"/>'
        # Snow cap
        '<polygon points="-8,-6 0,-22 8,-6 4,-4 0,-6 -4,-4" fill="#f4faff" stroke="#3a1410" stroke-width="1"/>'
    )
    return _wrap(x, y, scale, body, visibility)


def cliff(x, y, scale=1.0, visibility='known', **kw):
    """Cliff — sheer vertical face with a flat top."""
    body = (
        '<polygon points="-24,16 -22,-12 -8,-12 -6,-18 22,-18 22,16" fill="#a89888" stroke="#3a1410" stroke-width="2"/>'
        # Vertical strata
        '<line x1="-14" y1="-10" x2="-14" y2="14" stroke="#3a1410" stroke-width="0.8" opacity="0.6"/>'
        '<line x1="-2" y1="-16" x2="-2" y2="14" stroke="#3a1410" stroke-width="0.8" opacity="0.6"/>'
        '<line x1="10" y1="-16" x2="10" y2="14" stroke="#3a1410" stroke-width="0.8" opacity="0.6"/>'
    )
    return _wrap(x, y, scale, body, visibility)


# =============================================================================
# GENERIC FALLBACK
# =============================================================================

def landmark(x, y, scale=1.0, visibility='known', **kw):
    """Generic landmark — simple flag/banner."""
    body = (
        '<line x1="0" y1="16" x2="0" y2="-22" stroke="#3a1410" stroke-width="2.5"/>'
        '<polygon points="0,-22 18,-18 0,-12" fill="#a04a2e" stroke="#3a1410" stroke-width="1.5"/>'
        # Base
        '<ellipse cx="0" cy="16" rx="6" ry="2" fill="#5a4a3a" stroke="#3a1410" stroke-width="1"/>'
    )
    return _wrap(x, y, scale, body, visibility)


# =============================================================================
# REGISTRY
# =============================================================================

ICONS = {
    # Settlements
    'capital': capital,
    'city': city,
    'town': town,
    'village': village,
    'hamlet': hamlet,
    'manor': manor,
    'hold': hold,
    # Defensive
    'fort': fort,
    'watchtower': watchtower,
    'keep': keep,
    'ruined_keep': ruined_keep,
    'palisade': palisade,
    # Infrastructure
    'tollbooth': tollbooth,
    'bridge': bridge,
    'ford': ford,
    'ferry': ferry,
    'mill': mill,
    'lighthouse': lighthouse,
    'well': well,
    'waystation': waystation,
    # Religious / Cultural
    'shrine': shrine,
    'temple': temple,
    'monastery': monastery,
    'cemetery': cemetery,
    'gibbet': gibbet,
    'monument': monument,
    'standing_stones': standing_stones,
    # Resources
    'mine': mine,
    'quarry': quarry,
    'lumber_camp': lumber_camp,
    'fishing_camp': fishing_camp,
    'salt_works': salt_works,
    # Wilderness / Adventure
    'ruin': ruin,
    'dungeon': dungeon,
    'cave': cave,
    'lair': lair,
    'camp': camp,
    'bandit_camp': bandit_camp,
    'ambush_site': ambush_site,
    'battlefield': battlefield,
    # Natural Landmarks
    'waterfall': waterfall,
    'hot_spring': hot_spring,
    'oasis': oasis,
    'grove': grove,
    'ancient_tree': ancient_tree,
    'peak': peak,
    'cliff': cliff,
    # Generic
    'landmark': landmark,
}


def list_types() -> dict:
    """Return categorised type list. Used by the atlas generator."""
    return {
        'Settlements': ['capital', 'city', 'town', 'village', 'hamlet', 'manor', 'hold'],
        'Defensive': ['fort', 'watchtower', 'keep', 'ruined_keep', 'palisade'],
        'Infrastructure': ['tollbooth', 'bridge', 'ford', 'ferry', 'mill', 'lighthouse', 'well', 'waystation'],
        'Religious / Cultural': ['shrine', 'temple', 'monastery', 'cemetery', 'gibbet', 'monument', 'standing_stones'],
        'Resources': ['mine', 'quarry', 'lumber_camp', 'fishing_camp', 'salt_works'],
        'Wilderness / Adventure': ['ruin', 'dungeon', 'cave', 'lair', 'camp', 'bandit_camp', 'ambush_site', 'battlefield'],
        'Natural Landmarks': ['waterfall', 'hot_spring', 'oasis', 'grove', 'ancient_tree', 'peak', 'cliff'],
        'Generic': ['landmark'],
    }
