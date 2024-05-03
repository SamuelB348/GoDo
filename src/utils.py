from typing import Callable
import random
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from hex_tools import *


Player = int
R = 1
B = 2
Evaluation = float
Action = tuple[Hex, Hex]
Score = float


class Board:
    def __init__(self, grid: dict[Hex, Player], n: int):
        self.grid = grid
        self.red_hex = [hex_key for hex_key, player in grid.items() if player == R]
        self.blue_hex = [hex_key for hex_key, player in grid.items() if player == B]
        self.size = n

    def legals(self, player: Player) -> list[Action]:
        legals: list[Action] = []
        if player == R:
            for box in self.red_hex:
                for i in [1, 2, 3]:
                    if (
                        neighbor(box, i) in self.grid
                        and self.grid[neighbor(box, i)] == 0
                    ):
                        legals.append((box, neighbor(box, i)))
        elif player == B:
            for box in self.blue_hex:
                for i in [0, 4, 5]:
                    if (
                        neighbor(box, i) in self.grid
                        and self.grid[neighbor(box, i)] == 0
                    ):
                        legals.append((box, neighbor(box, i)))
        return legals

    def final(self, player: Player) -> bool:
        return len(self.legals(player)) == 0

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
            self.red_hex.remove(action[0])
            self.red_hex.append(action[1])
        else:
            self.blue_hex.remove(action[0])
            self.blue_hex.append(action[1])

    def reverse_update_dicts(self, player: Player, action: Action):
        if player == R:
            self.red_hex.remove(action[1])
            self.red_hex.append(action[0])
        else:
            self.blue_hex.remove(action[1])
            self.blue_hex.append(action[0])

    def evaluate_v1(self, player: Player):
        nb_moves_r: int = len(self.legals(R))
        nb_moves_b: int = len(self.legals(B))
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


State = Board
Strategy = Callable[[State, Player], Action]


def alphabeta(grid: State, depth: int, a: float, b: float, player: Player) -> float:
    if depth == 0 or grid.final(player):
        return grid.evaluate_v1(player)
    if player == R:
        best_value = float('-inf')
        for legal in grid.legals(player):
            grid.play(player, legal)
            best_value = max(best_value, alphabeta(grid, depth-1, a, b, B))
            grid.undo(player, legal)
            a = max(a, best_value)
            if a >= b:
                break  # β cut-off
        return best_value
    else:  # minimizing player
        best_value = float('inf')
        for legal in grid.legals(player):
            grid.play(player, legal)
            best_value = min(best_value, alphabeta(grid, depth-1, a, b, 2))
            grid.undo(player, legal)
            b = min(b, best_value)
            if a >= b:
                break  # α cut-off
        return best_value


def alphabeta_actions(grid: State, player: Player, depth: int) -> tuple[float, list[Action]]:
    if depth == 0 or grid.final(player):
        return grid.evaluate_v1(player), []
    if player == R:
        best_value = float('-inf')
        best_legals: list[Action] = []
        for legal in grid.legals(player):
            grid.play(player, legal)
            v = alphabeta(grid, depth, float('-inf'), float('inf'), B)
            grid.undo(player, legal)
            if v > best_value:
                best_value = v
                best_legals = [legal]
            elif v == best_value:
                best_legals.append(legal)
        return best_value, best_legals
    else:  # minimizing player
        best_value = float('inf')
        best_legals = []
        for legal in grid.legals(player):
            grid.play(player, legal)
            v = alphabeta(grid, depth, float('-inf'), float('inf'), R)
            grid.undo(player, legal)
            if v < best_value:
                best_value = v
                best_legals = [legal]
            elif v == best_value:
                best_legals.append(legal)
        return best_value, best_legals


def strategy_alphabeta_random(grid: State, player: Player) -> Action:
    actions = alphabeta_actions(grid, player, 4)
    list_moves: list[Action] = actions[1]
    # print(actions[0])
    return random.choice(list_moves)


def strategy_brain(board: Board, player: Player) -> Action:
    print("à vous de jouer: ", end="")
    start_q = int(input("start q :"))
    start_r = int(input("start r :"))
    end_q = int(input("end q :"))
    end_r = int(input("end r :"))
    depart = Hex(start_q, start_r)
    arrive = Hex(end_q, end_r)

    while (depart, arrive) not in board.legals(player):
        print("Coup illégal !")
        start_q = int(input("start q :"))
        start_r = int(input("start r :"))
        end_q = int(input("end q :"))
        end_r = int(input("end r :"))
        depart = Hex(start_q, start_r)
        arrive = Hex(end_q, end_r)

    return depart, arrive


def strategy_random(board: Board, player: Player) -> Action:
    return random.choice(board.legals(player))


def strategy_first_legal(board: Board, player: Player) -> Action:
    return board.legals(player)[0]


def dodo(strategy_rouge: Strategy, strategy_bleu: Strategy, size: int) -> Score:
    b = start_board(size)
    # b.pplot2()
    while True:
        s = strategy_rouge(b, 1)
        b.play(1, s)
        b.pplot2()
        if b.final(2):
            return -1
        s = strategy_bleu(b, 2)
        b.play(2, s)
        b.pplot2()
        if b.final(1):
            return 1
