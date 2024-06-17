"""
This section implements the game engines that manage the game AI (MCTS) and provide methods to
carry out a full game.
"""

from typing import Optional
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
import numpy as np

from mcts import MonteCarloTreeSearchNode
from types_constants import *
from board_utils import BoardUtils
from gamestate import GameState
from dodo import GameStateDodo
from gopher import GameStateGopher


class Engine:
    """
    A game engine managing one or more MCTSearchers.
    It manages the evolution of all the components throughout the game, and deals with what it
    receives from a referee.
    """

    def __init__(
        self,
        state: State,
        player: Player,
        hex_size: int,
        total_time: Time,
        c_param: float,
        improved_playout: bool = False,
        root_parallelization: bool = False,
    ):

        # The player we are playing for throughout the game
        self.player: Player = player
        # The opponent player
        self.opponent: Player = R if self.player == B else B
        # The board size
        self.size: int = hex_size

        # The board utilities
        self.board_utils = BoardUtils(hex_size, state)

        # The C exploration parameter in UCT
        self.c_param: float = c_param
        # The boolean indicating if we improve the playouts with minmax or not
        self.improved_playout: bool = improved_playout
        # The boolean indicating if we perform root parallelization or not
        self.root_parallelization: bool = root_parallelization
        # The list of MCTSearchers (if no root parallelization there will be one)
        self.MCTSearchers: list[MonteCarloTreeSearchNode] = self.generate_mctsearchers(
            state, hex_size, player, c_param, improved_playout
        )

        # The time available for all the game
        self.time: Time = total_time
        # The previous mean game length (half moves)
        # It is set to total_time (to get exactly 2 seconds for the first move)
        self.previous_mean_game_length: float = float(total_time)

    def generate_mctsearchers(
        self, state, hex_size, player, c_param, improved_playout
    ) -> list[MonteCarloTreeSearchNode]:
        """
        Generate a single instance of MonteCarloTreeSearchNode.
        Should be implemented in the subclasses.

        :param state: a state
        :param hex_size: the size of the board
        :param player: a player
        :param c_param: the c exploration parameter
        :param improved_playout: a boolean indicating if we perform minmax playout or not
        :return: a list of MCTSearchers
        """

        raise NotImplementedError("Must be implemented in subclasses")

    def has_played(self, state: State) -> Action:
        """
        Return the action the opponent has played based on the new state we receive.
        Should be implemented in the subclasses.

        :param state: a game state
        :return: the action the opponent has played
        """

        raise NotImplementedError("Must be implemented in subclasses")

    def update_state(self, has_played: Action) -> None:
        """
        Update all the MCTSearchers based on the action the opponent played.

        :param has_played: the action played by the opponent
        :return: None
        """

        for i, mctsearcher in enumerate(self.MCTSearchers):
            if has_played in mctsearcher.untried_actions:
                next_state: GameState = mctsearcher.state.move(has_played)
                self.MCTSearchers[i] = MonteCarloTreeSearchNode(
                    next_state,
                    self.player,
                    self.c_param,
                    self.improved_playout,
                    parent=mctsearcher,
                    parent_action=has_played,
                )
            else:
                for child in mctsearcher.children:
                    if child.parent_action == has_played:
                        self.MCTSearchers[i] = child
                        self.MCTSearchers[i].parent = None

    @staticmethod
    def run_mcts(i: int, mctsearcher: MonteCarloTreeSearchNode, time_allocated: float):
        """

        :param i: the index of the mctsearcher in the MCTSearchers list
        :param mctsearcher: a mctsearcher
        :param time_allocated: time allocated to play a move
        :return: the index, the mctsearcher, its children and the mean game length
        """

        mean_game_length = mctsearcher.perform_iterations(time_allocated)

        return i, mctsearcher, mctsearcher.children, mean_game_length

    def return_best_move(self, time_left: float) -> ActionDodo:
        time_allocated: float = 2 * (time_left / self.previous_mean_game_length)

        if self.root_parallelization:
            with ProcessPoolExecutor() as executor:
                futures = [
                    executor.submit(self.run_mcts, i, mctsearcher, time_allocated)
                    for i, mctsearcher in enumerate(self.MCTSearchers)
                ]
                results = [future.result() for future in futures]

        else:
            mean_game_length = self.MCTSearchers[0].perform_iterations(
                time_allocated
            )
            results = [(0, self.MCTSearchers[0], self.MCTSearchers[0].children, mean_game_length)]

        root_visits: dict[Action, int] = defaultdict(int)
        mean_game_lengths = []

        for i, mctsearcher, children, mean_game_length in results:
            self.MCTSearchers[i] = mctsearcher
            for child in children:
                root_visits[child.parent_action] += child.N
                mean_game_lengths.append(mean_game_length)

        best_root = max(root_visits, key=root_visits.get)
        print(root_visits)
        print(best_root)

        mean_game_length: float = np.mean(mean_game_lengths)

        self.update_state(best_root)

        if mean_game_length is not None:
            self.previous_mean_game_length = mean_game_length
            print(f"{time_left:.2f}, {time_allocated:.2f}, {mean_game_length:.2f}")
        for mctsearcher in self.MCTSearchers:
            print(mctsearcher)
        return best_root


