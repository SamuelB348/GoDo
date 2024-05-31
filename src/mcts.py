from __future__ import annotations
import copy
import time
import random
import cProfile
import pstats
from collections import defaultdict, deque
from typing import Union, Optional, DefaultDict
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from hex_tools import *
import gameplay as gp
import pprint
from other import sum_lists, print_percentage_bar
import multiprocessing
from random_agent import *
from time_manager import TimeManager

# -------------------- Alias de types et constantes pour communiquer avec l'arbitre -------------------- #

ActionGopher = Cell
ActionDodo = tuple[Cell, Cell]
Action = Union[ActionGopher, ActionDodo]
Player = int
R = 1
B = 2
State = list[tuple[Cell, Player]]
Score = int
Time = int

# -------------------- Autres alias de types et constantes -------------------- #

Grid = dict[Cell, Player]
CellSet = set[Cell]
Neighbors = dict[Cell, list[Cell]]


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
        self.opponent = R if player == B else B
        self.size: int = hex_size

        # -------------------- Structures de données -------------------- #

        self.grid: Grid = grid
        self.R_CELLS: CellSet = {
            cell for cell, player in self.grid.items() if player == R
        }
        self.B_CELLS: CellSet = {
            cell for cell, player in self.grid.items() if player == B
        }
        self.CELLS: CellSet = cells
        self.R_POV_NEIGHBORS: Neighbors = r_neighbors
        self.B_POV_NEIGHBORS: Neighbors = b_neighbors

        # -------------------- Autres -------------------- #

        self.legals: list[ActionDodo] = self.generate_legal_actions()
        self.move_stack: deque[ActionDodo] = deque()

    def generate_legal_actions(self) -> list[ActionDodo]:
        # if self.player == R:
        #     player_cells = R
        #     neighbors = self.R_POV_NEIGHBORS
        # else:
        #     player_cells = B
        #     neighbors = self.B_POV_NEIGHBORS
        #
        # legals = [(cell, nghb)
        #           for cell in self.CELLS
        #           if self.grid[cell] == player_cells
        #           for nghb in neighbors[cell]
        #           if self.grid[nghb] == 0]
        #
        # return legals

        # legals: list[ActionDodo] = []
        # for cell in self.R_CELLS if self.player == R else self.B_CELLS:
        #     for nghb in (
        #             self.R_POV_NEIGHBORS[cell]
        #             if self.player == R
        #             else self.B_POV_NEIGHBORS[cell]
        #     ):
        #         if self.grid[nghb] == 0:
        #             legals.append((cell, nghb))
        #
        # return legals

        player_cells = self.R_CELLS if self.player == R else self.B_CELLS
        neighbors = self.R_POV_NEIGHBORS if self.player == R else self.B_POV_NEIGHBORS
        grid = self.grid

        legals = [
            (cell, nghb)
            for cell in player_cells
            for nghb in neighbors[cell]
            if grid[nghb] == 0
        ]

        return legals

    def _legals_for_simulation(self, player):
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

    def simulate_game(self):
        while True:
            legals = self._legals_for_simulation(self.player)
            if len(legals) == 0:
                winner = self.player
                break
            move = random.choice(legals)
            self.play(move, self.player)

            legals = self._legals_for_simulation(self.opponent)
            if len(legals) == 0:
                winner = self.opponent
                break
            move = random.choice(legals)
            self.play(move, self.opponent)

        game_length = len(self.move_stack)
        self.undo_stack()

        return winner, game_length

    def play(self, action, player):
        self.move_stack.append((action, player))
        self.grid[action[0]] = 0
        self.grid[action[1]] = player
        if player == R:
            self.R_CELLS.discard(action[0])
            self.R_CELLS.add(action[1])
        else:
            self.B_CELLS.discard(action[0])
            self.B_CELLS.add(action[1])

    def undo_stack(self):
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

    def move(self, action: ActionDodo):
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
        c,
        parent=None,
        parent_action=None,
    ):
        self.state: GameState = state
        self.parent = parent
        self.parent_action: Optional[ActionDodo] = parent_action
        self.children = []
        self.Q = 0
        self.N = 0
        self.untried_actions: Optional[list[ActionDodo]] = None
        self.untried_actions = self.initialize_actions()
        self.player: Player = player
        self.opponent = R if self.player == B else B

        self.c = c
        return

    def initialize_actions(self) -> list[ActionDodo]:
        self.untried_actions = self.state.get_legal_actions().copy()
        return self.untried_actions

    def expand(self):
        action = self.untried_actions.pop()
        next_state = self.state.move(action)
        child_node = MonteCarloTreeSearchNode(
            next_state, self.player, self.c, parent=self, parent_action=action
        )

        self.children.append(child_node)
        return child_node

    def is_terminal_node(self) -> bool:
        return self.state.is_game_over()

    def rollout(self) -> tuple[int, int]:
        current_rollout_state = self.state
        result, game_length = current_rollout_state.simulate_game()
        # while not current_rollout_state.is_game_over():
        #     possible_moves = current_rollout_state.get_legal_actions()
        #     action = self.rollout_policy(possible_moves)
        #     current_rollout_state = current_rollout_state.move(action)

        if result != self.state.player:
            return 1, game_length
        else:
            return 0, game_length

    def backpropagate(self, result) -> None:
        self.N += 1.0
        self.Q += result
        if self.parent:
            self.parent.backpropagate(1 - result)

    def is_fully_expanded(self) -> bool:
        return len(self.untried_actions) == 0

    def best_child(self, c_param=0.1):
        choices_weights = [
            (c.Q / c.N) + c_param * np.sqrt((2 * np.log(self.N) / c.N))
            for c in self.children
        ]
        return self.children[np.argmax(choices_weights)]

    def best_final_child(self):
        choices_weight = [c.N for c in self.children]
        return self.children[np.argmax(choices_weight)]

    def rollout_policy(self, possible_moves) -> ActionDodo:
        return random.choice(possible_moves)

    def _tree_policy(self):

        current_node = self
        while not current_node.is_terminal_node():

            if not current_node.is_fully_expanded():
                return current_node.expand()
            else:
                current_node = current_node.best_child(c_param=self.c)
        return current_node

    def best_action(self, allocated_time):
        length_count = 0
        simulation_count = 1
        start_time = time.time()
        while time.time() - start_time < allocated_time:
            v = self._tree_policy()
            reward, game_length = v.rollout()
            length_count += game_length
            simulation_count += 1
            v.backpropagate(reward)
        print(simulation_count)
        return self.best_final_child(), max(int(length_count / simulation_count), 2)

    def __str__(self):
        return f"Parent action : {self.parent_action}\n|-- Number simulations : {self.N}\n|-- Number of victories : {self.Q}\n|-- Ratio : {self.Q/self.N:.3f}"


