import multiprocessing
import cProfile
import pstats
import ast

from mcts import *
from utils import *
from board_utils import BoardUtils


class Engine:
    def __init__(
        self, state: State, player: Player, hex_size: int, total_time: Time, c: float, p: float, f: float
    ):

        # -------------------- Basic attributes -------------------- #

        self.player: Player = player
        self.opponent: Player = R if self.player == B else B
        self.size: int = hex_size

        # -------------------- Board utilities -------------------- #

        self.board_utils = BoardUtils(hex_size, state)

        # -------------------- Monte Carlo Tree Searcher -------------------- #

        self.c: float = c
        self.p: float = p
        self.f: float = f
        self.MCTSearcher: MonteCarloTreeSearchNode = MonteCarloTreeSearchNode(
            GameStateDodo(
                self.board_utils.state_to_dict(state),
                R,
                hex_size,
                self.board_utils.R_POV_NEIGHBORS,
                self.board_utils.B_POV_NEIGHBORS,
                self.board_utils.CELL_KEYS,
                self.board_utils.TURN_KEY,
                self.board_utils.start_hash
            ),
            player,
            c,
            p
        )

        # -------------------- Time Management -------------------- #

        self.time: Time = total_time
        self.previous_mean_game_length: int = total_time

    def return_best_move(self, time_left: float) -> ActionDodo:
        time_allocated: float = self.f * (time_left / self.previous_mean_game_length)
        best_children, mean_game_length = self.MCTSearcher.best_action(time_allocated)
        self.MCTSearcher = best_children
        self.MCTSearcher.parent = None

        if mean_game_length is not None:
            self.previous_mean_game_length = mean_game_length
            # print(f"{time_left:.2f}, {time_allocated:.2f}, {mean_game_length:.2f}")
        # print(best_children)

        return best_children.parent_action

    def update_state(self, state: State):
        grid = self.board_utils.state_to_dict(state)
        current_legals: list[ActionDodo] = self.MCTSearcher.state.get_legal_actions()
        has_played: Optional[ActionDodo] = None
        for legal in current_legals:
            if grid[legal[0]] == 0 and grid[legal[1]] == self.opponent:
                has_played = legal
                break

        if has_played in self.MCTSearcher.untried_actions:
            next_state = self.MCTSearcher.state.move(has_played)
            self.MCTSearcher = MonteCarloTreeSearchNode(
                next_state,
                self.player,
                self.c,
                self.p,
                parent=self.MCTSearcher,
                parent_action=has_played,
            )
        else:
            for child in self.MCTSearcher.children:
                if child.parent_action == has_played:
                    self.MCTSearcher = child
                    self.MCTSearcher.parent = None


Environment = Engine


def start_board_dodo(size: int) -> State:
    grid: State = []
    n = size - 1
    for r in range(n, -n - 1, -1):
        q1 = max(-n, r - n)
        q2 = min(n, r + n)
        for q in range(q1, q2 + 1):
            if -q > r + (size - 3):
                grid.append((Cell(q, r), R))
            elif r > -q + (size - 3):
                grid.append((Cell(q, r), B))
            # else:
            #     grid.append((Cell(q, r), 0))
    return grid


def initialize(
    game: str, state: State, player: Player, hex_size: int, total_time: Time, c: float, p: float, f: float
) -> Environment:
    if game.lower() == "dodo":
        return Engine(state, player, hex_size, total_time, c, p, f)
    else:
        pass


def strategy(
    env: Environment, state: State, player: Player, time_left: float
) -> tuple[Environment, Action]:
    env.update_state(state)
    if env.MCTSearcher.is_terminal_node():
        return env, None
    best_action: Action = env.return_best_move(time_left)
    return env, best_action


def final_result(state: State, score: Score, player: Player):
    pass


def new_state_dodo(state: State, action: Action, player: Player):
    state.remove((action[0], player))
    state.append((action[1], player))


