import contextlib
import io
import os
import subprocess
import sys

import pytest

from snake_ai import agents
from snake_ai.game.snake import is_out_of_bounds, next_position
from snake_ai.search.astar import AStar, AStarNode
from snake_ai.search.gbfs import GBFS, GBFSNode

from helpers import new_game, play_astar


def follow(game, path):
    """Apply a path (skipping the initial direction) to a copy of the snake and
    check every step is legal. Return the final head position."""
    head = game.snake.get_head()
    body = list(game.snake.body)
    for direction in path[1:]:
        head = next_position(head, direction)
        assert not is_out_of_bounds(head)
        assert head not in body[:-1]
        body = [head] + body[:-1]
    return head


@pytest.mark.parametrize("agent_cls,node_cls", [(AStar, AStarNode), (GBFS, GBFSNode)])
@pytest.mark.parametrize("seed", range(5))
def test_search_finds_a_legal_path_to_the_food(agent_cls, node_cls, seed):
    game = new_game(seed)
    with contextlib.redirect_stdout(io.StringIO()):
        path = agent_cls(node_cls(game.board, game.snake, game.food)).search()
    assert path not in (None, "END")
    assert follow(game, path) == game.food.pos


def test_astar_path_is_shortest_on_empty_board():
    game = new_game(0)
    path = AStar(AStarNode(game.board, game.snake, game.food)).search()
    head, food = game.snake.get_head(), game.food.pos
    manhattan = (abs(head.x - food.x) + abs(head.y - food.y)) / 20
    assert len(path) - 1 == manhattan


def test_astar_keeps_eating():
    lines = play_astar(seed=3, frames=600)
    final_score = int(lines[-1].split()[0])
    assert final_score >= 20


def test_agents_can_be_used_without_the_rl_code():
    """The browser version has no PyTorch or Gymnasium: the agent registry and
    the game must not import `snake_ai.rl`."""
    code = (
        "import sys; import snake_ai.agents, snake_ai.game.game; "
        "loaded = [m for m in sys.modules if m.startswith(('snake_ai.rl', 'gymnasium'))]; "
        "assert not loaded, loaded"
    )
    env = dict(os.environ, SDL_VIDEODRIVER="dummy")
    subprocess.run([sys.executable, "-c", code], check=True, env=env, timeout=50)


def test_make_agent_builds_each_search_agent_with_its_node_type():
    game = new_game(0)
    assert type(agents.make_agent("astar", game)) is AStar
    assert type(agents.make_agent("gbfs", game).initial_node) is GBFSNode
    assert agents.make_agent("human", game) is None
