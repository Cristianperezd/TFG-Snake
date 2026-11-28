import random

import gymnasium as gym
import numpy as np
import pygame
from gymnasium import spaces

from snake_ai.game import constants, render
from snake_ai.game.food import Food
from snake_ai.game.snake import Snake, is_out_of_bounds, next_position

# Action index -> (direction, opposite direction that cannot be taken)
ACTIONS = {
    0: ("UP", "DOWN"),
    1: ("DOWN", "UP"),
    2: ("LEFT", "RIGHT"),
    3: ("RIGHT", "LEFT"),
}


class SnakeEnv(gym.Env):
    """Gymnasium environment for training reinforcement learning agents.

    Actions: 0 = up, 1 = down, 2 = left, 3 = right.

    Observation (9 values):
        food left, food right, food up, food down (0/1),
        last action (0-3),
        moving up, down, left, right is safe (0/1).

    Reward: +10 for every apple eaten, accumulated during the episode
    (the value returned is the running total), and -10 when the snake dies.

    Arguments:
        render_mode: None (no drawing), "human" (draw every step in a window)
            or "rgb_array" (`render()` returns the frame as an HxWx3 array).
            Frames have the same look as `snake-ai play`: the board and a side
            panel, WINDOW_HEIGHT x WINDOW_WIDTH pixels.
        max_episode_steps: if set, an episode is truncated after this many
            steps. The default, None, never truncates, as in the thesis.

    Seeding: the food positions come from Python's `random` module, as in the
    thesis. `reset(seed=n)` seeds it, so seeded resets are reproducible;
    `reset()` leaves it alone.

    `hud` (a dict, empty by default) adds rows to the side panel: `episode`,
    `episodes`, and `best` and `mean` over the finished episodes. It is only
    used for drawing.
    """

    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 60}

    def __init__(self, render_mode=None, max_episode_steps=None):
        super().__init__()
        if render_mode is not None and render_mode not in self.metadata["render_modes"]:
            raise ValueError(
                f"render_mode must be one of {self.metadata['render_modes']} or None, "
                f"got {render_mode!r}"
            )
        if max_episode_steps is not None and max_episode_steps < 1:
            raise ValueError(f"max_episode_steps must be at least 1, got {max_episode_steps}")
        self.render_mode = render_mode
        self.max_episode_steps = max_episode_steps
        self.action_space = spaces.Discrete(4)
        self.observation_space = spaces.Box(low=0, high=4, shape=(9,), dtype=np.float32)
        self.w = constants.WIDTH
        self.h = constants.HEIGHT
        self.display = None
        self.clock = None
        self.renderer = None
        self.hud = {}

    def step(self, action):
        direction, opposite = ACTIONS[int(action)]
        if self.snake.direction != opposite:
            self.snake.direction = direction

        self.snake.move()

        if self.food.detect_collision(self.snake):
            self.score += 1
            self.reward += 10
        else:
            self.snake.body.pop()

        if self.snake.check_collision():
            self.done = True
            self.reward = -10
        else:
            self.update_board()

        self.steps += 1
        truncated = (
            not self.done
            and self.max_episode_steps is not None
            and self.steps >= self.max_episode_steps
        )

        self.info = {}
        self.observation = self.get_observation(action)

        if self.render_mode == "human":
            self.render()

        return self.observation, self.reward, self.done, truncated, self.info

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        if seed is not None:
            # The food positions use Python's random module
            random.seed(seed)

        self.snake = Snake()
        self.food = Food()
        self.score = 0
        self.steps = 0
        self.done = False
        self.reward = 0
        self.update_board()
        self.info = {}

        # The snake always starts moving up, which is action 0
        self.observation = self.get_observation(0)

        if self.render_mode == "human":
            self.render()

        return self.observation, self.info

    def get_observation(self, action):
        head = self.snake.head
        observation = [
            int(self.food.pos.x < head.x),  # food left
            int(self.food.pos.x > head.x),  # food right
            int(self.food.pos.y < head.y),  # food up
            int(self.food.pos.y > head.y),  # food down
            int(action),
        ]
        observation.extend(self.check_safe_directions())
        return np.array(observation, dtype=np.float32)

    def _draw(self, surface):
        if self.renderer is None:
            self.renderer = render.Renderer()
        rows = render.stat_rows(
            self.score,
            len(self.snake.body),
            number=self.hud.get("episode"),
            total=self.hud.get("episodes"),
            best=self.hud.get("best"),
            mean=self.hud.get("mean"),
            fps=self.clock.get_fps() if self.clock is not None else None,
            label="Episode",
        )
        self.renderer.draw_frame(surface, self.snake, self.food, "PPO", rows)

    def render(self):
        if self.render_mode == "rgb_array":
            # Draw on an off-screen surface: no window is needed
            surface = pygame.Surface(render.WINDOW_SIZE)
            self._draw(surface)
            return np.transpose(pygame.surfarray.array3d(surface), (1, 0, 2)).astype(np.uint8)

        if self.render_mode == "human":
            if self.display is None:
                pygame.init()
                pygame.display.set_caption("Snake AI - PPO")
                self.display = pygame.display.set_mode(render.WINDOW_SIZE)
                self.clock = pygame.time.Clock()
            pygame.event.pump()  # Keep the window responsive
            self._draw(self.display)
            pygame.display.flip()
            self.clock.tick(self.metadata["render_fps"])
        return None

    def update_board(self):
        self.board = np.zeros((constants.GRID_ROWS, constants.GRID_COLS), dtype=np.int8)
        self.board[
            int(self.food.pos.y / constants.BLOCK), int(self.food.pos.x / constants.BLOCK)
        ] = 2
        for block in self.snake.body:
            self.board[int(block.y / constants.BLOCK), int(block.x / constants.BLOCK)] = 1

    def check_safe_directions(self):
        """For each of up, down, left, right: 1 if moving there does not kill the snake."""
        head = self.snake.get_head()
        safe = []
        for direction in constants.DIRECTIONS:
            position = next_position(head, direction)
            safe.append(int(not is_out_of_bounds(position) and position not in self.snake.body[1:]))
        return safe

    def close(self):
        if self.display is not None:
            pygame.display.quit()
            self.display = None
            self.clock = None
            self.renderer = None