def dodo(size: int, c1, p1, f1, c2, p2, f2):
    state_tmp = start_board_dodo(size)
    e1 = initialize("dodo", state_tmp, R, size, 120, c1, p1, f1)
    # e1.MCTSearcher.state.pplot()
    e2 = initialize("dodo", state_tmp, B, size, 120, c2, p2, f2)
    time_r: float = 120.
    time_b: float = 120.
    i = 0
    while True:
        start_time = time.time()
        s = strategy(e1, state_tmp, e1.player, time_r)[1]
        if s is None:
            e1.MCTSearcher.state.pplot()
            print(1, end="")
            return 1
        time_r -= time.time() - start_time
        # if i % 2 == 0:
        #     e1.MCTSearcher.state.pplot()
        new_state_dodo(state_tmp, s, R)

        start_time = time.time()
        s = strategy(e2, state_tmp, e2.player, time_b)[1]
        # src = input("Tuple source :")
        # src = ast.literal_eval(src)
        # dest = input("Tuple dest :")
        # dest = ast.literal_eval(dest)
        # s = (src, dest)
        if s is None:
            e2.MCTSearcher.state.pplot()
            print(2, end="")
            return -1
        time_b -= time.time() - start_time
        new_state_dodo(state_tmp, s, B)
        # i += 1


def wrapper(args):
    c1, p1, f1, c2, p2, f2, size = args
    return dodo(size, c1, p1, f1, c2, p2, f2)


def match(nb_games: int, size: int, c1, p1, f1, c2, p2, f2):
    nb_wins = 0
    nb_losses = 0

    with multiprocessing.Pool() as pool:
        args_list = [(c1, p1, f1, c2, p2, f2, size)] * (nb_games // 2)
        results = pool.map(wrapper, args_list)

    for result in results:
        if result == 1:
            nb_wins += 1
        else:
            nb_losses += 1

    with multiprocessing.Pool() as pool:
        args_list = [(c2, p2, f2, c1, p1, f1, size)] * (nb_games // 2)
        results = pool.map(wrapper, args_list)
    for result in results:
        if result == -1:
            nb_wins += 1
        else:
            nb_losses += 1

    print(f"\n({c1:.3f}, {p1}, {f1}) vs ({c2:.3f}, {p2}, {f2})")
    print_percentage_bar(nb_wins / nb_games, nb_losses / nb_games, nb_games)
    return nb_wins, nb_losses


def tuning_dodo(grid_size: int, nb_games: int, factor: float = 0.01):
    best_coeffs = np.array([0.17653504])
    list_best_coeff = []
    count = 0
    while True:
        deltas = np.random.normal(0, 0.1, 1)
        coeffs_a = best_coeffs + deltas
        coeffs_b = best_coeffs - deltas

        # S'assurer que les coefficients restent positifs
        coeffs_a[0] = max(coeffs_a[0], 0)
        coeffs_b[0] = max(coeffs_b[0], 0)

        results = match(nb_games, grid_size, coeffs_a[0], coeffs_b[0])

        if results[0] > 0.6 * nb_games:  # coeffs_a ont gagné
            best_coeffs = best_coeffs + (coeffs_a - best_coeffs) * factor
        elif results[0] < 0.4 * nb_games:
            best_coeffs = best_coeffs + (coeffs_b - best_coeffs) * factor

        list_best_coeff.append(best_coeffs[0])
        print(best_coeffs)

        if count % 2 == 0:
            plt.plot(list_best_coeff)
            plt.xlabel("Iteration")
            plt.ylabel("Best Coefficient")
            plt.title("Tuning Coefficient Over Time")
            plt.show()

        count += 1


def main():
    dodo(4, 1, "random", 2, 1, "anti-decisive", 2)
    # tab = []
    # for _ in range(1):
    #     tab.append(dodo(4, 1, 1))
    # print(tab.count(1), tab.count(-1))
    # plt.plot(sum_lists(tab))
    # plt.show()

    # v = []
    # for f in [10., 2.0, 3.5, 4.0, 5.0]:
    #     v.append(match(100, 4, 1, 1, f, 1, 1, 1)[0])
    # plt.plot(v)
    # plt.show()


if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()
    main()
    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats("tottime")
    stats.print_stats()
