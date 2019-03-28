from typing import Mapping, Optional, List

from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject

from primitives.point import Point

from rasterizer.polygon_helper import PolygonHelper
from rasterizer.polygon_factory import PolygonFactory

from widgets.polygon_properties import PolygonProperties


class PolygonDataHelper(QObject):
    """
    `PolygonDataHelper` wraps around `PolygonFactory` to provide the
    mapping for each `PolygonHelper` object to a `PolygonProperties` widget.
    """

    polygonChanged = pyqtSignal(PolygonHelper, bool)

    def __init__(self,
                 parent=None,
                 polygonFactory: Optional[PolygonFactory] = None):
        super().__init__(parent)
        self.panelParent = parent
        self.polygonFactory = PolygonFactory() \
            if polygonFactory is None else polygonFactory
        self.panelMapping: Mapping[PolygonHelper, PolygonProperties] = {}

    """ Polygon """

    def createPolygon(self, points: List[Point], name: str = "") \
            -> PolygonHelper:
        poly = self.polygonFactory.create(points, name)

        if poly is not None:
            self.createMappingFor(poly)

        return poly

    def insertPolygon(self, idx: int, poly: PolygonHelper) -> None:
        self.polygonFactory.insert(idx, poly)
        self.createMappingFor(poly)

    def appendPolygon(self, poly: PolygonHelper) -> None:
        self.polygonFactory.append(poly)
        self.createMappingFor(poly)

    def getPolygon(self, idx: int) -> Optional[PolygonHelper]:
        self.polygonFactory.get(idx)

    def updateAllPolygonCache(self) -> List[Exception]:
        return self.polygonFactory.update_all_cache()

    def removePolygon(self, poly: PolygonHelper) -> bool:
        if poly in self.polygonFactory:
            self.polygonFactory.remove(poly)
            self.removeMapping(poly)
            return True
        else:
            return False

    def removePolygonByIndex(self, idx: int) -> bool:
        if idx < len(self.polygonFactory):
            poly = self.polygonFactory[idx]
            del self.polygonFactory[idx]
            self.removeMapping(poly)
            return True
        else:
            return False

    """ Mapping """

    def getPropertiesWindowFor(self, poly: int) -> Optional[PolygonProperties]:
        if poly in self.panelMapping:
            pnl = self.panelMapping[poly]

            if pnl is None:
                pnl = PolygonProperties(poly, self.panelParent)
                pnl.propertiesChanged.connect(self.propertiesChange)
                self.panelMapping[poly] = pnl

            return pnl
        else:
            return None

    def getPropertiesWindowByIndex(self, idx: int) \
            -> Optional[PolygonProperties]:
        if idx < len(self.polygonFactory):
            return self.getPropertiesWindowFor(
                self.polygonFactory[idx]
            )
        else:
            return None

    def createMappingFor(self, poly: PolygonHelper) -> None:
        if poly not in self.panelMapping:
            self.panelMapping[poly] = None

    def removeMapping(self, poly: PolygonHelper) -> bool:
        if poly in self.panelMapping:
            pnl = self.panelMapping[poly]
            if pnl is not None:
                pnl.close()
            del(self.panelMapping[poly])
            return True
        else:
            return False

    def clearMapping(self) -> None:
        self.panelMapping.clear()

    def clearAll(self) -> None:
        self.polygonFactory.clear()
        self.panelMapping.clear()

    def generateMapping(self) -> None:
        for poly in self.polygonFactory:
            self.createMappingFor(poly)

    """ Receive changes from user """

    @pyqtSlot(PolygonHelper, bool)
    def propertiesChange(self, poly: PolygonHelper, requireRedraw: bool) \
            -> None:
        self.polygonChanged.emit(poly, requireRedraw)
