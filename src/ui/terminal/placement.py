from dataclasses import dataclass

from domain.board import BoardMatrix, CellValue
from domain.symbol import Symbols
from game import Game

from .board_renderer import BoardRenderer
from .keyboard import Key, raw_terminal, read_key


@dataclass
class PlacementCursor:
    row: int = 0
    col: int = 0
    direction_idx: int = 1

    @property
    def direction(self) -> str:
        return DIRECTIONS[self.direction_idx]


DIRECTIONS = ("up", "right", "down", "left")
DIRECTION_DELTAS = {
    "up": (-1, 0),
    "right": (0, 1),
    "down": (1, 0),
    "left": (0, -1),
}


class ShipPlacementUI:
    def __init__(self, game: Game, friendly_symbols: Symbols, compact_board_rendering: bool):
        self.__game = game
        self.__friendly_symbols = friendly_symbols
        self.__compact_board_rendering = compact_board_rendering
        self.__cursor = PlacementCursor()
        self.__message: str | None = None

    def place_next_ship(self, player_num: int, ship_size: int) -> bool:
        own_board = self.__get_player_board(player_num)
        self.__reset_cursor(own_board, ship_size)

        with raw_terminal():
            while True:
                self.__render(player_num, ship_size)
                key = read_key()

                if key == Key.ENTER:
                    try:
                        return self.__game.place_ship((self.__cursor.row, self.__cursor.col), self.__cursor.direction)
                    except Exception:
                        self.__message = "Positioning the ship there is impossible."
                elif key == Key.ROTATE:
                    self.__cursor.direction_idx = (self.__cursor.direction_idx + 1) % len(DIRECTIONS)
                elif key == Key.UP:
                    self.__cursor.row -= 1
                elif key == Key.DOWN:
                    self.__cursor.row += 1
                elif key == Key.LEFT:
                    self.__cursor.col -= 1
                elif key == Key.RIGHT:
                    self.__cursor.col += 1

    def __get_player_board(self, player_num: int) -> BoardMatrix:
        if player_num == 1:
            board, _ = self.__game.get_player1_boards_matrix()
        else:
            board, _ = self.__game.get_player2_boards_matrix()
        return board

    def __render(self, player_num: int, ship_size: int):
        player1_board, _ = self.__game.get_player1_boards_matrix()
        player2_board, _ = self.__game.get_player2_boards_matrix()
        player1_overlay = self.__preview_overlay(player1_board, ship_size) if player_num == 1 else None
        player2_overlay = self.__preview_overlay(player2_board, ship_size) if player_num == 2 else None

        print("\033[H\033[J", end="")
        print("=== Place Your Ships ===")
        print(f"\nPlayer {player_num} - place your ship (size {ship_size})")
        print(f"Head: row {self.__cursor.row}, col {self.__cursor.col}; direction: {self.__cursor.direction}")
        print("Move with arrow keys, rotate with r, place with Enter.")
        if self.__message is not None:
            print(f"Error: {self.__message}")
            self.__message = None
        else:
            print()
        print()
        player1_render = BoardRenderer.printable_board(
            player1_board,
            self.__friendly_symbols,
            "Player 1:",
            overlay=player1_overlay,
            compact=self.__compact_board_rendering,
        )
        player2_render = BoardRenderer.printable_board(
            player2_board,
            self.__friendly_symbols,
            "Player 2:",
            overlay=player2_overlay,
            compact=self.__compact_board_rendering,
        )
        print(BoardRenderer.side_by_side(player1_render, player2_render))

    def __preview_overlay(self, board: BoardMatrix, ship_size: int) -> dict[tuple[int, int], str]:
        overlay = {}
        size = len(board)
        for row, col in self.__ship_cells(ship_size):
            if 0 <= row < size and 0 <= col < size:
                overlay[(row, col)] = "@" if board[row][col] == CellValue.EMPTY else "!"
        return overlay

    def __reset_cursor(self, board: BoardMatrix, ship_size: int):
        for row in range(len(board)):
            for col in range(len(board)):
                for direction_idx, direction in enumerate(DIRECTIONS):
                    if self.__can_place_at(board, row, col, direction, ship_size):
                        self.__cursor = PlacementCursor(row, col, direction_idx)
                        return
        self.__cursor = PlacementCursor()

    def __can_place_at(self, board: BoardMatrix, row: int, col: int, direction: str, ship_size: int) -> bool:
        size = len(board)
        row_delta, col_delta = DIRECTION_DELTAS[direction]
        for offset in range(ship_size):
            cell_row = row + row_delta * offset
            cell_col = col + col_delta * offset
            if not (0 <= cell_row < size and 0 <= cell_col < size):
                return False
            if board[cell_row][cell_col] != CellValue.EMPTY:
                return False
        return True

    def __ship_cells(self, ship_size: int) -> list[tuple[int, int]]:
        row_delta, col_delta = DIRECTION_DELTAS[self.__cursor.direction]
        return [
            (self.__cursor.row + row_delta * offset, self.__cursor.col + col_delta * offset)
            for offset in range(ship_size)
        ]
