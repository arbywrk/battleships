from domain import Player, Fleet
from domain.board import BoardMatrix
from domain.shot_result import ShotResult


class Game:
    def __init__(self, board_size: int = 10):
        self.__first_player_turn = True
        self.__setup(board_size)

    def __setup(self, board_size: int):
        self.__player1 = Player(Fleet(), board_size)
        self.__player2 = Player(Fleet(), board_size)

    def get_current_player_number(self) -> int:
        return 1 if self.__first_player_turn else 2

    def get_next_ship_size(self) -> int | None:
        if self.__first_player_turn:
            return self.__player1.get_next_ship_size()
        return self.__player2.get_next_ship_size()

    def get_current_player_boards(self) -> tuple[BoardMatrix, BoardMatrix]:
        if self.__first_player_turn:
            return self.__player1.get_player_board_matrix(), self.__player1.get_opponent_board_matrix()
        return self.__player2.get_player_board_matrix(), self.__player2.get_opponent_board_matrix()

    def place_ship(self, ship_position: tuple[int, int], ship_direction: str) -> bool:
        """
        Place the next ship for the current player.
        Returns True if there are still more ships to place, False when all are placed.
        """
        if self.__first_player_turn:
            self.__player1.place_ship(ship_position, ship_direction)
            self.__first_player_turn = False
        else:
            self.__player2.place_ship(ship_position, ship_direction)
            self.__first_player_turn = True

        all_done = self.__player1.all_ships_placed() and self.__player2.all_ships_placed()
        return not all_done

    def try_hit(self, x: int, y: int) -> ShotResult:
        """Fire at the opponent. Switches turn unless the cell was already hit."""
        if self.__first_player_turn:
            result = self.__player2.receive_fire(x, y)
            self.__player1.mark_opponent_board(x, y, result)
            if result != ShotResult.ALREADY_HIT:
                self.__first_player_turn = False
        else:
            result = self.__player1.receive_fire(x, y)
            self.__player2.mark_opponent_board(x, y, result)
            if result != ShotResult.ALREADY_HIT:
                self.__first_player_turn = True
        return result

    def game_over(self) -> bool:
        return not self.__player1.has_undestroyed_ships() or \
               not self.__player2.has_undestroyed_ships()

    def get_player1_boards_matrix(self) -> tuple[BoardMatrix, BoardMatrix]:
        return self.__player1.get_player_board_matrix(), self.__player1.get_opponent_board_matrix()

    def get_player2_boards_matrix(self) -> tuple[BoardMatrix, BoardMatrix]:
        return self.__player2.get_player_board_matrix(), self.__player2.get_opponent_board_matrix()

    def get_winner(self) -> int | None:
        if not self.__player2.has_undestroyed_ships():
            return 1
        if not self.__player1.has_undestroyed_ships():
            return 2
        return None
