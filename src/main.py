from utils import *
import time


def test_play2():
    b = start_board(4)
    total_time = 0

    for i in range(5000):
        start_time = time.time()
        b.play(1, (Hex(-3, 0), Hex(-2, 1)))
        end_time = time.time()
        execution_time = end_time - start_time
        total_time += execution_time

    average_time = total_time / 5000
    return average_time


def test_dodo(n):
    return dodo(strategy_random, strategy_random, n)


def main():
    a = test_dodo(4)
    print(a)


if __name__ == "__main__":
    main()
