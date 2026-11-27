import random
from pathlib import Path

from snake_ai.search.astar import AStar, AStarNode
from snake_ai.game.game import Game

GOLDEN_DIR = Path(__file__).resolve().parent / "golden"


def new_game(seed):
    """New game with a fixed seed and no frame limit, so tests do not wait 1/30 s per frame."""
    random.seed(seed)
    return Game(fps=0)


def play_astar(seed, frames):
    """Play `frames` frames with the A* agent and return one line per frame:
    score, snake length, head position and food position."""
    game = new_game(seed)
    agent = AStar(AStarNode(game.board, game.snake, game.food))
    lines = []
    for _ in range(frames):
        game_over = game.step(agent)
        head = game.snake.body[0]
        lines.append(f"{game.score} {len(game.snake.body)} "
                     f"{int(head.x)},{int(head.y)} {int(game.food.pos.x)},{int(game.food.pos.y)}")
        if game_over:
            break
    return lines


def read_golden(name):
    return (GOLDEN_DIR / name).read_text().splitlines()
