"""
worldographer_editor.py — PySide6 GUI editor for Worldographer annotation files.

Usage:
    python worldographer_editor.py [path/to/map.wxx]

Layout overview:
    ┌─ Toolbar ─────────────────────────────────────────────────────────────┐
    │ [Open] [Save] [Render] [Fit]           Zoom: 45%  [Hide Map] [Opacity]│
    ├─ QSplitter ──────────────────────────────────────────────────────────┤
    │  Left: QTabWidget                    Right: SvgViewer                 │
    │  ┌ Roads │ Rivers │ Walls │ Moat │ Districts │ POIs │ Entity Defs ┐   │
    │  │ ┌── Entry list ─────────────────────────────────────────────┐ │   │
    │  │ │  ● road 1   Imperial Highway (NW)  30ft                   │ │   │
    │  │ │  ▶ road 2   Silberbach Road         30ft                  │ │   │
    │  │ └──────────────────────────────────────────────────────────┘ │   │
    │  │ ┌── Form ────────────────────────────────────────────────── ┐ │   │
    │  │ │  Name: [_______________________]                          │ │   │
    │  │ │  Base: [_______________________]                          │ │   │
    │  │ │  From: (31, 23)   To: (-1, 10)                           │ │   │
    │  │ │  Conditions: [multiline edit]                             │ │   │
    │  │ └──────────────────────────────────────────────────────────┘ │   │
    │  └──────────────────────────────────────────────────────────────┘   │
    ├─ Status bar ──────────────────────────────────────────────────────────┤
    │  silberbach_valley_map.annotations.md  │  12 TODOs  │  Rendered 14:22 │
    └───────────────────────────────────────────────────────────────────────┘
"""
from __future__ import annotations
import sys
import os
from datetime import datetime
from typing import Optional

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QSplitter, QTabWidget,
    QListWidget, QListWidgetItem, QFormLayout, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QPlainTextEdit, QComboBox, QCheckBox,
    QToolBar, QStatusBar, QFileDialog, QMessageBox, QSlider, QSizePolicy,
    QFrame, QScrollArea, QMenu, QToolButton,
)
from PySide6.QtCore import Qt, QSize, Signal, QObject
from PySide6.QtGui import QAction, QFont, QIcon, QColor

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from annotation_model import AnnotationModel, _serialize_conditions, _parse_conditions_text
from wxx_annotations import world_to_hex, world_to_square
from svg_viewer import SvgViewer

_RECENT_PATH = os.path.join(_HERE, '.worldographer_recent.json')


def _load_recent() -> list[str]:
    import json
    try:
        return json.load(open(_RECENT_PATH, encoding='utf-8'))
    except Exception:
        return []


def _save_recent(paths: list[str]) -> None:
    import json
    try:
        json.dump(paths, open(_RECENT_PATH, 'w', encoding='utf-8'))
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Text widget subclasses with guaranteed right-click context menus
# ---------------------------------------------------------------------------

class _TextEdit(QLineEdit):
    """QLineEdit that always shows a right-click context menu."""
    def contextMenuEvent(self, event):
        menu = self.createStandardContextMenu()
        menu.exec(event.globalPos())


class _TextArea(QPlainTextEdit):
    """QPlainTextEdit that always shows a right-click context menu."""
    def contextMenuEvent(self, event):
        menu = self.createStandardContextMenu()
        menu.exec(event.globalPos())


# ---------------------------------------------------------------------------
# Tiny signal wrapper so AnnotationModel can emit Qt signals
# ---------------------------------------------------------------------------

class ModelSignals(QObject):
    dirty_changed = Signal(bool)
    data_loaded = Signal()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

DIRECTION_GLYPH = {
    'forward': '→',   # →
    'reverse': '←',   # ←
}

def _todo_marker(value: str) -> str:
    """Return '● ' if value is a TODO placeholder, '' otherwise."""
    if not value:
        return '● '
    s = str(value).strip()
    if s.upper() == 'TODO' or s.startswith('TODO') or '##' in s:
        return '● '
    return ''


def _hline() -> QFrame:
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    line.setFrameShadow(QFrame.Sunken)
    return line


# ---------------------------------------------------------------------------
# Individual tab implementations
# ---------------------------------------------------------------------------

