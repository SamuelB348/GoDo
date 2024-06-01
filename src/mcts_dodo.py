from __future__ import annotations

import time
import random
import cProfile
import pstats
import multiprocessing
from collections import deque
from typing import Optional
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

from types_constants import *
from hex_tools import *
from random_agent import RandomAgent
from time_manager import TimeManager
from other import print_percentage_bar


class GameState:
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

        # -------------------- Structures de données -------------------- #

        self.grid: Grid = grid
        self.R_POV_NEIGHBORS: Neighbors = r_neighbors
        self.B_POV_NEIGHBORS: Neighbors = b_neighbors
        self.R_CELLS: CellSet = {
            cell for cell, player in self.grid.items() if player == R
        }
        self.B_CELLS: CellSet = {
            cell for cell, player in self.grid.items() if player == B
        }
        self.CELLS: CellSet = cells

        # -------------------- Autres -------------------- #
        # hash_state = hash((tuple(self.grid.items()), self.player))
        # if hash_state in legals_cache:
        #     self.legals = legals_cache[hash_state]
        # else:
        self.legals: list[ActionDodo] = self.generate_legal_actions(self.player)
            # legals_cache[hash_state] = self.legals
        self.move_stack: deque[tuple[ActionDodo, Player]] = deque()

    def generate_legal_actions(self, player: Player) -> list[ActionDodo]:
        player_cells = self.R_CELLS if player == R else self.B_CELLS
        neighbors = self.R_POV_NEIGHBORS if player == R else self.B_POV_NEIGHBORS
        grid = self.grid

        legals = [
            (cell, nghb)
            for cell in player_cells
            for nghb in neighbors[cell]
            if grid[nghb] == 0
        ]

        return legals

    def get_legal_actions(self) -> list[ActionDodo]:
        return self.legals

    def is_game_over(self) -> bool:
        return len(self.legals) == 0

    def game_result(self) -> Player:
        assert self.is_game_over()
        return self.player

    def move(self, action: ActionDodo) -> GameState:
        new_grid: Grid = self.grid.copy()
        new_grid[action[0]] = 0
        new_grid[action[1]] = self.player
        return GameState(
            new_grid,
            R if self.player == B else B,
            self.size,
            self.CELLS,
            self.R_POV_NEIGHBORS,
            self.B_POV_NEIGHBORS,
        )

    def simulate_game(self) -> tuple[Player, int, set[ActionDodo], set[ActionDodo]]:
        player_moves: set[ActionDodo] = set()
        opponent_moves: set[ActionDodo] = set()
        while True:
            legals: list[ActionDodo] = self.generate_legal_actions(self.player)
            if len(legals) == 0:
                winner = self.player
                break
            move: ActionDodo = random.choice(legals)
            player_moves.add(move)
            self.play(move, self.player)

            legals = self.generate_legal_actions(self.opponent)
            if len(legals) == 0:
                winner = self.opponent
                break
            move = random.choice(legals)
            opponent_moves.add(move)
            self.play(move, self.opponent)

        game_length: int = len(self.move_stack)
        self.undo_stack()

        return winner, game_length, player_moves, opponent_moves

    def play(self, action, player) -> None:
        self.move_stack.append((action, player))
        self.grid[action[0]] = 0
        self.grid[action[1]] = player
        if player == R:
            self.R_CELLS.discard(action[0])
            self.R_CELLS.add(action[1])
        else:
            self.B_CELLS.discard(action[0])
            self.B_CELLS.add(action[1])

    def undo_stack(self) -> None:
        while self.move_stack:
            action, player = self.move_stack.pop()
            self.grid[action[0]] = player
            self.grid[action[1]] = 0
            if player == R:
                self.R_CELLS.discard(action[1])
                self.R_CELLS.add(action[0])
            else:
                self.B_CELLS.remove(action[1])
                self.B_CELLS.add(action[0])

    def evaluate(self):
        return 1/(1+len(self.generate_legal_actions(self.opponent))) - 1/(1+len(self.get_legal_actions()))

    def pplot(self) -> None:
        """
        Produit un affichage graphique de la grille de jeu actuelle.
        """

        plt.figure(figsize=(10, 10))
        layout = Layout(layout_flat, Point(1, -1), Point(0, 0))

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
            plt.text(
                center.x,
                center.y,
                f"{box.q}, {box.r}",
                horizontalalignment="right",
            )
        plt.xlim(-2 * self.size - 1, 2 * self.size + 1)
        plt.ylim(-2 * self.size - 1, 2 * self.size + 1)
        plt.show()


