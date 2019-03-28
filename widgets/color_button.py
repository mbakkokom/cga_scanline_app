from typing import Optional

from PyQt5.QtWidgets import QPushButton, QColorDialog
from PyQt5.QtGui import QColor
from PyQt5.QtCore import pyqtSlot, pyqtSignal


class ColorButton(QPushButton):
    colorChanged = pyqtSignal(QColor)

    def __init__(self, parent=None, color: Optional[QColor] = None):
        super().__init__(parent)

        self.setFixedWidth(35)
        self.clicked.connect(self.click)

        self.color = QColor(0, 0, 0, 255) if color is None else color

    @property
    def color(self):
        return QColor(self._color)

    @color.setter
    def color(self, color: QColor):
        self._color = QColor(color)
        self._updateUI()

    def _updateUI(self):
        self.setStyleSheet(
            "QPushButton {{ background-color: rgba({}, {}, {}, {}) }}".
            format(
                self._color.red(),
                self._color.green(),
                self._color.blue(),
                self._color.alpha()
            )
        )

    @pyqtSlot()
    def click(self):
        col = QColorDialog.getColor(
            self._color, self, "", QColorDialog.ShowAlphaChannel
        )

        if col.isValid():
            self.color = col
            self.colorChanged.emit(self._color)
