import unicodedata

from domain.board import BoardMatrix, CellValue
from domain.symbol import Symbols
from game import Game
# from net.session import NetworkSession

from enum import StrEnum, auto

class PrintingMode(StrEnum):
    """Enum for printing modes"""
    # Player's boards and the enemy's boards are placed one under another
    ROW_MODE_ALL = auto()

    # Player's boards and the enemy's boards are placed one after another
    COLUMN_MODE_ALL = auto()

    # Each player's own board are placed one under another
    COLUMN_MODE_ONLY_PLAYERS = auto()

    # Each player's opponent's board are placed one under another
    COLUMN_MODE_ONLY_OPPONENTS = auto()


class TerminalUI:
    def __init__(self, game: Game, friendly_symbols: Symbols, enemy_symbols: Symbols):
        self.game = game
        self.__error_msg: str | None = None

        self.__friendly_symbols = friendly_symbols
        self.__enemy_symbols = enemy_symbols

    @staticmethod
    def __get_ship_symbol_width(ship_symbol: str) -> int:
        for ch in ship_symbol:
            ch_is_emoji: bool = unicodedata.east_asian_width(ch) == 'W'
            return 2 if ch_is_emoji else 1
        return 0

    def start(self):
        self.__start_menu()

    def __start_menu(self):
        print("Battleships")
        while True:
            print("1) Local 1v1")
            # print("2) Host network game")
            # print("3) Join network game")
            print("0) Exit")
            choice = input("Choose mode: ")
            if choice == '0':
                break
            elif choice == '1':
                self.__game_loop()
            # ignore for now
            # elif choice == '2':
            #     port = int(input("Port to listen on (e.g. 65432): "))
            #     NetworkSession.host(port, '🟦', '🟥')
            # elif choice == '3':
            #     host = input("Host IP: ")
            #     port = int(input("Port: "))
            #     NetworkSession.join(host, port, '🟦', '🟥')
            else:
                print("Unknown choice")

    def try_print_error(self):
        '''Prints the error message, if one is set, and resets the error_msg to None'''
        if self.__error_msg is not None:
            print(f"Error: {self.__error_msg}")
            self.__error_msg = None

    def set_error_msg(self, error_msg: str):
        self.__error_msg = error_msg

    @staticmethod
    def __printable_board(board_matrix: BoardMatrix, symbols: Symbols) -> str:
        # TODO: implement the entire function for next time
        # TODO EXTRA: make printing work
        max_symbol_width = symbols.max_symbol_width
        border = "-" * (len(board_matrix[0]) * (max_symbol_width + 4))

        fmt_board = ''
        for row in board_matrix:
            fmt_row = ''
            for cell in row:
                # last implementation: fmt_row = '|' + str(row)[1:-1].replace(', ', '|').replace("'", " ") + '|'
                symbol: str = ''
                padding: str = ''
                # you must calculate the padding needed for each value and place its corresponding
                # symbol in the fmt row
                if cell is CellValue.SHIP:
                    symbol = symbols.ship
                    # padding = ...
                if cell is CellValue.MISS:
                    pass
                if cell is CellValue.HIT:
                    pass
                if cell is CellValue.MISS:
                    pass

                # uncomment and complete this line
                # fmt_row += '|' +
                pass
            fmt_board += f'{border}\n{fmt_row}\n'


        fmt_board += border + '\n'
        return fmt_board

    def __print_boards(self, printing_mode: PrintingMode):
        player1_boards = self.game.get_player1_boards_matrix()
        player2_boards = self.game.get_player2_boards_matrix()

        if printing_mode == PrintingMode.COLUMN_MODE_ALL:
            print("Player 1 board:")
            print(TerminalUI.__printable_board(player1_boards[0], self.__friendly_symbols))
            print("Player 1 opponent's board:")
            print(TerminalUI.__printable_board(player1_boards[1], self.__enemy_symbols))
            print("Player 2 board:")
            print(TerminalUI.__printable_board(player2_boards[0], self.__friendly_symbols))
            print("Player 2 opponent's board:")
            print(TerminalUI.__printable_board(player2_boards[1], self.__enemy_symbols))
        elif printing_mode == PrintingMode.ROW_MODE_ALL:
            # TODO: complete
            pass

    def __game_loop(self):
        # first phase (place ships)
        # for local mode we place ships for both players

        printing_setting: PrintingMode = PrintingMode.COLUMN_MODE_ALL

        print("Players! Place your ships")
        more_ships_to_place = True
        while more_ships_to_place:
            # print the boards based on the printing mode
            self.__print_boards(printing_setting)
            self.try_print_error()

            raw = input("Give the coordinates for the ship: ").strip()
            parts = raw.split()
            if len(parts) < 2:
                self.set_error_msg("Two coordinates must be provided")
                continue

            try:
                x = int(parts[0])
                y = int(parts[1])
                ship_location = (x, y)
            except ValueError:
                self.set_error_msg("Invalid coordinates")
                continue
            ship_direction = input("Give the direction of the ship(up, dn, l, r): ").strip()
            if ship_direction not in ['up', 'dn', 'l', 'r']:
                self.set_error_msg("Invalid direction")
                continue

            try: 
                more_ships_to_place = self.game.place_ship(ship_location, ship_direction)
            except Exception as e:
                more_ships_to_place = True
                error_msg = str(e)

        # second phase (fight)
        game_over = False
        while not game_over:
            # TODO: implement error handleing for the game part (next time)
            # TODO: readd board printing
            self.try_print_error()

            raw = input("Give x and y (separated by space): ")
            parts: list[str] = raw.strip().split()
            if len(parts) != 2:
                self.set_error_msg("Invalid input")
                continue
            
            try:
                x = int(parts[0])
                y = int(parts[1])
            except ValueError:
                self.set_error_msg("Invalid value for coordinates")
                continue

            result = self.game.try_hit(x, y)
            print("Result:", result)

            # print boards for both players (for debug / local play)
            # TODO: switch to the __print_board method
            p1_board, p1_opp = self.game.get_player1_boards_matrix()
            p2_board, p2_opp = self.game.get_player2_boards_matrix()
            print("--- Player 1 board ---")
            print(p1_board)
            print("--- Player 1 view of opponent ---")
            print(p1_opp)
            print("--- Player 2 board ---")
            print(p2_board)
            print("--- Player 2 view of opponent ---")
            print(p2_opp)

            game_over: bool = self.game.game_over()

        self.__display_winner()

    def __display_winner(self):
        winner = self.game.get_winner()
        if winner is None:
            print("It's a draw (unexpected)")
        else:
            print(f"Player {winner} won!")