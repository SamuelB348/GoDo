#!/usr/bin/python3

import ast
import argparse
from typing import Dict, Any
from gndclient import start, Action, Score, Player, State, Time, DODO_STR, GOPHER_STR

from src.agents import *


def initialize(
    game: str, state: State, player: Player, hex_size: int, total_time: Time
) -> Environment:
    if game.lower() == "dodo":
        return EngineDodo(state, player, hex_size, total_time, 1.41, False, 2)
    else:
        return EngineGopher(state, player, hex_size, total_time, 1.41, False, 2)


def strategy_brain(
    env: Environment, state: State, player: Player, time_left: Time
) -> tuple[Environment, Action]:
    env.update_state(state)
    best_action: Action = env.return_best_move(time_left)
    return env, best_action


def final_result(state: State, score: Score, player: Player):
    print(f"Ending: {player} wins with a score of {score}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="ClientTesting", description="Test the IA02 python client"
    )

    parser.add_argument("group_id")
    parser.add_argument("members")
    parser.add_argument("password")
    parser.add_argument("-s", "--server-url", default="http://localhost:8080/")
    parser.add_argument("-d", "--disable-dodo", action="store_true")
    parser.add_argument("-g", "--disable-gopher", action="store_true")
    args = parser.parse_args()

    available_games = [DODO_STR, GOPHER_STR]
    if args.disable_dodo:
        available_games.remove(DODO_STR)
    if args.disable_gopher:
        available_games.remove(GOPHER_STR)

    start(
        args.server_url,
        args.group_id,
        args.members,
        args.password,
        available_games,
        initialize,
        strategy_brain,
        final_result,
        gui=True,
    )