class EngineDodo(Engine):
    """
    Extend the Engine class for Dodo.
    """

    def __init__(
        self,
        state: State,
        player: Player,
        hex_size: int,
        total_time: Time,
        c_param: float,
        improved_playout: bool = False,
        root_parallelization: bool = False,
    ):

        super().__init__(
            state,
            player,
            hex_size,
            total_time,
            c_param,
            improved_playout,
            root_parallelization,
        )

    def generate_mctsearchers(
        self, state, hex_size, player, c_param, improved_playout
    ) -> list[MonteCarloTreeSearchNode]:
        if self.root_parallelization:
            return [
                MonteCarloTreeSearchNode(
                    GameStateDodo(
                        self.board_utils.state_to_dict(state),
                        player,
                        hex_size,
                        self.board_utils.r_pov_neighbors,
                        self.board_utils.b_pov_neighbors,
                        self.board_utils.cell_keys,
                        self.board_utils.turn_key,
                        self.board_utils.start_hash,
                    ),
                    player,
                    c_param,
                    improved_playout,
                )
                for _ in range(4)
            ]
        else:
            return [
                MonteCarloTreeSearchNode(
                    GameStateDodo(
                        self.board_utils.state_to_dict(state),
                        player,
                        hex_size,
                        self.board_utils.r_pov_neighbors,
                        self.board_utils.b_pov_neighbors,
                        self.board_utils.cell_keys,
                        self.board_utils.turn_key,
                        self.board_utils.start_hash,
                    ),
                    player,
                    c_param,
                    improved_playout,
                )
            ]

    def has_played(self, state: State):
        grid = self.board_utils.state_to_dict(state)
        current_legals: list[ActionDodo] = self.MCTSearchers[
            0
        ].state.get_legal_actions()
        has_played: Optional[ActionDodo] = None
        for legal in current_legals:
            if grid[legal[0]] == 0 and grid[legal[1]] == self.opponent:
                has_played = legal
                break
        return has_played


class EngineGopher(Engine):
    """
    Extend the Engine class for Gopher.
    """

    def __init__(
        self,
        state: State,
        player: Player,
        hex_size: int,
        total_time: Time,
        c_param: float,
        improved_playout: bool,
        root_parallelization: bool,
    ):

        super().__init__(
            state,
            player,
            hex_size,
            total_time,
            c_param,
            improved_playout,
            root_parallelization,
        )

    def generate_mctsearchers(self, state, hex_size, player, c_param, improved_playout):
        if self.root_parallelization == 1:
            return [
                MonteCarloTreeSearchNode(
                    GameStateGopher(
                        self.board_utils.state_to_dict(state),
                        player,
                        hex_size,
                        self.board_utils.neighbors,
                        self.board_utils.cell_keys,
                        self.board_utils.turn_key,
                        self.board_utils.start_hash,
                    ),
                    player,
                    c_param,
                    improved_playout,
                )
                for _ in range(8)
            ]
        else:
            return [
                MonteCarloTreeSearchNode(
                    GameStateGopher(
                        self.board_utils.state_to_dict(state),
                        player,
                        hex_size,
                        self.board_utils.neighbors,
                        self.board_utils.cell_keys,
                        self.board_utils.turn_key,
                        self.board_utils.start_hash,
                    ),
                    player,
                    c_param,
                    improved_playout,
                )
            ]

    def has_played(self, state: State):
        grid = self.board_utils.state_to_dict(state)
        current_legals: list[ActionDodo] = self.MCTSearchers[
            0
        ].state.get_legal_actions()
        has_played: Optional[ActionDodo] = None
        for legal in current_legals:
            if grid[legal] == self.opponent:
                has_played = legal
                break
        return has_played


Environment = Union[EngineDodo, EngineGopher]
