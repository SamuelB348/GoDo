import numpy as np
from testing import *
from other import *


def main():
    #competition_framework(25, 5, 4, 20)
    test_strategies(4, 100)
    #match_vsrandom(5, 100, 11.87548155797398, 8.472525921917928, -16.631705605300297)
    #match(4, 200, 8.872642693757948, 0.8594601582455841, -2.6032144455777058, 18.336937403648957, 11.890445116925694, -12.795412743345464)
    #dodo_vsbrain(11.87548155797398, 8.472525921917928, -16.631705605300297, 4, R)
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
