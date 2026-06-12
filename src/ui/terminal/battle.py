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


class BattleTargetSelector:
    """Lets a player choose a target with the keyboard."""

    def __init__(
        self,
        player1_symbols: Symbols,
        player2_symbols: Symbols,
        player1_opponent_symbols: Symbols,
        player2_opponent_symbols: Symbols,
        compact_board_rendering: bool,
    ) -> None:
        self.__player1_symbols: Symbols = player1_symbols
        self.__player2_symbols: Symbols = player2_symbols
        self.__player1_opponent_symbols: Symbols = player1_opponent_symbols
        self.__player2_opponent_symbols: Symbols = player2_opponent_symbols
        self.__compact_board_rendering: bool = compact_board_rendering
        self.__cursor: TargetCursor = TargetCursor()
        self.__message: str | None = None

    def select_target(
        self,
        player_number: int,
        own_board: BoardMatrix,
        opponent_board: BoardMatrix,
        message: str | None = None,
    ) -> BoardPosition:
        """Let a player choose a target with the keyboard."""
        self.__message = message
        self.__move_cursor_to_first_open_cell(opponent_board)

        with raw_terminal():
            while True:
                self.__render_single_player_view(player_number, own_board, opponent_board)
                pressed_key: str = read_key()

                if pressed_key == Key.ENTER:
                    return self.__cursor.row, self.__cursor.column

                self.__handle_movement_key(opponent_board, pressed_key)

    def __handle_movement_key(self, opponent_board: BoardMatrix, pressed_key: str) -> None:
        """Move the targeting cursor inside the opponent board."""
        board_size: int = len(opponent_board)

        if pressed_key == Key.UP:
            self.__cursor.row = max(0, self.__cursor.row - 1)
        elif pressed_key == Key.DOWN:
            self.__cursor.row = min(board_size - 1, self.__cursor.row + 1)
        elif pressed_key == Key.LEFT:
            self.__cursor.column = max(0, self.__cursor.column - 1)
        elif pressed_key == Key.RIGHT:
            self.__cursor.column = min(board_size - 1, self.__cursor.column + 1)

    def __render_single_player_view(
        self,
        player_number: int,
        own_board: BoardMatrix,
        opponent_board: BoardMatrix,
    ) -> None:
        """Print the battle screen for one player."""
        print("\033[H\033[J", end="")
        print("=== Battle! ===")
        print(f"\nPlayer {player_number}'s turn")
        print(self.__cursor_description())
        print("Move with arrow keys, fire with Enter.")
        self.__print_message_line()
        print()
        print(BoardRenderer.side_by_side(
            BoardRenderer.printable_board(
                own_board,
                self.__own_symbols(player_number),
                "Your board:",
                compact=self.__compact_board_rendering,
            ),
            BoardRenderer.printable_board(
                opponent_board,
                self.__opponent_symbols(player_number),
                "Opponent:",
                overlay=self.__target_overlay(opponent_board),
                compact=self.__compact_board_rendering,
            ),
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

    def __target_overlay(self, opponent_board: BoardMatrix) -> BoardOverlay:
        """Return the symbol that marks the selected target cell."""
        target_position: BoardPosition = (self.__cursor.row, self.__cursor.column)
        target_cell: CellValue = opponent_board[self.__cursor.row][self.__cursor.column]

        if target_cell == CellValue.EMPTY:
            return {target_position: "@"}
        return {target_position: "!"}

    def __move_cursor_to_first_open_cell(self, opponent_board: BoardMatrix) -> None:
        """Start each turn on the first opponent cell that has not been used."""
        for row_index in range(len(opponent_board)):
            for column_index in range(len(opponent_board)):
                if opponent_board[row_index][column_index] == CellValue.EMPTY:
                    self.__cursor = TargetCursor(row_index, column_index)
                    return

        self.__cursor = TargetCursor()

    def __own_symbols(self, player_number: int) -> Symbols:
        if player_number == 2:
            return self.__player2_symbols
        return self.__player1_symbols

    def __opponent_symbols(self, player_number: int) -> Symbols:
        if player_number == 2:
            return self.__player2_opponent_symbols
        return self.__player1_opponent_symbols


class BattleTargetUI:
    """Runs local battle turns using the shared keyboard selector."""

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
        self.__selector: BattleTargetSelector = BattleTargetSelector(
            player1_symbols,
            player2_symbols,
            player1_opponent_symbols,
            player2_opponent_symbols,
            compact_board_rendering,
        )

    def take_turn(self, player_number: int, message: str | None = None) -> ShotResult:
        """Run one player's targeting turn and return the shot result."""
        turn_message: str | None = message

        while True:
            own_board, opponent_board = self.__current_player_boards(player_number)
            row, column = self.__selector.select_target(
                player_number,
                own_board,
                opponent_board,
                turn_message,
            )
            shot_result: ShotResult = self.__game.try_hit(row, column)

            if shot_result != ShotResult.ALREADY_HIT:
                return shot_result

            turn_message = "Already targeted that cell. Pick another."

    def __current_player_boards(self, player_number: int) -> tuple[BoardMatrix, BoardMatrix]:
        """Return the active player's own board and opponent board."""
        if player_number == 1:
            return self.__game.get_player1_boards_matrix()
        return self.__game.get_player2_boards_matrix()
