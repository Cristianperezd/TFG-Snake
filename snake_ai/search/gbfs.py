import heapq

from snake_ai.game import constants
from snake_ai.search.node import Node
from snake_ai.search.search_agent import SearchAgent


class GBFSNode(Node):
    """Node ordered by the heuristic h only."""

    def __lt__(self, other):
        return self.h < other.h


class GBFS(SearchAgent):
    """Greedy Best-First Search: always expands the node closest to the food."""

    node_class = GBFSNode

    def search(self):
        queue = []
        heapq.heappush(queue, self.initial_node)
        visited = []
        explored = 0
        while queue:
            node = heapq.heappop(queue)
            visited.append(tuple(node.board.flatten()))
            if explored == constants.MAX_EXPANDED_NODES:
                return "END"
            if self.is_goal(node):
                return self.get_solution(node)
            for child in self.expand(node):
                if tuple(child.board.flatten()) not in visited:
                    heapq.heappush(queue, child)
            explored += 1
        return None

    def expand(self, node):
        children = []
        for direction in constants.DIRECTIONS:
            if self.is_valid_direction(node, direction):
                new_board, new_snake, new_food = self.simulate_move(node, direction)
                children.append(GBFSNode(new_board, new_snake, new_food, node))
        return children
