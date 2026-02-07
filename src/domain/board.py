import unicodedata
from typing import TypeAlias

BoardMatrix: TypeAlias = list[list[str]]

class Board:
    def __init__(self, ship_symbol: str, size: int = 10):
        if type(size) is not int:
            raise Exception("ERROR: size must be an integer")

        self.__ship_symbol_w = 0
        for ch in ship_symbol:
            ch_is_emoji: bool = unicodedata.east_asian_width(ch) == 'W'
            self.__ship_symbol_w += 2 if ch_is_emoji else 1

        self.__empty_symbol = ' ' * self.__ship_symbol_w
        self.__ship_symbol = ship_symbol
        self.__board = [[self.__empty_symbol for _ in range(size)] for _ in range(size)]
    
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
        return self.__board[x][y] == self.__empty_symbol

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
        return x >= 0 and x < len(self.__board) and \
               y >= 0 and y < len(self.__board[x])

    def get_board_matrix(self) -> BoardMatrix:
        return self.__board

    def place_ship(self, x: int, y: int, direction: str, ship_length: int):
        """
        Places the ship in the board.
        
        :param self: class instance
        :param x: the x coordinate of the ship's head
        :param y: the y coordinate of the ship's head
        :param direction: direction of the ship's tail
        :raises Exception: if the ship can't be placed on the given position
        """

        # check if the head can be placed
        if not self.__is_valid_square(x, y) or \
           not self.__is_empty_square(x, y):
            raise Exception("Can't place ship on given postion")
        
        # check if the rest of the ship can be placed 
        if direction == "l":
            for i in range(1, ship_length):
                if not self.__is_valid_square(x, y - i) or \
                   not self.__is_empty_square(x, y - i):
                    raise Exception("Can't place ship in the given direction")
        elif direction == "r":
            for i in range(1, ship_length):
                if not self.__is_valid_square(x, y + i) or \
                   not self.__is_empty_square(x, y + i):
                    raise Exception("Can't place ship in the given direction")
        elif direction == "up":
            for i in range(1, ship_length):
                if not self.__is_valid_square(x - i, y) or \
                   not self.__is_empty_square(x - i, y):
                    raise Exception("Can't place ship in the given direction")
        elif direction == "dn":
            for i in range(1, ship_length):
                if not self.__is_valid_square(x + i, y) or \
                   not self.__is_empty_square(x + i, y):
                    raise Exception("Can't place ship in the given direction")
        else:
            raise Exception("Invalid Direction")

        # mark the place were the ship is placed
        self.__board[x][y] = self.__ship_symbol
        if direction == "l":
            for i in range(1, ship_length):
                self.__board[x][y - i] = self.__ship_symbol
        elif direction == "r":
            for i in range(1, ship_length):
                self.__board[x][y + i] = self.__ship_symbol
        elif direction == "up":
            for i in range(1, ship_length):
                self.__board[x - i][y] = self.__ship_symbol
        elif direction == "dn":
            for i in range(1, ship_length):
                self.__board[x + i][y] = self.__ship_symbol

    def _pad_symbol(self, ch: str) -> str:
        """Return a symbol padded to the ship symbol width."""
        base = ch
        # pad with spaces to match ship symbol width
        if len(base) < self.__ship_symbol_w:
            base = base + ' ' * (self.__ship_symbol_w - len(base))
        return base

    def get_symbol(self, x: int, y: int) -> str:
        if not self.__is_valid_square(x, y):
            raise IndexError("Invalid board coordinates")
        return self.__board[x][y]

    def set_symbol(self, x: int, y: int, symbol: str):
        if not self.__is_valid_square(x, y):
            raise IndexError("Invalid board coordinates")
        self.__board[x][y] = self._pad_symbol(symbol)

    def try_hit(self, x, y) -> str:
        """Apply a hit on the board and return the result: 'miss' or 'hit'.

        Raises IndexError for invalid coordinates and returns 'already' if the
        square was already targeted.
        """
        # TODO: use an enum
        # TODO: throw errors
        if not self.__is_valid_square(x, y):
            raise IndexError("Invalid board coordinates")

        current = self.__board[x][y]
        # Already targeted markers: an 'X' for hit or '.' for miss (padded)
        if current.strip() in ['X', '.']:
            return 'already'

        if current == self.__empty_symbol:
            # miss
            self.__board[x][y] = self._pad_symbol('.')
            return 'miss'
        elif current == self.__ship_symbol:
            # hit
            self.__board[x][y] = self._pad_symbol('X')
            return 'hit'
        else:
            # Shouldn't happen but treat as miss
            self.__board[x][y] = self._pad_symbol('.')
            return 'miss'

    def __str__(self) -> str:
        fmt_board = ''
        border = "-" * (len(self.__board[0]) * (3 + self.__ship_symbol_w) + 1)
        for row in self.__board:
            fmt_row = '|' + str(row)[1:-1].replace(', ', '|').replace("'", " ") + '|'
            fmt_board += f'{border}\n{fmt_row}\n'
        fmt_board += border + '\n'
        return fmt_board

