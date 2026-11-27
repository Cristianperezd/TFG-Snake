import gymnasium as gym
import numpy as np
import pygame
from gymnasium import spaces

import colors
import constants
from food import Food
from snake import Snake, is_out_of_bounds, next_position

# Action index -> (direction, opposite direction that cannot be taken)
ACTIONS = {
    0: ('UP', 'DOWN'),
    1: ('DOWN', 'UP'),
    2: ('LEFT', 'RIGHT'),
    3: ('RIGHT', 'LEFT'),
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
    """

    def __init__(self):
        super().__init__()
        self.action_space = spaces.Discrete(4)
        self.observation_space = spaces.Box(low=0, high=4, shape=(9,), dtype=np.float32)

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

        self.info = {}
        self.observation = self.get_observation(action)

        if self.render_mode == 'human':
            self.render()

        return self.observation, self.reward, self.done, False, self.info

    def reset(self, seed=None):
        self.snake = Snake()
        self.food = Food()
        self.w = constants.WIDTH
        self.h = constants.HEIGHT
        self.score = 0
        self.done = False
        self.reward = 0
        self.update_board()
        self.info = {}

        # The snake always starts moving up, which is action 0
        self.observation = self.get_observation(0)

        if self.render_mode == 'human':
            pygame.init()
            self.display = pygame.display.set_mode((self.w, self.h))
            self.clock = pygame.time.Clock()
            self.render()

        return self.observation, self.info

    def get_observation(self, action):
        head = self.snake.head
        observation = [
            int(self.food.pos.x < head.x),  # food left
            int(self.food.pos.x > head.x),  # food right
            int(self.food.pos.y < head.y),  # food up
            int(self.food.pos.y > head.y),  # food down
            action,
        ]
        observation.extend(self.check_safe_directions())
        return np.array(observation, dtype=np.float32)

    def render(self):
        self.display.fill(colors.BACKGROUND)
        self.snake.draw(display=self.display)
        self.food.draw(display=self.display)
        pygame.display.flip()
        self.clock.tick(60)

    def update_board(self):
        self.board = np.zeros((constants.GRID_ROWS, constants.GRID_COLS), dtype=np.int8)
        self.board[int(self.food.pos.y / constants.BLOCK), int(self.food.pos.x / constants.BLOCK)] = 2
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
        pygame.quit()
