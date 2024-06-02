from __future__ import annotations

import random
from collections import deque
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

from types_constants import *
from hex_tools import *


class GameStateGopher:
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

        # -------------------- Autres -------------------- #

        self.legals: list[ActionGopher] = self.generate_legal_actions(self.player)

    def generate_legal_actions(self, player: Player) -> list[ActionDodo]:
        pass

    def get_legal_actions(self) -> list[ActionDodo]:
        return self.legals

    def is_game_over(self) -> bool:
        pass

    def game_result(self) -> Player:
        pass

    def move(self, action: ActionDodo) -> GameStateDodo:
        pass

    def simulate_game(self) -> tuple[Player, int]:
        pass

    def play(self, action, player) -> None:
        pass

    def undo_stack(self) -> None:
        pass

    def pplot(self) -> None:
        pass