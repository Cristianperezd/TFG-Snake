"""Play Snake yourself or watch a search agent play, and print score statistics.

Examples:
    python main.py                                  # A* plays one game in a window
    python main.py --agent human                    # play with the arrow keys
    python main.py --agent gbfs --games 5 --fps 60
    python main.py --games 50 --headless            # thesis evaluation, no window
"""
import argparse
import os
import random
import statistics

os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT', '1')

import pygame  # noqa: E402

from snake_ai.game import constants
from snake_ai.game.game import Game
from snake_ai.search.astar import AStar
from snake_ai.search.gbfs import GBFS

AGENTS = {'human': None, 'gbfs': GBFS, 'astar': AStar}


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Play Snake yourself or let a search agent (GBFS or A*) play.")
    parser.add_argument('--agent', choices=AGENTS, default='astar',
                        help="who plays (default: %(default)s)")
    parser.add_argument('--games', type=positive_int, default=1,
                        help="number of games to play; the thesis used 50 (default: %(default)s)")
    parser.add_argument('--fps', type=non_negative_int, default=constants.FPS,
                        help="frames per second in the window, 0 = no limit (default: %(default)s)")
    parser.add_argument('--seed', type=int, default=None,
                        help="random seed for the food positions, for reproducible runs")
    parser.add_argument('--headless', action='store_true',
                        help="run without a window and without frame limit (not for --agent human)")
    parser.add_argument('--max-steps', type=positive_int, default=None,
                        help="stop a game after this many frames (default: no limit)")
    args = parser.parse_args(argv)
    if args.headless and args.agent == 'human':
        parser.error("--headless cannot be used with --agent human")
    return args


def positive_int(value):
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError(f"must be at least 1, got {value}")
    return number


def non_negative_int(value):
    number = int(value)
    if number < 0:
        raise argparse.ArgumentTypeError(f"must be 0 or more, got {value}")
    return number


def make_agent(name, game):
    """Return a search agent for `game`, or None for a human player."""
    agent_class = AGENTS[name]
    if agent_class is None:
        return None
    return agent_class(agent_class.node_class(game.board, game.snake, game.food))


def play_game(agent_name, fps=constants.FPS, render=True, max_steps=None):
    """Play one game. Return (score, end reason)."""
    game = Game(fps=fps, render=render)
    agent = make_agent(agent_name, game)
    steps = 0
    while not game.step(agent):
        steps += 1
        if max_steps is not None and steps >= max_steps:
            return game.score, 'step limit'
    return game.score, game.end_reason


def run(args):
    """Play `args.games` games, printing each score. Return the list of scores."""
    if args.headless:
        # Must be set before the first Game opens the display
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
    if args.seed is not None:
        random.seed(args.seed)

    fps = 0 if args.headless else args.fps
    scores = []
    for i in range(args.games):
        score, reason = play_game(args.agent, fps=fps, render=not args.headless,
                                  max_steps=args.max_steps)
        if reason == 'window closed':
            print("Window closed, stopping.")
            break
        scores.append(score)
        print(f"Game {i + 1}: score {score} ({reason})")
    return scores


def print_summary(scores):
    if not scores:
        return
    print(f"Games: {len(scores)}  Mean: {statistics.mean(scores):.2f}  "
          f"Min: {min(scores)}  Max: {max(scores)}")


def main(argv=None):
    args = parse_args(argv)
    try:
        scores = run(args)
    finally:
        pygame.quit()
    print_summary(scores)
    return scores


if __name__ == '__main__':
    main()
