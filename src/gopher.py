from __future__ import annotations

import random
from collections import deque
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

from types_constants import *
from hex_tools import *


class GameStateGopher:
    def __init__(
        self,
        grid: Grid,
        player: Player,
        hex_size: int,
        cells: CellSet,
        r_neighbors: Neighbors,
        b_neighbors: Neighbors,
    ):
        # -------------------- Attributs généraux -------------------- #

        self.turn: Player = player
        self.opponent: Player = R if player == B else B
        self.size: int = hex_size

        # -------------------- Autres -------------------- #

        self.legals: list[ActionGopher] = self.generate_legal_actions(self.player)

    def generate_legal_actions(self, player: Player) -> list[ActionGopher]:
        legals: list[ActionGopher] = []
        if player == R:
            for box in self.Empty_hex:
                nb_neighbors = 0
                info_rouge = False
                for i in [0, 1, 2, 3, 4, 5]:
                    if neighbor(box, i) in self.grid and self.grid[neighbor(box, i)] == R:
                        info_rouge = True
                        break
                    elif (
                            neighbor(box, i) in self.grid
                            and self.grid[neighbor(box, i)] == B
                    ):
                        nb_neighbors += 1
                if self.empty_grid(grid):
                    legals.append(box)
                elif 0 < nb_neighbors < 2 and not info_rouge:
                    legals.append(box)
        elif player == B:
            for box in self.Empty_hex:
                nb_neighbors = 0
                info_bleu = False
                for i in [0, 1, 2, 3, 4, 5]:
                    if neighbor(box, i) in self.grid and self.grid[neighbor(box, i)] == B:
                        info_bleu = True
                        break
                    elif (
                            neighbor(box, i) in self.grid
                            and self.grid[neighbor(box, i)] == R
                    ):
                        nb_neighbors += 1
                if 0 < nb_neighbors < 2 and not info_bleu:
                    legals.append(box)
        return legals

    def get_legal_actions(self) -> list[ActionGopher]:
        return self.legals

    def is_game_over(self) -> bool:
        return len(self.legals) == 0

    def game_result(self) -> Player:
        assert self.is_game_over()
        return self.turn

    def move(self, action: ActionDodo) -> GameStateDodo:
        pass

    def simulate_game(self) -> tuple[Player, int]: ##Je termine après
        tmp_grid = self.grid.copy()
        tmp_r_cells = self.R_CELLS.copy()
        tmp_b_cells = self.B_CELLS.copy()
        game_length = 0

        while True:
            legals: list[ActionGopher] = self.generate_legal_actions(self.turn)
            if len(legals) == 0:
                winner = self.turn
                break
            if p:
                move = random.choice(
                    self.alphabeta_actions_v1(
                        1, self.turn, float("-inf"), float("inf"), legals
                    )[1]
                )
            else:
                move: ActionGopher = random.choice(legals)
            self.play(move, self.turn)
            game_length += 1

            legals = self.generate_legal_actions(self.opponent)
            if len(legals) == 0:
                winner = self.opponent
                break
            if p:
                move = random.choice(
                    self.alphabeta_actions_v1(
                        1, self.opponent, float("-inf"), float("inf"), legals
                    )[1]
                )
            else:
                move: ActionDodo = random.choice(legals)
            self.play(move, self.opponent)
            game_length += 1

        self.grid = tmp_grid
        self.R_CELLS = tmp_r_cells
        self.B_CELLS = tmp_b_cells

        return winner, game_length

    def play(self, action, player) -> None:
        self.grid[action] = player
        self.update_sets(player, action) ##Pas sur que la fonction existe ducoup

    def undo_stack(self) -> None:
        pass

    def pplot(self) -> None:
        """
        Produit un affichage graphique de la grille de jeu actuelle.
        """

        plt.figure(figsize=(10, 10))
        layout = Layout(layout_pointy, Point(1, -1), Point(0, 0))

        for box, color in self.grid.items():
            corners = polygon_corners(layout, box)
            center = hex_to_pixel(layout, box)

            # Contours de chaque hexagone
            list_edges_x = [corner.x for corner in corners]
            list_edges_y = [corner.y for corner in corners]
            list_edges_x.append(list_edges_x[0])
            list_edges_y.append(list_edges_y[0])
            if color == 1:
                polygon = Polygon(
                    corners,
                    closed=True,
                    edgecolor="k",
                    facecolor="red",
                    alpha=0.8,
                    linewidth=2,
                )
            elif color == 2:
                polygon = Polygon(
                    corners,
                    closed=True,
                    edgecolor="k",
                    facecolor="blue",
                    alpha=0.8,
                    linewidth=2,
                )
            else:
                polygon = Polygon(
                    corners,
                    closed=True,
                    edgecolor="k",
                    facecolor="none",
                    alpha=0.8,
                    linewidth=2,
                )
            plt.gca().add_patch(polygon)
            plt.text(
                center.x,
                center.y,
                f"{box.q}, {box.r}",
                horizontalalignment="right",
            )
        plt.xlim(-2 * self.size - 1, 2 * self.size + 1)
        plt.ylim(-2 * self.size - 1, 2 * self.size + 1)
        plt.show()