class MonteCarloTreeSearchNode:
    def __init__(
        self,
        state: GameState,
        player: Player,
        c: float,
        rave_const: float,
        p,
        parent=None,
        parent_action: Optional[ActionDodo] = None,
    ):
        self.state: GameState = state
        self.parent: Optional[MonteCarloTreeSearchNode] = parent
        self.parent_action: Optional[ActionDodo] = parent_action
        self.children: list[MonteCarloTreeSearchNode] = []
        self.Q: int = 0
        self.N: int = 0
        self.Q_AMAF: int = 0
        self.N_AMAF: int = 0
        self.untried_actions: list[ActionDodo] = self.initialize_actions()
        self.player: Player = player
        self.opponent: Player = R if self.player == B else B
        self.c = c
        self.rave_const = rave_const
        self.p = p

    def initialize_actions(self) -> list[ActionDodo]:
        self.untried_actions = self.state.get_legal_actions().copy()
        return self.untried_actions

    def expand(self) -> MonteCarloTreeSearchNode:
        action: ActionDodo = self.untried_actions.pop()
        next_state: GameState = self.state.move(action)
        child_node: MonteCarloTreeSearchNode = MonteCarloTreeSearchNode(
            next_state, self.player, self.c, self.rave_const, self.p, parent=self, parent_action=action
        )

        self.children.append(child_node)
        return child_node

    def is_terminal_node(self) -> bool:
        return self.state.is_game_over()

    def rollout(self) -> tuple[int, int, set[ActionDodo], set[ActionDodo]]:
        current_rollout_state: GameState = self.state
        result, game_length, current_player_moves, current_opponent_moves = current_rollout_state.simulate_game()

        if result != self.state.player:  # Reward for the player who has played, not the one who must play
            return 1, game_length, current_opponent_moves, current_player_moves
        return 0, game_length, current_player_moves, current_opponent_moves

    def backpropagate(self, result) -> None:
        self.N += 1
        self.Q += result
        if self.parent:
            self.parent.backpropagate(1 - result)

    def amaf_backup(self, winning_moves, losing_moves):
        if self.parent:
            for child in self.parent.children:
                if child.parent_action in winning_moves:
                    child.N_AMAF += 1
                    child.Q_AMAF += 1
                if child.parent_action in losing_moves:
                    child.N_AMAF += 1
            self.parent.amaf_backup(losing_moves, winning_moves)

    def is_fully_expanded(self) -> bool:
        return len(self.untried_actions) == 0

    def best_child(self, c_param=0.1) -> MonteCarloTreeSearchNode:
        alpha = 0 if self.rave_const == 0 else max(0., (self.rave_const - self.N) / self.rave_const)

        UCT_choice = np.array([
            (c.Q / c.N) + c_param * np.sqrt((2 * np.log(self.N) / c.N))
            for c in self.children
        ])
        AMAF_choice = np.array([
            c.Q_AMAF / c.N_AMAF if c.N_AMAF != 0 else 0
            for c in self.children
        ])
        return self.children[np.argmax((1-alpha)*UCT_choice + alpha*AMAF_choice)]

    def best_final_child(self) -> MonteCarloTreeSearchNode:
        choices_weight: list[int] = [c.N for c in self.children]
        return self.children[np.argmax(choices_weight)]

    def rollout_policy(self, possible_moves) -> ActionDodo:
        return random.choice(possible_moves)

    def _tree_policy(self) -> MonteCarloTreeSearchNode:
        current_node = self
        while not current_node.is_terminal_node():

            if not current_node.is_fully_expanded():
                return current_node.expand()

            current_node = current_node.best_child(c_param=self.c)

        return current_node

    def best_action(
        self, allocated_time: float
    ) -> tuple[MonteCarloTreeSearchNode, int|None]:
        length_count: int = 0
        simulation_count: int = 1
        start_time: float = time.time()
        if self.is_fully_expanded() and len(self.children) == 1:
            return self.best_final_child(), None
        while time.time() - start_time < allocated_time:
            v: MonteCarloTreeSearchNode = self._tree_policy()
            reward, game_length, winning_moves, losing_moves = v.rollout()
            length_count += game_length
            simulation_count += 1
            v.backpropagate(reward)
            v.amaf_backup(winning_moves, losing_moves)

            if simulation_count % 50 == 0:
                first_visited, second_visited = self.get_two_most_visited()
                time_spent = time.time() - start_time
                time_left = allocated_time - time_spent
                if simulation_count * (time_left/time_spent) * self.p < first_visited - second_visited:
                    break
        print(simulation_count)
        return self.best_final_child(), max(int(length_count / simulation_count), 2)

    def get_two_most_visited(self):
        if not self.children or len(self.children) < 2:
            raise ValueError("The node should have at least two children.")

        first_max = second_max = float('-inf')

        for child in self.children:
            if child.N > first_max:
                second_max = first_max
                first_max = child.N
            elif child.N > second_max:
                second_max = child.N

        return first_max, second_max

    def __str__(self):
        return (
            f"Parent action : {self.parent_action}\n"
            f"|-- Number simulations : {self.N}\n"
            f"|-- Number of victories : {self.Q}\n"
            f"|-- AMAF count : {self.N_AMAF}\n"
            f"|-- AMAF wins : {self.Q_AMAF}\n"
            f"|-- Ratio : {self.Q/self.N:.3f}"
        )


