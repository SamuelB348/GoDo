import multiprocessing
import cProfile
import pstats
import ast

from mcts import *
from src.utils.utils import *
from src.utils.board_utils import BoardUtils


class Engine:
    def __init__(
        self,
        state: State,
        player: Player,
        hex_size: int,
        total_time: Time,
        c: float,
        p: float,
        f: float,
    ):

        # -------------------- Basic attributes -------------------- #

        self.player: Player = player
        self.opponent: Player = R if self.player == B else B
        self.size: int = hex_size

        # -------------------- Board utilities -------------------- #

        self.board_utils = BoardUtils(hex_size, state)

        # -------------------- Monte Carlo Tree Searcher -------------------- #

        self.c: float = c
        self.p: float = p
        self.f: float = f
        self.MCTSearcher: MonteCarloTreeSearchNode = self.generate_mctsearcher(
            state, hex_size, player, c, p
        )

        # -------------------- Time Management -------------------- #

        self.time: Time = total_time
        self.previous_mean_game_length: int = total_time

    def generate_mctsearcher(
        self, state, hex_size, player, c, p
    ) -> MonteCarloTreeSearchNode:
        raise NotImplementedError("Must be implemented in subclasses")

    def has_played(self, state: State):
        raise NotImplementedError("Must be implemented in subclasses")

    def update_state(self, state: State):
        has_played = self.has_played(state)
        if has_played in self.MCTSearcher.untried_actions:
            next_state = self.MCTSearcher.state.move(has_played)
            self.MCTSearcher = MonteCarloTreeSearchNode(
                next_state,
                self.player,
                self.c,
                self.p,
                parent=self.MCTSearcher,
                parent_action=has_played,
            )
        else:
            for child in self.MCTSearcher.children:
                if child.parent_action == has_played:
                    self.MCTSearcher = child
                    self.MCTSearcher.parent = None

    def return_best_move(self, time_left: float) -> ActionDodo:
        time_allocated: float = self.f * (time_left / self.previous_mean_game_length)
        best_children, mean_game_length = self.MCTSearcher.best_action(time_allocated)
        self.MCTSearcher = best_children
        print(best_children)
        self.MCTSearcher.parent = None

        if mean_game_length is not None:
            self.previous_mean_game_length = mean_game_length
            print(f"{time_left:.2f}, {time_allocated:.2f}, {mean_game_length:.2f}")

        return (tuple(best_children.parent_action[0]), tuple(best_children.parent_action[1]))
        # return best_children.parent_action


class EngineDodo(Engine):
    def __init__(
        self,
        state: State,
        player: Player,
        hex_size: int,
        total_time: Time,
        c: float,
        p: float,
        f: float,
    ):

        super().__init__(state, player, hex_size, total_time, c, p, f)

    def generate_mctsearcher(
        self, state, hex_size, player, c, p
    ) -> MonteCarloTreeSearchNode:
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
            c,
            p,
        )

    def has_played(self, state: State):
        grid = self.board_utils.state_to_dict(state)
        current_legals: list[ActionDodo] = self.MCTSearcher.state.get_legal_actions()
        has_played: Optional[ActionDodo] = None
        for legal in current_legals:
            if grid[legal[0]] == 0 and grid[legal[1]] == self.opponent:
                has_played = legal
                break
        return has_played


class EngineGopher(Engine):
    def __init__(
        self,
        state: State,
        player: Player,
        hex_size: int,
        total_time: Time,
        c: float,
        p: float,
        f: float,
    ):

        super().__init__(state, player, hex_size, total_time, c, p, f)

    def generate_mctsearcher(self, state, hex_size, player, c, p):
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
            c,
            p,
        )

    def has_played(self, state: State):
        grid = self.board_utils.state_to_dict(state)
        current_legals: list[ActionDodo] = self.MCTSearcher.state.get_legal_actions()
        has_played: Optional[ActionDodo] = None
        for legal in current_legals:
            if grid[legal] == self.opponent:
                has_played = legal
                break
        return has_played

