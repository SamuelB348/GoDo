# GoDo : an AI for the games of Gopher and Dodo

This repository contains the code for two AI game agents: one for ["Dodo"](https://www.marksteeregames.com/Dodo_rules.pdf) and the other for ["Gopher"](https://www.marksteeregames.com/Gopher_hex_rules.pdf). These are 2 Mark Steere games :red_circle::large_blue_circle:.

## Some of the Features

- :herb: **MCTS**: The two agents rely on the MCTS research algorithm. Our implementation is based on the UCT for a smarter exploration and exploitation balance, compared to the simple "vanilla" MCTS.
- :twisted_rightwards_arrows: **Root parallelization**: This is one of the many parallelization methods used for MCTS. This one seemed the easiest to implement in Python, allowing you to run multiple tree instances for more reliable results.
- :clipboard: **Transposition table**: Our algorithm keeps track of the previously seen positions. Therefore if you reencounter a position due to a transposition, previous results will be added to the current one to gather even more data.
- :hourglass: **Smart time management**: Our time management method is based on [this paper](https://dke.maastrichtuniversity.nl/m.winands/documents/time_management_for_monte_carlo_tree_search.pdf). It calculates the expected number of moves left until the end of the game to adapt its allocated time. It also uses early stop conditions to stop the search if no better solution can be found during the next expected iterations.

## Tech used

These AIs are fully written in Python 3 :snake:.

## Credits
- Thanks to all the IA02 professors at the UTC (Université de Technologie de Compiègne) for this very interesting project.
- Thanks to [Mark Steere](https://www.marksteeregames.com/) for these 2 great games that were fun to program.
- Thanks to [this page](https://ai-boson.github.io/mcts/) that helped us a lot going through MCTS implementation.
- A big thanks to [this article](https://www.redblobgames.com/grids/hexagons/) that helped us understand hexagonal grids and their representations.
- Thanks to the Maastricht University's prolific paper production on AI for games.

## For IA02 professors
### Evaluation
You can run `pylint` and `mypy` on the `src` directory. Please do not consider the test.py, gndclient.py, and main.py files for your evaluation. The first is just a testing file for ourselves that is not meant to be evaluated. The two latter are the 2 utilities supplied (test_client.py became main.py). You can use the followings commands:
```
pylint src --ignore=test.py,gndclient.py,main.py
```
and
```
mypy src --exclude 'test.py|main.py|gndclient.py'
```

### How to run the program
Change to the `src` directory. After that, you can run the commands you gave us to connect to the server and play (be careful `test_client.py` became `main.py`):
```
py main.py 12 "toto" "test"
```

If you want to play with the different features of our AI, you can go inside the `main.py` file, go to the `initialize` function and change the parameters inside the EngineDodo/EngineGopher classes (one is called `improved_playout` and the other is called `root_parallelization`, you can set them to `True`).

If you really want to test the `test.py` you can do it, you just have to choose the game you want to launch in the `main()` function, and you can run the program. It will display the grid as a plot.

In both cases, our program will print on the terminal some stats on the ongoing game that should be self-explanatory.

### The cons of our program
Here are the weaknesses of our program. They are essentially side effects of the different features we implemented:
- Parallelization in Python can be quite "slow" and add a significant overhead. Therefore, we make many more simulations, but under time pressure it is not adapted (we didn't use it for the tournament).
- The improved playout policy is a simple but efficient improvement of MCTS, even when we use min-max with very shallow depth (1 or 2). However, it takes a lot more time to complete the same number of iterations. That's why we didn't use this feature during the tournament.
- Dodo and Gopher are not the same games even though they are similar. Therefore, choosing the same algorithm (MCTS) may not be the best option. If you look at Ludii's versions of the 2 games, it uses MCTS for [Dodo](https://ludii.games/details.php?keyword=Dodo) but Alpha-beta for [Gopher](https://ludii.games/details.php?keyword=Gopher). However, our MCTS for Gopher still gave very good results.
