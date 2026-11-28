import numpy as np
import pygame

from snake_ai.game import colors, constants, controls
from snake_ai.game.food import Food
from snake_ai.game.render import WINDOW_SIZE, Renderer, stat_rows
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

    With `show_path=True` the window also shows the path the search agent is
    following and the cells its last search expanded.

    `hud` fills the side panel: a dict with the keys `agent` (the name shown
    as its title) and, optionally, `game` and `games` (current game and total),
    `best` and `mean` (over the games already played, None if there are none),
    and `fps` (False hides the measured frame rate, e.g. in recordings).

    When the game ends, `end_reason` says why: 'collision', 'no path' (the
    agent could not find a path to the food) or 'window closed' (the window
    was closed or Esc pressed). When the game is drawn, Space pauses it.
    """

    def __init__(self, fps=constants.FPS, render=True, hud=None, show_path=False):
        pygame.init()
        self.fps = fps
        self.render = render
        self.show_path = show_path
        self.agent = None  # The agent of the last step, for drawing its search
        self.hud = hud or {}
        self.hints = controls.HINTS  # Help lines at the bottom of the side panel
        self.end_reason = None
        self.w = constants.WIDTH
        self.h = constants.HEIGHT
        self.display = pygame.display.set_mode(WINDOW_SIZE)
        self.display.fill(colors.BACKGROUND)
        if render:
            pygame.display.set_caption(f"Snake AI - {self.hud.get('agent', 'Snake')}")
        self.clock = pygame.time.Clock()
        self._renderer = None

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

    @property
    def renderer(self):
        if self._renderer is None:  # Only created when something is drawn
            self._renderer = Renderer()
        return self._renderer

    def hud_rows(self):
        return stat_rows(
            self.score,
            len(self.snake.body),
            number=self.hud.get("game"),
            total=self.hud.get("games"),
            best=self.hud.get("best"),
            mean=self.hud.get("mean"),
            fps=self.clock.get_fps() if self.hud.get("fps", True) else None,
        )

    def draw(self, overlay=None):
        """Draw the current frame, with an optional (title, subtitle) message over the board."""
        self.renderer.draw_frame(
            self.display,
            self.snake,
            self.food,
            self.hud.get("agent", "Snake"),
            self.hud_rows(),
            hints=self.hints,
            overlay=overlay,
            search=self.search_overlay(),
        )
        pygame.display.flip()

    def search_overlay(self):
        """(path, explored) to draw with --show-path, or None."""
        if not self.show_path or self.agent is None:
            return None
        if self.agent.state != 1:  # The snake has just eaten: no path yet
            return (), ()
        return self.agent.planned_path(self.snake.get_head()), self.agent.expanded

    def pause(self):
        """Wait until Space is pressed again. Return False if the user quits instead."""
        self.draw(overlay=controls.PAUSED)
        return controls.wait(self.clock, skip_keys=(pygame.K_SPACE,))

    def show_game_over(self, seconds=0):
        """Draw the final board with why the game ended, and keep it on screen for
        `seconds` (Space or Enter skips it). Return False if the user quits."""
        self.draw(overlay=controls.game_over_text(self.end_reason))
        if seconds > 0:
            return controls.wait(self.clock, seconds)
        return True

    def step(self, agent=None):
        """Advance the game by one frame.

        With `agent=None` the snake is controlled with the arrow keys. Otherwise
        the agent plans a path to the food and the snake follows it.

        Returns True when the game is over (see `end_reason`), False otherwise.
        The final score is in `score`.

        This reads the window's events (Space pauses here, waiting until it is
        pressed again) and waits for the frame time; `steer` and `advance` are
        the parts that do neither, for loops that handle events and timing
        themselves (the browser version).
        """
        self.agent = agent
        for event in pygame.event.get():
            if controls.is_quit(event):
                return self._end("window closed")
            if self.render and controls.is_pause(event) and not self.pause():
                return self._end("window closed")
            if agent is None:
                self.steer(event)

        if self.advance(agent):
            return True
        self.clock.tick(self.fps)
        return False

    def steer(self, event):
        """Turn the snake if `event` is an arrow key press (human play)."""
        if event.type == pygame.KEYDOWN and event.key in KEY_DIRECTIONS:
            new_direction, opposite = KEY_DIRECTIONS[event.key]
            if self.snake.direction != opposite:
                self.snake.direction = new_direction

    def advance(self, agent=None):
        """Move the game one frame on, without reading events or waiting.

        Like `step`, `agent=None` is a human player (see `steer`) and the
        return value is True when the game is over. With `render` the new frame
        is drawn.
        """
        self.agent = agent
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
        return False
