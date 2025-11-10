
# TODO: ADD error handling, type hinting, decorators

class Ship:
    """ Impletes the ship class for the battleships game. """
    def __init__(self, size):
        self.__size = size
        self.__is_destroyed = False

    def get_size(self):
        return self.__size

    def is_destroyed(self):
        return self.__is_destroyed

    def hit(self):
        if self.__size == 0:
            return

        self.__size -= 1

        if self.__size == 0:
            self.__destroy()

    def __destroy(self):
        self.__is_destroyed = True

