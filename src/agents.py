"""
This section implements the game engines that manage the game AI (MCTS) and provide methods to
carry out a full game.
"""

from typing import Optional
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor

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

    The abstract methods (implemented in the subclasses) ar intentionally not typed.
    Types are defined in the subclasses.
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
        self.board_utils: BoardUtils = BoardUtils(hex_size, state)

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
        self.time: Time = total_time  # We don't use it actually during a game
        # The previous mean game length (half moves)
        # Should be redefined in the subclasses
        self.previous_mean_game_length: float = 1.0

    def generate_mctsearcher(
        self, state, hex_size, player, c_param, improved_playout
    ) -> MonteCarloTreeSearchNode:
        """
        Generates a single instance of MonteCarloTreeSearchNode.
        Should be implemented in the subclasses.

        :param state: a state
        :param hex_size: the size of the board
        :param player: a player
        :param c_param: the c exploration parameter
        :param improved_playout: a boolean indicating if we perform minmax playout or not
        :return: an instance of MonteCarloTreeSearchNode
        """

        raise NotImplementedError("Must be implemented in subclasses")

    def generate_mctsearchers(
        self,
        state: State,
        hex_size: int,
        player: Player,
        c_param: float,
        improved_playout: bool,
    ) -> list[MonteCarloTreeSearchNode]:
        """
        Generates a list of MonteCarloTreeSearchNodes.

        :param state: a state
        :param hex_size: the size of the board
        :param player: a player
        :param c_param: the c exploration parameter
        :param improved_playout: a boolean indicating if we perform minmax playout or not
        :return: a list of MCTSearchers
        """

        if self.root_parallelization:
            return [
                self.generate_mctsearcher(
                    state, hex_size, player, c_param, improved_playout
                )
                for _ in range(
                    4
                )  # Put here the number of cores you want to dedicate to the search
            ]
        # Otherwise it will be a unique MCTSearcher
        return [
            self.generate_mctsearcher(
                state, hex_size, player, c_param, improved_playout
            )
        ]

    def has_played(self, state) -> Action:
        """
        Returns the action the opponent has played based on the new state it receives.
        Should be implemented in the subclasses.

        :param state: a game state
        :return: the action the opponent has played
        """

        raise NotImplementedError("Must be implemented in subclasses")

    def update(self, has_played: Action) -> None:
        """
        Updates all the MCTSearchers based on the action the opponent played.

        :param has_played: the action played by the opponent
        :return: None
        """

        for i, mctsearcher in enumerate(self.MCTSearchers):
            # We update each MCTSearcher based on an action that was played
            # (played by the player or the opponent)
            # If the action was not explored before we create a new root node
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
            else:  # If the action was one of the child, the root becomes the child
                for child in mctsearcher.children:
                    if child.parent_action == has_played:
                        self.MCTSearchers[i] = child
                        self.MCTSearchers[i].parent = None

    @staticmethod
    def run_mcts(i: int, mctsearcher: MonteCarloTreeSearchNode, time_allocated: float):
        """
        Calls the perform_iterations on a single MCTSearcher.

        :param i: the index of the mctsearcher in the MCTSearchers list
        :param mctsearcher: a mctsearcher
        :param time_allocated: the time allocated to play a move
        :return: the index, the mctsearcher, its children and the mean game length
        """

        mean_game_length = mctsearcher.perform_iterations(time_allocated)

        # We return the mctsearcher because the original mctsearcher
        # doesn't update automatically (because of parallelization)
        return i, mctsearcher, mctsearcher.children, mean_game_length

    def return_best_move(self, time_left: float) -> Action:
        """
        Returns the best move based on the results of all the MCTSearchers.

        :param time_left: the time allocated to make a move
        :return: a legal action
        """

        # The time allocated should be 2 times the time_left/previous_mean_game_length
        # Indeed, previous_mean_game_length is the number of half-moves (for the 2 players)
        time_allocated: float = 2 * (time_left / self.previous_mean_game_length)

        # Root-parallelization or not, we return a list of tuples:
        # [(index, mctsearcher, its children, mean_game_length), ...]
        if self.root_parallelization:
            with ProcessPoolExecutor() as executor:
                futures = [
                    executor.submit(self.run_mcts, i, mctsearcher, time_allocated)
                    for i, mctsearcher in enumerate(self.MCTSearchers)
                ]
                results = [future.result() for future in futures]

        else:
            mean_game_length: float = self.MCTSearchers[0].perform_iterations(
                time_allocated
            )
            results = [
                (
                    0,
                    self.MCTSearchers[0],
                    self.MCTSearchers[0].children,
                    mean_game_length,
                )
            ]

        # We aggregate the results of the different trees with a dictionary
        root_visits: dict[Action, int] = defaultdict(int)
        mean_game_lengths = []

        for i, mctsearcher, children, mean_game_length in results:
            # We update the list of MCTSearchers
            self.MCTSearchers[i] = mctsearcher
            for child in children:
                root_visits[child.parent_action] += child.N
                mean_game_lengths.append(mean_game_length)

        # We select the best move based on the number of visits
        if len(root_visits) == 0:  # This happens sometimes
            # I guess because it ran out of time
            print(f"{time_left:.2f}, {time_allocated:.2f}")
        assert len(root_visits) > 0
        best_root = max(root_visits, key=root_visits.get)

        # We compute the next mean game length
        assert len(mean_game_lengths) > 0
        mean_game_length = sum(mean_game_lengths) / len(mean_game_lengths)

        # We update the mctsearchers based on the move chosen
        self.update(best_root)
        self.previous_mean_game_length = mean_game_length

        print(root_visits)
        print(f"{time_left:.2f}, {time_allocated:.2f}, {mean_game_length:.2f}")
        for mctsearcher in self.MCTSearchers:
            print(mctsearcher)

        return best_root


