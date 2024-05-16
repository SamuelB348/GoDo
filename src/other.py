import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
from hex_tools import *


def print_percentage_bar(percentage1, percentage2, sample_size):
    total_length = 100

    green_length = int(total_length * percentage1)
    red_length = int(total_length * percentage2)

    green_part = "=" * green_length
    red_part = "=" * red_length

    # Affichage de la barre de pourcentage avec les couleurs appropriées
    print(
        "\033[32m"
        + green_part
        + "\033[0m"
        + "|"
        + "\033[31m"
        + red_part
        + "\033[0m"
        + f" {percentage1*sample_size:.0f} vs {percentage2*sample_size:.0f}"
    )


def grid_heatmap_plot(heatmap: dict[Cell, float], hex_size: int):
    plt.figure(figsize=(10, 10))
    layout = Layout(layout_flat, Point(1, -1), Point(0, 0))

    min_count = min(heatmap.values())
    max_count = max(heatmap.values())

    norm = Normalize(vmin=min_count, vmax=max_count)
    cmap = plt.get_cmap('viridis')
    scalar_map = ScalarMappable(norm=norm, cmap=cmap)

    for box, count in heatmap.items():
        corners = polygon_corners(layout, box)
        center = hex_to_pixel(layout, box)

        # Contours de chaque hexagone
        list_edges_x = [corner.x for corner in corners]
        list_edges_y = [corner.y for corner in corners]
        list_edges_x.append(list_edges_x[0])
        list_edges_y.append(list_edges_y[0])

        color = scalar_map.to_rgba(count)

        polygon = Polygon(
            corners,
            closed=True,
            edgecolor="k",
            facecolor=color,
            alpha=0.8,
            linewidth=2,
        )

        plt.gca().add_patch(polygon)
        # plt.text(
        #     center.x,
        #     center.y,
        #     f"{count:.2f}",
        #     horizontalalignment="right",
        # )
    plt.xlim(-2 * hex_size-1, 2 * hex_size+1)
    plt.ylim(-2 * hex_size-1, 2 * hex_size+1)
    plt.show()


# def generate_random_games(board: Engine, player: Player, n: int):
#     count = 0
#     for i in range(n):
#         board_tmp: Engine = deepcopy(board)
#         current_player = player
#         while True:
#             s = strategy_random(board_tmp, current_player)
#             board_tmp.play(current_player, s)
#             if current_player == R:
#                 current_player = B
#             else:
#                 current_player = R
#
#             if current_player == B and board_tmp.is_final(B):  # blue wins
#                 if player == B:
#                     count += 1
#                 break
#             if current_player == R and board_tmp.is_final(R):  # red wins
#                 if player == R:
#                     count += 1
#                 break
#     return count
#
#
# def count_nb_moves(size: int, nb_games: int):
#     list_moves: list[int] = []
#     for i in range(nb_games):
#         count: int = 0
#         board_tmp: Engine = initialize("dodo", start_board(4), R, 4, 100)
#         while True:
#             s = strategy_random(board_tmp, R)
#             board_tmp.play(R, s)
#             count += 1
#             if board_tmp.is_final(B):
#                 list_moves.append(count)
#                 break
#             s = strategy_random(board_tmp, B)
#             board_tmp.play(B, s)
#             count += 1
#             if board_tmp.is_final(R):
#                 list_moves.append(count)
#                 break
#     return list_moves
#
#
# def nb_moves_left(size: int, nb_games: int):
#     nb_moves: list[list[int]] = []
#     for i in range(nb_games):
#         list_tmp = []
#         board_tmp: Engine = initialize("dodo", start_board(4), R, 4, 100)
#         while True:
#             s = strategy_random(board_tmp, R)
#             list_tmp.append(len(list(board_tmp.legals(R))))
#             board_tmp.play(R, s)
#             if board_tmp.is_final(B):
#                 nb_moves.append(list_tmp)
#                 break
#             s = strategy_random(board_tmp, B)
#             list_tmp.append(len(list(board_tmp.legals(B))))
#             board_tmp.play(B, s)
#             if board_tmp.is_final(R):
#                 nb_moves.append(list_tmp)
#                 break
#     return nb_moves
#
#
# def sum_lists(list_of_lists):
#     max_length = max(len(lst) for lst in list_of_lists)  # Trouve la longueur maximale parmi toutes les listes
#     new_lsts = [lst + [0] * max(0, max_length - len(lst)) for lst in list_of_lists]
#     summed_list = []
#     for i in range(max_length):
#         count = 0
#         nb = 0
#         for lst in new_lsts:
#             if lst[i] != 0:
#                 count += lst[i]
#                 nb += 1
#         summed_list.append(count/nb)
#     return summed_list

#     self.grid_weights_R[el] = 0
#     self.grid_weights_B[el] = 0
#
# victory_count_r: int = 0
# victory_count_b: int = 0
#
# for _ in range(nb_games):
#     while True:
#         act: ActionDodo = random.choice(self.legals(R))
#         self.play(R, act)
#         if self.is_final(B):
#             victory_count_b += 1
#             self.add_dicts(self.grid_weights_B, self.grid, B)
#             self.back_to_start_board()
#             break
#         act = random.choice(self.legals(B))
#         self.play(B, act)
#         if self.is_final(R):
#             victory_count_r += 1
#             self.add_dicts(self.grid_weights_R, self.grid, R)
#             self.back_to_start_board()
#             break
#
# for el in self.grid_weights_R:
#     self.grid_weights_R[el] /= victory_count_r
#     self.grid_weights_B[el] /= victory_count_b
