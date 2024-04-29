import matplotlib.pyplot as plt
from utils import *


def main():
    b = start_board(4)
    b.pplot()
    for move in b.legals(1):
        print(move[0], move[1])


if __name__ == '__main__':
    main()
