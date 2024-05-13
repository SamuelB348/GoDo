import copy
import random
from typing import Optional
from math import exp, log
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from hex_tools import *


ActionDodo = tuple[Cell, Cell]
Player = int
R = 1
B = 2
State = list[tuple[Cell, Player]]
Score = int
Evaluation = float
Time = int


class EngineDodo:
    def __init__(self, hex_size: int, time: Time):
        self.grid: Optional[dict[Cell, Player], None] = None
        self.R_hex: Optional[set[Cell], None] = None
        self.B_hex: Optional[set[Cell], None] = None

        self.size: int = hex_size
        self.nb_checkers: int = ((self.size+1)*self.size)//2 + (self.size - 1)
        self.time: Time = time

        # Attributs pour la fonction d'évaluation
        self.grid_weights_R: Optional[dict[Cell, float], None] = None
        self.grid_weights_B: Optional[dict[Cell, float], None] = None

        # Attributs pour le debug
        self.position_explored: int = 0

    def back_to_start_board(self):
        self.grid = dict()
        n = self.size - 1
        for r in range(n, -n - 1, -1):
            q1 = max(-n, r - n)
            q2 = min(n, r + n)
            for q in range(q1, q2 + 1):
                if -q > r + (self.size - 3):
                    self.grid[Cell(q, r)] = R
                elif r > -q + (self.size - 3):
                    self.grid[Cell(q, r)] = B
                else:
                    self.grid[Cell(q, r)] = 0
        self.R_hex = {hex_key for hex_key, player in self.grid.items() if player == R}
        self.B_hex = {hex_key for hex_key, player in self.grid.items() if player == B}

    @staticmethod
    def add_dicts(dict1, dict2, player: Player):
        for key in dict2.keys():
            if dict2[key] == player:
                dict1[key] += 1

    def generate_grid_heatmaps(self, nb_games: int):
        self.grid_weights_R: dict[Cell, float] = copy.deepcopy(self.grid)
        self.grid_weights_B: dict[Cell, float] = copy.deepcopy(self.grid)
        for el in self.grid_weights_R.keys():
            self.grid_weights_R[el] = 0
            self.grid_weights_B[el] = 0

        victory_count_r: int = 0
        victory_count_b: int = 0

        for i in range(nb_games):
            while True:
                act: ActionDodo = random.choice(self.legals(R))
                self.play(R, act)
                if self.is_final(B):
                    victory_count_b += 1
                    self.add_dicts(self.grid_weights_B, self.grid, B)
                    break
                act: ActionDodo = random.choice(self.legals(B))
                self.play(B, act)
                if self.is_final(R):
                    victory_count_r += 1
                    self.add_dicts(self.grid_weights_R, self.grid, R)
                    break

        for el in self.grid_weights_R:
            self.grid_weights_R[el] /= victory_count_r
            self.grid_weights_B[el] /= victory_count_b
        self.back_to_start_board()

    def update_state(self, grid: State):
        """
        Remet à jour les dictionnaires quand on reçoit un nouveau "state" de l'arbitre
        """

        self.grid: dict[Cell, Player] = dict(grid)
        self.R_hex = {hex_key for hex_key, player in self.grid.items() if player == R}
        self.B_hex = {hex_key for hex_key, player in self.grid.items() if player == B}

    def legals(self, player: Player) -> list[ActionDodo]:
        """
        Retourne les coups légaux du joueur en paramètre

        La méthode s'appuie sur les sets red_hex ou blue_hex pour gagner du temps plutôt que d'itérer sur
        toutes les cases du plateau.
        """

        legals: list[ActionDodo] = []
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

    def play(self, player: Player, action: ActionDodo):
        """
        Joue une action légale et modifie les attributs.

        Il faut à la fois modifier le dictionnaire de toutes les cases (grid) et les sets des cases de chaque joueur
        (red_hex et blue_hex).
        """

        self.grid[action[0]] = 0
        self.grid[action[1]] = player
        self.update_sets(player, action)

    def undo(self, player: Player, action: ActionDodo):
        """
        Inverse de la méthode play.
        """

        self.grid[action[0]] = player
        self.grid[action[1]] = 0
        self.reverse_update_sets(player, action)

    def update_sets(self, player: Player, action: ActionDodo):
        """
        Met à jour les sets red_hex et blue_hex après une action.
        """

        if player == R:
            self.R_hex.discard(action[0])
            self.R_hex.add(action[1])
        else:
            self.B_hex.discard(action[0])
            self.B_hex.add(action[1])

    def reverse_update_sets(self, player: Player, action: ActionDodo):
        """
        Met à jour les sets red_hex et blue_hex après un "undo".
        """

        if player == R:
            self.R_hex.discard(action[1])
            self.R_hex.add(action[0])
        else:
            self.B_hex.remove(action[1])
            self.B_hex.add(action[0])

    def neighbors(self, cell: Cell, player: Player) -> dict[Cell, Player]:
        neighbors: dict[Cell, Player] = {}
        if player == R:
            for i in [1, 2, 3]:
                if neighbor(cell, i) in self.grid:
                    neighbors[neighbor(cell, i)] = self.grid[neighbor(cell, i)]
        if player == B:
            for i in [0, 4, 5]:
                if neighbor(cell, i) in self.grid:
                    neighbors[neighbor(cell, i)] = self.grid[neighbor(cell, i)]
        return neighbors

    def nb_pins(self, player: Player) -> int:
        """
        Retourne le nombre de fois où player est bloqué c.-à-d. qu'il ne peut pas bouger,
        sauf si un jeton voisin appartenant au joueur adverse bouge
        """

        count: int = 0
        opponent = R if player == B else B
        for box in (self.R_hex if player == R else self.B_hex):
            neighbors = self.neighbors(box, player)
            if all(
                neighbors.values()
            ):  # Si toutes les cases voisines sont occupées (c.-à-d. != 0)
                for el in neighbors.keys():
                    if neighbors[el] == opponent and 0 in self.neighbors(el, opponent).values():
                        count += 1
        return count

    def evaluate_v1(
        self, player: Player, m: float = 0, p: float = 0, c: float = 0
    ) -> Evaluation:
        nb_moves_r: int = len(self.legals(R))
        nb_moves_b: int = len(self.legals(B))
        # Si un des deux joueurs gagne
        if player == R and nb_moves_r == 0:
            return 10000
        if player == B and nb_moves_b == 0:
            return -10000

        # Si un des deux joueurs gagne au prochain coup de manière certaine
        pins_r: int = self.nb_pins(R)
        pins_b: int = self.nb_pins(B)
        if player == R and nb_moves_b == 0 and pins_r == 0:
            return -10000
        if player == B and nb_moves_r == 0 and pins_b == 0:
            return 10000

        # facteur mobilité
        mobility = (3 * self.nb_checkers) * (1 / (nb_moves_r + 1) - 1 / (nb_moves_b + 1))

        # facteur position
        assert self.grid_weights_R is not None and self.grid_weights_B is not None
        position_r = sum(self.grid_weights_R[box] for box in self.R_hex)
        position_b = sum(self.grid_weights_B[box] for box in self.B_hex)
        position: float = (position_r - position_b) / self.nb_checkers

        # facteur contrôle
        control = (pins_r - pins_b) / self.nb_checkers

        # combinaison linéaire des différents facteurs
        return m * mobility + p * position + c * control

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
        if y == 0 or y == 1:
            d = log(nb)/(log(x)*log(2)) + 2
        else:
            d = log(nb)/(log(x)*log(y)) + 2
        return min(round(d), max_depth)

    def alphabeta_v1(
        self,
        depth: int,
        a: float,
        b: float,
        player: Player,
        m: float,
        p: float,
        c: float,
    ) -> float:
        """
        Minmax avec élagage alpha-beta.
        """

        if depth == 0 or self.is_final(player):
            return self.evaluate_v1(player, m, p, c)
        if player == R:
            best_value = float("-inf")

            for legal in self.legals(player):
                self.play(player, legal)
                best_value = max(
                    best_value, self.alphabeta_v1(depth - 1, a, b, B, m, p, c)
                )
                self.undo(player, legal)
                a = max(a, best_value)
                if a >= b:
                    break  # β cut-off

            return best_value
        else:
            best_value = float("inf")

            for legal in self.legals(player):
                self.play(player, legal)
                best_value = min(
                    best_value, self.alphabeta_v1(depth - 1, a, b, R, m, p, c)
                )
                self.undo(player, legal)
                b = min(b, best_value)
                if a >= b:
                    break  # α cut-off

            return best_value

    def alphabeta_actions_v1(
        self,
        player: Player,
        depth: int,
        a: float,
        b: float,
        legals: list[ActionDodo],
        m: float,
        p: float,
        c: float,
    ) -> tuple[float, list[ActionDodo]]:
        """
        Minmax avec élagage alpha-beta et choix d'une action.
        """

        if depth == 0 or len(legals) == 0:
            return self.evaluate_v1(player, m, p, c), []
        if player == R:
            best_value = float("-inf")
            best_legals: list[ActionDodo] = []
            if len(legals) == 1:
                return best_value, legals

            for legal in legals:
                self.play(player, legal)
                v = self.alphabeta_v1(depth - 1, a, b, B, m, p, c)
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
            if len(legals) == 1:
                return best_value, legals

            for legal in legals:
                self.play(player, legal)
                v = self.alphabeta_v1(depth - 1, a, b, R, m, p, c)
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
