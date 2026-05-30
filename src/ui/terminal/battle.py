from dataclasses import dataclass

from domain.board import BoardMatrix, CellValue
from domain.shot_result import ShotResult
from domain.symbol import Symbols
from game import Game

from .board_renderer import BoardRenderer
from .keyboard import Key, raw_terminal, read_key


@dataclass
class TargetCursor:
    row: int = 0
    col: int = 0


class BattleTargetUI:
    def __init__(self, game: Game, friendly_symbols: Symbols, enemy_symbols: Symbols, compact_board_rendering: bool):
        self.__game = game
        self.__friendly_symbols = friendly_symbols
        self.__enemy_symbols = enemy_symbols
        self.__compact_board_rendering = compact_board_rendering
        self.__cursor = TargetCursor()
        self.__message: str | None = None

    def take_turn(self, player_num: int, message: str | None = None) -> ShotResult:
        if message is not None:
            self.__message = message
        self.__reset_cursor(player_num)

        with raw_terminal():
            while True:
                self.__render(player_num)
                key = read_key()

                if key == Key.ENTER:
                    result = self.__game.try_hit(self.__cursor.row, self.__cursor.col)
                    if result == ShotResult.ALREADY_HIT:
                        self.__message = "Already targeted that cell. Pick another."
                        continue
                    return result
                if key == Key.UP:
                    self.__cursor.row = max(0, self.__cursor.row - 1)
                elif key == Key.DOWN:
                    self.__cursor.row = min(self.__board_size() - 1, self.__cursor.row + 1)
                elif key == Key.LEFT:
                    self.__cursor.col = max(0, self.__cursor.col - 1)
                elif key == Key.RIGHT:
                    self.__cursor.col = min(self.__board_size() - 1, self.__cursor.col + 1)

    def __render(self, player_num: int):
        player1_own_board, player1_opp_board = self.__game.get_player1_boards_matrix()
        player2_own_board, player2_opp_board = self.__game.get_player2_boards_matrix()
        player1_opp_overlay = self.__target_overlay(player1_opp_board) if player_num == 1 else None
        player2_opp_overlay = self.__target_overlay(player2_opp_board) if player_num == 2 else None

        print("\033[H\033[J", end="")
        print("=== Battle! ===")
        print(f"\nPlayer {player_num}'s turn")
        print(f"Target: row {self.__cursor.row + 1}, col {self.__cursor.col + 1}")
        print("Move with arrow keys, fire with Enter.")
        if self.__message is not None:
            print(self.__message)
            self.__message = None
        else:
            print()
        print()
        print(self.__render_boards(
            player1_own_board,
            player1_opp_board,
            player2_own_board,
            player2_opp_board,
            player1_opp_overlay,
            player2_opp_overlay,
        ))

    def __render_boards(
        self,
        player1_own_board: BoardMatrix,
        player1_opp_board: BoardMatrix,
        player2_own_board: BoardMatrix,
        player2_opp_board: BoardMatrix,
        player1_opp_overlay: dict[tuple[int, int], str] | None,
        player2_opp_overlay: dict[tuple[int, int], str] | None,
    ) -> str:
        player1_opp = BoardRenderer.printable_board(
            player1_opp_board,
            self.__enemy_symbols,
            "Player 1 opponent:",
            overlay=player1_opp_overlay,
            compact=self.__compact_board_rendering,
        )
        player2_opp = BoardRenderer.printable_board(
            player2_opp_board,
            self.__enemy_symbols,
            "Player 2 opponent:",
            overlay=player2_opp_overlay,
            compact=self.__compact_board_rendering,
        )
        player1_own = BoardRenderer.printable_board(
            player1_own_board,
            self.__friendly_symbols,
            "Player 1:",
            compact=self.__compact_board_rendering,
        )
        player2_own = BoardRenderer.printable_board(
            player2_own_board,
            self.__friendly_symbols,
            "Player 2:",
            compact=self.__compact_board_rendering,
        )
        return BoardRenderer.grid(player1_opp, player2_opp, player1_own, player2_own)

    def __target_overlay(self, board: BoardMatrix) -> dict[tuple[int, int], str]:
        target_symbol = "!" if board[self.__cursor.row][self.__cursor.col] != CellValue.EMPTY else "@"
        return {(self.__cursor.row, self.__cursor.col): target_symbol}

    def __reset_cursor(self, player_num: int):
        board = self.__opponent_board(player_num)
        for row in range(len(board)):
            for col in range(len(board)):
                if board[row][col] == CellValue.EMPTY:
                    self.__cursor = TargetCursor(row, col)
                    return
        self.__cursor = TargetCursor()

    def __opponent_board(self, player_num: int) -> BoardMatrix:
        if player_num == 1:
            _, board = self.__game.get_player1_boards_matrix()
        else:
            _, board = self.__game.get_player2_boards_matrix()
        return board

    def __board_size(self) -> int:
        return len(self.__opponent_board(self.__game.get_current_player_number()))
