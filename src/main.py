import numpy as np
from testing_dodo import *
from testing_gopher import *
from other import *


def main():

    ##########################
    # DODO
    ##########################

    #d: Environment = initialize("dodo", start_board_dodo(4), R, 4, 100)
    #d.pplot()
    #print(d.legals(2))
    #print(dodo(strategy_brain_dodo, strategy_brain_dodo, 4, True))


    ##########################
    # GOPHER
    ##########################

    #print(start_board_gopher(4))
    g: Environment = initialize("gopher", start_board_gopher(4), R, 4, 100)
    g.pplot()
    #print(g.legals(1))
    print(gopher(strategy_brain_gopher, strategy_brain_gopher, 4, True))


if __name__ == "__main__":
    main()
