import contextlib
import io

import pytest

from snake_ai.search.astar import AStar, AStarNode
from snake_ai.search.gbfs import GBFS, GBFSNode
from helpers import new_game, play_astar
from snake_ai.game.snake import is_out_of_bounds, next_position


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
    assert path not in (None, 'END')
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
