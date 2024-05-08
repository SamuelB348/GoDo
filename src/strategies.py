import random
from typing import Callable
import ast
from engine import *


Strategy = Callable[[Environment, State, Player, Time], tuple[Environment, Action]]


def strategy(
    env: Environment, state: State, player: Player, time_left: Time
) -> tuple[Environment, Action]:
    """
    Meilleure stratégie pour le moment (ici alphabeta avec eval_v1)
    """

    env.update_state(state)
    list_moves: list[Action] = env.alphabeta_actions(
        player, 5, float("-inf"), float("inf")
    )[1]
    return env, random.choice(list_moves)


##################################################
# Autres stratégies
##################################################


def strategy_brain(
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


def strategy_random(
    env: Environment, state: State, player: Player, time_left: Time
) -> tuple[Environment, Action]:
    env.update_state(state)
    return env, random.choice(list(env.legals(player)))


def strategy_first_legal(
    env: Environment, state: State, player: Player, time_left: Time
) -> tuple[Environment, Action]:
    env.update_state(state)
    return env, list(env.legals(player))[0]


def strategy_alphabeta(
    env: Environment, state: State, player: Player, time_left: Time
) -> tuple[Environment, Action]:
    env.update_state(state)
    list_moves: list[Action] = env.alphabeta_actions(
        player, 5, float("-inf"), float("inf")
    )[1]
    return env, random.choice(list_moves)


def strategy_alphabeta_adapt_depth_8_2_7(
    env: Environment, state: State, player: Player, time_left: Time
) -> tuple[Environment, Action]:
    env.update_state(state)
    depth = env.adaptable_depth(len(env.legals(player)), 8, 2, 7)
    list_moves: list[Action] = env.alphabeta_actions(
        player, depth, float("-inf"), float("inf")
    )[1]
    return env, random.choice(list_moves)


def strategy_alphabeta_adapt_depth_9_2_6(
    env: Environment, state: State, player: Player, time_left: Time
) -> tuple[Environment, Action]:
    env.update_state(state)
    depth = env.adaptable_depth(len(env.legals(player)), 9, 2, 6)
    print(depth)
    list_moves: list[Action] = env.alphabeta_actions(
        player, depth, float("-inf"), float("inf")
    )[1]
    return env, random.choice(list_moves)


def strategy_alphabeta_v2(
    env: Environment, state: State, player: Player, time_left: Time
) -> tuple[Environment, Action]:
    env.update_state(state)
    depth = env.adaptable_depth(len(env.legals(player)), 8, 2, 7)
    print(depth)
    list_moves: list[Action] = env.alphabeta_actions_v2(
        player, depth, float("-inf"), float("inf")
    )[1]
    return env, random.choice(list_moves)


##################################################
# Autres fonctions permettant l'initialisation
##################################################


def new_state(grid: State, action: Action, player: Player) -> State:
    for count, box in enumerate(grid):
        if box[0] == action[0]:
            grid[count] = (box[0], 0)
        if box[0] == action[1]:
            grid[count] = (box[0], player)
    return grid


def add_dicts(dict1, dict2, player: Player):
    for key in dict2.keys():
        if dict2[key] == player:
            dict1[key] += 1


def grid_heatmap(nb_games: int, board_size: int, player: Player):
    count_dict: dict[Cell, float] = dict(start_board(board_size))
    for el in count_dict.keys():
        count_dict[el] = 0

    victory_count: int = 0
    for i in range(nb_games):
        state_tmp = start_board(board_size)
        b: Engine = Engine(state_tmp, board_size, 100)
        while True:
            s = strategy_random(b, state_tmp, R, 100)
            new_state(state_tmp, s[1], R)
            b.play(R, s[1])
            if b.is_final(B):
                if player == B:
                    victory_count += 1
                    add_dicts(count_dict, dict(state_tmp), B)
                break
            s = strategy_random(b, state_tmp, B, 100)
            new_state(state_tmp, s[1], B)
            b.play(B, s[1])
            if b.is_final(R):
                if player == R:
                    victory_count += 1
                    add_dicts(count_dict, dict(state_tmp), R)
                break

    for el in count_dict.keys():
        count_dict[el] /= victory_count
    return count_dict


def initialize(
    game: str, state: State, player: Player, hex_size: int, total_time: Time
) -> Environment:
    if game.lower() == "dodo":
        env = Engine(state, hex_size, total_time)
        env.grid_weights_R = grid_heatmap((3*hex_size**2-3*hex_size+1)*10, hex_size, R)
        env.grid_weights_B = grid_heatmap((3*hex_size**2-3*hex_size+1)*10, hex_size, B)
        return env
    else:
        return Engine(state, hex_size, total_time)