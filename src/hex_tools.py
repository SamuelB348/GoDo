from __future__ import division
from __future__ import print_function
from collections import namedtuple
import math

Point = namedtuple("Point", ["x", "y"])
Cell = namedtuple("Cell", ["q", "r"])


def point_to_str(p: Point) -> str:
    return f"({p.x}, {p.y})"


def hex_to_str(h: Cell) -> str:
    return f"(q: {h.q}, r: {h.r})"


def hex_add(h1: Cell, h2: Cell) -> Cell:
    return Cell(h1.q + h2.q, h1.r + h2.r)


def hex_sub(h1: Cell, h2: Cell) -> Cell:
    return Cell(h1.q - h2.q, h1.r - h2.r)


def scale(h: Cell, k) -> Cell:
    return Cell(h.q * k, h.r * k)


hex_directions = [
    Cell(-1, 0), #0
    Cell(0, 1), #1
    Cell(1, 1), #2
    Cell(1, 0), #3
    Cell(0, -1), #4
    Cell(-1, -1), #5
]


def hex_direction(direction) -> Cell:
    return hex_directions[direction] #retourne la ième direction


def neighbor(h: Cell, direction: int):
    return hex_add(h, hex_direction(direction)) #donne la coord de case ième direction par rapport une case


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
    x = (m.f0 * h.q + m.f1 * h.r) * size.x
    y = (m.f2 * h.q + m.f3 * h.r) * size.y
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
