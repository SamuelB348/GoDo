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
        self.R_CELLS = {cell for cell, player in self.grid.items() if player == R}
        self.B_CELLS = {cell for cell, player in self.grid.items() if player == B}

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
