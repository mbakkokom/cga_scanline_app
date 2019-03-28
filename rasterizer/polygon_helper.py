from typing import List, Tuple, Optional

from . scanline.scanline import get_scanline_bucket, get_raster_lines
from primitives import Point, Polygon


class PolygonHelper(Polygon):
    """
    `PolygonHelper` gives abstractions to the `Polygon` primitive.
    """

    def __init__(self,
                 *args,
                 name: str = "",
                 fillColor: Optional[Tuple[int, int, int, int]] = None,
                 outlineColor: Optional[Tuple[int, int, int, int]] = None,
                 outlineThickness: int = 0,
                 parent=None):
        super().__init__(*args)
        self.parent = parent
        self.name = name

        # additional parameters
        self.fillColor: Tuple[int, int, int, int] = (0, 0, 0, 0) \
            if fillColor is None \
            else fillColor
        self.outlineColor: Tuple[int, int, int, int] = (0, 0, 0, 0) \
            if outlineColor is None \
            else outlineColor
        self.outlineThickness: int = outlineThickness

        # self.update_cache()

    @staticmethod
    def from_polygon(p: Polygon):
        return PolygonHelper(*p.points)

    @staticmethod
    def from_list(points: List[Tuple[int, int]]):
        return PolygonHelper(*[Point(x, y) for x, y in points])

    # --
    @property
    def has_cache(self) -> bool:
        return all(
            [
                hasattr(self, i)
                for i in ("cachedBucketIds", "cachedBucketVals", "cachedLines")
            ]
        )

    def update_cache(self) -> bool:
        """
        Generates a list of tuple with three integers: y, x1, x2
        """
        self.cachedBucketIds, self.cachedBucketVals = get_scanline_bucket(self)
        self.cachedLines = []

        prev = None
        for x, y in get_raster_lines(
            self.cachedBucketIds,
            self.cachedBucketVals
        ):
            if prev is None:
                prev = (y, x)
            else:
                y1 = prev[0]
                if y1 != y:
                    return False

                self.cachedLines.append((y, prev[1], x))
                prev = None

        return prev is None

    # TODO: remove?
    def get_cached_raster(self) -> List[Tuple[int, int, int]]:
        """
        Returns a list of tuple with three integers: y, x1, x2
        """
        return self.cachedLines
    # --

    def add_point(self, x: int, y: int) -> None:
        self.points.append(Point(x, y))

    def insert_point(self, idx: int, x: int, y: int) -> None:
        self.points.insert(idx, Point(x, y))

    def update_point(self, idx: int, x: int, y: int) -> bool:
        if idx >= len(self.points):
            return False
        else:
            p = self.points[idx]
            p.x = x
            p.y = y
            return True

    def update_points(self, points: List[Tuple[int, int]]) -> bool:
        if len(points) > len(self.points):
            return False

        idx = 0
        for x, y in points:
            p = self.points[idx]
            p.x = x
            p.y = y
            idx += 1

        return True

    def replace_points(self, points: List[Tuple[int, int]]) -> None:
        """
        This method allows updating any existing points and automatically
        creating new points.
        """

        idx = 0
        ln = len(self.points)
        for x, y in points:
            if idx < ln:
                p = self.points[idx]
                p.x = x
                p.y = y
            else:
                self.points.append(Point(x, y))
            idx += 1

    def remove_point(self, idx: int) -> bool:
        if idx >= len(self.points):
            return False
        else:
            del self.points[idx]
            return True

    def delete(self) -> bool:
        if self.parent is None:
            return False

        self.parent.remove(self)
        return True

    def __repr__(self) -> str:
        return "[Polygon \"{}\"]".format(self.name)