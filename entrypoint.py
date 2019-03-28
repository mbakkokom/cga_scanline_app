import sys
from PyQt5.QtWidgets import QApplication

from mainwindow import MainWindow
from primitives.point import Point


app = QApplication(sys.argv)

mw = MainWindow()

p1 = mw.polygonDataHelper.createPolygon([
    Point(0, 0),
    Point(200, 0),
    Point(100, 200)
], name="green")
p1.update_cache()
p1.fillColor = (75, 255, 125, 255)

p2 = mw.polygonDataHelper.createPolygon([
    Point(200, 400),
    Point(300, 100),
    Point(500, 200)
], name="yellow")
p2.update_cache()
p2.fillColor = (255, 255, 125, 255)

p3 = mw.polygonDataHelper.createPolygon([
    Point(50, 50),
    Point(400, 50),
    Point(400, 400),
    Point(50, 400)
], name="square")
p3.update_cache()
p3.fillColor = (255, 75, 10, 255)

mw.polygonsChanged()
mw.show()

sys.exit(app.exec_())
