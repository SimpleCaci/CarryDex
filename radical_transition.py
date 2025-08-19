# radical_transition.py
from PyQt5.QtCore import Qt, QRect, QPropertyAnimation, pyqtProperty
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtWidgets import QWidget
import math

class RadialTransition(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._radius = 0
        self._center = (0, 0)
        self.color = QColor(30, 30, 30)  # background circle color
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.hide()

    def setRadius(self, r):
        self._radius = r
        self.update()

    def getRadius(self):
        return self._radius

    radius = pyqtProperty(int, fget=getRadius, fset=setRadius)

    def paintEvent(self, event):
        if self.isVisible():
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setBrush(self.color)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(self._center[0]-self._radius,
                                self._center[1]-self._radius,
                                self._radius*2, self._radius*2)

    def start(self, center, duration=600, reverse=False, finished_callback=None):
        """Animate circle growing (reverse=False) or shrinking (reverse=True)"""
        self._center = center
        self.show()

        max_radius = int(math.hypot(self.width(), self.height()))

        self.anim = QPropertyAnimation(self, b"radius")
        self.anim.setDuration(duration)

        if reverse:
            self.setRadius(max_radius)
            self.anim.setStartValue(max_radius)
            self.anim.setEndValue(0)
        else:
            self.setRadius(0)
            self.anim.setStartValue(0)
            self.anim.setEndValue(max_radius)

        if finished_callback:
            self.anim.finished.connect(finished_callback)

        # auto-hide when shrinking ends
        if reverse:
            self.anim.finished.connect(self.hide)

        self.anim.start()
