import random


class Minesweeper:
    """
    Minesweeper game representation
    adapted from: https://cs50.harvard.edu/ai/2020/projects/1/minesweeper/
    board generation from: https://www.lvngd.com/blog/generating-minesweeper-boards-python/
    """

    def __init__(self, rows=9, cols=9, mines=10):
        assert 3 < rows < 50 and 3 < cols < 50 and 0 < mines  # check parameters
        assert 0 < mines / (rows * cols) < 0.5  # assure max mine density of 0.5

        # Set initial cols, rows, and number of mines
        self.rows = rows
        self.cols = cols
        self.mines = mines

        # Initialize an empty field with no mines aka all 0 then add the mines
        self.board = [[0 for i in range(0, rows)] for j in range(0, cols)]
        self.generate_board()

        # keep track of uncovered cells
        self.uncovered = set()
        self.game_over = False
        self.result = ""

        self.print()

    def generate_board(self):
        # Generate list of coordinates and sample mine coordinates
        board_coordinates = [(x, y) for x in range(0, self.cols) for y in range(0, self.rows)]
        mine_coordinates = random.sample(board_coordinates, self.mines)

        # place mines
        for mine in mine_coordinates:
            x, y = mine
            self.board[x][y] = 9
            neighbors = [(x - 1, y), (x - 1, y + 1), (x, y - 1), (x + 1, y - 1), (x + 1, y), (x + 1, y + 1), (x, y + 1),
                         (x - 1, y - 1)]

            # increase "mine counter" for all neighbors
            for n in neighbors:
                if 0 <= n[0] <= self.cols - 1 and 0 <= n[1] <= self.rows - 1 and n not in mine_coordinates:
                    self.board[n[0]][n[1]] += 1

    def uncover(self, cell):
        """
        uncovers a cell, adds it to uncovered-set and checks for game over
        :param cell: cell to uncover
        :return: value of the cell, game_over state and result string
        """
        x, y = cell
        val = self.board[x][y]

        # make sure that first uncover isn't a mine
        if len(self.uncovered) == 0 and val == 9:
            while val == 9:
                self.board = [[0 for i in range(0, self.rows)] for j in range(0, self.cols)]
                self.generate_board()
                val = self.board[x][y]

        self.uncovered.add(cell)

        if val == 9:
            self.game_over = True
            self.result = "Lost"
            print(self.result)
        if len(self.uncovered) == (self.rows * self.cols) - self.mines:
            self.game_over = True
            self.result = "Won"
            print(self.result)
        if val == 0:
            self.uncover_zeroes(cell)

        return val, self.game_over, self.result

    def uncover_zeroes(self, cell):
        neighbors = self.get_neighbors(cell)
        for neigh in neighbors:
            if neigh not in self.uncovered:
                self.uncover(neigh)

    def get_neighbors(self, cell):
        x, y = cell
        neighbors = []
        x_vals = [x - 1, x, x + 1]
        y_vals = [y - 1, y, y + 1]

        # collect neighbours only in bounds
        for i in range(0, 3):
            for j in range(0, 3):
                if i == 1 and j == 1:  # skip self
                    continue
                if 0 <= x_vals[i] <= self.cols - 1 and 0 <= y_vals[j] <= self.rows - 1:
                    neighbors.append((x_vals[i], y_vals[j]))

        return neighbors

    def is_mine(self, cell):
        x, y = cell
        return self.board[x][y] == 9

    def print(self):
        """
        Prints a text-based representation of the board.
        Mines are marked with *
        """
        print("Board: \n")
        for i in range(self.rows):
            for j in range(self.cols):
                if self.board[i][j] == 9:
                    print("| *", end="")
                else:
                    print("|", self.board[i][j], end="")
            print("|")
