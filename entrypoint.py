import sys
from PyQt5.QtWidgets import QApplication

from mainwindow import MainWindow
from primitives.point import Point


app = QApplication(sys.argv)

mw = MainWindow()
mw._rasterSurface.polygonFactory.create_polygon([
    Point(0, 0),
    Point(20, 0),
    Point(10, 20)
]).update_cache()
mw.show()

sys.exit(app.exec_())
