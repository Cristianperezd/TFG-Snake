import pygame
from pygame.math import Vector2

from snake_ai.game import colors, constants


def next_position(position, direction):
    """Return the cell reached by moving one block from `position` in `direction`."""
    if direction == "UP":
        return Vector2(position.x, position.y - constants.BLOCK)
    if direction == "DOWN":
        return Vector2(position.x, position.y + constants.BLOCK)
    if direction == "LEFT":
        return Vector2(position.x - constants.BLOCK, position.y)
    return Vector2(position.x + constants.BLOCK, position.y)


def is_out_of_bounds(position):
    return (
        position.x >= constants.WIDTH
        or position.x < 0
        or position.y >= constants.HEIGHT
        or position.y < 0
    )


class Snake:
    """Snake position, movement, collisions and rendering."""

    def __init__(self):
        self.direction = "UP"

        # Start in the middle of the board, three blocks long, facing up
        self.head = Vector2(
            (constants.GRID_COLS // 2) * constants.BLOCK,
            (constants.GRID_ROWS // 2) * constants.BLOCK,
        )
        self.body = [
            self.head,
            Vector2(self.head.x, self.head.y + constants.BLOCK),
            Vector2(self.head.x, self.head.y + 2 * constants.BLOCK),
        ]

    def get_head(self):
        return self.body[0]

    def draw(self, display):
        for index, block in enumerate(self.body):
            color = colors.SNAKE_HEAD if index == 0 else colors.SNAKE_BODY
            pygame.draw.rect(
                display, color, pygame.Rect(block.x, block.y, constants.BLOCK, constants.BLOCK)
            )

    def move(self):
        """Add a new head in the current direction. The caller removes the tail
        unless the snake has just eaten."""
        self.head = next_position(self.head, self.direction)
        self.body.insert(0, self.head)

    def check_collision(self):
        """True if the head is outside the board or on the snake's own body."""
        return is_out_of_bounds(self.head) or self.head in self.body[1:]
