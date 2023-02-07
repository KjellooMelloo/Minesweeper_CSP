from minesweeper import Minesweeper, Cell


class MinesweeperSolver:
    """
    Variables X are Cell objects with its values from
    Domain D, consisting of values 1 (mine) or 0 (no mine) and
    Constraints C, defined as "constant is equal to sum of neighbor variables"
    """

    def __init__(self, game=Minesweeper(), starting_point=(0, 0)):
        self.game = game
        self.cells = set()
        self.starting_point = starting_point

    def solve(self):
        self.game.uncover(self.starting_point.x, self.starting_point.y)  # don't need the return here
        self.cells = self.game.uncovered
        # while len(self.cells) != 0:
            # TODO
