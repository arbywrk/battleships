from enum import StrEnum, auto


class ShotResult(StrEnum):
    """The possible outcomes after a player fires at a cell."""

    MISS = auto()
    HIT = auto()
    SUNK = auto()
    WIN = auto()
    ALREADY_HIT = auto()
