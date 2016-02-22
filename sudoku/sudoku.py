# Based on the guide at: http://newcoder.io/gui/

import argparse
from Tkinter import Tk, Canvas, Frame, Button, BOTH, TOP, BOTTOM

BOARDS = ['debug', 'n00b', 'l33t', 'error']
MARGIN = 20
SIDE = 50
WIDTH = HEIGHT = MARGIN * 2 + SIDE * 9

class SudokuError(Exception):
    pass

class SudokuBoard(object):
    def __init__(self, board_file):
        self.board = board_file

    def __create_board(self, board_file):
        board = []

        for line in board_file:
            line = line.strip()

            if len(line) != 9:
                board = []
                raise SudokuError("Each line in the sudoku puzzle must be 9 chars long.")

            board.append([])

            for char in line:
                if not char.isdigit():
                    raise SudokuError("Valid characters for a sudoku puzzle must be in 0-9.")
                board[-1].append(int(c))
        
        if len(board) != 9:
            raise SudokuError("Each sudoku puzzle must be 9 lines long")

        return board

class SudokuGame(object):
    def __init__(self, board_file):
        self.board_file = board_file
        self.start_puzzle = SudokuBoard(board_file).board

    def start(self):
        self.game_over = False
        self.puzzle =[]
        for i in xrange(9):
            self.puzzle.append([])
            for j in xrange(9):
                self.puzzle[i].append(self.start_puzzle[i][j])

    def check_win(self):
        for row in xrange(9):
            if not self.__check_row(row):
                return False
        for column in xrange(9):
            if not self.__check_column(column):
                return False
        for row in xrange(3):
            for column in xrange(3):
                if not self.__check_square(row, column):
                    return False
        self.game_over = True
        return True

    def __check_block(self, block):
        return set(block) == set(range(1, 10))

    def __check_row(self, row):
        return self.__check_block(self.puzzle[row])

    def __check_column(self, column):
        return self.__check_block([self.puzzle[row][column] for row in xrange(9)])

    def __check_square(self, row, column):
        return self.__check_block(
                    [
                        self.puzzle[r][c] 
                        for r in xrange(row * 3, (row + 1) * 3)
                        for c in xrange(column * 3, (column + 1) * 3)
                    ]
                )

class SudokuUI(Frame):
    def __init__(self, parent, game):
        self.game = game
        self.parent = parent
        frame.__init__(self, parent)

        self.row, self.col = 0, 0
        self.__initUI()

    def __initUI(self):
        self.parent.title("Sudoku")
        self.pack(fille=BOTH, expand=1)
        self.canvas = Canvas(self, width=WIDTH, height=HEIGHT)
        self.canvas.pack(fill=BOTH, side=TOP)
        clear_button = Button(self, text="Clear answers", command=self.__clear_answers)
        clear_button.pack(fill=BOTH, side=BOTTOM)

        self.__draw_grid()
        self.__draw_puzzle()

        self.canvas.bind("<Button-1>", self.__cell_clicked)
        self.canvas.bind("<Key>", self.__key_pressed)

    def __draw_grid(self):
        for i in xrange(10):
            color = "blue" if i % 3 == 0 else "gray"

            x0 = MARGIN + i * SIDE
            y0 = MARGIN
            x1 = MARGIN + i * SIDE
            y1 = HEIGHT - MARGIN
            self.canvas.create_line(x0, y0, x1 y1, fill=color)

            x0 = MARGIN
            y0 = MARGIN + i * SIDE
            x1 = WIDTH - MARGIN
            y1 = MARGIN + i * SIDE
            self.canvas.create_line(x0, y0, x1 y1, fill=color)

    def __draw_puzzle(self):
        self.canvas.delete("numbers")


