from .board import Board
from .ship import Ship
from .player import Player
from .fleet import Fleet 

class Game:
    def __init__(self, friendly_symbol: str, enemy_symbol: str, board_size: int = 10):
        self.__is_running = False
        self.__setup(friendly_symbol, enemy_symbol, board_size)
    
    def __setup(self, friendly_symbol: str, enemy_symbol: str, board_size: int):
        self.__player1 = Player(Fleet(), friendly_symbol, enemy_symbol, board_size)
        self.__player2 = Player(Fleet(), friendly_symbol, enemy_symbol, board_size)

    def start_game_loop(self):
        if self.__is_running:
            return
        self.__is_running = True

        # first phase (place ships)
        self.__player1.place_ships()
        self.__player2.place_ships()

        # TODO: (in holiday) remove the return so that you can implement the try hit
        return # early return for developing the first part of the game

        # second phase (fight)
        first_players_turn = True
        while True:
            x, y = 1, 1 # this is test data (must be removed)
            #TODO:  get x, y from user
            if first_players_turn:
                self.__player1.try_hit(x, y)
                first_players_turn = False
            else:
                self.__player2.try_hit(x, y)
                first_players_turn = True
            if (self.__is_a_winner()):
                break
        
        # TODO: display the winner

        self.__is_running = False

    def __is_a_winner(self):
        if not self.__player1.has_remaining_ships() or not self.__player2.has_remaining_ships():
            return True
        return False

    def __str__(self):
        return "The game " + ("is" if self.__is_running else "is not") + " running"
