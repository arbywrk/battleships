class Board:
    def __init__(self, size: int = 10):
        if type(size) is not int:
            raise Exception("ERROR: size must be an integer")

        self.__board = [[" " for _ in range(size)] for _ in range(size)]

    def get_printable(self) -> str:
        return self.__str__()

    def place_ship(self, x, y, direction) -> bool:
        pass

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

