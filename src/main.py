import matplotlib.pyplot as plt
import numpy as np
from testing import *


def main():
    #test_all_strategies(grid_size=4, nb_games=50)
    dodo(strategy_alphabeta, strategy_random, 4, debug=True)


if __name__ == "__main__":
    main()
