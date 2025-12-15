import unicodedata

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

    def get_printable(self) -> str:
        return self.__str__()

    # TODO: (in holiday) replace the return type of this function to None (return nothing):
    # and handle the case in which you don't have valid input (the ones in which you return False)
    # with exceptions and try...except
    def place_ship(self, x: int, y: int, direction: str, ship_length: int) -> bool:
        """
        Places the ship in the board.
        
        :param self: class instance
        :param x: the x coordinate of the ship's head
        :param y: the y coordinate of the ship's head
        :param direction: direction of the ship's tail
        :return: True if the placement was successfull, False otherwise
        :rtype: bool
        """

        # check if the head can be placed
        if not self.__is_valid_square(x, y) or \
           not self.__is_empty_square(x, y):
            return False
        
        # check if the rest of the ship can be placed 
        if direction == "l":
            for i in range(1, ship_length):
                if not self.__is_valid_square(x, y - i) or \
                   not self.__is_empty_square(x, y - i):
                    return False
        elif direction == "r":
            for i in range(1, ship_length):
                if not self.__is_valid_square(x, y + i) or \
                   not self.__is_empty_square(x, y + i):
                    return False
        elif direction == "up":
            for i in range(1, ship_length):
                if not self.__is_valid_square(x - i, y) or \
                   not self.__is_empty_square(x - i, y):
                    return False
        elif direction == "dn":
            for i in range(1, ship_length):
                if not self.__is_valid_square(x + i, y) or \
                   not self.__is_empty_square(x + i, y):
                    return False
        else:
            return False

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

        return True # success

    # TODO: (in holiday) implement try_hit (follow the exemples we wrote)
    def try_hit(self, x, y) -> bool:
        # TODO: check if this was already hit
        # TODO: mark the ship as hit
        return True

    def __str__(self) -> str:
        fmt_board = ''
        border = "-" * (len(self.__board[0]) * (3 + self.__ship_symbol_w) + 1)
        for row in self.__board:
            fmt_row = '|' + str(row)[1:-1].replace(', ', '|').replace("'", " ") + '|'
            fmt_board += f'{border}\n{fmt_row}\n'
        fmt_board += border + '\n'
        return fmt_board

