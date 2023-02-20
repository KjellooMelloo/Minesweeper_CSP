import random

import pygame
import sys
import time

from minesweeper import Minesweeper
from minesweeper_solver import MinesweeperSolver

# adapted from: https://cs50.harvard.edu/ai/2020/projects/1/minesweeper/

HEIGHT = 8
WIDTH = 8
MINES = 10

# Colors
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
WHITE = (255, 255, 255)

# Create game
pygame.init()
size = width, height = 900, 600
screen = pygame.display.set_mode(size)

# Fonts
OPEN_SANS = "assets/fonts/OpenSans-Regular.ttf"
smallFont = pygame.font.Font(OPEN_SANS, 20)
mediumFont = pygame.font.Font(OPEN_SANS, 28)
largeFont = pygame.font.Font(OPEN_SANS, 40)

# Compute board size
BOARD_PADDING = 20
board_width = ((2 / 3) * width) - (BOARD_PADDING * 2)
board_height = height - (BOARD_PADDING * 2)
cell_size = int(min(board_width / WIDTH, board_height / HEIGHT))
board_origin = (BOARD_PADDING, BOARD_PADDING)

# Add images
flag = pygame.image.load("assets/images/flag.png")
flag = pygame.transform.scale(flag, (cell_size, cell_size))
mine = pygame.image.load("assets/images/mine.png")
mine = pygame.transform.scale(mine, (cell_size, cell_size))

# Create game and AI agent
game = Minesweeper(rows=HEIGHT, cols=WIDTH, mines=MINES)
rand_x = random.randint(0, WIDTH - 1)
rand_y = random.randint(0, HEIGHT - 1)
print("Starting point: ", rand_x, rand_y)
ai = MinesweeperSolver(game, starting_point=(rand_x, rand_y))

# Keep track of revealed cells, flagged cells, and if a mine was hit
revealed = set()
flags = set()
game_over = game.game_over
result = game.result

while True:

    # Check if game quit
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    screen.fill(BLACK)

    # Draw board
    flags = game.marked_to_coordinates()
    revealed = game.uncovered_to_coordinates()
    result = game.result

    cells = []
    for i in range(HEIGHT):
        row = []
        for j in range(WIDTH):

            # Draw rectangle for cell
            rect = pygame.Rect(
                board_origin[0] + j * cell_size,
                board_origin[1] + i * cell_size,
                cell_size, cell_size
            )
            pygame.draw.rect(screen, GRAY, rect)
            pygame.draw.rect(screen, WHITE, rect, 3)

            if game_over:
                # Result text
                text = result
                text = mediumFont.render(text, True, WHITE)
                textRect = text.get_rect()
                textRect.center = ((5 / 6) * width, (4 / 5) * height)
                screen.blit(text, textRect)

            # Add a mine, flag, or number if needed
            if (i, j) in flags:
                screen.blit(flag, rect)
            elif result == "Lost" and game.is_mine(i, j):
                screen.blit(mine, rect)
            elif (i, j) in revealed:
                val = smallFont.render(
                    str(game.board[i][j].constant),
                    True, BLACK
                )
                valTextRect = val.get_rect()
                valTextRect.center = rect.center
                screen.blit(val, valTextRect)

            row.append(rect)
        cells.append(row)

    # AI Move button
    aiButton = pygame.Rect(
        (2 / 3) * width + BOARD_PADDING, (1 / 5) * height - 50,
        (width / 3) - BOARD_PADDING * 2, 50
    )
    buttonText = mediumFont.render("AI Solve", True, BLACK)
    buttonRect = buttonText.get_rect()
    buttonRect.center = aiButton.center
    pygame.draw.rect(screen, WHITE, aiButton)
    screen.blit(buttonText, buttonRect)

    # Reset button
    resetButton = pygame.Rect(
        (2 / 3) * width + BOARD_PADDING, (1 / 5) * height + 20,
        (width / 3) - BOARD_PADDING * 2, 50
    )
    buttonText = mediumFont.render("Reset", True, BLACK)
    buttonRect = buttonText.get_rect()
    buttonRect.center = resetButton.center
    pygame.draw.rect(screen, WHITE, resetButton)
    screen.blit(buttonText, buttonRect)

    # Num mines
    numMines = "Mines: " + str(game.mines - len(game.marked))
    numMines = mediumFont.render(numMines, True, WHITE)
    numMinesRect = numMines.get_rect()
    numMinesRect.center = ((5 / 6) * width, (3 / 5) * height)
    screen.blit(numMines, numMinesRect)

    move = None

    left, _, right = pygame.mouse.get_pressed()

    # Check for a right-click to toggle flagging
    if right == 1 and not game_over:
        mouse = pygame.mouse.get_pos()
        for i in range(HEIGHT):
            for j in range(WIDTH):
                if cells[i][j].collidepoint(mouse) and (i, j) not in revealed:
                    game.flag(i, j)
                    time.sleep(0.2)

    elif left == 1:
        mouse = pygame.mouse.get_pos()

        # potential TODO
        # If AI button clicked, let AI solve
        if aiButton.collidepoint(mouse) and not game_over:
            ai.solve()
            revealed = game.uncovered_to_coordinates()
            flags = game.marked_to_coordinates()
            time.sleep(0.2)

        # Reset game state
        elif resetButton.collidepoint(mouse):
            game = Minesweeper(rows=HEIGHT, cols=WIDTH, mines=MINES)
            ai = MinesweeperSolver(game)
            revealed = set()
            flags = set()
            game_over = game.game_over
            result = game.result
            continue

        # User-made move
        elif not game_over:
            for i in range(HEIGHT):
                for j in range(WIDTH):
                    if (cells[i][j].collidepoint(mouse)
                            and (i, j) not in flags
                            and (i, j) not in revealed):
                        move = (i, j)

    # Make move and update AI knowledge
    if move:
        game_over = game.uncover(move[0], move[1])

    pygame.display.flip()
