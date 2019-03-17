from PyQt5.QtWidgets import QMainWindow, QWidget, QSplitter

from rasterizer.surface import RasterSurface


class MainWindow(QMainWindow):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self._mainSplitter = QSplitter(self)

        self._rasterSurface = RasterSurface(self)
        self._rasterSurface.setMinimumSize(400, 400)

        self._mainSplitter.addWidget(self._rasterSurface)
        self.setCentralWidget(self._rasterSurface)
