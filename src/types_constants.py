from typing import Union
from hex_tools import Cell


# -------------------- Communication avec l'arbitre -------------------- #

ActionGopher = Cell
ActionDodo = tuple[Cell, Cell]
Action = Union[ActionGopher, ActionDodo]
Player = int
R = 1
B = 2
State = list[tuple[Cell, Player]]
Score = int
Time = int

# -------------------- Autres alias de types et constantes -------------------- #

Grid = dict[Cell, Player]
CellSet = set[Cell]
Neighbors = dict[Cell, list[Cell]]
