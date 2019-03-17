from . point import Point


class Line:
    def __init__(self, x1=0, y1=0, x2=0, y2=0):
        self.p1 = Point(x1, y1)
        self.p2 = Point(x2, y2)

    @staticmethod
    def from_line(l):
        return Line.from_points(l.start, l.end)

    @staticmethod
    def from_points(p1, p2):
        return Line(p1.x, p1.y, p2.x, p2.y)

    @staticmethod
    def from_points_ref(p1, p2):
        r = Line()
        r.p1 = p1
        r.p2 = p2
        return r

    @property
    def start(self):
        return self.p1

    @start.setter
    def start(self, val):
        self.p1 = val

    @property
    def end(self):
        return self.p2

    @end.setter
    def end(self, val):
        self.p2 = val

    def delta(self):
        return Point(self.p2.x - self.p1.x, self.p2.y - self.p1.y)

    def delta_abs(self):
        return Point(abs(self.p2.x - self.p1.x), abs(self.p2.y - self.p1.y))

    def left_normal(self):
        return Point(-(self.p2.y - self.p1.y), self.p2.x - self.p1.x)

    def right_normal(self):
        return Point(self.p2.y - self.p1.y, -(self.p2.x - self.p1.x))

    def pseudocross(self, l):
        v1 = self.delta
        v2 = l.delta

        return v1.x * v2.y - v1.y * v2.x

    def swap_points(self):
        self.p1, self.p2 = self.p2, self.p1

    def __repr__(self):
        return "[Line ({}, {}) to ({}, {})]".format(
            self.p1.x, self.p1.y, self.p2.x, self.p2.y
            )
