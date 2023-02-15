from unittest import TestCase
from itertools import product

from minesweeper import Minesweeper
from gpt.gpt_solver_ac3_7 import MinesweeperSolver
from BasicPatternGenerator import BasicPatternGenerator


def generate_solutions(valid, size):
    solutions = [p for p in product([0, 1], repeat=size)]
    solutions.remove(tuple(valid))
    return solutions


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

    def test_valid_solution_corner(self):
        self.generator.mine_in_corner()
        self.solver.solve()
        # 'cover' last row and reset domains/ values
        self.solver.checked.remove((0, 2))
        self.solver.checked.remove((1, 2))
        self.solver.domains[(0, 2)] = {0, 1}
        self.solver.domains[(1, 2)] = {0, 1}
        self.solver.domains[(2, 2)] = {0, 1}
        self.solver.values[(0, 2)] = None
        self.solver.values[(1, 2)] = None
        self.solver.values[(2, 2)] = None
        self.solver.unassigned = [(x, y) for x, y in self.solver.variables if len(self.solver.domains[(x, y)]) > 1]
        valid = [0, 0, 1]  # valid solution
        self.assertTrue(self.solver.is_solution_valid(valid))
        # invalid solutions
        solutions = generate_solutions(valid, len(valid))
        for sol in solutions:
            self.assertFalse(self.solver.is_solution_valid(sol))

    def test_valid_solution_corner_only_zeroes(self):
        self.generator.mine_in_corner()
        self.solver.solve()
        # 'cover' last row and reset domains/ values
        self.solver.checked.remove((0, 2))
        self.solver.checked.remove((1, 1))
        self.solver.checked.remove((1, 2))
        self.solver.domains[(0, 2)] = {0, 1}
        self.solver.domains[(1, 1)] = {0, 1}
        self.solver.domains[(1, 2)] = {0, 1}
        self.solver.domains[(2, 2)] = {0, 1}
        self.solver.values[(0, 2)] = None
        self.solver.values[(1, 2)] = None
        self.solver.values[(1, 1)] = None
        self.solver.values[(2, 2)] = None
        self.solver.unassigned = [(x, y) for x, y in self.solver.variables if len(self.solver.domains[(x, y)]) > 1]
        valid = [0, 0, 0, 1]  # valid solution
        self.assertTrue(self.solver.is_solution_valid(valid))
        # invalid solutions
        solutions = generate_solutions(valid, len(valid))
        for sol in solutions:
            self.assertFalse(self.solver.is_solution_valid(sol))

    def test_valid_solution_center(self):
        self.generator.mine_in_center()
        self.solver.solve()
        # 'cover' middle row and reset domains/ values
        self.solver.checked.remove((0, 1))
        self.solver.checked.remove((2, 1))
        self.solver.domains[(0, 1)] = {0, 1}
        self.solver.domains[(1, 1)] = {0, 1}
        self.solver.domains[(2, 1)] = {0, 1}
        self.solver.values[(0, 1)] = None
        self.solver.values[(1, 1)] = None
        self.solver.values[(2, 1)] = None
        self.solver.unassigned = [(x, y) for x, y in self.solver.variables if len(self.solver.domains[(x, y)]) > 1]
        valid = [0, 1, 0]  # valid solution
        self.assertTrue(self.solver.is_solution_valid(valid))
        # invalid solutions
        solutions = generate_solutions(valid, len(valid))
        for sol in solutions:
            self.assertFalse(self.solver.is_solution_valid(sol))