class Engine:
    def __init__(
        self, state: Grid, player: Player, hex_size: int, total_time: Time, c: float, rave_const: float, p, f
    ):

        # -------------------- Attributs généraux -------------------- #

        self.player: Player = player
        self.opponent: Player = R if self.player == B else B
        self.size: int = hex_size

        # -------------------- Structures de données -------------------- #

        self.CELLS: CellSet = self.generate_cells(hex_size)
        self.R_POV_NEIGHBORS: Neighbors = self.generate_neighbors([1, 2, 3])
        self.B_POV_NEIGHBORS: Neighbors = self.generate_neighbors([0, 4, 5])

        # -------------------- Monte Carlo Tree Searcher -------------------- #

        self.c: float = c
        self.rave_const = rave_const
        self.p = p
        self.f = f
        self.MCTSearcher: MonteCarloTreeSearchNode = MonteCarloTreeSearchNode(
            GameState(
                state,
                R,
                hex_size,
                self.CELLS,
                self.R_POV_NEIGHBORS,
                self.B_POV_NEIGHBORS,
            ),
            player,
            c,
            rave_const,
            p
        )

        # -------------------- Time Allocator -------------------- #

        self.time: Time = total_time
        self.previous_mean_game_length: int = total_time
        self.time_manager: TimeManager = TimeManager()

    @staticmethod
    def generate_cells(hex_size: int) -> CellSet:
        grid = set()
        n = hex_size - 1
        for r in range(n, -n - 1, -1):
            q1 = max(-n, r - n)
            q2 = min(n, r + n)
            for q in range(q1, q2 + 1):
                grid.add(Cell(q, r))
        return grid

    def generate_neighbors(self, directions: list[int]) -> Neighbors:
        return {
            cell: [
                neighbor(cell, i) for i in directions if neighbor(cell, i) in self.CELLS
            ]
            for cell in self.CELLS
        }

    def select_best_move(self, time_left: float) -> ActionDodo:
        time_allocated: float = self.f * self.time_manager.simple_time_allocation(
            time_left, self.previous_mean_game_length
        )
        best_children, mean_game_length = self.MCTSearcher.best_action(time_allocated)
        self.MCTSearcher = best_children
        self.MCTSearcher.parent = None
        if mean_game_length is not None:
            self.previous_mean_game_length = mean_game_length
            # print(f"{time_left:.2f}, {time_allocated:.2f}, {mean_game_length:.2f}")
        print(best_children)
        return best_children.parent_action

    def update_state(self, grid: Grid):
        current_legals: list[ActionDodo] = self.MCTSearcher.state.get_legal_actions()
        has_played: Optional[ActionDodo] = None
        for legal in current_legals:
            if grid[legal[0]] == 0 and grid[legal[1]] == self.opponent:
                has_played = legal
                break
        if has_played in self.MCTSearcher.untried_actions:
            next_state = self.MCTSearcher.state.move(has_played)
            self.MCTSearcher = MonteCarloTreeSearchNode(
                next_state,
                self.player,
                self.c,
                self.rave_const,
                self.p,
                parent=self.MCTSearcher,
                parent_action=has_played,
            )
        else:
            for child in self.MCTSearcher.children:
                if child.parent_action == has_played:
                    self.MCTSearcher = child


