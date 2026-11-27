"""Train a PPO agent on SnakeEnv, saving a checkpoint every --checkpoint-freq steps.

Examples:
    snake-ai train                                        # same run as the thesis (~5M steps)
    snake-ai train --timesteps 200000 --run-name quick-test --seed 0

Checkpoints go to <models-dir>/<run-name>/<steps>.zip and TensorBoard logs to
<logs-dir>/<run-name>/.
"""
import argparse
import math
import os
import time

from snake_ai.rl import import_ppo
from snake_ai.rl.snake_env import SnakeEnv

# The thesis run: 499 checkpoints of 10,000 steps
DEFAULT_TIMESTEPS = 4_990_000
DEFAULT_CHECKPOINT_FREQ = 10_000


def add_arguments(parser):
    parser.add_argument('--timesteps', type=int, default=DEFAULT_TIMESTEPS,
                        help="total training steps (default: %(default)s)")
    parser.add_argument('--checkpoint-freq', type=int, default=DEFAULT_CHECKPOINT_FREQ,
                        help="save a checkpoint every this many steps (default: %(default)s)")
    parser.add_argument('--run-name', default=None,
                        help="name of the run folder (default: PPO-<timestamp>)")
    parser.add_argument('--models-dir', default='models',
                        help="where checkpoints are saved (default: %(default)s)")
    parser.add_argument('--logs-dir', default='logs',
                        help="where TensorBoard logs are saved (default: %(default)s)")
    parser.add_argument('--seed', type=int, default=None,
                        help="random seed for PPO and the food positions")


def check_arguments(parser, args):
    if args.timesteps < 1 or args.checkpoint_freq < 1:
        parser.error("--timesteps and --checkpoint-freq must be at least 1")
    if args.run_name is None:
        args.run_name = f"PPO-{int(time.time())}"


def run(args):
    PPO = import_ppo()

    models_dir = os.path.join(args.models_dir, args.run_name)
    log_dir = os.path.join(args.logs_dir, args.run_name)
    os.makedirs(models_dir, exist_ok=True)
    os.makedirs(log_dir, exist_ok=True)

    env = SnakeEnv()
    env.reset()

    model = PPO('MlpPolicy', env, verbose=1, tensorboard_log=log_dir, seed=args.seed)

    for i in range(1, math.ceil(args.timesteps / args.checkpoint_freq) + 1):
        steps = min(i * args.checkpoint_freq, args.timesteps)
        chunk = steps - (i - 1) * args.checkpoint_freq
        model.learn(total_timesteps=chunk, reset_num_timesteps=False, tb_log_name="PPO")
        model.save(os.path.join(models_dir, str(steps)))

    env.close()
    print(f"Checkpoints saved in {models_dir}")
