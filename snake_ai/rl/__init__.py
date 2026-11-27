"""Reinforcement learning: the Gymnasium environment and the PPO scripts.

Stable Baselines 3 is only imported when training or evaluating, so the
environment and the search agents can be used without it.

Importing this package registers the environment with Gymnasium as
`SnakeAI-v0`, so `gymnasium.make("SnakeAI-v0", render_mode="rgb_array")` works.
"""

from pathlib import Path

import gymnasium as gym

from snake_ai.rl.snake_env import SnakeEnv

__all__ = ["ENV_ID", "PRETRAINED_MODEL", "SnakeEnv", "import_ppo"]

ENV_ID = "SnakeAI-v0"

# PPO agent trained with the thesis configuration, shipped with the package
PRETRAINED_MODEL = Path(__file__).parent / "pretrained" / "ppo_snake.zip"

if ENV_ID not in gym.envs.registry:
    gym.register(id=ENV_ID, entry_point="snake_ai.rl.snake_env:SnakeEnv")


def import_ppo():
    """Import and return Stable Baselines 3's PPO, with a clear error if it is missing."""
    try:
        from stable_baselines3 import PPO
    except ImportError as error:
        raise SystemExit(
            "PPO training and evaluation need Stable Baselines 3. "
            'Install the rl extra: pip install -e ".[rl]"'
        ) from error
    return PPO
