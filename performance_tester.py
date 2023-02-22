import random
import time
from statistics import mean

from minesweeper import Minesweeper
from minesweeper_solver import MinesweeperSolver

RUNS = 100
HEIGHT = 5
WIDTH = 5
MINES = 3

success = 0
failure = 0
times = []
progresses = []

for x in range(RUNS):
    game = Minesweeper(rows=HEIGHT, cols=WIDTH, mines=MINES)
    rand_x = random.randint(0, WIDTH - 1)
    rand_y = random.randint(0, HEIGHT - 1)
    print("Starting point: ", rand_x, rand_y)
    ai = MinesweeperSolver(game, starting_point=(rand_x, rand_y))
    tic = time.perf_counter()
    ai.solve()
    toc = time.perf_counter()
    times.append((tic, toc))
    progresses.append(len([(x, y) for x, y in ai.variables if ai.values[(x, y)] is not None]) / (HEIGHT * WIDTH))

    if game.result == "Won":
        success += 1
    else:
        failure += 1

print("Result for {} runs with {} rows, {} columns and {} mines:".format(str(RUNS), str(HEIGHT), str(WIDTH), str(MINES)))
print("Successful solves: {}".format(str(success)))
print("Failed solves: {}".format(str(failure)))
print("Solving rate: {}".format(str(success / RUNS)))
print("Average solving time: {:0.4f}s".format(mean([y - x for x, y in times])))
print("Average progress per solve: {}".format(str(mean(progresses))))
