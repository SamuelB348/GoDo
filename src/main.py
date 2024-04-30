from utils import *


def main():
    b = start_board(4)
    b.pplot()
    for move in b.legals(1):
        print(move[0], move[1])
    r = play(b, 1, (Hex(-3, 0), Hex(-2, 1)))
    r.pplot()

if __name__ == "__main__":
    main()
