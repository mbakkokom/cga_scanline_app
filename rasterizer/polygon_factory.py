from typing import Tuple, List, Optional

from primitives import Point
from . polygon_helper import PolygonHelper


class PolygonFactory:
    def __init__(self):
        self.polygons: List[PolygonHelper] = list()

    def create_polygon(self, points: List[Point], name: str = "") \
            -> PolygonHelper:
        poly = PolygonHelper(*points, name=name, parent=self)
        self.polygons.append(poly)
        return poly

    def add_polygon(self, p: PolygonHelper) -> None:
        self.polygons.append(p)

    def get_polygon(self, idx: int) -> Optional[PolygonHelper]:
        if idx >= len(self.polygons):
            return None
        else:
            return self.polygons[idx]

    def update_all_cache(self) -> List[Exception]:
        errors = []

        for p in self.polygons:
            try:
                p.update_cache()
            except Exception as ex:
                errors.append(ex)

        return errors

    def delete_polygon(self, idx: int) -> None:
        del self.polygons[idx]

    def clear_polygons(self) -> None:
        self.polygons.clear()
