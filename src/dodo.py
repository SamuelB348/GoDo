"""
This section extends the GameState class for Dodo.
"""

from __future__ import annotations

import random
from functools import cached_property

from gamestate import GameState
from types_constants import *
from hex_tools import Layout, layout_flat, Point


class GameStateDodo(GameState):
    """
    Extends the GameState class for the game of Dodo.
    """

    def __init__(
        self,
        grid: Grid,
        player: Player,
        hex_size: int,
        r_neighbors: Neighbors,
        b_neighbors: Neighbors,
        zkeys: dict[Cell, ZKey],
        turn_key: int,
        state_hash: int,
    ):

        # For Dodo, we need the two different pov for the neighbors: the red's and the blue's
        self.r_pov_neighbors: Neighbors = r_neighbors
        self.b_pov_neighbors: Neighbors = b_neighbors
        super().__init__(grid, player, hex_size, zkeys, turn_key, state_hash)

    def empty_grid(self) -> bool:
        """
        Extends the empty_grid method of GameState.
        Always return False for Dodo.

        :return: a boolean
        """

        return False

    def generate_legal_actions(self, player: Player) -> list[ActionDodo]:
        """
        Extends the generate_legal_actions method of GameState.
        Generates all the legal actions of the player.

        :param player: the player whose legal moves we will calculate
        :return: a list of legal moves
        """

        player_cells: CellSet = self.r_cells if player == R else self.b_cells
        neighbors: Neighbors = (
            self.r_pov_neighbors if player == R else self.b_pov_neighbors
        )

        # For each cell in the player's cells, we check the neighbors to see if it's unoccupied.
        # If so, we add (cell, neighbor) to the legals
        legals: list[ActionDodo] = [
            (cell, nghb)
            for cell in player_cells
            for nghb in neighbors[cell]
            if self.grid[nghb] == 0
        ]

        return legals

    def move(self, action: ActionDodo) -> GameStateDodo:
        """
        Extends the move method of GameState.
        Modifies the game state, compute the resulting hash and return a new GameStateDodo.

        :param action: a legal action
        :return: a new GameStateDodo instance
        """

        new_grid: Grid = self.grid.copy()
        new_grid[action[0]] = 0
        new_grid[action[1]] = self.turn

        # To calculate the zobrist hash of the new game state
        # we just de the xor of all the different keys
        act_keys: tuple[int, int] = (
            (self.zkeys[action[0]].R, self.zkeys[action[1]].R)
            if self.turn == R
            else (self.zkeys[action[0]].B, self.zkeys[action[1]].B)
        )
        new_hash: int = self.hash ^ act_keys[0] ^ act_keys[1] ^ self.turn_key

        return GameStateDodo(
            new_grid,
            R if self.turn == B else B,
            self.size,
            self.r_pov_neighbors,
            self.b_pov_neighbors,
            self.zkeys,
            self.turn_key,
            new_hash,
        )

    def simulate_game(self, improved_playout: bool) -> tuple[Player, int]:
        """
        Extends the simulate_game method of GameState.
        Simulates a game from the current game state. Here we stay inside the current structure,
        therefore we will need to save the state before simulating and to restore it after.

        :param improved_playout: boolean indicating if it should perform minmax playouts or not.
        :return: the winner of the simulation and the length of the simulation (nb of half-moves)
        """

        # Save the current game state (no need for deepcopy here)
        tmp_grid: Grid = self.grid.copy()
        tmp_r_cells: CellSet = self.r_cells.copy()
        tmp_b_cells: CellSet = self.b_cells.copy()

        # We will count the number of half-move during the simulation.
        # It's useful for better time management
        game_length: int = 0

        while True:
            legals: list[ActionDodo] = self.generate_legal_actions(self.turn)
            if len(legals) == 0:
                # If the player has no legal moves, he wins
                winner: Player = self.turn
                break
            if improved_playout:
                move: ActionDodo = random.choice(
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
                # If the opponent has no legal moves, he wins
                winner = self.opponent
                break
            if improved_playout:
                move = random.choice(
                    self.alphabeta_actions_v1(
                        1, self.opponent, float("-inf"), float("inf"), legals
                    )[1]
                )
            else:
                move = random.choice(legals)
            self.play(move, self.opponent)
            game_length += 1

        # Restore the previous game state
        self.grid = tmp_grid
        self.r_cells = tmp_r_cells
        self.b_cells = tmp_b_cells

        return winner, game_length

    def play(self, action: ActionDodo, player: Player) -> None:
        """
        Extends the play method of GameState.
        Plays an action and modify the structure accordingly. Unlike the move method, here we stay
        inside the current structure. The modifications are not ment to be permanent.

        :param action: a legal action
        :param player: the player whose turn it is
        :return: None
        """

        # Update the grid, and the player cells according to the move
        self.grid[action[0]] = 0
        self.grid[action[1]] = player

        if player == R:
            self.r_cells.add(action[1])
            self.r_cells.discard(action[0])
        else:
            self.b_cells.add(action[1])
            self.b_cells.discard(action[0])

    def undo(self, action: ActionDodo, player: Player) -> None:
        """
        Extends the undo method of GameState.
        Undoes an action and modify the structure accordingly. Unlike the move method, here we stay
        inside the current game state structure. It is intended to be used when using alphabeta.

        :param action: a legal action to be undone
        :param player: the player whose turn it is
        :return: None
        """

        # Update the grid, and the player cells according to the move
        # Here it's the opposite of the play method

        self.grid[action[0]] = player
        self.grid[action[1]] = 0

        if player == R:
            self.r_cells.add(action[0])
            self.r_cells.discard(action[1])
        else:
            self.b_cells.add(action[0])
            self.b_cells.discard(action[1])

    def evaluate(self, legals: list[ActionDodo], player: Player) -> float:
        """
        Extends the evaluate method of GameState.
        Performs a very simple heuristic evaluation function for alphabeta:
        - The more the player has legal actions, the worst.
        - The more the opponent of the player has legal actions, the best.

        :param legals: the precomputed legals for one of the 2 players
        :param player: the player whose point of view is used to evaluate the game
        :return: a float representing the evaluation of the current position
        """

        if player == self.turn:
            return len(self.generate_legal_actions(self.opponent)) - len(legals)
        return len(legals) - len(self.generate_legal_actions(self.turn))

    @cached_property
    def get_layout(self) -> Layout:
        """
        Extends the get_layout method of GameState.
        For Dodo, it's a flat layout.

        :return: a layout
        """

        return Layout(layout_flat, Point(1, -1), Point(0, 0))
