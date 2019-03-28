from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QLineEdit, QSlider
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot

from rasterizer.polygon_helper import PolygonHelper

from widgets.color_button import ColorButton


class PolygonProperties(QWidget):
    propertiesChanged = pyqtSignal(PolygonHelper, bool)

    def __init__(self, polygon: PolygonHelper, parent=None):
        super().__init__(parent)
        self.polygon = polygon
        self.initUI()

    def initUI(self) -> None:
        self.setWindowFlags(Qt.Tool)
        self.setWindowModality(Qt.NonModal)

        # -- Content
        self._mainLayout = QGridLayout(self)
        self._mainLayout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(self._mainLayout)

        self._labelName = QLabel("Name:", self)
        self._mainLayout.addWidget(
            self._labelName,
            0,
            0,
            Qt.AlignLeft | Qt.AlignVCenter
        )

        self._textName = QLineEdit(self)
        self._textName.textChanged.connect(self.nameChanged)
        self._mainLayout.addWidget(
            self._textName,
            0,
            1,
            Qt.AlignLeft | Qt.AlignVCenter
        )

        self._labelFillColor = QLabel("Fill Color:", self)
        self._mainLayout.addWidget(
            self._labelFillColor,
            1,
            0,
            Qt.AlignLeft | Qt.AlignVCenter
        )

        self._buttonFillColor = ColorButton(self)
        self._buttonFillColor.colorChanged.connect(
            self.fillColorChanged
        )
        self._mainLayout.addWidget(
            self._buttonFillColor,
            1,
            1,
            Qt.AlignLeft | Qt.AlignVCenter
        )

        self._labelOutlineColor = QLabel("Outline Color:", self)
        self._mainLayout.addWidget(
            self._labelOutlineColor,
            2,
            0,
            Qt.AlignLeft | Qt.AlignVCenter
        )

        self._buttonOutlineColor = ColorButton(self)
        self._buttonOutlineColor.colorChanged.connect(
            self.outlineColorChanged
        )
        self._mainLayout.addWidget(
            self._buttonOutlineColor,
            2,
            1,
            Qt.AlignLeft | Qt.AlignVCenter
        )

        self._labelOutlineThickness = QLabel("Outline thickness:", self)
        self._mainLayout.addWidget(
            self._labelOutlineThickness,
            3,
            0,
            Qt.AlignLeft | Qt.AlignVCenter
        )

        self._sliderOutlineThickness = QSlider(Qt.Horizontal, self)
        self._sliderOutlineThickness.setMinimum(0)
        self._sliderOutlineThickness.setMaximum(20)
        self._sliderOutlineThickness.valueChanged.connect(
            self.outlineThicknessChanged
        )
        self._mainLayout.addWidget(
            self._sliderOutlineThickness,
            3,
            1,
            Qt.AlignLeft | Qt.AlignVCenter
        )

    def setName(self, name: str) -> None:
        self._textName.setText(name)

    def setFillColor(self, color: QColor) -> None:
        self._buttonFillColor.color = color

    def setOutlineColor(self, color: QColor) -> None:
        self._buttonOutlineColor.color = color

    def setOutlineThickness(self, thickness: int) -> None:
        self._sliderOutlineThickness.setValue(thickness)

    def updateUI(self) -> None:
        self.setName(self.polygon.name)
        self.setFillColor(QColor(*self.polygon.fillColor))
        self.setOutlineColor(QColor(*self.polygon.outlineColor))
        self.setOutlineThickness(self.polygon.outlineThickness)

    def show(self) -> None:
        self.updateUI()
        super().show()

    @pyqtSlot(str)
    def nameChanged(self, name: str) -> None:
        self.polygon.name = name
        self.propertiesChanged.emit(self.polygon, False)

    @pyqtSlot(QColor)
    def fillColorChanged(self, color: QColor) -> None:
        self.polygon.fillColor = (
            color.red(), color.green(), color.blue(), color.alpha()
        )
        self.propertiesChanged.emit(self.polygon, True)

    @pyqtSlot(QColor)
    def outlineColorChanged(self, color: QColor) -> None:
        self.polygon.outlineColor = (
            color.red(), color.green(), color.blue(), color.alpha()
        )
        self.propertiesChanged.emit(self.polygon, True)

    @pyqtSlot(int)
    def outlineThicknessChanged(self, thickness: int) -> None:
        self.polygon.outlineThickness = thickness
        self.propertiesChanged.emit(self.polygon, True)
