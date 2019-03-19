from PyQt5.QtWidgets import QMainWindow, QWidget, QSplitter, \
    QVBoxLayout
from PyQt5.QtCore import pyqtSlot

from rasterizer.polygon_factory import PolygonFactory
from rasterizer.surface import RasterSurface

from widgets.polygon_list import PolygonList


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
        self._mainSplitter.addWidget(self._rasterSurface)

        # Right pane
        self._rightPaneLayoutWrapper = QWidget(self)
        self._rightPaneLayout = QVBoxLayout(self._rightPaneLayoutWrapper)
        self._rightPaneLayoutWrapper.setLayout(self._rightPaneLayout)
        self._mainSplitter.addWidget(self._rightPaneLayoutWrapper)

        self._polygonList = PolygonList(
            parent=self,
            polygonFactory=self.polygonFactory
        )
        self._polygonList.polygonsChanged.connect(self._rasterSurface.repaint)
        self._rightPaneLayout.addWidget(self._polygonList)

        # Packing
        self.setCentralWidget(self._mainSplitter)

    @pyqtSlot()
    def polygonsChanged(self):
        self._polygonList.polygonsChange()
