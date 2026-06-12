from dataclasses import dataclass
from enum import StrEnum, auto

from domain.board import BoardMatrix, BoardPosition, CellValue
from domain.symbol import Symbols
from game import Game

from .board_renderer import BoardOverlay, BoardRenderer
from .keyboard import Key, raw_terminal, read_key

class Direction(StrEnum):
    UP = auto()
    DOWN = auto()
    RIGHT = auto()
    LEFT = auto()

    def delta(self) -> tuple[int, int]:
        match self:
            case Direction.UP:
                return -1, 0
            case Direction.DOWN:
                return 1, 0
            case Direction.RIGHT:
                return 0, 1
            case Direction.LEFT:
                return 0, -1

    def rotate(self) -> Direction:
        match self:
            case Direction.UP:
                return Direction.RIGHT
            case Direction.RIGHT:
                return Direction.DOWN
            case Direction.DOWN:
                return Direction.LEFT
            case Direction.LEFT:
                return Direction.UP

@dataclass
class PlacementCursor:
    """The ship head position and direction during placement."""

    row: int = 0
    column: int = 0
    direction: Direction = Direction.RIGHT

class ShipPlacementSelector:
    """Lets a player choose a ship position with the keyboard."""

    def __init__(
        self,
        player1_symbols: Symbols,
        player2_symbols: Symbols,
        compact_board_rendering: bool,
    ) -> None:
        self.__player1_symbols: Symbols = player1_symbols
        self.__player2_symbols: Symbols = player2_symbols
        self.__compact_board_rendering: bool = compact_board_rendering
        self.__cursor: PlacementCursor = PlacementCursor()
        self.__message: str | None = None

    def select_ship_position(
        self,
        player_number: int,
        ship_size: int,
        player_board: BoardMatrix,
        message: str | None = None,
    ) -> tuple[BoardPosition, str]:
        """Let a player choose a ship position with the keyboard."""
        self.__message = message
        self.__move_cursor_to_first_valid_position(player_board, ship_size)

        with raw_terminal():
            while True:
                self.__render_single_board(player_number, player_board, ship_size)
                pressed_key: str = read_key()

                if pressed_key == Key.ENTER:
                    if self.__can_place_at(
                        player_board,
                        self.__cursor.row,
                        self.__cursor.column,
                        self.__cursor.direction,
                        ship_size,
                    ):
                        return (
                            (self.__cursor.row, self.__cursor.column),
                            self.__cursor.direction.value,
                        )
                    self.__message = "Positioning the ship there is impossible."
                else:
                    self.__handle_movement_key(pressed_key, ship_size, len(player_board))

    def __handle_movement_key(self, pressed_key: str, ship_size: int, board_size: int) -> None:
        """Update the cursor after an arrow key or rotation key."""
        def normalize():
            # normalize up
            if self.__cursor.direction is Direction.UP:
                self.__cursor.row = max(ship_size - 1, self.__cursor.row)
            else:
                self.__cursor.row = max(0, self.__cursor.row)
            # normalize down
            if self.__cursor.direction is Direction.DOWN:
                self.__cursor.row = min(board_size - ship_size, self.__cursor.row)
            else:
                self.__cursor.row = min(board_size - 1, self.__cursor.row)
            # normalize right
            if self.__cursor.direction is Direction.RIGHT:
                self.__cursor.column = min(board_size - ship_size, self.__cursor.column)
            else:
                self.__cursor.column = min(board_size - 1, self.__cursor.column)
            # normalize left
            if self.__cursor.direction is Direction.LEFT:
                self.__cursor.column = max(ship_size - 1, self.__cursor.column)
            else:
                self.__cursor.column = max(0, self.__cursor.column)

        def move_up():
            self.__cursor.row -= 1
            normalize()

        def move_down():
            self.__cursor.row += 1
            normalize()

        def move_right():
            self.__cursor.column += 1
            normalize()

        def move_left():
            self.__cursor.column -= 1
            normalize()

        def rotate():
            self.__cursor.direction = self.__cursor.direction.rotate()
            normalize()

        if pressed_key == Key.ROTATE_RIGHT:
            rotate()
        elif pressed_key == Key.UP:
            move_up()
        elif pressed_key == Key.DOWN:
            move_down()
        elif pressed_key == Key.LEFT:
            move_left()
        elif pressed_key == Key.RIGHT:
            move_right()

    def __render_single_board(
        self,
        player_number: int,
        player_board: BoardMatrix,
        ship_size: int,
    ) -> None:
        """Print the placement screen for one player."""
        print("\033[H\033[J", end="")
        print("=== Place Your Ships ===")
        print(f"\nPlayer {player_number} - place your ship (size {ship_size})")
        print(self.__cursor_description())
        print("Move with arrow keys, rotate with r, place with Enter.")
        self.__print_message_line()
        print()
        print(BoardRenderer.printable_board(
            player_board,
            self.__symbols_for_player(player_number),
            f"Player {player_number}:",
            overlay=self.__preview_overlay(player_board, ship_size),
            compact=self.__compact_board_rendering,
        ))

    def __cursor_description(self) -> str:
        """Return a clear description of the cursor for the current player."""
        display_row: int = self.__cursor.row + 1
        display_column: int = self.__cursor.column + 1
        return f"Head: row {display_row}, col {display_column}; direction: {self.__cursor.direction}"

    def __print_message_line(self) -> None:
        """Print the current error message, or a blank line."""
        if self.__message is None:
            print()
            return

        print(f"Error: {self.__message}")
        self.__message = None

    def __symbols_for_player(self, player_number: int) -> Symbols:
        if player_number == 2:
            return self.__player2_symbols
        return self.__player1_symbols

    def __preview_overlay(self, board: BoardMatrix, ship_size: int) -> BoardOverlay:
        """Return symbols for the visible part of the ship preview."""
        overlay: BoardOverlay = {}
        board_size: int = len(board)

        for preview_row, preview_column in self.__ship_cells(ship_size):
            if 0 <= preview_row < board_size and 0 <= preview_column < board_size:
                if board[preview_row][preview_column] == CellValue.EMPTY:
                    overlay[(preview_row, preview_column)] = "@"
                else:
                    overlay[(preview_row, preview_column)] = "!"

        return overlay

    def __move_cursor_to_first_valid_position(self, board: BoardMatrix, ship_size: int) -> None:
        """Start each ship on the first valid placement found on the board."""
        for row_index in range(len(board)):
            for column_index in range(len(board)):
                for direction in Direction:
                    if self.__can_place_at(board, row_index, column_index, direction, ship_size):
                        self.__cursor = PlacementCursor(row_index, column_index, direction)
                        return

        self.__cursor = PlacementCursor()

    def __can_place_at(
        self,
        board: BoardMatrix,
        start_row: int,
        start_column: int,
        direction: Direction,
        ship_size: int,
    ) -> bool:
        """Return True when a ship fits at the requested position."""
        board_size: int = len(board)
        row_step, column_step = direction.delta()

        for cell_offset in range(ship_size):
            ship_row: int = start_row + row_step * cell_offset
            ship_column: int = start_column + column_step * cell_offset

            if not (0 <= ship_row < board_size and 0 <= ship_column < board_size):
                return False
            if board[ship_row][ship_column] != CellValue.EMPTY:
                return False

        return True

    def __ship_cells(self, ship_size: int) -> list[BoardPosition]:
        """Return the cells currently covered by the ship preview."""
        row_step, column_step = self.__cursor.direction.delta()
        ship_cells: list[BoardPosition] = []

        for cell_offset in range(ship_size):
            ship_row: int = self.__cursor.row + row_step * cell_offset
            ship_column: int = self.__cursor.column + column_step * cell_offset
            ship_cells.append((ship_row, ship_column))

        return ship_cells


class ShipPlacementUI:
    """Places ships in a local game using the shared keyboard selector."""

    def __init__(
        self,
        game: Game,
        player1_symbols: Symbols,
        player2_symbols: Symbols,
        compact_board_rendering: bool,
    ) -> None:
        self.__game: Game = game
        self.__selector: ShipPlacementSelector = ShipPlacementSelector(
            player1_symbols,
            player2_symbols,
            compact_board_rendering,
        )

    def place_next_ship(self, player_number: int, ship_size: int) -> bool:
        """Run the placement screen until the current ship is placed."""
        player_board: BoardMatrix = self.__get_player_board(player_number)
        message: str | None = None

        while True:
            ship_position, ship_direction = self.__selector.select_ship_position(
                player_number,
                ship_size,
                player_board,
                message,
            )

            try:
                return self.__game.place_ship(ship_position, ship_direction)
            except ValueError:
                message = "Positioning the ship there is impossible."

    def __get_player_board(self, player_number: int) -> BoardMatrix:
        """Return the own board for the requested player."""
        if player_number == 1:
            player_board, _opponent_board = self.__game.get_player1_boards_matrix()
        else:
            player_board, _opponent_board = self.__game.get_player2_boards_matrix()
        return player_board