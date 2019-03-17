

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @staticmethod
    def from_point(p):
        return Point(p.x, p.y)

    def to(self, p):
        return Point(p.x - self.x, p.y - self.y)

    def to_abs(self, p):
        return Point(abs(p.x - self.x), abs(p.y - self.y))

    def dot(self, p):
        return self.x * p.x + self.y * p.y

    def __mul__(self, s):
        new_value = Point.from_point(self)

        new_value.x *= s
        new_value.y *= s

        return new_value

    def __imul__(self, s):
        self.x *= s
        self.y *= s

    def __add__(self, p):
        new_value = Point.from_point(self)

        new_value.x += p.x
        new_value.y += p.y

        return new_value

    def __iadd__(self, p):
        self.x += p.x
        self.y += p.y

    def __abs__(self):
        return Point(abs(self.x), abs(self.y))

    def __eq__(self, p):
        return self.x == p.x and self.y == p.y

    def get_invert(self):
        return Point(-self.x, -self.y)

    def invert(self):
        self *= -1

    def __repr__(self):
        return "[Point {}, {}]".format(self.x, self.y)
