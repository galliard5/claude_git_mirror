---
name: Worldographer Wxx Parsing Reference
keywords: [worldographer, wxx, xml, hex grid, square grid, battlemap, map parsing, svg, reference]
description: Decoded specifics of the Worldographer .wxx format — both hex and square/battlemap variants — for building SVG renderers from project map files.
---

# Worldographer .wxx Parsing Reference

This document captures everything learned from parsing both hex (kingdom-scale) and square (battlemat-scale) maps. Read this **first** the next time a `.wxx` file shows up — these gotchas will be present in any other Worldographer export, and rediscovering them takes a session.

The companion script `wxx_to_svg.py` (in `Python/`) is a working renderer that handles both map types. Use it as a starting point and extend its styling for project-specific looks.

---

## 1. File format basics

A `.wxx` file is **gzip-compressed UTF-16 big-endian XML**.

```python
import gzip
with gzip.open('map.wxx', 'rb') as f:
    xml = f.read().decode('utf-16-be')
```

The decompressed file is `~600 KB` for a 50×50 hex map and `~60 KB` for a 25×19 square map. Regex parsing is fine — the XML isn't deeply nested.

---

## 2. Map type and orientation — the FIRST thing to check

Two attributes on the `<map>` root determine which rendering path to use:

```xml
<map type="WORLD"     hexOrientation="COLUMNS" ...>   <!-- flat-top hex -->
<map type="WORLD"     hexOrientation="ROWS"    ...>   <!-- pointy-top hex -->
<map type="BATTLEMAT" hexOrientation="SQUARE"  ...>   <!-- square / battlemap -->
```

Worldographer offers **four fundamental map types** in its New Map dialog. As far as decoding goes, they collapse into two structural categories — hex (any orientation) and square — but the `type` attribute and likely feature library will differ:

| User-facing name        | `type` attribute (observed/expected) | Grid kind | Notes |
|-------------------------|--------------------------------------|-----------|-------|
| World/Kingdom           | `WORLD`                              | hex       | Classic terrain library |
| Town/City/Village       | likely `TOWN` or similar             | hex       | Smaller scale, urban features (no sample yet) |
| Sector/Cosmic           | likely `COSMIC` or similar           | hex       | Starmap visuals (no sample yet) |
| Battlemat/Dungeon       | `BATTLEMAT`                          | square    | Battlemat feature library, terrain via shapes |

`hexOrientation` is the cleaner discriminator for rendering:

| Value     | Meaning                  | Geometry                                      |
|-----------|--------------------------|-----------------------------------------------|
| `COLUMNS` | flat-top hex             | columns line up vertically; odd cols offset DOWN |
| `ROWS`    | pointy-top hex           | rows line up horizontally; odd rows offset RIGHT |
| `SQUARE`  | square grid (battlemap)  | regular Cartesian grid, no offsets            |

`hexWidth` and `hexHeight` on the `<map>` element are screen render sizes in pixels and don't matter for parsing — world coordinates use a fixed 300-unit-per-tile system regardless (see §4).

---

## 3. Top-level XML structure

```
<map type="..." hexOrientation="..." ...>
  <gridandnumbering ... />
  <mapkey>...</mapkey>
  <terrainmap>name1 \t id1 \t name2 \t id2 ...</terrainmap>
  <maplayer name="..." isVisible="true" opacity="1.0"/>   ← multiple, in render order
  <maplayer name="..." .../>
  ...
  <tiles viewLevel="..." tilesWide="N" tilesHigh="M">
    <tilerow>...</tilerow>     ← one per COLUMN (column-major)
    ...
  </tiles>
  <features>
    <feature type="..." rotate="..." scale="..." ...>
      <location x="..." y="..."/>
      <label>...<location/>NAME</label>
    </feature>
    ...
  </features>
  <shapes>
    <shape tags="road|river|wall|floor|..." creationType="BASIC|CURVE"
           fillColor="r,g,b,a" fillTexture="..."
           strokeColor="r,g,b,a" strokeWidth="..."
           mapLayer="..." isCurve="true|false">
      <p type="m" x="..." y="..."/>
      <p type="c" x="..." y="..." cx1="..." cy1="..." cx2="..." cy2="..."/>
      <p x="..." y="..."/>
    </shape>
    ...
  </shapes>
  <labels>...</labels>
  <notes>
    <note>
      <notetext><html>...rich HTML descriptions...</html></notetext>
    </note>
  </notes>
  <configuration>
    <shape-config>
      <shapestyle name="..." strokeWidth="..." fillTexture="..." .../>
    </shape-config>
    <text-config>
      <labelstyle name="..." fontFace="..." .../>
    </text-config>
  </configuration>
</map>
```

