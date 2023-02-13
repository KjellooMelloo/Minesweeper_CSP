import random


class MinesweeperSolver:
    def __init__(self, game, starting_point=(0, 0)):
        self.game = game
        self.board = game.board
        self.variables = [(x, y) for x in range(self.game.cols) for y in range(self.game.rows)]  # if board[x][y] == -1]
        self.domains = {(x, y): {0, 1} for x, y in self.variables}
        self.values = {(x, y): None for x, y in self.variables}
        self.constraints = set()
        self.neighbors = {}
        self.starting_point = starting_point
        self.cells_to_check = set()
        self.cells_to_check.add(self.board[starting_point[0]][starting_point[1]])
        self.checked = set()

        for x, y in self.variables:
            self.neighbors[(x, y)] = self.game.get_neighbors(x, y)
        # for x, y in self.variables:
        # for x2, y2 in self.neighbors[(x, y)]:
        # self.constraints.add((x, y, x2, y2))

    def uncover_cells(self):
        while self.cells_to_check:
            cell = self.cells_to_check.pop()
            self.checked.add(cell)
            if self.game.uncover(cell.x, cell.y):  # game over
                return False

            self.update_domains_constraints(cell)
            if cell.constant == 0:  # uncover neighbors if constant is zero (all safe)
                for n in self.game.get_neighbors(cell.x, cell.y):
                    n_cell = self.board[n[0]][n[1]]
                    if n_cell not in self.checked:
                        self.cells_to_check.add(self.board[n_cell.x][n_cell.y])
                self.uncover_cells()
        return True

    def update_domains_constraints(self, c):
        for x, y in self.game.get_neighbors(c.x, c.y):
            self.constraints.add((c.x, c.y, x, y))
            self.constraints.add((x, y, c.x, c.y))
            self.domains[(c.x, c.y)] = {0}
            self.values[(c.x, c.y)] = 0

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
        :return: False, when inconsistent, True when finished
        """
        if not self.uncover_cells():
            return False
        queue = self.constraints
        while queue:
            xk, yk, xm, ym = queue.pop()
            if self.revise(xk, yk, xm, ym):
                if (xk, yk) in self.domains and len(self.domains[(xk, yk)]) == 0:  # inconsistent/ no solution
                    return False
                self.values[(xk, yk)] = list(self.domains[(xk, yk)])[0]  # set value
                for xi, yi in self.neighbors[(xk, yk)]:
                    if (xi, yi) in self.domains:
                        queue.add((xi, yi, xk, yk))
                if self.values[(xk, yk)] == 1:
                    self.game.flag(xk, yk)
                if self.is_consistent(xk, yk):  # can uncover every cell with value 0
                    for x, y in self.neighbors[(xk, yk)]:
                        if self.values[(x, y)] == 0 and (x, y) not in self.checked:
                            self.cells_to_check.add(self.board[x][y])
        return True

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
        neighbor = self.board[xm][ym]
        if neighbor not in self.checked:  # not yet uncovered, so we can't know the constant
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
            if not any(self.does_not_violate_constraints(xm, ym, mval) for mval in self.domains[xm, ym]):
                self.domains[(xk, yk)].remove(val)
                revised = True
        self.values[(xk, yk)] = prev_val

        return revised

    def does_not_violate_constraints(self, x, y, value):
        prev_val = self.values[(x, y)]
        self.values[(x, y)] = value
        for n in self.game.get_neighbors(x, y):
            nx, ny = n[0], n[1]
            if self.board[nx][ny] not in self.checked:  # ignore covered cells, because we don't know their constant
                continue
            if not self.meets_constraint(nx, ny):
                return False

        self.values[(x, y)] = prev_val
        return True

    def meets_constraint(self, x, y):
        const = self.board[x][y].constant
        num_mines = sum(
            self.values[(i, j)] for i, j in self.neighbors[(x, y)] if self.values[(i, j)] == 1)
        if num_mines > const:  # would be too many mines
            return False
        elif len([self.values[(i, j)] for i, j in self.neighbors[(x, y)] if
                  self.values[(i, j)] is None]) < const - num_mines:  # would be too few mines
            return False
        else:
            return True

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
                # assignment.pop()
        return solutions

    def is_solution_valid(self, assignment):
        all_valid = False
        for cell, value in zip(self.unassigned, assignment):  # TODO
            all_valid = self.does_not_violate_constraints(cell[0], cell[1], value)
        # after checking validity, set the cell's value back to None
        for cell in self.unassigned:
            self.values[(cell[0], cell[1])] = None
        return all_valid

    def is_consistent(self, x, y):
        return all(self.values[(i, j)] is not None for i, j in self.neighbors[(x, y)]) and sum(
            self.values[(i, j)] for i, j in self.neighbors[(x, y)]) == self.board[x][y].constant

    def solve(self):
        if not self.ac3():
            return False

        # TODO eigene Methode
        self.unassigned = [(x, y) for x, y in self.variables if len(self.domains[(x, y)]) > 1]
        solutions = self.backtrack([], len(self.unassigned), self.game.mines - len(self.game.marked), [])

        if not solutions:  # no solution found -> pick a random cell to uncover
            rand_cell = self.unassigned[random.randint(0, len(self.unassigned) - 1)]
            self.cells_to_check.add(self.board[rand_cell[0]][rand_cell[1]])
            return self.solve()

        # sum of values for every solution
        sum_sol = [sum(row[i] for row in solutions) for i in range(len(solutions[0]))]
        any_safe = False
        for i in range(len(sum_sol)):
            if sum_sol[i] == 0:  # safe cell in every solution
                self.cells_to_check.add(self.board[self.unassigned[i][0]][self.unassigned[i][1]])
                any_safe = True

        if not any_safe:  # take first solution and add safe cells
            first_sol = solutions[0]
            for i in range(first_sol):
                if first_sol[i] == 0:
                    self.cells_to_check.add(self.board[self.unassigned[i][0]][self.unassigned[i][1]])

        return self.solve()