class _BaseTab(QWidget):
    """Abstract base: a list on top, a form area below, separated by a splitter."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._model: Optional[AnnotationModel] = None
        self._loading: bool = False   # suppress change signals during populate

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        splitter = QSplitter(Qt.Vertical)
        outer.addWidget(splitter)

        # List widget (top pane)
        self._list = QListWidget()
        self._list.setFont(QFont('Consolas', 9))
        self._list.currentRowChanged.connect(self._on_row_changed)
        splitter.addWidget(self._list)

        # Scroll area wrapping the form (bottom pane)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        form_host = QWidget()
        self._form_layout = QFormLayout(form_host)
        self._form_layout.setContentsMargins(8, 8, 8, 8)
        self._form_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        scroll.setWidget(form_host)
        splitter.addWidget(scroll)
        splitter.setSizes([200, 300])

        self._current_ordinal: Optional[int] = None

    def set_model(self, model: AnnotationModel) -> None:
        self._model = model
        self.populate()

    def populate(self) -> None:
        """Rebuild the list from the model. Subclasses implement."""
        pass

    def _on_row_changed(self, row: int) -> None:
        """Subclasses implement: load the form for the selected row."""
        pass

    def _clear_form(self) -> None:
        while self._form_layout.count():
            item = self._form_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()


# ---------------------------------------------------------------------------
# Roads tab
# ---------------------------------------------------------------------------

class RoadsTab(_BaseTab):
    def populate(self) -> None:
        if not self._model:
            return
        self._loading = True
        self._list.clear()
        roads = self._model.data.get('roads', {})
        self._ordinals = sorted(roads.keys())
        for ordinal in self._ordinals:
            entry = roads[ordinal]
            name = entry.get('name', 'TODO')
            base = entry.get('base', '')
            marker = _todo_marker(name)
            # Extract width hint from base
            import re
            wm = re.search(r'width[=~]?(\d+)\s*ft', base, re.IGNORECASE)
            width_hint = f'  {wm.group(1)}ft' if wm else ''
            label = f'{marker}road {ordinal:<3}  {name:<28}{width_hint}'
            self._list.addItem(QListWidgetItem(label))
        self._loading = False
        if self._ordinals:
            self._list.setCurrentRow(0)

    def _on_row_changed(self, row: int) -> None:
        if self._loading or not self._model or row < 0:
            return
        if row >= len(self._ordinals):
            return
        ordinal = self._ordinals[row]
        self._current_ordinal = ordinal
        self._load_form(ordinal)

    def _load_form(self, ordinal: int) -> None:
        self._clear_form()
        roads = self._model.data.get('roads', {})
        entry = roads.get(ordinal, {})
        flow = entry.get('flow', {})

        def _lbl(text):
            lbl = QLabel(text)
            lbl.setStyleSheet('color: #888;')
            return lbl

        # Name
        self._name_edit = _TextEdit(entry.get('name', ''))
        self._name_edit.editingFinished.connect(self._commit)
        self._form_layout.addRow('Name:', self._name_edit)

        # Base
        self._base_edit = _TextEdit(entry.get('base', ''))
        self._base_edit.editingFinished.connect(self._commit)
        self._form_layout.addRow('Base:', self._base_edit)

        # Endpoints (read-only labels)
        from annotation_model import _fmt_cell
        pep = _fmt_cell(flow.get('primary_endpoint', ''))
        sep = _fmt_cell(flow.get('secondary_endpoint', ''))
        self._form_layout.addRow('From (primary):', _lbl(pep or '—'))
        self._form_layout.addRow('To (secondary):', _lbl(sep or '—'))

        # Conditions
        self._form_layout.addRow(_hline())
        cond_lines = _serialize_conditions(entry.get('conditions', {}))
        self._cond_edit = _TextArea('\n'.join(cond_lines))
        self._cond_edit.setPlaceholderText('  (col,row): ref=bridge#1')
        self._cond_edit.setMaximumHeight(120)
        self._cond_edit.focusOutEvent = lambda e, orig=self._cond_edit.focusOutEvent: (
            self._commit(), orig(e)
        )
        self._form_layout.addRow('Conditions:', self._cond_edit)

    def _commit(self) -> None:
        if not self._model or self._current_ordinal is None:
            return
        roads = self._model.data.get('roads', {})
        entry = roads.get(self._current_ordinal)
        if entry is None:
            return
        entry['name'] = self._name_edit.text().strip()
        entry['base'] = self._base_edit.text().strip()
        entry['conditions'] = _parse_conditions_text(self._cond_edit.toPlainText())
        self._model.mark_dirty()
        # Refresh list label
        self.populate()
        # Keep selection
        if self._current_ordinal in self._ordinals:
            idx = self._ordinals.index(self._current_ordinal)
            self._loading = True
            self._list.setCurrentRow(idx)
            self._loading = False


# ---------------------------------------------------------------------------
# Rivers tab
# ---------------------------------------------------------------------------

class RiversTab(_BaseTab):
    def populate(self) -> None:
        if not self._model:
            return
        self._loading = True
        self._list.clear()
        rivers = self._model.data.get('rivers', {})
        self._ordinals = sorted(rivers.keys())
        for ordinal in self._ordinals:
            entry = rivers[ordinal]
            name = entry.get('name', 'TODO')
            flow = entry.get('flow', {})
            direction = flow.get('direction', 'forward')
            glyph = DIRECTION_GLYPH.get(direction, '?')
            marker = _todo_marker(name)
            stitch = '  [stitched]' if 'stitch_with' in flow else ''
            label = f'{marker}river {ordinal:<3}  {glyph}  {name}{stitch}'
            self._list.addItem(QListWidgetItem(label))
        self._loading = False
        if self._ordinals:
            self._list.setCurrentRow(0)

    def _on_row_changed(self, row: int) -> None:
        if self._loading or not self._model or row < 0:
            return
        if row >= len(self._ordinals):
            return
        ordinal = self._ordinals[row]
        self._current_ordinal = ordinal
        self._load_form(ordinal)

    def _load_form(self, ordinal: int) -> None:
        self._clear_form()
        rivers = self._model.data.get('rivers', {})
        entry = rivers.get(ordinal, {})
        flow = entry.get('flow', {})

        def _lbl(text):
            lbl = QLabel(str(text) if text else '—')
            lbl.setStyleSheet('color: #888;')
            return lbl

        from annotation_model import _fmt_cell

        # Name
        self._name_edit = _TextEdit(entry.get('name', ''))
        self._name_edit.editingFinished.connect(self._commit)
        self._form_layout.addRow('Name:', self._name_edit)

        # Base
        self._base_edit = _TextEdit(entry.get('base', ''))
        self._base_edit.editingFinished.connect(self._commit)
        self._form_layout.addRow('Base:', self._base_edit)

        # Origin / Termination
        self._form_layout.addRow(_hline())
        self._origin_edit = _TextEdit(flow.get('origin', ''))
        self._origin_edit.setPlaceholderText('mountain springs, lake, etc.')
        self._origin_edit.editingFinished.connect(self._commit)
        self._form_layout.addRow('Origin:', self._origin_edit)
        self._form_layout.addRow('Origin cell:', _lbl(_fmt_cell(flow.get('origin_cell', ''))))
        self._term_edit = _TextEdit(flow.get('termination', ''))
        self._term_edit.setPlaceholderText('ocean, joins <river name>, etc.')
        self._term_edit.editingFinished.connect(self._commit)
        self._form_layout.addRow('Termination:', self._term_edit)
        self._form_layout.addRow('Term. cell:', _lbl(_fmt_cell(flow.get('termination_cell', ''))))

        # Direction row with flip button
        self._form_layout.addRow(_hline())
        direction = flow.get('direction', 'forward')
        dir_row = QWidget()
        dir_h = QHBoxLayout(dir_row)
        dir_h.setContentsMargins(0, 0, 0, 0)
        self._dir_label = QLabel(
            f'{DIRECTION_GLYPH.get(direction, "?")}  {direction}'
        )
        self._dir_label.setFont(QFont('Consolas', 10))
        flip_btn = QPushButton('⇄ Flip Direction')
        flip_btn.setMaximumWidth(130)
        flip_btn.clicked.connect(self._flip)
        dir_h.addWidget(self._dir_label)
        dir_h.addWidget(flip_btn)
        dir_h.addStretch()
        self._form_layout.addRow('Direction:', dir_row)

        # Stitch / join
        stitch_with = flow.get('stitch_with', '')
        stitch_row = QWidget()
        stitch_h = QHBoxLayout(stitch_row)
        stitch_h.setContentsMargins(0, 0, 0, 0)
        self._stitch_label = QLabel(stitch_with if stitch_with else '(none)')
        self._stitch_label.setStyleSheet('color: #888;')

        self._join_combo = QComboBox()
        self._join_combo.setMinimumWidth(280)
        self._join_combo.addItem('— Join with... —')
        candidates = self._model.get_river_join_candidates(ordinal)
        self._join_candidates = candidates   # [(other_idx, desc)]
        for _, desc in candidates:
            self._join_combo.addItem(desc)

        self._reverse_join_check = QCheckBox('Reverse other')
        join_btn = QPushButton('Join')
        join_btn.setMaximumWidth(60)
        join_btn.clicked.connect(self._do_join)

        stitch_h.addWidget(self._stitch_label)
        stitch_h.addStretch()
        stitch_h.addWidget(self._join_combo)
        stitch_h.addWidget(self._reverse_join_check)
        stitch_h.addWidget(join_btn)
        self._form_layout.addRow('Stitched to:', stitch_row)

        # Conditions
        self._form_layout.addRow(_hline())
        cond_lines = _serialize_conditions(entry.get('conditions', {}))
        self._cond_edit = _TextArea('\n'.join(cond_lines))
        self._cond_edit.setPlaceholderText('  (col,row): ref=bridge#1')
        self._cond_edit.setMaximumHeight(120)
        self._cond_edit.focusOutEvent = lambda e, orig=self._cond_edit.focusOutEvent: (
            self._commit(), orig(e)
        )
        self._form_layout.addRow('Conditions:', self._cond_edit)

    def _flip(self) -> None:
        if not self._model or self._current_ordinal is None:
            return
        self._model.flip_river(self._current_ordinal)
        # Refresh direction label
        rivers = self._model.data.get('rivers', {})
        entry = rivers.get(self._current_ordinal, {})
        direction = entry.get('flow', {}).get('direction', 'forward')
        self._dir_label.setText(f'{DIRECTION_GLYPH.get(direction, "?")}  {direction}')
        self.populate()
        if self._current_ordinal in self._ordinals:
            idx = self._ordinals.index(self._current_ordinal)
            self._loading = True
            self._list.setCurrentRow(idx)
            self._loading = False

    def _do_join(self) -> None:
        if not self._model or self._current_ordinal is None:
            return
        combo_idx = self._join_combo.currentIndex()
        if combo_idx <= 0 or combo_idx - 1 >= len(self._join_candidates):
            QMessageBox.information(self, 'Join', 'Select a river to join with first.')
            return
        other_idx, _ = self._join_candidates[combo_idx - 1]
        reverse_other = self._reverse_join_check.isChecked()
        try:
            self._model.join_rivers(self._current_ordinal, other_idx, reverse_b=reverse_other)
        except KeyError as e:
            QMessageBox.warning(self, 'Join Error', str(e))
            return
        self._stitch_label.setText(f'river {other_idx}')
        self.populate()

    def _commit(self) -> None:
        if not self._model or self._current_ordinal is None:
            return
        rivers = self._model.data.get('rivers', {})
        entry = rivers.get(self._current_ordinal)
        if entry is None:
            return
        entry['name'] = self._name_edit.text().strip()
        entry['base'] = self._base_edit.text().strip()
        entry.setdefault('flow', {})['origin'] = self._origin_edit.text().strip()
        entry['flow']['termination'] = self._term_edit.text().strip()
        entry['conditions'] = _parse_conditions_text(self._cond_edit.toPlainText())
        self._model.mark_dirty()
        self.populate()
        if self._current_ordinal in self._ordinals:
            idx = self._ordinals.index(self._current_ordinal)
            self._loading = True
            self._list.setCurrentRow(idx)
            self._loading = False


# ---------------------------------------------------------------------------
# Walls tab
# ---------------------------------------------------------------------------

class WallsTab(_BaseTab):
    def populate(self) -> None:
        if not self._model:
            return
        self._loading = True
        self._list.clear()
        self._wall_list = self._model.data.get('walls', [])
        for i, wall in enumerate(self._wall_list):
            name = wall.get('name', 'TODO')
            wtype = wall.get('type', '')
            cond = wall.get('condition', '')
            marker = _todo_marker(name)
            label = f'{marker}{wall.get("id", f"wall {i+1}")}  {name}  [{wtype}, {cond}]'
            self._list.addItem(QListWidgetItem(label))
        self._loading = False
        if self._wall_list:
            self._list.setCurrentRow(0)

    def _on_row_changed(self, row: int) -> None:
        if self._loading or not self._model or row < 0 or row >= len(self._wall_list):
            return
        self._current_ordinal = row
        self._load_form(row)

    def _load_form(self, idx: int) -> None:
        self._clear_form()
        wall = self._wall_list[idx]

        self._name_edit = _TextEdit(wall.get('name', ''))
        self._name_edit.editingFinished.connect(self._commit)
        self._form_layout.addRow('Name:', self._name_edit)

        self._type_edit = _TextEdit(wall.get('type', 'stone'))
        self._type_edit.setPlaceholderText('palisade | earthwork | stone | brick | ruins')
        self._type_edit.editingFinished.connect(self._commit)
        self._form_layout.addRow('Type:', self._type_edit)

        self._height_edit = _TextEdit(wall.get('height_m', ''))
        self._height_edit.editingFinished.connect(self._commit)
        self._form_layout.addRow('Height (m):', self._height_edit)

        self._thick_edit = _TextEdit(wall.get('thickness_m', ''))
        self._thick_edit.editingFinished.connect(self._commit)
        self._form_layout.addRow('Thickness (m):', self._thick_edit)

        self._cond_wall_edit = _TextEdit(wall.get('condition', 'intact'))
        self._cond_wall_edit.setPlaceholderText('intact | damaged | ruined | under_construction')
        self._cond_wall_edit.editingFinished.connect(self._commit)
        self._form_layout.addRow('Condition:', self._cond_wall_edit)

        self._form_layout.addRow(_hline())

        # Towers and gates — editable multi-line so long coord lists don't clip
        self._towers_edit = _TextArea(wall.get('towers', ''))
        self._towers_edit.setPlaceholderText('(auto-detected from .wxx features)')
        self._towers_edit.setFixedHeight(62)
        self._towers_edit.focusOutEvent = lambda e, orig=self._towers_edit.focusOutEvent: (
            self._commit(), orig(e)
        )
        self._form_layout.addRow('Towers:', self._towers_edit)

        self._gates_edit = _TextArea(wall.get('gates', ''))
        self._gates_edit.setPlaceholderText('(auto-detected from .wxx features)')
        self._gates_edit.setFixedHeight(62)
        self._gates_edit.focusOutEvent = lambda e, orig=self._gates_edit.focusOutEvent: (
            self._commit(), orig(e)
        )
        self._form_layout.addRow('Gates:', self._gates_edit)

        self._note_edit = _TextEdit(wall.get('note', ''))
        self._note_edit.editingFinished.connect(self._commit)
        self._form_layout.addRow('Note:', self._note_edit)

    def _commit(self) -> None:
        if not self._model or self._current_ordinal is None:
            return
        wall = self._wall_list[self._current_ordinal]
        wall['name'] = self._name_edit.text().strip()
        wall['type'] = self._type_edit.text().strip()
        wall['height_m'] = self._height_edit.text().strip()
        wall['thickness_m'] = self._thick_edit.text().strip()
        wall['condition'] = self._cond_wall_edit.text().strip()
        wall['towers'] = self._towers_edit.toPlainText().strip()
        wall['gates'] = self._gates_edit.toPlainText().strip()
        wall['note'] = self._note_edit.text().strip()
        self._model.mark_dirty()
        self.populate()
        if self._current_ordinal is not None and self._current_ordinal < self._list.count():
            self._loading = True
            self._list.setCurrentRow(self._current_ordinal)
            self._loading = False


# ---------------------------------------------------------------------------
# Moat tab
# ---------------------------------------------------------------------------

class MoatTab(_BaseTab):
    def populate(self) -> None:
        if not self._model:
            return
        self._loading = True
        self._list.clear()
        self._moat_list = self._model.data.get('moats', [])
        for i, moat in enumerate(self._moat_list):
            name = moat.get('name', 'TODO')
            src = moat.get('source', '')
            marker = _todo_marker(name)
            label = f'{marker}{moat.get("id", f"moat {i+1}")}  {name}  [{src}]'
            self._list.addItem(QListWidgetItem(label))
        self._loading = False
        if self._moat_list:
            self._list.setCurrentRow(0)

    def _on_row_changed(self, row: int) -> None:
        if self._loading or not self._model or row < 0 or row >= len(self._moat_list):
            return
        self._current_ordinal = row
        self._load_form(row)

    def _load_form(self, idx: int) -> None:
        self._clear_form()
        moat = self._moat_list[idx]

        self._name_edit = _TextEdit(moat.get('name', ''))
        self._name_edit.editingFinished.connect(self._commit)
        self._form_layout.addRow('Name:', self._name_edit)

        self._source_edit = _TextEdit(moat.get('source', 'river'))
        self._source_edit.setPlaceholderText('river | dug | dry')
        self._source_edit.editingFinished.connect(self._commit)
        self._form_layout.addRow('Source:', self._source_edit)

        self._width_edit = _TextEdit(moat.get('width_m', ''))
        self._width_edit.editingFinished.connect(self._commit)
        self._form_layout.addRow('Width (m):', self._width_edit)

        self._depth_edit = _TextEdit(moat.get('depth_m', ''))
        self._depth_edit.editingFinished.connect(self._commit)
        self._form_layout.addRow('Depth (m):', self._depth_edit)

        self._cond_moat_edit = _TextEdit(moat.get('condition', ''))
        self._cond_moat_edit.editingFinished.connect(self._commit)
        self._form_layout.addRow('Condition:', self._cond_moat_edit)

        is_seg = moat.get('is_river_segment', 'false').lower() == 'true'
        self._river_seg_check = QCheckBox('Natural river forms this barrier')
        self._river_seg_check.setChecked(is_seg)
        self._river_seg_check.toggled.connect(self._commit)
        self._form_layout.addRow('River segment:', self._river_seg_check)

        self._note_edit = _TextEdit(moat.get('note', ''))
        self._note_edit.editingFinished.connect(self._commit)
        self._form_layout.addRow('Note:', self._note_edit)

    def _commit(self) -> None:
        if not self._model or self._current_ordinal is None:
            return
        moat = self._moat_list[self._current_ordinal]
        moat['name'] = self._name_edit.text().strip()
        moat['source'] = self._source_edit.text().strip()
        moat['width_m'] = self._width_edit.text().strip()
        moat['depth_m'] = self._depth_edit.text().strip()
        moat['condition'] = self._cond_moat_edit.text().strip()
        moat['is_river_segment'] = 'true' if self._river_seg_check.isChecked() else 'false'
        moat['note'] = self._note_edit.text().strip()
        self._model.mark_dirty()
        self.populate()
        if self._current_ordinal is not None and self._current_ordinal < self._list.count():
            self._loading = True
            self._list.setCurrentRow(self._current_ordinal)
            self._loading = False


# ---------------------------------------------------------------------------
# Districts tab
# ---------------------------------------------------------------------------

class DistrictsTab(_BaseTab):
    def populate(self) -> None:
        if not self._model:
            return
        self._loading = True
        self._list.clear()
        self._dist_list = self._model.data.get('districts', [])
        for i, dist in enumerate(self._dist_list):
            name = dist.get('name', 'TODO')
            vis = dist.get('visibility', 'known')
            marker = _todo_marker(dist.get('description', 'TODO'))
            label = f'{marker}{dist.get("id", f"district {i+1}")}  {name}  [{vis}]'
            self._list.addItem(QListWidgetItem(label))
        self._loading = False
        if self._dist_list:
            self._list.setCurrentRow(0)

    def _on_row_changed(self, row: int) -> None:
        if self._loading or not self._model or row < 0 or row >= len(self._dist_list):
            return
        self._current_ordinal = row
        self._load_form(row)

    def _load_form(self, idx: int) -> None:
        self._clear_form()
        dist = self._dist_list[idx]

        self._name_edit = _TextEdit(dist.get('name', ''))
        self._name_edit.editingFinished.connect(self._commit)
        self._form_layout.addRow('Name:', self._name_edit)

        self._vis_combo = QComboBox()
        self._vis_combo.addItems(['known', 'local', 'hidden'])
        vis = dist.get('visibility', 'known')
        idx_vis = self._vis_combo.findText(vis)
        if idx_vis >= 0:
            self._vis_combo.setCurrentIndex(idx_vis)
        self._vis_combo.currentTextChanged.connect(self._commit)
        self._form_layout.addRow('Visibility:', self._vis_combo)

        self._desc_edit = _TextArea(dist.get('description', ''))
        self._desc_edit.setPlaceholderText('Describe this district...')
        self._desc_edit.setMaximumHeight(120)
        self._desc_edit.focusOutEvent = lambda e, orig=self._desc_edit.focusOutEvent: (
            self._commit(), orig(e)
        )
        self._form_layout.addRow('Description:', self._desc_edit)

        self._note_edit = _TextEdit(dist.get('note', ''))
        self._note_edit.editingFinished.connect(self._commit)
        self._form_layout.addRow('Note:', self._note_edit)

    def _commit(self) -> None:
        if not self._model or self._current_ordinal is None:
            return
        dist = self._dist_list[self._current_ordinal]
        dist['name'] = self._name_edit.text().strip()
        dist['visibility'] = self._vis_combo.currentText()
        dist['description'] = self._desc_edit.toPlainText().strip()
        dist['note'] = self._note_edit.text().strip()
        self._model.mark_dirty()
        self.populate()
        if self._current_ordinal is not None and self._current_ordinal < self._list.count():
            self._loading = True
            self._list.setCurrentRow(self._current_ordinal)
            self._loading = False


# ---------------------------------------------------------------------------
# POIs tab
# ---------------------------------------------------------------------------

def _build_wxx_poi_entries(model: 'AnnotationModel') -> list[dict]:
    """Build POI-like dicts from labeled .wxx features.

    Returns entries with source='wxx'.  Merges visibility and notes from the
    annotation dicts (feature_visibility, pois) where present.
    """
    if not model.wmap:
        return []
    orient = model.wmap.hex_orientation
    is_square = orient == 'SQUARE'
    fn = model.data.get('feature_names', {})
    fv = model.data.get('feature_visibility', {})

    # Build a lookup of annotation custom POIs by cell for quick note/desc merge
    custom_by_cell: dict = {}
    for poi in model.data.get('pois', []):
        if isinstance(poi.get('cell'), tuple):
            custom_by_cell[poi['cell']] = poi

    entries = []
    for f in model.wmap.features:
        if 'Coast' in f.type:
            continue
        raw_label = f.label.strip().replace('\n', ' ').replace('\r', '')
        if not raw_label:
            continue  # unlabeled features go in Feature Names section, not here

        cell = world_to_square(f.x, f.y) if is_square else world_to_hex(f.x, f.y, orient)
        name = fn.get(cell, raw_label)
        vis  = fv.get(cell, 'known')
        ann  = custom_by_cell.get(cell, {})

        # Shorten the Worldographer type path to the last segment
        short_type = f.type.split('/')[-1] if '/' in f.type else f.type

        entries.append({
            'source':    'wxx',
            'id':        f'wxx_{cell[0]}_{cell[1]}',
            'name':      name,
            'wxx_label': raw_label,
            'type':      short_type,
            'cell':      cell,
            'visibility': vis,
            'description': ann.get('description', ''),
            'note':      ann.get('note', ''),
        })

    entries.sort(key=lambda e: e['name'].lower())
    return entries


class POIsTab(_BaseTab):
    """Points of Interest.

    Shows two groups:
      ◈ labeled features from the .wxx (source='wxx') — name/type/cell read-only
      ● custom annotation POIs (source='custom') — fully editable
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        btn_bar = QWidget()
        btn_h = QHBoxLayout(btn_bar)
        btn_h.setContentsMargins(2, 2, 2, 2)
        add_btn = QPushButton('+ Add Custom POI')
        add_btn.setMaximumWidth(130)
        add_btn.setToolTip('Add a custom point of interest not already on the map')
        add_btn.clicked.connect(self._add_poi)
        remove_btn = QPushButton('Remove')
        remove_btn.setMaximumWidth(80)
        remove_btn.setToolTip('Remove the selected custom POI (map features cannot be removed here)')
        remove_btn.clicked.connect(self._remove_poi)
        btn_h.addWidget(add_btn)
        btn_h.addWidget(remove_btn)
        btn_h.addStretch()
        self.layout().insertWidget(0, btn_bar)

    def populate(self) -> None:
        if not self._model:
            return
        self._loading = True
        self._list.clear()
        from annotation_model import _fmt_cell

        # .wxx labeled features first
        wxx_entries  = _build_wxx_poi_entries(self._model)
        # Then annotation custom POIs
        custom_entries = [dict(p, source='custom') for p in self._model.data.get('pois', [])]

        self._poi_list = wxx_entries + custom_entries

        # Add a visual divider between the two groups if both are non-empty
        self._divider_row: Optional[int] = None
        if wxx_entries and custom_entries:
            self._divider_row = len(wxx_entries)

        for i, poi in enumerate(self._poi_list):
            if i == self._divider_row:
                divider = QListWidgetItem('── Custom POIs ──────────────────────────')
                divider.setFlags(Qt.NoItemFlags)
                divider.setForeground(QColor('#888888'))
                self._list.addItem(divider)

            src = poi.get('source', 'custom')
            name = poi.get('name', '')
            ptype = poi.get('type', 'landmark')
            cell = _fmt_cell(poi.get('cell', ''))
            if src == 'wxx':
                marker = '◈ '
            else:
                marker = _todo_marker(name)
            label = f'{marker}{cell}  {name}  [{ptype}]'
            item = QListWidgetItem(label)
            self._list.addItem(item)

        self._loading = False
        if self._poi_list:
            self._list.setCurrentRow(0)

    def _list_row_to_idx(self, row: int) -> int:
        """Map QListWidget row → _poi_list index (accounts for divider item)."""
        if self._divider_row is not None and row > self._divider_row:
            return row - 1   # divider occupies one row
        return row

    def _idx_to_list_row(self, idx: int) -> int:
        if self._divider_row is not None and idx >= self._divider_row:
            return idx + 1
        return idx

    def _on_row_changed(self, row: int) -> None:
        if self._loading or not self._model or row < 0:
            return
        idx = self._list_row_to_idx(row)
        if idx < 0 or idx >= len(self._poi_list):
            return
        # Skip if this is the divider row
        item = self._list.item(row)
        if item and not (item.flags() & Qt.ItemIsEnabled):
            return
        self._current_ordinal = idx
        self._load_form(idx)

    def _load_form(self, idx: int) -> None:
        self._clear_form()
        poi = self._poi_list[idx]
        from annotation_model import _fmt_cell
        src = poi.get('source', 'custom')
        is_wxx = src == 'wxx'

        def _ro_label(text: str) -> QLabel:
            lbl = QLabel(str(text))
            lbl.setStyleSheet('color: #888;')
            return lbl

        # Source badge
        src_lbl = _ro_label('◈ Map feature (from .wxx)' if is_wxx else '● Custom annotation POI')
        self._form_layout.addRow('Source:', src_lbl)
        self._form_layout.addRow(_hline())

        # Name
        if is_wxx:
            self._form_layout.addRow('Name:', _ro_label(poi.get('name', '')))
        else:
            self._name_edit = _TextEdit(poi.get('name', ''))
            self._name_edit.editingFinished.connect(self._commit)
            self._form_layout.addRow('Name:', self._name_edit)

        # Type
        if is_wxx:
            self._form_layout.addRow('Type:', _ro_label(poi.get('type', '')))
        else:
            self._type_edit = _TextEdit(poi.get('type', 'landmark'))
            self._type_edit.setPlaceholderText(
                'city | town | fort | watchtower | mine | shrine | landmark ...'
            )
            self._type_edit.editingFinished.connect(self._commit)
            self._form_layout.addRow('Type:', self._type_edit)

        # Cell
        if is_wxx:
            self._form_layout.addRow('Cell:', _ro_label(_fmt_cell(poi.get('cell', ''))))
        else:
            raw_cell = poi.get('cell', '')
            cell_str = _fmt_cell(raw_cell) if raw_cell else ''
            self._cell_edit = _TextEdit(cell_str)
            self._cell_edit.setPlaceholderText('(col, row)  e.g. (25, 18)')
            self._cell_edit.editingFinished.connect(self._commit)
            self._form_layout.addRow('Cell:', self._cell_edit)

        # Visibility — editable for both sources
        self._vis_combo = QComboBox()
        self._vis_combo.addItems(['known', 'local', 'hidden'])
        vis = poi.get('visibility', 'known')
        vi = self._vis_combo.findText(vis)
        if vi >= 0:
            self._vis_combo.setCurrentIndex(vi)
        self._vis_combo.currentTextChanged.connect(self._commit)
        self._form_layout.addRow('Visibility:', self._vis_combo)

        # Description — editable for both sources
        self._desc_edit = _TextArea(poi.get('description', ''))
        self._desc_edit.setPlaceholderText('Description visible to players...')
        self._desc_edit.setFixedHeight(80)
        self._desc_edit.focusOutEvent = lambda e, orig=self._desc_edit.focusOutEvent: (
            self._commit(), orig(e)
        )
        self._form_layout.addRow('Description:', self._desc_edit)

        # Note — editable for both sources
        self._note_edit = _TextEdit(poi.get('note', ''))
        self._note_edit.setPlaceholderText('GM-only notes...')
        self._note_edit.editingFinished.connect(self._commit)
        self._form_layout.addRow('Note (GM):', self._note_edit)

    def _add_poi(self) -> None:
        if not self._model:
            return
        pois = self._model.data.setdefault('pois', [])
        existing_ids = {p.get('id', '') for p in pois}
        n = len(pois) + 1
        while f'poi#{n}' in existing_ids:
            n += 1
        new_poi = {
            'id': f'poi#{n}',
            'name': 'New POI',
            'type': 'landmark',
            'cell': None,
            'visibility': 'known',
            'description': '',
            'note': '',
        }
        pois.append(new_poi)
        self._model.mark_dirty()
        self.populate()
        # Jump to the newly-added custom entry
        wxx_count = len(_build_wxx_poi_entries(self._model))
        new_idx = wxx_count + len(pois) - 1
        new_row = self._idx_to_list_row(new_idx)
        self._loading = True
        self._list.setCurrentRow(new_row)
        self._loading = False
        self._load_form(new_idx)
        if hasattr(self, '_name_edit'):
            self._name_edit.setFocus()
            self._name_edit.selectAll()

    def _remove_poi(self) -> None:
        if not self._model or self._current_ordinal is None:
            return
        poi = self._poi_list[self._current_ordinal]
        if poi.get('source') == 'wxx':
            QMessageBox.information(
                self, 'Cannot Remove',
                'Map features come from the .wxx file and cannot be removed here.\n'
                'Set Visibility to "hidden" to hide it from players instead.',
            )
            return
        pois = self._model.data.get('pois', [])
        # Find the matching entry in pois by id
        poi_id = poi.get('id')
        for i, p in enumerate(pois):
            if p.get('id') == poi_id:
                pois.pop(i)
                break
        self._model.mark_dirty()
        self._current_ordinal = None
        self._clear_form()
        self.populate()

    def _commit(self) -> None:
        if not self._model or self._current_ordinal is None:
            return
        poi = self._poi_list[self._current_ordinal]
        src = poi.get('source', 'custom')
        vis = self._vis_combo.currentText()
        desc = self._desc_edit.toPlainText().strip()
        note = self._note_edit.text().strip()

        if src == 'wxx':
            # Visibility → feature_visibility dict  (keyed by cell tuple)
            cell = poi.get('cell')
            if cell:
                if vis == 'known':
                    self._model.data.get('feature_visibility', {}).pop(cell, None)
                else:
                    self._model.data.setdefault('feature_visibility', {})[cell] = vis
            # Description / note → find or create a custom POI entry by cell
            if desc or note:
                pois = self._model.data.setdefault('pois', [])
                existing = next((p for p in pois if p.get('cell') == cell), None)
                if existing:
                    existing['description'] = desc
                    existing['note'] = note
                else:
                    pois.append({
                        'id': poi['id'],
                        'name': poi['name'],
                        'type': poi['type'],
                        'cell': cell,
                        'visibility': vis,
                        'description': desc,
                        'note': note,
                    })
            # Update local entry so it reflects without re-populate
            poi['visibility'] = vis
            poi['description'] = desc
            poi['note'] = note
        else:
            # Custom POI — update directly in data['pois']
            poi['name'] = self._name_edit.text().strip()
            poi['type'] = self._type_edit.text().strip()
            poi['visibility'] = vis
            poi['description'] = desc
            poi['note'] = note
            import re
            cell_text = self._cell_edit.text().strip()
            m = re.match(r'\(\s*(-?\d+)\s*,\s*(-?\d+)\s*\)', cell_text)
            if m:
                poi['cell'] = (int(m.group(1)), int(m.group(2)))
            elif cell_text:
                poi['cell'] = cell_text
            # Sync back into data['pois']
            pois = self._model.data.get('pois', [])
            poi_id = poi.get('id')
            for p in pois:
                if p.get('id') == poi_id:
                    p.update({k: v for k, v in poi.items() if k != 'source'})
                    break

        self._model.mark_dirty()
        # Only refresh the list label for the current row, no full re-populate
        from annotation_model import _fmt_cell
        row = self._idx_to_list_row(self._current_ordinal)
        item = self._list.item(row)
        if item:
            name = poi.get('name', '')
            ptype = poi.get('type', 'landmark')
            cell = _fmt_cell(poi.get('cell', ''))
            marker = '◈ ' if src == 'wxx' else _todo_marker(name)
            item.setText(f'{marker}{cell}  {name}  [{ptype}]')


