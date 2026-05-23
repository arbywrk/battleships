from dataclasses import dataclass, field
from domain.symbol import Symbols


@dataclass
class Settings:
    board_size: int = 10
    friendly_symbols: Symbols = field(default_factory=lambda: Symbols(' ', '🟦', '*', 'X'))
    enemy_symbols: Symbols = field(default_factory=lambda: Symbols(' ', '🟥', '*', 'X'))

    # Future network settings would go here:
    # host: str = 'localhost'
    # port: int = 65432
