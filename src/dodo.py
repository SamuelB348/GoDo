from __future__ import annotations

import random

from base_state import GameState
from types_constants import *
from hex_tools import *


class GameStateDodo(GameState):
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

        self.R_POV_NEIGHBORS: Neighbors = r_neighbors
        self.B_POV_NEIGHBORS: Neighbors = b_neighbors
        super().__init__(grid, player, hex_size, zkeys, turn_key, state_hash)

    def empty_grid(self) -> bool:
        return False

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

    def get_layout(self):
        return Layout(layout_flat, Point(1, -1), Point(0, 0))
