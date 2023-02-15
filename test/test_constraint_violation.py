from unittest import TestCase

from minesweeper import Minesweeper
from gpt.gpt_solver_ac3_7 import MinesweeperSolver
from BasicPatternGenerator import BasicPatternGenerator


class TestMinesweeperSolver(TestCase):
    game = None
    solver = None
    generator = None

    @classmethod
    def setUp(cls) -> None:
        cls.game = Minesweeper(3, 3, 1)
        cls.solver = MinesweeperSolver(cls.game)
        cls.generator = BasicPatternGenerator(cls.game, cls.solver)

    @classmethod
    def tearDown(cls) -> None:
        cls.game = None
        cls.solver = None
        cls.generator = None

    def test_trivial_complete(self):
        self.generator.mine_in_corner()
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

        # negative cases
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
        self.generator.mine_in_corner()
        self.solver.solve()  # trivial game
        # pretend lower row is covered
        self.solver.checked.remove((0, 2))
        self.solver.checked.remove((1, 2))
        # test invalid values for 'covered' cells
        self.assertTrue(self.solver.violates_constraints(0, 2, 1))
        self.assertTrue(self.solver.violates_constraints(1, 2, 1))
        self.assertTrue(self.solver.violates_constraints(2, 2, 0))
        # pretend middle row is covered
        self.solver.checked.remove((0, 1))
        self.solver.checked.remove((1, 1))
        self.solver.checked.remove((2, 1))
        self.assertTrue(self.solver.violates_constraints(0, 1, 1))
        self.assertTrue(self.solver.violates_constraints(1, 1, 1))
        self.assertTrue(self.solver.violates_constraints(2, 1, 1))
        # pretend every cell but middle and top middle are covered
        self.solver.checked.remove((0, 0))
        self.solver.checked.remove((2, 0))
        self.solver.checked.add((1, 1))
        self.assertTrue(self.solver.violates_constraints(0, 0, 1))
        self.assertTrue(self.solver.violates_constraints(0, 1, 1))
        self.assertTrue(self.solver.violates_constraints(2, 0, 1))
        self.assertTrue(self.solver.violates_constraints(2, 1, 1))

    def test_1_2_2_pattern(self):
        self.generator.mines_1_2_2()
        self.solver.uncover_cells()
        # (2, 2) and (1, 2) must be mines
        self.assertTrue(self.solver.violates_constraints(1, 2, 0))
        self.assertTrue(self.solver.violates_constraints(2, 2, 0))
        self.assertFalse(self.solver.violates_constraints(2, 2, 1))
        self.assertFalse(self.solver.violates_constraints(2, 2, 1))
        # (0, 2) could be a mine
        self.assertFalse(self.solver.violates_constraints(0, 2, 1))
        self.assertFalse(self.solver.violates_constraints(0, 2, 0))
        # if (1, 2) is a mine, (0, 2) can't be one
        self.solver.values[(1, 2)] = 1
        self.assertTrue(self.solver.violates_constraints(0, 2, 1))
        self.assertFalse(self.solver.violates_constraints(0, 2, 0))

    def test_pattern_1_2(self):
        self.generator.pattern_1_2()
        self.solver.cells_to_check.add((1, 2))
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

    def test_pattern_b1(self):
        self.generator.pattern_b1()
        self.solver.uncover_cells()
        # lower row must be mines
        self.assertTrue(self.solver.violates_constraints(0, 2, 0))
        self.assertTrue(self.solver.violates_constraints(1, 2, 0))
        self.assertTrue(self.solver.violates_constraints(2, 2, 0))
        self.assertFalse(self.solver.violates_constraints(0, 2, 1))
        self.assertFalse(self.solver.violates_constraints(1, 2, 1))
        self.assertFalse(self.solver.violates_constraints(2, 2, 1))
        # cover the 2s
        self.solver.checked.remove((0, 1))
        self.solver.checked.remove((2, 1))
        # check for 2s
        self.assertTrue(self.solver.violates_constraints(0, 1, 1))
        self.assertTrue(self.solver.violates_constraints(2, 1, 1))
        self.assertFalse(self.solver.violates_constraints(0, 1, 0))
        self.assertFalse(self.solver.violates_constraints(2, 1, 0))
