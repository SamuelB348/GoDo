"""
This section implements a generic game state, that can be adapted for dodo or gopher.
It contains the core logic of the game in itself (not the AI).

It defines several methods that will later be called by the MCTS section.
"""

from __future__ import annotations

from functools import cached_property
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

from types_constants import *
from hex_tools import hex_to_pixel, polygon_corners, Layout


class GameState:
    """
    GameState class encapsulating all the logic and methods essential to play moves,
    generate legal actions, simulate a whole game from the current position, etc...

    The abstract methods (implemented in the subclasses) ar intentionally not typed.
    Types are defined in the subclasses.
    """

    def __init__(
        self,
        grid: Grid,
        player: Player,
        hex_size: int,
        zkeys: dict[Cell, ZKey],
        turn_key: int,
        state_hash: int,
    ):

        # The player whose turn it is in the current situation
        self.turn: Player = player
        # The opponent of the player
        self.opponent: Player = R if player == B else B
        # The size of the board
        self.size: int = hex_size

        # The grid representing the checkers position on the board
        self.grid: Grid = grid
        # The cells of the red player
        self.r_cells: CellSet = {
            cell for cell, player in self.grid.items() if player == R
        }
        # The cells of the blue player
        self.b_cells: CellSet = {
            cell for cell, player in self.grid.items() if player == B
        }
        # The empty cells, not occupied by any player
        self.empty_cells: CellSet = {
            cell for cell, player in self.grid.items() if player == 0
        }

        # The zobrist keys of the cells
        self.zkeys: dict[Cell, ZKey] = zkeys
        # The key for the turn
        self.turn_key: int = turn_key
        # The hash of the current position
        self.hash: int = state_hash

        # Boolean to indicate if the board is empty
        self.is_empty: bool = self.empty_grid()
        # The possible legals for the player in this position
        self.legals: ListActions = self.generate_legal_actions(self.turn)

    def empty_grid(self):
        """
        Tells if the grid is empty or not.
        Should be implemented in the subclasses.
        :return:
        """

        raise NotImplementedError("Must be implemented in subclasses")

    def generate_legal_actions(self, player):
        """
        Generates all the legal actions of the given player.
        Should be implemented in the subclasses.

        :param player:
        :return:
        """

        raise NotImplementedError("Must be implemented in subclasses")

    def get_legal_actions(self):
        """
        Returns the legal actions on the current position.

        :return: the legals attribute
        """

        return self.legals

    def is_game_over(self) -> bool:
        """
        Returns True if the game is over.
        It doesn't tell which player has won, it differs in the 2 games.

        :return: a boolean
        """

        return len(self.legals) == 0

    def move(self, action):
        """
        Performs a move, and return a new GameState instance.
        Should be implemented in the subclasses.

        :param action: a legal action
        :return: a new GameState instance
        """

        raise NotImplementedError("Must be implemented in subclasses")

    def simulate_game(self, improved_playout):
        """
        Simulates a game from the current state.
        Should be implemented in the subclasses.

        :param improved_playout: a boolean indicating if we should perform minmax playout or not
        :return: a tuple (winner, game_length)
        """

        raise NotImplementedError("Must be implemented in subclasses")

    def play(self, action, player):
        """
        Plays a move while staying inside the structure.
        Modifies the structure accordingly, but the modifications are not meant to be permanent.
        Should be implemented in the subclasses.

        :param action: a legal action
        :param player: the player whose turn it is to play
        :return: None
        """

        raise NotImplementedError("Must be implemented in subclasses")

    def undo(self, action, player):
        """
        Opposite of the play method.
        Should be implemented in the subclasses.

        :param action: a legal action to undo
        :param player: the player whose turn it is
        :return: None
        """

        raise NotImplementedError("Must be implemented in subclasses")

    def evaluate(self, legals, player):
        """
        Computes a heuristic evaluation of the current position.
        Should be implemented in the subclasses.

        :param legals: the precomputed legals for one of the 2 players
        :param player: the player whose point of view is used to evaluate the game
        :return: a float representing the evaluation of the current position
        """

        raise NotImplementedError("Must be implemented in subclasses")

    def alphabeta(self, depth: int, player: Player, a: float, b: float) -> float:
        """
        Performs alphabeta search.

        :param depth: the depth of alphabeta search
        :param player: a player whose turn it is in the alphabeta search
        :param a: alpha parameter
        :param b: beta parameter
        :return: the alphabeta value
        """
        legals: ListActions = self.generate_legal_actions(player)

        if len(legals) == 0:
            return 10000 if player == self.turn else -10000

        if depth == 0:
            heuristic: float = self.evaluate(legals, player)
            return heuristic

        if player == self.turn:
            best_value: float = float("-inf")

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
        self, depth: int, player: Player, a: float, b: float, legals: ListActions
    ):
        """
        Same as alphabeta but with action selection.
        Must be called once when we start an alphabeta search.

        :param depth: the depth of alphabeta search
        :param player: a player whose turn it is in the alphabeta search
        :param a: alpha parameter
        :param b: beta parameter
        :param legals: the precomputed legals of the player
        :return: the best alphabeta values and the actions leading to them
        """

        if player == self.turn:
            best_value: float = float("-inf")
            best_legals = []

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
        """
        Returns the appropriate layout to display the board.

        :return: a layout
        """
        raise NotImplementedError("Must be implemented in subclasses")

    def pplot(self) -> None:
        """
        Displays the grid in a nice format
        """

        plt.figure(figsize=(10, 10))

        layout: Layout = self.get_layout

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
            # plt.text(
            #     center.x,
            #     center.y,
            #     f"{box[0]}, {box[1]}",
            #     horizontalalignment="right",
            # )
        plt.xlim(-2 * self.size - 1, 2 * self.size + 1)
        plt.ylim(-2 * self.size - 1, 2 * self.size + 1)
        plt.show()
