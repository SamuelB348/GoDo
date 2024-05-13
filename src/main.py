import numpy as np
from testing import *
from other import *


def main():

    ##########################
    # DODO
    ##########################

    d: Environment = initialize("dodo", start_board_dodo(4), R, 4, 100)
    d.pplot()

    ##########################
    # GOPHER
    ##########################

    g: Environment = initialize("gopher", start_board_gopher(4), R, 4, 100)
    g.pplot()


if __name__ == "__main__":
    main()
