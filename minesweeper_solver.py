from minesweeper import Minesweeper, Cell


class MinesweeperSolver:
    """
    Variables X are Cell objects with its values from
    Domain D, consisting of values 1 (mine) or 0 (no mine) and
    Constraints C, defined as "constant is equal to sum of neighbor variables"
    Unary constraints are just "constant != 9"
    """

    def __init__(self, game=Minesweeper(), starting_point=(0, 0)):
        self.game = game
        self.board = game.board
        self.cells = set()
        self.worklist = []
        self.worklist.append(self.board[starting_point[0]][starting_point[1]])
        self.moves = []

    def solve(self):
        self.add_attributes_to_cells()
        self.ac3()

    def add_attributes_to_cells(self):
        board_set = [set(cells) for cells in self.board]
        for cells in board_set:
            for cell in cells:
                cell.value = 0  # value to 0 as default (no mine)
                coordinates = self.game.get_neighbors(cell.x, cell.y)
                cell.neighbors = set([self.board[c[0]][c[1]] for c in coordinates])
                cell.is_satisfied = lambda const: const == sum([n.value for n in cell.neighbors])  # constraint
                cell.new_const = cell.constant  # for dynamically changing constant value and not altering original

    def ac3(self):
        while len(self.worklist) != 0:
            cell = self.worklist.pop()
            self.game.uncover(cell.x, cell.y)  # don't need the return here
            self.cells = self.game.uncovered  # we work on added attributes on cell objects, so we don't want .copy()
            if self.game.game_over:
                print("solver failed")
                return

            self.arc_reduce(cell)
            self.subset_arc_reduce()  # TODO wo?

        if len(self.game.uncovered) < self.game.rows * self.game.cols - self.game.mines:  # cells left, game not over
            print("TODO")

    def arc_reduce(self, cell):
        """
        If cell is satisfied, add its neighbors to worklist, if they are safe (0) or mark them as mine (1) else.
        Otherwise remove mine neighbors, if there are any, and decrease new_const
        :param cell: cell to examine
        """
        if cell.is_satisfied(cell.new_const):
            for neighbor in cell.neighbors.copy():
                if cell.new_const == 0:  # all neighbors are safe (value = 0) and can get probed
                    if neighbor not in self.worklist:
                        self.worklist.append(neighbor)
                    if cell in neighbor.neighbors:
                        neighbor.neighbors.remove(cell)  # neighbor can remove cell, cause it's satisfied
                else:  # all neighbors are mines
                    neighbor.value = 1
        else:
            # count amount of mines from neighbors, reduce new_const and remove mine-neighbors
            cell.new_const -= [n.value for n in cell.neighbors].count(1)
            for neighbor in cell.neighbors:
                if neighbor.value == 1:
                    cell.neighbors.remove(neighbor)

    def subset_arc_reduce(self, cell1=None, cell2=None):
        if not cell1:
            if len(self.worklist) < 2:
                return
            for i in range(0, len(self.worklist)):
                for j in range(1, len(self.worklist) - 1):
                    if not i == j:
                        self.subset_arc_reduce(self.worklist[i], self.worklist[j])
        else:
            if cell2.neighbors.issubset(cell1.neighbors):
                cell1.neighbors -= cell2.neighbors
                cell1.new_const -= cell2.new_const
                self.worklist.remove(cell1)  # TODO maybe just add to worklist, depends on where this method is called
                self.arc_reduce(cell1)
            elif cell1.neighbors.issubset(cell2.neighbors):
                self.subset_arc_reduce(cell2, cell1)