Environment = Engine


def start_board_dodo(size: int) -> State:
    grid: State = []
    n = size - 1
    for r in range(n, -n - 1, -1):
        q1 = max(-n, r - n)
        q2 = min(n, r + n)
        for q in range(q1, q2 + 1):
            if -q > r + (size - 3):
                grid.append((Cell(q, r), R))
            elif r > -q + (size - 3):
                grid.append((Cell(q, r), B))
            # else:
            #     grid.append((Cell(q, r), 0))
    return grid


def state_to_dict(state: State, size: int):
    grid = {}
    n = size - 1
    for r in range(n, -n - 1, -1):
        q1 = max(-n, r - n)
        q2 = min(n, r + n)
        for q in range(q1, q2 + 1):
            if (Cell(q, r), R) in state:
                grid[Cell(q, r)] = R
            elif (Cell(q, r), B) in state:
                grid[Cell(q, r)] = B
            else:
                grid[Cell(q, r)] = 0
    return grid


def initialize(
    game: str, state: State, player: Player, hex_size: int, total_time: Time, c: float, rave_const: float, p, f
) -> Environment:
    if game.lower() == "dodo":
        grid = state_to_dict(state, hex_size)
        return Engine(grid, player, hex_size, total_time, c, rave_const, p, f)
    else:
        pass


def strategy(
    env: Environment, state: State, player: Player, time_left: float
) -> tuple[Environment, Action]:
    new_grid = state_to_dict(state, env.size)
    env.update_state(new_grid)
    if env.MCTSearcher.is_terminal_node():
        return None
    return env.select_best_move(time_left)


def final_result(state: State, score: Score, player: Player):
    pass


def new_state_dodo(state: State, action: Action, player: Player):
    state.remove((action[0], player))
    state.append((action[1], player))


def dodo(size: int, c1, r1, p1, f1, c2, r2, p2, f2):
    state_tmp = start_board_dodo(size)
    e1 = initialize("dodo", state_tmp, R, size, 120, c1, r1, p1, f1)
    e2 = initialize("dodo", state_tmp, B, size, 120, c2, r2, p2, f2)
    time_r: float = 120.0/2
    time_b: float = 120.0/2
    i = 0
    while True:
        start_time = time.time()
        s = strategy(e1, state_tmp, e1.player, time_r)
        if s is None:
            e1.MCTSearcher.state.pplot()
            print(1, end="")
            return 1
        time_r -= time.time() - start_time
        # if i % 5 == 0:
        #     e1.MCTSearcher.state.pplot()
        new_state_dodo(state_tmp, s, R)

        start_time = time.time()
        s = strategy(e2, state_tmp, e2.player, time_b)
        if s is None:
            e2.MCTSearcher.state.pplot()
            print(2, end="")
            return -1
        time_b -= time.time() - start_time
        new_state_dodo(state_tmp, s, B)
        i += 1


