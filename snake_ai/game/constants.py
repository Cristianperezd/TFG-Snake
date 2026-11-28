"""Board geometry shared by the game, the agents and the RL environment."""

# Size of the board (the playfield) in pixels
WIDTH = 500
HEIGHT = 500

# The window adds a side panel with the score and statistics to the right of the board
PANEL_WIDTH = 200
WINDOW_WIDTH = WIDTH + PANEL_WIDTH
WINDOW_HEIGHT = HEIGHT

# Size of one cell in pixels
BLOCK = 20

# Board size in cells (25 x 25)
GRID_COLS = WIDTH // BLOCK
GRID_ROWS = HEIGHT // BLOCK

DIRECTIONS = ("UP", "DOWN", "LEFT", "RIGHT")

# Frames per second when the game is shown in a window
FPS = 30

# GBFS gives up a search after expanding this many nodes
MAX_EXPANDED_NODES = 2000
