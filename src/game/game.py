from src.domain import Player, Fleet

class Game:
    def __init__(self, friendly_symbol: str, enemy_symbol: str, board_size: int = 10):
        self.__is_running = False
        self.__first_player_turn = True
        self.__setup(friendly_symbol, enemy_symbol, board_size)
    
    def __setup(self, friendly_symbol: str, enemy_symbol: str, board_size: int):
        self.__player1 = Player(Fleet(), friendly_symbol, enemy_symbol, board_size)
        self.__player2 = Player(Fleet(), friendly_symbol, enemy_symbol, board_size)

    def place_ships(self):
        self.__player1.place_ships()
        self.__player2.place_ships()

    def try_hit(self, x: int, y: int):
        if self.__first_player_turn:
            self.__player1.try_hit(x, y)
            self.__first_player_turn = False
        else:
            self.__player2.try_hit(x, y)
            self.__first_player_turn = True

    def game_over(self):
        if not self.__player1.has_remaining_ships() or not self.__player2.has_remaining_ships():
            return True
        return False

    def __str__(self):
        return "The game " + ("is" if self.__is_running else "is not") + " running"
