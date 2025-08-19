# radial_transition.py
import math
from PyQt5.QtCore import Qt, QPropertyAnimation, pyqtProperty, QPoint
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtWidgets import QWidget, QStackedWidget


class RadialTransition(QWidget):
    def __init__(self, parent: QStackedWidget):
        super().__init__(parent)
        self._radius = 0.0
        self._center = None  # QPoint; defaulted at start()
        self._anim = None

        # overlay config
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setGeometry(parent.rect())
        self.hide()

        # color of the circle (opaque black)
        self.color = QColor(0, 0, 0)

    # ---- animated property ----
    def _get_radius(self) -> float:
        return self._radius

    def _set_radius(self, r: float):
        self._radius = r
        self.update()  # repaint

    radius = pyqtProperty(float, fget=_get_radius, fset=_set_radius)

    # ---- painting ----
    def paintEvent(self, _):
        if self._radius <= 0 or self._center is None:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        p.setPen(Qt.NoPen)
        p.setBrush(self.color)
        # draw centered circle
        p.drawEllipse(self._center, int(self._radius), int(self._radius))
        p.end()

    # ---- API ----
    def start(self, center: QPoint = None, duration: int = 600,
              reverse: bool = False,
              mid_callback=None,
              finished_callback=None):
        """
        Animate:
          - reverse=False: expand from 0 -> max; on finish -> mid_callback(), then finished_callback()
          - reverse=True : shrink from max -> 0; on finish -> hide() then finished_callback()
        """
        # ensure we cover the parent
        self.setGeometry(self.parent().rect())
        self.raise_()
        self.show()

        # default center to middle of parent if not provided
        if center is None:
            r = self.rect()
            self._center = QPoint(r.center().x(), r.center().y())
        else:
            self._center = center

        max_r = int(math.hypot(self.width(), self.height()))

        # set up animation
        if self._anim is not None:
            self._anim.stop()
            self._anim.deleteLater()
            self._anim = None

        self._anim = QPropertyAnimation(self, b"radius", self)
        self._anim.setDuration(max(1, duration))

        if reverse:
            self._set_radius(float(max_r))
            self._anim.setStartValue(float(max_r))
            self._anim.setEndValue(0.0)

            def on_done():
                self.hide()
                if callable(finished_callback):
                    finished_callback()

            self._anim.finished.connect(on_done)

        else:
            self._set_radius(0.0)
            self._anim.setStartValue(0.0)
            self._anim.setEndValue(float(max_r))

            def on_done():
                # call mid (e.g., switch page) first
                if callable(mid_callback):
                    mid_callback()
                # then any follow-up (e.g., start reverse)
                if callable(finished_callback):
                    finished_callback()

            self._anim.finished.connect(on_done)

        self._anim.start()
