import time
from strategies import *


def test_dodo(n):
    return dodo(strategy_brain, strategy_random, n)


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
    # test_wins(strategy_alphabeta_random, strategy_random, grid_size, nb_games)
    # test_wins(strategy_alphabeta_random, strategy_first_legal, grid_size, nb_games)
    #test_wins(strategy_minmax_random, strategy_minmax_random, grid_size, nb_games)
    test_wins(strategy_alphabeta_random, strategy_alphabeta_random, grid_size, nb_games)

    end = time.time()
    print(f"Runtime: {end - start:.2f} s")

