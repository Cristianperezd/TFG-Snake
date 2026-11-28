"""Who can play: the human player and the search agents, by name.

Kept apart from the command line so it can be used without importing the RL
code (and with it Gymnasium), e.g. in the browser version.
"""

from snake_ai.search.astar import AStar
from snake_ai.search.gbfs import GBFS

AGENTS = {"human": None, "gbfs": GBFS, "astar": AStar}
AGENT_NAMES = {"human": "Human", "gbfs": "GBFS", "astar": "A*"}


def make_agent(name, game):
    """Return a search agent for `game`, or None for a human player."""
    agent_class = AGENTS[name]
    if agent_class is None:
        return None
    return agent_class(agent_class.node_class(game.board, game.snake, game.food))
