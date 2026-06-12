import json
import socket
from typing import Any


Message = dict[str, Any]

class ConnectionClosedError(ConnectionError):
    """Raised when the remote peer closes the socket."""


def send_message(connection: socket.socket, message: Message) -> None:
    """Send one JSON message followed by a newline."""
    payload: str = json.dumps(message)
    connection.sendall(f"{payload}\n".encode("utf-8"))


def receive_message(file: Any) -> Message:
    """Read one newline-delimited JSON message from a socket file."""
    line: str = file.readline()
    if line == "":
        raise ConnectionClosedError("Connection closed")

    decoded_message = json.loads(line)
    if not isinstance(decoded_message, dict):
        raise ValueError("Expected a JSON object")

    return decoded_message