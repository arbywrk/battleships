import queue
import socket
import threading
from dataclasses import dataclass

from domain.board import BoardMatrix
from domain.shot_result import ShotResult
from game import Game
from settings import Settings

from .defaults import DEFAULT_HOST, DEFAULT_PORT
from .protocol import ConnectionClosedError, Message, receive_message, send_message


@dataclass
class ClientMessage:
    player_number: int
    message: Message


class ClientHandler(threading.Thread):
    """Reads messages from one client without blocking the game loop."""

    def __init__(
        self,
        player_number: int,
        connection: socket.socket,
        incoming_messages: queue.Queue[ClientMessage],
    ) -> None:
        super().__init__(daemon=True)
        self.player_number: int = player_number
        self.__connection: socket.socket = connection
        self.__incoming_messages: queue.Queue[ClientMessage] = incoming_messages
        self.__send_lock: threading.Lock = threading.Lock()
        self.__closed: bool = False

    def run(self) -> None:
        with self.__connection:
            file = self.__connection.makefile("r", encoding="utf-8")
            while not self.__closed:
                try:
                    message: Message = receive_message(file)
                except (ConnectionClosedError, OSError, ValueError):
                    self.__incoming_messages.put(ClientMessage(
                        self.player_number,
                        {"type": "disconnect"},
                    ))
                    return

                self.__incoming_messages.put(ClientMessage(self.player_number, message))

    def send(self, message: Message) -> None:
        with self.__send_lock:
            send_message(self.__connection, message)

    def close(self) -> None:
        self.__closed = True
        self.__connection.close()


class OnlineGameServer:
    """Hosts one two-player online game using the existing Game object."""

    def __init__(self, host: str, port: int, settings: Settings) -> None:
        self.__host: str = host
        self.__port: int = port
        self.__settings: Settings = settings
        self.__game: Game = Game(settings.board_size, settings.ship_sizes)
        self.__incoming_messages: queue.Queue[ClientMessage] = queue.Queue()
        self.__clients: dict[int, ClientHandler] = {}
        self.__next_request_id: int = 1

    def start(self) -> None:
        """Wait for two clients, then run placement and battle phases."""
        with socket.create_server((self.__host, self.__port), reuse_port=False) as server_socket:
            print(f"Server listening on {self.__host}:{self.__port}")
            self.__accept_players(server_socket)

        try:
            self.__broadcast({"type": "info", "message": "Both players connected. Game starting."})
            self.__placement_phase()
            self.__battle_phase()
        finally:
            self.__close_clients()

    def __accept_players(self, server_socket: socket.socket) -> None:
        for player_number in (1, 2):
            print(f"Waiting for player {player_number}...")
            connection, address = server_socket.accept()
            print(f"Player {player_number} connected from {address[0]}:{address[1]}")

            client: ClientHandler = ClientHandler(
                player_number,
                connection,
                self.__incoming_messages,
            )
            self.__clients[player_number] = client
            client.start()
            client.send({
                "type": "welcome",
                "player": player_number,
                "board_size": self.__settings.board_size,
                "ship_sizes": self.__settings.ship_sizes,
            })

    def __placement_phase(self) -> None:
        more_ships_to_place: bool = True
        message: str | None = None

        while more_ships_to_place:
            player_number: int = self.__game.get_current_player_number()
            ship_size: int | None = self.__game.get_next_ship_size()
            if ship_size is None:
                break

            own_board, _opponent_board = self.__boards_for_player(player_number)
            response: Message = self.__request(player_number, {
                "type": "place_ship",
                "player": player_number,
                "ship_size": ship_size,
                "own_board": self.__serialize_board(own_board),
                "message": message,
            })

            try:
                row, column = self.__read_position(response)
                direction: str = str(response["direction"]).lower()
                more_ships_to_place = self.__game.place_ship((row, column), direction)
                message = None
            except (KeyError, TypeError, ValueError, IndexError) as error:
                message = f"Invalid placement: {error}"

        self.__broadcast({"type": "info", "message": "All ships placed. Battle starting."})

    def __battle_phase(self) -> None:
        message_for_player: dict[int, str | None] = {1: None, 2: None}

        while not self.__game.game_over():
            player_number: int = self.__game.get_current_player_number()
            opponent_number: int = self.__opponent_number(player_number)
            own_board, opponent_board = self.__boards_for_player(player_number)

            response: Message = self.__request(player_number, {
                "type": "fire",
                "player": player_number,
                "own_board": self.__serialize_board(own_board),
                "opponent_board": self.__serialize_board(opponent_board),
                "message": message_for_player[player_number],
            })

            try:
                row, column = self.__read_position(response)
                shot_result: ShotResult = self.__game.try_hit(row, column)
            except (KeyError, TypeError, ValueError, IndexError) as error:
                message_for_player[player_number] = f"Invalid target: {error}"
                continue

            result_message: str = self.__shot_result_message(shot_result)
            message_for_player[player_number] = result_message
            if shot_result == ShotResult.ALREADY_HIT:
                continue

            self.__clients[opponent_number].send({
                "type": "opponent_fired",
                "row": row + 1,
                "column": column + 1,
                "result": shot_result.value,
                "message": f"Opponent fired at row {row + 1}, col {column + 1}: {result_message}",
            })

        winner: int | None = self.__game.get_winner()
        self.__broadcast({"type": "game_over", "winner": winner})

    def __request(self, player_number: int, payload: Message) -> Message:
        request_id: int = self.__next_request_id
        self.__next_request_id += 1
        payload["request_id"] = request_id

        self.__clients[player_number].send(payload)

        while True:
            client_message: ClientMessage = self.__incoming_messages.get()
            message: Message = client_message.message

            if message.get("type") == "disconnect":
                raise ConnectionClosedError(f"Player {client_message.player_number} disconnected")

            if client_message.player_number != player_number:
                continue

            if message.get("request_id") == request_id:
                return message

    def __boards_for_player(self, player_number: int) -> tuple[BoardMatrix, BoardMatrix]:
        if player_number == 1:
            return self.__game.get_player1_boards_matrix()
        return self.__game.get_player2_boards_matrix()

    @staticmethod
    def __read_position(message: Message) -> tuple[int, int]:
        row: int = int(message["row"]) - 1
        column: int = int(message["column"]) - 1
        return row, column

    @staticmethod
    def __serialize_board(board: BoardMatrix) -> list[list[int]]:
        return [[int(cell) for cell in row] for row in board]

    @staticmethod
    def __opponent_number(player_number: int) -> int:
        if player_number == 1:
            return 2
        return 1

    @staticmethod
    def __shot_result_message(shot_result: ShotResult) -> str:
        result_messages: dict[ShotResult, str] = {
            ShotResult.MISS: "Miss!",
            ShotResult.HIT: "Hit!",
            ShotResult.SUNK: "Hit and sunk!",
            ShotResult.WIN: "Hit and sunk - final blow!",
            ShotResult.ALREADY_HIT: "Already targeted that cell.",
        }
        return result_messages[shot_result]

    def __broadcast(self, message: Message) -> None:
        for client in self.__clients.values():
            client.send(message)

    def __close_clients(self) -> None:
        for client in self.__clients.values():
            client.close()


def main() -> None:
    server = OnlineGameServer(DEFAULT_HOST, DEFAULT_PORT, Settings())
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    except ConnectionClosedError as error:
        print(f"\n{error}")


if __name__ == "__main__":
    main()
