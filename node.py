from food import Food
from snake import Snake


class Node:
    """A state in the search tree.

    h: Manhattan distance (in pixels) from the snake's head to the food.
    g: number of moves from the root of the search.
    cost: g + h.
    """

    def __init__(self, board, snake: Snake, food: Food, parent=None):
        self.board = board
        self.snake = snake
        self.food = food
        self.parent = parent
        self.h = self.calculate_h()
        self.g = parent.g + 1 if parent is not None else 1
        self.cost = self.h + self.g

    def calculate_h(self):
        head = self.snake.get_head()
        return abs(head.x - self.food.pos.x) + abs(head.y - self.food.pos.y)
