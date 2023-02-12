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

            self.update_constraints(cell)
            if cell.constant == 0:  # uncover neighbors if constant is zero (all safe)
                for n in self.game.get_neighbors(cell.x, cell.y):
                    n_cell = self.board[n[0]][n[1]]
                    if n_cell not in self.checked:
                        self.cells_to_check.add(self.board[n_cell.x][n_cell.y])
                self.uncover_cells()
        return True

    def update_constraints(self, c):
        for x, y in self.game.get_neighbors(c.x, c.y):
            if (x, y) in self.domains:
                self.constraints.add((c.x, c.y, x, y))
                self.constraints.add((x, y, c.x, c.y))

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
                for xi, yi in self.neighbors[(xk, yk)]:
                    if (xi, yi) in self.domains:
                        queue.add((xi, yi, xk, yk))
                if 1 in self.domains[(xk, yk)]:  # must be a mine
                    self.game.flag(xk, yk)
                    self.values[(xk, yk)] = 1
                if 0 in self.domains[(xk, yk)] and self.is_consistent(xk, yk):  # can uncover every cell with value 0
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
        neighbor_const = neighbor.constant

        for val in list(self.domains[(xk, yk)]):
            # if all(self.does_not_conflict(x, y, xk, yk) for y in self.domains[xk, yk]):
            # get amount of 'probably safe' from neighbors of (xm, ym)
            safe_around = len(
                [(x, y) for x, y in self.neighbors[(xm, ym)] if (x, y) in self.domains and 0 in self.domains[(x, y)]])
            # would this value violate the constraint?
            if val + len(self.neighbors[(xm, ym)]) - safe_around > neighbor_const:
                self.domains[(xk, yk)].remove(val)
                revised = True
        return revised

    def does_not_conflict(self, x, y, xk, yk):  # TODO bessere Alternative? Analoger zum Pseudocode
        return x + y <= self.board[xk][yk]

    def backtrack(self):
        if not self.ac3():
            return False

        if all(len(self.domains[(x, y)]) == 1 for x, y in self.variables):
            return self.domains

        unassigned = [(x, y) for x, y in self.variables if len(self.domains[(x, y)]) > 1]
        for x, y in unassigned:
            for value in list(self.domains[(x, y)]):

                self.values[(x, y)] = value
                self.domains[(x, y)] = {value}

                result = self.backtrack()
                if result:
                    return result

                self.values[(x, y)] = None
                self.domains[(x, y)] = {0, 1}

        return False

    def is_consistent(self, x, y):
        return all(self.values[(i, j)] is not None for i, j in self.neighbors[(x, y)]) and sum(
            self.values[(i, j)] for i, j in self.neighbors[(x, y)]) == self.board[x][y]

    def solve(self):
        self.ac3()
        self.backtrack()
