

class RasterState:
    def __init__(self, edge, y_max, x, dx, dy, remainder=0):
        self.edge = edge
        self.y_max = y_max
        self.x = x
        self.dx = dx
        self.dy = dy
        self.remainder = remainder

    @property
    def slope(self):
        return self.dy / self.dx

    def __repr__(self):
        return "{{ {} {} {} {} {} }}".format(
            self.y_max, self.x, self.dx, self.dy, self.remainder
            )
