import sys
import termios
import tty
from contextlib import contextmanager
from typing import Iterator


class Key:
    """Names used by the UI after reading keyboard input."""

    ENTER: str = "enter"
    LEFT: str = "left"
    RIGHT: str = "right"
    UP: str = "up"
    DOWN: str = "down"
    ROTATE: str = "rotate"
    OTHER: str = "other"


@contextmanager
def raw_terminal() -> Iterator[None]:
    """
    Temporarily read keys immediately instead of waiting for typed input.

    The original terminal settings are restored even if the game raises an
    error while this mode is active.
    """
    input_file_descriptor: int = sys.stdin.fileno()
    original_terminal_settings: list[object] = termios.tcgetattr(input_file_descriptor)

    try:
        tty.setcbreak(input_file_descriptor)
        yield
    finally:
        termios.tcsetattr(input_file_descriptor, termios.TCSADRAIN, original_terminal_settings)


def read_key() -> str:
    """Read one keyboard action and return one of the values from Key."""
    first_character: str = sys.stdin.read(1)

    if first_character in ("\n", "\r"):
        return Key.ENTER
    if first_character.lower() == "r":
        return Key.ROTATE
    if first_character == "\x1b":
        return __read_arrow_key()

    return Key.OTHER


def __read_arrow_key() -> str:
    """Read the rest of an arrow-key escape sequence."""
    arrow_sequence: str = sys.stdin.read(2)

    if arrow_sequence == "[A":
        return Key.UP
    if arrow_sequence == "[B":
        return Key.DOWN
    if arrow_sequence == "[C":
        return Key.RIGHT
    if arrow_sequence == "[D":
        return Key.LEFT

    return Key.OTHER
