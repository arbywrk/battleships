from .fleet import Fleet
from .board import Board, BoardMatrix
from .ship import Ship
from enum import Enum

# TODO: use direction enum
# class Direction(Enum):
#     UP = 'up'
#     DOWN = 'down'
#     RIGHT = 'right'
#     LEFT = 'left'

class Player:
    def __init__(self, fleet: Fleet, friedly_ship_symbol: str, enemy_ship_symbol: str, board_size: int):
        self.__fleet = fleet
        self.__player_board = Board(friedly_ship_symbol, board_size)
        self.__opponent_board = Board(enemy_ship_symbol, board_size)
        self.__all_ships_placed = False
        self.__idx_of_next_ship_to_place = 0
        # map coordinates (x,y) -> Ship (for hits)
        self.__ship_positions: dict[tuple[int,int], Ship] = {}

    def __place_ship(self, x: int, y: int, direction: str, ship_size: int):
        """
        Calls the board's method for placing a ship and registers the ship's
        occupied positions in the `__ship_positions` mapping.

        Raises: Propagets any exception from Board.place_ship() 
        """
        self.__player_board.place_ship(x, y, direction, ship_size)

        # register ship positions so we can map hits to ship instances
        ship = None
        for s in self.__fleet.get_ships():
            if s.get_size() == ship_size:
                ship = s
                break
        if ship is None:
            # Fallback: create a Ship to represent positions (shouldn't happen)
            ship = Ship(ship_size)

        # depending on direction record the positions
        self.__ship_positions[(x, y)] = ship
        if direction == "l":
            for i in range(1, ship_size):
                self.__ship_positions[(x, y - i)] = ship
        elif direction == "r":
            for i in range(1, ship_size):
                self.__ship_positions[(x, y + i)] = ship
        elif direction == "up":
            for i in range(1, ship_size):
                self.__ship_positions[(x - i, y)] = ship
        elif direction == "dn":
            for i in range(1, ship_size):
                self.__ship_positions[(x + i, y)] = ship


    def place_ship(self, ship_position: tuple[int, int], ship_direction: str):
        """Places the ship on its own board"""
        if (self.__all_ships_placed):
            raise Exception("All ships were placed")

        ship = self.__fleet.get_ships()[self.__idx_of_next_ship_to_place]
        x = ship_position[0] 
        y = ship_position[1]
        self.__place_ship(x, y, ship_direction, ship.get_size())

        self.__idx_of_next_ship_to_place += 1
        if self.__idx_of_next_ship_to_place == len(self.__fleet.get_ships()):
            self.__all_ships_placed = True

    def try_hit(self, x, y) -> str:
        """Attempt to mark a hit on our internal opponent board (used for local mode).
        Returns 'miss' or 'hit' or 'already'."""
        return self.__opponent_board.try_hit(x, y)

    def has_undestroyed_ships(self) -> bool:
        return not self.__fleet.destroyed()

    def all_ships_placed(self) -> bool:
        return self.__all_ships_placed

    def receive_fire(self, x: int, y: int) -> str:
        """Process an incoming fire at (x,y) on this player's board and return
        one of: 'miss', 'hit', 'sunk', 'win', 'already'"""
        # TODO: create a new enum for miss/hit/sunk/win/already
        result = self.__player_board.try_hit(x, y)
        if result == 'miss':
            return 'miss'
        if result == 'already':
            return 'already'
        if result == 'hit':
            # find ship object for this coordinate (if any)
            ship: Ship | None = self.__ship_positions.get((x, y), None)
            if ship is not None: # TODO: convert to error
                ship.hit()
                if ship.is_destroyed():
                    if self.__fleet.destroyed():
                        return 'win'
                    return 'sunk'
                return 'hit'
            # if no ship object mapping found, just return 'hit'
            return 'hit'

        # default
        return 'miss'

    def mark_opponent_board(self, x: int, y: int, result: str):
        """Update the local view of the opponent board based on a result."""
        if result in ['miss']:
            self.__opponent_board.set_symbol(x, y, '.')
        elif result in ['hit', 'sunk', 'win']: # TODO: change this to enum too
            self.__opponent_board.set_symbol(x, y, 'X')
        # ignore unknown results

    def get_player_board_matrix(self) -> BoardMatrix:
        return self.__player_board.get_board_matrix()

    def get_opponent_board_matrix(self) -> BoardMatrix:
        return self.__opponent_board.get_board_matrix()