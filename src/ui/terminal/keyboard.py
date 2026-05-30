import sys
import termios
import tty
from contextlib import contextmanager
from typing import Iterator


class Key:
    ENTER = "enter"
    LEFT = "left"
    RIGHT = "right"
    UP = "up"
    DOWN = "down"
    ROTATE = "rotate"
    OTHER = "other"


@contextmanager
def raw_terminal() -> Iterator[None]:
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        yield
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def read_key() -> str:
    ch = sys.stdin.read(1)
    if ch in ("\n", "\r"):
        return Key.ENTER
    if ch.lower() == "r":
        return Key.ROTATE
    if ch == "\x1b":
        sequence = sys.stdin.read(2)
        if sequence == "[A":
            return Key.UP
        if sequence == "[B":
            return Key.DOWN
        if sequence == "[C":
            return Key.RIGHT
        if sequence == "[D":
            return Key.LEFT
    return Key.OTHER
