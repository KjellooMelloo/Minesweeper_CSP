class MinesweeperSolver:
    def __init__(self, board):
        self.board = board
        self.variables = [(i, j) for i in range(len(board)) for j in range(len(board[0]))]
        self.domains = {var: {0, 1} for var in self.variables}
        self.constraints = []
        for i, row in enumerate(board):
            for j, cell in enumerate(row):
                if cell != 9:
                    for x, y in self.neighbors(i, j):
                        if board[x][y] != 9:
                            self.constraints.append(((i, j), (x, y)))

    def neighbors(self, i, j):
        neighbors = []
        if i > 0:
            neighbors.append((i - 1, j))
        if i < len(self.board) - 1:
            neighbors.append((i + 1, j))
        if j > 0:
            neighbors.append((i, j - 1))
        if j < len(self.board[0]) - 1:
            neighbors.append((i, j + 1))
        return neighbors

    def revise(self, xi, xj, xk, yk):
        revised = False
        for x in self.domains[xi, xj]:
            if all(self.does_not_conflict(x, y, xk, yk) for y in self.domains[xk, yk]):
                revised = True
                break
        if revised:
            self.domains[xi, xj].remove(x)
        return revised

    def does_not_conflict(self, x, y, xk, yk):
        return x + y <= self.board[xk][yk]

    def ac3(self):
        queue = []
        for xi, xj, v in self.constraints:
            for xk, yk in self.variables:
                if (xi, xj) != (xk, yk):
                    queue.append((xi, xj, xk, yk))
        while queue:
            xi, xj, xk, yk = queue.pop()
            if self.revise(xi, xj, xk, yk):
                if len(self.domains[xk, yk]) == 0:
                    return False
                for xl, yl in self.variables:
                    if (xk, yk) != (xl, yl):
                        queue.append((xl, yl, xk, yk))
        return True

    def backtrack(self):
        if not any(len(self.domains[var]) == 0 for var in self.variables):
            return self.domains
        var = min(self.variables, key=lambda var: len(self.domains[var]))
        for value in self.domains[var]:
            assignment = Minesweeper