class Engine:
    def __init__(self, state: Grid, player: Player, hex_size: int, total_time: Time, c):

        # -------------------- Attributs généraux -------------------- #

        self.player: Player = player
        self.opponent = R if self.player == B else B
        self.size: int = hex_size

        # -------------------- Structures de données -------------------- #

        self.CELLS: CellSet = self.generate_cells(hex_size)
        self.R_POV_NEIGHBORS: Neighbors = self.generate_neighbors([1, 2, 3])
        self.B_POV_NEIGHBORS: Neighbors = self.generate_neighbors([0, 4, 5])

        # -------------------- Monte Carlo Tree Searcher -------------------- #

        self.c = c
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
        )

        # -------------------- Time Allocator -------------------- #

        self.time: Time = total_time
        self.previous_mean_game_length: Optional[float] = total_time
        self.time_manager = TimeManager()

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

    def select_best_move(self, time_left):
        time_allocated = self.time_manager.simple_time_allocation(
            time_left, self.previous_mean_game_length
        )
        best_children, mean_game_length = self.MCTSearcher.best_action(time_allocated)
        self.MCTSearcher = best_children
        self.previous_mean_game_length = mean_game_length
        print(f"{time_left:.2f}, {time_allocated:.2f}, {mean_game_length:.2f}")
        print(best_children)
        return best_children.parent_action

    def update_state(self, grid: Grid):
        current_legals = self.MCTSearcher.state.get_legal_actions()
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
    game: str, state: State, player: Player, hex_size: int, total_time: Time, c
) -> Environment:
    if game.lower() == "dodo":
        grid = state_to_dict(state, hex_size)
        return Engine(grid, player, hex_size, total_time, c)
    else:
        pass


