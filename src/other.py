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
