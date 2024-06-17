"""
This section implements a class that contains hexagonal board utilities.
"""

import random
from types_constants import Cell, State, Grid, CellSet, Neighbors, ZKey, R, B
from hex_tools import neighbor


class BoardUtils:
    """
    Class containing some utilities to manipulate efficiently the board, including :

    - Pre-computed cells of the board
    - Pre-computed neighbors of all the cells (from the red's pov and the blue's pov for Dodo,
      and everyone's pov for Gopher)
    - The Zobrist hash keys of all the cells (and the hash for the turn)
    - A method to convert a state from the referee into a dictionary for a faster implementation
    """

    def __init__(self, hex_size: int, state: State):
        self.size: int = hex_size
        self.cells: CellSet = self.generate_cells(self.size)

        self.r_pov_neighbors: Neighbors = self.generate_neighbors([1, 2, 3])
        self.b_pov_neighbors: Neighbors = self.generate_neighbors([0, 4, 5])
        self.neighbors: Neighbors = self.generate_neighbors([0, 1, 2, 3, 4, 5])

        self.cell_keys: dict[Cell, ZKey]
        self.turn_key: int
        self.cell_keys, self.turn_key = self.generate_zobrist_keys()
        self.start_hash: int = self.compute_start_hash(state)

    @staticmethod
    def generate_cells(hex_size: int) -> CellSet:
        """
        Generate all the cells of the board of a given size.

        :param hex_size: the size of the board (the length of the board sides, in cells)
        :return: a set of all the cells of the board, as coordinates (ex: {(0,0), (-1,3), ...})
        """

        cells: set[Cell] = set()
        n: int = hex_size - 1

        for r in range(n, -n - 1, -1):
            q1: int = max(-n, r - n)
            q2: int = min(n, r + n)
            for q in range(q1, q2 + 1):
                cells.add((q, r))

        return cells

    def generate_neighbors(self, directions: list[int]) -> Neighbors:
        """
        Generate all the neighbors towards the given directions, for all the cells on the board.

        :param directions: a list of directions for which we want to compute the neighbors
        :return: a dictionary {cell: list of all the neighbors towards the different directions}
        """

        return {
            cell: [
                neighbor(cell, i) for i in directions if neighbor(cell, i) in self.cells
            ]
            for cell in self.cells
        }

    def generate_zobrist_keys(self) -> tuple[dict[Cell, ZKey], int]:
        """
        Generate all the different zobrist keys for all the cells, for all the players,
        as well as the key representing whose turn it is.

        :return: a tuple composed of a dictionary {cell: zobrist keys}, and a unique turn key
        """

        cell_keys: dict[Cell, ZKey] = {}
        used_keys: set[int] = set()

        def generate_unique_key() -> int:
            """

            :return: a unique random number, different from all the already chosen hash keys
            """

            key: int = random.getrandbits(64)
            while key in used_keys:
                key = random.getrandbits(64)
            used_keys.add(key)
            return key

        for cell in self.cells:
            key_r: int = generate_unique_key()
            key_b: int = generate_unique_key()
            cell_keys[cell] = ZKey(key_r, key_b)

        return cell_keys, generate_unique_key()

    def compute_start_hash(self, state: State) -> int:
        """
        Computes the starting Zobrist hash of a given state,
        which will be used later when we play a move or so.

        :param state: a state of the board
        :return: a Zobrist hash representing the current state of the board (a big integer)
        """

        start_hash: int = 0

        for cell, player in state:
            if player == R:
                start_hash ^= self.cell_keys[cell].R
            else:
                start_hash ^= self.cell_keys[cell].B

        return start_hash

    def state_to_dict(self, state: State):
        """
        Convert a state in the form of a list[(cell, player)] into a dictionary dict[cell: player].

        :param state: the state we want to convert
        :return: a dictionary equivalent to the original state
        """

        grid: Grid = {}
        n: int = self.size - 1

        for r in range(n, -n - 1, -1):
            q1: int = max(-n, r - n)
            q2: int = min(n, r + n)
            for q in range(q1, q2 + 1):
                if ((q, r), R) in state:
                    grid[(q, r)] = R
                elif ((q, r), B) in state:
                    grid[(q, r)] = B
                else:
                    grid[(q, r)] = 0

        return grid
