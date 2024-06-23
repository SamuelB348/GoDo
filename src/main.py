#!/usr/bin/python3

import ast
import argparse
from typing import Dict, Any
import random
from gndclient import start, Action, Score, Player, State, Time, DODO_STR, GOPHER_STR
from agents import *


def initialize(
    game: str, state: State, player: Player, hex_size: int, total_time: Time
) -> Environment:
    print("je joue", player)
    if game.lower() == "dodo":
        return EngineDodo(
            state, 
            player, 
            hex_size, 
            total_time, 
            c_param=1, 
            improved_playout=False, 
            root_parallelization=False
        )
    else:
        return EngineGopher(
            state, 
            player, 
            hex_size, 
            total_time, 
            c_param=1, 
            improved_playout=False, 
            root_parallelization=False
        )


def strategy(
    env: Environment, state: State, player: Player, time_left: Time
) -> tuple[Environment, Action]:
    # If time falls under 120 s, we stop root parallelization
    if time_left < 120 and len(env.MCTSearchers) > 1:
        env.MCTSearchers = random.choice(env.MCTSearchers)
    env.update(env.has_played(state))
    best_action: Action = env.return_best_move(time_left)
    return env, best_action


def final_result(state: State, score: Score, player: Player):
    MonteCarloTreeSearchNode.STATE_CACHE = {}
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
        strategy,
        final_result,
        gui=True,
    )
