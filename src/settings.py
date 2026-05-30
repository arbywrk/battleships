from dataclasses import dataclass, field
from domain.symbol import Symbols


def default_friendly_symbols() -> Symbols:
    return Symbols(' ', '🟦', '*', 'X')


def default_enemy_symbols() -> Symbols:
    return Symbols(' ', '🟥', '*', 'X')


@dataclass
class Settings:
    board_size: int = 10
    compact_board_rendering: bool = True
    friendly_symbols: Symbols = field(default_factory=default_friendly_symbols)
    enemy_symbols: Symbols = field(default_factory=default_enemy_symbols)
