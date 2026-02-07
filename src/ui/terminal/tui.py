from game import Game
# from net.session import NetworkSession

class TerminalUI:
    def __init__(self, game: Game):
        self.game = game
        self.__error_msg: str | None = None

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

    def __game_loop(self):
        # first phase (place ships)
        # for local mode we place ships for both players
        
        print("Players! Place your ships")
        more_ships_to_place = True
        while more_ships_to_place:
            print(self.game.get_player1_boards()[0])
            print(self.game.get_player2_boards()[0])
            self.try_print_error()

            raw = input("Give the coordinates for the ship: ").strip()
            parts = raw.split()
            if (len(parts) < 2):
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
                continue;

            try: 
                more_ships_to_place = self.game.place_ship(ship_location, ship_direction)
            except Exception as e:
                more_ships_to_place = True
                error_msg = str(e)

        # second phase (fight)
        game_over = False
        while not game_over:
            # TODO: implement error handleing for the game part (next time)
            print("Player 1 board:")
            print(self.game.get_player1_boards()[0])
            print("Player 1 opponent's board:")
            print(self.game.get_player1_boards()[1])
            print("Player 2 board:")
            print(self.game.get_player2_boards()[0])
            print("Player 2 opponent's board:")
            print(self.game.get_player2_boards()[1])
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
            p1_board, p1_opp = self.game.get_player1_boards()
            p2_board, p2_opp = self.game.get_player2_boards()
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