---

## 4. Hex map specifics

### Hex coordinate system is STRETCHED, not geometric

This is the most important thing to get right. Worldographer's world coordinate system uses **300×300 world units per hex**, regardless of the visual aspect ratio of the rendered hex shape. The same 300-unit grid is used for both flat-top and pointy-top orientations — only the axis pairings change.

#### COLUMNS orientation (flat-top hex)

Columns line up vertically. Odd columns shift down by half a hex.

| Constant       | Value | Why |
|----------------|-------|-----|
| `HEX_W`        | 300   | Hex width (point to point, horizontal) |
| `HEX_H`        | 300   | Hex height in world units (NOT √3·size) |
| `COL_STRIDE`   | 225   | = 0.75 × HEX_W |
| `ROW_STRIDE`   | 300   | = HEX_H |
| `COL_OFFSET_Y` | 150   | Odd columns shift DOWN by half a hex |

```python
def hex_center_columns(col, row):
    cx = col * 225 + 150
    cy = row * 300 + 150
    if col % 2 == 1: cy += 150         # odd cols shifted down
    return cx, cy

def hex_polygon_columns(col, row):
    cx, cy = hex_center_columns(col, row)
    return [
        (cx - 150, cy),         # left point
        (cx -  75, cy - 150),   # upper-left
        (cx +  75, cy - 150),   # upper-right
        (cx + 150, cy),         # right point
        (cx +  75, cy + 150),   # lower-right
        (cx -  75, cy + 150),   # lower-left
    ]
```

#### ROWS orientation (pointy-top hex)

Rows line up horizontally. Odd rows shift right by half a hex. The strides are swapped versus COLUMNS:

| Constant       | Value | Why |
|----------------|-------|-----|
| `HEX_W`        | 300   | Hex width in world units |
| `HEX_H`        | 300   | Hex height (point to point, vertical) |
| `COL_STRIDE`   | 300   | = HEX_W |
| `ROW_STRIDE`   | 225   | = 0.75 × HEX_H |
| `ROW_OFFSET_X` | 150   | Odd rows shift RIGHT by half a hex |

```python
def hex_center_rows(col, row):
    cx = col * 300 + 150
    cy = row * 225 + 150
    if row % 2 == 1: cx += 150         # odd rows shifted right
    return cx, cy

def hex_polygon_rows(col, row):
    cx, cy = hex_center_rows(col, row)
    return [
        (cx,       cy - 150),   # top point
        (cx + 150, cy -  75),   # upper-right
        (cx + 150, cy +  75),   # lower-right
        (cx,       cy + 150),   # bottom point
        (cx - 150, cy +  75),   # lower-left
        (cx - 150, cy -  75),   # upper-left
    ]
```

Common failure mode: features land 3–4 cells off from where they should. That's usually the **`row_stride = 260` bug** (using geometric √3·size instead of the flat 300 for COLUMNS, or 225 for ROWS). The discrepancy compounds with cell index, so cells near the origin look fine while distant ones drift.

### Tilerow is column-major (both orientations)

`<tilerow>` elements are **always columns**, regardless of hex orientation. Counter-intuitively, even ROWS-oriented maps store data column-major: tilerow 0 contains all of column 0's cells, top to bottom. The first `<tilerow>` is column 0 of the grid; each tile entry is newline-separated within the tilerow text; each tile is tab-separated fields where field 0 is the terrain ID.

```python
tilerows = re.findall(r'<tilerow[^>]*>([^<]*)</tilerow>', xml)
GRID = []
for col_text in tilerows:
    col_hexes = col_text.strip().split('\n')
    GRID.append([int(h.split('\t')[0]) for h in col_hexes if h.strip()])
# Access: GRID[col][row] regardless of hex orientation
```

### Tile field count varies by tile

Some tiles have a **shorthand 6-field encoding** ending in `Z`, used for "default" tiles (typically water/empty terrain with no blend data):

