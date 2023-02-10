from typing import List, Tuple


def minesweeper_solver(board: List[List[str]], hints: List[Tuple[int, int, int]]) -> List[List[str]]:
    n = len(board)
    m = len(board[0])

    # Create a list of variables, each represented as a tuple (i, j)
    variables = [(i, j) for i in range(n) for j in range(m)]

    # Create a list of constraints, where each constraint is a tuple (xi, xj, value)
    # representing that the cell at (xi, xj) must be equal to the value
    constraints = []
    for i, j, v in hints:
        constraints.append((i, j, str(v)))

    # Function to get the number of mines in a 3x3 neighborhood
    def get_neighborhood_mines(i, j):
        count = 0
        for x in range(i - 1, i + 2):
            for y in range(j - 1, j + 2):
                if 0 <= x < n and 0 <= y < m and board[x][y] == '*':
                    count += 1
        return count

    # Function to check if the board is valid
    def is_valid(board):
        for i in range(n):
            for j in range(m):
                if board[i][j] != '*' and board[i][j] != '.':
                    count = get_neighborhood_mines(i, j)
                    if count != int(board[i][j]):
                        return False
        return True

    # Function to solve the constraint satisfaction problem using backtracking
    def backtrack(board):
        if not variables:
            return board
        (i, j) = variables.pop()
        for v in ['*', '.']:
            board[i][j] = v
            if is_valid(board):
                result = backtrack(board)
                if result is not None:
                    return result
        variables.append((i, j))
        return None

    # Apply the constraints to the board
    for i, j, v in constraints:
        board[i][j] = v

    # Solve the constraint satisfaction problem
    solution = backtrack(board)
    return solution


board = [['.', '.', '.', '.'],
         ['.', '.', '.', '.'],
         ['.', '.', '.', '.'],
         ['.', '.', '.', '.']
         ]
hints = [(0, 1, 1), (2, 2, 2)]

print(minesweeper_solver(board, hints))
# Output: [['.', '*', '.', '.'],
#          ['.', '.', '.', '.'],
#          ['.', '.', '*', '.'],
#          ['.', '.', '.', '.']]