def wrapper(args):
    c1, r1, p1, f1, c2, r2, p2, f2, size = args
    return dodo(size, c1, r1, p1, f1, c2, r2, p2, f2)


def match(nb_games: int, size: int, c1, r1, p1, f1, c2, r2, p2, f2):
    nb_wins = 0
    nb_losses = 0

    with multiprocessing.Pool() as pool:
        args_list = [(c1, r1, p1, f1, c2, r2, p2, f2, size)] * (nb_games // 2)
        results = pool.map(wrapper, args_list)

    for result in results:
        if result == 1:
            nb_wins += 1
        else:
            nb_losses += 1

    with multiprocessing.Pool() as pool:
        args_list = [(c2, r2, p2, f2, c1, r1, p1, f1, size)] * (nb_games // 2)
        results = pool.map(wrapper, args_list)
    for result in results:
        if result == -1:
            nb_wins += 1
        else:
            nb_losses += 1

    print(f"\n({c1:.3f}, {r1}, {p1}, {f1}) vs ({c2:.3f}, {r2}, {p2}, {f2})")
    print_percentage_bar(nb_wins / nb_games, nb_losses / nb_games, nb_games)
    return nb_wins, nb_losses


def tuning_dodo(grid_size: int, nb_games: int, factor: float = 0.01):
    best_coeffs = np.array([0.17653504])
    list_best_coeff = []
    count = 0
    while True:
        deltas = np.random.normal(0, 0.1, 1)
        coeffs_a = best_coeffs + deltas
        coeffs_b = best_coeffs - deltas

        # S'assurer que les coefficients restent positifs
        coeffs_a[0] = max(coeffs_a[0], 0)
        coeffs_b[0] = max(coeffs_b[0], 0)

        results = match(nb_games, grid_size, coeffs_a[0], coeffs_b[0])

        if results[0] > 0.6 * nb_games:  # coeffs_a ont gagné
            best_coeffs = best_coeffs + (coeffs_a - best_coeffs) * factor
        elif results[0] < 0.4 * nb_games:
            best_coeffs = best_coeffs + (coeffs_b - best_coeffs) * factor

        list_best_coeff.append(best_coeffs[0])
        print(best_coeffs)

        if count % 2 == 0:
            plt.plot(list_best_coeff)
            plt.xlabel("Iteration")
            plt.ylabel("Best Coefficient")
            plt.title("Tuning Coefficient Over Time")
            plt.show()

        count += 1


def main():
    # for _ in range(100):
    #     e = initialize("dodo", start_board_dodo(4), R, 4, 100, 1.)
    #     a = e.select_best_move()
    dodo(7, 1, 0, 0.2, 1.5, 1, 0, 0.8, 5)
    # print(strategy(e, start_board_dodo(4), R, 100))
    # tab = []
    # for _ in range(1):
    #     tab.append(dodo(4, 1, 1))
    # print(tab.count(1), tab.count(-1))
    # plt.plot(sum_lists(tab))
    # plt.show()
    #
    # print(tab.count(1), tab.count(-1))
    # v = []
    # for r in [10, 20, 30, 40]:
    #     v.append(match(100, 4, 1, r, 1, 0)[0])
    # plt.plot(v)
    # plt.show()
    # match(100, 4, 1, 0, 1, 50)
    # tuning_dodo(4, 10)


if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()
    main()
    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats("tottime")
    stats.print_stats()
