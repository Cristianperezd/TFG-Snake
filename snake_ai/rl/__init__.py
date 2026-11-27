"""Reinforcement learning: the Gymnasium environment and the PPO scripts.

Stable Baselines 3 is only imported when training or evaluating, so the
environment can be used without it.
"""

from snake_ai.rl.snake_env import SnakeEnv

__all__ = ["SnakeEnv"]
