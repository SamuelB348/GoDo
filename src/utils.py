from hex_tools import *
import matplotlib.pyplot as plt

Player = int
R = 1
B = 2
Evaluation = float


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
            # différencier le cas en fonction du joueur
            if box.player == player:
                for i in range(1, 4):
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
