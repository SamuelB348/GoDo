import time
from strategies import *


def new_state(grid: State, action: Action, player: Player) -> State:
    for i in range(len(grid)):
        if grid[i][0] == action[0]:
            grid[i] = (grid[i][0], 0)
        if grid[i][0] == action[1]:
            grid[i] = (grid[i][0], player)
    return grid


def dodo(
    strategy_rouge: Strategy, strategy_bleu: Strategy, size: int, debug=False
) -> Score:
    state_tmp = start_board(size)
    time_left = 100
    b: Engine = initialize("dodo", state_tmp, R, size-1, time_left)
    b.pplot()
    while True:
        s = strategy_rouge(b, state_tmp, R, time_left)
        new_state(state_tmp, s[1], R)
        b.play(R, s[1])
        if debug:
            b.pplot()
        if b.is_final(B):
            return -1
        s = strategy_bleu(b, state_tmp, B, time_left)
        new_state(state_tmp, s[1], B)
        b.play(B, s[1])
        if debug:
            b.pplot()
        if b.is_final(R):
            return 1


def print_percentage_bar(percentage1, percentage2, sample_size):
    total_length = 100

    green_length = int(total_length * percentage1)
    red_length = int(total_length * percentage2)

    green_part = "=" * green_length
    red_part = "=" * red_length

    # Affichage de la barre de pourcentage avec les couleurs appropriées
    print(
        "\033[32m"
        + green_part
        + "\033[0m"
        + "|"
        + "\033[31m"
        + red_part
        + "\033[0m"
        + f" {percentage1*sample_size:.0f} vs {percentage2*sample_size:.0f}"
    )


def test_wins(strategy1: Strategy, strategy2: Strategy, grid_size: int, nb_games: int):
    print(strategy1.__name__ + " vs " + strategy2.__name__)
    nb_wins = 0
    nb_losses = 0
    for i in range(nb_games):
        print(f"Partie n° {i+1}")
        if i < nb_games // 2:
            a = dodo(strategy1, strategy2, grid_size)
            if a == 1:
                nb_wins += 1
            else:
                nb_losses += 1
        else:
            a = dodo(strategy2, strategy1, grid_size)
            if a == -1:
                nb_wins += 1
            else:
                nb_losses += 1

    print_percentage_bar(nb_wins / nb_games, nb_losses / nb_games, nb_games)


def test_all_strategies(grid_size: int, nb_games: int):
    start = time.time()

    # test_wins(strategy_random, strategy_random, grid_size, nb_games)
    # test_wins(strategy_first_legal, strategy_first_legal, grid_size, nb_games)
    # test_wins(strategy_first_legal, strategy_random, grid_size, nb_games)
    test_wins(strategy_alphabeta, strategy_random, grid_size, nb_games)
    #test_wins(strategy_minmax_random, strategy_random, grid_size, nb_games)
    # test_wins(strategy_alphabeta_random, strategy_first_legal, grid_size, nb_games)
    # test_wins(strategy_minmax_random, strategy_minmax_random, grid_size, nb_games)
    # test_wins(strategy_alphabeta_random, strategy_alphabeta_random, grid_size, nb_games)

    end = time.time()
    print(f"Runtime: {end - start:.2f} s")
