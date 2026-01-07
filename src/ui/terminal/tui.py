from src.game import Game;

class TerminalUI:
    def __init__(self, game: Game):
        self.game = game

    def start(self):
        self.__start_menu()

    def __start_menu(self):
        print("Battleships")
        input("Press Enter to Start")
        self.__game_loop()

    def __game_loop(self):
        # first phase (place ships)
        self.game.place_ships()

        # second phase (fight)
        game_over = False
        while not game_over:
            x, y = input("Give x and y: ")
            # TODO: validate input
            x = int(x)
            y = int(y)
            self.game.try_hit(x, y)
            game_over = self.game.game_over()
        
        # TODO: display the winner

        self.__display_winner()

    def __display_winner(self):
        pass