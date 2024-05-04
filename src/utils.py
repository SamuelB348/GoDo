import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import random
from hex_tools import *
from typing import Iterator


Player = int
R = 1
B = 2
Evaluation = float
Action = tuple[Hex, Hex]
Score = float


class Board:
    def __init__(self, grid: dict[Hex, Player], n: int):
        self.grid = grid
        self.red_hex = {hex_key for hex_key, player in grid.items() if player == R}
        self.blue_hex = {hex_key for hex_key, player in grid.items() if player == B}
        self.size = n

    def legals(self, player: Player) -> Iterator[Action]:
        legals: list[Action] = []
        if player == R:
            for box in self.red_hex:
                for i in [1, 2, 3]:
                    if (
                        neighbor(box, i) in self.grid
                        and self.grid[neighbor(box, i)] == 0
                    ):
                        yield box, neighbor(box, i)
        elif player == B:
            for box in self.blue_hex:
                for i in [0, 4, 5]:
                    if (
                        neighbor(box, i) in self.grid
                        and self.grid[neighbor(box, i)] == 0
                    ):
                        yield box, neighbor(box, i)
        return legals

    def final(self, player: Player) -> bool:
        return len(list(self.legals(player))) == 0

    def play(self, player: Player, action: Action):
        self.grid[action[0]] = 0
        self.grid[action[1]] = player
        self.update_dicts(player, action)

    def undo(self, player: Player, action: Action):
        self.grid[action[0]] = player
        self.grid[action[1]] = 0
        self.reverse_update_dicts(player, action)

    def update_dicts(self, player: Player, action: Action):
        if player == R:
            self.red_hex.discard(action[0])
            self.red_hex.add(action[1])
        else:
            self.blue_hex.discard(action[0])
            self.blue_hex.add(action[1])

    def reverse_update_dicts(self, player: Player, action: Action):
        if player == R:
            self.red_hex.discard(action[1])
            self.red_hex.add(action[0])
        else:
            self.blue_hex.remove(action[1])
            self.blue_hex.add(action[0])

    def evaluate_v1(self, player: Player):
        nb_moves_r: int = len(list(self.legals(R)))
        nb_moves_b: int = len(list(self.legals(B)))
        if player == R and nb_moves_r == 0:
            return 10000
        if player == B and nb_moves_b == 0:
            return -10000
        if player == R and nb_moves_b == 0:
            return -10000
        if player == B and nb_moves_r == 0:
            return 10000
        return 1/nb_moves_r - 1/nb_moves_b

    def pplot(self):
        plt.figure(figsize=(10, 10))

        layout = Layout(layout_flat, Point(1, -1), Point(0, 0))
        for box in self.grid:
            corners = polygon_corners(layout, box)
            center = hex_to_pixel(layout, box)

            # Contours de chaque hexagone
            list_edges_x = [corner.x for corner in corners]
            list_edges_y = [corner.y for corner in corners]
            list_edges_x.append(list_edges_x[0])
            list_edges_y.append(list_edges_y[0])
            plt.plot(list_edges_x, list_edges_y, color="k")

            if self.grid[box] == 1:
                plt.plot(center.x, center.y, marker="o", markersize=10, color="red")
            elif self.grid[box] == 2:
                plt.plot(center.x, center.y, marker="o", markersize=10, color="blue")
            plt.text(
                center.x,
                center.y,
                f"{box.q}, {box.r}",
                horizontalalignment="right",
            )
        plt.xlim(-2 * self.size - 1, 2 * self.size + 1)
        plt.ylim(-2 * self.size - 1, 2 * self.size + 1)
        plt.show()

    def pplot2(self):
        plt.figure(figsize=(10, 10))
        layout = Layout(layout_flat, Point(1, -1), Point(0, 0))

        for box, color in self.grid.items():
            corners = polygon_corners(layout, box)
            center = hex_to_pixel(layout, box)

            # Contours de chaque hexagone
            list_edges_x = [corner.x for corner in corners]
            list_edges_y = [corner.y for corner in corners]
            list_edges_x.append(list_edges_x[0])
            list_edges_y.append(list_edges_y[0])
            if color == 1:
                polygon = Polygon(
                    corners,
                    closed=True,
                    edgecolor="k",
                    facecolor="red",
                    alpha=0.8,
                    linewidth=2,
                )
            elif color == 2:
                polygon = Polygon(
                    corners,
                    closed=True,
                    edgecolor="k",
                    facecolor="blue",
                    alpha=0.8,
                    linewidth=2,
                )
            else:
                polygon = Polygon(
                    corners,
                    closed=True,
                    edgecolor="k",
                    facecolor="none",
                    alpha=0.8,
                    linewidth=2,
                )
            plt.gca().add_patch(polygon)
            plt.text(
                center.x,
                center.y,
                f"{box.q}, {box.r}",
                horizontalalignment="right",
            )
        plt.xlim(-2 * self.size - 1, 2 * self.size + 1)
        plt.ylim(-2 * self.size - 1, 2 * self.size + 1)
        plt.show()


def start_board(size: int) -> Board:
    grid: dict[Hex, Player] = {}
    n = size - 1
    for r in range(n, -n - 1, -1):
        q1 = max(-n, r - n)
        q2 = min(n, r + n)
        for q in range(q1, q2 + 1):
            if -q > r + (size - 3):
                grid[Hex(q, r)] = R
            elif r > -q + (size - 3):
                grid[Hex(q, r)] = B
            else:
                grid[Hex(q, r)] = 0
    return Board(grid, n)
