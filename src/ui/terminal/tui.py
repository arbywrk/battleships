from domain.shot_result import ShotResult
from game import Game
from settings import Settings

from .board_renderer import BoardRenderer
from .placement import ShipPlacementUI


class TerminalUI:
    def __init__(self, game: Game, settings: Settings):
        self.__game = game
        self.__settings = settings
        self.__error_msg: str | None = None

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

    def __print_battle_boards(self, player_num: int):
        if player_num == 1:
            own_board, opp_board = self.__game.get_player1_boards_matrix()
        else:
            own_board, opp_board = self.__game.get_player2_boards_matrix()
        print(BoardRenderer.printable_board(own_board, self.__settings.friendly_symbols, "Your board:"))
        print()
        print(BoardRenderer.printable_board(opp_board, self.__settings.enemy_symbols, "Opponent's board:"))

    def __print_error(self):
        if self.__error_msg is not None:
            print(f"Error: {self.__error_msg}")
            self.__error_msg = None

    def __game_loop(self):
        self.__placement_phase()
        self.__battle_phase()

    def __placement_phase(self):
        placement_ui = ShipPlacementUI(self.__game, self.__settings.friendly_symbols)
        more_ships = True
        while more_ships:
            player_num = self.__game.get_current_player_number()
            ship_size = self.__game.get_next_ship_size()
            if ship_size is None:
                break
            more_ships = placement_ui.place_next_ship(player_num, ship_size)

        print("\nAll ships placed!")

    def __battle_phase(self):
        print("\n=== Battle! ===")
        while not self.__game.game_over():
            player_num = self.__game.get_current_player_number()
            print(f"\nPlayer {player_num}'s turn")
            self.__print_battle_boards(player_num)
            print()
            self.__print_error()

            raw = input("Target  Row  Col (e.g. 3 5): ").strip()
            parts = raw.split()
            if len(parts) != 2:
                self.__error_msg = "Provide exactly row and col — e.g. '3 5'"
                continue

            try:
                x = int(parts[0])
                y = int(parts[1])
            except ValueError:
                self.__error_msg = "Row and col must be whole numbers"
                continue

            result = self.__game.try_hit(x, y)

            if result == ShotResult.ALREADY_HIT:
                self.__error_msg = "Already targeted that cell — pick another"
                continue

            result_labels = {
                ShotResult.MISS: "Miss!",
                ShotResult.HIT:  "Hit!",
                ShotResult.SUNK: "Hit and sunk!",
                ShotResult.WIN:  "Hit and sunk — final blow!",
            }
            print(result_labels.get(result, str(result)))

        self.__display_winner()

    def __display_winner(self):
        winner = self.__game.get_winner()
        if winner is None:
            print("\nDraw (unexpected state)")
        else:
            print(f"\nPlayer {winner} wins!")
