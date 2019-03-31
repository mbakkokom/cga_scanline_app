from PyQt5.QtWidgets import QMenu, QAction
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QObject, pyqtSignal, pyqtSlot, QEvent

from primitives.point import Point

from widgets.raster_surface import RasterSurface
from widgets.polygon_transformer import PolygonTransformer

from helpers.polygon_transformation_helper import \
    Matrix33, matmul33, transformPolygon, getTranslationMatrix


class UserTransformationHelper(QObject):
    """
    Usage note: the 'W' part of the XYW coordinate is always ignored.
    """

    transformOriginColor = QColor(210, 210, 210, 255)

    userRequestedOriginPointChange = pyqtSignal()
    userFinishedOriginPointChange = pyqtSignal(bool)
    userRequestedTransformAllPolygon = pyqtSignal()
    userFinishedTransformAllPolygon = pyqtSignal()

    def __init__(self, parent: RasterSurface):
        super().__init__(parent)
        self.rasterSurface = parent

        self.originPoint = Point(0, 0)
        self.currentlySelectingNewOrigin = False

        # -- context menu
        self.contextMenu = QMenu("&Transformation", parent)

        self.setTransformOriginAction = QAction(
            "Set transform origin",
            self.contextMenu
        )
        self.setTransformOriginAction.triggered.connect(
            self.userRequestOriginPointChange
        )

        self.resetTransformOriginAction = QAction(
            "Reset transform origin"
        )
        self.resetTransformOriginAction.triggered.connect(
            self.userRequestOriginPointReset
        )

        self.showTransformOriginAction = QAction(
            "Show transform origin",
            self.contextMenu
        )
        self.showTransformOriginAction.setCheckable(True)
        self.showTransformOriginAction.setChecked(True)
        self.showTransformOriginAction.toggled.connect(
            self.toggleShowTransformOrigin
        )

        self.transformAllPolygonsAction = QAction(
            "Transform all polygons",
            self.contextMenu
        )
        self.transformAllPolygonsAction.triggered.connect(
            self.userRequestTransformAllPolygon
        )

        self.contextMenu.addActions([
            self.setTransformOriginAction,
            self.resetTransformOriginAction
        ])
        self.contextMenu.addSeparator()
        self.contextMenu.addAction(self.transformAllPolygonsAction)
        self.contextMenu.addSeparator()
        self.contextMenu.addAction(self.showTransformOriginAction)

        self.rasterSurface.renderEnd.connect(self.rasterSurfaceRender)
        self.rasterSurface.installEventFilter(self)

    def eventFilter(self, obj: QObject, event: QEvent) -> None:
        if self.currentlySelectingNewOrigin:
            et = event.type()
            if et == QEvent.MouseMove:
                np = self.rasterSurface.mapFromGlobal(
                    event.globalPos()
                )
                self.originPoint.x, self.originPoint.y = \
                    np.x(), \
                    self.rasterSurface.height() - np.y()
                self.rasterSurface.repaint()
            elif et == QEvent.MouseButtonRelease:
                self.endSelectNewOriginPoint()
            elif et == QEvent.KeyRelease:
                key = event.key()
                if key == Qt.Key_Escape:
                    self.endSelectNewOriginPoint(False)
        return False

    def beginSelectNewOriginPoint(self) -> None:
        self._lastOriginPoint = self.originPoint
        self.originPoint = Point.from_point(self.originPoint)
        self.currentlySelectingNewOrigin = True
        self.rasterSurface.setMouseTracking(True)
        self.rasterSurface.grabKeyboard()

    def endSelectNewOriginPoint(self, save: bool = True) -> None:
        if not save:
            self.originPoint = self._lastOriginPoint
        self.currentlySelectingNewOrigin = False
        self.rasterSurface.setMouseTracking(False)
        self.rasterSurface.releaseKeyboard()
        self.userFinishedOriginPointChange.emit(save)

    @pyqtSlot(bool)
    def toggleShowTransformOrigin(self, checked: bool) -> None:
        if checked:
            self.rasterSurface.renderEnd.connect(self.rasterSurfaceRender)
        else:
            self.rasterSurface.renderEnd.disconnect(self.rasterSurfaceRender)
        self.rasterSurface.repaint()

    @pyqtSlot()
    def userRequestOriginPointChange(self) -> None:
        self.userRequestedOriginPointChange.emit()
        self.beginSelectNewOriginPoint()

    @pyqtSlot()
    def userRequestOriginPointReset(self) -> None:
        self.originPoint.x, self.originPoint.y = 0, 0
        self.rasterSurface.repaint()

    @pyqtSlot()
    def userRequestTransformAllPolygon(self) -> None:
        self.userRequestedTransformAllPolygon.emit()

        dlg = PolygonTransformer(self.parent())
        dlg.userAcknowledgedTransformation.connect(
            self.userFinishTransformAllPolygon
        )
        dlg.show()

    @pyqtSlot(tuple)
    def userFinishTransformAllPolygon(self, mat: Matrix33) -> None:
        mat = matmul33(
            getTranslationMatrix(-self.originPoint.x, -self.originPoint.y),
            mat
        )

        mat = matmul33(
            mat,
            getTranslationMatrix(self.originPoint.x, self.originPoint.y)
        )

        for poly in self.rasterSurface.polygonFactory:
            transformPolygon(mat, poly)
            poly.update_cache()

        self.userFinishedTransformAllPolygon.emit()

    def rasterSurfaceRender(self, painter: QPainter) -> None:
        transformOriginColor = self.transformOriginColor
        originPoint = self.originPoint

        height = self.rasterSurface.height()

        pen: QPen = painter.pen()
        pen.setColor(transformOriginColor)
        pen.setWidth(2)
        painter.setPen(pen)

        x = originPoint.x
        y = height - originPoint.y

        painter.drawRect(
            x - 4, y - 4,
            8, 8
        )

        painter.drawLine(x, y - 2, x, y - 6)
        painter.drawLine(x, y + 2, x, y + 6)
        painter.drawLine(x - 2, y, x - 6, y)
        painter.drawLine(x + 2, y, x + 6, y)