# ---------------------------------------------------------------------------
# Entity Defs tab (Linear Feature Details)
# ---------------------------------------------------------------------------

def _collect_all_refs(model: 'AnnotationModel') -> set:
    """Return all ref IDs used in road/river conditions."""
    refs = set()
    for section in ('roads', 'rivers'):
        for entry in model.data.get(section, {}).values():
            for cond in entry.get('conditions', {}).values():
                for r in (cond.get('ref', []) or []):
                    if isinstance(r, str):
                        refs.add(r)
    return refs


class EntityDefsTab(_BaseTab):
    """Shows defined entity refs AND refs used in conditions but not yet defined."""

    # Default field templates per ref prefix so new stubs have sensible fields
    _STUB_FIELDS = {
        'toll':    [('name', ''), ('type', 'tollbooth'), ('controlled_by', ''),
                    ('fee', ''), ('note', '')],
        'bridge':  [('name', ''), ('type', 'bridge'), ('material', 'stone'),
                    ('length_m', ''), ('note', '')],
        'ford':    [('name', ''), ('type', 'ford'), ('difficulty', ''), ('note', '')],
        'gate':    [('name', ''), ('type', 'gatehouse'), ('controlled_by', ''),
                    ('condition', 'intact'), ('note', '')],
        'ferry':   [('name', ''), ('type', 'ferry'), ('note', '')],
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        # Button bar above the list
        btn_bar = QWidget()
        btn_h = QHBoxLayout(btn_bar)
        btn_h.setContentsMargins(2, 2, 2, 2)
        add_btn = QPushButton('+ Add Ref')
        add_btn.setMaximumWidth(90)
        add_btn.clicked.connect(self._add_ref)
        refresh_btn = QPushButton('↻ Refresh')
        refresh_btn.setMaximumWidth(80)
        refresh_btn.setToolTip(
            'Re-scan all conditions in memory for referenced refs.\n'
            'Use this after editing road/river conditions without reloading the file.'
        )
        refresh_btn.clicked.connect(self._refresh)
        btn_h.addWidget(add_btn)
        btn_h.addWidget(refresh_btn)
        btn_h.addStretch()
        self.layout().insertWidget(0, btn_bar)

    def populate(self) -> None:
        if not self._model:
            return
        self._loading = True
        self._list.clear()
        linear = self._model.data.get('linear_details', {})
        all_used_refs = _collect_all_refs(self._model)
        undefined_refs = sorted(all_used_refs - set(linear.keys()))

        # Build the master list: defined first, then undefined stubs
        self._ref_ids = sorted(linear.keys()) + undefined_refs
        self._undefined_set = set(undefined_refs)

        for ref_id in self._ref_ids:
            if ref_id in self._undefined_set:
                label = f'★ {ref_id:<14}  (not yet defined — click to fill in)'
            else:
                details = linear[ref_id]
                name = details.get('name', '')
                dtype = details.get('type', '')
                label = f'{ref_id:<16}  {name}  [{dtype}]'
            self._list.addItem(QListWidgetItem(label))

        self._loading = False
        if self._ref_ids:
            self._list.setCurrentRow(0)

    def _on_row_changed(self, row: int) -> None:
        if self._loading or not self._model or row < 0 or row >= len(self._ref_ids):
            return
        self._current_ordinal = row
        self._load_form(row)

    def _find_references(self, ref_id: str) -> list[str]:
        """Return human-readable strings for every road/river that uses ref_id."""
        hits = []
        if not self._model:
            return hits
        from annotation_model import _fmt_cell
        for section, prefix in [('roads', 'road'), ('rivers', 'river')]:
            for ordinal, entry in sorted(self._model.data.get(section, {}).items()):
                for cell, cond in entry.get('conditions', {}).items():
                    cond_refs = cond.get('ref', [])
                    if isinstance(cond_refs, str):
                        cond_refs = [cond_refs]
                    if ref_id in cond_refs:
                        name = entry.get('name', '')
                        label_name = f' "{name}"' if name and name != 'TODO' else ''
                        hits.append(f'{prefix} {ordinal}{label_name}  @ {_fmt_cell(cell)}')
                        break  # only list each road/river once
        return hits

    def _load_form(self, idx: int) -> None:
        self._clear_form()
        ref_id = self._ref_ids[idx]
        linear = self._model.data.get('linear_details', {})
        is_new = ref_id in self._undefined_set

        id_lbl = QLabel(f'{ref_id}{"   ★ undefined — fill in to define it" if is_new else ""}')
        id_lbl.setFont(QFont('Consolas', 10))
        if is_new:
            id_lbl.setStyleSheet('color: #cc7700;')
        self._form_layout.addRow('Ref ID:', id_lbl)
        self._form_layout.addRow(_hline())

        # Determine fields: either existing values or a sensible stub template
        if is_new:
            prefix = ref_id.split('#')[0].lower() if '#' in ref_id else ref_id.lower()
            stub = self._STUB_FIELDS.get(prefix, [('name', ''), ('type', ''), ('note', '')])
            details = dict(stub)
        else:
            details = dict(linear.get(ref_id, {}))

        self._field_edits: dict[str, QLineEdit] = {}
        for k, v in details.items():
            edit = _TextEdit(str(v))
            edit.editingFinished.connect(self._commit)
            self._form_layout.addRow(f'{k}:', edit)
            self._field_edits[k] = edit

        # --- Referenced by ---
        back_refs = self._find_references(ref_id)
        self._form_layout.addRow(_hline())
        if back_refs:
            ref_text = '\n'.join(back_refs)
        else:
            ref_text = '(not referenced by any road or river condition)'
        ref_display = _TextArea()
        ref_display.setPlainText(ref_text)
        ref_display.setReadOnly(True)
        # Size to fit content: ~20px per line, min 40, max 120
        line_count = max(1, len(back_refs))
        ref_display.setFixedHeight(min(120, max(44, line_count * 21 + 10)))
        ref_display.setStyleSheet(
            'color: #888; font-style: italic; background: transparent; border: none;'
        )
        self._form_layout.addRow('Referenced by:', ref_display)

    def _refresh(self) -> None:
        """Re-scan in-memory conditions and repopulate the list."""
        if not self._model:
            return
        # Remember which ref was selected so we can restore it
        prev_ref = self._ref_ids[self._current_ordinal] if (
            self._current_ordinal is not None and self._ref_ids
        ) else None
        self.populate()
        if prev_ref and prev_ref in self._ref_ids:
            idx = self._ref_ids.index(prev_ref)
            self._loading = True
            self._list.setCurrentRow(idx)
            self._loading = False
            self._load_form(idx)

    def _add_ref(self) -> None:
        """Prompt for a new ref ID and add a blank stub."""
        if not self._model:
            return
        from PySide6.QtWidgets import QInputDialog
        ref_id, ok = QInputDialog.getText(
            self, 'Add Entity Ref',
            'Enter ref ID (e.g. bridge#3, toll#2, gatehouse#1):',
        )
        if not ok or not ref_id.strip():
            return
        ref_id = ref_id.strip()
        linear = self._model.data.setdefault('linear_details', {})
        if ref_id not in linear:
            prefix = ref_id.split('#')[0].lower() if '#' in ref_id else ref_id.lower()
            stub = self._STUB_FIELDS.get(prefix, [('name', ''), ('type', ''), ('note', '')])
            linear[ref_id] = dict(stub)
            self._model.mark_dirty()
        self.populate()
        if ref_id in self._ref_ids:
            self._loading = True
            self._list.setCurrentRow(self._ref_ids.index(ref_id))
            self._loading = False
            self._load_form(self._ref_ids.index(ref_id))

    def _commit(self) -> None:
        if not self._model or self._current_ordinal is None:
            return
        ref_id = self._ref_ids[self._current_ordinal]
        linear = self._model.data.setdefault('linear_details', {})
        # Commit always writes — this promotes undefined stubs to defined ones
        entry = {}
        for k, edit in self._field_edits.items():
            entry[k] = edit.text().strip()
        linear[ref_id] = entry
        # Remove from undefined set if it was there
        self._undefined_set.discard(ref_id)
        self._model.mark_dirty()
        # Refresh list label to show it's now defined
        self.populate()
        if ref_id in self._ref_ids:
            idx = self._ref_ids.index(ref_id)
            self._loading = True
            self._list.setCurrentRow(idx)
            self._loading = False


# ---------------------------------------------------------------------------
# Intent tab (plain text editing)
# ---------------------------------------------------------------------------

class IntentTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._model: Optional[AnnotationModel] = None
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel('Project styling:'))
        self._project_edit = _TextEdit()
        self._project_edit.setPlaceholderText('default | aethelmark')
        self._project_edit.editingFinished.connect(self._commit)
        layout.addWidget(self._project_edit)

        layout.addWidget(_hline())
        layout.addWidget(QLabel('Narrative notes (one bullet per line, no leading "-"):'))
        self._narrative_edit = _TextArea()
        self._narrative_edit.setPlaceholderText(
            'Describe the map\'s intended use, design pressures, etc.'
        )
        self._narrative_edit.focusOutEvent = lambda e, orig=self._narrative_edit.focusOutEvent: (
            self._commit(), orig(e)
        )
        layout.addWidget(self._narrative_edit)

    def set_model(self, model: AnnotationModel) -> None:
        self._model = model
        self._project_edit.setText(model.data.get('project', 'default'))
        narrative = model.data.get('intent_narrative', [])
        self._narrative_edit.setPlainText('\n'.join(narrative))

    def _commit(self) -> None:
        if not self._model:
            return
        self._model.data['project'] = self._project_edit.text().strip() or 'default'
        text = self._narrative_edit.toPlainText().strip()
        self._model.data['intent_narrative'] = [
            line.strip().lstrip('- ').strip()
            for line in text.splitlines()
            if line.strip()
        ]
        self._model.mark_dirty()


