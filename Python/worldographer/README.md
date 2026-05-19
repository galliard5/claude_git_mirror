# Worldographer Map Tooling

A Python toolkit for post-processing [Worldographer](https://worldographer.com/) `.wxx` map files into annotated SVGs and AI-readable map descriptions, with a PySide6 GUI editor for the annotation workflow.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Requirements](#2-requirements)
3. [Project file layout](#3-project-file-layout)
4. [The annotation workflow](#4-the-annotation-workflow)
5. [Command-line tools](#5-command-line-tools)
6. [GUI Editor](#6-gui-editor)
7. [Annotation file format reference](#7-annotation-file-format-reference)
8. [Adding a new project style](#8-adding-a-new-project-style)
9. [Known limitations](#9-known-limitations)
10. [Packaging for distribution](#10-packaging-for-distribution)

---

## 1. Overview

Worldographer exports maps as `.wxx` files — gzip-compressed UTF-16-BE XML. These files encode every hex cell, terrain type, feature icon, and hand-drawn shape (roads, rivers, walls, districts), but carry no narrative information: no road names, no river names, no settlement descriptions.

This toolkit bridges that gap with a three-step workflow:

```
.wxx  →  [scaffold]  →  .annotations.md  →  [render]  →  .svg
                              ↑
                       author edits here
```

1. **Scaffold** — on first run the renderer reads the `.wxx`, detects roads, rivers, walls, districts, and POIs, and writes a `.annotations.md` sidecar with labelled TODO placeholders.
2. **Annotate** — the author fills in real names, base conditions, flow origins/terminations, POI descriptions, entity definitions (bridges, tolls, fords), etc. — either by editing the `.md` file directly or via the GUI editor.
3. **Render** — on subsequent runs the renderer merges the annotation data into the `.svg` output, embedding a structured description block in the SVG comment header that AI tools can parse without seeing the image.

A fourth tool (`wxx_to_claude.py`) can generate a standalone `.md` description file suitable for dropping directly into a chat context.

---

## 2. Requirements

| Package | Version | Purpose |
|---------|---------|---------|
| Python | 3.10 + | Runtime |
| PySide6 | 6.x | GUI editor |

No other third-party packages are required. All other imports (`gzip`, `re`, `math`, `subprocess`, `json`, `datetime`, `pathlib`) are Python standard library.

### Install PySide6

```
pip install PySide6
```

---

## 3. Project file layout

```
worldographer/
│
│   Core tools
├── wxx_to_svg.py          Renders .wxx → .svg  (main render pipeline)
├── wxx_to_claude.py       Renders .wxx → .md   (AI description only)
├── wxx_annotations.py     Scaffold, parse, and merge annotation sidecars
│
│   GUI editor
├── worldographer_editor.py   PySide6 main window
├── annotation_model.py       Data model (load / save / render / river join)
├── svg_viewer.py             Pan-zoom SVG canvas widget
│
│   Support modules
├── worldographer_palette.py  Terrain colour palette (TERRAIN_COLORS dict)
├── worldographer_atlas.py    Multi-map atlas builder
├── extract_terrain_palette.py  Helper: extract palette from a live .wxx
│
│   Project style profiles
├── projects/
│   ├── __init__.py
│   ├── default.py         Default styling (generic fantasy world)
│   └── aethelmark.py      Aethelmark campaign-specific styling
│
│   Icon and terrain vocabularies  (by Worldographer map type)
├── icons/
│   ├── world.py, town.py, battlemap.py, cosmic.py
└── terrain/
    ├── world.py, town.py, battlemap.py
```

### Per-map sidecar files (generated alongside your `.wxx`)

```
silberbach_valley_map.svg                  Rendered output
silberbach_valley_map.annotations.md       The annotation file you edit
silberbach_valley_map.annotations.previous.md   Backup after --regenerate
```

The annotation file name is derived from the **SVG output path**, not the `.wxx` path. If you name the SVG differently from the `.wxx` (e.g. replacing spaces with underscores), the annotation file takes the SVG's base name.

---

## 4. The annotation workflow

### First run (scaffold)

```
python wxx_to_svg.py "my map.wxx" my_map.svg
```

Because no `my_map.annotations.md` exists yet, the renderer:

- Detects all roads, rivers, walls, moats, and district polygons in the `.wxx`
- Infers road widths from Worldographer's `strokeWidth` (weight/100 ≈ feet)
- Detects tower and gatehouse features adjacent to wall paths
- Identifies river pairs that share endpoints (stitch candidates)
- Writes `my_map.annotations.md` filled with `TODO` placeholders
- Produces a diagnostic SVG for orientation

### Edit the annotation file

Open `my_map.annotations.md` in any text editor **or** in the GUI editor. Fill in:

- Road and river **names** and **base conditions**
- River **origins** and **terminations**
- Wall **type**, **height**, **condition**
- District **descriptions** and **visibility**
- **Entity definitions** for bridges, tolls, and fords referenced in conditions
- **POI** names and descriptions for custom points of interest
- **Feature visibility overrides** (`known` / `local` / `hidden`)

### Production render

Run the same command again:

```
python wxx_to_svg.py "my map.wxx" my_map.svg
```

The renderer now merges the annotation data and produces a fully-labelled SVG with a structured description block in the header comment.

### Regenerating after map changes

If you substantially change the `.wxx` (add roads, reroute a river, add walls):

```
python wxx_to_svg.py "my map.wxx" my_map.svg --regenerate-annotations
```

The existing annotation file is backed up to `.annotations.previous.md` and a fresh scaffold is written. You then copy your named entries from `.previous.md` into the new scaffold.

---

## 5. Command-line tools

### wxx_to_svg.py

```
python wxx_to_svg.py <input.wxx> <output.svg> [options]
```

| Option | Effect |
|--------|--------|
| `--regenerate-annotations` | Back up existing annotation file and scaffold a new one |
| `--player` | Player render: `hidden` features omitted; `local` features shown unlabelled |
| `--gm` | GM render: all features shown (default) |
| `--project NAME` | Override project style (e.g. `aethelmark`). Normally read from the annotation file's `project:` key |
| `--no-claude-header` | Skip the embedded AI description block |
| `--width N` | Also write a PNG at width N pixels (requires `cairosvg`) |

### wxx_to_claude.py

Generates a standalone AI-readable `.md` description (no SVG).

```
python wxx_to_claude.py <input.wxx> <output.md> [--annotations path/to/annotations.md]
```

The output is suitable for pasting directly into a chat context. It includes:
- Map metadata (type, grid size, orientation)
- Linear feature paths with cell-by-cell coordinates and `@ref` markers
- Entity definitions table
- POIs with coordinates
- District membership for each hex feature

---

## 6. GUI Editor

```
python worldographer_editor.py [path/to/map.wxx]
```

The editor provides a split-pane interface: annotation tabs on the left, SVG preview on the right.

### Toolbar

| Button | Shortcut | Action |
|--------|----------|--------|
| Open .wxx (▾) | Ctrl+O | Open file dialog; arrow opens recent files dropdown (last 10) |
| Save | Ctrl+S | Write annotation file to disk |
| Render SVG | Ctrl+R | Auto-save then run wxx_to_svg.py; reloads the preview |
| Regenerate Scaffold | — | Back up annotation file and re-scaffold from .wxx |
| Quit | Ctrl+Q | Exit; prompts Save/Don't Save/Cancel if there are unsaved changes |

### SVG Preview (right pane)

| Action | Effect |
|--------|--------|
| Drag | Pan |
| Scroll wheel | Zoom (centred on cursor) |
| Double-click | Fit to window |
| `+` / `-` | Zoom in/out |
| `0` or `F` | Fit to window |
| Arrow keys | Pan |
| Hide Map / Show Map | Collapse/expand the preview panel |
| Opacity slider | Blend the SVG for overlay reference work |

### Annotation tabs

**Roads** — list of all road/bridge shapes. Select an entry to edit its name, base surface description, and conditions. Conditions are entered in `(col, row): key=value` format.

**Rivers** — same as Roads plus:
- Direction indicator (`→` forward / `←` reverse)
- **⇄ Flip Direction** — toggles the flow direction between forward and reverse
- **Join with…** dropdown — only shows rivers that share an actual endpoint with the selected river (validated geometrically). Choose a partner, optionally tick "Reverse other", then click Join to stitch them.

**Walls** — wall segment name, type, height, thickness, condition, and editable towers/gates lists (auto-populated from nearby .wxx features on scaffold).

**Moat** — moat name, source (river/dug/dry), dimensions, condition.

**Districts** — district name, visibility, and description for each polygon area.

**POIs** — two groups in one list:
- `◈` **Map features** (from the .wxx): read-only name/type/cell. Visibility, Description, and GM Note are editable and write to the annotation file.
- `●` **Custom annotation POIs**: fully editable. Use `+ Add Custom POI` to create new ones; `Remove` to delete them.

**Entity Defs** — defines bridges, tolls, fords, gatehouses etc. referenced by `ref=` conditions in roads/rivers. The tab automatically shows:
- Defined entities (white)
- `★` undefined-but-referenced entities (orange) — click one to fill in its fields; on commit it moves to the defined group
- **↻ Refresh** re-scans in-memory conditions without requiring a file save/reload
- **+ Add Ref** prompts for a new ref ID and creates a typed stub
- Each entity shows "Referenced by:" listing every road/river condition that uses it

**Intent** — project style selector and free-form narrative notes about the map's design intent.

### Status bar

```
silberbach_valley_map.annotations.md *  │  12 TODOs  │  Last render: 14:22
```

- `*` — unsaved changes
- TODO count turns orange when nonzero, green when all fields are filled
- Last render time updates after each successful Render SVG

---

## 7. Annotation file format reference

The annotation file is a Markdown-flavoured plain-text file. Sections are delimited by `##` headers; entries within sections by `###` headers.

### Sections

#### `## Project`
```yaml
project: default          # or aethelmark, or any name in projects/
```

#### `## Intent / ### Narrative`
Free-form bullet points describing the map's design intent. Surfaced to AI consumers.

#### `## Elevation Overrides`
```
overrides:
  (15, 12): 1800m         # ridge fortress site
```

#### `## Roads`
```
### road N
name: Imperial Highway (NW)
base: Cobble and packed dirt, well-travelled, width=30
flow:
  primary_endpoint: (31, 23)
  secondary_endpoint: (-1, 10)
conditions:
  (-1, 10): to the capital
  (31, 23): ref=bridge#4, ref=bridge#5, ref=bridge#6, ref=toll#3
```

#### `## Rivers`
```
### river N
name: Angerap River
base: width=Wide, moderate current
flow:
  origin: mountain snowmelt
  origin_cell: (-1, 4)
  termination: ocean
  termination_cell: (41, 50)
  direction: forward          # or reverse
  stitch_with: river 2        # optional: joins two segments into one logical river
conditions:
  (35, 40): ref=toll#1, ref=bridge#1
```

#### `## Walls`
```
### wall 1
name: City Wall
type: stone                   # palisade | earthwork | stone | brick | ruins
height_m: 8
thickness_m: 2
condition: intact             # intact | damaged | ruined | under_construction
towers: (38,36), (22,14), (29,35), (23,33), (19,26), (19,19)
gates: (33,35), (21,16), (19,24)
note: Northwestern gate has been walled up since the siege of 1142
```

#### `## Moat`
```
### moat 1
name: River Moat
source: river                 # river | dug | dry
width_m: 40
depth_m: 3
condition: seasonal — dry in late summer
is_river_segment: true
note:
```

#### `## Districts`
```
### district 1
name: Old Town
visibility: known             # known | local | hidden
description: The oldest part of the city, densely packed...
note:
```

#### `## Linear Feature Details`

Defines the entities referenced by `ref=` conditions. The ref ID prefix determines the field template:

| Prefix | Fields |
|--------|--------|
| `bridge#N` | name, type, material, length_m, note, clearance |
| `toll#N` | name, type, controlled_by, fee, note |
| `ford#N` | name, type, difficulty, note |
| `gatehouse#N` | name, type, controlled_by, condition, note |
| `ferry#N` | name, type, note |
| anything else | name, type, note |

Example:
```
### bridge#1
name: Kaelan Bridge
type: bridge
material: stone
length_m: 40
note: toll bridge
clearance: 10m
```

#### `## Points of Interest`

Custom POIs not already represented by .wxx feature icons:

```
### poi#1
name: Hidden Shrine of the Old Faith
type: shrine
cell: (25, 18)
visibility: hidden            # known | local | hidden
description: A moss-covered altar, unknown to the city authorities.
note: The keeper is Marta in the Old Town.
```

#### `## Feature Visibility Overrides`

Override the render visibility of any .wxx feature by cell:

```
(22, 14): local               # unlabelled on player maps
(31, 25): hidden              # GM only
```

#### `## Feature Names`

Rename any .wxx feature by cell (including unlabelled ones):

```
(35, 3): North Mine Head
(32, 2): East Shaft
```

### Visibility values

| Value | Effect on player render | Effect on GM render |
|-------|------------------------|---------------------|
| `known` | Shown with label | Shown with label |
| `local` | Shown without label | Shown with label |
| `hidden` | Not shown | Shown with label (grey) |

---

## 8. Adding a new project style

Create `projects/myproject.py` with any subset of these dicts/functions:

```python
# projects/myproject.py

ROAD_STYLE   = {'stroke': '#5a3d1d', 'stroke_width': 3.0, 'fill': 'none'}
RIVER_STYLE  = {'stroke': '#4a8fbf', 'stroke_width': 5.0, 'fill': 'none'}
WALL_STYLE   = {'stroke': '#3a2a1a', 'stroke_width': 8.0, 'fill': 'none'}
MOAT_STYLE   = {'stroke': '#4a8fbf', 'stroke_width': 4.0, 'fill': 'none',
                'stroke_dasharray': '6,3'}
DISTRICT_STYLE = {'stroke': '#888', 'stroke_width': 1.5, 'fill': 'none',
                  'stroke_dasharray': '4,4'}
```

Then set `project: myproject` in your annotation file's `## Project` section, or pass `--project myproject` on the command line.

---

## 9. Known limitations

- **River path display**: The `.wxx` stores Bézier control points, not interpolated hex cells. `sample_path_cells()` linearly interpolates between control points to find which hexes a path touches. For heavily curved paths this is an approximation; the shape will render correctly in the SVG but the condition cell coordinates in the annotation file may not perfectly align with the visual curve.

- **Stitch candidates are advisory**: The scaffold marks river pairs whose endpoints share adjacent hexes as stitch candidates. You still need to manually set `stitch_with:` and `direction:` — the tool cannot determine which segment is "upstream" automatically.

- **District gap analysis**: Worldographer draws each district as a closed polygon. Districts that share a boundary (e.g. a city wall running between two districts) may have a 1–2 hex gap in the polygon fill. This is expected — the wall occupies those hexes.

- **Annotation round-trip**: The annotation file is human-editable plain text. Comments (`# ...`) and free-text lines in `conditions:` blocks are preserved on disk but stripped by the parser. Do not put critical information in comments.

- **PNG export**: `--width N` requires `cairosvg` (`pip install cairosvg`). Not installed by default.

---

## 10. Packaging for distribution

To distribute the editor to a friend who has no Python installed, you need to bundle the entire Python runtime, all libraries, and all project files into a self-contained folder or installer.

### Recommended approach: PyInstaller + Inno Setup

#### Step 1 — Install PyInstaller

```
pip install pyinstaller
```

#### Step 2 — Fix the render subprocess (required before bundling)

In a PyInstaller bundle `sys.executable` points to the bundled `.exe`, not to Python. The current `annotation_model.py` uses a subprocess call to run `wxx_to_svg.py` as a script, which breaks in bundles.

Add this function to `wxx_to_svg.py` **above** `def main()`:

```python
def render_map(wxx_path: str, svg_path: str,
               player: bool = False, regenerate: bool = False,
               project: str = None) -> tuple[bool, str]:
    """Callable API for the GUI (avoids subprocess in bundled apps)."""
    import io, traceback
    old_argv = sys.argv
    try:
        args = [wxx_path, svg_path]
        if player:      args.append('--player')
        if regenerate:  args.append('--regenerate-annotations')
        if project:     args += ['--project', project]
        sys.argv = ['wxx_to_svg.py'] + args
        # Redirect stdout/stderr
        buf = io.StringIO()
        import contextlib
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            main()
        return True, buf.getvalue()
    except SystemExit as e:
        return (e.code == 0), buf.getvalue()
    except Exception:
        return False, traceback.format_exc()
    finally:
        sys.argv = old_argv
```

Then update `annotation_model.py` `render()` to try the direct call first:

```python
def render(self) -> tuple[bool, str]:
    if not self.wxx_path or not self.svg_path:
        return False, 'No .wxx file loaded.'
    try:
        from wxx_to_svg import render_map
        return render_map(self.wxx_path, self.svg_path)
    except ImportError:
        pass
    # Fallback: subprocess (development only)
    script = os.path.join(_HERE, 'wxx_to_svg.py')
    result = subprocess.run(
        [sys.executable, script, self.wxx_path, self.svg_path],
        capture_output=True, text=True, timeout=60,
    )
    return result.returncode == 0, result.stdout + result.stderr
```

#### Step 3 — Create a PyInstaller spec file

Create `worldographer_editor.spec`:

```python
# worldographer_editor.spec
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

added_files = [
    ('projects',  'projects'),
    ('icons',     'icons'),
    ('terrain',   'terrain'),
]

a = Analysis(
    ['worldographer_editor.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        'PySide6.QtSvg',
        'PySide6.QtXml',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz, a.scripts, [],
    exclude_binaries=True,
    name='WorldographerEditor',
    debug=False,
    console=False,          # no console window
    icon=None,              # add path to .ico file here if you have one
)
coll = COLLECT(
    exe, a.binaries, a.zipfiles, a.datas,
    name='WorldographerEditor',
)
```

#### Step 4 — Build

```
pyinstaller worldographer_editor.spec
```

This creates `dist/WorldographerEditor/` — a folder containing the `.exe` and all dependencies. Test it before wrapping:

```
dist\WorldographerEditor\WorldographerEditor.exe
```

#### Step 5 — Wrap as an installer with Inno Setup (optional)

1. Download [Inno Setup](https://jrsoftware.org/isinfo.php) (free)
2. Create `installer.iss`:

```ini
[Setup]
AppName=Worldographer Annotation Editor
AppVersion=1.0
DefaultDirName={autopf}\WorldographerEditor
DefaultGroupName=Worldographer Editor
OutputDir=installer_output
OutputBaseFilename=WorldographerEditor_Setup
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\WorldographerEditor\*"; DestDir: "{app}"; Flags: recursesubdirs

[Icons]
Name: "{group}\Worldographer Editor"; Filename: "{app}\WorldographerEditor.exe"
Name: "{commondesktop}\Worldographer Editor"; Filename: "{app}\WorldographerEditor.exe"

[Run]
Filename: "{app}\WorldographerEditor.exe"; Description: "Launch editor"; Flags: postinstall
```

3. Compile in Inno Setup IDE → produces `WorldographerEditor_Setup.exe`

#### Estimated bundle size

| Component | Size |
|-----------|------|
| Python runtime | ~15 MB |
| PySide6 / Qt6 libraries | ~250–300 MB |
| Project scripts and data | ~1 MB |
| **Total (folder)** | **~270–320 MB** |
| **Installer (.exe, compressed)** | **~120–150 MB** |

#### What the recipient needs

- Windows 10 or 11 (64-bit)
- Nothing else — Python, pip, and all libraries are bundled

#### What they do NOT need to install

- Python
- PySide6
- Any other packages

The `.wxx` files remain on their machine as before; they just need to point the editor at them with **File → Open .wxx**.
