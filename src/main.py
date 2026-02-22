from game import Game
from ui import TerminalUI

#TODO: make a settings class

def main():
    friendly_color = '🟦'
    enemy_color = '🟥'
    board_size = 10
    game = Game(board_size)
    ui = TerminalUI(game, friendly_color, enemy_color)
    ui.start()

if __name__ == "__main__":
    main()
