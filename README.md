# AI for the games of Dodo and Gopher

This repository contains the code for two AI game agents: one for ["Dodo"](https://www.marksteeregames.com/Dodo_rules.pdf) and the other for ["Gopher"](https://www.marksteeregames.com/Gopher_hex_rules.pdf). These are 2 Mark Steere games.

## Some of the Features
- MCTS: the two agents rely on the MCTS research algorithm. Our implementation is based on the UCT for a smarter exploration and exploitation balance, compared to the simple "vanilla" MCTS.
- Root parallelization: This is one of the many parallelization methods used for MCTS. This one seemed the easiest to do in Python, allowing you to run multiple tree instances for more reliable results.
- Transposition table: Our algorithm keeps track of the previously seen positions. Therefore if you reencounter a position due to a transposition, previous results will be added to the current one to gather even more data.
- Smart time management: our time management methods are based on [this paper]([https://www.marksteeregames.com/Dodo_rules.pdf](https://dke.maastrichtuniversity.nl/m.winands/documents/time_management_for_monte_carlo_tree_search.pdf))
[this article](https://www.redblobgames.com/grids/hexagons/) pour la gestion des grilles hexagonales.

## Choses à faire:
- [ ] Améliorer la fonction d'évaluation
- [ ] Prendre en compte le paramètre time dans les méthodes
- [ ] Améliorer le parcours d'états
