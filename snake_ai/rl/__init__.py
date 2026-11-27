"""Reinforcement learning: the Gymnasium environment and the PPO scripts.

Stable Baselines 3 is only imported when training or evaluating, so the
environment and the search agents can be used without it.
"""

from snake_ai.rl.snake_env import SnakeEnv

__all__ = ["SnakeEnv", "import_ppo"]


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