```
0\t-3\t1\t0\t47\tZ          ← 6 fields: terrain_id=0, ?, polar=1, ?, ?, Z
```

Other tiles carry the full **11-field encoding** with terrain blending data:

```
9\t1000\t0\t0\t36\t9\t35\t0\t2\t2\t0    ← 11 fields
```

For renderers that only need the terrain ID, this doesn't matter — field 0 works either way. But if you need the blend data, check field count first.

### Tile field 2 is a polar/arctic overlay flag

Field 2 (the third tab-separated field) is a **boolean polar overlay flag**: `0` = normal, `1` = arctic/snow overlay. This flag is **independent of base terrain** and applies an ice/snow visual on top of whatever terrain ID the hex carries:

| Tile data | Result |
|-----------|--------|
| `0\t-3\t0\t0\t47\tZ` | Water Ocean — deep blue |
| `0\t-3\t1\t0\t47\tZ` | Water Ocean + polar — pale blue ice sheet |
| `1\t1000\t0\t...` | Farmland — green |
| `1\t1000\t1\t...` | Farmland + polar — frozen tundra (white wash) |

A simple way to render this is to draw the base terrain colour, then overlay a translucent white polygon (~85% opacity) on flagged hexes. The base shows through faintly enough to distinguish frozen ocean (pale blue) from frozen land (off-white).

```python
for col in range(cols):
    for row in range(rows):
        # field 0 = terrain id, field 2 = polar flag
        line = tile_lines[col][row]
        fields = line.split('\t')
        terrain_id = int(fields[0])
        polar = len(fields) > 2 and fields[2] == '1'
        # ... draw terrain hex, then if polar, overlay '#f4faff' at 0.85 opacity ...
```

The other 8+ tab-separated fields per tile are decoration data (terrain blend %, feature overlay IDs, etc.) — usually safe to ignore for basic rendering.

### Hex feature library

Hex maps use the `Classic/` icon library: `Classic Settlement Capital`, `Classic Settlement Village`, `Classic Building Cottage`, `Classic Military Fort`, `Classic Resource Mines`, `Classic Symbol Bridge`, `Classic Symbol Anchor`, plus decorative water-edge tiles like `Classic Coasts/1 Blue Water Edge A`.

Town and Cosmic map types likely use distinct libraries (e.g. `Town/...`, `Cosmic/...`) — not yet confirmed.

**Coast / water-edge features are decoration, not data.** Worldographer rotates a small library of edge tiles (rotate, scale, isFlipHorizontal/Vertical) to build seamless coastlines around water hexes. Don't render them as feature icons. The water hexes themselves are in the grid (terrain ID for "Water Sea" or "Water Ocean"); render the lake/sea by drawing a shape over those hexes.

### Tile-level decorations are part of the terrain texture

Looking at a Worldographer-rendered map, you'll see palm trees, mountain icons, grass tufts, sand patches, etc. drawn on individual hexes. These are **NOT separate features** — they're built into the terrain texture. The only data is the terrain ID in field 0. A simplified SVG renderer can ignore the per-hex decorations entirely and just colour the hex by its terrain.

---

## 5. Square / battlemat map specifics

### The tile grid is essentially unused

In a square map, **all tiles are identical "blank" entries**. The terrainmap typically only contains `Blank\t0`, and every tile in `<tilerow>` reads `0\t1\t0\t0\t0\tZ` (or similar uniform data). The terrain you see on screen comes from `<shape>` elements, not the grid.

```python
# In a square map: GRID[col][row] is always the same id (likely 0). Don't bother
# colouring the grid by terrain — just render the shapes over a default background.
```

### Each tile is still 300×300 world units

Even though Worldographer renders battlemap tiles at 75 screen pixels each by default, the **world coordinate system is the same 300 units per tile**. A 25×19 map spans `(0,0)` to `(7500, 5700)` in world coords. Square tile centres:

```python
def square_center(col, row, tile_size=300):
    return col * tile_size + tile_size/2, row * tile_size + tile_size/2
```

No column/row offset — square grids are regular.

### Terrain is in shapes, organised by `tags`

Square map shapes carry a `tags` attribute that drives their meaning:

