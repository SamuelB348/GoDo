# Generated code -- CC0 -- No Rights Reserved -- http://www.redblobgames.com/grids/hexagons/

from __future__ import division
from __future__ import print_function
import collections
import math


class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __str__(self):
        return f"({self.x}, {self.y})"


class Hex:
    def __init__(self, q, r, s):
        assert not (round(q + r + s) != 0), "q + r + s must be 0"
        self.q = q
        self.r = r
        self.s = s

    def __add__(self, other):
        return Hex(self.q + other.q, self.r + other.r, self.s + other.s)

    def __sub__(self, other):
        return Hex(self.q - other.q, self.r - other.r, self.s - other.s)

    def scale(self, k):
        return Hex(self.q * k, self.r * k, self.s * k)

    def rotate_left(self):
        return Hex(-self.s, -self.q, -self.r)

    def rotate_right(self):
        return Hex(-self.r, -self.s, -self.q)

    def neighbor(self, direction):
        return self + hex_direction(direction)

    def diagonal_neighbor(self, direction):
        return self + hex_diagonals[direction]

    def length(self):
        return (abs(self.q) + abs(self.r) + abs(self.s)) // 2

    def to_tuple(self):
        return self.q, self.r, self.s

    def __str__(self):
        return f"(q: {self.q}, r: {self.r}, s: {self.s})"


hex_directions = [
    Hex(1, 0, -1),
    Hex(1, -1, 0),
    Hex(0, -1, 1),
    Hex(-1, 0, 1),
    Hex(-1, 1, 0),
    Hex(0, 1, -1),
]


def hex_direction(direction) -> Hex:
    return hex_directions[direction]


hex_diagonals = [
    Hex(2, -1, -1),
    Hex(1, -2, 1),
    Hex(-1, -1, 2),
    Hex(-2, 1, 1),
    Hex(-1, 2, -1),
    Hex(1, 1, -2),
]


class Orientation:
    def __init__(
        self,
        f0: float,
        f1: float,
        f2: float,
        f3: float,
        b0: float,
        b1: float,
        b2: float,
        b3: float,
        start_angle: float,
    ):
        self.f0 = f0
        self.f1 = f1
        self.f2 = f2
        self.f3 = f3
        self.b0 = b0
        self.b1 = b1
        self.b2 = b2
        self.b3 = b3
        self.start_angle = start_angle


class Layout:
    def __init__(self, orientation: Orientation, size: Point, origin: Point):
        self.orientation = orientation
        self.size = size
        self.origin = origin


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
    0.0,
    math.sqrt(3.0) / 2.0,
    math.sqrt(3.0),
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
    return Hex(q, r, -q - r)


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
