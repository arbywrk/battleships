from domain import Fleet, Player
from domain.board import BoardMatrix, BoardPosition
from domain.shot_result import ShotResult


class Game:
    """Coordinates the two players and controls whose turn it is."""

    def __init__(self, board_size: int, ship_sizes: list[int]) -> None:
        self.__player1: Player = Player(Fleet(ship_sizes), board_size)
        self.__player2: Player = Player(Fleet(ship_sizes), board_size)
        self.__is_player1_turn: bool = True

    def get_current_player_number(self) -> int:
        """Return 1 or 2 for the player whose turn is active."""
        if self.__is_player1_turn:
            return 1
        return 2

    def get_next_ship_size(self) -> int | None:
        """Return the next ship size for the player who is placing now."""
        return self.__current_player().get_next_ship_size()

    def get_current_player_boards(self) -> tuple[BoardMatrix, BoardMatrix]:
        """Return the own board and opponent view for the current player."""
        return (
            self.__current_player().get_player_board_matrix(),
            self.__current_player().get_opponent_board_matrix(),
        )

    def place_ship(self, ship_position: BoardPosition, ship_direction: str) -> bool:
        """
        Place the next ship for the current player.

        Returns True while there are more ships to place.
        Returns False once both players have placed all ships.
        """
        self.__current_player().place_ship(ship_position, ship_direction)
        self.__switch_turn()

        both_players_finished: bool = (
            self.__player1.all_ships_placed()
            and self.__player2.all_ships_placed()
        )
        return not both_players_finished

    def try_hit(self, row: int, column: int) -> ShotResult:
        """Fire at the opponent. The turn changes after a new valid shot."""
        current_player: Player = self.__current_player()
        opponent: Player = self.__opponent_player()

        shot_result: ShotResult = opponent.receive_fire(row, column)
        current_player.mark_opponent_board(row, column, shot_result)

        if shot_result != ShotResult.ALREADY_HIT:
            self.__switch_turn()

        return shot_result

    def game_over(self) -> bool:
        """Return True when at least one player has lost every ship."""
        return (
            not self.__player1.has_undestroyed_ships()
            or not self.__player2.has_undestroyed_ships()
        )

    def get_player1_boards_matrix(self) -> tuple[BoardMatrix, BoardMatrix]:
        """Return player 1's own board and opponent view."""
        return (
            self.__player1.get_player_board_matrix(),
            self.__player1.get_opponent_board_matrix(),
        )

    def get_player2_boards_matrix(self) -> tuple[BoardMatrix, BoardMatrix]:
        """Return player 2's own board and opponent view."""
        return (
            self.__player2.get_player_board_matrix(),
            self.__player2.get_opponent_board_matrix(),
        )

    def get_winner(self) -> int | None:
        """Return the winning player number, or None if nobody has won yet."""
        if not self.__player2.has_undestroyed_ships():
            return 1
        if not self.__player1.has_undestroyed_ships():
            return 2
        return None

    def __current_player(self) -> Player:
        """Return the player whose turn is active."""
        if self.__is_player1_turn:
            return self.__player1
        return self.__player2

    def __opponent_player(self) -> Player:
        """Return the player who is being targeted this turn."""
        if self.__is_player1_turn:
            return self.__player2
        return self.__player1

    def __switch_turn(self) -> None:
        """Pass the turn to the other player."""
        self.__is_player1_turn = not self.__is_player1_turn
