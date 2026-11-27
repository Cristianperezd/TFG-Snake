from node import Node


class AStarNode(Node):
    """Node ordered by total cost g + h."""

    def __lt__(self, other):
        return self.cost < other.cost