def strategy(
    env: Environment, state: State, player: Player, time_left: Time
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
    # return state


def game_loop(size: int):
    times = []
    state_tmp = start_board_dodo(size)
    e = initialize("dodo", state_tmp, R, size, 100)
    b = gp.initialize("dodo", state_tmp, B, size, 100)
    while True:
        start = time.time()
        s = strategy(e, state_tmp, e.player, 100)
        times.append(time.time() - start)
        if s is None:
            e.MCTSearcher.state.pplot()
            print(1)
            return times
        # e.MCTSearcher.state.pplot()
        b.play(R, s)
        # b.pplot(b.grid)
        if b.is_final(B):
            b.pplot(b.grid)
            print(2)
            return times
        state_tmp = new_state_dodo(state_tmp, s, R)
        # act = random.choice(e.MCTSearcher.state.legals)
        act = gp.generic_strategy_dodo(
            b, state_tmp, B, 100, 1.25002444, 0.26184217, 0.14314292, -0.17516003
        )[1]
        b.play(B, act)
        # b.pplot(b.grid)
        state_tmp = new_state_dodo(state_tmp, act, B)


def dodo(size: int, c1, c2):
    state_tmp = start_board_dodo(size)
    e1 = initialize("dodo", state_tmp, R, size, 120, c1)
    e2 = initialize("dodo", state_tmp, B, size, 120, c2)
    time_r = 120
    time_b = 120
    i=0
    while True:
        start_time = time.time()
        s = strategy(e1, state_tmp, e1.player, time_r)
        if s is None:
            print(1, end="")
            return 1
        time_r -= time.time() - start_time
        if i % 20 == 0:
            e1.MCTSearcher.state.pplot()
        new_state_dodo(state_tmp, s, R)

        start_time = time.time()
        s = strategy(e2, state_tmp, e2.player, time_b)
        if s is None:
            print(2, end="")
            return -1
        time_b -= time.time() - start_time
        new_state_dodo(state_tmp, s, B)
        i  += 1


def wrapper(args):
    c1, c2, size = args
    return dodo(size, c1, c2)


def match(nb_games: int, size: int, c1, c2):
    nb_wins = 0
    nb_losses = 0

    with multiprocessing.Pool() as pool:
        args_list = [(c1, c2, size)] * (nb_games // 2)
        results = pool.map(wrapper, args_list)

    for result in results:
        if result == 1:
            nb_wins += 1
        else:
            nb_losses += 1

    with multiprocessing.Pool() as pool:
        args_list = [(c2, c1, size)] * (nb_games // 2)
        results = pool.map(wrapper, args_list)
    for result in results:
        if result == -1:
            nb_wins += 1
        else:
            nb_losses += 1

    print(f"\n({c1:.3f}) vs ({c2:.3f})")
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
    dodo(8, 0.5, 0.1)
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
    # for c in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]:
    #     v.append(match(100, 4, c, 0)[0])
    # plt.plot(v)
    # plt.show()
    # match(10, 4, 0.1, 1)
    # tuning_dodo(4, 10)


if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()
    main()
    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats("tottime")
    stats.print_stats()
