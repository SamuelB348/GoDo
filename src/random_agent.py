from __future__ import annotations

import random
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

from hex_tools import *
from types_constants import *
from board_utils import BoardUtils


class RandomAgent:
    def __init__(
        self,
        state: State,
        player: Player,
        hex_size: int,
    ):
        # -------------------- Attributs généraux -------------------- #

        self.player: Player = player
        self.size: int = hex_size

        # -------------------- Structures de données -------------------- #

        self.board_utils = BoardUtils(hex_size, state)
        self.grid: Grid = self.board_utils.state_to_dict(state)
        self.R_CELLS: CellSet = {
            cell for cell, player in self.grid.items() if player == R
        }
        self.B_CELLS: CellSet = {
            cell for cell, player in self.grid.items() if player == B
        }
        self.CELLS: CellSet = self.board_utils.cells
        self.R_POV_NEIGHBORS: Neighbors = self.board_utils.r_pov_neighbors
        self.B_POV_NEIGHBORS: Neighbors = self.board_utils.b_pov_neighbors

    def update_state(self, state: State):
        self.grid = self.board_utils.state_to_dict(state)
        self.R_CELLS = {
            cell for cell, player in self.grid.items() if player == R
        }
        self.B_CELLS = {
            cell for cell, player in self.grid.items() if player == B
        }

    def get_legal_actions(self) -> list[ActionDodo]:
        legals: list[ActionDodo] = []
        for cell in self.R_CELLS if self.player == R else self.B_CELLS:
            for nghb in (
                    self.R_POV_NEIGHBORS[cell]
                    if self.player == R
                    else self.B_POV_NEIGHBORS[cell]
            ):
                if self.grid[nghb] == 0:
                    legals.append((cell, nghb))

        return legals

    def is_final(self):
        return len(self.get_legal_actions()) == 0

    def get_action(self):
        return random.choice(self.get_legal_actions())

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

