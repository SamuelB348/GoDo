import random
from typing import Callable, Union
import ast
from engine_dodo import *
from engine_gopher import *


Environment = Union[EngineDodo, EngineGopher]
Action = Union[ActionGopher, ActionDodo]
Strategy = Callable[[Environment, State, Player, Time], tuple[Environment, Action]]


#########################
# Initialisation de DODO
#########################


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
            else:
                grid.append((Cell(q, r), 0))
    return grid


###########################
# Initialisation de GOPHER
###########################

def start_board_gopher(size: int) -> State:
    grid: State = []
    n = size - 1
    for r in range(n, -n - 1, -1):
        q1 = max(-n, r - n)
        q2 = min(n, r + n)
        for q in range(q1, q2 + 1):
            grid.append((Cell(q, r), 0))
    return grid


##################################################
# Initialisation générale
##################################################


def initialize(
    game: str, state: State, player: Player, hex_size: int, total_time: Time
) -> Environment:
    if game.lower() == "dodo":
        env = EngineDodo(state, hex_size, total_time)
        return env
    elif game.lower() == "gopher":
        env = EngineGopher(state, hex_size, total_time)
        return env


def final_result(state: State, score: Score, player: Player):
    pass


##################################################
# Différentes stratégies
##################################################


def strategy_brain_dodo(
    env: Environment, state: State, player: Player, time_left: Time
) -> tuple[Environment, Action]:
    env.update_state(state)

    print("à vous de jouer: ", end="")
    src = input("Tuple source :")
    src = ast.literal_eval(src)
    src_cell: Cell = Cell(int(src[0]), int(src[1]))
    dest = input("Tuple dest :")
    dest = ast.literal_eval(dest)
    dest_cell: Cell = Cell(int(dest[0]), int(dest[1]))

    while (src, dest) not in list(env.legals(player)):
        print("Coup illégal !")
        src = input("Tuple source :")
        src = ast.literal_eval(src)
        src_cell = Cell(int(src[0]), int(src[1]))
        dest = input("Tuple dest :")
        dest = ast.literal_eval(dest)
        dest_cell = Cell(int(dest[0]), int(dest[1]))

    return env, (src_cell, dest_cell)


def strategy_brain_gopher(
    env: Environment, state: State, player: Player, time_left: Time
) -> tuple[Environment, Action]:
    pass


def strategy_random(
    env: Environment, state: State, player: Player, time_left: Time
) -> tuple[Environment, Action]:
    # env.update_state(state)
    return env, random.choice(env.legals(player))


def generic_strategy_dodo(
    env: Environment,
    state: State,
    player: Player,
    time_left: Time,
    m: float,
    p: float,
    c: float,
) -> tuple[Environment, Action]:
    env.update_state(state)

    opponent: Player = R if player == B else B
    legals = env.legals(player)
    legals_opp = env.legals(opponent)

    if len(legals) == 1:
        return env, legals[0]

    # depth = env.adaptable_depth_v2(len(legals), len(legals_opp), 1000000, 12)
    # depth = env.adaptable_depth_v1(len(legals), 8, 3, 7)

    depth = 2
    list_moves: list[ActionDodo] = env.alphabeta_actions_v1(
        state,
        player,
        depth,
        float("-inf"),
        float("inf"),
        legals,
        m,
        p,
        c,
    )[1]

    # for action in list_moves:
    #     if player == R and hex_sub(action[1], action[0]) == hex_directions[2]:
    #         return env, action
    #     if player == B and hex_sub(action[1], action[0]) == hex_directions[5]:
    #         return env, action

    return env, random.choice(list_moves)
