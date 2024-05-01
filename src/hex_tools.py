from __future__ import division
from __future__ import print_function
from collections import namedtuple
import math

Point = namedtuple('Point', ['x', 'y'])
Hex = namedtuple('Hex', ['q', 'r'])


def point_to_str(p: Point) -> str:
    return f"({p.x}, {p.y})"


def hex_add(h1: Hex, h2: Hex) -> Hex:
    return Hex(h1.q + h2.q, h1.r + h2.r)


def hex_sub(h1: Hex, h2: Hex) -> Hex:
    return Hex(h1.q - h2.q, h1.r - h2.r)


def scale(h: Hex, k) -> Hex:
    return Hex(h.q * k, h.r * k)


def rotate_left(h: Hex) -> Hex:
    return Hex(-h.q, -h.r)


def rotate_right(h: Hex) -> Hex:
    return Hex(-h.r, -h.q)


hex_directions = [
    Hex(-1, 0),
    Hex(0, 1),
    Hex(1, 1),
    Hex(1, 0),
    Hex(0, -1),
    Hex(-1, -1),
]


def hex_direction(direction) -> Hex:
    return hex_directions[direction]


def neighbor(h: Hex, direction: int):
    return hex_add(h, hex_direction(direction))


def hex_to_str(h: Hex) -> str:
    return f"(q: {h.q}, r: {h.r})"


Orientation = namedtuple("Orientation", ["f0", "f1", "f2", "f3", "b0", "b1", "b2", "b3", "start_angle"])
Layout = namedtuple("Layout", ["orientation", "size", "origin"])


layout_pointy = Orientation(
    math.sqrt(3.0),
    math.sqrt(3.0) / 2.0,
    0.0,
    3.0 / 2.0,
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


def hex_to_pixel(layout: Layout, h: Hex) -> Point:
    m = layout.orientation
    size = layout.size
    origin = layout.origin
    x = (m.f0 * h.q + m.f1 * h.r) * size.x
    y = (m.f2 * h.q + m.f3 * h.r) * size.y
    return Point(x + origin.x, y + origin.y)


def pixel_to_hex(layout: Layout, p: Point) -> Hex:
    m = layout.orientation
    size = layout.size
    origin = layout.origin
    pt = Point((p.x - origin.x) / size.x, (p.y - origin.y) / size.y)
    q = m.b0 * pt.x + m.b1 * pt.y
    r = m.b2 * pt.x + m.b3 * pt.y
    return Hex(q, r)


def hex_corner_offset(layout: Layout, corner: int) -> Point:
    m = layout.orientation
    size = layout.size
    angle = 2.0 * math.pi * (m.start_angle - corner) / 6.0
    return Point(size.x * math.cos(angle), size.y * math.sin(angle))


def polygon_corners(layout: Layout, h: Hex) -> list[Point]:
    corners: list[Point] = []
    center = hex_to_pixel(layout, h)
    for i in range(0, 6):
        offset = hex_corner_offset(layout, i)
        corners.append(Point(center.x + offset.x, center.y + offset.y))
    return corners
