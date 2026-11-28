import numpy as np

from snake_ai.game import constants
from snake_ai.search.node import Node
from snake_ai.search.search_agent import SearchAgent


class AStarNode(Node):
    """Node ordered by total cost g + h."""

    def __lt__(self, other):
        return self.cost < other.cost


class AStar(SearchAgent):
    """A* search ordered by g + h.

    To avoid exploring redundant paths, the agent remembers the lowest cost
    that has reached each cell and discards children that reach a cell with an
    equal or higher cost.
    """

    node_class = AStarNode

    def reset(self, initial_node):
        super().reset(initial_node)
        self.best_cost = np.full((constants.GRID_ROWS, constants.GRID_COLS), np.inf)

    def search(self):
        queue = [self.initial_node]
        visited = []
        while queue:
            node = queue.pop(0)
            self.expanded.append(node.snake.get_head())
            visited.append(tuple(node.board.flatten()))
            if self.is_goal(node):
                return self.get_solution(node)
            for child in self.expand(node):
                if tuple(child.board.flatten()) not in visited:
                    queue.append(child)
            queue.sort(key=lambda n: n.cost)
        return None

    def expand(self, node):
        children = []
        for direction in constants.DIRECTIONS:
            if self.is_valid_direction(node, direction):
                new_board, new_snake, new_food = self.simulate_move(node, direction)
                child = AStarNode(new_board, new_snake, new_food, node)
                head = new_snake.get_head()
                cell = (int(head.y / constants.BLOCK), int(head.x / constants.BLOCK))
                if self.best_cost[cell] > child.cost:
                    self.best_cost[cell] = child.cost
                    children.append(child)
        return children
