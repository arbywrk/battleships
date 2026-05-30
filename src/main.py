from settings import Settings
from game import Game
from ui import TerminalUI


def main() -> None:
    """Create the game objects and start the terminal UI."""
    settings: Settings = Settings()
    game: Game = Game(settings.board_size, settings.ship_sizes)
    ui: TerminalUI = TerminalUI(game, settings)
    ui.start()


if __name__ == "__main__":
    main()
