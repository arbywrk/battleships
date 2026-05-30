from domain.shot_result import ShotResult
from game import Game
from settings import Settings

from .battle import BattleTargetUI
from .placement import ShipPlacementUI


class TerminalUI:
    def __init__(self, game: Game, settings: Settings):
        self.__game = game
        self.__settings = settings

    def start(self):
        self.__start_menu()

    def __start_menu(self):
        print("=== Battleships ===")
        while True:
            print("\n1) Local 1v1")
            print("0) Exit")
            choice = input("Choose: ").strip()
            if choice == '0':
                print("Goodbye!")
                break
            elif choice == '1':
                self.__game_loop()
            else:
                print("Invalid choice, try again.")

    def __game_loop(self):
        self.__placement_phase()
        self.__battle_phase()

    def __placement_phase(self):
        placement_ui = ShipPlacementUI(
            self.__game,
            self.__settings.friendly_symbols,
            self.__settings.compact_board_rendering,
        )
        more_ships = True
        while more_ships:
            player_num = self.__game.get_current_player_number()
            ship_size = self.__game.get_next_ship_size()
            if ship_size is None:
                break
            more_ships = placement_ui.place_next_ship(player_num, ship_size)

        print("\nAll ships placed!")

    def __battle_phase(self):
        battle_ui = BattleTargetUI(
            self.__game,
            self.__settings.friendly_symbols,
            self.__settings.enemy_symbols,
            self.__settings.compact_board_rendering,
        )
        message = None
        while not self.__game.game_over():
            player_num = self.__game.get_current_player_number()
            result = battle_ui.take_turn(player_num, message)

            result_labels = {
                ShotResult.MISS: "Miss!",
                ShotResult.HIT:  "Hit!",
                ShotResult.SUNK: "Hit and sunk!",
                ShotResult.WIN:  "Hit and sunk — final blow!",
            }
            message = result_labels.get(result, str(result))

        self.__display_winner()

    def __display_winner(self):
        winner = self.__game.get_winner()
        if winner is None:
            print("\nDraw (unexpected state)")
        else:
            print(f"\nPlayer {winner} wins!")
