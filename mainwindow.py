from PyQt5.QtWidgets import QMainWindow, QWidget, QSplitter, \
    QVBoxLayout, QPushButton
from PyQt5.QtCore import pyqtSlot

from rasterizer.polygon_factory import PolygonHelper, PolygonFactory

from widgets.polygon_list import PolygonList
from widgets.raster_surface import RasterSurface

from draw_tool.user_draw_tool_helper import UserDrawToolHelper


class MainWindow(QMainWindow):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.polygonFactory = PolygonFactory()
        self.initUI()
        self._polygonList.polygonsChange()

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
            self.userDrawNewPolygon
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
        self._polygonList.polygonsChanged.connect(self._rasterSurface.repaint)
        self._rightPaneLayout.addWidget(self._polygonList)

        self._drawBeginButton = QPushButton(
            "Draw",
            self._rightPaneLayoutWrapper
        )
        self._drawBeginButton.clicked.connect(
            # TODO create a discrete function
            lambda x: self._userDrawToolHelper.beginNewPolygon()
        )
        self._rightPaneLayout.addWidget(self._drawBeginButton)

        # Packing
        self.setCentralWidget(self._mainSplitter)

    @pyqtSlot()
    def polygonsChanged(self) -> None:
        self._polygonList.polygonsChange()

    @pyqtSlot(bool, PolygonHelper)
    def userDrawNewPolygon(self,
                           confirm: bool,
                           polygon: PolygonHelper) -> None:
        if confirm is True:
            polygon.fillColor = (255, 255, 255, 255)
            polygon.name = "new"
            polygon.update_cache()
            self.polygonFactory.add_polygon(polygon)
            self._polygonList.polygonsChange()
            self._rasterSurface.repaint()
