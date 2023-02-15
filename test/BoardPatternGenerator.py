from minesweeper import Cell


class BoardPatternGenerator:

    def __init__(self, game, solver):
        self.game = game
        self.solver = solver

    def mine_in_corner(self):
        """
        | 0| 0| 0|
        | 0| 1| 1|
        | 0| 1| *|
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

    def mine_in_center_plus_hints(self):
        """
        | 1| 1| 1|
        | 1| *| 1|
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
        | 1| *| *|
        """
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

    def mines_1_2_1(self):  # TODO für solution_validity
        """
        | 0| 0| 0|
        | 1| 2| 1|
        | *| 2| *|
        """
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

        self.solver.cells_to_check.add((1, 2))
        self.game.print()

    def mines_2_3_2(self):
        """
        | 0| 0| 0|
        | 2| 3| 2|
        | *| *| *|
        """
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
