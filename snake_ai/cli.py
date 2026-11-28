"""Command-line interface: `snake-ai play`, `snake-ai train` and `snake-ai evaluate`.

Examples:
    snake-ai play                                   # A* plays one game in a window
    snake-ai play --agent human                     # play with the arrow keys
                                                    # (Space pauses, Esc quits)
    snake-ai play --agent gbfs --games 5 --fps 60
    snake-ai play --show-path                       # draw A*'s path and explored cells
    snake-ai play --games 50 --headless             # thesis evaluation, no window
    snake-ai train --timesteps 200000 --run-name quick --seed 0
    snake-ai evaluate models/quick/200000.zip --episodes 10 --no-render

`python -m snake_ai` works the same way. Training and evaluation need the
`rl` extra (Stable Baselines 3), which is only imported when they run.
"""

import argparse
import os
import random
import statistics

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pygame  # noqa: E402

from snake_ai import __version__  # noqa: E402
from snake_ai.game import constants  # noqa: E402
from snake_ai.game.game import Game  # noqa: E402
from snake_ai.rl import evaluate, train  # noqa: E402
from snake_ai.search.astar import AStar  # noqa: E402
from snake_ai.search.gbfs import GBFS  # noqa: E402

AGENTS = {"human": None, "gbfs": GBFS, "astar": AStar}
AGENT_NAMES = {"human": "Human", "gbfs": "GBFS", "astar": "A*"}


def positive_int(value):
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError(f"must be at least 1, got {value}")
    return number


def non_negative_float(value):
    number = float(value)
    if not number >= 0:
        raise argparse.ArgumentTypeError(f"must be 0 or more, got {value}")
    return number


def non_negative_int(value):
    number = int(value)
    if number < 0:
        raise argparse.ArgumentTypeError(f"must be 0 or more, got {value}")
    return number


# snake-ai play


def add_play_arguments(parser):
    parser.add_argument(
        "--agent", choices=AGENTS, default="astar", help="who plays (default: %(default)s)"
    )
    parser.add_argument(
        "--games",
        type=positive_int,
        default=1,
        help="number of games to play; the thesis used 50 (default: %(default)s)",
    )
    parser.add_argument(
        "--fps",
        type=non_negative_int,
        default=constants.FPS,
        help="frames per second in the window, 0 = no limit (default: %(default)s)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="random seed for the food positions, for reproducible runs",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="run without a window and without frame limit (not for --agent human)",
    )
    parser.add_argument(
        "--max-steps",
        type=positive_int,
        default=None,
        help="stop a game after this many frames (default: no limit)",
    )
    parser.add_argument(
        "--show-path",
        action="store_true",
        help="draw the path the search agent plans and the cells its search explores",
    )
    parser.add_argument(
        "--game-over-delay",
        type=non_negative_float,
        default=1.5,
        metavar="SECONDS",
        help="how long the game-over message stays in the window; skipped with --fps 0 "
        "and --headless (default: %(default)s)",
    )


def check_play_arguments(parser, args):
    if args.headless and args.agent == "human":
        parser.error("--headless cannot be used with --agent human")
    if args.show_path and args.agent == "human":
        parser.error("--show-path needs a search agent (gbfs or astar)")


def make_agent(name, game):
    """Return a search agent for `game`, or None for a human player."""
    agent_class = AGENTS[name]
    if agent_class is None:
        return None
    return agent_class(agent_class.node_class(game.board, game.snake, game.food))


def run_game(agent_name, fps=constants.FPS, render=True, max_steps=None, hud=None, show_path=False):
    """Play one game and return the finished `Game` (see `score` and `end_reason`).

    `hud` is shown in the side panel of the window and `show_path` draws the
    agent's search (see `Game`)."""
    hud = {"agent": AGENT_NAMES[agent_name], **(hud or {})}
    game = Game(fps=fps, render=render, hud=hud, show_path=show_path)
    agent = make_agent(agent_name, game)
    steps = 0
    while not game.step(agent):
        steps += 1
        if max_steps is not None and steps >= max_steps:
            game.end_reason = "step limit"
            break
    return game


def play_game(agent_name, fps=constants.FPS, render=True, max_steps=None, hud=None):
    """Play one game. Return (score, end reason)."""
    game = run_game(agent_name, fps=fps, render=render, max_steps=max_steps, hud=hud)
    return game.score, game.end_reason


def play(args):
    """Play `args.games` games, printing each score. Return the list of scores."""
    if args.headless:
        # Must be set before the first Game opens the display
        os.environ["SDL_VIDEODRIVER"] = "dummy"
    if args.seed is not None:
        random.seed(args.seed)

    fps = 0 if args.headless else args.fps
    render = not args.headless
    scores = []
    for i in range(args.games):
        hud = {
            "game": i + 1,
            "games": args.games,
            "best": max(scores) if scores else None,
            "mean": statistics.mean(scores) if scores else None,
        }
        game = run_game(
            args.agent,
            fps=fps,
            render=render,
            max_steps=args.max_steps,
            hud=hud,
            show_path=args.show_path,
        )
        if game.end_reason == "window closed":
            print("Window closed, stopping.")
            break
        scores.append(game.score)
        print(f"Game {i + 1}: score {game.score} ({game.end_reason})")
        if render and not game.show_game_over(args.game_over_delay if fps > 0 else 0):
            print("Window closed, stopping.")
            break
    return scores


def print_summary(scores):
    if not scores:
        return
    print(
        f"Games: {len(scores)}  Mean: {statistics.mean(scores):.2f}  "
        f"Min: {min(scores)}  Max: {max(scores)}"
    )


def run_play(args):
    try:
        scores = play(args)
    finally:
        pygame.quit()
    print_summary(scores)
    return scores


# Argument parsing and entry point

COMMANDS = {
    # name: (help, add arguments, check arguments, run)
    "play": (
        "play Snake yourself or let a search agent (GBFS or A*) play",
        add_play_arguments,
        check_play_arguments,
        run_play,
    ),
    "train": (
        "train a PPO agent on the Snake environment (needs the rl extra)",
        train.add_arguments,
        train.check_arguments,
        train.run,
    ),
    "evaluate": (
        "evaluate a trained PPO agent on Snake (needs the rl extra)",
        evaluate.add_arguments,
        evaluate.check_arguments,
        evaluate.run,
    ),
}


def build_parser():
    """Return the top-level parser and a dict with the parser of each command."""
    parser = argparse.ArgumentParser(
        prog="snake-ai", description="Snake played by search agents (GBFS, A*) and a PPO agent."
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    commands = parser.add_subparsers(dest="command", metavar="COMMAND", required=True)
    subparsers = {}
    for name, (help_text, add_arguments, _, _) in COMMANDS.items():
        description = help_text[0].upper() + help_text[1:] + "."
        subparsers[name] = commands.add_parser(name, help=help_text, description=description)
        add_arguments(subparsers[name])
    return parser, subparsers


def parse_args(argv=None):
    parser, subparsers = build_parser()
    args = parser.parse_args(argv)
    check_arguments = COMMANDS[args.command][2]
    check_arguments(subparsers[args.command], args)
    return args


def main(argv=None):
    args = parse_args(argv)
    COMMANDS[args.command][3](args)
    return 0
