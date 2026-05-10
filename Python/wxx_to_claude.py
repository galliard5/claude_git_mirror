"""
wxx_to_claude.py — Convert a Worldographer .wxx into a compact text format
designed for an LLM to read and reason about — not for visual display.

The goal is to give Claude (or any LLM) enough structured information to answer
spatial questions about the map ("what hex is Silberbach in," "which roads
connect Westgate to anything," "trace the river") in as few tokens as possible.

What we keep:
  - Map metadata (size, orientation, type)
  - Per-cell terrain ID (compressed run-length encoded)
  - Settlement / feature list with hex coordinates and types
  - Road / river network as cell sequences (NOT as Bezier control points)
  - Polar/arctic overlay cells

What we drop:
  - Every visual decoration (trees, mountain peaks, vignette, etc.)
  - SVG path control-point precision
  - Texture references, colours, stroke widths
  - The hex polygon geometry itself (Claude can re-derive from col/row)

Output is a Markdown document with structured sections. Token cost typically
drops by 100x-200x vs the rendered SVG.
"""
from __future__ import annotations
import sys, math
from collections import defaultdict
from pathlib import Path

# Reuse the parser from wxx_to_svg
from wxx_to_svg import (
    load_wxx, parse_wxx, WxxMap,
    hex_geometry_for, square_center, HEX_W, HEX_H,
)


# =============================================================================
# Coordinate inversion — given world (x, y), find which (col, row) it sits in
# =============================================================================

def world_to_hex(wx: float, wy: float, orientation: str) -> tuple[int, int]:
    """Inverse of hex_center for the given orientation. Returns nearest cell."""
    if orientation == 'ROWS':
        # Pointy-top: col_stride=300, row_stride=225, odd rows shift right by 150
        row = round((wy - 150) / 225)
        if row % 2 == 1:
            col = round((wx - 300) / 300)
        else:
            col = round((wx - 150) / 300)
    else:
        # COLUMNS (flat-top): col_stride=225, row_stride=300, odd cols shift down by 150
        col = round((wx - 150) / 225)
        if col % 2 == 0:
            row = round((wy - 150) / 300)
        else:
            row = round((wy - 300) / 300)
    return col, row


def world_to_square(wx: float, wy: float, tile_size: float = 300.0) -> tuple[int, int]:
    return int(wx // tile_size), int(wy // tile_size)


# =============================================================================
# Terrain glyph mapping — short, mnemonic single-character codes
# =============================================================================
# Aim: each terrain category collapses to one ASCII char. Renderer-friendly
# fidelity isn't important here; we just need Claude to be able to scan the
# grid and recognize "what kind of cell is this."

DEFAULT_GLYPHS = {
    # Water
    'Water Ocean': '~', 'Water Sea': '~', 'Water Shallow': '~',
    'Water River': '~', 'Water Lake': '~', 'Water Wetlands': '%',
    # Mountains
    'Mountains': '^', 'Mountain': '^',
    'Mountains Forest Evergreen': 'M', 'Mountain Forest Evergreen': 'M',
    'Mountains Forest Deciduous': 'M', 'Mountains Forest Mixed': 'M',
    'Mountains Forest Jungle': 'J',
    # Hills
    'Hills': 'h', 'Hills Grassland': 'h', 'Hills Shrubland': 'h',
    'Hills Forest Evergreen': 'H', 'Hills Forest Deciduous': 'H',
    'Hills Forest Mixed': 'H', 'Hills Forest Jungle': 'j',
    # Forests (flat)
    'Flat Forest Evergreen': 'f', 'Flat Forest Evergreen Heavy': 'F',
    'Flat Forest Deciduous': 'f', 'Flat Forest Mixed': 'f',
    'Flat Forest Jungle': 'g', 'Flat Forest Wetlands': '%',
    # Open / farmland / grassland
    'Flat Farmland': '.', 'Flat Farmland Cultivated': '.',
    'Flat Farmland Varied': '.', 'Flat Grassland': ',',
    'Flat Shrubland': ',', 'Flat Plain': ',',
    # Desert
    'Flat Desert Rocky': 'd', 'Flat Desert Dunes': 'd',
    # Special
    'Underdark Open': 'r',  # repurposed: rural neighbourhood
    'Blank': ' ',
}
DEFAULT_GLYPH = '?'


def glyph_for_terrain(name: str) -> str:
    """Pick a single char to represent a terrain. Strip 'Classic/' prefix."""
    if not name:
        return DEFAULT_GLYPH
    bare = name.split('/', 1)[-1]
    return DEFAULT_GLYPHS.get(bare, DEFAULT_GLYPH)


# =============================================================================
# Path → cell-sequence compression
# =============================================================================
# A road or river in the source is dozens of Bezier control points. For Claude
# to answer "which cells does this road pass through," we just need the ordered
# list of unique cells the path crosses. We sample along each segment densely,
# convert each sample to (col, row), and dedupe consecutive duplicates.

def sample_path_cells(points: list, orientation: str, samples_per_segment: int = 10) -> list:
    """Walk a path's points and return [(col, row), ...] of cells touched."""
    if not points:
        return []
    cells = []
    last_cell = None
    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]
        for t in range(samples_per_segment + 1):
            s = t / samples_per_segment
            wx = x1 + (x2 - x1) * s
            wy = y1 + (y2 - y1) * s
            cell = world_to_hex(wx, wy, orientation) if orientation != 'SQUARE' else world_to_square(wx, wy)
            if cell != last_cell:
                cells.append(cell)
                last_cell = cell
    return cells


