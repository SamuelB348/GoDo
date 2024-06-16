from __future__ import division
from __future__ import print_function
from collections import namedtuple
import math

from types_constants import Cell

Point = namedtuple("Point", ["x", "y"])


hex_directions = [
    (-1, 0),
    (0, 1),
    (1, 1),
    (1, 0),
    (0, -1),
    (-1, -1),
]


def hex_direction(direction) -> Cell:
    return hex_directions[direction]


def neighbor(h: Cell, direction: int):
    d = hex_directions[direction]
    return h[0] + d[0], h[1] + d[1]


Orientation = namedtuple(
    "Orientation", ["f0", "f1", "f2", "f3", "b0", "b1", "b2", "b3", "start_angle"]
)
Layout = namedtuple("Layout", ["orientation", "size", "origin"])


layout_pointy = Orientation(
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

layout_flat = Orientation(
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
    m = layout.orientation
    size = layout.size
    origin = layout.origin
    x = (m.f0 * h[0] + m.f1 * h[1]) * size.x
    y = (m.f2 * h[0] + m.f3 * h[1]) * size.y
    return Point(x + origin.x, y + origin.y)


def hex_corner_offset(layout: Layout, corner: int) -> Point:
    m = layout.orientation
    size = layout.size
    angle = 2.0 * math.pi * (m.start_angle - corner) / 6.0
    return Point(size.x * math.cos(angle), size.y * math.sin(angle))


def polygon_corners(layout: Layout, h: Cell) -> list[Point]:
    corners: list[Point] = []
    center = hex_to_pixel(layout, h)
    for i in range(0, 6):
        offset = hex_corner_offset(layout, i)
        corners.append(Point(center.x + offset.x, center.y + offset.y))
    return corners
