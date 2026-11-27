import heapq

import constants
from gbfs_node import GBFSNode
from search_agent import SearchAgent

# Give up a search after expanding this many nodes
MAX_EXPANDED_NODES = 2000


class GBFS(SearchAgent):
    """Greedy Best-First Search: always expands the node closest to the food."""

    def search(self):
        queue = []
        heapq.heappush(queue, self.initial_node)
        visited = []
        explored = 0
        while queue:
            node = heapq.heappop(queue)
            visited.append(tuple(node.board.flatten()))
            if explored == MAX_EXPANDED_NODES:
                return 'END'
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
