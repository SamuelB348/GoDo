import cProfile
import pstats

import numpy as np
from testing_dodo import *
from other import *
import time
import pandas as pd
from collections import defaultdict


def main():

    ##########################
    # DODO
    ##########################
    # d = EngineDodo(start_board_dodo(5), 5, 100)
    # d.pplot(d.grid)
    # match(4, 100, 5.50613098, 2.9965201, -1.01483344, 0, 0.1, 1.26463952, -1.02441619, 0)
    match_vsrandom(4, 100, 1.25002444, 0.26184217, 0.14314292, -0.17516003)
    # tuning_dodo(4, 10, 0.01)
    #test_strategies(4, 100)

    # a = d.iterative_deepening(16, 1, R, d.legals(R), 1.25002444, 0.26184217, 0.14314292, -0.17516003)
    # print(a)
    # a = dodo_vsrandom(1.25002444, 0.26184217, 0.14314292, -0.17516003, 5, R)
    # for _ in range(10):
    #     d = EngineDodo(start_board_dodo(4), 4, 100)
    #     a = d.alphabeta_actions_v1(R, 5, float('-inf'), float('inf'), d.legals(R), 1.25002444, 0.26184217, 0.14314292, -0.17516003)
    # a = dodo(strategy_random, strategy_random, 7)
    # for _ in range(100):
    #     dodo(strategy_random, strategy_random, 10)

    def first_moves(n=1000):
        dico = defaultdict(int)
        count = defaultdict(int)

        for _ in range(n):
            b = initialize("dodo", start_board_dodo(5), R, 5, 0)
            first = strategy_random(b, None, R, 0)
            first_move = first[1]
            count[first_move] += 1

            b.play(R, first_move)

            while True:
                s = strategy_random(b, None, B, 0)
                b.play(B, s[1])

                if b.is_final(R):
                    dico[first_move] += 1
                    break

                s = strategy_random(b, None, R, 0)
                b.play(R, s[1])

                if b.is_final(B):
                    break

        # Calculer le ratio de victoires pour chaque premier coup
        for move in dico:
            dico[move] /= count[move]

        return dico

    def plot_results(data):
        df = pd.DataFrame(list(data.items()), columns=['Tuple', 'Value'])

        # Trier le DataFrame par la colonne 'Value' dans l'ordre décroissant
        df = df.sort_values(by='Value', ascending=False)

        # Créer le barplot
        plt.figure(figsize=(10, 6))
        plt.bar(df['Tuple'].astype(str), df['Value'], color='skyblue')

        # Ajouter des labels et un titre
        plt.xlabel('Tuples')
        plt.ylabel('Values')
        plt.title('Barplot of Tuples vs. Values')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        # Afficher le plot
        plt.show()

    # plot_results(first_moves(10000))

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
