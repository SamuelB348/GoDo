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
    # d = EngineDodo(start_board_dodo(4), 4, 100)
    # d.play(R, ((-3, 0), (-2, 1)))
    #
    # print(d.legals(B))
    # d.play(B, ((0, 2), (-1, 1)))
    # d.pplot()
    # print(d.neighbors((-2, 1), R))
    # print(d.symetrical(d.grid))
    # d.pplot()
    #match(4, 100, 8.872642693757948, 0.8594601582455841, -2.6032144455777058, 8.6709186, 1.9808019, -2.61928918)
    match_vsrandom(4, 4, -8.745262479285948, 2.2106489937139884, -9.061331443015954)
    #tuning_dodo_v2(4, 10, 10000)
    #test_strategies(4, 100)
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
