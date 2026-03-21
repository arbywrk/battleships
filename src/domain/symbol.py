import unicodedata
from dataclasses import dataclass

@dataclass
class Symbols:
    empty: str
    ship: str
    hit: str
    miss: str

    @staticmethod
    def symbol_width(symbol: str) -> int:
        for ch in symbol:
            ch_is_emoji: bool = unicodedata.east_asian_width(ch) == 'W'
            return 2 if ch_is_emoji else 1
        return 0

    @property
    def empty_width(self) -> int:
        return Symbols.symbol_width(self.empty)

    @property
    def ship_width(self) -> int:
        return Symbols.symbol_width(self.ship)

    @property
    def hit_width(self) -> int:
        return Symbols.symbol_width(self.hit)

    @property
    def miss_width(self) -> int:
        return Symbols.symbol_width(self.miss)

    @property
    def max_symbol_width(self) -> int:
        return max(self.empty_width, self.ship_width, self.hit_width, self.miss_width)

