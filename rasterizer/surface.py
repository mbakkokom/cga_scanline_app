from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QPen, QColor

from . polygon_factory import PolygonFactory
from . scanline import get_raster_lines


class RasterSurface(QWidget):
    """
    This widget helps manage primitives and shows the rasterized result.
    """

    def __init__(self, parent=None, polygonFactory=None):
        super().__init__(parent)

        if polygonFactory is None:
            polygonFactory = PolygonFactory()
        
        self.polygonFactory = polygonFactory

    def paintEvent(self, event):
        painter = QPainter(self)
        pen: QPen = painter.pen()

        blockColor = QColor(0, 0, 0, 255)

        if self.targetShape is None:
            super().paintEvent(event)
        else:
            painter.eraseRect(0, 0, self.width, self.height)
            prev = None

            for pos in get_raster_lines(self.targetShape):
                print(pos)

                if prev is None:
                    prev = pos
                else:
                    # add scaling
                    y = self.height - (prev[1])

                    x1 = prev[0]
                    x2 = pos[0]

                    pen.setColor(blockColor)
                    painter.setPen(pen)

                    painter.fillRect(
                        x1,
                        y,
                        x2 - x1,
                        1,
                        QColor(0, 0, 0, 255)
                    )

                    prev = None

            pen.setColor(QColor(255, 255, 255, 255))
            painter.setPen(pen)
            for ln in self.targetShape.lines_iter():
                painter.drawLine(
                    ln.start.x,
                    self.height - ln.start.y,
                    ln.end.x,
                    self.height - ln.end.y)
