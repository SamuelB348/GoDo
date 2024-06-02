from __future__ import annotations

import random
from collections import deque
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
        cells: CellSet,
        r_neighbors: Neighbors,
        b_neighbors: Neighbors,
    ):
        # -------------------- Attributs généraux -------------------- #

        self.player: Player = player
        self.opponent: Player = R if player == B else B
        self.size: int = hex_size

        # -------------------- Structures de données -------------------- #

        self.grid: Grid = grid
        self.R_POV_NEIGHBORS: Neighbors = r_neighbors
        self.B_POV_NEIGHBORS: Neighbors = b_neighbors
        self.R_CELLS: CellSet = {
            cell for cell, player in self.grid.items() if player == R
        }
        self.B_CELLS: CellSet = {
            cell for cell, player in self.grid.items() if player == B
        }
        self.CELLS: CellSet = cells

        # -------------------- Autres -------------------- #

        self.legals: list[ActionDodo] = self.generate_legal_actions(self.player)
        self.move_stack: deque[tuple[ActionDodo, Player]] = deque()

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
        return self.player

    def move(self, action: ActionDodo) -> GameStateDodo:
        new_grid: Grid = self.grid.copy()
        new_grid[action[0]] = 0
        new_grid[action[1]] = self.player
        return GameStateDodo(
            new_grid,
            R if self.player == B else B,
            self.size,
            self.CELLS,
            self.R_POV_NEIGHBORS,
            self.B_POV_NEIGHBORS,
        )

    def simulate_game(self) -> tuple[Player, int]:
        tmp_grid = self.grid.copy()
        tmp_r_cells = self.R_CELLS.copy()
        tmp_b_cells = self.B_CELLS.copy()
        game_length = 0
        while True:
            legals: list[ActionDodo] = self.generate_legal_actions(self.player)
            if len(legals) == 0:
                winner = self.player
                break
            move: ActionDodo = random.choice(legals)
            self.play(move, self.player)
            game_length += 1

            legals = self.generate_legal_actions(self.opponent)
            if len(legals) == 0:
                winner = self.opponent
                break
            move = random.choice(legals)
            self.play(move, self.opponent)
            game_length += 1

        # game_length: int = len(self.move_stack)
        self.grid = tmp_grid
        self.R_CELLS = tmp_r_cells
        self.B_CELLS = tmp_b_cells
        # self.undo_stack()

        return winner, game_length

    def play(self, action, player) -> None:
        # self.move_stack.append((action, player))
        self.grid[action[0]] = 0
        self.grid[action[1]] = player
        if player == R:
            self.R_CELLS.add(action[1])
            self.R_CELLS.discard(action[0])
        else:
            self.B_CELLS.add(action[1])
            self.B_CELLS.discard(action[0])

    def undo_stack(self) -> None:
        while self.move_stack:
            action, player = self.move_stack.pop()
            self.grid[action[0]] = player
            self.grid[action[1]] = 0
            if player == R:
                self.R_CELLS.discard(action[1])
                self.R_CELLS.add(action[0])
            else:
                self.B_CELLS.remove(action[1])
                self.B_CELLS.add(action[0])

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

