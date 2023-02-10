from typing import List, Tuple


class MinesweeperSolver:
    def __init__(self, board: List[List[int]], hints: List[Tuple[int, int, int]]):
        self.board = board
        self.hints = hints
        self.n = len(board)
        self.m = len(board[0])
        self.variables = [(i, j) for i in range(self.n) for j in range(self.m)]
        self.constraints = []
        for i, j, v in hints:
            self.constraints.append((i, j, str(v)))

    def get_neighborhood_mines(self, i, j):
        count = 0
        for x in range(i - 1, i + 2):
            for y in range(j - 1, j + 2):
                if 0 <= x < self.n and 0 <= y < self.m and self.board[x][y] == 9:
                    count += 1
        return count

    def is_valid(self):
        for i in range(self.n):
            for j in range(self.m):
                if self.board[i][j] != 9 and self.board[i][j] != 0:
                    count = self.get_neighborhood_mines(i, j)
                    if count != int(self.board[i][j]):
                        return False
        return True

    def revise(self, xi, xj, xk, yk):
        revised = False
        for v in self.board[xi][xj]:
            count = self.get_neighborhood_mines(xk, yk)
            if v == 9 and count == int(self.board[xk][yk]):
                self.board[xi][xj].remove(v)
                revised = True
            if v != 9 and count != int(v):
                self.board[xi][xj].remove(v)
                revised = True
        return revised

    def ac3(self):
        queue = []
        for xi, xj, v in self.constraints:
            for xk, yk in self.variables:
                if (xi, xj) != (xk, yk) and self.board[xk][yk] != 9:
                    queue.append((xi, xj, xk, yk))
        while queue:
            xi, xj, xk, yk = queue.pop()
            if self.revise(xi, xj, xk, yk):
                if len(self.board[xk][yk]) == 0:
                    return False
                for xl, yl in self.variables:
                    if (xk, yk) != (xl, yl) and self.board[xl][yl] != 9:
                        queue.append((xl, yl, xk, yk))
        return True

    def solve(self):
        if self.ac3():
            return self.board
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
