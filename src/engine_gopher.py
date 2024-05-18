from math import exp, log
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from hex_tools import *


ActionGopher = Cell
Player = int
R = 1
B = 2
State = list[tuple[Cell, Player]]
Score = int
Evaluation = float
Time = int


class EngineGopher:
    def __init__(self, grid: State, hex_size: int, time: Time):
        self.grid: dict[Cell, Player] = dict(grid)
        self.R_hex: set[Cell] = {hex_key for hex_key, player in self.grid.items() if player == R}
        self.B_hex: set[Cell] = {hex_key for hex_key, player in self.grid.items() if player == B}
        self.Empty_hex: set[Cell] = {hex_key for hex_key, player in self.grid.items() if player == 0}

        self.size: int = hex_size
        self.time: Time = time

        # Attributs pour le debug
        self.position_explored: int = 0

    def update_state(self, grid: State):
        """
        Remet à jour les dictionnaires quand on reçoit un nouveau "state" de l'arbitre
        """

        self.grid = dict(grid)
        self.R_hex = {hex_key for hex_key, player in self.grid.items() if player == R}
        self.B_hex = {hex_key for hex_key, player in self.grid.items() if player == B}
        self.Empty_hex = {hex_key for hex_key, player in self.grid.items() if player == 0}

    def legals(self, player: Player) -> list[ActionGopher]:
        if player == R:
            for box in self.Empty_hex:
                nb_neighbors = 0
                for i in [0, 1, 2, 3, 4, 5]:
                    if self.grid[neighbor(box, i)] == R:
                        nb_neighbors = 0
                        break
                    elif (
                            neighbor(box, i) in self.grid
                            and self.grid[neighbor(box, i)] == B
                    ):
                        nb_neighbors += 1
                if nb_neighbors == 1:
                    yield box, neighbor(box, player)
        elif player == B:
            for box in self.Empty_hex:
                nb_neighbors = 0
                for i in [0, 1, 2, 3, 4, 5]:
                    if self.grid[neighbor(box, i)] == B:
                        nb_neighbors = 0
                        break
                    elif (
                            neighbor(box, i) in self.grid
                            and self.grid[neighbor(box, i)] == R
                    ):
                        nb_neighbors += 1
                if nb_neighbors == 1:
                    yield box, neighbor(box, player)

    def is_final(self, player: Player) -> bool:
        return len(self.legals(player)) == 0

    def play(self, player: Player, action: ActionGopher):
        self.grid[action] = player
        self.update_sets(player, action)

    def undo(self, player: Player, action: ActionGopher):
        self.grid[action] = 0
        self.reverse_update_sets(player, action)

    def update_sets(self, player: Player, action: ActionGopher):
        """
        Met à jour les sets R_hex et B_hex et Empty_hex après une action.
        """
        if player == R:
            self.R_hex.add(action)
        else:
            self.B_hex.add(action)
        self.Empty_hex.discard(action)

    def reverse_update_sets(self, player: Player, action: ActionGopher):
        """
        Met à jour les sets R_hex et B_hex et Empty_hex après un "undo".
        """
        if player == R:
            self.R_hex.discard(action)
        else:
            self.B_hex.discard(action)
        self.Empty_hex.add(action)

    def neighbors(self, cell: Cell, player: Player) -> dict[Cell, Player]:
        neighbors: dict[Cell, Player] = {}
        if player == R:
            for i in [0, 1, 2, 3, 4, 5]:
                if neighbor(cell, i) in self.grid:
                    neighbors[neighbor(cell, i)] = self.grid[neighbor(cell, i)]
        if player == B:
            for i in [0, 1, 2, 3, 4, 5]:
                if neighbor(cell, i) in self.grid:
                    neighbors[neighbor(cell, i)] = self.grid[neighbor(cell, i)]
        return neighbors

    def evaluate_test(self, player: Player) -> Evaluation:
        pass

    @staticmethod
    def adaptable_depth_v1(
        x: int, upper_bound: int, lower_bound: int, critical_point: int
    ) -> int:
        d = upper_bound - (
            (upper_bound - lower_bound) / (1 + exp(-(x - critical_point)))
        )
        return round(d)

    @staticmethod
    def adaptable_depth_v2(x: int, y: int,  nb: int, max_depth: int) -> int:
        d = log(nb)/(log(x)*log(y)) + 2
        return min(round(d), max_depth)

    def alphabeta_v1(
        self,
        depth: int,
        a: float,
        b: float,
        player: Player,
    ) -> float:
        """
        Minmax avec élagage alpha-beta.
        """
        pass

    def alphabeta_actions_v1(
        self,
        depth: int,
        a: float,
        b: float,
        player: Player,
    ) -> tuple[float, list[ActionGopher]]:
        """
        Minmax avec élagage alpha-beta et choix d'une action.
        """
        pass

    def pplot(self):
        """
        Produit un affichage graphique de la grille de jeu actuelle.
        """

        plt.figure(figsize=(10, 10))
        layout = Layout(layout_pointy, Point(1, -1), Point(0, 0))

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

