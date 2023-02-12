class MinesweeperSolver:
    def __init__(self, board, hints):
        self.board = board
        self.hints = hints
        self.variables = []
        for i in range(len(board)):
            for j in range(len(board[0])):
                if board[i][j] != 9:
                    self.variables.append((i, j))

    def ac3(self):
        queue = [(i, j) for i, j in self.variables]
        while queue:
            (i, j) = queue.pop(0)
            if self.remove_inconsistent_values(i, j):
                for x, y in self.neighbors(i, j):
                    queue.append((x, y))

    def remove_inconsistent_values(self, i, j):
        removed = False
        count = 0
        for x, y in self.neighbors(i, j):
            if self.board[x][y] == 9:
                count += 1
        if count != self.board[i][j]:
            self.board[i][j] = 9
            removed = True
        return removed

    def neighbors(self, i, j):
        neighbors = [(i - 1, j - 1), (i - 1, j), (i - 1, j + 1),
                     (i, j - 1), (i, j + 1),
                     (i + 1, j - 1), (i + 1, j), (i + 1, j + 1)]
        return [(x, y) for x, y in neighbors if 0 <= x < len(self.board) and 0 <= y < len(self.board[0])]

    def backtrack(self, index):
        if index == len(self.variables):
            return True
        (i, j) = self.variables[index]
        for value in range(self.board[i][j], 9):
            self.board[i][j] = value
            if self.backtrack(index + 1):
                return True
        self.board[i][j] = self.board[i][j]
        return False

    def solve(self):
        self.ac3()
        if self.backtrack(0):
            return self.board
        else:
            return None


board = [[1, 1, 1, 9, 1],
         [1, 9, 2, 9, 1],
         [1, 9, 2, 9, 1],
         [1, 1, 1, 1, 1],
         [9, 9, 9, 9, 9],
         ]

hints = [(0, 0, 1), (0, 1, 1), (1, 0, 1)]

solver = MinesweeperSolver(board, hints)
result = solver.solve()

if result is not None:
    for row in result:
        print(row)
else:
    print("No solution found.")
