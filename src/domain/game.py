class Game:
    def __init__(self):
        self.__is_running = False


    def start_game_loop(self):
        self.__is_running = True
        pass

    def __str__(self):
        return "The game " + ("is" if self.__is_running else "is not") + " running"

