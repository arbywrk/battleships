import socket
from typing import Any

from domain.board import BoardMatrix, CellValue
from domain.symbol import Symbols
from settings import Settings
from ui.terminal.board_renderer import BoardRenderer

from .defaults import DEFAULT_HOST, DEFAULT_PORT
from .protocol import ConnectionClosedError, Message, receive_message, send_message


class OnlineGameClient:
    """Terminal client for the socket-based online mode."""

    def __init__(self, host: str, port: int, settings: Settings) -> None:
        self.__host: str = host
        self.__port: int = port
        self.__settings: Settings = settings
        self.__player_number: int | None = None

    def start(self) -> None:
        with socket.create_connection((self.__host, self.__port)) as connection:
            print(f"Connected to {self.__host}:{self.__port}")
            print("Waiting for another player...")
            file = connection.makefile("r", encoding="utf-8")

            while True:
                try:
                    message: Message = receive_message(file)
                except ConnectionClosedError:
                    print("Server disconnected.")
                    return

                should_continue: bool = self.__handle_message(connection, message)
                if not should_continue:
                    return

    def __handle_message(self, connection: socket.socket, message: Message) -> bool:
        message_type: str = str(message.get("type"))

        if message_type == "welcome":
            self.__player_number = int(message["player"])
            print(f"You are player {self.__player_number}.")
            return True

        if message_type == "info":
            print(f"\n{message['message']}")
            return True

        if message_type == "place_ship":
            response: Message = self.__prompt_for_ship(message)
            send_message(connection, response)
            return True

        if message_type == "fire":
            response = self.__prompt_for_target(message)
            send_message(connection, response)
            return True

        if message_type == "opponent_fired":
            print(f"\n{message['message']}")
            return True

        if message_type == "game_over":
            winner: Any = message.get("winner")
            if winner == self.__player_number:
                print("\nYou win!")
            else:
                print(f"\nPlayer {winner} wins.")
            return False

        print(f"Unknown server message: {message}")
        return True

    def __prompt_for_ship(self, message: Message) -> Message:
        board: BoardMatrix = self.__deserialize_board(message["own_board"])
        ship_size: int = int(message["ship_size"])

        print("\n=== Place Your Ships ===")
        self.__print_optional_message(message)
        print(BoardRenderer.printable_board(
            board,
            self.__own_symbols(),
            f"Player {self.__player_number}:",
            compact=self.__settings.compact_board_rendering,
        ))
        print(f"Place ship size {ship_size}. Rows and columns are 1-based.")

        row, column = self.__prompt_position("Ship head")
        direction: str = self.__prompt_direction()

        return {
            "type": "place_ship",
            "request_id": message["request_id"],
            "row": row,
            "column": column,
            "direction": direction,
        }

    def __prompt_for_target(self, message: Message) -> Message:
        own_board: BoardMatrix = self.__deserialize_board(message["own_board"])
        opponent_board: BoardMatrix = self.__deserialize_board(message["opponent_board"])

        print("\n=== Battle ===")
        self.__print_optional_message(message)
        print(BoardRenderer.side_by_side(
            BoardRenderer.printable_board(
                own_board,
                self.__own_symbols(),
                "Your board:",
                compact=self.__settings.compact_board_rendering,
            ),
            BoardRenderer.printable_board(
                opponent_board,
                self.__opponent_symbols(),
                "Opponent:",
                compact=self.__settings.compact_board_rendering,
            ),
        ))

        row, column = self.__prompt_position("Target")

        return {
            "type": "fire",
            "request_id": message["request_id"],
            "row": row,
            "column": column,
        }

    @staticmethod
    def __prompt_position(label: str) -> tuple[int, int]:
        row, column = 0, 0
        while True:
            raw_value: str = input(f"{label} row col: ").strip()
            parts: list[str] = raw_value.replace(",", " ").split()
            if len(parts) != 2:
                print("Enter two numbers, for example: 3 7")
                continue

            try:
                row: int = int(parts[0])
                column: int = int(parts[1])
            except ValueError:
                print("Row and column must be numbers.")
                continue

            if row <= 0 or column <= 0:
                print("Rows and columns start at 1.")
                continue

            break
        return row, column

    @staticmethod
    def __prompt_direction() -> str:
        directions: dict[str, str] = {
            "u": "up",
            "up": "up",
            "d": "down",
            "down": "down",
            "l": "left",
            "left": "left",
            "r": "right",
            "right": "right",
        }

        while True:
            raw_value: str = input("Direction (up/down/left/right): ").strip().lower()
            direction: str | None = directions.get(raw_value)
            if direction is not None:
                return direction
            print("Choose up, down, left, or right.")

    def __own_symbols(self) -> Symbols:
        if self.__player_number == 2:
            return self.__settings.player2_symbols
        return self.__settings.player1_symbols

    def __opponent_symbols(self) -> Symbols:
        if self.__player_number == 2:
            return self.__settings.player2_opponent_symbols
        return self.__settings.player1_opponent_symbols

    @staticmethod
    def __deserialize_board(board: list[list[int]]) -> BoardMatrix:
        return [[CellValue(cell) for cell in row] for row in board]

    @staticmethod
    def __print_optional_message(message: Message) -> None:
        optional_message: str | None = message.get("message")
        if optional_message:
            print(optional_message)


def main() -> None:
    client = OnlineGameClient(DEFAULT_HOST, DEFAULT_PORT, Settings())
    try:
        client.start()
    except KeyboardInterrupt:
        print("\nClient stopped.")


if __name__ == "__main__":
    main()