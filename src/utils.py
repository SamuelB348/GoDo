from typing import Callable
import random
import matplotlib.pyplot as plt
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
        self.size = n

    def legals(self, player: Player) -> list[Action]:
        legals: list[Action] = []
        for box in self.grid:
            if self.grid[box] == player == 1:
                for i in [1, 2, 3]:
                    if (
                        neighbor(box, i) in self.grid
                        and self.grid[neighbor(box, i)] == 0
                    ):
                        legals.append((box, neighbor(box, i)))
            elif self.grid[box] == player == 2:
                for i in [0, 4, 5]:
                    if (
                        neighbor(box, i) in self.grid
                        and self.grid[neighbor(box, i)] == 0
                    ):
                        legals.append((box, neighbor(box, i)))
        return legals

    def final(self, player: Player) -> bool:
        if len(self.legals(player)) == 0:
            return True
        return False

    def play(self, player: Player, action: Action):
        new_grid = self.grid.copy()
        new_grid[action[0]] = 0
        new_grid[action[1]] = player
        return Board(new_grid, self.size)

    def pplot(self):
        plt.figure(figsize=(10, 10))

        layout = Layout(layout_flat, Point(1, -1), Point(0, 0))
        for box in self.grid:
            corners = polygon_corners(layout, box)
            center = hex_to_pixel(layout, box)

            # Contours de chaque hexagone
            list_edges_x = []
            list_edges_y = []
            for corner in corners:
                list_edges_x.append(corner.x)
                list_edges_y.append(corner.y)
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


def dodo(strategy_rouge: Strategy, strategy_bleu: Strategy, size: int) -> Score:
    b = start_board(size)
    b.pplot()
    while True:
        s = strategy_rouge(b, 1)
        b = b.play(1, s)
        if b.final(2):
            b.pplot()
            return -1
        s = strategy_bleu(b, 2)
        b = b.play(2, s)
        if b.final(1):
            b.pplot()
            return 1