class EngineDodo(Engine):
    """
    Extends the Engine class for Dodo.
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
        # We redefine this attribute to 120 which is an estimation of the
        # mean number of moves during a game of Dodo (size 4)
        self.previous_mean_game_length = 120.0

    def generate_mctsearcher(
        self,
        state: State,
        hex_size: int,
        player: Player,
        c_param: float,
        improved_playout: bool,
    ) -> MonteCarloTreeSearchNode:
        """
        Extends the generate mctsearcher method of Engine.
        Generates a single instance of MonteCarloTreeSearchNode, adapted to Dodo.

        :param state: a state
        :param hex_size: the size of the board
        :param player: a player
        :param c_param: the c exploration parameter
        :param improved_playout: a boolean indicating if we perform minmax playout or not
        :return: an instance of MonteCarloTreeSearchNode
        """

        return MonteCarloTreeSearchNode(
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

    def has_played(self, state: State) -> ActionDodo:
        """
        Extends the has_played method of Engine.
        Returns the Dodo action the opponent has played based on the new state we receive.

        :param state: a game state
        :return: the action the opponent has played
        """

        grid = self.board_utils.state_to_dict(state)
        current_legals: list[ActionDodo] = self.MCTSearchers[
            0
        ].state.get_legal_actions()
        has_played: ActionDodo = ((-10, -10), (10, 10))

        for legal in current_legals:
            if grid[legal[0]] == 0 and grid[legal[1]] == self.opponent:
                has_played = legal
                break

        return has_played


class EngineGopher(Engine):
    """
    Extends the Engine class for Gopher.
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
        # We redefine this attribute to 50 which is an estimation of the
        # mean number of moves during a game of Gopher (size 6)
        self.previous_mean_game_length = 50.0

    def generate_mctsearcher(
        self,
        state: State,
        hex_size: int,
        player: Player,
        c_param: float,
        improved_playout: bool,
    ):
        """
        Extends the generate mctsearcher method of Engine.
        Generate a single instance of MonteCarloTreeSearchNode, adapted to Gopher.

        :param state: a state
        :param hex_size: the size of the board
        :param player: a player
        :param c_param: the c exploration parameter
        :param improved_playout: a boolean indicating if we perform minmax playout or not
        :return: an instance of MonteCarloTreeSearchNode
        """

        return MonteCarloTreeSearchNode(
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

    def has_played(self, state: State) -> ActionGopher:
        """
        Extends the has_played method of Engine.
        Returns the Gopher action the opponent has played based on the new state we receive.

        :param state: a game state
        :return: the action the opponent has played
        """

        grid = self.board_utils.state_to_dict(state)
        current_legals: list[ActionGopher] = self.MCTSearchers[
            0
        ].state.get_legal_actions()
        has_played: ActionGopher = (-10, -10)

        for legal in current_legals:
            if grid[legal] == self.opponent:
                has_played = legal
                break

        return has_played


Environment = Union[EngineDodo, EngineGopher]
