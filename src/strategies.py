from typing import Callable
from copy import deepcopy
from utils import *

State = Board
Strategy = Callable[[State, Player], Action]


def minmax(grid: State, depth: int, player: Player) -> float:
    if depth == 0 or grid.final(player):
        return grid.evaluate_v1(player)
    if player == R:
        best_value = float("-inf")
        for legal in grid.legals(player):
            grid.play(player, legal)
            v = minmax(grid, depth - 1, B)
            grid.undo(player, legal)
            best_value = max(best_value, v)
        return best_value
    else:
        best_value = float("inf")
        for legal in grid.legals(player):
            grid.play(player, legal)
            v = minmax(grid, depth - 1, R)
            grid.undo(player, legal)
            best_value = min(best_value, v)
        return best_value


def minmax_actions(
    grid: State, player: Player, depth: int
) -> tuple[float, list[Action]]:
    if depth == 0 or grid.final(player):
        return grid.evaluate_v1(player), []
    if player == R:
        best_value = float("-inf")
        best_legals: list[Action] = []
        for legal in grid.legals(player):
            grid.play(player, legal)
            v = minmax(grid, depth - 1, B)
            grid.undo(player, legal)
            if v > best_value:
                best_value = v
                best_legals = [legal]
            elif v == best_value:
                best_legals.append(legal)
        return best_value, best_legals
    else:  # minimizing player
        best_value = float("inf")
        best_legals = []
        for legal in grid.legals(player):
            grid.play(player, legal)
            v = minmax(grid, depth - 1, R)
            grid.undo(player, legal)
            if v < best_value:
                best_value = v
                best_legals = [legal]
            elif v == best_value:
                best_legals.append(legal)
        return best_value, best_legals


def alphabeta(grid: State, depth: int, a: float, b: float, player: Player) -> float:
    if depth == 0 or grid.final(player):
        return grid.evaluate_v1(player)
    if player == R:
        best_value = float("-inf")
        for legal in grid.legals(player):
            grid.play(player, legal)
            best_value = max(best_value, alphabeta(grid, depth - 1, a, b, B))
            grid.undo(player, legal)
            a = max(a, best_value)
            if a >= b:
                break  # β cut-off
        return best_value
    else:
        best_value = float("inf")
        for legal in grid.legals(player):
            grid.play(player, legal)
            best_value = min(best_value, alphabeta(grid, depth - 1, a, b, R))
            grid.undo(player, legal)
            b = min(b, best_value)
            if a >= b:
                break  # α cut-off
        return best_value


def alphabeta_actions(
    grid: State, player: Player, depth: int
) -> tuple[float, list[Action]]:
    if depth == 0 or grid.final(player):
        return grid.evaluate_v1(player), []
    if player == R:
        best_value = float("-inf")
        best_legals: list[Action] = []
        for legal in grid.legals(player):
            grid.play(player, legal)
            v = alphabeta(grid, depth - 1, float("-inf"), float("inf"), B)
            grid.undo(player, legal)
            if v > best_value:
                best_value = v
                best_legals = [legal]
            elif v == best_value:
                best_legals.append(legal)
        return best_value, best_legals
    else:  # minimizing player
        best_value = float("inf")
        best_legals = []
        for legal in grid.legals(player):
            grid.play(player, legal)
            v = alphabeta(grid, depth - 1, float("-inf"), float("inf"), R)
            grid.undo(player, legal)
            if v < best_value:
                best_value = v
                best_legals = [legal]
            elif v == best_value:
                best_legals.append(legal)
        return best_value, best_legals


def generate_random_games(board: State, player: Player, n: int):
    count = 0
    for i in range(n):
        board_tmp: State = deepcopy(board)
        current_player = player
        while True:
            s = strategy_random(board_tmp, current_player)
            board_tmp.play(current_player, s)
            if current_player == R:
                current_player = B
            else:
                current_player = R

            if current_player == B and board_tmp.final(B):  # blue wins
                if player == B:
                    count += 1
                break
            if current_player == R and board_tmp.final(R):  # red wins
                if player == R:
                    count += 1
                break
    return count


def strategy_minmax_random(grid: State, player: Player) -> Action:
    list_moves: list[Action] = minmax_actions(grid, player, 4)[1]
    return random.choice(list_moves)


def strategy_alphabeta_random(grid: State, player: Player) -> Action:
    list_moves: list[Action] = alphabeta_actions(grid, player, 4)[1]
    return random.choice(list_moves)


def strategy_random(board: Board, player: Player) -> Action:
    return random.choice(list(board.legals(player)))


def strategy_first_legal(board: Board, player: Player) -> Action:
    return list(board.legals(player))[0]


def strategy_brain(board: Board, player: Player) -> Action:
    print("à vous de jouer: ", end="")
    start_q = int(input("start q :"))
    start_r = int(input("start r :"))
    end_q = int(input("end q :"))
    end_r = int(input("end r :"))
    depart = Hex(start_q, start_r)
    arrive = Hex(end_q, end_r)

    while (depart, arrive) not in board.legals(player):
        print("Coup illégal !")
        start_q = int(input("start q :"))
        start_r = int(input("start r :"))
        end_q = int(input("end q :"))
        end_r = int(input("end r :"))
        depart = Hex(start_q, start_r)
        arrive = Hex(end_q, end_r)

    return depart, arrive


def dodo(
    strategy_rouge: Strategy, strategy_bleu: Strategy, size: int, debug=False
) -> Score:
    b = start_board(size)
    while True:
        s = strategy_rouge(b, 1)
        b.play(1, s)
        if debug:
            b.pplot2()
        if b.final(2):
            return -1
        s = strategy_bleu(b, 2)
        b.play(2, s)
        if debug:
            b.pplot2()
        if b.final(1):
            return 1
