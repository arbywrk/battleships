from .ship import Ship


class Fleet:
    """The collection of ships owned by one player."""

    def __init__(self, ship_sizes: list[int]) -> None:
        self.__ships: list[Ship] = []
        for ship_size in ship_sizes:
            self.__ships.append(Ship(ship_size))

    def get_ships(self) -> list[Ship]:
        """Return the ships in the order they should be placed."""
        return self.__ships

    def destroyed(self) -> bool:
        """Return True when every ship in the fleet has been destroyed."""
        for ship in self.__ships:
            if not ship.is_destroyed():
                return False
        return True
