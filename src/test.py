"""
This section implements simple game loops to test the agents.
It's not meant to be clean code.
"""

import cProfile
import pstats
import random
import time
import ast

from types_constants import *
from agents import EngineDodo, EngineGopher


Environment = Union[EngineDodo, EngineGopher]


def start_board_dodo(size: int) -> State:
    """
    Generates a starting board configuration for Dodo.

    :param size: the size of the board
    :return: a state
    """

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
    """
    Generates a starting board configuration for Gopher.

    :param size: the size of the board
    :return: a state
    """

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
    """
    Initializes a game environment (an Engine).

    """

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
    env: Environment, state: State, time_left: float
) -> tuple[Environment, Action]:
    """
    Returns the action chosen by the environment.

    """

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
    state.remove((action, 0))


def dodo(
        size: int,
        c_param1,
        improved_playout1,
        root_parallelization1,
        c_param2,
        improved_playout2,
        root_parallelization2
):
    """
    Game loop for Dodo.

    """

    state_tmp = start_board_dodo(size)
    e1 = initialize("dodo", state_tmp, R, size, 300, c_param1, improved_playout1, root_parallelization1)
    e2 = None
    time_r: float = 300.0
    time_b: float = 300.0

    while True:
        start_time = time.time()
        s = strategy(e1, state_tmp, time_r)[1]
        if s is None:
            e1.MCTSearchers[0].state.pplot()
            print(1, end="")
            return 1
        time_r -= time.time() - start_time
        new_state_dodo(state_tmp, s, R)
        e1.MCTSearchers[0].state.pplot()

        if e2 is None:
            e2 = initialize("dodo", state_tmp, B, size, 300, c_param2, improved_playout2, root_parallelization2)
        start_time = time.time()
        s = strategy(e2, state_tmp, time_b)[1]
        if s is None:
            e2.MCTSearchers[0].state.pplot()
            print(2, end="")
            return -1
        time_b -= time.time() - start_time
        new_state_dodo(state_tmp, s, B)


def gopher(
        size: int,
        c_param1,
        improved_playout1,
        root_parallelization1,
        c_param2,
        improved_playout2,
        root_parallelization2
):
    """
    Game loop for Gopher.

    """

    state_tmp = start_board_gopher(size)
    e1 = initialize("gopher", state_tmp, R, size, 150, c_param1, improved_playout1, root_parallelization1)
    e2 = None
    time_r: float = 150.
    time_b: float = 150.

    while True:
        start_time = time.time()
        s = strategy(e1, state_tmp, time_r)[1]
        if s is None:
            e1.MCTSearchers[0].state.pplot()
            print(2, end="")
            return -1
        time_r -= time.time() - start_time

        new_state_gopher(state_tmp, s, R)
        e1.MCTSearchers[0].state.pplot()

        if e2 is None:
            e2 = initialize("gopher", state_tmp, B, size, 150, c_param2, improved_playout2, root_parallelization2)
        start_time = time.time()
        s = strategy(e2, state_tmp, time_b)[1]
        if s is None:
            e2.MCTSearchers[0].state.pplot()
            print(1, end="")
            return 1
        time_b -= time.time() - start_time
        new_state_gopher(state_tmp, s, B)


def main():
    # dodo(4, 1, False, False, 1, False, False)
    gopher(6, 1, False, False, 1, False, False)


if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()
    main()
    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats("tottime")
    stats.print_stats()
