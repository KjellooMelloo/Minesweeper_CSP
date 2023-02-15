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

    def test_corner_mine_success(self):
        self.generator.mine_in_corner()
        self.preconditions()
        self.assertTrue(self.solver.solve())
        self.postconditions()
        self.assertTrue(self.solver.domains[(i, j)] == {0} for i, j in range(3) if i != 2 and j != 2)  # domains correct
        self.assertTrue(self.solver.domains[(2, 2)] == {1})  # mine correct
        self.assertTrue(self.solver.values[(i, j)] == 0 for i, j in range(3) if i != 2 and j != 2)  # values correct
        self.assertTrue(self.solver.values[(2, 2)] == 1)  # mine value correct

    def test_center_mine_success(self):
        self.generator.mine_in_center()
        self.preconditions()
        self.assertTrue(self.solver.solve())
        self.postconditions()
        self.assertTrue(len(self.solver.constraints) == 0)
        self.assertTrue(self.solver.domains[(i, j)] == {0} for i, j in range(3) if i != 1 and j != 1)  # domains correct
        self.assertTrue(self.solver.domains[(1, 1)] == {1})  # mine correct
        self.assertTrue(self.solver.values[(i, j)] == 0 for i, j in range(3) if i != 1 and j != 1)  # values correct
        self.assertTrue(self.solver.values[(1, 1)] == 1)  # mine value correct

    def test_1_2_2_pattern(self):
        self.generator.mines_1_2_2()
        self.preconditions()
        self.assertTrue(self.solver.solve())
        self.postconditions()
        self.assertTrue(len(self.solver.constraints) == 0)
        self.assertTrue(self.solver.domains[(1, 2)] == {1})  # mine correct
        self.assertTrue(self.solver.domains[(2, 2)] == {1})  # mine correct
        self.assertTrue(self.solver.values[(1, 2)] == 1)  # mine value correct
        self.assertTrue(self.solver.values[(2, 2)] == 1)  # mine value correct

    # ----- HELPER ----- #

    def preconditions(self):
        self.assertFalse(all(
            self.solver.is_cell_consistent(x, y) for x, y in self.solver.variables if self.solver.values[(x, y)] != 1))
        self.assertTrue(not any(
            self.solver.is_cell_consistent(x, y) for x, y in self.solver.variables if self.solver.values[(x, y)] != 1))
        self.assertFalse(self.solver.is_solver_consistent())

    def postconditions(self):
        self.assertTrue(all(
            self.solver.is_cell_consistent(x, y) for x, y in self.solver.variables if self.solver.values[(x, y)] != 1))
        self.assertTrue(all(self.solver.values[(x, y)] is not None for x, y in self.solver.variables))
        self.assertTrue(all(len(self.solver.domains[(x, y)]) == 1 for x, y in self.solver.variables))
        self.assertTrue(sum(self.solver.values[(x, y)] for x, y in self.solver.variables) == self.game.mines)
        self.assertTrue(self.solver.is_solver_consistent())
        self.assertTrue(self.game.game_over)
        self.assertTrue(self.game.result == "Won")
