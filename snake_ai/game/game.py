import numpy as np
import pygame

from snake_ai.game import colors, constants
from snake_ai.game.food import Food
from snake_ai.game.snake import Snake

KEY_DIRECTIONS = {
    pygame.K_UP: ("UP", "DOWN"),
    pygame.K_DOWN: ("DOWN", "UP"),
    pygame.K_LEFT: ("LEFT", "RIGHT"),
    pygame.K_RIGHT: ("RIGHT", "LEFT"),
}


class Game:
    """Game loop, rendering and board state.

    `board` is a GRID_ROWS x GRID_COLS matrix: 0 = empty, 1 = snake, 2 = food.

    `fps` limits the frame rate (0 = as fast as possible) and `render=False`
    skips drawing, which is useful for fast headless evaluation. Neither
    affects the game itself.

    When the game ends, `end_reason` says why: 'collision', 'no path' (the
    agent could not find a path to the food) or 'window closed'.
    """

    def __init__(self, fps=constants.FPS, render=True):
        pygame.init()
        self.fps = fps
        self.render = render
        self.end_reason = None
        self.w = constants.WIDTH
        self.h = constants.HEIGHT
        self.display = pygame.display.set_mode((self.w, self.h))
        self.display.fill(colors.BACKGROUND)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)

        self.score = 0
        self.snake = Snake()
        self.food = Food()
        self.update_board()

    @property
    def game_over(self):
        return self.end_reason is not None

    def _end(self, reason):
        self.end_reason = reason
        return True

    def update_board(self):
        self.board = np.zeros((constants.GRID_ROWS, constants.GRID_COLS), dtype=np.int8)
        self.board[
            int(self.food.pos.y / constants.BLOCK), int(self.food.pos.x / constants.BLOCK)
        ] = 2
        for block in self.snake.body:
            self.board[int(block.y / constants.BLOCK), int(block.x / constants.BLOCK)] = 1

    def draw(self):
        self.display.fill(colors.BACKGROUND)
        self.snake.draw(display=self.display)
        self.food.draw(display=self.display)
        score_text = self.font.render("Score: " + str(self.score), True, colors.TEXT)
        self.display.blit(score_text, (10, 10))
        pygame.display.flip()

    def step(self, agent=None):
        """Advance the game by one frame.

        With `agent=None` the snake is controlled with the arrow keys. Otherwise
        the agent plans a path to the food and the snake follows it.

        Returns True when the game is over (see `end_reason`), False otherwise.
        The final score is in `score`.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return self._end("window closed")
            if agent is None and event.type == pygame.KEYDOWN and event.key in KEY_DIRECTIONS:
                new_direction, opposite = KEY_DIRECTIONS[event.key]
                if self.snake.direction != opposite:
                    self.snake.direction = new_direction

        if agent is not None and agent.state == 0:
            agent.reset(agent.node_class(self.board, self.snake, self.food))
            agent.solution = agent.search()
            if agent.solution == "END" or agent.solution is None:
                return self._end("no path")
            agent.solution.pop(0)  # Drop the current direction
            agent.state = 1
            agent.counter = 0

        if agent is not None and agent.state == 1:
            self.snake.direction = agent.solution[agent.counter]
            agent.counter += 1

        self.snake.move()

        if self.food.detect_collision(self.snake):
            self.score += 1
            if agent is not None:
                agent.state = 0
        else:
            self.snake.body.pop()

        # Check the collision first: a head outside the board has no cell to mark
        if self.snake.check_collision():
            return self._end("collision")

        self.update_board()

        if self.render:
            self.draw()
        self.clock.tick(self.fps)
        return False
