from minesweeper import Minesweeper, Cell


class MinesweeperSolver:
    """
    Variables X are Cell objects with its values from
    Domain D, consisting of values from 0-8 and
    Constraints C, defined as "value is equal to num neighbors"
    """

    def __init__(self, game=Minesweeper(), starting_point=(0, 0)):
        self.game = game
        self.cells = set()
        self.starting_point = starting_point

    def solve(self):
        self.game.uncover(self.starting_point)  # don't need the return here
        self.initialize_cells()
        # while not self.game.game_over:

    def initialize_cells(self):
        cells = self.game.uncovered

        for cell in cells:
            self.cells.add(Cell(cell.x, cell.y, self.game.board[cell.x][cell.y]))

        # self.constraint = self.value == len(self.neighbors) or self.value == 9

