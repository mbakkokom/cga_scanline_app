from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtCore import pyqtSignal

from . polygon_factory import PolygonFactory


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

    def paintEvent(self, event):
        height = self.height()

        painter = QPainter(self)
        pen: QPen = painter.pen()

        blockColor = QColor(0, 0, 0, 255)
        painter.eraseRect(0, 0, self.width(), height)

        self.renderBegin.emit(painter)

        for poly in reversed(self.polygonFactory.polygons):
            if poly.has_cache:
                col = QColor(
                    poly.fillColor[0], poly.fillColor[1],
                    poly.fillColor[2], poly.fillColor[3]
                )

                for y, x1, x2 in poly.cachedLines:
                    y = height - y

                    pen.setColor(blockColor)
                    painter.setPen(pen)

                    painter.fillRect(
                        x1,
                        y,
                        x2 - x1,
                        1,
                        col
                    )

        """
        pen.setColor(QColor(255, 255, 255, 255))
        painter.setPen(pen)
        for poly in self.polygonFactory.polygons:
            for ln in poly.lines_iter():
                painter.drawLine(
                    ln.start.x,
                    height - ln.start.y,
                    ln.end.x,
                    height - ln.end.y)
        """

        self.renderEnd.emit(painter)
