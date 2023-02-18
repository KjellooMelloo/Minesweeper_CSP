import random


class MinesweeperSolver:
    def __init__(self, game, starting_point=(0, 0)):
        self.game = game
        self.board = game.board
        self.variables = [(x, y) for x in range(self.game.cols) for y in range(self.game.rows)]
        self.domains = {(x, y): {0, 1} for x, y in self.variables}  # 0 is safe, 1 is unsafe/ mine
        self.values = {(x, y): None for x, y in self.variables}
        self.constraints = set()
        self.neighbors = {}
        self.unassigned = []
        start_x, start_y = starting_point
        self.cells_to_check = set()
        self.cells_to_check.add((start_x, start_y))
        self.checked = set()
        self.cache = {}  # for efficiency when generating and checking possible solutions

        for x, y in self.variables:
            self.neighbors[(x, y)] = self.game.get_neighbors(x, y)

    def ac3(self):
        """
        ``begin``
            `unary/ node consistency`

            ``for i <- 1 until n do NC(i);``

            ``Q <- {(i,j) | (i,j) ∈ arcs(G), i != j}``

            ``while Q not empty do``
                ``begin``
                    ``select and delete any arc (k, m) from Q;``

                    ``if REVISE ((k, m)) then Q <- Q u {(i, k) | (i, k) ∈ arcs(G), i != k, i != m}``
            ``end``
        ``end``

        :return: False, when game over (won or lost), True, when no more progress possible yet
        """""
        self.uncover_cells()
        queue = self.constraints
        while queue:
            xk, yk, xm, ym = queue.pop()
            if self.revise(xk, yk, xm, ym):
                self.values[(xk, yk)] = list(self.domains[(xk, yk)])[0]  # set value
                for xi, yi in self.neighbors[(xk, yk)]:  # add edges from neighbors to queue
                    if (xi, yi, xk, yk) not in queue:
                        queue.add((xi, yi, xk, yk))
                if self.values[(xk, yk)] == 1:  # if we have a mine, we flag it in game. just for GUI, isn't necessary
                    self.game.flag(xk, yk)
                if self.is_cell_consistent(xk, yk):  # can uncover every neighbor with value 0
                    for x, y in self.neighbors[(xk, yk)]:
                        if self.values[(x, y)] == 0 and (x, y) not in self.checked:
                            self.cells_to_check.add((x, y))

        if self.game.game_over:
            return True
        elif self.cells_to_check:  # can continue
            self.ac3()
        else:  # finished for now
            return False

    def uncover_cells(self):
        """
        Method uncovers cells in ``cells_to_check`` on the minesweeper board and updates domains and constraints for the
        cell. When the cells constant is 0, we can safely add its neighbors to ``cells_to_check`` and uncover them
        aswell. In case the game ends when uncovering a cell (either the last cell or a mine), we update domains and
        constraints for consistency
        """""
        while self.cells_to_check:
            x, y = self.cells_to_check.pop()
            cell = self.board[x][y]
            self.checked.add((x, y))
            if self.game.uncover(x, y):  # game over
                self.update_domains_constraints(x, y)  # update for last cell in case game is over - for consistency
                return

            self.update_domains_constraints(x, y)
            if cell.constant == 0:  # uncover neighbors if constant is zero (all safe)
                for n in self.game.get_neighbors(x, y):
                    nx, ny = n
                    if (nx, ny) not in self.checked:
                        self.cells_to_check.add((nx, ny))
                self.uncover_cells()

    def update_domains_constraints(self, x, y):
        """
        After uncovering a cell, we can update its domains and constraints and values. If we have safely uncovered a
        cell, it is safe, so domain is {0} and value can be set to 0. We also create constraints of the edges between
        this cell and its neighbors

        :param x: x of cell
        :param y: y of cell
        """""
        for i, j in self.game.get_neighbors(x, y):
            self.constraints.add((x, y, i, j))
            self.constraints.add((i, j, x, y))
            self.domains[(x, y)] = {0}
            self.values[(x, y)] = 0

    def revise(self, xk, yk, xm, ym):
        """
        ``begin``
            ``DELETE <- false``

            ``for each x ∈ Dk do``
                ``if there is no y ∈ Dm such that Pkm(x, y) then``
                    ``begin``
                        ``delete x from Dk;``
                        ``DELETE <- true``
                    ``end;``
            ``return DELETE``
        ``end``
        """""
        revised = False
        if (xm, ym) not in self.checked:  # not yet uncovered, so we can't know the constant
            return revised
        prev_val = self.values[(xk, yk)]  # save previous value, so we can reset it after

        for val in list(self.domains[(xk, yk)]):
            self.values[(xk, yk)] = val
            # if there is no y ∈ Dm such that Pkm(x, y)
            if all(self.violates_constraints(xm, ym, mval) for mval in self.domains[xm, ym]):
                self.domains[(xk, yk)].remove(val)
                revised = len(self.domains[(xk, yk)]) > 0
                if not revised:  # domain can get empty by accident - bug?
                    self.domains[(xk, yk)] = {0, 1}
        self.values[(xk, yk)] = prev_val

        return revised

    def violates_constraints(self, x, y, value):
        """
        Method checks, if constraints are violated, when we set ``(x, y)`` to ``value``. Constraints are violated, when
        any neighbor's constraints aren't met (in ``meets_constraints``)

        :param x: x of cell
        :param y: y of cell
        :param value: value to check for
        :return: True, when constraints are violated, False else
        """""
        prev_val = self.values[(x, y)]  # save previous value, so we can reset it after
        self.values[(x, y)] = value
        for n in self.game.get_neighbors(x, y):
            nx, ny = n
            if not self.meets_constraint(nx, ny, (nx, ny) in self.checked):
                self.values[(x, y)] = prev_val
                return True

        self.values[(x, y)] = prev_val
        return False

    def meets_constraint(self, x, y, checked):
        """
        Method checks, if constraints are met for cell at ``(x, y)``. When param ``checked`` is False, it means that
        we can't check this cell, because it isn't uncovered and therefore we don't/ can't know the constant. In that
        case we recursively call this method on uncovered neighbors.

        Possible violations of constraints are, when number of mines (cells with value of 1 in neighbors) would be
        higher than the constant of this cell or when amount of unknown values couldn't meet the amount of mines the
        constant implies (too few mines)

        :param x: x of cell
        :param y: y of cell
        :param checked: True: cell has been checked/ uncovered, False: cell is covered
        :return: True, when constraints are met, False when violated
        """""
        if not checked:
            open_neighbors = [(i, j) for i, j in self.neighbors[(x, y)] if (i, j) in self.checked]
            res = True
            for i, j in open_neighbors:
                res = res and self.meets_constraint(i, j, True)
            return res
        const = self.board[x][y].constant
        num_mines = sum(
            self.values[(i, j)] for i, j in self.neighbors[(x, y)] if self.values[(i, j)] == 1)
        unknown = len([self.values[(i, j)] for i, j in self.neighbors[(x, y)] if
                       self.values[(i, j)] is None])
        if num_mines > const:  # would be too many mines
            return False
        elif unknown < const - num_mines:  # would be too few mines
            return False
        else:
            return True

    def find_solutions(self):
        """
        This gets called when AC3 is finished, but the game isn't over/ solved. It calls ``backtrack`` to generate
        every possible solution for those cells where no value is set. This gets highly complex very fast, so it uses
        a heuristic to reduce search space and complexity (``O(2^n)``). This heuristic is to only take unassigned cells
        which are next to safe ones (those with value of 0) and take a max of 10 of those.

        When no solutions are found, a random cell is picked to uncover next and ``solve()`` gets called again. When
        there is just one solution, we can assign those values and call ``solve()``. When there are multiple solutions,
        we look for safe cells in every solution and add those to ``cells_to_check``. When there aren't any safe cells,
        we take a corner as next cell, because it has the lowest probability to contain a mine, or assign the values
        from the first solution, when no corners are available

        :return: return of solve()
        """""
        print("Generating solutions")
        # heuristic to reduce search space: only take unassigned next to assigned/ safe ones and max length of 10
        self.unassigned = [(x, y) for x, y in self.variables if len(self.domains[(x, y)]) > 1 and any(
            self.values[(i, j)] == 0 for i, j in self.neighbors[(x, y)])][:10]
        are_last_cells = len(self.unassigned) < len(
            [(x, y) for x, y in self.variables if len(self.domains[(x, y)]) > 1])
        solutions = self.backtrack(self.game.mines - len(self.game.marked), are_last_cells)

        if not solutions:  # no solution found -> pick a random cell to uncover
            if not self.unassigned:
                return self.solve()
            self.pick_random_cell()
            return self.solve()

        print("Solutions found: ", len(solutions))
        if len(solutions) == 1:
            print("One solution found. Assigning values")
            self.assign_solution_values(solutions[0])
            return self.solve()

        # look for safe cells in every solution
        any_safe = self.find_safe_cells(solutions)

        if not any_safe:  # take either first solution or a corner
            self.no_safe_cells(solutions)

        return self.solve()

    def backtrack(self, mines_left, last_cells=False):
        """"
        Calls recursive method ``backtrack_helper`` to generate solutions and returns those
        
        :param mines_left: amount of mines left
        :param last_cells: True, when solution for last cells is required. Important for behavior of helper method
        :return: 2D array of solutions
        """""
        return self.backtrack_helper([], mines_left, [], last_cells)

    def backtrack_helper(self, assignment, mines_left, solutions, last_cells=False):
        """
        Generates every possible assignment for the cells in ``unassigned``. Every valid assignment gets saved to
        ``solutions``. When ``last_cells``, the sum of  ``assignment`` has to be equal to ``mines_left``, else it can
        be between 1 and ```mines_left``

        :param assignment: current assignment list for values (0 or 1) of unassigned cells
        :param mines_left: amount of mines left
        :param solutions: list to collect valid assignments
        :param last_cells: True, when we are trying to assign the last cells
        :return: solutions array of valid assignments
        """""
        if len(assignment) > len(self.unassigned):
            return
        elif sum(assignment) > mines_left:
            return
        else:
            for choice in [0, 1]:
                assignment.append(choice)
                # when last cells, it has to be equal to mines_left, else it can be between 1 and mines_left
                if ((last_cells and sum(assignment) == mines_left) or (0 < sum(assignment) <= mines_left)) and len(
                        assignment) == len(self.unassigned):
                    if self.is_solution_valid(assignment):
                        # only keep valid solutions
                        c = assignment.copy()
                        solutions.append(c)
                self.backtrack_helper(assignment, mines_left, solutions)
                assignment.pop()
                self.cache.pop(tuple(assignment), None)  # remove possibly outdated assignment from cache
            return solutions

    def is_solution_valid(self, assignment):
        """
        Checks if ``assignment`` is valid aka it doesn't violate constraints. First we check if the assignment is in
        cache and return it to reduce computation time. Then we assign every value from the assignment and check for
        constraint violation. Then every value (and domain) gets reset, result gets cached and validity of this
        assignment is returned

        :param assignment: assignment of values for unassigned cells to check for
        :return: True, when assignment is valid, False else
        """
        key = tuple(assignment)
        if key in self.cache:
            return self.cache[key]

        all_valid = True
        for (x, y), value in zip(self.unassigned, assignment):  # set every value and domains
            self.values[(x, y)] = value
            self.domains[(x, y)] = {value}
        for (x, y), value in zip(self.unassigned, assignment):  # check for constraint violations and cell consistency
            all_valid = all_valid and not self.violates_constraints(x, y, value)  # and self.is_cell_consistent(x, y)

        # after checking validity, reset values and domains
        for (x, y) in self.unassigned:
            self.values[(x, y)] = None
            self.domains[(x, y)] = {0, 1}
        self.cache[key] = all_valid  # cache the result
        return all_valid

    def pick_random_cell(self):
        """Picks a random cell from ``unassigned`` and adds it to ``cells_to_check``."""""
        rand_x, rand_y = self.unassigned[random.randint(0, len(self.unassigned) - 1)]
        while (rand_x, rand_y) in self.checked:
            rand_x, rand_y = self.unassigned[random.randint(0, len(self.unassigned) - 1)]
        self.cells_to_check.add((rand_x, rand_y))
        print("No solution found, picked random cell: ", rand_x, rand_y)

    def assign_solution_values(self, solution):
        """
        Assigns values from ``solution`` to ``unassigned``, adds the safe cells to ``cells_to_check`` and marks mines.
        
        :param solution: list of values for assignment
        """""
        for i in range(len(solution)):
            x, y = self.unassigned[i]
            if solution[i] == 0 and (x, y) not in self.checked:
                self.cells_to_check.add((x, y))
            else:
                self.domains[(x, y)] = {1}
                self.values[(x, y)] = 1
                self.game.flag(x, y)

    def find_safe_cells(self, solutions):
        """
        Looks for cells, which values are 0 in every generated valid solution in ``solutions``. If there are safe cells,
        the can be added to ``cells_to_check``.

        :param solutions: 2D array of valid assignments
        :return: True, when there have been any safe cells, False else
        """""
        # sum of values for every solution
        sum_sol = [sum(row[i] for row in solutions) for i in range(len(solutions[0]))]
        any_safe = False
        print("Looking for a safe cell in any solution")
        for i in range(len(sum_sol)):
            if sum_sol[i] == 0:  # safe cell in every solution
                x, y = self.unassigned[i]
                if (x, y) not in self.checked:
                    self.cells_to_check.add((x, y))
                    any_safe = True
                    print("Found safe cell: ", x, y)
        return any_safe

    def no_safe_cells(self, solutions):
        """
        When no safe cells have been found, we have to continue somehow. We first look if there are covered corner cells
        and add one to ``cells_to_check``, as they are most probably safe. Else we take the assignment from the first
        solution and add safe cells to ``cells_to_check``
        
        :param solutions: 2D array of valid assignments
        """""
        print("No safe cells found.")
        self.ac3()
        if self.get_corners():
            print("Taking corner")
            self.cells_to_check.add(self.get_corners()[0])
        else:
            print("Taking first solution")
            first_sol = solutions[0]
            for i in range(len(first_sol)):
                if first_sol[i] == 0:
                    x, y = self.unassigned[i]
                    if (x, y) not in self.checked:
                        self.cells_to_check.add((x, y))

    def get_corners(self):
        """
        Collects corner coordinates and returns those, that aren't unsafe (value == 1) and aren't checked
        
        :return: list of valid corners
        """""
        corners = [(0, 0), (0, self.game.rows - 1), (self.game.cols - 1, 0), (self.game.cols - 1, self.game.rows - 1)]
        return [(x, y) for x, y in corners if self.values[(x, y)] != 1 and (x, y) not in self.checked]

    def is_cell_consistent(self, x, y):
        """
        Cell can either be safe- or mine-consistent. Cell is safe-consistent if: every neighbor has a value set AND (
        cell is not yet checked (can't know the constant) OR sum of values of neighbors is equals constant of this
        cell).
        Cell is mine_consistent if: value is set to 1 AND domain is {1}

        :param x: x of cell
        :param y: y of cell
        :return: True, when either safe- or mine-consistent, False else
        """""
        safe_consistent = all(self.values[(i, j)] is not None for i, j in self.neighbors[(x, y)]) and (
                (x, y) not in self.checked or sum(
            self.values[(i, j)] for i, j in self.neighbors[(x, y)]) == self.board[x][y].constant)
        mine_consistent = self.values[(x, y)] == 1 and self.domains[(x, y)] == {1}
        return safe_consistent or mine_consistent

    def is_solver_consistent(self):
        """
        Checks if every cell, that is not marked as a mine, is consistent. Then checks that every value is set. Then
        checks if every domain has a size of 1. Then checks that the sum of self.values is equals to amount of mines

        :return: True, when everything is consistent, False else
        """""
        return all(self.is_cell_consistent(x, y) for x, y in self.variables if self.values[(x, y)] != 1) and not any(
            self.values[(x, y)] is None for x, y in self.variables) and all(
            len(self.domains[(x, y)]) == 1 for x, y in self.variables) and sum(
            self.values.values()) == self.game.mines

    def uncover_and_mark_remaining_cells(self):
        """
        When game is over or solver is consistent, there could still be covered cells. This method collects and uncovers
        those. This is for consistency of solver
        """""
        cells = [(x, y) for x, y in self.variables if self.values[(x, y)] == 0 or self.values[(x, y)] is None]
        for x, y in cells:
            if (x, y) not in self.checked:
                self.game.uncover(x, y)
                self.checked.add((x, y))
        self.constraints = set()

    def solve(self):
        """
        Main method to call on this solver to start solving process.

        1. AC3 algorithm and revise
        2a. game finished by minesweeper rules
        2b. game finished by consistent state of solver
        3a. Every mine is marked, can uncover the rest of the cells --> back to 1.
        3b. find valid solutions by backtracking
        4a. No solution found, uncovering random cell --> back to 1.
        4b. Adding safe cells to uncover, which are 0 in every valid solution
        4c. No safe cells found --> take first of valid solutions as assignment and try
        5. back to 1.

        :return: True, when finished and successful, False else
        """""
        print("Starting solve with AC3 and revise")
        mines_left = self.game.mines - len(self.game.marked)
        cells_left = self.game.cols * self.game.rows - len(self.game.uncovered) - len(self.game.marked)
        print("Mines left: {}, Cells left: {}".format(str(mines_left), str(cells_left)))

        if self.ac3() or self.is_solver_consistent():  # ac3 is finished and game is over or solver is consistent
            print("Game over")
            # for consistency of solver and more convincing GUI
            if self.is_solver_consistent():
                self.game.game_over = True
                self.game.result = "Won"
            if self.game.result == "Won":
                print("Uncovering and marking last cells")
                self.uncover_and_mark_remaining_cells()
            print("Game result: ", self.game.result)
            self.print()
            return self.game.game_over

        mines_left = self.game.mines - len(self.game.marked)
        cells_left = self.game.cols * self.game.rows - len(self.game.uncovered) - len(self.game.marked)
        print("Mines left: {}, Cells left: {}".format(str(mines_left), str(cells_left)))

        if mines_left == 0 and cells_left > 0:
            print("No more mines left, can uncover rest of cells")
            for x, y in self.variables:
                if (x, y) not in self.checked and self.values[(x, y)] != 1:
                    self.cells_to_check.add((x, y))
            return self.ac3()

        return self.find_solutions()

    def print(self):
        """
        Prints a text-based representation of the status of solver.
        Cells marked as safe are printed as 0, mines as 1 and unknown as -
        """""
        print("Solver: \n")
        for x in range(self.game.cols):
            for y in range(self.game.rows):
                if not self.values[(x, y)]:
                    print("|", "-", end="")
                else:
                    print("|", self.values[(x, y)], end="")
            print("|")
