from typing import Tuple

from PyQt5.QtWidgets import QMainWindow, QWidget, QSplitter, \
    QVBoxLayout, QHBoxLayout, QPushButton, QColorDialog, \
    QMenu, QAction, QFileDialog
from PyQt5.QtGui import QColor
from PyQt5.QtCore import pyqtSlot, Qt, QCoreApplication

from rasterizer.polygon_helper import PolygonHelper
from rasterizer.polygon_factory import PolygonFactory

from widgets.polygon_list import PolygonList
from widgets.raster_surface import RasterSurface
# from widgets.polygon_properties import PolygonProperties
from widgets.error_list_drawer import ErrorListDrawer
from widgets.polygon_data_helper import PolygonDataHelper

from draw_tool.user_draw_tool_helper import UserDrawToolHelper

from fileio import FileIO


class MainWindow(QMainWindow):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.polygonFactory = PolygonFactory()
        self.polygonDataHelper = PolygonDataHelper(self, self.polygonFactory)

        self._polygonFillColor = QColor(255, 255, 255, 255)
        self._polygonOutlineColor = QColor(0, 0, 0, 255)

        self.initUI()
        self._polygonList.polygonsChange()

        self._polygonId = 0

    def initUI(self) -> None:
        # -- Menu
        self._menuFile = QMenu("&File", self)
        self.menuBar().addMenu(self._menuFile)

        self._actionFileNew = QAction("&New", self._menuFile)
        self._actionFileNew.setShortcut(Qt.CTRL | Qt.Key_N)
        self._actionFileNew.triggered.connect(self.clearAllObjects)

        self._actionFileOpen = QAction("&Open", self._menuFile)
        self._actionFileOpen.setShortcut(Qt.CTRL | Qt.Key_O)
        self._actionFileOpen.triggered.connect(self.fileOpen)

        self._actionFileSaveAs = QAction("&Save As", self._menuFile)
        self._actionFileSaveAs.setShortcut(Qt.CTRL | Qt.Key_S)
        self._actionFileSaveAs.triggered.connect(self.fileSaveAs)

        self._actionFileExit = QAction("Quit", self._menuFile)
        self._actionFileExit.setShortcut(Qt.CTRL | Qt.Key_Q)
        self._actionFileExit.triggered.connect(self.quitApplication)

        self._menuFile.addAction(self._actionFileNew)
        self._menuFile.addSeparator()
        self._menuFile.addActions([
            self._actionFileOpen,
            self._actionFileSaveAs
        ])
        self._menuFile.addSeparator()
        self._menuFile.addAction(self._actionFileExit)

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
            self.polygonDataHelper,
            parent=self
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
    def createNewPolygon(self) -> None:
        self._userDrawToolHelper.beginNewPolygon()

    @pyqtSlot()
    def fillColorChange(self) -> None:
        self._polygonFillColor = QColorDialog.getColor(
            self._polygonFillColor, self
        )
        self._drawFillColorButton.updateColor()

    @pyqtSlot()
    def outlineColorChange(self) -> None:
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
            self.polygonDataHelper.insertPolygon(0, polygon)
            self._polygonList.polygonsChange()

        self._drawButtonLayoutWrapper.show()
        self._rasterSurface.repaint()

    @pyqtSlot()
    def clearAllObjects(self) -> None:
        self.polygonDataHelper.clearAll()
        self._polygonList.polygonsChange()
        self._rasterSurface.repaint()

    @pyqtSlot()
    def fileOpen(self) -> None:
        result: Tuple[str, str] = QFileDialog.getOpenFileName(
            self,
            "Select file",
            "",
            "JSON Files (*.json);;All Files (*.*)"
        )
        if len(result) != 2 or len(result[0]) == 0:
            return

        fn = result[0]
        print("FILE READ \"{}\"".format(fn))

        self.polygonDataHelper.clearAll()

        hdl = FileIO(self.polygonFactory)
        _, errs = hdl.readFile(fn)

        errs += self.polygonDataHelper.updateAllPolygonCache()

        self.polygonDataHelper.generateMapping()

        self._polygonList.polygonsChange()
        self._rasterSurface.repaint()

        if len(errs) > 0:
            ErrorListDrawer(
                "There were some errors while importing the JSON file:",
                errs,
                self
            ).show()

    @pyqtSlot()
    def fileSaveAs(self) -> None:
        result: Tuple[str, str] = QFileDialog.getSaveFileName(
            self,
            "Select file",
            "",
            "JSON Files (*.json);;All Files (*.*)"
        )
        if len(result) != 2 or len(result[0]) == 0:
            return

        fn = result[0]
        print("FILE WRITE \"{}\"".format(fn))

        hdl = FileIO(self.polygonFactory)
        _, err = hdl.writeFile(fn)

        if err is not None:
            ErrorListDrawer(
                "There were some errors while exporting the JSON file:",
                [err],
                self
            ).show()

    @pyqtSlot()
    def quitApplication(self) -> None:
        QCoreApplication.exit()