| `tags` value | Meaning | Typical fill | Typical use |
|--------------|---------|--------------|-------------|
| `ground`     | Outdoor terrain region | `fillTexture` (e.g. "Forest Floor") | grass, sand, stone areas |
| `floor`      | Indoor floor region    | `fillColor` or `fillTexture`        | building interiors |
| `room`       | Same as floor functionally | `fillColor`                     | individual rooms |
| `wall`       | Wall outline / line segment | `strokeColor` only             | building walls, fences |
| (anything)   | User-tagged custom         | varies                           | project-specific |

`creationType` distinguishes:
- `BASIC` — straight-edged polygon or polyline
- `CURVE` — Bezier-curved path (splines)

`isCurve="true"` redundantly confirms a curve shape.

`fillColor` and `strokeColor` are RGBA float strings: `"0.678,0.847,0.902,1.0"` = light blue. Convert to hex like:

```python
def rgba_to_hex(s):
    if not s or s == 'null': return None
    nums = [float(x) for x in s.split(',')]
    return '#{:02x}{:02x}{:02x}'.format(
        *(max(0, min(255, int(round(n * 255)))) for n in nums[:3])
    )
```

`fillTexture` references named textures from Worldographer's library (e.g. "Forest Floor", "Stone Light 5x5", "Rock Dark"). A renderer outside Worldographer can't reproduce these — substitute a sensible solid colour by texture name, or fall back to the tag's default style.

### Layer order matters

The `<maplayer>` elements at the top of the file define render order. **They appear in TOP-DOWN drawing order** (first layer in file is topmost in render, drawn last). For SVG, reverse the list to get bottom-up render order, then sort shapes by their `mapLayer` attribute:

```python
layers = re.findall(r'<maplayer\s+name="([^"]+)"', xml)
layers = list(reversed(layers))   # now bottom-to-top
layer_index = {name: i for i, name in enumerate(layers)}
sorted_shapes = sorted(shapes, key=lambda s: layer_index.get(s.map_layer, len(layers)))
```

Typical battlemap layer stack (bottom → top):
1. Below All
2. Terrain Water
3. Above Water
4. Terrain Land
5. Above Terrain
6. Features
7. Grid
8. Labels

### Default backdrop

There's no shape covering "empty space" in a battlemap — the BATTLEMAT map type just shows a default light-blue backdrop where no shape paints. Render this explicitly as a base rectangle in your SVG (e.g. `#ADD8E6`) before drawing shapes.

### Square feature library

Square maps use the `Battlemat/` icon library: `Battlemat/Door Wood`, `Battlemat/Window No Light`, `Battlemat/Stairs Wood`, `Battlemat/Bed Weathered`, `Battlemat/Chair Weathered`, `Battlemat/Table Rectangle Weathered`, `Battlemat/Fireplace`, `Battlemat/Bookcase Weathered`, `Battlemat/Barrel Wood`, etc. These reference Worldographer texture art that can't be reproduced externally — render as labelled markers, simplified icons, or coloured circles.

---

## 6. CRITICAL: shape `<p>` elements have THREE forms

This was the parser bug that made road segments and polygon shapes break in different ways. Worldographer point elements appear in three flavours:

| Form | Meaning | Example |
|------|---------|---------|
| Move-to | Start of a sub-path | `<p type="m" x="100" y="100"/>` |
| Cubic Bezier | Curved segment with 2 control points | `<p type="c" x="200" y="100" cx1="..." cy1="..." cx2="..." cy2="..."/>` |
| **Implicit** | **No `type` attribute** | `<p x="200" y="100"/>` |

The implicit form means **line-to** for subsequent points, but **the FIRST point of any shape is always an implicit move-to regardless of declared type**. Many polygon shapes (especially square-map ground/floor/room shapes) have no `type="m"` first point at all — every `<p>` is typeless. Treat the first one as `M` and the rest as `L`.

