from enum import StrEnum, auto


class ShotResult(StrEnum):
    MISS = auto()
    HIT = auto()
    SUNK = auto()
    WIN = auto()
    ALREADY_HIT = auto()
