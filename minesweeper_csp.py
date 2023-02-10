import random


class MinesweeperCSP:
    def __init__(self, game, starting_point=(0, 0)):
        self.game = game
        self.board = game.board
        self.cells_to_check = [self.board[starting_point[0]][starting_point[1]]]
        self.checked_cells = set()
        self.marked_count = {}
        self.moves = []

    def solve(self):
        self.add_attributes_to_cells()
        while self.cells_to_check:
            cell = self.cells_to_check.pop()
            if self.uncover_cell(cell):  # uncovered a mine
                return
            self.simplify_constraints()

        mines_left = self.game.mines - len(self.game.marked)
        if len(self.moves) > 0 and mines_left > 0:
            # do backtracking search to pick cells to uncover
            self.search()
        mines_left = self.game.mines - len(self.game.marked)
        # check if last mine is surrounded by other mines
        if mines_left:
            cells_left = list(
                set([self.board[x][y] for x in range(0, self.game.cols) for y in range(0, self.game.rows)])
                - self.game.marked - self.game.uncovered)
            if cells_left:
                if len(cells_left) == mines_left:
                    for sq in cells_left:
                        self.mark_cell(sq, True)
        else:
            # if there are still uncovered cells
            if self.moves:
                for cell in self.moves:
                    for neighbor in cell.neighbors:
                        self.uncover_cell(neighbor)
        return

    def add_attributes_to_cells(self):
        board_set = [set(cells) for cells in self.board]
        for cells in board_set:
            for cell in cells:
                cell.value = None  # value to default
                coordinates = self.game.get_neighbors(cell.x, cell.y)
                cell.neighbors = set([self.board[c[0]][c[1]] for c in coordinates])
                cell.is_satisfied = lambda const: const == sum([n.value for n in cell.neighbors])  # constraint
                cell.new_const = cell.constant  # for dynamically changing constant value and not altering original

    def uncover_cell(self, cell):
        """returns True if the uncovered cell is a mine"""
        if cell in self.checked_cells:
            return
        x, y = cell.x, cell.y
        self.checked_cells.add(cell)
        if self.game.uncover(x, y):
            # uncovered a mine
            return True

        self.mark_cell(cell)
        if cell.constant == 0:
            # add neighbors of cell to cells_to_check
            for n in cell.neighbors:
                if n not in self.checked_cells:
                    self.cells_to_check.append(n)
        elif 0 < cell.constant < 9:
            # numbered cell, add to list of moves
            if cell not in self.moves:
                self.moves.append(cell)
            return
        return

    def mark_cell(self, cell, is_mine=False):
        """update neighbors of known mine or safe cell"""
        x, y = cell.x, cell.y
        if (x, y) not in self.marked_count:
            self.marked_count[(x, y)] = 1
        else:
            self.marked_count[(x, y)] += 1
        if is_mine:
            cell.value = 1
            self.game.flag(x, y)
        # remove known cell from adjacent neighbor constraints
        for neighbor in cell.neighbors:
            if cell in neighbor.neighbors:
                neighbor.neighbors.remove(cell)
                if is_mine:
                    # if cell is a mine, decrement neighbors constants
                    neighbor.new_const -= 1
        return

    def simplify_constraints(self):
        neighbors_to_remove = set()
        for move in self.moves:
            if len(move.neighbors) == move.new_const:
                # leftover neighbors are mines
                while move.neighbors:
                    cell = move.neighbors.pop()
                    self.mark_cell(cell, True)
                neighbors_to_remove.add(move)
            elif move.new_const == 0:
                # if there are neighbors left, they are safe cells
                while move.neighbors:
                    cell = move.neighbors.pop()
                    self.cells_to_check.append(cell)
                neighbors_to_remove.add(move)
        # remove any cells that have been satisfied
        for m in neighbors_to_remove:
            self.moves.remove(m)

        # now look at pairs of constraints to reduce subsets
        neighbors_to_remove = set()
        if len(self.moves) > 1:
            i = 0
            j = i + 1
            while i < len(self.moves):
                while j < len(self.moves):
                    c1 = self.moves[i]
                    c2 = self.moves[j]
                    to_remove = self.simplify(c1, c2)
                    if to_remove:
                        neighbors_to_remove.update(to_remove)
                    j += 1
                i += 1
                j = i + 1
        for m in neighbors_to_remove:
            self.moves.remove(m)
        return

    def simplify(self, c1, c2):
        if c1 == c2:
            return
        to_remove = set()
        c1_neighbors = c1.neighbors
        c2_neighbors = c2.neighbors
        if c1_neighbors and c2_neighbors:
            if c1_neighbors.issubset(c2_neighbors):
                c2.neighbors = c2_neighbors - c1_neighbors
                c2.new_const -= c1.new_const
                if c2.new_const == 0 and len(c2.neighbors) > 0:
                    # neighbors are safe/can be uncovered
                    while c2.neighbors:
                        n = c2.neighbors.pop()
                        if n not in self.cells_to_check and n not in self.checked_cells:
                            self.cells_to_check.append(n)
                    to_remove.add(c2)
                elif c2.new_const > 0 and c2.new_const == len(c2.neighbors):
                    while c2.neighbors:
                        n = c2.neighbors.pop()
                        self.mark_cell(n, True)
                    to_remove.add(c2)
                if c1.new_const > 0 and c1.new_const == len(c1.neighbors):
                    while c1.neighbors:
                        n = c1.neighbors.pop()
                        self.mark_cell(n, True)
                    to_remove.add(c1)

                return to_remove
            elif c2_neighbors.issubset(c1_neighbors):
                return self.simplify(c2, c1)

    def search(self):
        # backtracking for all solutions with the remaining cells
        res = {}
        # make a list of unknown constraints
        for m in self.moves:
            if m.neighbors:
                for neighbor in m.neighbors:
                    if neighbor not in res:
                        res[neighbor] = 1
                    else:
                        res[neighbor] += 1
        cells = list(res.keys())
        mines_left = self.game.mines - len(self.game.marked)
        cells_left = len(cells)

        def backtrack(comb):
            if len(comb) > cells_left:
                return
            elif sum(comb) > mines_left:
                return
            else:
                for choice in [0, 1]:
                    comb.append(choice)
                    if sum(comb) == mines_left and len(comb) == cells_left:
                        valid = self.check_solution_validity(cells, comb)
                        if valid:
                            # only keep valid solutions
                            c = comb.copy()
                            solutions.append(c)
                    backtrack(comb)
                return solutions

        solutions = []
        # backtrack to find solutions if there are fewer mines than cells
        if mines_left < cells_left:
            backtrack([])
        if solutions:
            # check if any cells are safe in all solutions
            cell_solution_counts = {}
            for c in range(len(solutions)):
                for cell in range(len(solutions[c])):
                    current_cell = cells[cell]
                    if current_cell not in cell_solution_counts:
                        cell_solution_counts[current_cell] = solutions[c][cell]
                    else:
                        cell_solution_counts[current_cell] += solutions[c][cell]
            added_safe_cells = False
            for cell, count in cell_solution_counts.items():
                if count == 0:
                    added_safe_cells = True
                    self.cells_to_check.append(cell)
            if not added_safe_cells:
                # pick a random solution and probe safe cells
                random_solution = random.randint(0, len(solutions) - 1)
                comb = solutions[random_solution]
                for cell, value in zip(cells, comb):
                    if value == 0:
                        # currently just adding all cells marked as safe in the first solution in list
                        self.cells_to_check.append(cell)

        else:
            # no solutions, so pick a random cell
            cells_left = list(
                set([self.board[x][y] for x in range(0, self.game.cols) for y in range(0, self.game.rows)])
                - self.game.marked - self.game.uncovered)
            random_square = random.randint(0, len(cells_left) - 1)
            next_square = cells_left[random_square]
            self.cells_to_check.append(next_square)
        return

    def check_solution_validity(self, cells, comb):
        """check each solution from backtracking to make sure they don't violate constraints"""
        all_valid = False
        for cell, value in zip(cells, comb):
            all_valid = self.meets_constraints(cell, value)
        # after checking validity, set the cell's val back to None
        for cell in cells:
            cell.value = None
        return all_valid

    def meets_constraints(self, variable, val):
        """sets the variable to the value {0,1} and checks to see if it violates constraints"""
        variable.value = val
        for n in variable.neighbors:
            neighbor_constant = n.constant
            # only look at neighbors that are uncovered and aren't mines
            if n.value is not None and n.value != 1:
                mines, safe, unknown = self.get_neighbor_count(n)
                if mines > neighbor_constant:
                    # violation: too many mines
                    return False
                elif (neighbor_constant - mines) > unknown:
                    # violation: not enough mines
                    return False
        return True

    def get_neighbor_count(self, variable):
        """
        return count of mines, safe cells and unknown cells around the variable
        """
        mine_count = 0
        unknown_count = 0
        safe_count = 0
        for nb in variable.neighbors:
            if nb.value == 1:
                mine_count += 1
            elif nb.value == 0:
                safe_count += 1
            elif not nb.value:
                unknown_count += 1
        return mine_count, safe_count, unknown_count
