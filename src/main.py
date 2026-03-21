from domain.symbol import Symbols
from game import Game
from ui import TerminalUI

#TODO: make a settings class

def main():
    friendly_symbols = Symbols(' ', '🟦', '*', 'X')
    enemy_symbols = Symbols(' ', '🟥', '*', 'X')
    board_size = 10
    game = Game(board_size)
    ui = TerminalUI(game, friendly_symbols, enemy_symbols)
    #ui.start()

if __name__ == "__main__":
    main()
