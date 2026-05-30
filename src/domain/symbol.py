import unicodedata
from dataclasses import dataclass


@dataclass
class Symbols:
    """The text symbols used when drawing a board."""

    empty: str
    ship: str
    hit: str
    miss: str

    @staticmethod
    def symbol_width(symbol: str) -> int:
        """Return how many terminal columns a symbol usually needs."""
        if symbol == "":
            return 0

        first_character: str = symbol[0]
        character_is_wide: bool = unicodedata.east_asian_width(first_character) == "W"
        if character_is_wide:
            return 2
        return 1

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
        """Return the widest symbol used by this set."""
        return max(
            self.empty_width,
            self.ship_width,
            self.hit_width,
            self.miss_width,
        )
