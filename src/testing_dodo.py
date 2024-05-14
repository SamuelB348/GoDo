import copy
import time
import random
import pprint
import multiprocessing
from itertools import product
import numpy as np
from gameplay import *
from other import print_percentage_bar


def new_state_dodo(grid: State, action: Action, player: Player) -> State:
    for count, box in enumerate(grid):
        if box[0] == action[0]:
            grid[count] = (box[0], 0)
        if box[0] == action[1]:
            grid[count] = (box[0], player)
    return grid


def dodo(
    strategy_rouge: Strategy, strategy_bleu: Strategy, size: int, debug=False
) -> Score:
    state_tmp = start_board_dodo(size)
    time_left = 100
    b: EngineDodo = initialize("dodo", state_tmp, R, size, time_left)
    while True:
        s = strategy_rouge(b, state_tmp, R, time_left)
        new_state_dodo(state_tmp, s[1], R)
        b.play(R, s[1])
        if debug:
            b.pplot()
        if b.is_final(B):
            return -1
        s = strategy_bleu(b, state_tmp, B, time_left)
        new_state_dodo(state_tmp, s[1], B)
        b.play(B, s[1])
        if debug:
            b.pplot()
        if b.is_final(R):
            return 1


def wrapper1(args):
    m, p, c, best_coeffs, grid_size = args
    return dodo_test(m, p, c, best_coeffs[0], best_coeffs[1], best_coeffs[2], grid_size)


def wrapper2(args):
    m, p, c, best_coeffs, grid_size = args
    return dodo_test(best_coeffs[0], best_coeffs[1], best_coeffs[2], m, p, c, grid_size)


def dodo_test(
    m1: float, p1: float, c1: float, m2: float, p2: float, c2: float, size: int
):
    state_tmp = start_board_dodo(size)
    time_left = 100
    b: EngineDodo = initialize("dodo", state_tmp, R, size, time_left)
    while True:
        s = generic_strategy_dodo(b, state_tmp, R, time_left, m1, p1, c1)
        new_state_dodo(state_tmp, s[1], R)
        b.play(R, s[1])
        if b.is_final(B):
            print("1", end="")
            return -1
        s = generic_strategy_dodo(b, state_tmp, B, time_left, m2, p2, c2)
        new_state_dodo(state_tmp, s[1], B)
        b.play(B, s[1])
        if b.is_final(R):
            print("1", end="")
            return 1


def dodo_vsrandom(e: EngineDodo, m1: float, p1: float, c1: float, size: int, player: Player):
    state_tmp = start_board_dodo(size)
    time_left = 100
    b: EngineDodo = copy.deepcopy(e)
    while True:
        s = (
            generic_strategy_dodo(b, state_tmp, R, time_left, m1, p1, c1)
            if player == R
            else strategy_random(b, state_tmp, R, time_left)
        )
        new_state_dodo(state_tmp, s[1], R)
        b.play(R, s[1])
        if b.is_final(B):
            print(B, end="")
            b.pplot()
            return -1
        s = (
            generic_strategy_dodo(b, state_tmp, B, time_left, m1, p1, c1)
            if player == B
            else strategy_random(b, state_tmp, B, time_left)
        )
        new_state_dodo(state_tmp, s[1], B)
        b.play(B, s[1])
        if b.is_final(R):
            print(R, end="")
            b.pplot()
            return 1


def dodo_vsbrain(m1: float, p1: float, c1: float, size: int, player: Player):
    state_tmp = start_board_dodo(size)
    time_left = 100
    b: EngineDodo = initialize("dodo", start_board_dodo(size), R, size, 100)
    while True:
        s = (
            generic_strategy_dodo(b, state_tmp, R, time_left, m1, p1, c1)
            if player == R
            else strategy_brain_dodo(b, state_tmp, R, time_left)
        )
        new_state_dodo(state_tmp, s[1], R)
        b.play(R, s[1])
        b.pplot()
        if b.is_final(B):
            print("1", end="")
            return -1
        s = (
            generic_strategy_dodo(b, state_tmp, B, time_left, m1, p1, c1)
            if player == B
            else strategy_brain_dodo(b, state_tmp, B, time_left)
        )
        new_state_dodo(state_tmp, s[1], B)
        b.play(B, s[1])
        b.pplot()
        if b.is_final(R):
            print("1", end="")
            return 1

