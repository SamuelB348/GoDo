import random
from functools import cached_property
from math import exp, log
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from hex_tools import *


# ------------- Alias de types et constantes pour communiquer avec l'arbitre ------------- #

ActionDodo = tuple[Cell, Cell]
Player = int
R = 1
B = 2
State = list[tuple[Cell, Player]]
Score = int
Evaluation = float
Time = int


# -------------------------- Autres alias de types et constantes ------------------------- #

Grid = dict[Cell, Player]
CheckerSet = set[Cell]
Neighbors = dict[Cell, list[Cell]]
GridWeights = dict[Cell, float]
Hash = int
Cache = dict[tuple[Hash, Player], Evaluation]
Depth = int


class EngineDodo:
    """
    Environnement de jeu principal, qui contient tous les algorithmes, méthodes,
    structures, cache, etc. pour faire fonctionner l'IA.
    """

    def __init__(self, grid: State, hex_size: int, time: Time):

        # Attributs généraux
        self.size: int = hex_size
        self.time: Time = time

        # Structures de données
        self.grid: Grid = dict(grid)
        self.R_cell: CheckerSet = {
            cell for cell, player in self.grid.items() if player == R
        }
        self.B_cell: CheckerSet = {
            cell for cell, player in self.grid.items() if player == B
        }
        self.R_neighbors: Neighbors = {
            cell: [neighbor(cell, i) for i in [1, 2, 3] if neighbor(cell, i) in self.grid] for cell in self.grid
        }
        self.B_neighbors: Neighbors = {
            cell: [neighbor(cell, i) for i in [0, 4, 5] if neighbor(cell, i) in self.grid] for cell in self.grid
        }

        # Attributs pour la fonction d'évaluation
        self.grid_weights_R: GridWeights = self.generate_grid_heatmaps(R)
        self.grid_weights_B: GridWeights = self.generate_grid_heatmaps(B)

        # Attributs pour les caches
        self.cache: Cache = {}
        self.sorted_keys = {key: tuple(sorted(key)) for key in self.grid}

        # Attributs pour le debug
        self.position_explored: int = 0
        self.terminal_node: int = 0
        self.state_stack: list[Grid] = []

    @cached_property
    def nb_checkers(self) -> int:
        """
        Le nombre de pions est constant le long de la partie (pas de prises)
        mais dépend de la taille de la grille.
        Par conséquent, il n'a besoin d'être calculé qu'une fois (→ cached_property)
        et sera utilisé le reste du temps comme un attribut normal.

        :return: Le nombre de pions possédés par chaque joueur
        """

        return ((self.size + 1) * self.size) // 2 + (self.size - 1)

    @staticmethod
    def symetrical(dico):
        """
        Le symétrique d'un état du jeu correspond au dictionnaire où la clé key de type Cell
        reçoit les valeurs de la clé (key[1], key[0]).

        :param dico: Un dictionnaire de type Grid, qui représente un état de jeu.
        :return: Le dictionnaire symétrique de type Grid.
        """

        sym = []
        for cell in dico:
            sym.append((cell, dico[(cell[1], cell[0])]))
        return tuple(sym)

    def grid_hash(self) -> Hash:
        """

        :return: Le hash (censé être invariant aux symmétries) de self.grid.
        """

        hash_list: list[tuple[Cell, tuple[Player, Player]]] = [
            (key, (self.grid[key], self.grid[(key[1], key[0])]))
            for key in self.sorted_keys
        ]
        return hash(tuple(hash_list))

    def generate_grid_heatmaps(self, player: Player) -> GridWeights:
        """
        Calcule, pour chaque case de la grille, le nombre minimal de case à traverser
        pour atteindre la case la plus éloignée de la grille du point de vue de 'player'.

        :param player: Un joueur (R ou B).
        :return: La grille des poids associés à chaque case.
        """

        grid_weights: GridWeights = {}
        for cell in self.grid:
            if player == R:
                grid_weights[cell] = 1 - (
                    max(abs(cell[0] - (self.size - 1)), abs(cell[1] - (self.size - 1)))
                    / (2 * (self.size - 1))
                )
            else:
                grid_weights[cell] = 1 - (
                    max(abs(cell[0] + (self.size - 1)), abs(cell[1] + (self.size - 1)))
                    / (2 * (self.size - 1))
                )
        return grid_weights

    def update_state(self, state: State) -> None:
        """
        Remet à jour self.grid et les sets R_cell et B_cell quand on reçoit
        un nouveau "state" de l'arbitre.

        :param state: Un 'state' de type State reçu de l'arbitre.
        :return: None
        """

        self.grid = dict(state)
        self.R_cell = {hex_key for hex_key, player in self.grid.items() if player == R}
        self.B_cell = {hex_key for hex_key, player in self.grid.items() if player == B}

    def legals(self, player: Player) -> list[ActionDodo]:
        """
        Retourne les coups légaux du joueur en paramètre. La méthode s'appuie sur les sets R_cell ou B_cell
        pour itérer uniquement usr les cases du joueur.

        :param player: Le joueur dont on calcule les coups légaux.
        :return: Une liste de coups légaux (de type ActionDodo : tuple[Cell, Cell])
        """

        legals: list[ActionDodo] = []
        if player == R:
            for cell in self.R_cell:
                for nghb in self.R_neighbors[cell]:
                    if self.grid[nghb] == 0:
                        legals.append((cell, nghb))
        elif player == B:
            for cell in self.B_cell:
                for nghb in self.B_neighbors[cell]:
                    if self.grid[nghb] == 0:
                        legals.append((cell, nghb))

        return legals

    def is_final(self, player: Player) -> bool:
        """
        Méthode pour savoir si le joueur 'player' a gagné.

        :param player: Un joueur (R ou B).
        :return: Un booléen ("a gagné" ou "n'a pas gagné").
        """

        return len(self.legals(player)) == 0

    def play(self, player: Player, action: ActionDodo) -> None:
        """
        Joue une action légale et modifie les attributs grid, R_cell et B_cell.

        :param player: Le joueur qui joue l'action.
        :param action: L'action de type ActionDodo qui est jouée.
        :return: None
        """

        self.grid[action[0]] = 0
        self.grid[action[1]] = player
        self.update_sets(player, action)

    def undo(self, player: Player, action: ActionDodo) -> None:
        """
        Inverse de la méthode play.

        :param player: Le joueur qui 'déjoue' l'action.
        :param action: L'action de type ActionDodo qui est 'déjouée'.
        """

        self.grid[action[0]] = player
        self.grid[action[1]] = 0
        self.reverse_update_sets(player, action)

    def update_sets(self, player: Player, action: ActionDodo) -> None:
        """
        Met à jour les sets R_cell et B_cell après une action.

        :param player: Le joueur qui joue l'action.
        :param action: L'action de type ActionDodo qui est jouée.
        """

        if player == R:
            self.R_cell.discard(action[0])
            self.R_cell.add(action[1])
        else:
            self.B_cell.discard(action[0])
            self.B_cell.add(action[1])

    def reverse_update_sets(self, player: Player, action: ActionDodo) -> None:
        """
        Met à jour les sets R_cell et B_cell après un 'undo'.

        :param player: Le joueur qui 'déjoue' l'action.
        :param action: L'action de type ActionDodo qui est 'déjouée'.
        """

        if player == R:
            self.R_cell.discard(action[1])
            self.R_cell.add(action[0])
        else:
            self.B_cell.remove(action[1])
            self.B_cell.add(action[0])

    def neighbors(self, cell: Cell, player: Player) -> dict[Cell, Player]:
        """
        Calcule l'ensemble des voisins (existants) d'une case selon la perspective du joueur 'player', ainsi
        que les joueurs qui sont présents sur ces cases.

        :param cell: La case dont on veut connaître les voisins.
        :param player: La perspective selon laquelle on veut connaître les voisins (celle de R ou B)
        :return: Un dictionnaire contenant les voisins de la case et les joueurs qui sont dessus.
        """

        neighbors: dict[Cell, Player] = {}
        if player == R:
            neighbors = {nghb: self.grid[nghb] for nghb in self.R_neighbors[cell]}
        if player == B:
            neighbors = {nghb: self.grid[nghb] for nghb in self.B_neighbors[cell]}
        return neighbors

    def nb_pins(self, player: Player) -> int:
        """
        Retourne le nombre de fois où 'player' est bloqué c.-à-d. qu'il ne peut pas bouger,
        sauf si un jeton voisin appartenant au joueur adverse bouge.

        :param player: Un joueur (R ou B).
        :return: Nombre de blocages ('pins') du joueur.
        """

        count: int = 0
        opponent = R if player == B else B
        for cell in self.R_cell if player == R else self.B_cell:
            neighbors = self.neighbors(cell, player)
            if all(
                neighbors.values()
            ):  # Si toutes les cases voisines sont occupées (c.-à-d. != 0)
                for nghb in neighbors:
                    if (
                        neighbors[nghb] == opponent
                        and 0 in self.neighbors(nghb, opponent).values()
                    ):
                        count += 1
        return count

    def calculate_metrics(
        self,
    ) -> tuple[list[ActionDodo], float, float, list[ActionDodo], float, float]:

        legals_r: list[ActionDodo] = []
        pins_r: float = 0.0
        position_r: float = 0.0

        legals_b: list[ActionDodo] = []
        pins_b: float = 0.0
        position_b: float = 0.0

        for cell in self.R_cell:
            position_r += self.grid_weights_R[cell]
            for nghb in self.R_neighbors[cell]:
                if self.grid[nghb] == 0:
                    legals_r.append((cell, nghb))
                elif self.grid[nghb] == B and 0 in [
                    self.grid[nghb_B] for nghb_B in self.B_neighbors[nghb]
                ]:
                    pins_r += 1

        for cell in self.B_cell:
            position_b += self.grid_weights_B[cell]
            for nghb in self.B_neighbors[cell]:
                if self.grid[nghb] == 0:
                    legals_b.append((cell, nghb))
                elif self.grid[nghb] == R and 0 in [
                    self.grid[nghb_R] for nghb_R in self.R_neighbors[nghb]
                ]:
                    pins_b += 1

        return legals_r, pins_r, position_r, legals_b, pins_b, position_b

    def evaluate_v1(
        self, player: Player, m: float = 0, p: float = 0, c: float = 0
    ) -> Evaluation:

        # state = tuple(self.grid.items())
        state: Hash = self.grid_hash()
        if (state, player) in self.cache:
            return self.cache[(state, player)]

        legals_r, pins_r, position_r, legals_b, pins_b, position_b = (
            self.calculate_metrics()
        )

        nb_moves_r: int = len(legals_r)
        nb_moves_b: int = len(legals_b)

        # Si un des deux joueurs gagne
        if player == R and nb_moves_r == 0:
            self.cache[(state, player)] = 10000
            return 10000
        if player == B and nb_moves_b == 0:
            self.cache[(state, player)] = -10000
            return -10000

        # Si un des deux joueurs gagne au prochain coup de manière certaine
        if player == R and nb_moves_b == 0 and pins_b == 0:
            self.cache[(state, player)] = -10000
            return -10000
        if player == B and nb_moves_r == 0 and pins_r == 0:
            self.cache[(state, player)] = 10000
            return 10000

        # Facteur "mobilité"
        mobility = (nb_moves_r - nb_moves_b) / (3 * self.nb_checkers)
        # Facteur "position"
        position: float = (position_r - position_b) / self.nb_checkers
        # Facteur "contrôle"
        control = (pins_r - pins_b) / self.nb_checkers

        # Combinaison linéaire des différents facteurs
        evaluation = m * mobility + p * position + c * control

        # Mise en cache
        self.cache[(state, player)] = evaluation

        return evaluation

    @staticmethod
    def adaptable_depth_v1(
        x: int, upper_bound: int, lower_bound: int, inflexion_point: int
    ) -> Depth:
        d = upper_bound - (
            (upper_bound - lower_bound) / (1 + exp(-(x - inflexion_point)))
        )
        return round(d)

    @staticmethod
    def adaptable_depth_v2(x: int, y: int, bound: int, max_depth: Depth) -> Depth:
        if y in (0, 1):
            d = log(bound) / (log(x) * log(2)) + 2
        else:
            d = log(bound) / (log(x) * log(y)) + 2
        return min(round(d), max_depth)

    def simulate_random_games(
        self, state: State, player: Player, nb_games: int
    ) -> float:
        nb_victory: int = 0
        opponent: Player = B if player == B else R
        for _ in range(nb_games):
            while True:
                legals_opp = self.legals(opponent)
                if len(legals_opp) == 0:
                    break
                act: ActionDodo = random.choice(legals_opp)
                self.play(opponent, act)

                legals_p = self.legals(player)
                if len(legals_p) == 0:
                    nb_victory += 1
                    break
                act = random.choice(legals_p)
                self.play(player, act)
            self.update_state(state)

        return nb_victory / nb_games

    def order_moves(
        self, state: State, legals: list[ActionDodo], player: Player, nb_games: int
    ):
        ordered_moves: dict[ActionDodo, float] = {}

        for move in legals:
            self.play(player, move)
            score = self.simulate_random_games(state, player, nb_games)
            if score >= 0.9:
                return {move: 0.9}
            ordered_moves[move] = score
        ordered_moves = dict(
            sorted(ordered_moves.items(), key=lambda item: item[1], reverse=True)
        )
        # self.pplot()
        # print(ordered_moves)
        return ordered_moves

    def alphabeta_v1(
        self,
        depth: int,
        a: float,
        b: float,
        player: Player,
        m: float,
        p: float,
        c: float,
    ) -> float:
        """
        Minmax avec élagage alpha-beta.
        """

        if depth == 0 or self.is_final(player):
            self.terminal_node += 1
            return self.evaluate_v1(player, m, p, c)

        self.position_explored += 1
        if player == R:
            best_value = float("-inf")

            for legal in self.legals(player):
                self.play(player, legal)
                best_value = max(
                    best_value, self.alphabeta_v1(depth - 1, a, b, B, m, p, c)
                )
                self.undo(player, legal)
                a = max(a, best_value)
                if a >= b:
                    break  # β cut-off

            return best_value
        else:
            best_value = float("inf")

            for legal in self.legals(player):
                self.play(player, legal)
                best_value = min(
                    best_value, self.alphabeta_v1(depth - 1, a, b, R, m, p, c)
                )
                self.undo(player, legal)
                b = min(b, best_value)
                if a >= b:
                    break  # α cut-off

            return best_value

    def alphabeta_actions_v1(
        self,
        state: State,
        player: Player,
        depth: int,
        a: float,
        b: float,
        legals: list[ActionDodo],
        m: float,
        p: float,
        c: float,
    ) -> tuple[float, list[ActionDodo]]:
        """
        Minmax avec élagage alpha-beta et choix d'une action.
        """

        if depth == 0 or len(legals) == 0:
            return self.evaluate_v1(player, m, p, c), []

        if player == R:
            best_value = float("-inf")
            best_legals: list[ActionDodo] = []
            if len(legals) == 1:
                self.terminal_node = 0
                self.position_explored = 0
                return best_value, legals

            for legal in legals:
                self.play(player, legal)
                v = self.alphabeta_v1(depth - 1, a, b, B, m, p, c)
                self.undo(player, legal)
                if v > best_value:
                    best_value = v
                    best_legals = [legal]
                elif v == best_value:
                    best_legals.append(legal)
                a = max(a, best_value)

            self.terminal_node = 0
            self.position_explored = 0

            return best_value, best_legals
        else:  # minimizing player
            best_value = float("inf")
            best_legals = []
            if len(legals) == 1:
                return best_value, legals

            for legal in legals:
                self.play(player, legal)
                v = self.alphabeta_v1(depth - 1, a, b, R, m, p, c)
                self.undo(player, legal)
                if v < best_value:
                    best_value = v
                    best_legals = [legal]
                elif v == best_value:
                    best_legals.append(legal)
                b = min(b, best_value)

            self.terminal_node = 0
            self.position_explored = 0

            return best_value, best_legals

    def pplot(self, grid):
        """
        Produit un affichage graphique de la grille de jeu actuelle.
        """

        plt.figure(figsize=(10, 10))
        layout = Layout(layout_flat, Point(1, -1), Point(0, 0))

        for box, player in grid.items():
            corners = polygon_corners(layout, box)
            center = hex_to_pixel(layout, box)

            # Contours de chaque hexagone
            list_edges_x = [corner.x for corner in corners]
            list_edges_y = [corner.y for corner in corners]
            list_edges_x.append(list_edges_x[0])
            list_edges_y.append(list_edges_y[0])
            if player == 1:
                color = "red"
            elif player == 2:
                color = "blue"
            else:
                color = "none"

            polygon = Polygon(
                corners,
                closed=True,
                edgecolor="k",
                facecolor=color,
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
