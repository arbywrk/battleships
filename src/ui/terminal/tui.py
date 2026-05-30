from domain.shot_result import ShotResult
from game import Game
from settings import Settings

from .battle import BattleTargetUI
from .placement import ShipPlacementUI


class TerminalUI:
    """The main terminal interface for the game."""

    def __init__(self, game: Game, settings: Settings) -> None:
        self.__game: Game = game
        self.__settings: Settings = settings

    def start(self) -> None:
        """Start the menu shown when the program opens."""
        self.__start_menu()

    def __start_menu(self) -> None:
        """Show the menu until the user starts a game or exits."""
        print("=== Battleships ===")

        while True:
            print("\n1) Local 1v1")
            print("0) Exit")

            menu_choice: str = input("Choose: ").strip()
            if menu_choice == "0":
                print("Goodbye!")
                return
            if menu_choice == "1":
                self.__game_loop()
                return

            print("Invalid choice, try again.")

    def __game_loop(self) -> None:
        """Run the two main game phases in order."""
        self.__placement_phase()
        self.__battle_phase()

    def __placement_phase(self) -> None:
        """Let both players place all ships."""
        placement_ui: ShipPlacementUI = ShipPlacementUI(
            self.__game,
            self.__settings.player1_symbols,
            self.__settings.player2_symbols,
            self.__settings.compact_board_rendering,
        )

        more_ships_to_place: bool = True
        while more_ships_to_place:
            current_player_number: int = self.__game.get_current_player_number()
            next_ship_size: int | None = self.__game.get_next_ship_size()

            if next_ship_size is None:
                break

            more_ships_to_place = placement_ui.place_next_ship(current_player_number, next_ship_size)

        print("\nAll ships placed!")

    def __battle_phase(self) -> None:
        """Let players fire at each other until one player wins."""
        battle_ui: BattleTargetUI = BattleTargetUI(
            self.__game,
            self.__settings.player1_symbols,
            self.__settings.player2_symbols,
            self.__settings.player1_opponent_symbols,
            self.__settings.player2_opponent_symbols,
            self.__settings.compact_board_rendering,
        )
        message_for_next_turn: str | None = None

        while not self.__game.game_over():
            current_player_number: int = self.__game.get_current_player_number()
            shot_result: ShotResult = battle_ui.take_turn(current_player_number, message_for_next_turn)
            message_for_next_turn = self.__shot_result_message(shot_result)

        self.__display_winner()

    def __shot_result_message(self, shot_result: ShotResult) -> str:
        """Return the message shown after a shot."""
        result_messages: dict[ShotResult, str] = {
            ShotResult.MISS: "Miss!",
            ShotResult.HIT: "Hit!",
            ShotResult.SUNK: "Hit and sunk!",
            ShotResult.WIN: "Hit and sunk - final blow!",
        }
        return result_messages.get(shot_result, str(shot_result))

    def __display_winner(self) -> None:
        """Print the winner after the game ends."""
        winner: int | None = self.__game.get_winner()
        if winner is None:
            print("\nDraw (unexpected state)")
            return

        print(f"\nPlayer {winner} wins!")
