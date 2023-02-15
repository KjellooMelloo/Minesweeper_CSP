from unittest import TestCase

from minesweeper import Minesweeper, Cell
from gpt.gpt_solver_ac3_7 import MinesweeperSolver


class TestMinesweeperSolver(TestCase):
    game = None
    solver = None

    @classmethod
    def setUp(cls) -> None:
        cls.game = Minesweeper(3, 3, 1)
        cls.solver = MinesweeperSolver(cls.game)

    @classmethod
    def tearDown(cls) -> None:
        cls.game = None
        cls.solver = None

    def test_solver_corner_mine_success(self):
        self.mine_in_corner()
        self.assertTrue(self.solver.solve())
        self.assertTrue(self.game.game_over)
        self.assertTrue(self.game.result == "Won")
        self.assertTrue(self.solver.domains[(i, j)] == {0} for i, j in range(3) if i != 2 and j != 2)  # domains correct
        self.assertTrue(self.solver.domains[(2, 2)] == {1})  # mine correct
        self.assertTrue(self.solver.values[(i, j)] == 0 for i, j in range(3) if i != 2 and j != 2)  # values correct
        self.assertTrue(self.solver.values[(2, 2)] == 1)  # mine value correct

    def test_solver_center_mine_success(self):
        self.mine_in_center_plus_hints()
        self.assertTrue(self.solver.solve())
        self.assertTrue(self.game.game_over)
        self.assertTrue(self.game.result == "Won")
        self.assertTrue(len(self.solver.constraints) == 0)
        self.assertTrue(self.solver.domains[(i, j)] == {0} for i, j in range(3) if i != 1 and j != 1)  # domains correct
        self.assertTrue(self.solver.domains[(1, 1)] == {1})  # mine correct
        self.assertTrue(self.solver.values[(i, j)] == 0 for i, j in range(3) if i != 1 and j != 1)  # values correct
        self.assertTrue(self.solver.values[(1, 1)] == 1)  # mine value correct

    # -------HELPER--------

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
