from .fleet import Fleet
from .board import Board, BoardMatrix, CellValue, ShipDirection
from .ship import Ship
from .shot_result import ShotResult
from .execptions import AlreadyHitException


class Player:
    def __init__(self, fleet: Fleet, board_size: int):
        self.__fleet = fleet
        self.__player_board = Board(board_size)
        self.__opponent_board = Board(board_size)
        self.__all_ships_placed = False
        self.__idx_of_next_ship_to_place = 0
        self.__ship_positions: dict[tuple[int, int], Ship] = {}

    def __place_ship(self, x: int, y: int, direction: str, ship: Ship):
        self.__player_board.place_ship(x, y, direction, ship.get_size())

        self.__ship_positions[(x, y)] = ship
        if direction == ShipDirection.LEFT:
            for i in range(1, ship.get_size()):
                self.__ship_positions[(x, y - i)] = ship
        elif direction == ShipDirection.RIGHT:
            for i in range(1, ship.get_size()):
                self.__ship_positions[(x, y + i)] = ship
        elif direction == ShipDirection.UP:
            for i in range(1, ship.get_size()):
                self.__ship_positions[(x - i, y)] = ship
        elif direction == ShipDirection.DOWN:
            for i in range(1, ship.get_size()):
                self.__ship_positions[(x + i, y)] = ship

    def place_ship(self, ship_position: tuple[int, int], ship_direction: str):
        """Places the next ship in the fleet on the player's board."""
        if self.__all_ships_placed:
            raise Exception("All ships were already placed")

        ship = self.__fleet.get_ships()[self.__idx_of_next_ship_to_place]
        self.__place_ship(ship_position[0], ship_position[1], ship_direction, ship)

        self.__idx_of_next_ship_to_place += 1
        if self.__idx_of_next_ship_to_place == len(self.__fleet.get_ships()):
            self.__all_ships_placed = True

    def all_ships_placed(self) -> bool:
        return self.__all_ships_placed

    def get_next_ship_size(self) -> int | None:
        if self.__all_ships_placed:
            return None
        return self.__fleet.get_ships()[self.__idx_of_next_ship_to_place].get_size()

    def has_undestroyed_ships(self) -> bool:
        return not self.__fleet.destroyed()

    def receive_fire(self, x: int, y: int) -> ShotResult:
        """Process incoming fire on this player's board and return the result."""
        try:
            result = self.__player_board.try_hit(x, y)
        except AlreadyHitException:
            return ShotResult.ALREADY_HIT

        if result == CellValue.MISS:
            return ShotResult.MISS

        if result == CellValue.HIT:
            ship: Ship | None = self.__ship_positions.get((x, y), None)
            if ship is not None:
                ship.hit()
                if ship.is_destroyed():
                    if self.__fleet.destroyed():
                        return ShotResult.WIN
                    return ShotResult.SUNK
            return ShotResult.HIT

        return ShotResult.MISS

    def mark_opponent_board(self, x: int, y: int, result: ShotResult):
        """Update the local view of the opponent's board."""
        if result == ShotResult.MISS:
            self.__opponent_board.set_cell_value(x, y, CellValue.MISS)
        elif result in (ShotResult.HIT, ShotResult.SUNK, ShotResult.WIN):
            self.__opponent_board.set_cell_value(x, y, CellValue.HIT)

    def get_player_board_matrix(self) -> BoardMatrix:
        return self.__player_board.get_board_matrix()

    def get_opponent_board_matrix(self) -> BoardMatrix:
        return self.__opponent_board.get_board_matrix()
