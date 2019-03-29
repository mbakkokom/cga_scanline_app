from typing import List, Optional

from primitives import Point
from . polygon_helper import PolygonHelper


class PolygonFactory(list):
    def __init__(self):
        super().__init__()

    def create(self, points: List[Point], name: str = "") \
            -> PolygonHelper:
        poly = PolygonHelper(*points, name=name, parent=self)
        self.append(poly)
        return poly

    def get(self, idx: int) -> Optional[PolygonHelper]:
        if idx > len(self):
            return None
        else:
            return self[idx]

    def update_all_cache(self) -> List[Exception]:
        errors = []

        for p in self:
            try:
                p.update_cache()
            except Exception as ex:
                errors.append(ex)

        return errors

    def removeByIndex(self, idx: int) -> None:
        del self.polygons[idx]
