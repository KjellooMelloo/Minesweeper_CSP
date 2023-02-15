from minesweeper import Cell


class BasicPatternGenerator:

    def __init__(self, game, solver):
        self.game = game
        self.solver = solver

    def mine_in_corner(self):
        """
        | 0| 0| 0|
        | 0| 1| 1|
        | 0| 1| ?|
        """
        for x in range(self.game.cols):
            for y in range(self.game.rows):
                if x == y == 2:
                    self.game.board[x][y] = Cell(x, y, 9)
                elif x > 0 and y > 0:
                    self.game.board[x][y] = Cell(x, y, 1)
                else:
                    self.game.board[x][y] = Cell(x, y, 0)

        self.game.print()

    def mine_in_center(self):
        """
        | 1| 1| 1|
        | 1| ?| 1|
        | 1| 1| 1|
        """
        for x in range(self.game.cols):
            for y in range(self.game.rows):
                if x == y == 1:
                    self.game.board[x][y] = Cell(x, y, 9)
                else:
                    self.game.board[x][y] = Cell(x, y, 1)
        self.game.print()
        # add upper left corner as hints
        self.solver.cells_to_check.add((1, 0))
        self.solver.cells_to_check.add((0, 1))

    def mines_1_2_2(self):
        """
        | 0| 0| 0|
        | 1| 2| 2|
        | 1| ?| ?|
        """
        self.game.mines = 2
        for x in range(self.game.cols):
            self.game.board[x][0] = Cell(x, 0, 0)

        self.game.board[0][1] = Cell(0, 1, 1)
        self.game.board[0][2] = Cell(0, 2, 1)
        self.game.board[1][1] = Cell(1, 1, 2)
        self.game.board[1][2] = Cell(1, 2, 9)
        self.game.board[2][1] = Cell(2, 1, 2)
        self.game.board[2][2] = Cell(2, 2, 9)

        self.solver.cells_to_check.add((1, 0))
        self.solver.cells_to_check.add((2, 0))

        self.game.print()

    def mines_4(self):
        """
        | 2| ?| 2|
        | ?| 4| ?|
        | 2| ?| ?|
        """
        self.game.mines = 4
        for x in range(self.game.cols):
            for y in range(self.game.rows):
                if x == 1 or y == 1:
                    self.game.board[x][y] = Cell(x, y, 9)
                else:
                    self.game.board[x][y] = Cell(x, y, 2)
        self.game.board[1][1] = Cell(1, 1, 4)
        self.solver.cells_to_check.add((2, 0))
        self.solver.cells_to_check.add((1, 1))
        self.solver.cells_to_check.add((0, 2))

    # from: https://minesweeper.online/help/patterns

    def pattern_b1(self):
        """
        | 0| 0| 0|
        | 2| 3| 2|
        | ?| ?| ?|
        """
        self.game.mines = 3
        for x in range(self.game.cols):
            self.game.board[x][0] = Cell(x, 0, 0)
            self.game.board[x][2] = Cell(x, 2, 9)

        self.game.board[0][1] = Cell(0, 1, 2)
        self.game.board[1][1] = Cell(1, 1, 3)
        self.game.board[2][1] = Cell(2, 1, 2)

        for x in range(self.game.cols):
            for y in range(self.game.rows):
                if y != 2:
                    self.solver.cells_to_check.add((x, y))
        self.game.print()

    def pattern_b2(self):
        """
        | ?| 0| 0|
        | ?| 2| 2|
        | ?| *| *|
        """
        self.game.mines = 2
        self.solver.cells_to_check.remove((0, 0))
        self.game.board[0][0] = Cell(0, 0, 0)
        self.game.board[0][1] = Cell(0, 1, 0)
        self.game.board[0][2] = Cell(0, 2, 0)
        self.game.board[1][0] = Cell(1, 0, 0)
        self.game.board[1][1] = Cell(1, 1, 2)
        self.game.board[1][2] = Cell(1, 2, 9)
        self.game.board[2][0] = Cell(2, 0, 0)
        self.game.board[2][1] = Cell(2, 1, 2)
        self.game.board[2][2] = Cell(2, 2, 9)

        for x in range(self.game.cols):
            for y in range(self.game.rows):
                if x > 0:
                    self.solver.checked.add((x, y))
                    if y < 2:
                        self.solver.domains[(x, y)] = {0}
                        self.solver.values[(x, y)] = 0
                    else:
                        self.solver.domains[(x, y)] = {1}
                        self.solver.values[(x, y)] = 1
        self.game.print()

    def pattern_1_1(self):
        """
        | 0| 0| 0|
        | 1| 1| 1|
        | ?| ?| ?|
        """
        for x in range(self.game.cols):
            for y in range(self.game.rows):
                self.game.board[x][y] = Cell(x, y, y)
        self.game.board[1][2] = Cell(1, 2, 9)
        self.game.print()

    def pattern_1_2(self):
        """
        | 0| 0| 0|
        | 1| 2| 1|
        | ?| ?| ?|
        """
        self.game.mines = 2
        for x in range(self.game.cols):
            self.game.board[x][0] = Cell(x, 0, 0)
            self.game.board[x][2] = Cell(x, 2, 9)

        self.game.board[1][2] = Cell(1, 2, 2)
        self.game.board[0][1] = Cell(0, 1, 1)
        self.game.board[1][1] = Cell(1, 1, 2)
        self.game.board[2][1] = Cell(2, 1, 1)

        for x in range(self.game.cols):
            for y in range(self.game.rows):
                if y != 2:
                    self.solver.cells_to_check.add((x, y))

        self.game.print()
