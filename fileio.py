from typing import Tuple, List, Optional
import json

from primitives.point import Point

from rasterizer.polygon_helper import PolygonHelper
from rasterizer.polygon_factory import PolygonFactory


class FileIO:
    """
    FileIO helps import and export of polygon data using JSON.
    The generic structure of each object will follow close of `PolygonHelper`.

    {
        "version": "1.0",
        "objects": [
            {
                "name": $strval,
                "points": [
                    [ $intval, $intval ],
                    ...
                ],
                "fillColor": [ $intval, $intval, $intval, $intval ],
                "outlineColor": [ $intval, $intval, $intval, $intval ],
                "outlineThickness": $intval
            },
            ...
        ]
    }
    """

    def __init__(self, polygonFactory: PolygonFactory):
        self.polygonFactory = polygonFactory

    @staticmethod
    def fetchIntegerFrom(obj) -> int:
        if not isinstance(obj, int):
            raise TypeError(
                "invalid parameter type: {}".format(obj.__class__.__name__)
            )

        return obj

    @staticmethod
    def fetchStringFrom(obj) -> str:
        if not isinstance(obj, str):
            raise TypeError(
                "invalid parameter type: {}".format(obj.__class__.__name__)
            )

        return obj

    @staticmethod
    def fetchPointsFrom(obj) -> List[Point]:
        if not isinstance(obj, (tuple, list)):
            raise TypeError(
                "invalid parameter type: {}".format(obj.__class__.__name__)
            )

        points = []

        for i in obj:
            if not isinstance(i, (tuple, list)):
                raise TypeError(
                    "invalid parameter type: {}".format(i.__class__.__name__)
                )

            ln = len(i)
            if ln != 2:
                raise ValueError(
                    "invalid parameter length: ".format(ln)
                )

            for j in i:  # only for two integers
                if not isinstance(j, int):
                    raise TypeError(
                        "invalid parameter type: {}".format(
                            j.__class__.__name__
                        )
                    )

            points.append(Point(i[0], i[1]))

        return points

    @staticmethod
    def fetchColorFrom(obj) -> Tuple[int, int, int, int]:
        if not isinstance(obj, (tuple, list)):
            raise TypeError(
                "invalid parameter type: {}".format(obj.__class__.__name__)
            )

        ln = len(obj)
        if ln != 4:
            raise ValueError(
                "invalid parameter length: ".format(ln)
            )

        for i in obj:  # only for four integers
            if not isinstance(i, int):
                raise TypeError(
                    "invalid parameter type: {}".format(
                        i.__class__.__name__
                    )
                )
            elif i < 0 or i > 255:
                raise ValueError(
                    "invalid parameter value: {}".format(i)
                )

        return (obj[0], obj[1], obj[2], obj[3])

    @staticmethod
    def createPolygonHelperFromObject(json: object) -> PolygonHelper:
        name = FileIO.fetchStringFrom(json["name"])
        points = FileIO.fetchPointsFrom(json["points"])
        fillColor = FileIO.fetchColorFrom(json["fillColor"])
        outlineColor = FileIO.fetchColorFrom(json["outlineColor"])
        outlineThickness = FileIO.fetchIntegerFrom(json["outlineThickness"])

        return PolygonHelper(
            *points,
            name=name,
            fillColor=fillColor,
            outlineColor=outlineColor,
            outlineThickness=outlineThickness
        )

    def readFile(self, fn: str) -> Tuple[bool, List[Exception]]:
        """
        This function automatically clears out the `polygonFactory`
        """

        ret = True
        exc = []

        try:
            with open(fn, 'r') as fp:
                obj = json.load(fp)

                if obj["version"] != "1.0":
                    raise ValueError(
                        "invalid file version: {}".format(obj["version"])
                    )
                elif not isinstance(obj["objects"], list):
                    raise TypeError(
                        "invalid object list type: {}".format(
                            obj["objects"].__class__.__name__
                        )
                    )

                for poly in obj["objects"]:
                    try:
                        self.polygonFactory.append(
                            FileIO.createPolygonHelperFromObject(poly)
                        )
                    except Exception as ex:
                        exc.append(ex)
        except Exception as ex:
            ret = False
            exc.append(ex)

        return ret, exc

    @staticmethod
    def createObjectFromPolygonHelper(obj: PolygonHelper) -> object:
        return {
            "name": obj.name,
            "points": [(p.x, p.y) for p in obj.points],
            "fillColor": obj.fillColor,
            "outlineColor": obj.outlineColor,
            "outlineThickness": obj.outlineThickness
        }

    def writeFile(self, fn: str) -> Tuple[bool, Optional[Exception]]:
        try:
            with open(fn, 'w') as fp:
                json.dump(
                    {
                        "version": "1.0",
                        "objects": [
                            FileIO.createObjectFromPolygonHelper(i)
                            for i in self.polygonFactory
                        ]
                    },
                    fp
                )
        except Exception as ex:
            return False, ex

        return True, None
