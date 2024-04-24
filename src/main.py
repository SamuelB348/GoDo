import matplotlib.pyplot as plt
from utils import *


def test_map():
    board = set()
    n = 4

    for q in range(-n, n + 1):
        r1 = max(-n, -q - n)
        r2 = min(n, -q + n)
        for r in range(r1, r2 + 1):
            board.add(Hex(q, r, -q - r))
    plt.figure(figsize=(10, 10))

    layout = Layout(layout_flat, Point(1, 1), Point(0, 0))
    for hexagon in board:
        corners = polygon_corners(layout, hexagon)
        center = hex_to_pixel(layout, hexagon)
        # Contours de chaque hexagone
        list_edges_x = []
        list_edges_y = []
        for corner in corners:
            list_edges_x.append(corner.x)
            list_edges_y.append(corner.y)
        list_edges_x.append(list_edges_x[0])
        list_edges_y.append(list_edges_y[0])
        plt.plot(list_edges_x, list_edges_y, color='blue')
        plt.plot(center.x, center.y, marker='o', color='red')

    plt.xlim(-2*n-1, 2*n+1)  # Limite des abscisses de 0 à 6
    plt.ylim(-2*n-1, 2*n+1)
    plt.show()

test_map()