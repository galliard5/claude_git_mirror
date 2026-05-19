"""
svg_viewer.py — SVG viewer widget with pan and zoom.

A self-contained QWidget that renders an SVG file, supports:
  - Mouse drag to pan
  - Scroll wheel to zoom (centered on cursor)
  - Fit-to-view reset
  - Opacity slider for overlay blending
  - show/hide (caller responsibility: just call hide()/show())

Used by worldographer_editor.py.
"""
from __future__ import annotations
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import QWidget, QSizePolicy
from PySide6.QtCore import Qt, QPointF, QRectF, QSizeF, Signal
from PySide6.QtGui import QPainter, QColor, QPen, QFont
from PySide6.QtSvg import QSvgRenderer


class SvgViewer(QWidget):
    """Pan-zoomable SVG canvas.

    Usage:
        viewer = SvgViewer()
        viewer.load_svg('/path/to/map.svg')

    Signals:
        zoom_changed(float) — emitted when zoom level changes
    """

    zoom_changed = Signal(float)

    # Zoom limits
    ZOOM_MIN = 0.05
    ZOOM_MAX = 20.0
    ZOOM_STEP = 0.15   # fraction of current scale per wheel notch

    def __init__(self, parent=None):
        super().__init__(parent)
        self._renderer = QSvgRenderer(self)
        self._loaded: bool = False
        self._svg_path: Optional[str] = None

        # View state
        self._scale: float = 1.0
        self._offset: QPointF = QPointF(0.0, 0.0)
        self._drag_last: Optional[QPointF] = None
        self._opacity: float = 1.0

        self.setMouseTracking(True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(200, 200)
        self.setFocusPolicy(Qt.WheelFocus)
        self.setBackgroundRole(self.backgroundRole())

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load_svg(self, path: str) -> bool:
        """Load an SVG file.  Returns True on success."""
        if not Path(path).exists():
            self._loaded = False
            self._svg_path = None
            self.update()
            return False
        ok = self._renderer.load(path)
        if ok:
            self._loaded = True
            self._svg_path = path
            self.fit_to_view()
        else:
            self._loaded = False
        self.update()
        return ok

    def reload(self) -> bool:
        """Reload the current SVG file from disk (after re-render)."""
        if self._svg_path:
            return self.load_svg(self._svg_path)
        return False

    def fit_to_view(self) -> None:
        """Reset zoom/pan so the entire SVG fits in the widget."""
        if not self._loaded:
            return
        svgw = self._renderer.defaultSize().width()
        svgh = self._renderer.defaultSize().height()
        if svgw <= 0 or svgh <= 0:
            return
        scale_x = self.width() / svgw
        scale_y = self.height() / svgh
        self._scale = min(scale_x, scale_y) * 0.95   # 5% margin
        # Center
        fitted_w = svgw * self._scale
        fitted_h = svgh * self._scale
        self._offset = QPointF(
            (self.width() - fitted_w) / 2.0,
            (self.height() - fitted_h) / 2.0,
        )
        self.zoom_changed.emit(self._scale)
        self.update()

    def zoom_to(self, scale: float, center: Optional[QPointF] = None) -> None:
        """Zoom to an absolute scale, optionally keeping a point fixed."""
        old_scale = self._scale
        self._scale = max(self.ZOOM_MIN, min(self.ZOOM_MAX, scale))
        if center is not None:
            # Adjust offset so `center` stays at the same widget position
            ratio = self._scale / old_scale
            self._offset = center - (center - self._offset) * ratio
        self.zoom_changed.emit(self._scale)
        self.update()

    def set_opacity(self, opacity: float) -> None:
        """Set rendering opacity (0.0 – 1.0)."""
        self._opacity = max(0.0, min(1.0, opacity))
        self.update()

    @property
    def current_scale(self) -> float:
        return self._scale

    @property
    def svg_path(self) -> Optional[str]:
        return self._svg_path

    # ------------------------------------------------------------------
    # Qt event overrides
    # ------------------------------------------------------------------

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

        # Background
        painter.fillRect(self.rect(), QColor('#2b2b2b'))

        if not self._loaded:
            painter.setPen(QColor('#888888'))
            painter.setFont(QFont('Sans', 11))
            painter.drawText(
                self.rect(),
                Qt.AlignCenter,
                'No SVG loaded.\nRender the map to see it here.',
            )
            return

        svgw = self._renderer.defaultSize().width()
        svgh = self._renderer.defaultSize().height()

        painter.translate(self._offset)
        painter.scale(self._scale, self._scale)

        if self._opacity < 1.0:
            painter.setOpacity(self._opacity)

        self._renderer.render(painter, QRectF(0, 0, svgw, svgh))

    def resizeEvent(self, event):
        # When the widget first gets a real size, fit the SVG
        if self._loaded and event.oldSize().width() <= 0:
            self.fit_to_view()
        super().resizeEvent(event)

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if delta == 0:
            return
        # Zoom centered on cursor position
        cursor = QPointF(event.position())
        factor = 1.0 + self.ZOOM_STEP * (1 if delta > 0 else -1)
        self.zoom_to(self._scale * factor, center=cursor)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_last = QPointF(event.position())
            self.setCursor(Qt.ClosedHandCursor)

    def mouseMoveEvent(self, event):
        if self._drag_last is not None:
            delta = QPointF(event.position()) - self._drag_last
            self._offset += delta
            self._drag_last = QPointF(event.position())
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_last = None
            self.setCursor(Qt.ArrowCursor)

    def mouseDoubleClickEvent(self, event):
        """Double-click resets to fit-to-view."""
        self.fit_to_view()

    def keyPressEvent(self, event):
        key = event.key()
        if key in (Qt.Key_Plus, Qt.Key_Equal):
            center = QPointF(self.width() / 2, self.height() / 2)
            self.zoom_to(self._scale * (1 + self.ZOOM_STEP), center)
        elif key == Qt.Key_Minus:
            center = QPointF(self.width() / 2, self.height() / 2)
            self.zoom_to(self._scale * (1 - self.ZOOM_STEP), center)
        elif key in (Qt.Key_0, Qt.Key_F):
            self.fit_to_view()
        elif key == Qt.Key_Left:
            self._offset += QPointF(-20, 0)
            self.update()
        elif key == Qt.Key_Right:
            self._offset += QPointF(20, 0)
            self.update()
        elif key == Qt.Key_Up:
            self._offset += QPointF(0, -20)
            self.update()
        elif key == Qt.Key_Down:
            self._offset += QPointF(0, 20)
            self.update()
        else:
            super().keyPressEvent(event)
