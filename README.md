# AI for the games of Dodo and Gopher

This repository contains the code for two AI game agents: one for ["Dodo"](https://www.marksteeregames.com/Dodo_rules.pdf) and the other for ["Gopher"](https://www.marksteeregames.com/Gopher_hex_rules.pdf). These are 2 Mark Steere games :red_circle::large_blue_circle:.

## Some of the Features

- :herb: **MCTS**: The two agents rely on the MCTS research algorithm. Our implementation is based on the UCT for a smarter exploration and exploitation balance, compared to the simple "vanilla" MCTS.
- :twisted_rightwards_arrows: **Root parallelization**: This is one of the many parallelization methods used for MCTS. This one seemed the easiest to do in Python, allowing you to run multiple tree instances for more reliable results.
- :clipboard: **Transposition table**: Our algorithm keeps track of the previously seen positions. Therefore if you reencounter a position due to a transposition, previous results will be added to the current one to gather even more data.
- :hourglass: **Smart time management**: Our time management method is based on [this paper](https://dke.maastrichtuniversity.nl/m.winands/documents/time_management_for_monte_carlo_tree_search.pdf). It calculates the expected number of moves left until the end of the game to adapt its allowed time. It also uses early stop conditions to stop the search if no better solution can be found during the next expected iterations.

## Tech used

These AIs are fully written in Python 3 :snake: essentially for readability and ease of programming.

## Credits
- Thanks to [Mark Steere](https://www.marksteeregames.com/) for these 2 great games that were fun to program.
- A big thanks to [this article](https://www.redblobgames.com/grids/hexagons/) that helped us understand hexagonal grids and their representations.
