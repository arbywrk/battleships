from .ship import Ship

class Fleet:
    def __init__(self):
        self.__ships: list[Ship] = [Ship(5), Ship(4), Ship(3), Ship(3), Ship(2)]

    def get_ships(self) -> list[Ship]:
        return self.__ships

    def destroyed(self) -> bool:
        for ship in self.__ships:
            if not ship.is_destroyed():
                return False
        return True
