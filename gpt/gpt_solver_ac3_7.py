import random


class MinesweeperSolver:
    def __init__(self, game, starting_point=(0, 0)):
        self.game = game
        self.board = game.board
        self.variables = [(x, y) for x in range(self.game.cols) for y in range(self.game.rows)]  # if board[i][j] == -1]
        self.domains = {(x, y): {0, 1} for x, y in self.variables}
        self.values = {(x, y): None for x, y in self.variables}
        self.constraints = set()
        self.neighbors = {}
        start_x, start_y = starting_point
        self.cells_to_check = set()
        self.cells_to_check.add((start_x, start_y))
        self.checked = set()

        for x, y in self.variables:
            self.neighbors[(x, y)] = self.game.get_neighbors(x, y)
        # for x, y in self.variables:
        # for x2, y2 in self.neighbors[(x, y)]:
        # self.constraints.add((x, y, x2, y2))

    def uncover_cells(self):
        while self.cells_to_check:
            x, y = self.cells_to_check.pop()
            cell = self.board[x][y]
            self.checked.add((x, y))
            if self.game.uncover(x, y):  # game over
                self.update_domains_constraints(x, y)  # update for last cell in case game is won - for consistency
                return

            self.update_domains_constraints(x, y)
            if cell.constant == 0:  # uncover neighbors if constant is zero (all safe)
                for n in self.game.get_neighbors(x, y):
                    nx, ny = n
                    if (nx, ny) not in self.checked:
                        self.cells_to_check.add((nx, ny))
                self.uncover_cells()

    def update_domains_constraints(self, x, y):
        for i, j in self.game.get_neighbors(x, y):
            self.constraints.add((x, y, i, j))
            self.constraints.add((i, j, x, y))
            self.domains[(x, y)] = {0}
            self.values[(x, y)] = 0

    def ac3(self):
        """
        begin
            for i <- 1 until n do NC(i);    unary/ node consistency
            Q <- {(i,j) | (i,j) ∈ arcs(G), i != j}

            while Q not empty do
                begin
                    select and delete any arc (k, m) from Q;
                    if REVISE ((k, m)) then Q <- Q u {(i, k) | (i, k) ∈ arcs(G), i != k, i != m}
            end
        end
        :return: False, when game over (won or lost), True, when no more progress possible yet
        """
        self.uncover_cells()
        queue = self.constraints
        while queue:
            xk, yk, xm, ym = queue.pop()
            if self.revise(xk, yk, xm, ym):
                if (xk, yk) in self.domains and len(self.domains[(xk, yk)]) == 0:  # inconsistent/ no solution
                    return True
                self.values[(xk, yk)] = list(self.domains[(xk, yk)])[0]  # set value
                for xi, yi in self.neighbors[(xk, yk)]:
                    if (xi, yi) in self.domains and (xi, yi, xk, yk) not in queue:
                        queue.add((xi, yi, xk, yk))
                if self.values[(xk, yk)] == 1:
                    self.game.flag(xk, yk)
                if self.is_cell_consistent(xk, yk):  # can uncover every cell with value 0
                    for x, y in self.neighbors[(xk, yk)]:
                        if self.values[(x, y)] == 0 and (x, y) not in self.checked:
                            self.cells_to_check.add((x, y))

        if self.game.game_over:  # first set domains and values before checking for game over, so solver is consistent
            return True
        elif self.cells_to_check:  # can continue
            self.ac3()
        else:  # finished for now
            return False

    def revise(self, xk, yk, xm, ym):
        """
        begin
            DELETE <- false
            for each x ∈ Dk do
                if there is no y ∈ Dm such that Pkm(x, y) then
                    begin
                        delete x from Dk;
                        DELETE <- true
                    end;
            return DELETE
        end
        """
        revised = False
        if (xm, ym) not in self.checked:  # not yet uncovered, so we can't know the constant
            return revised
        # neighbor_const = neighbor.constant
        prev_val = self.values[(xk, yk)]

        for val in list(self.domains[(xk, yk)]):
            # get amount of 'probably safe' from neighbors of (xm, ym)
            # safe_around = len(
            #     [(x, y) for x, y in self.neighbors[(xm, ym)] if (x, y) in self.domains and 0 in self.domains[(x, y)]])
            # # would this value violate the constraint?
            # if val + len(self.neighbors[(xm, ym)]) - safe_around > neighbor_const:
            #     self.domains[(xk, yk)].remove(val)
            #     revised = True
            self.values[(xk, yk)] = val
            if all(self.violates_constraints(xm, ym, mval) for mval in self.domains[xm, ym]):
                self.domains[(xk, yk)].remove(val)
                revised = True
        self.values[(xk, yk)] = prev_val

        return revised

    def violates_constraints(self, x, y, value):
        prev_val = self.values[(x, y)]
        self.values[(x, y)] = value
        for n in self.game.get_neighbors(x, y):
            nx, ny = n
            if (nx, ny) not in self.checked:  # ignore covered cells, because we don't know their constant
                continue
            if not self.meets_constraint(nx, ny):
                self.values[(x, y)] = prev_val
                return True

        self.values[(x, y)] = prev_val
        return False

    def meets_constraint(self, x, y):
        const = self.board[x][y].constant
        num_mines = sum(
            self.values[(i, j)] for i, j in self.neighbors[(x, y)] if self.values[(i, j)] == 1)
        unknown = len([self.values[(i, j)] for i, j in self.neighbors[(x, y)] if
                       self.values[(i, j)] is None])
        # marked = len([self.board[i][j] for i, j in self.neighbors[(i, j)] if self.board[i][j] in self.game.marked])
        if num_mines > const:  # would be too many mines
            return False
        elif unknown < const - num_mines:  # would be too few mines
            return False
        else:
            return True

    def find_solutions(self):
        print("Generating solutions")
        self.unassigned = [(x, y) for x, y in self.variables if len(self.domains[(x, y)]) > 1]
        solutions = self.backtrack([], len(self.unassigned), self.game.mines - len(self.game.marked), [])

        if not solutions:  # no solution found -> pick a random cell to uncover
            rand_x, rand_y = self.unassigned[random.randint(0, len(self.unassigned) - 1)]
            self.cells_to_check.add((rand_x, rand_y))
            print("No solution found, picked random cell: ", rand_x, rand_y)
            return self.solve()

        print("Solutions found: ", len(solutions))
        # sum of values for every solution
        sum_sol = [sum(row[i] for row in solutions) for i in range(len(solutions[0]))]
        any_safe = False
        print("Looking for a safe cell in any solution")
        for i in range(len(sum_sol)):
            if sum_sol[i] == 0:  # safe cell in every solution
                x, y = self.unassigned[i]
                self.cells_to_check.add((x, y))
                any_safe = True
                print("Found safe cell: ", x, y)

        if not any_safe:  # take first solution and add safe cells
            print("No safe cells found. Taking first solution")
            first_sol = solutions[0]
            for i in range(len(first_sol)):
                if first_sol[i] == 0:
                    x, y = self.unassigned[i]
                    self.cells_to_check.add((x, y))

        return self.solve()

    def backtrack(self, assignment, cells_left, mines_left, solutions):  # TODO
        if len(assignment) > cells_left:
            return
        elif sum(assignment) > mines_left:
            return
        else:
            for choice in [0, 1]:  # domain
                assignment.append(choice)
                if sum(assignment) == mines_left and len(assignment) == cells_left:
                    valid = self.is_solution_valid(assignment)
                    if valid:
                        c = assignment.copy()
                        solutions.append(c)
                self.backtrack(assignment, cells_left, mines_left, solutions)
                assignment.pop()
        return solutions

    def is_solution_valid(self, assignment):
        all_valid = True
        for (x, y), value in zip(self.unassigned, assignment):  # set every value and domains
            self.values[(x, y)] = value
            self.domains[(x, y)] = {value}
        for (x, y), value in zip(self.unassigned, assignment):  # check for constraint violations and cell consistency
            all_valid = all_valid and not self.violates_constraints(x, y, value) and self.is_cell_consistent(x, y)

        # after checking validity, reset values and domains
        for (x, y) in self.unassigned:
            self.values[(x, y)] = None
            self.domains[(x, y)] = {None}
        return all_valid

    def is_cell_consistent(self, x, y):
        safe_consistent = all(self.values[(i, j)] is not None for i, j in self.neighbors[(x, y)]) and sum(
            self.values[(i, j)] for i, j in self.neighbors[(x, y)]) == self.board[x][y].constant
        mine_consistent = self.values[(x, y)] == 1 and self.domains[(x, y)] == {1} and self.board[x][y].constant
        return safe_consistent or mine_consistent

    def is_solver_consistent(self):
        """
        Checks if every cell, that is not marked as a mine, is consistent. Then checks that every value is set. Then
        checks if every domain has a size of 1. Then checks that the sum of self.values is equals to amount of mines
        :return: True, when everything is consistent, False else
        """
        return all(self.is_cell_consistent(x, y) for x, y in self.variables if self.values[(x, y)] != 1) and not any(
            self.values[(x, y)] is None for x, y in self.variables) and all(
            len(self.domains[(x, y)]) == 1 for x, y in self.variables) and sum(
            self.values.values()) == self.game.mines

    def solve(self):
        print("Starting solve with AC3 and revise")
        if self.ac3():  # ac3 is finished and game is over
            print("Found solution")
            return self.game.game_over
        if self.is_solver_consistent():
            print("Found solution")
            self.game.game_over = True
            self.game.result = "Won"
            return True

        mines_left = self.game.mines - len(self.game.marked)
        cells_left = self.game.cols * self.game.rows - len(self.game.uncovered) - len(self.game.marked)
        print("Mines left: {}, Cells left: {}".format(str(mines_left), str(cells_left)))
        if mines_left == 0 and cells_left > 0:
            print("No more mines left, can uncover rest of cells")
            for x, y in self.variables:
                if len(self.domains[(x, y)]) > 1:
                    self.cells_to_check.add((x, y))
            return self.ac3()

        return self.find_solutions()
