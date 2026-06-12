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
            print("2) Host online game")
            print("3) Join online game")
            print("0) Exit")

            menu_choice: str = input("Choose: ").strip()
            if menu_choice == "0":
                print("Goodbye!")
                return
            if menu_choice == "1":
                self.__game_loop()
                self.__reset_game()
                continue
            if menu_choice == "2":
                self.__host_online_game()
                continue
            if menu_choice == "3":
                self.__join_online_game()
                continue

            print("Invalid choice, try again.")

    def __host_online_game(self) -> None:
        """Start a local server, join it as player 1, then return to the menu."""
        import threading
        import time

        from network.defaults import DEFAULT_HOST, DEFAULT_PORT
        from network.server import OnlineGameServer

        if not self.__can_host_online_game(DEFAULT_HOST, DEFAULT_PORT):
            print("\nCannot host right now. The online port is already in use.")
            input("Press Enter to return to the menu.")
            return

        server: OnlineGameServer = OnlineGameServer(
            DEFAULT_HOST,
            DEFAULT_PORT,
            self.__settings,
        )
        server_thread = threading.Thread(
            target=self.__run_online_server,
            args=(server,),
            daemon=True,
        )
        server_thread.start()
        time.sleep(0.2)

        print("\nHosting online game.")
        try:
            self.__run_online_client("Could not connect to the hosted game.")
        finally:
            server.stop()

    def __join_online_game(self) -> None:
        """Join a hosted online game, then return to the menu."""
        self.__run_online_client("No online server is running.")

    def __run_online_client(self, unavailable_message: str) -> None:
        """Run the online client and handle failed connection attempts."""
        import socket

        from network.client import OnlineGameClient
        from network.defaults import DEFAULT_HOST, DEFAULT_PORT

        client: OnlineGameClient = OnlineGameClient(
            DEFAULT_HOST,
            DEFAULT_PORT,
            self.__settings,
        )

        try:
            client.start()
        except KeyboardInterrupt:
            print("\nOnline game stopped.")
        except (ConnectionRefusedError, TimeoutError, socket.gaierror, OSError):
            print(f"\n{unavailable_message}")
            input("Press Enter to return to the menu.")

    @staticmethod
    def __run_online_server(server) -> None:
        """Run the server thread without exposing tracebacks to the menu."""
        from network.protocol import ConnectionClosedError

        try:
            server.start()
        except ConnectionClosedError as error:
            print(f"\n{error}")
        except OSError as error:
            print(f"\nOnline server stopped: {error}")

    @staticmethod
    def __can_host_online_game(host: str, port: int) -> bool:
        """Return True when the configured host and port are available."""
        import socket

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe_socket:
                probe_socket.bind((host, port))
        except OSError:
            return False

        return True

    def __reset_game(self) -> None:
        """Create a fresh local game after a completed game."""
        self.__game = Game(self.__settings.board_size, self.__settings.ship_sizes)

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

    def __display_winner(self) -> None:
        """Print the winner after the game ends."""
        winner: int | None = self.__game.get_winner()
        if winner is None:
            print("\nDraw (unexpected state)")
            return

        print(f"\nPlayer {winner} wins!")

    @staticmethod
    def __shot_result_message(shot_result: ShotResult) -> str:
        """Return the message shown after a shot."""
        result_messages: dict[ShotResult, str] = {
            ShotResult.MISS: "Miss!",
            ShotResult.HIT: "Hit!",
            ShotResult.SUNK: "Hit and sunk!",
            ShotResult.WIN: "Hit and sunk - final blow!",
        }
        return result_messages.get(shot_result, str(shot_result))