# =============================================================================
# Document builder
# =============================================================================

def build_claude_doc_from_map(wmap: WxxMap, source_label: str = '') -> str:
    """Produce a compact Markdown representation from an already-parsed map."""
    is_square = wmap.hex_orientation == 'SQUARE'
    orientation = wmap.hex_orientation
    cols, rows = wmap.tiles_wide, wmap.tiles_high

    out = []
    title = source_label or 'map'
    # Strip extension if present
    if title.lower().endswith('.wxx'):
        title = title[:-4]
    out.append(f"# Map: {title}")
    out.append("")
    out.append(f"- **Type:** {wmap.map_type}")
    out.append(f"- **Orientation:** {orientation} "
               + ("(pointy-top hex; odd rows shift right)" if orientation == 'ROWS'
                  else "(flat-top hex; odd cols shift down)" if orientation == 'COLUMNS'
                  else "(square grid)"))
    out.append(f"- **Size:** {cols} cols × {rows} rows ({cols * rows} cells)")
    out.append("")

    # ── Terrain legend ─────────────────────────────────────
    used_terrains = set()
    for col in wmap.grid:
        for tid in col:
            used_terrains.add(tid)
    out.append("## Terrain legend")
    out.append("")
    out.append("Single-char glyphs used in the grid below:")
    out.append("")
    out.append("| Glyph | Terrain |")
    out.append("|-------|---------|")
    glyph_to_name = {}
    for tid in sorted(used_terrains):
        name = wmap.terrain.get(tid, f'unknown:{tid}')
        glyph = glyph_for_terrain(name)
        glyph_to_name.setdefault(glyph, name)
        out.append(f"| `{glyph}` | {name} (id {tid}) |")
    out.append("")

    # ── Grid ───────────────────────────────────────────────
    out.append("## Grid")
    out.append("")
    if orientation == 'ROWS':
        out.append("Each row is one hex-row; odd rows are visually shifted right by half a hex.")
    elif orientation == 'COLUMNS':
        out.append("Each row is one hex-row; columns are vertical, odd columns shifted down by half a hex (this is hard to depict in plain text — use the cell coordinates rather than visual position).")
    out.append("")
    out.append("```")
    if cols <= 100:
        out.append("    " + "".join(str(c // 10) if c % 10 == 0 else " " for c in range(cols)))
        out.append("    " + "".join(str(c % 10) for c in range(cols)))
    for r in range(rows):
        line = []
        for c in range(cols):
            if c < len(wmap.grid) and r < len(wmap.grid[c]):
                tid = wmap.grid[c][r]
                name = wmap.terrain.get(tid, '')
                ch = glyph_for_terrain(name)
                if (c < len(wmap.polar) and r < len(wmap.polar[c])
                        and wmap.polar[c][r]):
                    ch = '*' if ch in (' ', '~', '.', ',') else ch.upper()
                line.append(ch)
            else:
                line.append(' ')
        prefix = "  " if (orientation == 'ROWS' and r % 2 == 1) else ""
        out.append(f"{r:3d} {prefix}{''.join(line)}")
    out.append("```")
    out.append("")
    out.append("Polar/arctic overlay tiles are shown uppercase or with `*` for ocean/farmland.")
    out.append("")

    # ── Features ───────────────────────────────────────────
    real_features = [f for f in wmap.features if 'Coast' not in f.type]
    out.append(f"## Features ({len(real_features)})")
    out.append("")
    if real_features:
        out.append("| Cell | Type | Label |")
        out.append("|------|------|-------|")
        for f in sorted(real_features, key=lambda f: (f.y, f.x)):
            if is_square:
                cell = world_to_square(f.x, f.y)
            else:
                cell = world_to_hex(f.x, f.y, orientation)
            short = f.type.split('/', 1)[-1] if '/' in f.type else f.type
            label = f.label or '(unlabeled)'
            out.append(f"| ({cell[0]},{cell[1]}) | {short} | {label} |")
        out.append("")

    # ── Shapes (roads, rivers, walls) ─────────────────────
    shapes_by_tag = defaultdict(list)
    for s in wmap.shapes:
        shapes_by_tag[s.tag or '(untagged)'].append(s)

    if shapes_by_tag:
        out.append(f"## Linear features ({len(wmap.shapes)} total)")
        out.append("")
        for tag, slist in sorted(shapes_by_tag.items()):
            out.append(f"### {tag} ({len(slist)})")
            out.append("")
            for i, s in enumerate(slist):
                cells = sample_path_cells(s.points, orientation if not is_square else 'SQUARE')
                if not cells:
                    continue
                deduped = [cells[0]]
                for c in cells[1:]:
                    if c != deduped[-1]:
                        deduped.append(c)
                cell_list = " → ".join(f"({c},{r})" for c, r in deduped)
                out.append(f"- **{tag} {i + 1}** ({len(deduped)} cells): {cell_list}")
            out.append("")

    # ── Adjacency / network summary ───────────────────────
    if not is_square and real_features and shapes_by_tag:
        out.append("## Settlement connectivity")
        out.append("")
        out.append("Which roads/rivers pass through the same cell as each labelled feature.")
        out.append("")
        cell_owners = defaultdict(list)
        for tag, slist in shapes_by_tag.items():
            for i, s in enumerate(slist):
                for c in sample_path_cells(s.points, orientation):
                    cell_owners[c].append((tag, i + 1))
        out.append("| Settlement | Cell | Touched by |")
        out.append("|------------|------|------------|")
        for f in sorted(real_features, key=lambda f: f.label or ''):
            if not f.label:
                continue
            cell = world_to_hex(f.x, f.y, orientation)
            owners = list(cell_owners.get(cell, []))
            for dc, dr in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]:
                owners.extend(cell_owners.get((cell[0] + dc, cell[1] + dr), []))
            unique = sorted(set(owners))
            owner_str = ", ".join(f"{t}#{i}" for t, i in unique) or "(none)"
            out.append(f"| {f.label} | ({cell[0]},{cell[1]}) | {owner_str} |")
        out.append("")

    return '\n'.join(out)


def build_claude_doc(wxx_path: str) -> str:
    """Convenience wrapper: load + parse + describe in one call."""
    xml = load_wxx(wxx_path)
    wmap = parse_wxx(xml)
    return build_claude_doc_from_map(wmap, source_label=Path(wxx_path).name)


def main():
    if len(sys.argv) < 3:
        print("Usage: wxx_to_claude.py <input.wxx> <output.md>")
        sys.exit(1)
    inp, out = sys.argv[1], sys.argv[2]
    doc = build_claude_doc(inp)
    Path(out).write_text(doc, encoding='utf-8')
    size = len(doc)
    # Rough token estimate
    approx_tokens = size // 3.5
    print(f"Wrote {out}: {size:,} chars (~{approx_tokens:,.0f} tokens)")


if __name__ == '__main__':
    main()
