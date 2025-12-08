class Board:
    def __init__(self, size: int = 10):
        if type(size) is not int:
            raise Exception("ERROR: size must be an integer")

        self.__board = [[" " for _ in range(size)] for _ in range(size)]

    def get_printable(self) -> str:
        return self.__str__()

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
        if x < 0 or x >= len(self.__board) or \
           y < 0 or y >= len(self.__board[x]) or \
           self.__board[x][y] != " ":
            return False
        
        # check if the rest of the ship can be placed 
        if direction == "l":
            for i in range(1, ship_length):
                if y - i < 0 or self.__board[x][y - i] != " ":
                    return False
        elif direction == "r":
            for i in range(1, ship_length):
                if y + i >= len(self.__board[x]) or self.__board[x][y + i] != " ":
                    return False
        elif direction == "up":
            for i in range(1, ship_length):
                if x - i < 0 or self.__board[x - i][y] != " ":
                    return False
        elif direction == "dn":
            for i in range(1, ship_length):
                if y + i >= len(self.__board) or self.__board[x + i][y] != " ":
                    return False
        else:
            return False

        # mark the place were the ship is placed
        self.__board[x][y] = "🟦"
        if direction == "l":
            for i in range(1, ship_length):
                self.__board[x][y - i] = "🟦"
        elif direction == "r":
            for i in range(1, ship_length):
                self.__board[x][y + i] = "🟦"
        elif direction == "up":
            for i in range(1, ship_length):
                self.__board[x - i][y] = "🟦"
        elif direction == "dn":
            for i in range(1, ship_length):
                self.__board[x + i][y] = "🟦"

        return True # success

    def __has_ship(self, x, y) -> bool:
        return self.__board[x][y] != " "

    def try_hit(self, x, y) -> bool:
        # TODO: check if this was already hit
        if self.__has_ship(x, y):
            # TODO: mark the ship as hit
            return True
        return False

    def __str__(self) -> str:
        fmt_board = str(self.__board) \
                    .replace("], ", "|\n") \
                    .replace("[", "|") \
                    .replace("]", "|") \
                    .replace(", ", "|") \
                    .replace("'", " ") \
                    .replace("||", "|")
        border = "-" * (len(self.__board[0]) * 4 + 1)
        fmt_board_with_borders = border + "\n" + \
                                 fmt_board.replace("\n", "\n" + border + "\n") + \
                                 "\n" + border
        return fmt_board_with_borders

