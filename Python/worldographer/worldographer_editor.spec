# worldographer_editor.spec
#
# PyInstaller spec for the Worldographer Annotation Editor.
#
# Usage (from the project folder):
#   pyinstaller worldographer_editor.spec
#
# Output:
#   dist\WorldographerEditor\WorldographerEditor.exe  (+ all deps)
#
# Requirements:
#   pip install pyinstaller PySide6
#
# Notes:
#   - Python 3.10+ required (match-statement, union-type hints)
#   - PySide6 6.x bundles Qt DLLs automatically via the hook
#   - The 'projects', 'icons', and 'terrain' sub-packages must be
#     collected as data because they are imported by name at runtime
#   - wxx_to_svg.py, wxx_annotations.py, etc. are picked up as pure-
#     Python source modules via Analysis; no special treatment needed
# ---------------------------------------------------------------------------

import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

block_cipher = None

# ---------------------------------------------------------------------------
# Collect every sub-module from our runtime sub-packages so PyInstaller
# doesn't miss lazily-imported modules (e.g. projects.aethelmark).
# ---------------------------------------------------------------------------
hidden = []
for pkg in ('projects', 'icons', 'terrain'):
    hidden += collect_submodules(pkg)

# PySide6 extras that are used indirectly and may not be auto-detected
hidden += [
    'PySide6.QtSvg',
    'PySide6.QtXml',
    'PySide6.QtWidgets',
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtPrintSupport',   # pulled in by some Qt styles on Windows
]

# ---------------------------------------------------------------------------
# Data files: the sub-packages are pure Python, but we need their .py
# files present so __import__ / importlib.import_module() can find them.
# collect_data_files copies the whole tree; include_py_files=True ensures
# .py sources (not just compiled .pyc) are bundled.
# ---------------------------------------------------------------------------
datas = []
for pkg in ('projects', 'icons', 'terrain'):
    datas += collect_data_files(pkg, include_py_files=True)

# If you have a custom window icon, uncomment and set the path:
# ICON_PATH = str(Path('assets') / 'worldographer.ico')

a = Analysis(
    ['worldographer_editor.py'],
    pathex=[str(Path('.').resolve())],
    binaries=[],
    datas=datas,
    hiddenimports=hidden,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude heavy optional libs that are not needed at runtime
        'matplotlib', 'numpy', 'pandas', 'scipy', 'PIL', 'cv2',
        'cairosvg',   # only used for PNG export via CLI, not GUI
        'tkinter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='WorldographerEditor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,           # set False if UPX causes false-positive AV hits
    console=False,      # no console window; set True for debug builds
    # icon=ICON_PATH,   # uncomment if you have a .ico file
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='WorldographerEditor',
)
