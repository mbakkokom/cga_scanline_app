from . line import Line, Point


class Polygon:
    def __init__(self, *args):
        self.points = []

        for p in args:
            self.points.append(Point.from_point(p))

    @staticmethod
    def from_polygon(p):
        return Polygon(*p.points)

    @staticmethod
    def from_list(lst):
        ln = len(lst)

        if ln <= 0 or ln % 2 != 0:
            raise ValueError("list must be a multiple of two")

        idx = 0
        points = []

        while idx < ln:
            points.append(Point(lst[idx], lst[idx + 1]))
            idx += 2

        return Polygon(*points)

    def clone_points(self):
        return list(self.points)

    def get_point(self, idx):
        ln = len(self.points)
        if idx >= ln:
            raise IndexError("list index out of range")

        return Point.from_point(self.points[idx])

    def get_point_ref(self, idx):
        ln = self.points.length
        if idx >= ln:
            raise IndexError("list index out of range")

        return self.points[idx]

    def get_line(self, idx):
        ln = self.points.length
        if idx >= ln:
            raise IndexError("list index out of range")

        return Line.from_points(self.points[idx], self.points[(idx + 1) % ln])

    @property
    def length(self):
        return len(self.points)

    def points_iter(self):
        for p in self.points:
            yield p

    def lines_iter(self):
        i = 0
        ln = len(self.points)

        while i < ln:
            n = i
            i += 1
            nx = i % ln

            yield Line.from_points(self.points[n], self.points[nx])

    def is_clockwise(self):
        ln = len(self.points)
        if ln < 3:
            raise ValueError("polygon must be comprised of at least 3 points")

        l1 = self.get_line(0)
        v1 = l1.delta

        l2 = self.get_line(1)
        v2 = l2.delta

        v1.x * v2.y - v1.y * v2.x < 0

    def is_convex(self):
        ln = len(self.points)
        if ln < 3:
            raise ValueError("polygon must be comprised of at least 3 points")

        first = l1 = self.get_line(0)
        l2 = self.get_line(1)

        c1 = c2 = l1.pseudocross(l2)

        i = 2
        while i < ln and c1 * c2 > 0:
            l1 = l2
            c1 = c2
            l2 = self.get_line(i)
            c2 = l1.pseudocross(l2)
            i += 1

        if c1 * c2 > 0:
            return c2 * l2.pseudocross(first) > 0
        else:
            return False
