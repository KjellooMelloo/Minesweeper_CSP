from typing import List, Tuple


class MinesweeperSolver:
    def __init__(self, board: List[List[int]], hints: List[Tuple[int, int, int]]):
        self.board = board
        self.hints = hints
        self.n = len(board)
        self.m = len(board[0])

        # Create a list of variables, each represented as a tuple (i, j)
        self.variables = [(i, j) for i in range(self.n) for j in range(self.m) if self.board[i][j] == 0]

        # Create a list of constraints, where each constraint is a tuple (xi, xj, value)
        # representing that the cell at (xi, xj) must be equal to the value
        self.constraints = []
        for i, j, v in self.hints:
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

    def get_neighbors(self, i, j):
        neighbors = []
        for x in range(i - 1, i + 2):
            for y in range(j - 1, j + 2):
                if 0 <= x < self.n and 0 <= y < self.m and (x, y) != (i, j):
                    neighbors.append((x, y))
        return neighbors

    def ac3(self):
        """
        begin
            for i <- 1 until n do NC(i);    unary/ node consistency
            Q <- {(i,j) | (i,j) e arcs(G), i != j}

            while Q not empty do
                begin
                    select and delete any arc (k, m) from Q;
                    if REVISE ((k, m)) then Q <- Q u {(i, k) | (i, k) e arcs(G), i != k, i != m}
            end
        end
        :return:
        """
        queue = list(self.constraints)
        while queue:
            (xi, xj, value) = queue.pop(0)
            if self.revise(xi, xj, value):
                if len(self.board[xi][xj]) == 0:
                    return False
                for neighbor in self.get_neighbors(xi, xj):
                    if self.board[neighbor[0]][neighbor[1]] != 9:
                        queue.append((neighbor[0], neighbor[1], self.board[neighbor[0]][neighbor[1]]))
        return True

    def revise(self, xi, xj, value):
        """
        begin
            DELETE <- false
            for each x e Di do
                if there is no y e Dj such that Pij(x, y) then
                    begin
                        delete x from Di;
                        DELETE <- true
                    end;
            return DELETE
        end
        """
        revised = False
        count = self.get_neighborhood_mines(xi, xj)
        for x in range(xi - 1, xi + 2):
            for y in range(xj - 1, xj + 2):
                if 0 <= x < self.n and 0 <= y < self.m and self.board[x][y] != 9:
                    if value == '0' and (x, y) in self.variables:
                        self.board[x][y] = '0'
                        self.variables.remove((x, y))
                        revised = True
                    elif value != '0' and self.board[x][y] != '0':
                        if (x, y) in self.variables:
                            self.board[x][y] = str(int(value) - count)
                            revised = True
        return revised

    def solve(self):
        if self.ac3() and self.is_valid():
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
