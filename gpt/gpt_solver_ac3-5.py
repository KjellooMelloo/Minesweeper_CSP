class MinesweeperSolver:
    def __init__(self, board):
        self.board = board
        self.variables = []
        self.domains = {}
        self.constraints = []
        for i, row in enumerate(board):
            for j, value in enumerate(row):
                if value == 9:
                    continue
                self.variables.append((i, j))
                self.domains[(i, j)] = set(range(10))
                self.domains[(i, j)].remove(9)
                neighbors = []
                if i > 0:
                    neighbors.append((i - 1, j))
                if i < len(board) - 1:
                    neighbors.append((i + 1, j))
                if j > 0:
                    neighbors.append((i, j - 1))
                if j < len(row) - 1:
                    neighbors.append((i, j + 1))
                for x, y in neighbors:
                    if board[x][y] == 9:
                        self.constraints.append((i, j, 9))
        for i, j in self.variables:
            if board[i][j] != 9:
                for x, y in self.variables:
                    if board[x][y] == 9:
                        self.constraints.append((i, j, x, y))

    def revise(self, xi, xj, xk, yk):
        revised = False
        for x in self.domains[(xi, xj)]:
            if x in self.domains[(xk, yk)]:
                self.domains[(xk, yk)].remove(x)
                revised = True
        return revised

    def ac3(self):
        queue = []
        for xi, xj, xk, yk in self.constraints:
            if self.revise(xi, xj, xk, yk):
                if len(self.domains[(xk, yk)]) == 0:
                    return False
                for xl, yl in self.variables:
                    if (xk, yk) != (xl, yl):
                        queue.append((xk, yk, xl, yl))
        return True

    def backtrack(self, assignment=None):
        if assignment is None:
            assignment = {}
        if len(assignment) == len(self.variables):
            return assignment

        unassigned = [var for var in self.variables if var not in assignment]
        first = unassigned[0]

        for value in self.domains[first]:
            temp = assignment.copy()
            temp[first] = value
            if self.ac3():
                result = self.backtrack(temp)
                if result is not None:
                    return result

        return None
