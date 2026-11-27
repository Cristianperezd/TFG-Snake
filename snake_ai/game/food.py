import random

import pygame
from pygame.math import Vector2

from snake_ai.game import colors, constants


class Food:
    """Food position, respawning and rendering."""

    def __init__(self):
        # The first apple always appears in the second column, at a random row
        row = random.randint(0, (constants.HEIGHT - constants.BLOCK) // constants.BLOCK)
        self.pos = Vector2(constants.BLOCK, row * constants.BLOCK)

    def generate(self):
        """Move the food to a random cell."""
        x = random.randint(0, (constants.WIDTH - constants.BLOCK) // constants.BLOCK)
        y = random.randint(0, (constants.HEIGHT - constants.BLOCK) // constants.BLOCK)
        self.pos = Vector2(x * constants.BLOCK, y * constants.BLOCK)

    def draw(self, display):
        pygame.draw.rect(display, colors.FOOD,
                         pygame.Rect(self.pos.x, self.pos.y, constants.BLOCK, constants.BLOCK))

    def detect_collision(self, snake):
        """If the snake's head is on the food, respawn it outside the snake and return True."""
        if snake.head != self.pos:
            return False

        self.generate()
        while self.pos in snake.body:
            self.generate()
        return True
