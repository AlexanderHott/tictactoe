import argparse
import socket
import threading
import typing as t

PlayerT = t.Union[t.Literal["X"], t.Literal["O"]]


class TicTacToe:
    def __init__(self) -> None:
        self.board: list[list[t.Union[PlayerT, t.Literal[" "]]]] = [
            [" ", " ", " "],
            [" ", " ", " "],
            [" ", " ", " "],
        ]  # 3x3
        self.turn: PlayerT = "X"
        self.you: PlayerT = "X"
        self.opponent: PlayerT = "O"
        self.winner: t.Optional[PlayerT] = None
        self.game_over: bool = False

        # turn counter
        self.counter: int = 0

    def host_game(self, host: str, port: int) -> None:
        """Create a server to play on."""
        # Create a server to connect to
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((host, port))
        # listen for incoming connections
        server.listen(1)

        # accept connection
        client, addr = server.accept()

        # assign player tiles
        self.you = "X"
        self.opponent = "O"
        threading.Thread(target=self.handle_connection, args=(client,)).start()
        # close listener, we only need 1 connection
        server.close()

    def connect_to_game(self, host: str, port: int) -> None:
        """Create a client to connect to a game server."""
        # connect to server
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((host, port))

        # assign player tiles
        self.you = "O"
        self.opponent = "X"
        threading.Thread(target=self.handle_connection, args=(client,)).start()

    def handle_connection(self, client: socket.socket) -> None:
        """Main game loop."""
        while not self.game_over:
            if self.turn == self.you:
                move = input("Enter your move (row,col): ")
                if self.check_valid_move(move):
                    self.send_move(
                        client, move
                    )  # send move to opponent before making the move,
                    # because makeing the move might close the connection if you win
                    self.make_move(move, self.you)
                    self.turn = self.opponent
                else:
                    print("Invalid move!\nTry the format 0,0")
            else:
                data = client.recv(1024)
                if not data:
                    break
                else:
                    self.make_move(data.decode("utf-8"), self.opponent)
                    self.turn = self.you
        client.close()  # close connection after there is as winner
        return

    def make_move(self, move: str, player: PlayerT) -> t.Union[None, t.NoReturn]:
        """Assign a tile to the game board."""
        if self.game_over:
            return None
        row, col = move.split(",")  # Move format "row,col"
        self.counter += 1
        self.board[int(row)][int(col)] = player
        self.print_board()
        self.check_for_winner()

        if self.winner == self.you:
            print("You win!")
            exit()
        elif self.winner == self.opponent:
            print("You lose!")
            exit()
        elif self.counter == 9:
            print("Tie!")
            exit()
        return None

    def check_valid_move(self, move: str) -> bool:
        if "," in move:
            row, col = move.split(",")
            if row not in ["0", "1", "2"] or col not in ["0", "1", "2"]:
                return False
            if self.board[int(row)][int(col)] != " ":
                return False
            return True
        return False

    def check_for_winner(self) -> None:
        # magic square, all rows add up to 15
        magic = [[8, 1, 6], [3, 5, 7], [4, 9, 2]]

        # multiply each number by 1 if it is an X,
        # 2 if it is an O, and 0 if it is a blank
        mul = [
            [n * 1 if x == "X" else n * 2 if x == "O" else 0 for x, n in zip(row, mrow)]
            for row, mrow in zip(self.board, magic)
        ]

        # if any row, col, diag adds up to 15, then X is the winner
        if (
            sum(mul[0]) == 15  # row
            or sum(mul[1]) == 15
            or sum(mul[2]) == 15
            or sum(mul[i][0] for i in range(3)) == 15  # col
            or sum(mul[i][1] for i in range(3)) == 15
            or sum(mul[i][2] for i in range(3)) == 15
            or mul[0][0] + mul[1][1] + mul[2][2] == 15  # diag
            or mul[0][2] + mul[1][1] + mul[2][0] == 15
        ):
            self.winner = "X"
            self.game_over = True

        # if any row, col, diag adds up to 30, then O is the winner
        elif (
            sum(mul[0]) == 30
            or sum(mul[1]) == 30
            or sum(mul[2]) == 30
            or sum(mul[i][0] for i in range(3)) == 30
            or sum(mul[i][1] for i in range(3)) == 30
            or sum(mul[i][2] for i in range(3)) == 30
            or mul[0][0] + mul[1][1] + mul[2][2] == 30
            or mul[0][2] + mul[1][1] + mul[2][0] == 30
        ):
            self.winner = "O"
            self.game_over = True

    def print_board(self) -> None:
        print("\n")
        for i, row in enumerate(self.board):
            print(" " + " | ".join(row))
            if i != 2:  # print horizontal line only between rows
                print("-----------")
        print("\n")

    def send_move(self, client, move) -> None:
        client.send(move.encode("utf-8"))


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("connection", nargs=1, help="'host' or 'connect'")
    parser.add_argument("--host", help="host to connect to", default="localhost")
    parser.add_argument("--port", help="port to connect to", default=9999, type=int)

    args = parser.parse_args()

    game = TicTacToe()
    if "host" in args.connection:
        game.host_game(args.host, args.port)
    elif "connect" in args.connection:
        game.connect_to_game(args.host, args.port)
    else:
        print("Invalid connection type. Try 'host' or 'connect'")
