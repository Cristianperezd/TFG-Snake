"""Load a trained PPO checkpoint, play some episodes and print score statistics.

Without a MODEL argument the pretrained agent shipped with the package is used.

Examples:
    snake-ai evaluate                                     # the pretrained agent
    snake-ai evaluate models/PPO-1686657037/990000.zip
    snake-ai evaluate models/PPO-1686657037/990000.zip --episodes 50 --no-render --seed 0
"""

import argparse
import os
import statistics

from snake_ai.rl import PRETRAINED_MODEL, import_ppo
from snake_ai.rl.snake_env import SnakeEnv


def add_arguments(parser):
    parser.add_argument(
        "model",
        nargs="?",
        default=str(PRETRAINED_MODEL),
        help="checkpoint saved by snake-ai train (.zip); default: the pretrained agent",
    )
    parser.add_argument(
        "--episodes", type=int, default=50, help="number of episodes to play (default: %(default)s)"
    )
    parser.add_argument(
        "--render",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="show the game in a window (default: on)",
    )
    parser.add_argument(
        "--seed", type=int, default=None, help="random seed for the policy and the food positions"
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=None,
        help="stop an episode after this many steps (default: no limit)",
    )
    parser.add_argument(
        "--game-over-delay",
        type=float,
        default=1.5,
        metavar="SECONDS",
        help="how long the game-over message stays in the window (default: %(default)s)",
    )


def check_arguments(parser, args):
    if args.episodes < 1:
        parser.error("--episodes must be at least 1")
    if args.max_steps is not None and args.max_steps < 1:
        parser.error("--max-steps must be at least 1")
    if not args.game_over_delay >= 0:
        parser.error("--game-over-delay must be 0 or more")


def run(args):
    if not os.path.isfile(args.model):
        raise SystemExit(f"Model file not found: {args.model}")
    PPO = import_ppo()
    from stable_baselines3.common.utils import set_random_seed

    if args.seed is not None:
        set_random_seed(args.seed)  # Python's random (food), NumPy and PyTorch

    env = SnakeEnv(render_mode="human" if args.render else None, max_episode_steps=args.max_steps)
    model = PPO.load(args.model, device="cpu")

    scores = []
    for episode in range(args.episodes):
        env.hud = {
            "episode": episode + 1,
            "episodes": args.episodes,
            "best": max(scores) if scores else None,
            "mean": statistics.mean(scores) if scores else None,
        }
        # Seeding the first reset is enough: later resets continue the same sequence
        obs, _ = env.reset(seed=args.seed if episode == 0 else None)
        terminated = truncated = False
        while not (terminated or truncated or env.quit_requested):
            action, _ = model.predict(obs)
            obs, _, terminated, truncated, _ = env.step(action)
        if env.quit_requested:
            print("Window closed, stopping.")
            break
        scores.append(env.score)
        print(f"Episode {episode + 1}: score {env.score}" + (" (step limit)" if truncated else ""))
        reason = "step limit" if truncated else "collision"
        if not env.show_game_over(reason, args.game_over_delay):
            print("Window closed, stopping.")
            break

    env.close()
    if not scores:
        return scores
    print(
        f"Episodes: {len(scores)}  Mean: {statistics.mean(scores):.2f}  "
        f"Min: {min(scores)}  Max: {max(scores)}"
    )
    return scores
