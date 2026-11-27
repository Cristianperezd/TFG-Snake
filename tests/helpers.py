import random
from pathlib import Path

from astar import AStar
from astar_node import AStarNode
from game import Game

GOLDEN_DIR = Path(__file__).resolve().parent / "golden"


class _NoWaitClock:
    """Replaces pygame's clock so tests do not wait 1/30 s per frame."""

    def tick(self, *args):
        return 0


def new_game(seed):
    random.seed(seed)
    game = Game()
    game.clock = _NoWaitClock()
    return game


def play_astar(seed, frames):
    """Play `frames` frames with the A* agent and return one line per frame:
    score, snake length, head position and food position."""
    game = new_game(seed)
    agent = AStar(AStarNode(game.board, game.snake, game.food))
    lines = []
    for _ in range(frames):
        result = game.step(agent)
        head = game.snake.body[0]
        lines.append(f"{game.score} {len(game.snake.body)} "
                     f"{int(head.x)},{int(head.y)} {int(game.food.pos.x)},{int(game.food.pos.y)}")
        if result:
            break
    return lines


def read_golden(name):
    return (GOLDEN_DIR / name).read_text().splitlines()
