import os
import sys
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


if os.name == "nt":
    import msvcrt

    @contextmanager
    def raw_terminal() -> Iterator[None]:
        """
        On Windows, msvcrt.getwch() already reads keys immediately,
        so no terminal mode change is needed.
        """
        yield

    def read_key() -> str:
        """Read one keyboard action and return one of the values from Key."""
        first_character: str = msvcrt.getwch()

        if first_character in ("\r", "\n"):
            return Key.ENTER

        if first_character.lower() == "r":
            return Key.ROTATE

        # Windows special keys are returned as a prefix followed by a code.
        if first_character in ("\x00", "\xe0"):
            second_character: str = msvcrt.getwch()
            return _read_windows_special_key(second_character)

        return Key.OTHER

    def _read_windows_special_key(key_code: str) -> str:
        """Translate Windows special-key codes into UI key names."""
        if key_code == "H":
            return Key.UP
        if key_code == "P":
            return Key.DOWN
        if key_code == "K":
            return Key.LEFT
        if key_code == "M":
            return Key.RIGHT

        return Key.OTHER


else:
    import termios
    import tty

    @contextmanager
    def raw_terminal() -> Iterator[None]:
        """
        Temporarily read keys immediately instead of waiting for typed input.

        The original terminal settings are restored even if the game raises an
        error while this mode is active.
        """
        input_file_descriptor: int = sys.stdin.fileno()
        original_terminal_settings: list[object] = termios.tcgetattr(
            input_file_descriptor
        )

        try:
            tty.setcbreak(input_file_descriptor)
            yield
        finally:
            termios.tcsetattr(
                input_file_descriptor,
                termios.TCSADRAIN,
                original_terminal_settings,
            )

    def read_key() -> str:
        """Read one keyboard action and return one of the values from Key."""
        first_character: str = sys.stdin.read(1)

        if first_character in ("\n", "\r"):
            return Key.ENTER

        if first_character.lower() == "r":
            return Key.ROTATE

        if first_character == "\x1b":
            return _read_posix_arrow_key()

        return Key.OTHER

    def _read_posix_arrow_key() -> str:
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
