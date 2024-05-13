import copy
import time
import random
import pprint
import multiprocessing
from itertools import product
import numpy as np
from gameplay import *
from other import print_percentage_bar


def new_state_gopher(grid: State, action: Action, player: Player) -> State:
    pass


def gopher(
    strategy_rouge: Strategy, strategy_bleu: Strategy, size: int, debug=False
) -> Score:
    state_tmp = start_board_gopher(size)
    time_left = 100
    b: EngineGopher = initialize("gopher", state_tmp, R, size, time_left)
    while True:
        s = strategy_rouge(b, state_tmp, R, time_left)
        new_state_gopher(state_tmp, s[1], R)
        b.play(R, s[1])
        if debug:
            b.pplot()
        if b.is_final(B):
            return -1
        s = strategy_bleu(b, state_tmp, B, time_left)
        new_state_gopher(state_tmp, s[1], B)
        b.play(B, s[1])
        if debug:
            b.pplot()
        if b.is_final(R):
            return 1