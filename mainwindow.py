from PyQt5.QtWidgets import QMainWindow, QWidget, QSplitter, \
    QVBoxLayout, QHBoxLayout, QPushButton, QColorDialog
from PyQt5.QtGui import QColor
from PyQt5.QtCore import pyqtSlot

from rasterizer.polygon_factory import PolygonHelper, PolygonFactory

from widgets.polygon_list import PolygonList
from widgets.raster_surface import RasterSurface

from draw_tool.user_draw_tool_helper import UserDrawToolHelper


class MainWindow(QMainWindow):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.polygonFactory = PolygonFactory()

        self._polygonFillColor = QColor(255, 255, 255, 255)
        self._polygonOutlineColor = QColor(0, 0, 0, 255)

        self.initUI()
        self._polygonList.polygonsChange()

        self._polygonId = 0

    def initUI(self) -> None:
        # -- Content
        self._mainSplitter = QSplitter(self)

        # Raster surface
        self._rasterSurface = RasterSurface(
            self, polygonFactory=self.polygonFactory
        )
        self._rasterSurface.setMinimumSize(400, 400)

        self._userDrawToolHelper = UserDrawToolHelper(self)
        self._userDrawToolHelper.install(self._rasterSurface)
        self._userDrawToolHelper.polygonDrawFinished.connect(
            self.userFinishedDrawing
        )
        self._userDrawToolHelper.polygonDrawStarted.connect(
            self.userStartedDrawing
        )

        self._mainSplitter.addWidget(self._rasterSurface)

        # Right pane
        self._rightPaneLayoutWrapper = QWidget(self)

        self._rightPaneLayout = QVBoxLayout(self._rightPaneLayoutWrapper)
        self._rightPaneLayout.setContentsMargins(0, 0, 0, 0)

        self._rightPaneLayoutWrapper.setLayout(self._rightPaneLayout)
        self._mainSplitter.addWidget(self._rightPaneLayoutWrapper)

        self._polygonList = PolygonList(
            parent=self,
            polygonFactory=self.polygonFactory
        )
        # FIXME workaround for dark theme
        self._polygonList.setStyleSheet(
            "QListWidget { background-color: black; color: white }"
        )
        self._polygonList.polygonsChanged.connect(self._rasterSurface.repaint)
        self._rightPaneLayout.addWidget(self._polygonList)

        # Draw pane
        self._drawButtonLayoutWrapper = QWidget(self._rasterSurface)
        self._drawButtonLayoutWrapper.setContentsMargins(0, 0, 0, 0)

        self._drawButtonLayout = QHBoxLayout(self._drawButtonLayoutWrapper)
        self._drawButtonLayout.setContentsMargins(0, 0, 0, 0)
        self._drawButtonLayoutWrapper.setLayout(self._drawButtonLayout)

        self._drawBeginButton = QPushButton(
            "Draw", self._drawButtonLayoutWrapper
        )
        self._drawBeginButton.clicked.connect(self.createNewPolygon)

        self._drawFillColorButton = QPushButton(self._drawButtonLayoutWrapper)
        self._drawFillColorButton.setFixedWidth(35)
        self._drawFillColorButton.updateColor = lambda: \
            self._drawFillColorButton.setStyleSheet(
                "QPushButton {{ background-color: rgba({}, {}, {}, {}) }}".
                format(
                    self._polygonFillColor.red(),
                    self._polygonFillColor.green(),
                    self._polygonFillColor.blue(),
                    self._polygonFillColor.alpha()
                )
            )
        self._drawFillColorButton.updateColor()
        self._drawFillColorButton.clicked.connect(self.fillColorChange)

        self._drawOutlineColorButton = QPushButton(
            self._drawButtonLayoutWrapper
        )
        self._drawOutlineColorButton.setFixedWidth(35)
        self._drawOutlineColorButton.updateColor = lambda: \
            self._drawOutlineColorButton.setStyleSheet(
                "QPushButton {{ background-color: rgba({}, {}, {}, {}) }}".
                format(
                    self._polygonOutlineColor.red(),
                    self._polygonOutlineColor.green(),
                    self._polygonOutlineColor.blue(),
                    self._polygonOutlineColor.alpha()
                )
            )
        self._drawOutlineColorButton.updateColor()
        self._drawOutlineColorButton.clicked.connect(self.outlineColorChange)

        self._drawButtonLayout.addWidget(self._drawBeginButton)
        self._drawButtonLayout.addWidget(self._drawFillColorButton)
        self._drawButtonLayout.addWidget(self._drawOutlineColorButton)

        # Packing
        self.setCentralWidget(self._mainSplitter)

    @pyqtSlot()
    def polygonsChanged(self) -> None:
        self._polygonList.polygonsChange()

    @pyqtSlot()
    def createNewPolygon(self):
        self._userDrawToolHelper.beginNewPolygon()

    @pyqtSlot()
    def fillColorChange(self):
        self._polygonFillColor = QColorDialog.getColor(
            self._polygonFillColor, self
        )
        self._drawFillColorButton.updateColor()

    @pyqtSlot()
    def outlineColorChange(self):
        self._polygonOutlineColor = QColorDialog.getColor(
            self._polygonOutlineColor, self
        )
        self._drawOutlineColorButton.updateColor()

    @pyqtSlot(PolygonHelper)
    def userStartedDrawing(self, polygon: PolygonHelper) -> None:
        self._drawButtonLayoutWrapper.hide()

    @pyqtSlot(bool, PolygonHelper)
    def userFinishedDrawing(self,
                            confirm: bool,
                            polygon: PolygonHelper) -> None:
        if confirm is True:
            # TODO default properties
            polygon.fillColor = (
                self._polygonFillColor.red(),
                self._polygonFillColor.green(),
                self._polygonFillColor.blue(),
                self._polygonFillColor.alpha()
            )
            polygon.outlineColor = (
                self._polygonOutlineColor.red(),
                self._polygonOutlineColor.green(),
                self._polygonOutlineColor.blue(),
                self._polygonOutlineColor.alpha()
            )
            polygon.outlineThickness = 3
            polygon.name = "new{}".format(self._polygonId)

            self._polygonId += 1

            polygon.update_cache()
            # self.polygonFactory.add_polygon(polygon)
            self.polygonFactory.polygons.insert(0, polygon)
            self._polygonList.polygonsChange()

        self._drawButtonLayoutWrapper.show()
        self._rasterSurface.repaint()