```python
def parse_shape_path(shape_xml):
    raw = []
    for m in re.finditer(r'<p\b([^/]*)/>', shape_xml):
        attrs = m.group(1)
        type_m = re.search(r'\stype="([mc])"', attrs)
        x_m = re.search(r'\sx\s*=\s*"([^"]+)"', attrs)
        y_m = re.search(r'\sy\s*=\s*"([^"]+)"', attrs)
        if not (x_m and y_m): continue
        ptype = type_m.group(1) if type_m else None
        x, y = float(x_m.group(1)), float(y_m.group(1))
        cx1 = cy1 = cx2 = cy2 = None
        if ptype == 'c':
            cx1 = float(re.search(r'cx1="([^"]+)"', attrs).group(1))
            cy1 = float(re.search(r'cy1\s*=\s*"([^"]+)"', attrs).group(1))
            cx2 = float(re.search(r'cx2="([^"]+)"', attrs).group(1))
            cy2 = float(re.search(r'cy2\s*=\s*"([^"]+)"', attrs).group(1))
        raw.append((ptype, x, y, cx1, cy1, cx2, cy2))

    d = []
    for i, (ptype, x, y, cx1, cy1, cx2, cy2) in enumerate(raw):
        if i == 0:
            d.append(f'M {x:.2f},{y:.2f}')              # FIRST point is always M
        elif ptype == 'c' and cx1 is not None:
            d.append(f'C {cx1:.2f},{cy1:.2f} {cx2:.2f},{cy2:.2f} {x:.2f},{y:.2f}')
        elif ptype == 'm':
            d.append(f'M {x:.2f},{y:.2f}')
        else:
            d.append(f'L {x:.2f},{y:.2f}')
    return ' '.join(d), [(p[1], p[2]) for p in raw]
```

For polygon-like shapes (`ground`, `floor`, `room`), append `Z` to close the path so the fill is correct.

---

## 7. Features: shared coordinate space, plus transform attributes

Feature `x, y` are in the same world-coordinate space as the hex grid / square grid — no transformation needed. For hex maps, use `hex_center()` to find which hex a feature sits on. For square maps, use `square_center()`.

Each feature carries transform attributes that matter for icon rendering:

- `rotate="0.0"` — degrees
- `scale="-1.0"` — negative values mean flip-around-axis
- `isFlipHorizontal="true|false"`
- `isFlipVertical="true|false"`
- `zOrder="..."` — drawing order

For text labels you can ignore these. For decorative tile features (coast tiles, terrain overlays, oriented furniture) they matter — Worldographer rotates and flips a small library of tiles to build seamless arrangements.

Feature label text is wrapped inside a nested `<label>` element — the regex needs to extract the text content after the inner `<location>` self-closing tag:

```python
feat_pattern = re.compile(
    r'<feature\s+type="([^"]+)"[^>]*?>'
    r'.*?<location\s+viewLevel="[^"]*"\s+x="([^"]+)"\s+y="([^"]+)"\s*/>'
    r'(?:.*?<label[^>]*?>.*?<location[^>]*/>([^<]*)</label>)?'
    r'\s*</feature>',
    re.DOTALL
)
```

The `(?:...)?` makes the label optional — some features (especially decorative coast tiles) have empty or absent labels.

---

## 8. Verification methodology

Before rendering anything fancy, **anchor against known features**. The user usually knows where their major settlements or rooms are. Confirm your geometry by checking that the feature's world `(x, y)` round-trips to the expected `(col, row)`:

```python
# Hex: inverse of hex_center
def hex_at_world(wx, wy):
    col = round((wx - 150) / 225)
    if col % 2 == 0:
        row = round((wy - 150) / 300)
    else:
        row = round((wy - 300) / 300)
    return col, row

# Square: trivial inverse
def square_at_world(wx, wy):
    return int(wx // 300), int(wy // 300)
```

Run this against 3–5 known features. If even one is off by more than 0–1 cells, the geometry is wrong. Don't try to render until they all line up.

---

## 9. Project conventions (Aethelmark-specific)

These reflect choices for *this* project, not the format itself.

### Palette source: `worldographer_terrain.properties`

The authoritative source of truth for terrain colours and feature definitions is `worldographer_terrain.properties`, extracted from the Worldographer .jar. This file defines:

- **480 terrains with authoritative fill colours** — Classic (84), ISO Cols (162), ISO Rows (165), Floor (58), Cosmic (4), Full Classic (4), plus a few singletons.
- **1232 feature/icon definitions** — Battlemat (324), Structure (310), Isometric Region (193), Classic features (129), Token (89), Coasts (59), and others.

**Source location inside the .jar** (for re-extraction after Worldographer updates):

```
Worldographer-0.0.1-SNAPSHOT.jar
  └── generator-data/
        └── terrain.properties
```

A .jar is a zip archive — open with any zip tool (7-Zip, `unzip`, etc.) and copy the file out.

