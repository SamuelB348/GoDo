from typing import Callable
from copy import deepcopy
import ast
from engine import *


Strategy = Callable[[Engine, State, Player, Time], tuple[Environment, Action]]


def strategy(
    env: Environment, state: State, player: Player, time_left: Time
) -> tuple[Environment, Action]:
    """
    Meilleure stratégie pour le moment (ici alphabeta avec eval_v1)
    """

    env.reset_dicts(state)
    list_moves: list[Action] = env.alphabeta_actions(player, 5, float("-inf"), float("inf"))[1]
    return env, random.choice(list_moves)


##################################################
# Autres stratégies
##################################################


def strategy_brain(env: Environment, state: State, player: Player, time_left: Time) -> tuple[Environment, Action]:
    env.reset_dicts(state)

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


def strategy_random(env: Environment, state: State, player: Player, time_left: Time) -> tuple[Environment, Action]:
    env.reset_dicts(state)
    return env, random.choice(list(env.legals(player)))


def strategy_first_legal(env: Environment, state: State, player: Player, time_left: Time) -> tuple[Environment, Action]:
    env.reset_dicts(state)
    return env, list(env.legals(player))[0]


def strategy_minmax(env: Environment, state: State, player: Player, time_left: Time) -> tuple[Environment, Action]:
    env.reset_dicts(state)
    list_moves: list[Action] = env.minmax_actions(player, 5)[1]
    return env, random.choice(list_moves)


def strategy_alphabeta(
    env: Environment, state: State, player: Player, time_left: Time
) -> tuple[Environment, Action]:
    env.reset_dicts(state)
    list_moves: list[Action] = env.alphabeta_actions(player, 5, float("-inf"), float("inf"))[1]
    return env, random.choice(list_moves)
