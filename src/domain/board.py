from enum import IntEnum, StrEnum, auto
from typing import TypeAlias

from domain.execptions import AlreadyHitException


class ShipDirection(StrEnum):
    """The four directions a ship can point from its head cell."""

    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()


class CellValue(IntEnum):
    """The possible values stored in one board cell."""

    EMPTY = 0
    SHIP = 1
    HIT = 2
    MISS = 3


BoardPosition: TypeAlias = tuple[int, int]
BoardMatrix: TypeAlias = list[list[CellValue]]


DIRECTION_STEPS: dict[ShipDirection, BoardPosition] = {
    ShipDirection.UP: (-1, 0),
    ShipDirection.DOWN: (1, 0),
    ShipDirection.LEFT: (0, -1),
    ShipDirection.RIGHT: (0, 1),
}


class Board:
    """Stores the cells for one Battleships board."""

    def __init__(self, size: int = 10) -> None:
        if not isinstance(size, int):
            raise TypeError("Board size must be an integer")
        if size <= 0:
            raise ValueError("Board size must be positive")

        self.__size: int = size
        self.__board: BoardMatrix = [
            [CellValue.EMPTY for _column in range(size)]
            for _row in range(size)
        ]

    def get_board_matrix(self) -> BoardMatrix:
        """Return the board cells so the UI can display them."""
        return self.__board

    def place_ship(self, row: int, column: int, direction: ShipDirection | str, ship_length: int) -> None:
        """Place a ship if every cell it needs is inside the board and empty."""
        ship_direction: ShipDirection = ShipDirection(direction)
        ship_cells: list[BoardPosition] = self.get_ship_cells(row, column, ship_direction, ship_length)

        if not self.__can_place_ship(ship_cells):
            raise ValueError("Can't place ship on given position")

        for ship_row, ship_column in ship_cells:
            self.__board[ship_row][ship_column] = CellValue.SHIP

    def get_cell_value(self, row: int, column: int) -> CellValue:
        """Return the value at one board position."""
        if not self.__is_valid_position(row, column):
            raise IndexError("Invalid board coordinates")
        return self.__board[row][column]

    def set_cell_value(self, row: int, column: int, value: CellValue) -> None:
        """Set the value at one board position."""
        if not self.__is_valid_position(row, column):
            raise IndexError("Invalid board coordinates")
        self.__board[row][column] = value

    def try_hit(self, row: int, column: int) -> CellValue:
        """Fire at a board position and return whether it was a hit or miss."""
        if not self.__is_valid_position(row, column):
            raise IndexError("Invalid board coordinates")

        current_cell_value: CellValue = self.__board[row][column]
        if current_cell_value in (CellValue.HIT, CellValue.MISS):
            raise AlreadyHitException

        if current_cell_value == CellValue.SHIP:
            self.__board[row][column] = CellValue.HIT
            return CellValue.HIT

        self.__board[row][column] = CellValue.MISS
        return CellValue.MISS

    def get_ship_cells(
        self,
        start_row: int,
        start_column: int,
        direction: ShipDirection,
        ship_length: int,
    ) -> list[BoardPosition]:
        """Return all cells a ship would occupy from its head position."""
        if ship_length <= 0:
            raise ValueError("Ship length must be positive")

        row_step, column_step = DIRECTION_STEPS[direction]
        ship_cells: list[BoardPosition] = []

        for cell_offset in range(ship_length):
            ship_row: int = start_row + row_step * cell_offset
            ship_column: int = start_column + column_step * cell_offset
            ship_cells.append((ship_row, ship_column))

        return ship_cells

    def __can_place_ship(self, ship_cells: list[BoardPosition]) -> bool:
        """Return True when every ship cell is inside the board and empty."""
        for row, column in ship_cells:
            if not self.__is_valid_position(row, column):
                return False
            if self.__board[row][column] != CellValue.EMPTY:
                return False
        return True

    def __is_valid_position(self, row: int, column: int) -> bool:
        """Return True when the row and column are inside the board."""
        return 0 <= row < self.__size and 0 <= column < self.__size

    def __str__(self) -> str:
        return str(self.__board)
