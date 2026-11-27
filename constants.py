"""Board geometry shared by the game, the agents and the RL environment."""

# Window size in pixels
WIDTH = 500
HEIGHT = 500

# Size of one cell in pixels
BLOCK = 20

# Board size in cells (25 x 25)
GRID_COLS = WIDTH // BLOCK
GRID_ROWS = HEIGHT // BLOCK

DIRECTIONS = ('UP', 'DOWN', 'LEFT', 'RIGHT')
