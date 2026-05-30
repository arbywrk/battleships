class Ship:
    """A ship that can be hit until all of its cells are destroyed."""

    def __init__(self, size: int) -> None:
        if not isinstance(size, int):
            raise TypeError("Ship size must be an integer")
        if size <= 0:
            raise ValueError("Ship size must be positive")

        self.__size: int = size
        self.__remaining_health: int = size

    def get_size(self) -> int:
        """Return the original ship size used during placement."""
        return self.__size

    def is_destroyed(self) -> bool:
        """Return True when this ship has no health left."""
        return self.__remaining_health == 0

    def hit(self) -> None:
        """Remove one health point from the ship."""
        if self.__remaining_health == 0:
            return

        self.__remaining_health -= 1