**Project paths:**
- `Other_References/worldographer_terrain.properties` — the extracted source file
- `Python/worldographer/worldographer_palette.py` — generated palette module
- `Python/worldographer/extract_terrain_palette.py` — the extractor script
- `Python/worldographer/wxx_to_svg.py` — the renderer that imports the palette

Schema per line:

```
Namespace/Name = texture_path \t scale \t r,g,b,a \t weight [\t marker \t blend_neighbours]
```

Worldographer uses `\` to escape spaces in the Java .properties key syntax (`Classic\ Mountains\ Forest`). Strip that during parsing.

The companion script `extract_terrain_palette.py` parses this file and writes `worldographer_palette.py`, which `wxx_to_svg.py` imports directly. To regenerate after a Worldographer update:

```cmd
D:
cd D:\Claude_MCP_folder\Python\worldographer
python extract_terrain_palette.py ..\..\Other_References\worldographer_terrain.properties worldographer_palette.py
```

Heuristic for distinguishing terrains from features in the .properties file: terrains have an RGBA tuple at field 2 (e.g. `.6,.78,.4,1`), features only have `path \t scale`. Split on `,` in field 2 to discriminate.

### Project overrides

Project-specific palette overrides live in `wxx_to_svg.py` under `_PROJECT_OVERRIDES`. These win over the authoritative palette where both define a colour.

**Repurposed terrain IDs.** "Classic/Underdark Open" is being used to mark **rural neighbourhoods** at kingdom-scale view, not literal cave systems. Render as a light cream-pink hex with 2 small cottages.

**Color palette: bright valley + autumn mountains** — Aethelmark/Silberbach Valley gets a warmer, more saturated take on the default Classic colours. Other maps that import the renderer without overrides get Worldographer's stock palette directly.

**Settlement icon mapping** for hex maps:

- `Settlement Capital` → walled city, red palette, three towers (e.g. Silberbach)
- `Settlement Village` → paired house cluster
- `Building Cottage` → single building (manors and hamlets — Isalia's Manor, Reinheim, Waldheim)
- `Building Clanmoot` → longhouse silhouette (Aldenburg Hold)
- `Military Fort` → square fort with corner towers (Westgate)
- `Resource Mines` → cave mouth + crossed pickaxes
- `Symbol Bridge` → arched bridge
- `Symbol Anchor` → ferry crossing

**Square map conventions** (TBD as battlemaps come in for this project):

- Layer stack typically: ground → floors → walls → features
- For interior maps, default backdrop is light blue (BATTLEMAT default)
- Furniture renders as labelled markers, not Worldographer art

---

## 10. Pre-render verification checklist

Run through this every time before bothering with stylistic polish.

**Common to both map types:**

1. **Map type** — does `<map type>` and `hexOrientation` match what the user described? Auto-route accordingly.
2. **Layer count** — does `len(layers)` look reasonable? (typically 5–10)
3. **Shape count** — does the count of paths in your output match `<shape>` count in the source (minus single-point degenerate shapes)?
4. **Feature anchoring** — pick 3 known items, confirm world `(x, y)` maps to expected `(col, row)`.

**Hex maps additionally:**

5. **Hex orientation** — is `hexOrientation` `COLUMNS` or `ROWS`? Use the matching `hex_center_*` and `hex_polygon_*` from §4.
6. **Hex count** — does `len(GRID) == tilesWide` and `len(GRID[0]) == tilesHigh`? (column-major in both orientations)
7. **Terrain IDs** — every ID in the grid appears in TERRAIN? Any unmapped IDs?
8. **Polar overlay** — any tiles with field 2 = `1`? If so, render the white wash on those hexes.
9. **Coast features** — identified and excluded from regular feature rendering?
10. **Water hexes** — actual water (id varies; `Classic/Water Sea` or `Classic/Water Ocean`) hexes rendered as the lake/sea body, not just the coast ornaments?

**Square maps additionally:**

11. **Tile uniformity** — confirm all tiles are blank (`'0\t1\t0\t0\t0\tZ'` or similar). If they vary, the tile grid IS being used and you need to handle it.
12. **Shape tags** — recognised tags (`ground`, `floor`, `room`, `wall`)? Any custom tags the user added that need styling?
13. **Polygon closure** — ground/floor/room paths should end with `Z` to fill correctly.

Once all relevant checks pass, the map will be structurally correct and any remaining issues are stylistic.