def test_wins(strategy1: Strategy, strategy2: Strategy, grid_size: int, nb_games: int):
    print(strategy1.__name__ + " vs " + strategy2.__name__)
    nb_wins = 0
    nb_losses = 0
    for i in range(nb_games):
        print(f"Partie n° {i+1}")
        if i < nb_games // 2:
            a = dodo(strategy1, strategy2, grid_size)
            if a == 1:
                print("joueur 1 gagne")
                nb_wins += 1
            else:
                print("joueur 1 perd")
                nb_losses += 1
        else:
            a = dodo(strategy2, strategy1, grid_size)
            if a == -1:
                print("joueur 1 gagne")
                nb_wins += 1
            else:
                print("joueur 1 perd")
                nb_losses += 1

    print_percentage_bar(nb_wins / nb_games, nb_losses / nb_games, nb_games)


def write_comb_to_file(filename, l):
    with open(filename, "a") as f:
        f.write(str(l) + "\n")


def read_combs_from_file(filename):
    tuples = []
    with open(filename, "r") as f:
        for line in f:
            tuple_data = eval(line.strip())
            tuples.append(tuple_data)
    return tuples


def test_strategies(grid_size: int, nb_games: int):
    already_explored = read_combs_from_file("logs/explored_combs.txt")
    best_coeffs: tuple = (11.87548155797398, 8.472525921917928, -16.631705605300297)

    while True:
        m = random.uniform(-20.0, 20.0)
        p = random.uniform(0.0, 20.0)
        c = random.uniform(-20.0, 0.0)
        if (
            int(m != 0) + int(p != 0) + int(c != 0) >= 3
            and (m, p, c) not in already_explored
        ):
            already_explored.append((m, p, c))
            write_comb_to_file("logs/explored_combs.txt", (m, p, c))

            print(f"mobility : {m}, pos : {p}, con: {c}")
            nb_wins = 0
            nb_losses = 0

            with multiprocessing.Pool() as pool:
                args_list = [(m, p, c, best_coeffs, grid_size)] * (nb_games // 2)
                results = pool.map(wrapper1, args_list)
            for result in results:
                if result == 1:
                    nb_wins += 1
                else:
                    nb_losses += 1

            with multiprocessing.Pool() as pool:
                args_list = [(m, p, c, best_coeffs, grid_size)] * (nb_games // 2)
                results = pool.map(wrapper2, args_list)
            for result in results:
                if result == -1:
                    nb_wins += 1
                else:
                    nb_losses += 1

            print(
                f"\n{[m, p, c]} vs {best_coeffs} : Wins: {nb_wins}, Losses: {nb_losses}"
            )
            print_percentage_bar(nb_wins / nb_games, nb_losses / nb_games, nb_games)
            print()

            if nb_wins >= 0.6 * nb_games:
                best_coeffs = (m, p, c)
            write_comb_to_file("logs/best_combs.txt", best_coeffs)


def tuning_dodo(grid_size: int, nb_games: int, factor: float = 0.01):
    best_coeffs = np.array((8.6709186, 1.9808019, -2.61928918))
    list_best_coeff = []
    count = 0
    while True:
        deltas = np.random.normal(0, 2, 3)
        coeffs_a = tuple(np.add(deltas, best_coeffs))
        coeffs_b = tuple(np.add(-deltas, best_coeffs))
        results = match(grid_size, nb_games, coeffs_a[0], coeffs_a[1], coeffs_a[2], coeffs_b[0], coeffs_b[1], coeffs_b[2])
        if results[0] > 0.5*nb_games:  # coeffs_a ont gagné
            best_coeffs = np.add(best_coeffs, np.subtract(coeffs_a, best_coeffs)*factor)
        else:
            best_coeffs = np.add(best_coeffs, np.subtract(coeffs_b, best_coeffs) * factor)
        print(best_coeffs)
        list_best_coeff.append(best_coeffs)
        if count % 2 == 0:
            plt.plot([coeff[0] for coeff in list_best_coeff])
            plt.plot([coeff[1] for coeff in list_best_coeff])
            plt.plot([coeff[2] for coeff in list_best_coeff])
            plt.show()
        count += 1


def tuning_dodo_v2(grid_size: int, nb_games: int, nb_iter: int, a=0.01, c=0.05):
    best_coeffs = np.array((-10.28453201, 3.12370101, -8.05037163))
    list_best_coeff = []
    count = 0
    alpha = 0.602
    gamma = 0.101
    A = nb_iter * 0.1
    for k in range(nb_iter):
        ak = a / (k + 1 + A)**alpha
        ck = c / (k + 1)**gamma
        delta = np.random.choice([-1, 1], size=3)
        coeffs_a = best_coeffs + ck * delta
        coeffs_b = best_coeffs - ck * delta
        results = match(grid_size, nb_games, coeffs_a[0], coeffs_a[1], coeffs_a[2], coeffs_b[0], coeffs_b[1], coeffs_b[2])
        best_coeffs = best_coeffs + ak * (results[0] - results[1]) / (ck * delta)
        print(best_coeffs)
        list_best_coeff.append(best_coeffs)
        if count % 10 == 0:
            plt.plot([coeff[0] for coeff in list_best_coeff])
            plt.plot([coeff[1] for coeff in list_best_coeff])
            plt.plot([coeff[2] for coeff in list_best_coeff])
            plt.show()
        count += 1


def match(grid_size: int, nb_games: int, m1, p1, c1, m2, p2, c2):
    nb_wins = 0
    nb_losses = 0

    with multiprocessing.Pool() as pool:
        args_list = [(m1, p1, c1, [m2, p2, c2], grid_size)] * (nb_games // 2)
        results = pool.map(wrapper1, args_list)
    for result in results:
        if result == 1:
            nb_wins += 1
        else:
            nb_losses += 1

    with multiprocessing.Pool() as pool:
        args_list = [(m1, p1, c1, [m2, p2, c2], grid_size)] * (nb_games // 2)
        results = pool.map(wrapper2, args_list)
    for result in results:
        if result == -1:
            nb_wins += 1
        else:
            nb_losses += 1

    print(f"\n({m1:.3f}, {p1:.3f}, {c1:.3f}) vs ({m2:.3f}, {p2:.3f}, {c2:.3f})")
    print_percentage_bar(nb_wins / nb_games, nb_losses / nb_games, nb_games)
    return nb_wins, nb_losses


def match_vsrandom(grid_size: int, nb_games: int, m, p, c):
    nb_wins = 0
    nb_losses = 0
    b: EngineDodo = initialize("dodo", start_board_dodo(grid_size), R, grid_size, 100)
    results = []
    for i in range(nb_games // 2):
        results.append(dodo_vsrandom(b, m, p, c, grid_size, R))
    for result in results:
        if result == 1:
            nb_wins += 1
        else:
            nb_losses += 1

    results = []
    for i in range(nb_games // 2):
        results.append(dodo_vsrandom(b, m, p, c, grid_size, B))
    for result in results:
        if result == -1:
            print(1, end="")
            nb_wins += 1
        else:
            print(2, end="")
            nb_losses += 1

    print(f"\n{[m, p, c]} vs random : Wins: {nb_wins}, Losses: {nb_losses}\n")
    print_percentage_bar(nb_wins / nb_games, nb_losses / nb_games, nb_games)


def competition_framework(
    nb_agents: int, nb_agents_per_comp: int, grid_size: int, nb_games: int
):
    best_agents = []

    # Initialisation des agents
    for _ in range(nb_agents // nb_agents_per_comp):
        a = np.random.uniform(0, 20, nb_agents_per_comp)
        b = np.random.uniform(0, 20, nb_agents_per_comp)
        c = np.random.uniform(-20, 0, nb_agents_per_comp)
        agent_group = np.stack((a, b, c), axis=-1)
        best_agents.append(agent_group.tolist())
    pprint.pp(best_agents)

    while len(best_agents[0]) != 1:
        winners = []
        for group in best_agents:
            print("Nouvelle competition : ")
            scores = [[0 for _ in range(len(group))] for _ in range(len(group))]
            for i in range(len(group)):
                for j in range(len(group)):
                    if np.any(group[i] != group[j]) and i < j:
                        m1 = group[i][0]
                        p1 = group[i][1]
                        c1 = group[i][2]
                        m2 = group[j][0]
                        p2 = group[j][1]
                        c2 = group[j][2]
                        score = match(grid_size, nb_games, m1, p1, c1, m2, p2, c2)
                        scores[i][j] = score[0]
                        scores[j][i] = score[1]
                        pprint.pprint(scores)
            results = np.sum(np.array(scores), axis=1)
            best_agent = np.argmax(results)
            print(group[best_agent])
            winners.append(group[best_agent])
            print()

        if len(winners) != 1:
            best_agents = []
            for i in range(0, len(winners), nb_agents_per_comp):
                best_agents.append([winners[i : i + nb_agents_per_comp - 1]])
            print("Les gagnants sont : ")
            pprint.pp(best_agents)
        else:
            best_agents = winners
            pprint.pp(best_agents)
            break