# ---------------------------------------------------------------------------
# Main window
# ---------------------------------------------------------------------------

class MainWindow(QMainWindow):
    def __init__(self, initial_wxx: Optional[str] = None):
        super().__init__()
        self.setWindowTitle('Worldographer Annotation Editor')
        self.resize(1400, 860)

        self._model = AnnotationModel()
        self._last_render_time: Optional[str] = None

        self._build_ui()
        self._update_status()

        if initial_wxx:
            self._load_file(initial_wxx)

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        # Central splitter
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self._splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self._splitter)

        # Left: tabs
        self._tabs = QTabWidget()
        self._tabs.setMinimumWidth(380)

        self._roads_tab = RoadsTab()
        self._rivers_tab = RiversTab()
        self._walls_tab = WallsTab()
        self._moat_tab = MoatTab()
        self._districts_tab = DistrictsTab()
        self._pois_tab = POIsTab()
        self._entity_tab = EntityDefsTab()
        self._intent_tab = IntentTab()

        self._tabs.addTab(self._roads_tab, 'Roads')
        self._tabs.addTab(self._rivers_tab, 'Rivers')
        self._tabs.addTab(self._walls_tab, 'Walls')
        self._tabs.addTab(self._moat_tab, 'Moat')
        self._tabs.addTab(self._districts_tab, 'Districts')
        self._tabs.addTab(self._pois_tab, 'POIs')
        self._tabs.addTab(self._entity_tab, 'Entity Defs')
        self._tabs.addTab(self._intent_tab, 'Intent')

        self._splitter.addWidget(self._tabs)

        # Right: SVG viewer + controls strip
        viewer_container = QWidget()
        viewer_layout = QVBoxLayout(viewer_container)
        viewer_layout.setContentsMargins(0, 0, 0, 0)
        viewer_layout.setSpacing(2)

        # Viewer controls strip
        ctrl_strip = QWidget()
        ctrl_h = QHBoxLayout(ctrl_strip)
        ctrl_h.setContentsMargins(4, 2, 4, 2)

        self._zoom_label = QLabel('Zoom: 100%')
        self._zoom_label.setMinimumWidth(80)

        fit_btn = QPushButton('Fit')
        fit_btn.setMaximumWidth(40)
        fit_btn.setToolTip('Reset zoom to fit map in window (or double-click map)')
        fit_btn.clicked.connect(self._fit_view)

        self._toggle_btn = QPushButton('Hide Map')
        self._toggle_btn.setMaximumWidth(80)
        self._toggle_btn.setCheckable(True)
        self._toggle_btn.toggled.connect(self._toggle_viewer)

        opacity_label = QLabel('Opacity:')
        self._opacity_slider = QSlider(Qt.Horizontal)
        self._opacity_slider.setRange(10, 100)
        self._opacity_slider.setValue(100)
        self._opacity_slider.setMaximumWidth(100)
        self._opacity_slider.valueChanged.connect(self._on_opacity_changed)

        ctrl_h.addWidget(self._zoom_label)
        ctrl_h.addWidget(fit_btn)
        ctrl_h.addStretch()
        ctrl_h.addWidget(opacity_label)
        ctrl_h.addWidget(self._opacity_slider)
        ctrl_h.addWidget(self._toggle_btn)

        viewer_layout.addWidget(ctrl_strip)

        self._svg_viewer = SvgViewer()
        self._svg_viewer.zoom_changed.connect(self._on_zoom_changed)
        viewer_layout.addWidget(self._svg_viewer)

        self._splitter.addWidget(viewer_container)

        # Split roughly half-half
        self._splitter.setSizes([560, 840])
        self._splitter.setCollapsible(0, False)
        self._splitter.setCollapsible(1, True)

        # Toolbar
        self._build_toolbar()

        # Status bar
        self._status_file = QLabel('No file loaded')
        self._status_todos = QLabel('')
        self._status_render = QLabel('')
        sb = self.statusBar()
        sb.addWidget(self._status_file, 2)
        sb.addPermanentWidget(self._status_todos)
        sb.addPermanentWidget(self._status_render)

    def _build_toolbar(self) -> None:
        tb = self.addToolBar('Main')
        tb.setMovable(False)
        tb.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        # Split button: left side opens dialog, right side drops recent files
        self._open_btn = QToolButton()
        self._open_btn.setText('Open .wxx')
        self._open_btn.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self._open_btn.setPopupMode(QToolButton.MenuButtonPopup)
        self._open_btn.setShortcut('Ctrl+O')
        self._open_btn.clicked.connect(self._open_file_dialog)
        self._recent_menu = QMenu(self._open_btn)
        self._open_btn.setMenu(self._recent_menu)
        self._rebuild_recent_menu()
        tb.addWidget(self._open_btn)

        tb.addSeparator()

        self._save_action = QAction('Save', self)
        self._save_action.setShortcut('Ctrl+S')
        self._save_action.triggered.connect(self._save)
        self._save_action.setEnabled(False)
        tb.addAction(self._save_action)

        self._render_action = QAction('Render SVG', self)
        self._render_action.setShortcut('Ctrl+R')
        self._render_action.triggered.connect(self._render)
        self._render_action.setEnabled(False)
        tb.addAction(self._render_action)

        tb.addSeparator()

        regen_action = QAction('Regenerate Scaffold', self)
        regen_action.setToolTip('Back up existing .annotations.md and regenerate from .wxx')
        regen_action.triggered.connect(self._regenerate)
        regen_action.setEnabled(False)
        self._regen_action = regen_action
        tb.addAction(regen_action)

        tb.addSeparator()

        quit_action = QAction('Quit', self)
        quit_action.setShortcut('Ctrl+Q')
        quit_action.setToolTip('Exit the editor (Ctrl+Q)  —  prompts to save if there are unsaved changes')
        quit_action.triggered.connect(self.close)   # close() triggers closeEvent
        tb.addAction(quit_action)

    # ------------------------------------------------------------------
    # File operations
    # ------------------------------------------------------------------

    def _rebuild_recent_menu(self) -> None:
        """Rebuild the dropdown attached to the Open button."""
        self._recent_menu.clear()
        recent = _load_recent()
        if not recent:
            act = self._recent_menu.addAction('(no recent files)')
            act.setEnabled(False)
        else:
            for path in recent:
                name = os.path.basename(path)
                folder = os.path.basename(os.path.dirname(path))
                act = self._recent_menu.addAction(f'{name}  —  {folder}')
                act.setToolTip(path)
                act.setEnabled(os.path.exists(path))
                act.triggered.connect(lambda checked=False, p=path: self._load_file(p))
            self._recent_menu.addSeparator()
            clear_act = self._recent_menu.addAction('Clear Recent Files')
            clear_act.triggered.connect(self._clear_recent_files)

    def _push_recent(self, wxx_path: str) -> None:
        recent = _load_recent()
        if wxx_path in recent:
            recent.remove(wxx_path)
        recent.insert(0, wxx_path)
        _save_recent(recent[:10])
        self._rebuild_recent_menu()

    def _clear_recent_files(self) -> None:
        _save_recent([])
        self._rebuild_recent_menu()

    def _open_file_dialog(self) -> None:
        if self._model.is_dirty:
            resp = QMessageBox.question(
                self, 'Unsaved Changes',
                'You have unsaved changes. Open a new file anyway?',
                QMessageBox.Yes | QMessageBox.No,
            )
            if resp != QMessageBox.Yes:
                return
        path, _ = QFileDialog.getOpenFileName(
            self, 'Open Worldographer Map', '', 'Worldographer Maps (*.wxx)'
        )
        if path:
            self._load_file(path)

    def _load_file(self, wxx_path: str) -> None:
        self.setWindowTitle(f'Loading — {os.path.basename(wxx_path)}...')
        QApplication.processEvents()
        try:
            warnings = self._model.load(wxx_path)
        except Exception as exc:
            QMessageBox.critical(self, 'Load Error', f'Failed to load:\n{exc}')
            self.setWindowTitle('Worldographer Annotation Editor')
            return

        if warnings:
            QMessageBox.information(self, 'Load Notices', '\n'.join(warnings))

        self._push_recent(wxx_path)
        self._populate_all_tabs()
        self._save_action.setEnabled(True)
        self._render_action.setEnabled(True)
        self._regen_action.setEnabled(True)

        # Load existing SVG if present
        if self._model.svg_path and os.path.exists(self._model.svg_path):
            self._svg_viewer.load_svg(self._model.svg_path)
            mtime = os.path.getmtime(self._model.svg_path)
            self._last_render_time = datetime.fromtimestamp(mtime).strftime('%H:%M')

        self.setWindowTitle(
            f'Worldographer Annotation Editor — {os.path.basename(wxx_path)}'
        )
        self._update_status()

    def _populate_all_tabs(self) -> None:
        for tab in (
            self._roads_tab, self._rivers_tab, self._walls_tab,
            self._moat_tab, self._districts_tab, self._pois_tab,
            self._entity_tab,
        ):
            tab.set_model(self._model)
        self._intent_tab.set_model(self._model)

    def _save(self) -> None:
        if not self._model.wxx_path:
            return
        try:
            self._model.save()
        except Exception as exc:
            QMessageBox.critical(self, 'Save Error', f'Failed to save:\n{exc}')
            return
        self._update_status()
        self.statusBar().showMessage('Saved.', 3000)

    def _render(self) -> None:
        if not self._model.wxx_path:
            return
        # Auto-save before rendering
        if self._model.is_dirty:
            self._save()

        self.statusBar().showMessage('Rendering SVG...')
        QApplication.processEvents()

        success, output = self._model.render()
        if not success:
            QMessageBox.warning(
                self, 'Render Failed',
                f'wxx_to_svg.py returned an error:\n\n{output[:2000]}',
            )
            self.statusBar().showMessage('Render failed.', 5000)
            return

        # Reload SVG
        if self._model.svg_path:
            self._svg_viewer.reload()
        self._last_render_time = datetime.now().strftime('%H:%M')
        self.statusBar().showMessage('Render complete.', 4000)
        self._update_status()

        # Show any warnings from render output
        if 'WARNING' in output or 'warning' in output.lower():
            QMessageBox.information(
                self, 'Render Warnings',
                f'Render completed with notices:\n\n{output[:3000]}',
            )

    def _regenerate(self) -> None:
        if not self._model.wxx_path:
            return
        resp = QMessageBox.question(
            self, 'Regenerate Scaffold',
            'This will back up the current .annotations.md to .annotations.previous.md '
            'and generate a fresh scaffold.\n\nYour edits will be moved to the .previous file.\n\n'
            'Continue?',
            QMessageBox.Yes | QMessageBox.No,
        )
        if resp != QMessageBox.Yes:
            return
        import shutil
        annot = self._model.annot_path
        prev = annot.replace('.annotations.md', '.annotations.previous.md')
        if os.path.exists(annot):
            shutil.copy2(annot, prev)
        # Remove existing so load() scaffolds fresh
        if os.path.exists(annot):
            os.remove(annot)
        self._load_file(self._model.wxx_path)
        self.statusBar().showMessage(f'Scaffold regenerated. Previous saved to {os.path.basename(prev)}', 6000)

    # ------------------------------------------------------------------
    # Viewer controls
    # ------------------------------------------------------------------

    def _fit_view(self) -> None:
        self._svg_viewer.fit_to_view()

    def _toggle_viewer(self, hidden: bool) -> None:
        if hidden:
            self._splitter.setSizes([self._splitter.width(), 0])
            self._toggle_btn.setText('Show Map')
        else:
            total = self._splitter.width()
            self._splitter.setSizes([total // 2, total // 2])
            self._toggle_btn.setText('Hide Map')

    def _on_zoom_changed(self, scale: float) -> None:
        self._zoom_label.setText(f'Zoom: {int(scale * 100)}%')

    def _on_opacity_changed(self, value: int) -> None:
        self._svg_viewer.set_opacity(value / 100.0)

    # ------------------------------------------------------------------
    # Status bar
    # ------------------------------------------------------------------

    def _update_status(self) -> None:
        if self._model.wxx_path:
            fname = os.path.basename(self._model.annot_path or '')
            dirty = ' *' if self._model.is_dirty else ''
            self._status_file.setText(f'{fname}{dirty}')

            todos = self._model.get_todo_count()
            if todos:
                self._status_todos.setText(f'  {todos} TODOs  ')
                self._status_todos.setStyleSheet('color: #cc7700;')
            else:
                self._status_todos.setText('  All filled  ')
                self._status_todos.setStyleSheet('color: #44aa44;')

            if self._last_render_time:
                self._status_render.setText(f'  Last render: {self._last_render_time}  ')
            else:
                self._status_render.setText('  Not yet rendered  ')
        else:
            self._status_file.setText('No file loaded')
            self._status_todos.setText('')
            self._status_render.setText('')

    def closeEvent(self, event) -> None:
        if self._model.is_dirty:
            box = QMessageBox(self)
            box.setWindowTitle('Unsaved Changes')
            box.setText('You have unsaved changes to the annotation file.')
            box.setInformativeText('Save before closing?')
            save_btn    = box.addButton('Save and Exit',     QMessageBox.AcceptRole)
            discard_btn = box.addButton("Don't Save",        QMessageBox.DestructiveRole)
            cancel_btn  = box.addButton('Cancel',            QMessageBox.RejectRole)
            box.setDefaultButton(save_btn)
            box.setEscapeButton(cancel_btn)
            box.exec()
            clicked = box.clickedButton()
            if clicked == save_btn:
                self._save()
                event.accept()
            elif clicked == discard_btn:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    app = QApplication(sys.argv)
    app.setApplicationName('Worldographer Annotation Editor')

    # Dark-ish palette to match typical worldbuilding vibes
    app.setStyle('Fusion')

    initial = sys.argv[1] if len(sys.argv) > 1 else None
    win = MainWindow(initial_wxx=initial)
    win.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
