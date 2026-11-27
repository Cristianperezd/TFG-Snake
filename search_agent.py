import copy

import numpy as np

import constants
from snake import is_out_of_bounds, next_position


class SearchAgent:
    """Common logic for the search agents.

    The game asks the agent for a path to the food (`search`), then follows it
    one move per frame. `state` is 0 when a new path is needed and 1 while the
    agent is following `solution`; `counter` is the index of the next move.
    """

    def __init__(self, initial_node):
        self.reset(initial_node)

    def reset(self, initial_node):
        self.initial_node = initial_node
        self.state = 0
        self.solution = None
        self.counter = 0

    def search(self):
        raise NotImplementedError

    def is_valid_direction(self, node, direction):
        """True if moving in `direction` does not hit a wall or the snake's body."""
        head = next_position(node.snake.get_head(), direction)
        return not is_out_of_bounds(head) and head not in node.snake.body[1:]

    def simulate_move(self, node, direction):
        """Return (board, snake, food) after moving the snake one step in `direction`."""
        new_snake = copy.deepcopy(node.snake)
        new_snake.direction = direction
        new_snake.move()
        new_snake.body.pop()

        new_food = copy.deepcopy(node.food)
        new_board = np.zeros((constants.GRID_ROWS, constants.GRID_COLS), dtype=np.int8)
        new_board[int(new_food.pos.y / constants.BLOCK), int(new_food.pos.x / constants.BLOCK)] = 2
        for block in new_snake.body:
            new_board[int(block.y / constants.BLOCK), int(block.x / constants.BLOCK)] = 1

        return new_board, new_snake, new_food

    def get_solution(self, node):
        """List of directions from the root to `node`. The first one is the root's
        current direction, which the game skips."""
        solution = []
        while node is not None:
            solution.append(node.snake.direction)
            node = node.parent
        solution.reverse()
        return solution

    def is_goal(self, node):
        return node.snake.body[0] == node.food.pos
