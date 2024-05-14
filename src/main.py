import numpy as np
from testing_dodo import *
from other import *


def main():

    ##########################
    # DODO
    ##########################

    d: Environment = initialize("dodo", start_board_dodo(4), R, 4, 100)
    d.pplot()
    #match(4, 100, 8.872642693757948, 0.8594601582455841, -2.6032144455777058, 8.6709186, 1.9808019, -2.61928918)
    tuning_dodo_v2(4, 10, 10000)
    #test_strategies(4, 100)
    ##########################
    # GOPHER
    ##########################

    # g: Environment = initialize("gopher", start_board_gopher(4), R, 4, 100)
    # g.pplot()


if __name__ == "__main__":
    main()
