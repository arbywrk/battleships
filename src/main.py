from game import Game
from ui import TerminalUI

#TODO: make a settings class

def main():
    player1_color = '🟦'
    player2_color = '🟥'
    board_size = 10
    game = Game(player1_color, player2_color, board_size)
    ui = TerminalUI(game) 
    ui.start()

if __name__ == "__main__":
    main()
