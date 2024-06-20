"""
This section extends the GameState class for Gopher.
"""

from __future__ import annotations

import random
from functools import cached_property

from gamestate import GameState
from types_constants import *
from hex_tools import Layout, layout_pointy, Point


class GameStateGopher(GameState):
    """
    Extends the GameState class for the game of Gopher.
    """

    def __init__(
        self,
        grid: Grid,
        player: Player,
        hex_size: int,
        neighbors: Neighbors,
        zkeys: dict[Cell, ZKey],
        turn_key: int,
        state_hash: int,
    ):

        # For Gopher, we need all the neighbors of each cell
        self.neighbors: Neighbors = neighbors
        super().__init__(grid, player, hex_size, zkeys, turn_key, state_hash)

    def empty_grid(self) -> bool:
        """
        Extend the empty_grid method of GameState.
        Return False if there is at least one cell occupied.

        :return: a boolean
        """

        for cell in self.grid:
            if self.grid[cell] != 0:
                return False
        return True

    def generate_legal_actions(self, player: Player) -> list[ActionGopher]:
        """
        Extend the generate_legal_actions method of GameState.
        Generate all the legal actions of the player.

        :param player: the player whose legal moves we will calculate
        :return: a list of legal moves
        """

        legals: list[ActionGopher] = []
        opponent_cells: CellSet
        opponent: Player
        opponent_cells, opponent = (
            (self.r_cells, R) if player == B else (self.b_cells, B)
        )

        # If it's the first move, we place automatically the first checker on a corner
        # Otherwise it would be too time-consuming
        if player == R and self.is_empty:
            return [(0, self.size - 1)]

        # The idea here is to iterate over the opponent cells
        # Then we look at the neighbors, and then the neighbors of the neighbors
        for box in opponent_cells:
            for nghb in self.neighbors[box]:
                if self.grid[nghb] == 0:
                    is_valid: bool = True
                    for nghb_bis in self.neighbors[nghb]:
                        if self.grid[nghb_bis] == opponent and nghb_bis != box:
                            is_valid = False
                            break
                        if self.grid[nghb_bis] == player:
                            is_valid = False
                            break
                    if is_valid:
                        legals.append(nghb)

        return legals

    def move(self, action: ActionGopher) -> GameStateGopher:
        """
        Extends the move method of GameState.
        Modify the game state, compute the resulting hash and return a new GameStateGopher.

        :param action: a legal action
        :return: a new GameStateGopher instance
        """

        new_grid: Grid = self.grid.copy()
        new_grid[action] = self.turn

        # To calculate the zobrist hash of the new game state
        # we just de the xor of all the different keys
        act_key: int = self.zkeys[action].R if self.turn == R else self.zkeys[action].B
        new_hash: int = self.hash ^ act_key ^ self.turn_key

        return GameStateGopher(
            new_grid,
            R if self.turn == B else B,
            self.size,
            self.neighbors,
            self.zkeys,
            self.turn_key,
            new_hash,
        )

    def simulate_game(self, improved_playout) -> tuple[Player, int]:
        """
        Extends the simulate_game method of GameState.
        Simulate a game from the current game state. Here we stay inside the current structure,
        therefore we will need to save the state before simulating and to restore it after.

        :param improved_playout: boolean indicating if it should perform minmax playouts or not.
        :return: the winner of the simulation and the length of the simulation (nb of half-moves)
        """

        # Save the current game state (no need for deepcopy here)
        tmp_grid: Grid = self.grid.copy()
        tmp_r_cells: CellSet = self.r_cells.copy()
        tmp_b_cells: CellSet = self.b_cells.copy()
        tmp_empty_cells: CellSet = self.empty_cells.copy()
        was_empty: bool = self.is_empty

        # We will count the number of half-move during the simulation.
        # It's useful for better time management
        game_length: int = 0
        self.is_empty = False

        while True:
            legals: list[ActionGopher] = self.generate_legal_actions(self.turn)
            if len(legals) == 0:
                # If the player has no legal moves, the opponent wins
                winner: Player = self.opponent
                break
            if improved_playout:
                move: ActionGopher = random.choice(
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
                # If the opponent has no legal moves, the player wins
                winner = self.turn
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
        self.empty_cells = tmp_empty_cells
        self.is_empty = was_empty

        return winner, game_length

    def play(self, action: ActionGopher, player: Player) -> None:
        """
        Extends the play method of GameState.
        Play an action and modify the structure accordingly. Unlike the move method, here we stay
        inside the current structure. The modifications are not ment to be permanent.

        :param action: a legal action
        :param player: the player whose turn it is
        :return: None
        """

        # Update the grid, the player cells and the empty information according to the move
        self.is_empty = False
        self.grid[action] = player

        if player == R:
            self.r_cells.add(action)
        else:
            self.b_cells.add(action)

        self.empty_cells.discard(action)

    def undo(self, action: ActionGopher, player: Player) -> None:
        """
        Extends the undo method of GameState.
        Undo an action and modify the structure accordingly. Unlike the move method, here we stay
        inside the current game state structure. It is intended to be used when using alphabeta.

        :param action: a legal action to be undone
        :param player: the player whose turn it is
        :return: None
        """

        # Update the grid, and the player cells according to the move
        # Here it's the opposite of the play method

        self.grid[action] = 0

        if player == R:
            self.r_cells.discard(action)
        else:
            self.b_cells.discard(action)

        self.empty_cells.add(action)

    def evaluate(self, legals: list[ActionGopher], player: Player) -> float:
        """
        Extends the evaluate method of GameState.
        Perform a very simple heuristic evaluation function for alphabeta:
        - The more the player has legal actions, the best.
        - The more the opponent of the player has legal actions, the worst.

        :param legals: the precomputed legals for one of the 2 players
        :param player: the player whose point of view is used to evaluate the game
        :return: a float representing the evaluation of the current position
        """

        if player == self.turn:
            return len(legals) - len(self.generate_legal_actions(self.opponent))
        return len(self.generate_legal_actions(self.turn)) - len(legals)

    @cached_property
    def get_layout(self):
        """
        Extends the get_layout method of GameState.
        For Gopher, it's a pointy layout.

        :return: a layout
        """

        return Layout(layout_pointy, Point(1, -1), Point(0, 0))
