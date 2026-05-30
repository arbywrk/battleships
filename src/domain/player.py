from .board import Board, BoardMatrix, BoardPosition, CellValue, ShipDirection
from .execptions import AlreadyHitException
from .fleet import Fleet
from .ship import Ship
from .shot_result import ShotResult


class Player:
    """Stores one player's fleet and both boards they can see."""

    def __init__(self, fleet: Fleet, board_size: int) -> None:
        self.__fleet: Fleet = fleet
        self.__player_board: Board = Board(board_size)
        self.__opponent_board: Board = Board(board_size)
        self.__all_ships_placed: bool = False
        self.__next_ship_index: int = 0
        self.__ship_by_position: dict[BoardPosition, Ship] = {}

    def place_ship(self, ship_position: BoardPosition, ship_direction: str) -> None:
        """Place the next unplaced ship in this player's fleet."""
        if self.__all_ships_placed:
            raise ValueError("All ships were already placed")

        ship: Ship = self.__fleet.get_ships()[self.__next_ship_index]
        direction: ShipDirection = ShipDirection(ship_direction)
        start_row, start_column = ship_position

        self.__player_board.place_ship(start_row, start_column, direction, ship.get_size())
        self.__remember_ship_positions(start_row, start_column, direction, ship)
        self.__move_to_next_ship()

    def all_ships_placed(self) -> bool:
        """Return True when this player has placed every ship."""
        return self.__all_ships_placed

    def get_next_ship_size(self) -> int | None:
        """Return the size of the next ship that must be placed."""
        if self.__all_ships_placed:
            return None
        return self.__fleet.get_ships()[self.__next_ship_index].get_size()

    def has_undestroyed_ships(self) -> bool:
        """Return True while at least one ship still has health left."""
        return not self.__fleet.destroyed()

    def receive_fire(self, row: int, column: int) -> ShotResult:
        """Apply a shot to this player's own board."""
        try:
            cell_hit_result: CellValue = self.__player_board.try_hit(row, column)
        except AlreadyHitException:
            return ShotResult.ALREADY_HIT

        if cell_hit_result == CellValue.MISS:
            return ShotResult.MISS

        return self.__handle_ship_hit(row, column)

    def mark_opponent_board(self, row: int, column: int, result: ShotResult) -> None:
        """Update this player's view of the opponent's board after firing."""
        if result == ShotResult.MISS:
            self.__opponent_board.set_cell_value(row, column, CellValue.MISS)
        elif result in (ShotResult.HIT, ShotResult.SUNK, ShotResult.WIN):
            self.__opponent_board.set_cell_value(row, column, CellValue.HIT)

    def get_player_board_matrix(self) -> BoardMatrix:
        """Return this player's own board."""
        return self.__player_board.get_board_matrix()

    def get_opponent_board_matrix(self) -> BoardMatrix:
        """Return what this player knows about the opponent's board."""
        return self.__opponent_board.get_board_matrix()

    def __remember_ship_positions(
        self,
        start_row: int,
        start_column: int,
        direction: ShipDirection,
        ship: Ship,
    ) -> None:
        """Remember which ship is located at each occupied cell."""
        ship_cells: list[BoardPosition] = self.__player_board.get_ship_cells(
            start_row,
            start_column,
            direction,
            ship.get_size(),
        )

        for ship_position in ship_cells:
            self.__ship_by_position[ship_position] = ship

    def __move_to_next_ship(self) -> None:
        """Advance the placement pointer after a ship was placed."""
        self.__next_ship_index += 1
        if self.__next_ship_index == len(self.__fleet.get_ships()):
            self.__all_ships_placed = True

    def __handle_ship_hit(self, row: int, column: int) -> ShotResult:
        """Damage the ship at a hit position and return the shot result."""
        hit_ship: Ship | None = self.__ship_by_position.get((row, column))
        if hit_ship is None:
            return ShotResult.HIT

        hit_ship.hit()
        if not hit_ship.is_destroyed():
            return ShotResult.HIT

        if self.__fleet.destroyed():
            return ShotResult.WIN
        return ShotResult.SUNK
