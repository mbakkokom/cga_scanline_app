from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QSlider
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt, pyqtSlot

from widgets.color_button import ColorButton

from helpers.user_draw_tool_helper import UserDrawToolHelper


class UserDrawPanel(QWidget):
    def __init__(self, drawHelper: UserDrawToolHelper = None, parent=None):
        super().__init__(parent)

        self.drawHelper = UserDrawToolHelper(parent) \
            if drawHelper is None else drawHelper

        self.fillColor = QColor(255, 255, 255, 255)
        self.outlineColor = QColor(0, 0, 0, 255)
        self.outlineThickness = 1

        self.initUI()

    def initUI(self):
        # Draw pane
        self.setContentsMargins(0, 0, 0, 0)

        self._drawButtonLayout = QHBoxLayout(self)
        self._drawButtonLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self._drawButtonLayout)

        self._drawBeginButton = QPushButton(
            "Draw", self
        )
        self._drawBeginButton.clicked.connect(self.createNewPolygon)

        self._drawFillColorButton = ColorButton(
            self,
            self.fillColor
        )
        self._drawFillColorButton.colorChanged.connect(self.fillColorChange)

        self._drawOutlineColorButton = ColorButton(
            self,
            self.outlineColor
        )
        self._drawOutlineColorButton.colorChanged.connect(
            self.outlineColorChange
        )

        self._drawOutlineThicknessSlider = QSlider(Qt.Horizontal, self)
        self._drawOutlineThicknessSlider.setMinimum(0)
        self._drawOutlineThicknessSlider.setMaximum(20)
        self._drawOutlineThicknessSlider.setValue(
            self.outlineThickness
        )
        self._drawOutlineThicknessSlider.valueChanged.connect(
            self.outlineThicknessChanged
        )

        self._drawButtonLayout.addWidget(self._drawBeginButton)
        self._drawButtonLayout.addWidget(self._drawFillColorButton)
        self._drawButtonLayout.addWidget(self._drawOutlineColorButton)
        self._drawButtonLayout.addWidget(self._drawOutlineThicknessSlider)

    @pyqtSlot()
    def createNewPolygon(self) -> None:
        self.drawHelper.beginNewPolygon()

    @pyqtSlot(QColor)
    def fillColorChange(self, color: QColor) -> None:
        self.fillColor = QColor(color)

    @pyqtSlot(QColor)
    def outlineColorChange(self, color: QColor) -> None:
        self.outlineColor = QColor(color)

    @pyqtSlot(int)
    def outlineThicknessChanged(self, thickness: int) -> None:
        self.outlineThickness = thickness
