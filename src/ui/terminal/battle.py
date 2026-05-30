from dataclasses import dataclass

from domain.board import BoardMatrix, BoardPosition, CellValue
from domain.shot_result import ShotResult
from domain.symbol import Symbols
from game import Game

from .board_renderer import BoardOverlay, BoardRenderer
from .keyboard import Key, raw_terminal, read_key


@dataclass
class TargetCursor:
    """The target position selected by the current player."""

    row: int = 0
    column: int = 0


class BattleTargetUI:
    """Lets players choose a target with the keyboard."""

    def __init__(
        self,
        game: Game,
        player1_symbols: Symbols,
        player2_symbols: Symbols,
        player1_opponent_symbols: Symbols,
        player2_opponent_symbols: Symbols,
        compact_board_rendering: bool,
    ) -> None:
        self.__game: Game = game
        self.__player1_symbols: Symbols = player1_symbols
        self.__player2_symbols: Symbols = player2_symbols
        self.__player1_opponent_symbols: Symbols = player1_opponent_symbols
        self.__player2_opponent_symbols: Symbols = player2_opponent_symbols
        self.__compact_board_rendering: bool = compact_board_rendering
        self.__cursor: TargetCursor = TargetCursor()
        self.__message: str | None = None

    def take_turn(self, player_number: int, message: str | None = None) -> ShotResult:
        """Run one player's targeting turn and return the shot result."""
        self.__message = message
        self.__move_cursor_to_first_open_target(player_number)

        with raw_terminal():
            while True:
                self.__render(player_number)
                pressed_key: str = read_key()

                if pressed_key == Key.ENTER:
                    shot_result: ShotResult | None = self.__try_fire()
                    if shot_result is not None:
                        return shot_result
                else:
                    self.__handle_movement_key(player_number, pressed_key)

    def __try_fire(self) -> ShotResult | None:
        """Fire at the selected cell, or keep the turn open if it was used."""
        shot_result: ShotResult = self.__game.try_hit(self.__cursor.row, self.__cursor.column)

        if shot_result == ShotResult.ALREADY_HIT:
            self.__message = "Already targeted that cell. Pick another."
            return None

        return shot_result

    def __handle_movement_key(self, player_number: int, pressed_key: str) -> None:
        """Move the targeting cursor inside the opponent board."""
        board_size: int = len(self.__opponent_board(player_number))

        if pressed_key == Key.UP:
            self.__cursor.row = max(0, self.__cursor.row - 1)
        elif pressed_key == Key.DOWN:
            self.__cursor.row = min(board_size - 1, self.__cursor.row + 1)
        elif pressed_key == Key.LEFT:
            self.__cursor.column = max(0, self.__cursor.column - 1)
        elif pressed_key == Key.RIGHT:
            self.__cursor.column = min(board_size - 1, self.__cursor.column + 1)

    def __render(self, player_number: int) -> None:
        """Print the full battle screen."""
        player1_board, player1_opponent_board = self.__game.get_player1_boards_matrix()
        player2_board, player2_opponent_board = self.__game.get_player2_boards_matrix()

        player1_target_overlay: BoardOverlay | None = None
        player2_target_overlay: BoardOverlay | None = None
        if player_number == 1:
            player1_target_overlay = self.__target_overlay(player1_opponent_board)
        else:
            player2_target_overlay = self.__target_overlay(player2_opponent_board)

        print("\033[H\033[J", end="")
        print("=== Battle! ===")
        print(f"\nPlayer {player_number}'s turn")
        print(self.__cursor_description())
        print("Move with arrow keys, fire with Enter.")
        self.__print_message_line()
        print()
        print(self.__render_boards(
            player1_board,
            player1_opponent_board,
            player2_board,
            player2_opponent_board,
            player1_target_overlay,
            player2_target_overlay,
        ))

    def __cursor_description(self) -> str:
        """Return a clear description of the selected target."""
        display_row: int = self.__cursor.row + 1
        display_column: int = self.__cursor.column + 1
        return f"Target: row {display_row}, col {display_column}"

    def __print_message_line(self) -> None:
        """Print the previous shot result, or a blank line."""
        if self.__message is None:
            print()
            return

        print(self.__message)
        self.__message = None

    def __render_boards(
        self,
        player1_board: BoardMatrix,
        player1_opponent_board: BoardMatrix,
        player2_board: BoardMatrix,
        player2_opponent_board: BoardMatrix,
        player1_target_overlay: BoardOverlay | None,
        player2_target_overlay: BoardOverlay | None,
    ) -> str:
        """Return own boards on top and opponent views underneath."""
        player1_opponent_text: str = BoardRenderer.printable_board(
            player1_opponent_board,
            self.__player1_opponent_symbols,
            "Player 1 opponent:",
            overlay=player1_target_overlay,
            compact=self.__compact_board_rendering,
        )
        player2_opponent_text: str = BoardRenderer.printable_board(
            player2_opponent_board,
            self.__player2_opponent_symbols,
            "Player 2 opponent:",
            overlay=player2_target_overlay,
            compact=self.__compact_board_rendering,
        )
        player1_board_text: str = BoardRenderer.printable_board(
            player1_board,
            self.__player1_symbols,
            "Player 1:",
            compact=self.__compact_board_rendering,
        )
        player2_board_text: str = BoardRenderer.printable_board(
            player2_board,
            self.__player2_symbols,
            "Player 2:",
            compact=self.__compact_board_rendering,
        )

        return BoardRenderer.grid(
            player1_board_text,
            player2_board_text,
            player1_opponent_text,
            player2_opponent_text,
        )

    def __target_overlay(self, opponent_board: BoardMatrix) -> BoardOverlay:
        """Return the symbol that marks the selected target cell."""
        target_position: BoardPosition = (self.__cursor.row, self.__cursor.column)
        target_cell: CellValue = opponent_board[self.__cursor.row][self.__cursor.column]

        if target_cell == CellValue.EMPTY:
            return {target_position: "@"}
        return {target_position: "!"}

    def __move_cursor_to_first_open_target(self, player_number: int) -> None:
        """Start each turn on the first opponent cell that has not been used."""
        opponent_board: BoardMatrix = self.__opponent_board(player_number)

        for row_index in range(len(opponent_board)):
            for column_index in range(len(opponent_board)):
                if opponent_board[row_index][column_index] == CellValue.EMPTY:
                    self.__cursor = TargetCursor(row_index, column_index)
                    return

        self.__cursor = TargetCursor()

    def __opponent_board(self, player_number: int) -> BoardMatrix:
        """Return the active player's view of the opponent board."""
        if player_number == 1:
            _player_board, opponent_board = self.__game.get_player1_boards_matrix()
        else:
            _player_board, opponent_board = self.__game.get_player2_boards_matrix()
        return opponent_board
