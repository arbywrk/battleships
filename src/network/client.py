import socket
from typing import Any

from domain.board import BoardMatrix, CellValue
from settings import Settings
from ui.terminal.battle import BattleTargetSelector
from ui.terminal.placement import ShipPlacementSelector

from .protocol import ConnectionClosedError, Message, receive_message, send_message


class OnlineGameClient:
    """Terminal client for the socket-based online mode."""

    def __init__(self, host: str, port: int, settings: Settings) -> None:
        self.__host: str = host
        self.__port: int = port
        self.__player_number: int | None = None
        self.__placement_selector: ShipPlacementSelector = ShipPlacementSelector(
            settings.player1_symbols,
            settings.player2_symbols,
            settings.compact_board_rendering,
        )
        self.__battle_selector: BattleTargetSelector = BattleTargetSelector(
            settings.player1_symbols,
            settings.player2_symbols,
            settings.player1_opponent_symbols,
            settings.player2_opponent_symbols,
            settings.compact_board_rendering,
        )

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
        player_number: int = self.__require_player_number()
        (row, column), direction = self.__placement_selector.select_ship_position(
            player_number,
            ship_size,
            board,
            message.get("message"),
        )

        return {
            "type": "place_ship",
            "request_id": message["request_id"],
            "row": row + 1,
            "column": column + 1,
            "direction": direction,
        }

    def __prompt_for_target(self, message: Message) -> Message:
        own_board: BoardMatrix = self.__deserialize_board(message["own_board"])
        opponent_board: BoardMatrix = self.__deserialize_board(message["opponent_board"])
        row, column = self.__battle_selector.select_target(
            self.__require_player_number(),
            own_board,
            opponent_board,
            message.get("message"),
        )

        return {
            "type": "fire",
            "request_id": message["request_id"],
            "row": row + 1,
            "column": column + 1,
        }

    def __require_player_number(self) -> int:
        if self.__player_number is None:
            raise RuntimeError("The server has not assigned a player number yet")
        return self.__player_number

    @staticmethod
    def __deserialize_board(board: list[list[int]]) -> BoardMatrix:
        return [[CellValue(cell) for cell in row] for row in board]
