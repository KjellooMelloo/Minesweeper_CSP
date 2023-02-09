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
        self.board = [[Cell(x, y, 0) for y in range(0, rows)] for x in range(0, cols)]
        self.generate_board()
        self.check_consistency()

        # keep track of uncovered cells
        self.uncovered = set()
        self.marked = set()
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
            self.board[x][y].constant = 9
            neighbors = self.get_neighbors(x, y)

            # increase "mine counter" for all neighbors
            for n in neighbors:
                if n not in mine_coordinates:
                    self.board[n[0]][n[1]].constant += 1

    def check_consistency(self):
        for x in range(0, self.cols):
            for y in range(0, self.rows):
                cell = self.board[x][y]
                if 0 < cell.constant < 9:
                    mine_neighbors = [self.board[n[0]][n[1]] for n in self.get_neighbors(x, y)]
                    if cell.constant != [m.constant == 9 for m in mine_neighbors].count(True):
                        print("not consistent!")

    def uncover(self, x, y):
        """
        uncovers a cell, adds it to uncovered-set and checks for game over
        :param x: x value to uncover
        :param y: y value to uncover
        :return: Cell at x, y, game_over state and result string
        """
        cell = self.board[x][y]
        val = cell.constant

        if cell in self.uncovered:
            return

        # make sure that first uncover isn't a mine
        if len(self.uncovered) == 0 and val == 9:
            while val == 9:
                self.board = [[Cell(x, y, 0) for y in range(0, self.rows)] for x in range(0, self.cols)]
                self.generate_board()
                val = self.board[x][y].constant

        self.uncovered.add(cell)

        if val == 9:
            self.game_over = True
            self.result = "Lost"
            print(self.result)
        elif len(self.uncovered) == (self.rows * self.cols) - self.mines:
            self.game_over = True
            self.result = "Won"
            print(self.result)
        if val == 0:
            self.uncover_zeroes(x, y)

        return self.game_over

    def uncover_zeroes(self, x, y):
        """
        uncovers all neighboring zeroes
        :param x: x of current cell
        :param y: x of current cell
        """
        neighbors = self.get_neighbors(x, y)
        for neigh in neighbors:
            if self.board[neigh[0]][neigh[1]] not in self.uncovered:
                self.uncover(neigh[0], neigh[1])

    def get_neighbors(self, x, y):
        """
        Returns x and x coordinate-list of neighbors
        :param x: x of current cell
        :param y: x of current cell
        :return: neighbors as (x,x)-list
        """
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

    def flag(self, x, y):
        cell = self.board[x][y]
        if cell in self.uncovered:
            return
        cell.marked = not cell.marked
        self.marked.add(cell) if cell.marked else self.marked.remove(cell)

    def is_mine(self, x, y):
        return self.board[x][y].constant == 9

    def uncovered_to_coordinates(self):
        return set([cell.to_coordinate() for cell in self.uncovered])

    def marked_to_coordinates(self):
        return set([cell.to_coordinate() for cell in self.marked])

    def print(self):
        """
        Prints a text-based representation of the board.
        Mines are marked with *
        """
        print("Board: \n")
        for y in range(self.rows):
            for x in range(self.cols):
                if self.board[x][y].constant == 9:
                    print("| *", end="")
                else:
                    print("|", self.board[x][y].constant, end="")
            print("|")


class Cell:

    def __init__(self, x, y, constant):
        self.x = x
        self.y = y
        self.constant = constant
        self.marked = False

    def to_coordinate(self):
        return self.x, self.y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.x and self.constant == other.constant

    def __hash__(self):
        return hash((self.x, self.y, self.constant))

    def __str__(self):
        return "(x:" + str(self.x) + ",x:" + str(self.y) + ",constant:" + str(self.constant) + ")"
