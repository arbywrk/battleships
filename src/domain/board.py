from enum import IntEnum, StrEnum, auto
from typing import TypeAlias
from domain.execptions import AlreadyHitException

class ShipDirection(StrEnum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()

class CellValue(IntEnum):
    EMPTY = 0
    SHIP = 1
    HIT = 2
    MISS = 3

BoardMatrix: TypeAlias = list[list[CellValue]]

class Board:
    def __init__(self, size: int = 10):
        if type(size) is not int:
            raise Exception("ERROR: size must be an integer")
        self.__size = size
        self.__board: BoardMatrix = [[CellValue.EMPTY for _ in range(size)] for _ in range(size)]
    
    def __is_empty_square(self, x: int, y: int) -> bool:
        """
        __is_empty_square check if the square at position x and y is free.
        
        :param self: the Board
        :param x: the row number
        :type x: int
        :param y: the column number
        :type y: int
        :return: True if the square is empty, False otherwise 
        :rtype: bool
        """
        if not self.__is_valid_square(x, y):
            raise Exception("Invalid position")

        return self.__board[x][y] == CellValue.EMPTY

    def __is_valid_square(self, x: int, y: int) -> bool:
        """
        __is_valid_square check if the given coordinates point to a valid square.
        
        :param self: the Board
        :param x: the row number
        :type x: int
        :param y: the column number
        :type y: int
        :return: True if the square is valid, False otherwise
        :rtype: bool
        """
        return 0 <= x < self.__size and 0 <= y < self.__size

    def get_board_matrix(self) -> BoardMatrix:
        return self.__board

    def place_ship(self, x: int, y: int, direction: ShipDirection, ship_length: int):
        """Places the ship in the board."""

        if ship_length <= 0:
            raise Exception("Invalid Ship length")

        # check if the head can be placed
        if not self.__is_valid_square(x, y) or \
           not self.__is_empty_square(x, y):
            raise Exception("Can't place ship on given position")
        
        # check if the rest of the ship can be placed 
        if direction == ShipDirection.LEFT:
            for i in range(1, ship_length):
                if not self.__is_valid_square(x, y - i) or \
                   not self.__is_empty_square(x, y - i):
                    raise Exception("Can't place ship in the given direction")
        elif direction == ShipDirection.RIGHT:
            for i in range(1, ship_length):
                if not self.__is_valid_square(x, y + i) or \
                   not self.__is_empty_square(x, y + i):
                    raise Exception("Can't place ship in the given direction")
        elif direction == ShipDirection.UP:
            for i in range(1, ship_length):
                if not self.__is_valid_square(x - i, y) or \
                   not self.__is_empty_square(x - i, y):
                    raise Exception("Can't place ship in the given direction")
        elif direction == ShipDirection.DOWN:
            for i in range(1, ship_length):
                if not self.__is_valid_square(x + i, y) or \
                   not self.__is_empty_square(x + i, y):
                    raise Exception("Can't place ship in the given direction")
        else:
            raise Exception("Invalid Direction")

        # mark the place were the ship is placed
        self.__board[x][y] = CellValue.SHIP
        if direction == "l":
            for i in range(1, ship_length):
                self.__board[x][y - i] = CellValue.SHIP
        elif direction == "r":
            for i in range(1, ship_length):
                self.__board[x][y + i] = CellValue.SHIP
        elif direction == "up":
            for i in range(1, ship_length):
                self.__board[x - i][y] = CellValue.SHIP
        elif direction == "dn":
            for i in range(1, ship_length):
                self.__board[x + i][y] = CellValue.SHIP

    def get_cell_value(self, x: int, y: int) -> CellValue:
        if not self.__is_valid_square(x, y):
            raise IndexError("Invalid coordinates")
        return self.__board[x][y]

    def set_cell_value(self, x: int, y: int, value: CellValue):
        if not self.__is_valid_square(x, y):
            raise IndexError("Invalid board coordinates")
        self.__board[x][y] = value


    def try_hit(self, x, y) -> CellValue:
        if not self.__is_valid_square(x, y):
            raise IndexError("Invalid board coordinates")

        current = self.__board[x][y]

        if current in [CellValue.HIT, CellValue.MISS]:
            raise AlreadyHitException

        if current == CellValue.EMPTY:
            self.__board[x][y] = CellValue.MISS
            return CellValue.MISS
        elif current == CellValue.SHIP:
            self.__board[x][y] = CellValue.HIT
            return CellValue.HIT
        else:
            # Shouldn't happen but treat as miss
            self.__board[x][y] = CellValue.MISS
            return CellValue.MISS

    def __str__(self) -> str:
        return self.__board.__str__()
