from typing import Union
from collections import namedtuple
from hex_tools import Cell


# -------------------- Communication avec l'arbitre -------------------- #

ActionGopher = Cell
ActionDodo = tuple[Cell, Cell]
Action = Union[ActionGopher, ActionDodo]
Player = int
State = list[tuple[Cell, Player]]
Score = int
Time = int

# -------------------- Autres alias de types et constantes -------------------- #

R = 1
B = 2
Grid = dict[Cell, Player]
CellSet = set[Cell]
Neighbors = dict[Cell, list[Cell]]
zkey = namedtuple("zkey", ["R", "B"])