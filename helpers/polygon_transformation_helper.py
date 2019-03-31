from typing import Tuple
import math

from rasterizer.polygon_helper import PolygonHelper


Matrix33 = Tuple[
    Tuple[int, int, int],
    Tuple[int, int, int],
    Tuple[int, int, int]
]

IDENTITY_MATRIX: Matrix33 = ((1, 0, 0), (0, 1, 0), (0, 0, 1))


def matmul33(m1: Matrix33, m2: Matrix33) -> None:
    return (
        (
            m1[0][0] * m2[0][0] + m1[0][1] * m2[1][0] + m1[0][2] * m2[2][0],
            m1[0][0] * m2[0][1] + m1[0][1] * m2[1][1] + m1[0][2] * m2[2][1],
            m1[0][0] * m2[0][2] + m1[0][1] * m2[1][2] + m1[0][2] * m2[2][2]
        ),
        (
            m1[1][0] * m2[0][0] + m1[1][1] * m2[1][0] + m1[1][2] * m2[2][0],
            m1[1][0] * m2[0][1] + m1[1][1] * m2[1][1] + m1[1][2] * m2[2][1],
            m1[1][0] * m2[0][2] + m1[1][1] * m2[1][2] + m1[1][2] * m2[2][2]
        ),
        (
            m1[2][0] * m2[0][0] + m1[2][1] * m2[1][0] + m1[2][2] * m2[2][0],
            m1[2][0] * m2[0][1] + m1[2][1] * m2[1][1] + m1[2][2] * m2[2][1],
            m1[2][0] * m2[0][2] + m1[2][1] * m2[1][2] + m1[2][2] * m2[2][2]
        )
    )


def getTranslationMatrix(x, y) -> Matrix33:
    return (
        (1, 0, 0),
        (0, 1, 0),
        (x, y, 1)
    )


def getRotationMatrix(theta) -> Matrix33:
    """
    `theta` must be in degrees!
    """
    rad = math.radians(theta)
    cos = math.cos(rad)
    sin = math.sin(rad)

    return (
        (cos, sin, 0),
        (-sin, cos, 0),
        (0, 0, 1)
    )


def getScalingMatrix(x, y) -> Matrix33:
    return (
        (x, 0, 0),
        (0, y, 0),
        (0, 0, 1)
    )


def getSheeringMatrix(h, v) -> None:
    return (
        (1, v, 0),
        (h, 1, 0),
        (0, 0, 1)
    )


def transformPolygon(transformationMatrix: Matrix33, polygon: PolygonHelper) \
     -> None:
    M = transformationMatrix

    for p in polygon.points:
        x = p.x
        y = p.y

        p.x = round(x * M[0][0] + y * M[1][0] + M[2][0])
        p.y = round(x * M[0][1] + y * M[1][1] + M[2][1])
