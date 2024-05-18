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
    # d = EngineDodo(start_board_dodo(10), 10, 100)
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
    match(4, 100, -5.52324828, 1.33774885, -1.21411309, -6.05022081, 1.50063963, -1.19807841)
    # match_vsrandom(5, 10, -5.52324828, 1.33774885, -1.21411309)
    #tuning_dodo(4, 10, 0.01)
    # tuning_dodo_v2(6, 10, 10000)
    #test_strategies(4, 100)

    # dico = dict(start_board_dodo(4))
    # list_list = [list(el) for el in start_board_dodo(4)]
    # print(dico)
    # print(list_list)
    # for i in range(10000):
    #     new = tuple(dico.items())

    # for _ in range(100):
    #     dodo(strategy_random, strategy_random, 4)

    # dodo_vsbrain(-3.22970786, 1.69112454, -1.18968059, 4, R)
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
