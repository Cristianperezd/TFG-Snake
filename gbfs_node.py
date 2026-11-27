from node import Node


class GBFSNode(Node):
    """Node ordered by the heuristic h only."""

    def __lt__(self, other):
        return self.h < other.h
