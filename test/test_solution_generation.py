from unittest import TestCase
from itertools import product

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

    def test_pattern_corner_1(self):
        self.generator.pattern_corner_1()
        self.solver.uncover_cells()
        self.solver.unassigned = [(x, y) for x, y in self.solver.variables if
                                  len(self.solver.domains[(x, y)]) > 1 and any(
                                      self.solver.values[(i, j)] == 0 for i, j in self.solver.neighbors[(x, y)])][:10]
        valids = [[0, 0, 1], [0, 1, 0], [1, 0, 0]]
        backtrack_solutions = self.solver.backtrack(1)
        for valid in valids:
            self.assertTrue(self.solver.is_solution_valid(valid))
            self.assertTrue(valid in backtrack_solutions)

    def test_pattern_corner_1_with_2_mines(self):
        self.generator.pattern_corner_1_with_2_mines()
        self.solver.uncover_cells()
        self.solver.unassigned = [(x, y) for x, y in self.solver.variables if
                                  len(self.solver.domains[(x, y)]) > 1 and any(
                                      self.solver.values[(i, j)] == 0 for i, j in self.solver.neighbors[(x, y)])][:10]
        valids = [[0, 0, 1], [0, 1, 0], [1, 0, 0]]
        backtrack_solutions = self.solver.backtrack(2)
        for valid in valids:
            self.assertTrue(self.solver.is_solution_valid(valid))
            self.assertTrue(valid in backtrack_solutions)

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
        valid = [0, 0, 1]  # valid solution
        self.generate_and_test_solutions(valid, len(valid))
        self.assertTrue(len(self.solver.backtrack(1)) == 1)
        self.assertTrue(self.solver.backtrack(1)[0] == valid)

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
        valid = [0, 0, 0, 1]  # valid solution
        self.generate_and_test_solutions(valid, len(valid))
        self.assertTrue(len(self.solver.backtrack(1)) == 1)
        self.assertTrue(self.solver.backtrack(1)[0] == valid)

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
        valid = [0, 1, 0]  # valid solution
        self.generate_and_test_solutions(valid, len(valid))
        self.assertTrue(len(self.solver.backtrack(1)) == 1)
        self.assertTrue(self.solver.backtrack(1)[0] == valid)

    def test_valid_solution_1_2_2(self):
        self.generator.mines_1_2_2()
        self.solver.solve()
        # forget 1s and mines
        self.solver.checked.remove((0, 1))
        self.solver.domains[(0, 1)] = {0, 1}
        self.solver.domains[(0, 2)] = {0, 1}
        self.solver.domains[(1, 2)] = {0, 1}
        self.solver.domains[(2, 2)] = {0, 1}
        self.solver.values[(0, 1)] = None
        self.solver.values[(0, 2)] = None
        self.solver.values[(1, 2)] = None
        self.solver.values[(2, 2)] = None
        valid = [0, 0, 1, 1]  # valid solution
        self.generate_and_test_solutions(valid, len(valid))
        self.assertTrue(len(self.solver.backtrack(2)) == 1)
        self.assertTrue(self.solver.backtrack(2)[0] == valid)

    def test_multiple_valid_solutions_1_2_2_(self):
        self.generator.mines_1_2_2()
        # only uncover 2s
        self.solver.cells_to_check.remove((0, 0))
        self.solver.cells_to_check.remove((1, 0))
        self.solver.cells_to_check.remove((2, 0))
        self.solver.cells_to_check.add((1, 1))
        self.solver.cells_to_check.add((2, 1))
        self.solver.ac3()
        self.solver.unassigned = [(x, y) for x, y in self.solver.variables if
                                  len(self.solver.domains[(x, y)]) > 1 and any(
                                      self.solver.values[(i, j)] == 0 for i, j in self.solver.neighbors[(x, y)])][:10]
        valids = [[0, 0, 0, 1, 1, 0, 0], [0, 0, 0, 1, 0, 1, 0], [0, 0, 0, 1, 0, 0, 1], [0, 0, 0, 0, 1, 1, 0],
                  [0, 0, 0, 0, 1, 0, 1], [0, 0, 0, 0, 0, 1, 1]]  # valid solutions
        backtrack_solutions = self.solver.backtrack(2)
        for valid in valids:
            self.assertTrue(self.solver.is_solution_valid(valid))
            self.assertTrue(valid in backtrack_solutions)

        invalids = [p for p in product([0, 1], repeat=7)]
        for invalid in invalids:
            if list(invalid) not in valids:
                self.assertFalse(self.solver.is_solution_valid(invalid))

        self.assertTrue(len(backtrack_solutions) == len(valids))
        self.assertTrue(sorted(backtrack_solutions) == sorted(valids))

    def test_multiple_valid_solutions_mines_4(self):
        self.generator.mines_4()
        self.solver.cells_to_check.remove((0, 0))
        self.solver.cells_to_check.remove((2, 0))
        self.solver.cells_to_check.remove((1, 1))
        self.solver.cells_to_check.remove((0, 2))
        self.solver.cells_to_check.add((1, 1))
        self.solver.uncover_cells()
        self.solver.unassigned = [(x, y) for x, y in self.solver.variables if
                                  len(self.solver.domains[(x, y)]) > 1 and any(
                                      self.solver.values[(i, j)] == 0 for i, j in self.solver.neighbors[(x, y)])][:10]
        solutions = [p for p in product([0, 1], repeat=8)]
        backtrack_solutions = self.solver.backtrack(4)
        valids = [sol for sol in solutions if sum(sol) == 4]
        for valid in valids:
            self.assertTrue(self.solver.is_solution_valid(valid))
            self.assertTrue(list(valid) in backtrack_solutions)

        invalids = [sol for sol in solutions if sum(sol) != 4]
        for invalid in invalids:
            self.assertFalse(self.solver.is_solution_valid(invalid))

        self.assertTrue(len(backtrack_solutions) == len(valids))
        self.assertTrue(sorted(backtrack_solutions) == sorted([list(valid) for valid in valids]))

    # ----- HELPER -----

    def generate_and_test_solutions(self, valid, size):
        self.solver.unassigned = [(x, y) for x, y in self.solver.variables if
                                  len(self.solver.domains[(x, y)]) > 1 and any(
                                      self.solver.values[(i, j)] == 0 for i, j in self.solver.neighbors[(x, y)])][:10]
        self.assertTrue(self.solver.is_solution_valid(valid))
        solutions = [p for p in product([0, 1], repeat=size)]
        solutions.remove(tuple(valid))
        for sol in solutions:
            self.assertFalse(self.solver.is_solution_valid(sol))
