from hex_tools import *
from typing import Callable
import matplotlib.pyplot as plt

Player = int
R = 1
B = 2
Evaluation = float
Action = tuple[Hex, Hex]
Score = float


class Box:
    def __init__(self, q: int, r: int, p: Player):
        self.coordinates = Hex(q, r)
        self.player = p

    def __str__(self):
        return (
            f"q: {self.coordinates.q}, r: {self.coordinates.r}, couleur: {self.player}"
        )


class Board:
    def __init__(self, boxes: list[Box], n: int):
        self.boxes = boxes
        self.size = n
        self.linkage_table = {box.coordinates.to_tuple(): box for box in boxes}

    def legals(self, player: Player) -> list[tuple[Hex, Hex]]:
        legals: list[tuple[Hex, Hex]] = []
        for box in self.boxes:
            if box.player == player == 1:
                for i in [1, 2, 3]:
                    if (
                        box.coordinates.neighbor(i).to_tuple() in self.linkage_table
                        and self.linkage_table[
                            box.coordinates.neighbor(i).to_tuple()
                        ].player
                        == 0
                    ):
                        legals.append((box.coordinates, box.coordinates.neighbor(i)))
            elif box.player == player == 2:
                for i in [0, 4, 5]:
                    if (
                        box.coordinates.neighbor(i).to_tuple() in self.linkage_table
                        and self.linkage_table[
                            box.coordinates.neighbor(i).to_tuple()
                        ].player
                        == 0
                    ):
                        legals.append((box.coordinates, box.coordinates.neighbor(i)))
        return legals

    def final(self, player: Player) -> bool:
        if len(self.legals(player)) == 0:
            return True
        return False

    def pplot(self):
        plt.figure(figsize=(10, 10))

        layout = Layout(layout_flat, Point(1, -1), Point(0, 0))
        for box in self.boxes:
            corners = polygon_corners(layout, box.coordinates)
            center = hex_to_pixel(layout, box.coordinates)

            # Contours de chaque hexagone
            list_edges_x = []
            list_edges_y = []
            for corner in corners:
                list_edges_x.append(corner.x)
                list_edges_y.append(corner.y)
            list_edges_x.append(list_edges_x[0])
            list_edges_y.append(list_edges_y[0])
            plt.plot(list_edges_x, list_edges_y, color="k")
            if box.player == 1:
                plt.plot(center.x, center.y, marker="o", markersize=10, color="red")
            elif box.player == 2:
                plt.plot(center.x, center.y, marker="o", markersize=10, color="blue")
            plt.text(
                center.x,
                center.y,
                f"{box.coordinates.q}, {box.coordinates.r}",
                horizontalalignment="right",
            )
        plt.xlim(-2 * self.size - 1, 2 * self.size + 1)
        plt.ylim(-2 * self.size - 1, 2 * self.size + 1)
        plt.show()


def start_board(size: int) -> Board:
    list_boxes: list[Box] = []
    n = size - 1
    for r in range(n, -n - 1, -1):
        q1 = max(-n, r - n)
        q2 = min(n, r + n)
        for q in range(q1, q2 + 1):
            if -q > r + (size - 3):
                list_boxes.append(Box(q, r, R))
            elif r > -q + (size - 3):
                list_boxes.append(Box(q, r, B))
            else:
                list_boxes.append(Box(q, r, 0))
    return Board(list_boxes, n)


State = Board
Strategy = Callable[[State, Player], Action]


def play(b: Board, player: Player, action: tuple[Hex, Hex]) -> Board:
    new_boxes: list[Box] = []
    for box in b.boxes:
        if not (
            box.coordinates.q == action[0].q
            and box.coordinates.r == action[0].r
            and box.player == player
        ) and not (
            box.coordinates.q == action[1].q
            and box.coordinates.r == action[1].r
            and box.player == 0
        ):
            new_boxes.append(box)
    new_boxes.append(Box(action[0].q, action[0].r, 0))
    new_boxes.append(Box(action[1].q, action[1].r, player))
    return Board(new_boxes, b.size)


def strategy_brain(board: Board, player: Player) -> Action:  # À faire correctement
    print("à vous de jouer: ", end="")
    # a faire plus tard
    # s = input()
    # print()
    # t = ast.literal_eval(s)
    start_q = int(input("start q :"))
    start_r = int(input("start r :"))
    end_q = int(input("end q :"))
    end_r = int(input("end r :"))
    depart = Hex(start_q, start_r)
    arrive = Hex(end_q, end_r)
    bool = False
    for action in board.legals(player):
        if action[0].q == depart.q and action[0].r == depart.r and action[1].q == arrive.q and action[1].r == arrive.r:
            bool = True
    
    while not bool:
        print("Coup illégal !")
        start_q = int(input("start q :"))
        start_r = int(input("start r :"))
        end_q = int(input("end q :"))
        end_r = int(input("end r :"))
        bool = False
        for action in board.legals(player):
            if action[0].q == depart.q and action[0].r == depart.r and action[1].q == arrive.q and action[1].r == arrive.r:
                bool = True

    return Hex(start_q, start_r), Hex(end_q, end_r)


def dodo(
    strategy_rouge: Strategy, strategy_bleu: Strategy, size: int, debug: bool = False
) -> Score:
    b = start_board(size)
    b.pplot()
    while not (b.final(1) or b.final(2)):
        s = strategy_rouge(b, 1)
        b = play(b, 1, s)
        b.pplot()
        if b.final(2):
            return -1
        else:
            s = strategy_bleu(b, 2)
            b = play(b, 2, s)
            b.pplot()
            if b.final(1):
                return 1
