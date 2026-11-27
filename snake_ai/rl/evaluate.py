"""Load a trained PPO checkpoint, play some episodes and print score statistics.

Examples:
    snake-ai evaluate models/PPO-1686657037/990000.zip
    snake-ai evaluate models/PPO-1686657037/990000.zip --episodes 50 --no-render --seed 0
"""

import argparse
import statistics

from snake_ai.rl import import_ppo
from snake_ai.rl.snake_env import SnakeEnv


def add_arguments(parser):
    parser.add_argument("model", help="path to a checkpoint saved by snake-ai train (.zip)")
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


def check_arguments(parser, args):
    if args.episodes < 1:
        parser.error("--episodes must be at least 1")
    if args.max_steps is not None and args.max_steps < 1:
        parser.error("--max-steps must be at least 1")


def run(args):
    PPO = import_ppo()
    from stable_baselines3.common.utils import set_random_seed

    if args.seed is not None:
        set_random_seed(args.seed)  # Python's random (food), NumPy and PyTorch

    env = SnakeEnv()
    env.reset()
    if args.render:
        env.render_mode = "human"  # The environment then draws every step

    model = PPO.load(args.model, env=env)

    scores = []
    for episode in range(args.episodes):
        obs, _ = env.reset()
        done = False
        steps = 0
        while not done:
            action, _ = model.predict(obs)
            obs, reward, done, trunc, info = env.step(action)
            steps += 1
            if args.max_steps is not None and steps >= args.max_steps:
                break
        scores.append(env.score)
        print(f"Episode {episode + 1}: score {env.score}" + ("" if done else " (step limit)"))

    env.close()
    print(
        f"Episodes: {len(scores)}  Mean: {statistics.mean(scores):.2f}  "
        f"Min: {min(scores)}  Max: {max(scores)}"
    )
    return scores
