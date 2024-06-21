"""
This section gives some utilities to manipulate efficiently hexagonal grids and their
representations.

It was made possible thanks to: https://www.redblobgames.com/grids/hexagons/
"""

from typing import NamedTuple
import math

from types_constants import Cell


class Point(NamedTuple):
    """
    Point class that will be used to display a hexagonal grid.
    It has 2 coordinates representing a point in the plane.
    """

    x: float
    y: float


# The 6 directions you can go towards on a hexagonal grid.
# It depends on the way you orient the grid. On a Dodo grid it would be:
# (-1, 0)  -> NW
# (0, 1)   -> N
# (1, 1)   -> NE
# (1, 0)   -> SE
# (0, -1)  -> S
# (-1, -1) -> SW
hex_directions: list[tuple[int, int]] = [
    (-1, 0),
    (0, 1),
    (1, 1),
    (1, 0),
    (0, -1),
    (-1, -1),
]


def hex_direction(direction: int) -> Cell:
    """
    Returns a direction based on its index in the hex_directions list.

    :param direction: the index of the direction in the hex_directions list
    :return: the corresponding direction as a tuple
    """

    return hex_directions[direction]


def neighbor(h: Cell, direction: int):
    """
    Computes the neighbor Cell of h, given a certain direction.

    :param h: a hexagonal cell
    :param direction: the index of the direction in the hex_directions list
    :return: the neighbor towards the given direction
    """

    d = hex_directions[direction]
    return h[0] + d[0], h[1] + d[1]


class Orientation(NamedTuple):
    """
    Orientation class, useful to orient the grid and the configuration of the cells,
    especially when you want to display it.
    """

    f0: float
    f1: float
    f2: float
    f3: float
    b0: float
    b1: float
    b2: float
    b3: float
    start_angle: float


class Layout(NamedTuple):
    """
    Layout class, containing an Orientation, a size and an origin.
    This class is a utility to display a hexagonal grid.
    """

    orientation: Orientation
    size: Point
    origin: Point


# Orientation to orient the cells with pointy tops.
layout_pointy: Orientation = Orientation(
    math.sqrt(3.0),
    -math.sqrt(3.0) / 2.0,
    0.0,
    -3.0 / 2.0,
    math.sqrt(3.0) / 3.0,
    -1.0 / 3.0,
    0.0,
    2.0 / 3.0,
    0.5,
)


# Orientation to orient the cells with flat tops.
layout_flat: Orientation = Orientation(
    3.0 / 2.0,
    -3.0 / 2.0,
    -math.sqrt(3.0) / 2.0,
    -math.sqrt(3.0) / 2.0,
    2.0 / 3.0,
    0.0,
    -1.0 / 3.0,
    math.sqrt(3.0) / 3.0,
    0.0,
)


def hex_to_pixel(layout: Layout, h: Cell) -> Point:
    """
    Converts a hexagonal Cell into a pixel (i.e. a point in the plane) given a certain Layout.

    :param layout: a Layout, as defined above
    :param h: a hexagonal Cell you want to convert into a pixel (a Point)
    :return: a Point representing the coordinates of h in the plane, given a certain Layout.
    """

    m: Orientation = layout.orientation
    size: Point = layout.size
    origin: Point = layout.origin
    x: float = (m.f0 * h[0] + m.f1 * h[1]) * size.x
    y: float = (m.f2 * h[0] + m.f3 * h[1]) * size.y
    return Point(x + origin.x, y + origin.y)


def hex_corner_offset(layout: Layout, corner: int) -> Point:
    """
    Computes the offset you must apply to any Cell to have the coordinates of one of the 6 corners.

    :param layout: a Layout, as defined above
    :param corner: an integer representing one of the 6 corners around a hexagonal Cell
    :return: a Point representing the offset to apply to have the coordinates of a given corner
    """

    m: Orientation = layout.orientation
    size: Point = layout.size
    angle: float = 2.0 * math.pi * (m.start_angle - corner) / 6.0
    return Point(size.x * math.cos(angle), size.y * math.sin(angle))


def polygon_corners(layout: Layout, h: Cell) -> list[Point]:
    """
    Compute the coordinates of all the corners of a given Cell, given a specific layout.

    :param layout: a Layout, as defined above
    :param h: a Cell whose corners you want to know
    :return: a list of corners (i.e. a list of Points)
    """
    corners: list[Point] = []
    center: Point = hex_to_pixel(layout, h)
    for i in range(0, 6):
        offset: Point = hex_corner_offset(layout, i)
        corners.append(Point(center.x + offset.x, center.y + offset.y))
    return corners
