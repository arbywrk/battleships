from dataclasses import dataclass, field

from defaults import default_ship_sizes
from domain.symbol import Symbols


def default_player1_symbols() -> Symbols:
    """Return symbols used for player 1's own board."""
    return Symbols(" ", "🟦", "*", "X")


def default_player2_symbols() -> Symbols:
    """Return symbols used for player 2's own board."""
    return Symbols(" ", "🟩", "*", "X")


def default_player1_opponent_symbols() -> Symbols:
    """Return symbols used for player 1's view of player 2."""
    return Symbols(" ", "🟩", "*", "X")


def default_player2_opponent_symbols() -> Symbols:
    """Return symbols used for player 2's view of player 1."""
    return Symbols(" ", "🟦", "*", "X")


@dataclass
class Settings:
    """Configuration values for the game."""

    board_size: int = 10
    ship_sizes: list[int] = field(default_factory=default_ship_sizes)
    compact_board_rendering: bool = True
    player1_symbols: Symbols = field(default_factory=default_player1_symbols)
    player2_symbols: Symbols = field(default_factory=default_player2_symbols)
    player1_opponent_symbols: Symbols = field(default_factory=default_player1_opponent_symbols)
    player2_opponent_symbols: Symbols = field(default_factory=default_player2_opponent_symbols)
