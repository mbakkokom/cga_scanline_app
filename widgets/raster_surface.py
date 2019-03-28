from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QPen, QColor, QPaintEvent
from PyQt5.QtCore import pyqtSignal, QPoint

from rasterizer.polygon_factory import PolygonFactory


class RasterSurface(QWidget):
    """
    This widget helps manage primitives and shows the rasterized result.
    """

    # Signals
    renderBegin = pyqtSignal(QPainter)
    renderEnd = pyqtSignal(QPainter)

    def __init__(self, parent=None, polygonFactory: PolygonFactory = None):
        super().__init__(parent)

        if polygonFactory is None:
            polygonFactory = PolygonFactory()

        self.polygonFactory = polygonFactory

    def paintEvent(self, event: QPaintEvent):
        height = self.height()

        painter = QPainter(self)
        pen: QPen = painter.pen()

        blockColor = QColor(0, 0, 0, 255)
        painter.eraseRect(0, 0, self.width(), height)

        self.renderBegin.emit(painter)

        for poly in reversed(self.polygonFactory):
            if len(poly.points) > 0:
                r, g, b, a = poly.fillColor
                if poly.has_cache and a != 0:
                    col = QColor(r, g, b, a)
                    pen.setColor(blockColor)
                    painter.setPen(pen)

                    for y, x1, x2 in poly.cachedLines:
                        y = height - y

                        painter.fillRect(
                            x1,
                            y,
                            x2 - x1,
                            1,
                            col
                        )

                r, g, b, a = poly.outlineColor
                if poly.outlineThickness > 0 and a != 0:
                    pen.setColor(QColor(r, g, b, a))
                    pen.setWidth(poly.outlineThickness)
                    painter.setPen(pen)

                    points = [QPoint(i.x, height - i.y) for i in poly.points]

                    painter.drawPolygon(points[0], *points[1:])

        self.renderEnd.emit(painter)
