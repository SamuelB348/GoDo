from typing import Iterator, Union, Callable
from math import exp
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from hex_tools import *


ActionGopher = Cell
ActionDodo = tuple[Cell, Cell]
Action = Union[ActionGopher, ActionDodo]
Player = int
R = 1
B = 2
State = list[tuple[Cell, Player]]
Score = int
Evaluation = float
Time = int


class Engine:
    def __init__(self, grid: State, hex_size: int, time: Time):
        self.grid: dict[Cell, Player] = dict(grid)
        self.R_hex = {hex_key for hex_key, player in self.grid.items() if player == R}
        self.B_hex = {hex_key for hex_key, player in self.grid.items() if player == B}
        self.size = hex_size
        self.time = time

        # Attributs pour la fonction d'évaluation
        self.grid_weights_R = None
        self.grid_weights_B = None
        # Attributs pour le debug
        self.position_explored = 0

    def update_state(self, grid: State):
        """
        Remet à jour les dictionnaires quand on reçoit un nouveau "state" de l'arbitre
        """

        self.grid: dict[Cell, Player] = dict(grid)
        self.R_hex = {hex_key for hex_key, player in self.grid.items() if player == R}
        self.B_hex = {hex_key for hex_key, player in self.grid.items() if player == B}

    def legals(self, player: Player) -> list[Action]:
        """
        Retourne les coups légaux du joueur en paramètre

        La méthode s'appuie sur les sets red_hex ou blue_hex pour gagner du temps plutôt que d'itérer sur
        toutes les cases du plateau.
        """

        legals: list[Action] = []
        if player == R:
            for box in self.R_hex:
                for i in [1, 2, 3]:
                    if (
                        neighbor(box, i) in self.grid.keys()
                        and self.grid[neighbor(box, i)] == 0
                    ):
                        legals.append((box, neighbor(box, i)))
        elif player == B:
            for box in self.B_hex:
                for i in [0, 4, 5]:
                    if (
                        neighbor(box, i) in self.grid
                        and self.grid[neighbor(box, i)] == 0
                    ):
                        legals.append((box, neighbor(box, i)))
        return legals

    def is_final(self, player: Player) -> bool:
        return len(self.legals(player)) == 0

    def play(self, player: Player, action: Action):
        """
        Joue une action légale et modifie les attributs.

        Il faut à la fois modifier le dictionnaire de toutes les cases (grid) et les sets des cases de chaque joueur
        (red_hex et blue_hex).
        """

        self.grid[action[0]] = 0
        self.grid[action[1]] = player
        self.update_sets(player, action)

    def undo(self, player: Player, action: Action):
        """
        Inverse de la méthode play.
        """

        self.grid[action[0]] = player
        self.grid[action[1]] = 0
        self.reverse_update_sets(player, action)

    def update_sets(self, player: Player, action: Action):
        """
        Met à jour les sets red_hex et blue_hex après une action.
        """

        if player == R:
            self.R_hex.discard(action[0])
            self.R_hex.add(action[1])
        else:
            self.B_hex.discard(action[0])
            self.B_hex.add(action[1])

    def reverse_update_sets(self, player: Player, action: Action):
        """
        Met à jour les sets red_hex et blue_hex après un "undo".
        """

        if player == R:
            self.R_hex.discard(action[1])
            self.R_hex.add(action[0])
        else:
            self.B_hex.remove(action[1])
            self.B_hex.add(action[0])

    def evaluate_v1(self, player: Player) -> Evaluation:
        """
        Fonction d'évaluation de l'état courant du jeu dans lequel est self.
        """

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
        return 1 / nb_moves_r - 1 / nb_moves_b

    def evaluate_v2(self, player: Player) -> Evaluation:
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
        mobility = 1 / nb_moves_r - 1 / nb_moves_b
        position = 0
        for box in self.R_hex:
            position += self.grid_weights_R[box]
        for box in self.B_hex:
            position -= self.grid_weights_B[box]
        return 20*mobility + 5*position

    @staticmethod
    def adaptable_depth(x: int, upper_bound: int, lower_bound: int, critical_point: int) -> int:
        d = upper_bound - ((upper_bound - lower_bound) / (1 + exp(-(x-critical_point))))
        return round(d)

    def alphabeta(self, depth: int, a: float, b: float, player: Player) -> float:
        """
        Minmax avec élagage alpha-beta.
        """

        if depth == 0 or self.is_final(player):
            return self.evaluate_v1(player)
        if player == R:
            best_value = float("-inf")

            for legal in self.legals(player):
                self.play(player, legal)
                best_value = max(best_value, self.alphabeta(depth - 1, a, b, B))
                self.undo(player, legal)
                a = max(a, best_value)
                if a >= b:
                    break  # β cut-off

            return best_value
        else:
            best_value = float("inf")

            for legal in self.legals(player):
                self.play(player, legal)
                best_value = min(best_value, self.alphabeta(depth - 1, a, b, R))
                self.undo(player, legal)
                b = min(b, best_value)
                if a >= b:
                    break  # α cut-off

            return best_value

    def alphabeta_actions(
        self, player: Player, depth: int, a: float, b: float
    ) -> tuple[float, list[Action]]:
        """
        Minmax avec élagage alpha-beta et choix d'une action.
        """

        if depth == 0 or self.is_final(player):
            return self.evaluate_v1(player), []
        if player == R:
            best_value = float("-inf")
            best_legals: list[Action] = []

            for legal in self.legals(player):
                self.play(player, legal)
                v = self.alphabeta(depth - 1, a, b, B)
                self.undo(player, legal)
                if v > best_value:
                    best_value = v
                    best_legals = [legal]
                elif v == best_value:
                    best_legals.append(legal)
                a = max(a, best_value)

            return best_value, best_legals
        else:  # minimizing player
            best_value = float("inf")
            best_legals = []

            for legal in self.legals(player):
                self.play(player, legal)
                v = self.alphabeta(depth - 1, a, b, R)
                self.undo(player, legal)
                if v < best_value:
                    best_value = v
                    best_legals = [legal]
                elif v == best_value:
                    best_legals.append(legal)
                b = min(b, best_value)

            return best_value, best_legals

    def alphabeta_v2(self, depth: int, a: float, b: float, player: Player) -> float:
        """
        Minmax avec élagage alpha-beta.
        """

        if depth == 0 or self.is_final(player):
            return self.evaluate_v2(player)
        if player == R:
            best_value = float("-inf")

            for legal in self.legals(player):
                self.play(player, legal)
                best_value = max(best_value, self.alphabeta_v2(depth - 1, a, b, B))
                self.undo(player, legal)
                a = max(a, best_value)
                if a >= b:
                    break  # β cut-off

            return best_value
        else:
            best_value = float("inf")

            for legal in self.legals(player):
                self.play(player, legal)
                best_value = min(best_value, self.alphabeta_v2(depth - 1, a, b, R))
                self.undo(player, legal)
                b = min(b, best_value)
                if a >= b:
                    break  # α cut-off

            return best_value

    def alphabeta_actions_v2(
        self, player: Player, depth: int, a: float, b: float
    ) -> tuple[float, list[Action]]:
        """
        Minmax avec élagage alpha-beta et choix d'une action.
        """

        if depth == 0 or self.is_final(player):
            return self.evaluate_v2(player), []
        if player == R:
            best_value = float("-inf")
            best_legals: list[Action] = []

            for legal in self.legals(player):
                self.play(player, legal)
                v = self.alphabeta_v2(depth - 1, a, b, B)
                self.undo(player, legal)
                if v > best_value:
                    best_value = v
                    best_legals = [legal]
                elif v == best_value:
                    best_legals.append(legal)
                a = max(a, best_value)

            return best_value, best_legals
        else:  # minimizing player
            best_value = float("inf")
            best_legals = []

            for legal in self.legals(player):
                self.play(player, legal)
                v = self.alphabeta_v2(depth - 1, a, b, R)
                self.undo(player, legal)
                if v < best_value:
                    best_value = v
                    best_legals = [legal]
                elif v == best_value:
                    best_legals.append(legal)
                b = min(b, best_value)

            return best_value, best_legals

    def pplot(self):
        """
        Produit un affichage graphique de la grille de jeu actuelle.
        """

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


Environment = Engine


def start_board(size: int) -> State:
    grid: State = []
    n = size - 1
    for r in range(n, -n - 1, -1):
        q1 = max(-n, r - n)
        q2 = min(n, r + n)
        for q in range(q1, q2 + 1):
            if -q > r + (size - 3):
                grid.append((Cell(q, r), R))
            elif r > -q + (size - 3):
                grid.append((Cell(q, r), B))
            else:
                grid.append((Cell(q, r), 0))
    return grid


def final_result(state: State, score: Score, player: Player):
    pass
