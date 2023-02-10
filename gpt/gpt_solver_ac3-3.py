class MinesweeperSolver:
    def __init__(self, board, hints):
        self.board = board
        self.hints = hints
        self.variables = []
        for i in range(len(board)):
            for j in range(len(board[0])):
                if board[i][j] == 0:
                    self.variables.append((i, j))

    def AC3(self):
        queue = [(i, j, k) for i, j in self.variables for k in range(9)]
        while queue:
            (i, j, k) = queue.pop(0)
            if self.remove_inconsistent_values(i, j, k):
                for x, y in self.neighbors(i, j):
                    if self.board[x][y] != 9:
                        queue.append((x, y, int(self.board[x][y])))

    def remove_inconsistent_values(self, i, j, k):
        removed = False
        if k in self.board[i][j]:
            count = 0
            for x, y in self.neighbors(i, j):
                if self.board[x][y] == 9:
                    count += 1
            if count != k:
                self.board[i][j].remove(k)
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
        for value in self.board[i][j]:
            self.board[i][j] = value
            if self.backtrack(index + 1):
                return True
        self.board[i][j] = self.board[i][j][:]
        return False

    def solve(self):
        self.AC3()
        if self.backtrack(0):
            return self.board
        else:
            return None


board = [[0, 0, 0, 0, 0],
         [0, 0, 0, 9, 0],
         [0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0],
         [0, 0, 0, 0, 0],
         ]

hints = [(1, 3, 9), (2, 2, 1), (3, 2, 1), (4, 2, 2), ]

solved_board = MinesweeperSolver(board, hints).solve()

for row in solved_board:
    print(row)
