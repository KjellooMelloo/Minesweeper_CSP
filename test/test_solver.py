from unittest import TestCase

from minesweeper import Minesweeper, Cell
from gpt.gpt_solver_ac3_7 import MinesweeperSolver
from BoardPatternGenerator import BoardPatternGenerator


class TestMinesweeperSolver(TestCase):
    game = None
    solver = None
    generator = None

    @classmethod
    def setUp(cls) -> None:
        cls.game = Minesweeper(3, 3, 1)
        cls.solver = MinesweeperSolver(cls.game)
        cls.generator = BoardPatternGenerator(cls.game, cls.solver)

    @classmethod
    def tearDown(cls) -> None:
        cls.game = None
        cls.solver = None
        cls.generator = None

    def test_solver_corner_mine_success(self):
        self.generator.mine_in_corner()
        self.assertTrue(self.solver.solve())
        self.assertTrue(self.game.game_over)
        self.assertTrue(self.game.result == "Won")
        self.assertTrue(self.solver.domains[(i, j)] == {0} for i, j in range(3) if i != 2 and j != 2)  # domains correct
        self.assertTrue(self.solver.domains[(2, 2)] == {1})  # mine correct
        self.assertTrue(self.solver.values[(i, j)] == 0 for i, j in range(3) if i != 2 and j != 2)  # values correct
        self.assertTrue(self.solver.values[(2, 2)] == 1)  # mine value correct

    def test_solver_center_mine_success(self):
        self.generator.mine_in_center_plus_hints()
        self.assertTrue(self.solver.solve())
        self.assertTrue(self.game.game_over)
        self.assertTrue(self.game.result == "Won")
        self.assertTrue(len(self.solver.constraints) == 0)
        self.assertTrue(self.solver.domains[(i, j)] == {0} for i, j in range(3) if i != 1 and j != 1)  # domains correct
        self.assertTrue(self.solver.domains[(1, 1)] == {1})  # mine correct
        self.assertTrue(self.solver.values[(i, j)] == 0 for i, j in range(3) if i != 1 and j != 1)  # values correct
        self.assertTrue(self.solver.values[(1, 1)] == 1)  # mine value correct
