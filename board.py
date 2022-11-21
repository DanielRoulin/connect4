import numpy as np


class Board:
    def __init__(self):
        self.width = 7
        self.height = 6
        self.board = np.full((self.width, self.height), 0, dtype="u1")
        self.player = 1

        self.last_column = 0
        self.last_line = 0

        self.apparence = {
            0: "::",
            1: "\N{ESC}[41m  \N{ESC}[m",
            2: "\N{ESC}[44m  \N{ESC}[m",
            3: "\N{ESC}[42m  \N{ESC}[m",
        }

    def print(self):
        print(" ".join(map(lambda n: str(n) + "." if n < 10 else str(n), range(1, self.width + 1))))
        for line in reversed(range(self.height)):
            line_str = ""
            for column in range(self.width):
                line_str += self.apparence[self.board[column, line]] + " "
                # line_str += str(self.board[column, line]) + " "
            print(line_str)

    def save(self, path):
        np.savetxt(path, self.board, fmt="%0u")

    def load(self, path):
        self.board = np.loadtxt(path, dtype="u1")

    def set(self, column, line, value):
        self.board[column, line] = value

    def try_input(self, column):
        for line, n in enumerate(self.board[column]):
            if n == 0:
                self.board[column, line] = self.player
                self.player = 2 if self.player == 1 else 1
                self.last_column = column
                self.last_line = line
                return True
        return False

    def check_win(self):
        return self.check_win_at_pos(self.last_column, self.last_line)

    def check_win_at_pos(self, column, line):
        # Vertical
        if line >= 3 :
            potential_col = self.board[column, line-3:line+1]
            if np.all(potential_col == potential_col[0]):
                self.board[column, line-3:line+1] = 3
                return True
        # Horizontal
        streak = 1
        prev = 0
        for i in range(max(0, column-3), min(self.width, column+4)):
            n = self.board[i, line]
            if n == prev and n != 0:
                streak += 1
            else:
                streak = 1
                prev = n
            if streak == 4:
                self.board[[i - j for j in range(4)], line] = 3
                return True
        # First diagonal
        #     #
        #   #
        # #
        start = -min(column, line, 3)
        stop = min(self.width - column, self.height - line, 4)
        streak = 1
        prev = 0
        for i in range(start, stop):
            n = self.board[column + i, line + i]
            if n == prev and n != 0:
                streak += 1
            else:
                streak = 1
                prev = n
            if streak == 4:
                for j in range(i - 3, i + 1):
                    self.board[column + j, line + j] = 3
                return True
        # Second diagonal
        # #
        #   #
        #     #
        start = -min(column, self.height - line -1 , 3)
        stop = min(self.width - column, line + 1, 4)
        streak = 1
        prev = 0
        for i in range(start, stop):
            n = self.board[column + i, line - i]
            if n == prev and n != 0:
                streak += 1
            else:
                streak = 1
                prev = n
            if streak == 4:
                for j in range(i - 3, i + 1):
                    self.board[column + j, line - j] = 3
                return True
        # No win :(
        return False


    def indices_of_win(self, array):
        streak = 1
        prev = 0
        for i, n in enumerate(array):
            if n == prev and n != 0:
                streak += 1
            else:
                streak = 1
                prev = n
            if streak == 4:
                return [i - j for j in range(4)]
        return []


if __name__ == "__main__":
    b = Board()
    # b.set(4, 4, 2)
    b.load("board.out")

    # b.check_win(0, 0)
    b.check_win(6, 0)
    # b.set(4, 4, 1)
    b.print()
