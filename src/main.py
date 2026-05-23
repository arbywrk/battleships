from settings import Settings
from game import Game
from ui import TerminalUI


def main():
    settings = Settings()
    game = Game(settings.board_size)
    ui = TerminalUI(game, settings)
    ui.start()


if __name__ == "__main__":
    main()
