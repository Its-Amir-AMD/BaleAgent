from __future__ import annotations
from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve
from PySide6.QtWidgets import QPushButton
from PySide6.QtGui import QIcon


class DockButton(QPushButton):
    def __init__(self, key: str, tooltip: str, icon_factory, parent=None):
        super().__init__(parent)
        self.key = key
        self.icon_factory = icon_factory
        self.setObjectName("DockButton")
        self.setToolTip(tooltip)
        self.setAccessibleName(tooltip)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(54, 52)
        self.setIconSize(QSize(21, 21))
        self.setFocusPolicy(Qt.StrongFocus)
        self._anim = QPropertyAnimation(self, b"iconSize", self)
        self._anim.setDuration(145)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)

    def set_icon_tint(self, color: str):
        self.setIcon(self.icon_factory(self.key, color))

    def _animate(self, size: QSize):
        self._anim.stop()
        self._anim.setStartValue(self.iconSize())
        self._anim.setEndValue(size)
        self._anim.start()

    def enterEvent(self, event):
        self._animate(QSize(27, 27))
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._animate(QSize(21, 21))
        super().leaveEvent(event)
