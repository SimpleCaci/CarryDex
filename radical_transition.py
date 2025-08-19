import math
from PyQt5.QtCore import Qt, QPropertyAnimation, pyqtProperty, QPoint, QTimer
from PyQt5.QtGui import QPainter, QBrush
from PyQt5.QtWidgets import QWidget


class RadialTransition(QWidget):
    def __init__(self, parent=None, color=Qt.black):
        super().__init__(parent)
        self._radius = 0
        self._center = QPoint(0, 0)
        self.color = color
        self.anim = None

        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(parent.rect())
        self.hide()

    # ---- Radius property (for animation) ----
    def getRadius(self):
        return self._radius

    def setRadius(self, r):
        self._radius = r
        self.update()

    radius = pyqtProperty(int, fget=getRadius, fset=setRadius)

    # ---- Painting ----
    def paintEvent(self, event):
        if self._radius > 0:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setBrush(QBrush(self.color))
            painter.setPen(Qt.NoPen)

            painter.drawEllipse(self._center, self._radius, self._radius)

    # ---- Transition start ----
    def start(self, center, duration=600, reverse=False, finished_callback=None, mid_callback=None):
        """
        Animate circle growing (reverse=False) or shrinking (reverse=True).
        mid_callback is called at max expansion (for page switching).
        """
        if isinstance(center, tuple):
            center = QPoint(center[0], center[1])

        self._center = center
        self.show()

        max_radius = int(math.hypot(self.width(), self.height()))
        self.anim = QPropertyAnimation(self, b"radius")
        self.anim.setDuration(duration)

        if reverse:
            self.setRadius(max_radius)
            self.anim.setStartValue(max_radius)
            self.anim.setEndValue(0)

            # Auto-hide when finished
            self.anim.finished.connect(self.hide)
            if finished_callback:
                self.anim.finished.connect(finished_callback)

        else:  # Growing transition
            self.setRadius(0)
            self.anim.setStartValue(0)
            self.anim.setEndValue(max_radius)

            if finished_callback:
                self.anim.finished.connect(finished_callback)

            # Call mid_callback at max radius (just before reversing)
            if mid_callback:
                QTimer.singleShot(duration, mid_callback)

        self.anim.start()
