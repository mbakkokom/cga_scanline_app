from typing import Optional

from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject, QEvent, Qt

from rasterizer.polygon_factory import PolygonHelper
from widgets.raster_surface import RasterSurface


class UserDrawToolHelper(QObject):

    # This signal is emitted when a polygon
    polygonDrawFinished = pyqtSignal(bool, PolygonHelper)

    def __init__(self, parent: QObject = None):
        super().__init__(parent)
        self._editingPolygon: Optional[PolygonHelper] = None

    def install(self, rasterSurface: RasterSurface) -> None:
        self.rasterSurface = rasterSurface
        self.rasterSurface.installEventFilter(self)
        self.rasterSurface.renderEnd.connect(self.rasterSurfaceRender)

    def eventFilter(self, obj: QObject, event: QEvent) -> None:
        if obj is not self.rasterSurface:
            return False

        et = event.type()
        if et == QEvent.MouseMove:
            self._cursorPos = self.rasterSurface.mapFromGlobal(
                event.globalPos()
            )
            if self._editingPolygon is not None:
                self.rasterSurface.repaint()
        elif self._editingPolygon is not None:
            if et == QEvent.MouseButtonPress:
                pass
            elif et == QEvent.MouseButtonRelease:
                np = self._cursorPos
                if self.rasterSurface.geometry().contains(np):
                    self._editingPolygon.add_point(
                        np.x(),
                        self.rasterSurface.height() - np.y()
                    )
            elif et == QEvent.KeyRelease:
                key = event.key()
                if key == Qt.Key_Return or key == Qt.Key_Enter:
                    self.endEditing(self._editingPolygon.length >= 3)
                elif key == Qt.Key_Escape:
                    self.endEditing(False)

        return False

    def beginNewPolygon(self) -> None:
        self._editingPolygon = PolygonHelper()
        self.rasterSurface.setMouseTracking(True)
        self.rasterSurface.grabKeyboard()

    def endEditing(self, savePolygon=True) -> None:
        self.rasterSurface.setMouseTracking(False)
        self.rasterSurface.releaseKeyboard()
        poly = self._editingPolygon
        self._editingPolygon = None
        self.polygonDrawFinished.emit(
            savePolygon, poly
        )

    @pyqtSlot(QPainter)
    def rasterSurfaceRender(self, painter: QPainter):
        if self._editingPolygon is None:
            return

        pointColor = QColor(75, 125, 255, 255)
        lineColor = QColor(255, 225, 75, 255)

        pen = painter.pen()
        pen.setColor(lineColor)
        painter.setPen(pen)

        height = self.rasterSurface.height()

        ln = self._editingPolygon.length
        if ln > 0:
            prev = None
            for p in self._editingPolygon.points_iter():
                if prev is None:
                    prev = p
                    painter.fillRect(
                        p.x - 5,
                        height - p.y - 5,
                        10,
                        10,
                        pointColor
                    )
                else:
                    painter.fillRect(
                        p.x - 5,
                        height - p.y - 5,
                        10,
                        10,
                        pointColor
                    )
                    painter.drawLine(
                        prev.x,
                        height - prev.y,
                        p.x,
                        height - p.y
                    )
                    prev = p
            p = self._cursorPos  # Qt's QPoint
            painter.fillRect(p.x() - 5, p.y() - 5, 10, 10, pointColor)
            painter.drawLine(prev.x, height - prev.y, p.x(), p.y())
        else:
            p = self._cursorPos  # Qt's QPoint
            painter.fillRect(p.x() - 5, p.y() - 5, 10, 10, pointColor)       