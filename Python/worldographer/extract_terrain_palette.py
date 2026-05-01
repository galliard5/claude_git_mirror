"""
extract_terrain_palette.py — Convert worldographer_terrain.properties → Python.

Reads the terrain definitions extracted from Worldographer's .jar and produces
a Python source file containing the full authoritative palette (~1700 entries
across all namespaces: Classic, Battlemat, Cosmic, Isometric, etc.).

Schema of each line in the .properties file:
    Namespace/Name=texture_path \t scale \t r,g,b,a \t weight \t [marker] \t [blend_neighbours]

Where:
    name              — terrain identifier (matches what's in <terrainmap> in .wxx files)
    texture_path      — relative path to texture PNG (or 'x' for solid-colour-only)
    scale             — texture render scale (typically .75)
    r,g,b,a           — fill colour as floats 0-1; this is what we want for SVG
    weight            — terrain "weight" (used by Worldographer for blend priority)
    marker            — typically 'x'; meaning unclear
    blend_neighbours  — semicolon-separated list of terrain names that this terrain
                        will visually blend with at hex borders

Output is a single dict mapping the full terrain name (e.g. "Classic/Mountains Forest
Evergreen") to a 7-character hex string (e.g. "#667321").
"""
import re
import sys
from pathlib import Path


def parse_rgba_to_hex(rgba_str: str) -> str | None:
    """Convert 'r,g,b,a' floats to '#rrggbb'. Returns None on failure."""
    try:
        nums = [float(x.strip()) for x in rgba_str.split(',')]
        r = max(0, min(255, int(round(nums[0] * 255))))
        g = max(0, min(255, int(round(nums[1] * 255))))
        b = max(0, min(255, int(round(nums[2] * 255))))
        return f'#{r:02x}{g:02x}{b:02x}'
    except (ValueError, IndexError):
        return None


def parse_terrain_properties(path: str) -> tuple[dict, dict]:
    """Parse a terrain.properties file. Returns (terrains, features).

    Terrains are entries with a colour field — used to fill hex/square cells.
    Features are entries that are just path+scale — used as placeable icons.
    """
    text = Path(path).read_text(encoding='utf-8')
    terrains = {}
    features = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        name = key.replace(r'\ ', ' ').strip()
        if not name or name.startswith('#'):
            continue
        fields = value.split('\t')
        # Heuristic: if field 2 looks like an RGBA tuple, it's a terrain;
        # otherwise it's a feature/icon.
        if len(fields) >= 3 and ',' in fields[2]:
            color = parse_rgba_to_hex(fields[2])
            if color is not None:
                texture = fields[0] if fields[0] != 'x' else None
                weight = fields[3] if len(fields) > 3 else None
                blend_with = []
                if len(fields) > 5 and fields[5]:
                    blend_with = [s.strip() for s in fields[5].split(';') if s.strip()]
                terrains[name] = {
                    'color': color,
                    'texture': texture,
                    'rgba_raw': fields[2],
                    'weight': weight,
                    'blend_with': blend_with,
                }
                continue
        # Otherwise treat as a feature/icon definition (just path + maybe scale)
        if fields and fields[0] and fields[0] != 'x':
            features[name] = {
                'texture': fields[0],
                'scale': fields[1] if len(fields) > 1 else None,
            }
    return terrains, features


def write_palette_module(terrains: dict, features: dict, output_path: str):
    """Write a Python module with both the terrain palette and feature catalog."""
    lines = [
        '"""',
        'Worldographer authoritative terrain palette and feature catalog.',
        '',
        'Auto-generated from worldographer_terrain.properties (extracted from the',
        "Worldographer .jar). Read by wxx_to_svg.py to colour terrain cells and",
        'identify placeable feature icons.',
        '',
        f'Contents:',
        f'  - {len(terrains)} terrain entries with fill colours (Classic, Cosmic, ISO, Floor, Full Classic).',
        f'  - {len(features)} feature/icon definitions (Battlemat, Structure, Token, etc.) —',
        "    the texture path is provided but cannot be reproduced outside Worldographer.",
        '',
        'Use:',
        '    from worldographer_palette import TERRAIN_COLORS, FEATURE_ICONS',
        '    color = TERRAIN_COLORS.get("Classic/Mountains Forest Evergreen", "#cccccc")',
        '    icon  = FEATURE_ICONS.get("Battlemat/Door Wood")  # → {"texture": ..., "scale": ...}',
        '"""',
        '',
    ]

    # ─── Terrains ────────────────────────────────────────────
    lines.append('# Map from terrain name → "#rrggbb" hex colour.')
    lines.append('# Names match what appears in <terrainmap> elements of .wxx files.')
    lines.append('TERRAIN_COLORS = {')
    by_ns = {}
    for name in sorted(terrains):
        ns = name.split('/', 1)[0] if '/' in name else '(other)'
        by_ns.setdefault(ns, []).append(name)
    for ns in sorted(by_ns):
        lines.append(f'    # ─── {ns} ({len(by_ns[ns])} entries) ───')
        for name in by_ns[ns]:
            color = terrains[name]['color']
            lines.append(f'    {name!r}: {color!r},')
        lines.append('')
    lines.append('}')
    lines.append('')

    # ─── Features ────────────────────────────────────────────
    lines.append('# Map from feature/icon name → {"texture": str, "scale": str|None}')
    lines.append('# Use to identify the type of a <feature> element in a .wxx file.')
    lines.append('FEATURE_ICONS = {')
    by_ns = {}
    for name in sorted(features):
        ns = name.split('/', 1)[0] if '/' in name else '(other)'
        by_ns.setdefault(ns, []).append(name)
    for ns in sorted(by_ns):
        lines.append(f'    # ─── {ns} ({len(by_ns[ns])} entries) ───')
        for name in by_ns[ns]:
            entry = features[name]
            tex = entry['texture']
            scale = entry['scale']
            lines.append(f'    {name!r}: {{"texture": {tex!r}, "scale": {scale!r}}},')
        lines.append('')
    lines.append('}')
    lines.append('')

    Path(output_path).write_text('\n'.join(lines), encoding='utf-8')
    print(f'Wrote {output_path}: {len(terrains)} terrains, {len(features)} features')


def main():
    if len(sys.argv) < 3:
        print('Usage: extract_terrain_palette.py <input.properties> <output.py>')
        sys.exit(1)
    inp, out = sys.argv[1], sys.argv[2]
    terrains, features = parse_terrain_properties(inp)
    write_palette_module(terrains, features, out)

    # Print summary
    def summarise(d, label):
        by_ns = {}
        for name in d:
            ns = name.split('/', 1)[0] if '/' in name else '(other)'
            by_ns[ns] = by_ns.get(ns, 0) + 1
        print(f'\n{label}:')
        for ns, n in sorted(by_ns.items(), key=lambda x: -x[1]):
            print(f'  {ns:<25} {n:>4}')

    summarise(terrains, 'Terrains by namespace')
    summarise(features, 'Features by namespace')


if __name__ == '__main__':
    main()
