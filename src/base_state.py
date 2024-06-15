from __future__ import annotations

from functools import cached_property
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

from types_constants import *
from hex_tools import *


class GameState:
    def __init__(
        self,
        grid: Grid,
        player: Player,
        hex_size: int,
        zkeys,
        turn_key,
        state_hash,
    ):
        # -------------------- Basic attributes -------------------- #

        self.turn: Player = player
        self.opponent: Player = R if player == B else B
        self.size: int = hex_size

        # -------------------- Board representation -------------------- #

        self.grid: Grid = grid
        self.R_CELLS: CellSet = {
            cell for cell, player in self.grid.items() if player == R
        }
        self.B_CELLS: CellSet = {
            cell for cell, player in self.grid.items() if player == B
        }
        self.EMPTY_CELLS: CellSet = {
            cell for cell, player in self.grid.items() if player == 0
        }

        self.zkeys = zkeys
        self.turn_key = turn_key
        self.hash = state_hash

        # -------------------- Other -------------------- #

        self.is_empty = self.empty_grid()
        self.legals: list[Action] = self.generate_legal_actions(self.turn)

    def empty_grid(self) -> bool:
        raise NotImplementedError("Must be implemented in subclasses")

    def generate_legal_actions(self, player: Player) -> list[Action]:
        raise NotImplementedError("Must be implemented in subclasses")

    def get_legal_actions(self) -> list[Action]:
        return self.legals

    def is_game_over(self) -> bool:
        return len(self.legals) == 0

    def game_result(self) -> Player:
        raise NotImplementedError("Must be implemented in subclasses")

    def move(self, action: Action) -> GameState:
        raise NotImplementedError("Must be implemented in subclasses")

    def simulate_game(self, p) -> tuple[Player, int]:
        raise NotImplementedError("Must be implemented in subclasses")

    def play(self, action, player) -> None:
        raise NotImplementedError("Must be implemented in subclasses")

    def undo(self, action, player):
        raise NotImplementedError("Must be implemented in subclasses")

    def evaluate(self, legals, player):
        raise NotImplementedError("Must be implemented in subclasses")

    def alphabeta(self, depth: int, player: Player, a: float, b: float) -> float:
        legals = self.generate_legal_actions(player)
        if len(legals) == 0:
            return 10000 if player == self.turn else -10000
        if depth == 0:
            eval = self.evaluate(legals, player)
            # print(eval)
            return eval

        if player == self.turn:
            best_value = float("-inf")
            for legal in legals:
                self.play(legal, player)
                best_value = max(
                    best_value, self.alphabeta(depth - 1, self.opponent, a, b)
                )
                self.undo(legal, player)
                a = max(a, best_value)
                if a >= b:
                    break  # β cut-off

            return best_value
        else:
            best_value = float("inf")
            for legal in legals:
                self.play(legal, player)
                best_value = min(best_value, self.alphabeta(depth - 1, self.turn, a, b))
                self.undo(legal, player)
                b = min(b, best_value)
                if a >= b:
                    break  # α cut-off

            return best_value

    def alphabeta_actions_v1(
        self,
        depth: int,
        player: Player,
        a: float,
        b: float,
        legals: list[Action],
    ) -> tuple[float, list[Action]]:
        if player == self.turn:
            best_value = float("-inf")
            best_legals: list[Action] = []
            if len(legals) == 1:
                return best_value, legals

            for legal in legals:
                self.play(legal, player)
                v = self.alphabeta(depth - 1, self.opponent, a, b)
                self.undo(legal, player)
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
                self.play(legal, player)
                v = self.alphabeta(depth - 1, self.turn, a, b)
                self.undo(legal, player)
                if v < best_value:
                    best_value = v
                    best_legals = [legal]
                elif v == best_value:
                    best_legals.append(legal)
                b = min(b, best_value)

            return best_value, best_legals

    @cached_property
    def get_layout(self):
        raise NotImplementedError("Must be implemented in subclasses")

    def pplot(self) -> None:
        """
        Produit un affichage graphique de la grille de jeu actuelle.
        """

        plt.figure(figsize=(10, 10))

        layout = self.get_layout()

        for box, player in self.grid.items():
            corners = polygon_corners(layout, box)
            center = hex_to_pixel(layout, box)

            # Contours de chaque hexagone
            list_edges_x = [corner.x for corner in corners]
            list_edges_y = [corner.y for corner in corners]
            list_edges_x.append(list_edges_x[0])
            list_edges_y.append(list_edges_y[0])
            if player == 1:
                color = "red"
            elif player == 2:
                color = "blue"
            else:
                color = "none"

            polygon = Polygon(
                corners,
                closed=True,
                edgecolor="k",
                facecolor=color,
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