from django.conf import settings
from dataclasses import dataclass
from typing import Literal


@dataclass
class Direction:
    row: Literal["+", ""] = ""
    col: Literal["+", "-", ""] = ""

    def is_valid(self, row: int, col: int):
        return not (self.col == "+" and col + 4 > settings.CONNECT_FOUR_COLUMNS) and \
               not (self.row == "+" and row + 4 > settings.CONNECT_FOUR_ROWS) and \
               not (self.col == "-" and col < 3)

    def next(self, row: int, col: int, i: int):
        if self.row == "+":
            row = row + i
        if self.col == "+":
            col = col + i
        if self.col == "-":
            col = col - i
        return row, col

    def connect_four(self, coordinate: (int, int), coins):
        if not self.is_valid(*coordinate):
            return False
        player = coins.get(coordinate)
        for i in range(1, 4):
            next_player = coins.get(self.next(*coordinate, i))
            if next_player != player:
                return False
        return True
