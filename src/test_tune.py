import multiprocessing
import cProfile
import pstats
import random
import time
import ast
import numpy as np
import matplotlib.pyplot as plt

from types_constants import *
from utils import print_percentage_bar
from agents import EngineDodo, EngineGopher


Environment = Union[EngineDodo, EngineGopher]


def start_board_dodo(size: int) -> State:
    grid: State = []
    n = size - 1
    for r in range(n, -n - 1, -1):
        q1 = max(-n, r - n)
        q2 = min(n, r + n)
        for q in range(q1, q2 + 1):
            if -q > r + (size - 3):
                grid.append(((q, r), R))
            elif r > -q + (size - 3):
                grid.append(((q, r), B))
            else:
                grid.append(((q, r), 0))
    return grid


def start_board_gopher(size: int) -> State:
    grid: State = []
    n = size - 1
    for r in range(n, -n - 1, -1):
        q1 = max(-n, r - n)
        q2 = min(n, r + n)
        for q in range(q1, q2 + 1):
            grid.append(((q, r), 0))
    return grid


def initialize(
    game: str,
    state: State,
    player: Player,
    hex_size: int,
    total_time: Time,
    c_param: float,
    improved_playout: bool,
    root_parallelization: bool,
) -> Environment:
    if game.lower() == "dodo":
        return EngineDodo(
            state,
            player,
            hex_size,
            total_time,
            c_param,
            improved_playout,
            root_parallelization,
        )
    else:
        return EngineGopher(
            state,
            player,
            hex_size,
            total_time,
            c_param,
            improved_playout,
            root_parallelization,
        )


def strategy(
    env: Environment, state: State, player: Player, time_left: float
) -> tuple[Environment, Action]:
    env.update(env.has_played(state))
    if time_left < 120 and len(env.MCTSearchers) > 1:
        env.MCTSearchers = [random.choice(env.MCTSearchers)]
    if env.MCTSearchers[0].is_terminal_node():
        return env, None
    best_action: Action = env.return_best_move(time_left)
    return env, best_action


def new_state_dodo(state: State, action: ActionDodo, player: Player):
    if (action[0], player) not in state:
        print(action[0], player)
    state.remove((action[0], player))
    state.append((action[0], 0))
    state.append((action[1], player))
    state.remove((action[1], 0))


def new_state_gopher(state: State, action: Action, player: Player):
    state.append((action, player))


def dodo(size: int, c1, p1, f1, c2, p2, f2):
    state_tmp = start_board_dodo(size)
    e1 = initialize("dodo", state_tmp, R, size, 120, c1, p1, f1)
    e2 = None
    time_r: float = 300.0
    time_b: float = 300.0
    # e1.MCTSearcher.state.pplot()
    # r = RandomAgent(state_tmp, B, size)
    while True:
        start_time = time.time()
        s = strategy(e1, state_tmp, e1.player, time_r)[1]
        if s is None:
            e1.MCTSearchers[0].state.pplot()
            print(1, end="")
            return 1
        time_r -= time.time() - start_time
        new_state_dodo(state_tmp, s, R)
        e1.MCTSearchers[0].state.pplot()
        if e2 is None:
            e2 = initialize("dodo", state_tmp, B, size, 120, c2, p2, f2)
        start_time = time.time()
        # r.update_state(state_tmp)
        # if r.is_final():
        #     print(2, end="")
        #     return -1
        # s = r.get_action()

        # src = input("Tuple source :")
        # src = ast.literal_eval(src)
        # dest = input("Tuple dest :")
        # dest = ast.literal_eval(dest)
        # s = (src, dest)

        s = strategy(e2, state_tmp, e2.player, time_b)[1]
        if s is None:
            e2.MCTSearchers[0].state.pplot()
            print(2, end="")
            return -1
        time_b -= time.time() - start_time
        new_state_dodo(state_tmp, s, B)


def gopher(size: int, c1, p1, f1, c2, p2, f2):
    state_tmp = start_board_gopher(size)
    e1 = initialize("gopher", state_tmp, R, size, 120, c1, p1, f1)
    e2 = None
    time_r: float = 150.
    time_b: float = 150.

    while True:
        start_time = time.time()
        s = strategy(e1, state_tmp, e1.player, time_r)[1]
        if s is None:
            e1.MCTSearchers[0].state.pplot()
            print(2, end="")
            return -1
        time_r -= time.time() - start_time
        # print(time_r)
        new_state_gopher(state_tmp, s, R)
        e1.MCTSearchers[0].state.pplot()

        if e2 is None:
            e2 = initialize("gopher", state_tmp, B, size, 120, c2, p2, f2)

        start_time = time.time()
        s = strategy(e2, state_tmp, e2.player, time_b)[1]
        # dest = input("Tuple dest :")
        # dest = ast.literal_eval(dest)
        # s = dest
        if s is None:
            e2.MCTSearchers[0].state.pplot()
            print(1, end="")
            return 1
        time_b -= time.time() - start_time
        new_state_gopher(state_tmp, s, B)
        # e2.MCTSearchers[0].state.pplot()


def wrapper(args):
    c1, p1, f1, c2, p2, f2, size = args
    return dodo(size, c1, p1, f1, c2, p2, f2)


def match(nb_games: int, size: int, c1, p1, f1, c2, p2, f2):
    nb_wins = 0
    nb_losses = 0

    with multiprocessing.Pool() as pool:
        args_list = [(c1, p1, f1, c2, p2, f2, size)] * (nb_games // 2)
        results = pool.map(wrapper, args_list)

    for result in results:
        if result == 1:
            nb_wins += 1
        else:
            nb_losses += 1

    with multiprocessing.Pool() as pool:
        args_list = [(c2, p2, f2, c1, p1, f1, size)] * (nb_games // 2)
        results = pool.map(wrapper, args_list)
    for result in results:
        if result == -1:
            nb_wins += 1
        else:
            nb_losses += 1

    print(f"\n({c1:.3f}, {p1}, {f1}) vs ({c2:.3f}, {p2}, {f2})")
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
    # match(100, 4, 1, False, 2, 2, False, 2)
    # dodo(4, 1, False, False, 1, False, False)
    # match(20, 4, 0.5, False, False, 1, False, False)
    gopher(6, 1, False, False, 1, False, False)


if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()
    main()
    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats("tottime")
    stats.print_stats()
