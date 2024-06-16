import random
from types_constants import State, CellSet, Neighbors, ZKey, R, B
from hex_tools import neighbor


class BoardUtils:
    """
    Class containing some utilities to manipulate efficiently the board, including :

    - Pre-computed cells of the board
    - Pre-computed neighbors of all the cells (from the red's pov and the blue's pov for Dodo, and everyone's pov
      for Gopher)
    - The Zobrist hash keys of all the cells (and the hash for the turn)
    - A method to convert a state from the referee into a dictionary for a faster implementation

    """

    def __init__(self, hex_size: int, state: State):
        """
        Constructor of the BoardUtils class

        :param hex_size: the size of the board (the length of the board sides, in cells)
        :param state: a state from which we will compute utilities
        """

        self.size = hex_size
        self.cells = self.generate_cells(self.size)
        self.r_pov_neighbors = self.generate_neighbors([1, 2, 3])
        self.b_pov_neighbors = self.generate_neighbors([0, 4, 5])
        self.neighbors = self.generate_neighbors([0, 1, 2, 3, 4, 5])
        self.cell_keys, self.turn_key = self.generate_zobrist_keys()
        self.start_hash = self.compute_start_hash(state)

    @staticmethod
    def generate_cells(hex_size: int) -> CellSet:
        """

        :param hex_size: the size of the board (the length of the board sides, in cells)
        :return: a set of all the cells of the board, under the form of coordinates (ex: {(0,0), (-1,3), ...})
        """

        cells = set()
        n = hex_size - 1
        for r in range(n, -n - 1, -1):
            q1 = max(-n, r - n)
            q2 = min(n, r + n)
            for q in range(q1, q2 + 1):
                cells.add((q, r))
        return cells

    def generate_neighbors(self, directions: list[int]) -> Neighbors:
        """

        :param directions: a list of directions for which we want to compute the neighbors
        :return: a dictionary with keys being the different cells on the board, and the values being a list of all the
        neighbors towards the different directions
        """

        return {
            cell: [
                neighbor(cell, i) for i in directions if neighbor(cell, i) in self.cells
            ]
            for cell in self.cells
        }

    def generate_zobrist_keys(self):
        """

        :return: a tuple composed of :
        - a dictionary with the cells as the keys and the Zobrist hash keys of the cells as the
          values (one cell has two hash keys, on for the red and one for the blue)
        - a unique zobrist hash representing whose turn it is
        """

        cell_keys = {}
        used_keys = set()

        def generate_unique_key():
            """

            :return: a unique random number, different from all the already chosen hash keys
            """

            key = random.getrandbits(64)
            while key in used_keys:
                key = random.getrandbits(64)
            used_keys.add(key)
            return key

        for cell in self.cells:
            key_r = generate_unique_key()
            key_b = generate_unique_key()
            cell_keys[cell] = ZKey(key_r, key_b)

        return cell_keys, generate_unique_key()

    def compute_start_hash(self, state: State):
        """
        Given a state, it computes the starting Zobrist hash, which will be used later when we play a move or so.

        :param state: a state of the board
        :return: a Zobrist hash representing the current state of the board (a big integer)
        """

        start_hash = 0
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

        grid = {}
        n = self.size - 1
        for r in range(n, -n - 1, -1):
            q1 = max(-n, r - n)
            q2 = min(n, r + n)
            for q in range(q1, q2 + 1):
                if ((q, r), R) in state:
                    grid[(q, r)] = R
                elif ((q, r), B) in state:
                    grid[(q, r)] = B
                else:
                    grid[(q, r)] = 0
        return grid
