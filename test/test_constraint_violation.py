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

    def test_trivial_complete(self):
        self.mine_in_corner()
        self.solver.solve()  # trivial game
        # test invalid value for every cell
        self.assertTrue(self.solver.violates_constraints(2, 2, 0))
        self.assertTrue(self.solver.violates_constraints(0, 0, 1))
        self.assertTrue(self.solver.violates_constraints(0, 1, 1))
        self.assertTrue(self.solver.violates_constraints(0, 2, 1))
        self.assertTrue(self.solver.violates_constraints(1, 0, 1))
        self.assertTrue(self.solver.violates_constraints(2, 0, 1))
        self.assertTrue(self.solver.violates_constraints(1, 2, 1))
        self.assertTrue(self.solver.violates_constraints(2, 1, 1))
        self.assertTrue(self.solver.violates_constraints(1, 1, 1))

        self.assertFalse(self.solver.violates_constraints(2, 2, 1))
        self.assertFalse(self.solver.violates_constraints(0, 0, 0))
        self.assertFalse(self.solver.violates_constraints(0, 1, 0))
        self.assertFalse(self.solver.violates_constraints(0, 2, 0))
        self.assertFalse(self.solver.violates_constraints(1, 0, 0))
        self.assertFalse(self.solver.violates_constraints(2, 0, 0))
        self.assertFalse(self.solver.violates_constraints(1, 2, 0))
        self.assertFalse(self.solver.violates_constraints(2, 1, 0))
        self.assertFalse(self.solver.violates_constraints(1, 1, 0))

    def test_trivial_incomplete(self):
        self.mine_in_corner()
        self.solver.solve()  # trivial game
        # pretend lower row is covered
        self.solver.checked.remove(self.game.board[0][2])
        self.solver.checked.remove(self.game.board[1][2])
        # test invalid values for 'covered' cells
        self.assertTrue(self.solver.violates_constraints(0, 2, 1))
        self.assertTrue(self.solver.violates_constraints(1, 2, 1))
        self.assertTrue(self.solver.violates_constraints(2, 2, 0))
        # pretend middle row is covered
        self.solver.checked.remove(self.game.board[0][1])
        self.solver.checked.remove(self.game.board[1][1])
        self.solver.checked.remove(self.game.board[2][1])
        self.assertTrue(self.solver.violates_constraints(0, 1, 1))
        self.assertTrue(self.solver.violates_constraints(1, 1, 1))
        self.assertTrue(self.solver.violates_constraints(2, 1, 1))
        # pretend every cell but middle and top middle are covered
        self.solver.checked.remove(self.game.board[0][0])
        self.solver.checked.remove(self.game.board[2][0])
        self.solver.checked.add(self.game.board[1][1])
        self.assertTrue(self.solver.violates_constraints(0, 0, 1))
        self.assertTrue(self.solver.violates_constraints(0, 1, 1))
        self.assertTrue(self.solver.violates_constraints(2, 0, 1))
        self.assertTrue(self.solver.violates_constraints(2, 1, 1))

    def test_1_2_1_pattern(self):
        self.mines_1_2_1()
        self.solver.cells_to_check.add(self.game.board[1][2])
        self.solver.uncover_cells()
        # (0, 2) and (2, 2) must be mines
        self.assertTrue(self.solver.violates_constraints(0, 2, 0))
        self.assertTrue(self.solver.violates_constraints(2, 2, 0))
        self.assertFalse(self.solver.violates_constraints(0, 2, 1))
        self.assertFalse(self.solver.violates_constraints(2, 2, 1))

        # (1, 2) can't be a mine if (0, 2) is a mine
        self.solver.values[(0, 2)] = 1
        self.assertTrue(self.solver.violates_constraints(1, 2, 1))
        self.assertFalse(self.solver.violates_constraints(1, 2, 0))

        # (1, 2) can't be a mine if (2, 2) is a mine
        self.solver.values[(0, 2)] = None
        self.solver.values[(2, 2)] = 1
        self.assertTrue(self.solver.violates_constraints(1, 2, 1))
        self.assertFalse(self.solver.violates_constraints(1, 2, 0))

    def test_2_3_2_pattern(self):
        self.mines_2_3_2()
        self.solver.uncover_cells()
        # lower row must be mines
        self.assertTrue(self.solver.violates_constraints(0, 2, 0))
        self.assertTrue(self.solver.violates_constraints(1, 2, 0))
        self.assertTrue(self.solver.violates_constraints(2, 2, 0))
        self.assertFalse(self.solver.violates_constraints(0, 2, 1))
        self.assertFalse(self.solver.violates_constraints(1, 2, 1))
        self.assertFalse(self.solver.violates_constraints(2, 2, 1))
        # cover the 2s
        self.solver.checked.remove(self.game.board[0][1])
        self.solver.checked.remove(self.game.board[2][1])
        # check for 2s
        self.assertTrue(self.solver.violates_constraints(0, 1, 1))
        self.assertTrue(self.solver.violates_constraints(2, 1, 1))
        self.assertFalse(self.solver.violates_constraints(0, 1, 0))
        self.assertFalse(self.solver.violates_constraints(2, 1, 0))

    # -------HELPER--------

    def mine_in_corner(self):
        """
        | 0| 0| 0|
        | 0| 1| 1|
        | 0| 1| *|
        """
        self.solver.cells_to_check.remove(self.game.board[0][0])
        for x in range(self.game.cols):
            for y in range(self.game.rows):
                if x == y == 2:
                    self.game.board[x][y] = Cell(x, y, 9)
                elif x > 0 and y > 0:
                    self.game.board[x][y] = Cell(x, y, 1)
                else:
                    self.game.board[x][y] = Cell(x, y, 0)

        self.solver.cells_to_check.add(self.game.board[0][0])
        self.game.print()

    def mines_1_2_1(self): # TODO für solution_validity
        """
        | 0| 0| 0|
        | 1| 2| 1|
        | *| 2| *|
        """
        self.solver.cells_to_check.remove(self.game.board[0][0])
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
                    self.solver.cells_to_check.add(self.game.board[x][y])

        self.game.print()

    def mines_2_3_2(self):
        """
        | 0| 0| 0|
        | 2| 3| 2|
        | *| *| *|
        """
        self.solver.cells_to_check.remove(self.game.board[0][0])
        for x in range(self.game.cols):
            self.game.board[x][0] = Cell(x, 0, 0)
            self.game.board[x][2] = Cell(x, 2, 9)

        self.game.board[0][1] = Cell(0, 1, 2)
        self.game.board[1][1] = Cell(1, 1, 3)
        self.game.board[2][1] = Cell(2, 1, 2)

        for x in range(self.game.cols):
            for y in range(self.game.rows):
                if y != 2:
                    self.solver.cells_to_check.add(self.game.board[x][y])
        self.game.print()
