from testing import *


def main():
    # test_all_strategies(grid_size=4, nb_games=10)
    dodo(strategy_alphabeta_random, strategy_brain, 4)


if __name__ == "__main__":
    main()
