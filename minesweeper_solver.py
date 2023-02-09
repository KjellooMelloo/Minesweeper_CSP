from minesweeper import Minesweeper, Cell


class MinesweeperSolver:
    """
    Variables X are Cell objects with its values from
    Domain D, consisting of values 1 (mine) or 0 (no mine) and
    Constraints C, defined as "constant is equal to sum of neighbor variables"
    Unary constraints are just "constant != 9"
    """

    def __init__(self, game, starting_point=(0, 0)):
        self.game = game
        self.board = game.board
        self.cells = set()
        self.cells_to_check = set()
        self.cells_to_check.add(self.board[starting_point[0]][starting_point[1]])
        self.checked = set()
        self.worklist = []

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
        while len(self.cells_to_check) != 0:
            cell = self.cells_to_check.pop()
            if self.game.uncover(cell.x, cell.x):    # return is (bool, str)
                print("solver failed")
                return

            # add all uncovered squares to cells_to_check but remove already checked ones
            self.cells_to_check = self.cells_to_check.union(self.game.uncovered).difference(self.checked)
            self.arc_reduce(cell)
            self.subset_arc_reduce()  # TODO wo?

        if len(self.game.uncovered) < self.game.rows * self.game.cols - self.game.mines:  # cells left, game not over
            print("TODO")

    def arc_reduce(self, cell):
        """
        If cell is satisfied, add its neighbors to cells_to_check, if they are safe (0) or mark them as mine (1) else.
        Otherwise remove mine neighbors, if there are any, and decrease new_const
        :param cell: cell to examine
        """
        if cell.is_satisfied(cell.new_const):
            for neighbor in cell.neighbors.copy():
                if cell.new_const == 0:  # all neighbors are safe (value = 0) and can get probed
                    if neighbor not in self.cells_to_check and neighbor not in self.checked:
                        self.cells_to_check.add(neighbor)
                    if cell in neighbor.neighbors:
                        neighbor.neighbors.remove(cell)  # neighbor can remove cell, cause it's satisfied
                else:  # all neighbors are mines
                    neighbor.value = 1
                    self.game.flag(neighbor.x, neighbor.y)
                    if neighbor in self.cells_to_check:  # we don't want to work a mine
                        self.cells_to_check.remove(neighbor)
                        self.checked.add(neighbor)
            self.checked.add(cell)
        else:
            # count amount of mines from neighbors, reduce new_const and remove mine-neighbors
            cell.new_const -= [n.value for n in cell.neighbors].count(1)
            for neighbor in cell.neighbors.copy():
                if neighbor.value == 1:
                    cell.neighbors.remove(neighbor)
                    if neighbor in self.cells_to_check:  # we don't want to work a mine
                        self.cells_to_check.remove(neighbor)
                        self.checked.add(neighbor)
            self.checked.add(cell)
            self.worklist.append(cell)

    def subset_arc_reduce(self, cell1=None, cell2=None):
        if not cell1:
            if len(self.worklist) < 2:
                return
            worklist_copy = self.worklist.copy()
            for i in range(0, len(worklist_copy)):
                for j in range(1, len(worklist_copy) - 1):
                    if not i == j:
                        self.subset_arc_reduce(worklist_copy[i], worklist_copy[j])

        else:
            if cell1 == cell2:
                return
            if cell2.neighbors.issubset(cell1.neighbors):
                cell1.neighbors -= cell2.neighbors
                cell1.new_const -= cell2.new_const
                self.arc_reduce(cell1)
                self.arc_reduce(cell2)
                if cell1.is_satisfied(cell1.new_const) and cell1 in self.worklist:
                    self.worklist.remove(cell1)
                if cell2.is_satisfied(cell2.new_const) and cell2 in self.worklist:
                    self.worklist.remove(cell2)
            elif cell1.neighbors.issubset(cell2.neighbors):
                self.subset_arc_reduce(cell2, cell1)
