from .fleet import Fleet
from .board import Board

class Player:
    def __init__(self, fleet: Fleet, friedly_ship_symbol: str, enemy_ship_symbol: str, board_size: int):
        self.__fleet = fleet
        self.__player_board = Board(friedly_ship_symbol, board_size)
        self.__opponent_board = Board(enemy_ship_symbol, board_size)

    #TODO: change direction to an enum (in class)
    def __place_ship(self, x: int, y: int, direction: str, ship_size: int) -> bool:
        """
        Calls the board's method for placing a ship
        
        :param x: the x coordinate where to place the front of the ship
        :param y: the y coordinate where to place the front of the ship
        :param direction: the direction in which the back of the ship will point

        :return bool: True if the placement was successful, False otherwise
        """
        return self.__player_board.place_ship(x, y, direction, ship_size)

    def place_ships(self):
        """Gets the input from the user and places the ships"""
        for ship in self.__fleet.get_ships():
            while True:
                print(self.__player_board.get_printable())
                x = int(input("Give x of head: "))
                y = int(input("Give y of head: "))
                direction = input("Give direction(l, r, up, dn)")
                # TODO: check input validity (in class)
                ok = self.__place_ship(x, y, direction, ship.get_size())
                if ok:
                    break
                print("Can't place ship on the given location")

    def try_hit(self, x, y) -> bool:
        return self.__opponent_board.try_hit(x, y)

    def has_remaining_ships(self) -> bool:
        return not self.__fleet.destroyed()