from __future__ import annotations

import random

from gamestate import GameState
from types_constants import *
from hex_tools import *


class GameStateGopher(GameState):
    def __init__(
        self,
        grid: Grid,
        player: Player,
        hex_size: int,
        neighbors: Neighbors,
        zkeys,
        turn_key,
        state_hash,
    ):

        self.NEIGHBORS: Neighbors = neighbors
        super().__init__(grid, player, hex_size, zkeys, turn_key, state_hash)

    def empty_grid(self) -> bool:
        for cell in self.grid:
            if self.grid[cell] != 0:
                return False
        return True

    def generate_legal_actions(self, player: Player) -> list[ActionGopher]:
        legals = []
        opponent_cells, opponent = (self.R_CELLS, R) if player == B else (self.B_CELLS, B)

        if player == R and self.is_empty:
            return [(0, self.size-1)]

        for box in opponent_cells:
            for nghb in self.NEIGHBORS[box]:
                if self.grid[nghb] == 0:
                    is_valid = True
                    for nghb_bis in self.NEIGHBORS[nghb]:
                        if self.grid[nghb_bis] == opponent and nghb_bis != box:
                            is_valid = False
                            break
                        if self.grid[nghb_bis] == player:
                            is_valid = False
                            break
                    if is_valid:
                        legals.append(nghb)
        return legals

    def game_result(self) -> Player:
        assert self.is_game_over()
        return self.opponent

    def move(self, action: ActionGopher) -> GameStateGopher:
        new_grid: Grid = self.grid.copy()
        new_grid[action] = self.turn

        act_key = (
            self.zkeys[action].R
            if self.turn == R
            else self.zkeys[action].B
        )
        new_hash = self.hash ^ act_key ^ self.turn_key

        return GameStateGopher(
            new_grid,
            R if self.turn == B else B,
            self.size,
            self.NEIGHBORS,
            self.zkeys,
            self.turn_key,
            new_hash,
        )

    def simulate_game(self, p) -> tuple[Player, int]:
        tmp_grid = self.grid.copy()
        tmp_r_cells = self.R_CELLS.copy()
        tmp_b_cells = self.B_CELLS.copy()
        tmp_empty_cells = self.EMPTY_CELLS.copy()
        was_empty = self.is_empty
        self.is_empty = False
        game_length = 0

        while True:
            legals: list[ActionGopher] = self.generate_legal_actions(self.turn)
            if len(legals) == 0:
                winner = self.opponent
                break
            if p:
                move = random.choice(
                    self.alphabeta_actions_v1(
                        1, self.turn, float("-inf"), float("inf"), legals
                    )[1]
                )
            else:
                move = random.choice(legals)
            self.play(move, self.turn)
            game_length += 1

            legals = self.generate_legal_actions(self.opponent)
            if len(legals) == 0:
                winner = self.turn
                break
            if p:
                move = random.choice(
                    self.alphabeta_actions_v1(
                        1, self.opponent, float("-inf"), float("inf"), legals
                    )[1]
                )
            else:
                move = random.choice(legals)
            self.play(move, self.opponent)
            game_length += 1

        self.grid = tmp_grid
        self.R_CELLS = tmp_r_cells
        self.B_CELLS = tmp_b_cells
        self.EMPTY_CELLS = tmp_empty_cells
        self.is_empty = was_empty

        return winner, game_length

    def play(self, action, player) -> None:
        self.is_empty = False
        self.grid[action] = player
        if player == R:
            self.R_CELLS.add(action)
        else:
            self.B_CELLS.add(action)
        self.EMPTY_CELLS.discard(action)

    def undo(self, action, player):
        self.grid[action] = 0
        if player == R:
            self.R_CELLS.discard(action)
        else:
            self.B_CELLS.discard(action)
        self.EMPTY_CELLS.add(action)

    def evaluate(self, legals, player):
        if player == self.turn:
            return len(legals) - len(self.generate_legal_actions(self.opponent))
        else:
            return len(self.generate_legal_actions(self.turn)) - len(legals)

    def get_layout(self):
        return Layout(layout_pointy, Point(1, -1), Point(0, 0))


if __name__ == "__main__":
    from board_utils import BoardUtils
    from test_tune import start_board_gopher
    s = start_board_gopher(6)
    b = BoardUtils(6, s)

    e = GameStateGopher(b.state_to_dict(s), R, 6, b.neighbors, b.cell_keys, b.turn_key, b.compute_start_hash(s))
    e.play((0, 5), R)
    e.play((-1, 4), B)
    e.play((-2, 3), R)
    e.play((1, 5), B)
    e.play((1, 4), R)
    e.play((0, 3), B)
    e.play((-1, 2), R)
    e.play((-1, 1), B)
    e.play((-2, 0), R)
    e.play((-2, -1), B)
    e.play((0, 1), R)
    e.play((0, 0), B)
    e.play((1, 0), R)
    e.play((1, 2), B)
    e.play((2, 3), R)
    e.play((1, -1), B)
    e.play((-3, -2), R)
    e.play((2, 1), B)
    e.play((1, -2), R)
    e.play((3, 3), B)
    e.play((4, 3), R)
    e.play((4, 2), B)
    e.play((5, 2), R)
    e.play((0, -3), B)
    e.play((-1, -4), R)
    e.play((-3, -3), B)
    e.play((-4, -4), R)
    e.play((-5, -5), B)
    e.pplot()
    print(e.alphabeta_actions_v1(10, R, float('-inf'), float('inf'), e.generate_legal_actions(R)))
