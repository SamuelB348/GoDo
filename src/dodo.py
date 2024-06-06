from __future__ import annotations

import random
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

from types_constants import *
from hex_tools import *


class GameStateDodo:
    def __init__(
        self,
        grid: Grid,
        player: Player,
        hex_size: int,
        r_neighbors: Neighbors,
        b_neighbors: Neighbors,
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
        self.R_POV_NEIGHBORS: Neighbors = r_neighbors
        self.B_POV_NEIGHBORS: Neighbors = b_neighbors
        self.R_CELLS: CellSet = {
            cell for cell, player in self.grid.items() if player == R
        }
        self.B_CELLS: CellSet = {
            cell for cell, player in self.grid.items() if player == B
        }
        self.zkeys = zkeys
        self.turn_key = turn_key
        self.hash = state_hash

        # -------------------- Other -------------------- #

        self.legals: list[ActionDodo] = self.generate_legal_actions(self.turn)

    def generate_legal_actions(self, player: Player) -> list[ActionDodo]:
        player_cells = self.R_CELLS if player == R else self.B_CELLS
        neighbors = self.R_POV_NEIGHBORS if player == R else self.B_POV_NEIGHBORS

        legals = [
            (cell, nghb)
            for cell in player_cells
            for nghb in neighbors[cell]
            if self.grid[nghb] == 0
        ]
        return legals

    def get_legal_actions(self) -> list[ActionDodo]:
        return self.legals

    def is_game_over(self) -> bool:
        return len(self.legals) == 0

    def game_result(self) -> Player:
        assert self.is_game_over()
        return self.turn

    def move(self, action: ActionDodo) -> GameStateDodo:
        new_grid: Grid = self.grid.copy()
        new_grid[action[0]] = 0
        new_grid[action[1]] = self.turn
        act_keys = (
            (self.zkeys[action[0]].R, self.zkeys[action[1]].R)
            if self.turn == R
            else (self.zkeys[action[0]].B, self.zkeys[action[1]].B)
        )
        new_hash = self.hash ^ act_keys[0] ^ act_keys[1] ^ self.turn_key
        return GameStateDodo(
            new_grid,
            R if self.turn == B else B,
            self.size,
            self.R_POV_NEIGHBORS,
            self.B_POV_NEIGHBORS,
            self.zkeys,
            self.turn_key,
            new_hash,
        )

    def simulate_game(self, p) -> tuple[Player, int]:
        tmp_grid = self.grid.copy()
        tmp_r_cells = self.R_CELLS.copy()
        tmp_b_cells = self.B_CELLS.copy()
        game_length = 0

        while True:
            legals: list[ActionDodo] = self.generate_legal_actions(self.turn)
            if len(legals) == 0:
                winner = self.turn
                break
            if p:
                move = random.choice(
                    self.alphabeta_actions_v1(
                        1, self.turn, float("-inf"), float("inf"), legals
                    )[1]
                )
            else:
                move: ActionDodo = random.choice(legals)
            self.play(move, self.turn)
            game_length += 1

            legals = self.generate_legal_actions(self.opponent)
            if len(legals) == 0:
                winner = self.opponent
                break
            if p:
                move = random.choice(
                    self.alphabeta_actions_v1(
                        1, self.opponent, float("-inf"), float("inf"), legals
                    )[1]
                )
            else:
                move: ActionDodo = random.choice(legals)
            self.play(move, self.opponent)
            game_length += 1

        self.grid = tmp_grid
        self.R_CELLS = tmp_r_cells
        self.B_CELLS = tmp_b_cells

        return winner, game_length

    def play(self, action, player) -> None:
        self.grid[action[0]] = 0
        self.grid[action[1]] = player
        if player == R:
            self.R_CELLS.add(action[1])
            self.R_CELLS.discard(action[0])
        else:
            self.B_CELLS.add(action[1])
            self.B_CELLS.discard(action[0])

    def undo(self, action, player):
        self.grid[action[0]] = player
        self.grid[action[1]] = 0
        if player == R:
            self.R_CELLS.add(action[0])
            self.R_CELLS.discard(action[1])
        else:
            self.B_CELLS.add(action[0])
            self.B_CELLS.discard(action[1])

    def evaluate(self, legals, player):
        if player == self.turn:
            return len(self.generate_legal_actions(self.opponent)) - len(legals)
        else:
            return len(legals) - len(self.generate_legal_actions(self.turn))

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
        legals: list[ActionDodo],
    ) -> tuple[float, list[ActionDodo]]:
        if player == self.turn:
            best_value = float("-inf")
            best_legals: list[ActionDodo] = []
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

    def pplot(self) -> None:
        """
        Produit un affichage graphique de la grille de jeu actuelle.
        """

        plt.figure(figsize=(10, 10))
        layout = Layout(layout_flat, Point(1, -1), Point(0, 0))

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
