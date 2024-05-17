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
    def __init__(self, grid: State, hex_size: int, time: Time):
        self.grid: dict[Cell, Player] = dict(grid)
        self.R_hex: set[Cell] = {
            hex_key for hex_key, player in self.grid.items() if player == R
        }
        self.B_hex: set[Cell] = {
            hex_key for hex_key, player in self.grid.items() if player == B
        }
        self.R_neighbors = {cell: [neighbor(cell, i) for i in [1, 2, 3] if neighbor(cell, i) in self.grid] for cell in self.grid}
        self.B_neighbors = {cell: [neighbor(cell, i) for i in [0, 4, 5] if neighbor(cell, i) in self.grid] for cell in self.grid}

        self.size: int = hex_size
        self.nb_checkers: int = ((self.size + 1) * self.size) // 2 + (self.size - 1)
        self.time: Time = time

        # Attributs pour la fonction d'évaluation
        self.grid_weights_R: Optional[dict[Cell, int | float]] = None
        self.grid_weights_B: Optional[dict[Cell, float]] = None

        # Caches
        self.cache = {}

        # Attributs pour le debug
        self.position_explored: int = 0
        self.terminal_node: int = 0

    @staticmethod
    def symetrical(dico):
        sym = tuple()
        for cell in dico:
            dist = abs(cell[0] - cell[1])
            if cell[0] < cell[1]:
                sym += ((cell, dico[(cell[0]+dist, cell[1]-dist)]),)
            elif cell[0] > cell[1]:
                sym += ((cell, dico[(cell[0]-dist, cell[1]+dist)]),)
            else:
                sym += ((cell, dico[cell]),)
        return sym

    def back_to_start_board(self):
        self.grid = {}
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
        for key in dict2:
            if dict2[key] == player:
                dict1[key] += 1

    def generate_grid_heatmaps(self):
        self.grid_weights_R = {}
        self.grid_weights_B = {}
        for el in self.grid:
            self.grid_weights_R[el] = 1 - (max(abs(el[0] - (self.size - 1)), abs(el[1] - (self.size - 1))) / (2 * (self.size - 1)))
            self.grid_weights_B[el] = 1 - (max(abs(el[0] + (self.size - 1)), abs(el[1] + (self.size - 1))) / (2 * (self.size - 1)))

    def update_state(self, grid: State):
        """
        Remet à jour les dictionnaires quand on reçoit un nouveau "state" de l'arbitre
        """

        self.grid = dict(grid)
        self.R_hex = {hex_key for hex_key, player in self.grid.items() if player == R}
        self.B_hex = {hex_key for hex_key, player in self.grid.items() if player == B}

    def legals(self, player: Player) -> list[ActionDodo]:
        """
        Retourne les coups légaux du joueur en paramètre

        La méthode s'appuie sur les sets red_hex ou blue_hex pour gagner du temps plutôt que d'itérer
        sur toutes les cases du plateau.
        """

        legals: list[ActionDodo] = []
        if player == R:
            for box in self.R_hex:
                for nghb in self.R_neighbors[box]:
                    if self.grid[nghb] == 0:
                        legals.append((box, nghb))
        elif player == B:
            for box in self.B_hex:
                for nghb in self.B_neighbors[box]:
                    if self.grid[nghb] == 0:
                        legals.append((box, nghb))

        return legals

    def is_final(self, player: Player) -> bool:
        return len(self.legals(player)) == 0

    def play(self, player: Player, action: ActionDodo):
        """
        Joue une action légale et modifie les attributs.

        Il faut à la fois modifier le dictionnaire de toutes les cases (grid) et les sets des cases de
        chaque joueur (red_hex et blue_hex).
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
            neighbors = {nghb: self.grid[nghb] for nghb in self.R_neighbors[cell]}
        if player == B:
            neighbors = {nghb: self.grid[nghb] for nghb in self.B_neighbors[cell]}
        return neighbors

    def nb_pins(self, player: Player) -> int:
        """
        Retourne le nombre de fois où player est bloqué c.-à-d. qu'il ne peut pas bouger,
        sauf si un jeton voisin appartenant au joueur adverse bouge
        """

        count: int = 0
        opponent = R if player == B else B
        for box in self.R_hex if player == R else self.B_hex:
            neighbors = self.neighbors(box, player)
            if all(
                neighbors.values()
            ):  # Si toutes les cases voisines sont occupées (c.-à-d. != 0)
                for cell in neighbors:
                    if (
                        neighbors[cell] == opponent
                        and 0 in self.neighbors(cell, opponent).values()
                    ):
                        count += 1
        return count

    def calculate_metrics(self):
        legals_r: list[ActionDodo] = []
        pins_r: float = 0.0
        position_r: float = 0.0

        legals_b: list[ActionDodo] = []
        pins_b: float = 0.0
        position_b: float = 0.0

        for box in self.R_hex:
            position_r += self.grid_weights_R[box]
            for nghb in self.R_neighbors[box]:
                if self.grid[nghb] == 0:
                    legals_r.append((box, nghb))
                elif self.grid[nghb] == B and 0 in self.neighbors(nghb, B).values():
                    pins_r += 1

        for box in self.B_hex:
            position_b += self.grid_weights_B[box]
            for nghb in self.B_neighbors[box]:
                if self.grid[nghb] == 0:
                    legals_b.append((box, nghb))
                elif self.grid[nghb] == R and 0 in self.neighbors(nghb, R).values():
                    pins_b += 1

        return legals_r, pins_r, position_r, legals_b, pins_b, position_b

    def evaluate_v1(
        self, player: Player, m: float = 0, p: float = 0, c: float = 0
    ) -> Evaluation:

        state = tuple(self.grid.items())
        if state in self.cache:
            return self.cache[state]

        legals_r, pins_r, position_r, legals_b, pins_b, position_b = self.calculate_metrics()

        nb_moves_r: int = len(legals_r)
        nb_moves_b: int = len(legals_b)
        # Si un des deux joueurs gagne
        if player == R and nb_moves_r == 0:
            return 10000
        if player == B and nb_moves_b == 0:
            return -10000

        # Si un des deux joueurs gagne au prochain coup de manière certaine

        if player == R and nb_moves_b == 0 and pins_r == 0:
            return -10000
        if player == B and nb_moves_r == 0 and pins_b == 0:
            return 10000

        # facteur mobilité
        # mobility = (3 * self.nb_checkers) * (
        #     1 / (nb_moves_r + 1) - 1 / (nb_moves_b + 1)
        # )
        mobility = (nb_moves_r - nb_moves_b) / (3*self.nb_checkers)

        # facteur position
        # assert self.grid_weights_R is not None and self.grid_weights_B is not None
        # position_r = sum(self.grid_weights_R[box] for box in self.R_hex)
        # position_b = sum(self.grid_weights_B[box] for box in self.B_hex)
        position: float = (position_r - position_b) / self.nb_checkers

        # facteur contrôle
        control = (pins_r - pins_b) / self.nb_checkers

        evaluation = m * mobility + p * position + c * control
        self.cache[state] = evaluation
        # sym = self.symetrical(self.grid)
        # self.cache[sym] = evaluation
        # combinaison linéaire des différents facteurs
        return evaluation

    @staticmethod
    def adaptable_depth_v1(
        x: int, upper_bound: int, lower_bound: int, critical_point: int
    ) -> int:
        d = upper_bound - (
            (upper_bound - lower_bound) / (1 + exp(-(x - critical_point)))
        )
        return round(d)

    @staticmethod
    def adaptable_depth_v2(x: int, y: int, nb: int, max_depth: int) -> int:
        if y in (0, 1):
            d = log(nb) / (log(x) * log(2)) + 2
        else:
            d = log(nb) / (log(x) * log(y)) + 2
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
            self.terminal_node += 1
            return self.evaluate_v1(player, m, p, c)
        self.position_explored += 1
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
                self.terminal_node = 0
                self.position_explored = 0
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

            self.terminal_node = 0
            self.position_explored = 0
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

            self.terminal_node = 0
            self.position_explored = 0
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
