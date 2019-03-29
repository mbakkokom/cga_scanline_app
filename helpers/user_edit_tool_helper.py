from typing import Optional

from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject, QPoint, QEvent, Qt

from primitives.point import Point

from rasterizer.polygon_helper import PolygonHelper

from widgets.raster_surface import RasterSurface


class UserEditToolHelper(QObject):
    polygonEditStarted = pyqtSignal(PolygonHelper)
    polygonEditFinished = pyqtSignal(bool, PolygonHelper)

    def __init__(self, parent: QObject = None):
        super().__init__(parent)
        self._editingPolygon: Optional[PolygonHelper] = None
        self._cursorPos = QPoint(0, 0)
        self._highlightedPoint: Optional[Point] = None
        self._highlightedPointActive: bool = False

    def install(self, rasterSurface: RasterSurface) -> None:
        self.rasterSurface = rasterSurface
        self.rasterSurface.installEventFilter(self)
        self.rasterSurface.renderEnd.connect(self.rasterSurfaceRender)

    def eventFilter(self, obj: QObject, event: QEvent) -> None:
        if obj is not self.rasterSurface or self._editingPolygon is None:
            return False

        et = event.type()
        if et == QEvent.MouseMove:
            self._cursorPos = self.rasterSurface.mapFromGlobal(
                event.globalPos()
            )
            if self._editingPolygon is not None:
                if self._highlightedPoint is not None and \
                   self._highlightedPointActive:
                    self._highlightedPoint.x, self._highlightedPoint.y = \
                        self._cursorPos.x(), \
                        self.rasterSurface.height() - self._cursorPos.y()
                    self._editingPolygon.update_cache()
                self.rasterSurface.repaint()
        elif self._editingPolygon is not None:
            if et == QEvent.MouseButtonPress:
                np = self._cursorPos
                if self.rasterSurface.geometry().contains(np):
                    x = np.x()
                    y = np.y()
                    height = self.rasterSurface.height()

                    for p in self._editingPolygon.points:
                        if abs(x - p.x) <= 5 and abs(y - height + p.y) <= 5:
                            self._highlightedPoint = p
                            self._highlightedPointActive = True
                            self.rasterSurface.repaint()
                            break
            elif et == QEvent.MouseButtonRelease:
                # self._highlightedPoint = None
                self._highlightedPointActive = False
                self.rasterSurface.repaint()
            elif et == QEvent.KeyRelease:
                key = event.key()
                if key == Qt.Key_Return or key == Qt.Key_Enter:
                    self.endEditing(True)
                elif key == Qt.Key_Escape:
                    self.endEditing(False)

        return False

    def beginEditPolygon(self, targetShape: PolygonHelper) -> None:
        # reset states
        self._highlightedPoint = None
        self._highlightedPointActive = False

        self._editingPolygon = targetShape
        self._originalPoints = [
            Point.from_point(p) for p in targetShape.points
        ]

        self.rasterSurface.setMouseTracking(True)
        self.rasterSurface.grabKeyboard()
        self.polygonEditStarted.emit(self._editingPolygon)
        self.rasterSurface.repaint()

    def endEditing(self, savePolygon=True) -> None:
        self.rasterSurface.setMouseTracking(False)
        self.rasterSurface.releaseKeyboard()

        poly = self._editingPolygon
        savePolygon = savePolygon and len(poly.points) >= 3

        if not savePolygon:
            poly.points = self._originalPoints
            poly.update_cache()

        self._editingPolygon = None
        self.polygonEditFinished.emit(savePolygon, poly)

    @pyqtSlot()
    def userRequestNewPoint(self) -> bool:
        if self._highlightedPoint is not None:
            curPoint = self._highlightedPoint
            idx = self._editingPolygon.points.index(curPoint)
            nextPoint = self._editingPolygon.points[
                (idx + 1) % self._editingPolygon.length
            ]

            length = curPoint.to(nextPoint)

            newPoint = Point(
                curPoint.x + int(length.x / 2),
                curPoint.y + int(length.y / 2)
            )

            self._editingPolygon.points.insert(idx + 1, newPoint)

            self._highlightedPoint = newPoint
            self.rasterSurface.repaint()
            return True
        else:
            return False

    @pyqtSlot()
    def userRequestDeletePoint(self) -> bool:
        if self._highlightedPoint is not None:
            self._editingPolygon.points.remove(self._highlightedPoint)
            self._editingPolygon.update_cache()
            self._highlightedPoint = None
            self._highlightedPointActive = False
            self.rasterSurface.repaint()
            return True
        else:
            return False

    @pyqtSlot(QPainter)
    def rasterSurfaceRender(self, painter: QPainter):
        if self._editingPolygon is None:
            return

        pointColor = QColor(75, 125, 255, 255)
        activePointColor = QColor(255, 125, 75, 255)
        lineColor = QColor(255, 225, 75, 255)

        pen: QPen = painter.pen()
        pen.setColor(lineColor)
        pen.setWidth(1)
        painter.setPen(pen)

        height = self.rasterSurface.height()

        for p in self._editingPolygon.points:
            painter.fillRect(
                p.x - 5,
                height - p.y - 5,
                10,
                10,
                activePointColor if p is self._highlightedPoint else pointColor
            )

        for l in self._editingPolygon.lines_iter():
            painter.drawLine(
                l.start.x,
                height - l.start.y,
                l.end.x,
                height - l.end.y
            )
