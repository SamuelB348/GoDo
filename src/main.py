import cProfile
import pstats

import numpy as np
from testing_dodo import *
from other import *
import time


def main():

    ##########################
    # DODO
    ##########################
    d = EngineDodo(start_board_dodo(4), 4, 100)
    # for _ in range(10000):
    #     a = d.hash_dict()

    # for _ in range(10000):
    #     a = hash(tuple(d.grid.items()))
    # d.play(R, ((-3, 0), (-2, 1)))
    # d.play(B, ((0, 2), (-1, 1)))
    # d.pplot()
    # a = d.hash_dict()
    # # d.grid = dict(d.symetrical(d.grid))
    # d.undo(B, ((0, 2), (-1, 1)))
    # d.pplot()
    # b = d.hash_dict()
    # print(a == b)
    # d.pplot()
    # d.grid = dict(d.symetrical(d.grid))
    # d.pplot()
    # d.generate_grid_heatmaps()
    # print(d.evaluate_v1(B, 1, 1, 1))
    # grid_heatmap_plot(d.grid_weights_R_dist, 10)
    # grid_heatmap_plot(d.grid_weights_B_dist, 10)
    # print(d.legals(R))
    # d.play(R, ((-3, 0), (-2, 1)))
    # d.pplot()
    # print(d.legals(B))
    # d.play(B, ((0, 2), (-1, 1)))
    # d.pplot()
    # print(d.neighbors((-2, 1), R))
    # print(d.symetrical(d.grid))
    # d.pplot()
    # match(4, 100, -5.52324828, 1.33774885, -1.21411309, -16.65091422, 8.74257623, -7.67015625)
    # match_vsrandom(4, 100, -3.1584889, 1.26463952, -1.02441619)
    # tuning_dodo(4, 10, 0.01)
    # tuning_dodo_v2(6, 10, 10000)
    #test_strategies(4, 100)

    # dico = dict(start_board_dodo(4))
    # list_list = [list(el) for el in start_board_dodo(4)]
    # print(dico)
    # print(list_list)
    # for i in range(10000):
    #     new = tuple(dico.items())
    # d = EngineDodo(start_board_dodo(4), 4, 100)
    # # legal = ((-6, 0), (-5, 1))
    # for _ in range(200):
    #     a = d.alphabeta_actions_v1(start_board_dodo(4), R, 2, float('-inf'), float('inf'), d.legals(R), 1, 0, 0)

    # dodo_vsbrain(-5.52324828, 1.33774885, -1.21411309, 4, R)

    # print(d.hash_dict())
    for _ in range(10):
        dodo(strategy_random, strategy_random, 10)
    ##########################
    # GOPHER
    ##########################

    # g: Environment = initialize("gopher", start_board_gopher(4), R, 4, 100)
    # g.pplot()


if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()
    main()
    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats('tottime')
    stats.print_stats()
