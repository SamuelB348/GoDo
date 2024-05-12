import numpy as np
from testing import *
from other import *


def main():
    competition_framework(100, 10, 5, 100)
    #test_strategies(4, 100)
    # match_vsrandom(4, 100, 1, 2, -3)

    # data = read_combs_from_file("best_combs.txt")
    #
    # # Transpose les données pour avoir trois listes de valeurs
    # data_transposed = list(zip(*data))
    #
    # # Plot des courbes
    # plt.plot(data_transposed[0], label='Premiers éléments')
    # plt.plot(data_transposed[1], label='Seconds éléments')
    # plt.plot(data_transposed[2], label='Troisièmes éléments')
    #
    # # Ajoute les titres et légendes
    # plt.title('Courbes des premiers, seconds et troisièmes éléments')
    # plt.xlabel('Index')
    # plt.ylabel('Valeur')
    # plt.legend()
    #
    # # Affiche le plot
    # plt.show()


if __name__ == "__main__":
    main()
