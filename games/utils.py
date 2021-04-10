from django.conf import settings
from dataclasses import dataclass


@dataclass
class Direction:
    row: str = ""
    col: str = ""

    def is_valid(self, row: int, col: int):
        return not (self.col == "+" and col + 4 > settings.CONNECT_FOUR_COLUMNS) and \
               not (self.row == "+" and row + 4 > settings.CONNECT_FOUR_ROWS) and \
               not (self.col == "-" and col < 3)

    def next(self, row: int, col: int, i: int):
        if self.row == "+":
            row = row + i
        if self.row == "-":
            row = row - i
        if self.col == "+":
            col = col + i
        if self.col == "-":
            col = col - i
        return row, col
