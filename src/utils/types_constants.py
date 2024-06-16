from typing import Union
from collections import namedtuple


# -------------------- Communication avec l'arbitre -------------------- #

Cell = tuple[int, int]
ActionGopher = Cell
ActionDodo = tuple[Cell, Cell]
Action = Union[ActionGopher, ActionDodo]
Player = int
State = list[tuple[Cell, Player]]
Score = int
Time = int

# -------------------- Autres alias de types et constantes -------------------- #

R: Player = 1
B: Player = 2
Grid = dict[Cell, Player]
CellSet = set[Cell]
Neighbors = dict[Cell, list[Cell]]
ZKey = namedtuple("ZKey", ["R", "B"])
