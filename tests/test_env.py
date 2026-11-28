import random

import numpy as np
import pytest

from snake_ai.game import colors, constants
from snake_ai.rl.snake_env import SnakeEnv


def test_reset_returns_valid_observation():
    env = SnakeEnv()
    obs, info = env.reset()
    assert obs.shape == (9,)
    assert obs.dtype == np.float32
    assert env.observation_space.contains(obs)
    assert info == {}


def test_step_returns_gymnasium_tuple():
    env = SnakeEnv()
    env.reset()
    obs, reward, terminated, truncated, info = env.step(0)
    assert env.observation_space.contains(obs)
    assert terminated is False and truncated is False
    assert obs[4] == 0  # last action


def test_dying_gives_negative_reward_and_ends_episode():
    env = SnakeEnv()
    env.reset()
    for _ in range(50):
        obs, reward, terminated, _, _ = env.step(0)  # keep going up into the wall
        if terminated:
            break
    assert terminated
    assert reward == -10


def test_eating_increases_score_and_reward():
    env = SnakeEnv()
    env.reset()
    head = env.snake.get_head()
    env.food.pos = head - (0, 20)  # put the food right above the head
    _, reward, terminated, _, _ = env.step(0)
    assert not terminated
    assert env.score == 1
    assert reward == 10


def test_safe_directions_at_start():
    env = SnakeEnv()
    obs, _ = env.reset()
    # Up, left and right are free; down is the snake's own body
    assert list(obs[5:]) == [1, 0, 1, 1]


# Gymnasium API


def test_passes_gymnasium_env_checker():
    from gymnasium.utils.env_checker import check_env

    check_env(SnakeEnv(), skip_render_check=True)
    check_env(SnakeEnv(render_mode="rgb_array"))


def test_rejects_unknown_render_mode():
    with pytest.raises(ValueError):
        SnakeEnv(render_mode="ascii")


def play_seeded_episode(env, seed, steps=200):
    """Reset with `seed` and play a fixed action sequence; return what happened."""
    obs, _ = env.reset(seed=seed)
    trace = [tuple(obs)]
    actions = [0, 2, 1, 3]
    for i in range(steps):
        obs, reward, terminated, truncated, _ = env.step(actions[(i // 3) % 4])
        trace.append((tuple(obs), reward, terminated))
        if terminated or truncated:
            break
    return trace, (env.food.pos.x, env.food.pos.y)


def test_seeded_resets_are_reproducible():
    env = SnakeEnv()
    first = play_seeded_episode(env, seed=3)
    random.random()  # Using the random module in between must not matter
    assert play_seeded_episode(env, seed=3) == first
    assert play_seeded_episode(SnakeEnv(), seed=3) == first


def test_different_seeds_place_the_food_differently():
    foods = set()
    for seed in range(10):
        env = SnakeEnv()
        env.reset(seed=seed)
        foods.add((env.food.pos.x, env.food.pos.y))
    assert len(foods) > 1


def test_unseeded_reset_uses_the_global_random_state():
    # Thesis behaviour: reset() without a seed follows Python's random module
    random.seed(5)
    env = SnakeEnv()
    env.reset()
    unseeded = (env.food.pos.x, env.food.pos.y)
    env.reset(seed=5)
    assert (env.food.pos.x, env.food.pos.y) == unseeded


def test_no_truncation_by_default():
    env = SnakeEnv()
    env.reset(seed=0)
    for action in [2, 0, 3, 1] * 25:  # Moves in a small square, never dies
        _, _, terminated, truncated, _ = env.step(action)
        assert not terminated and not truncated


def test_truncates_after_max_episode_steps():
    env = SnakeEnv(max_episode_steps=10)
    env.reset(seed=0)
    for step in range(1, 11):
        _, _, terminated, truncated, _ = env.step([2, 0, 3, 1][step % 4])
        assert not terminated
        assert truncated == (step == 10)
    env.reset(seed=0)
    _, _, _, truncated, _ = env.step(2)
    assert not truncated  # The step counter starts again on reset


def test_dying_on_the_last_step_is_termination_not_truncation():
    env = SnakeEnv(max_episode_steps=13)
    env.reset(seed=0)
    for _ in range(13):  # The head starts 12 rows below the top wall
        _, _, terminated, truncated, _ = env.step(0)
    assert terminated and not truncated


def test_rejects_invalid_max_episode_steps():
    with pytest.raises(ValueError):
        SnakeEnv(max_episode_steps=0)


def test_rgb_array_render_returns_the_frame():
    env = SnakeEnv(render_mode="rgb_array")
    env.reset(seed=0)
    frame = env.render()
    # The board (500 x 500) and the side panel to its right
    assert frame.shape == (constants.WINDOW_HEIGHT, constants.WINDOW_WIDTH, 3)
    assert frame.shape == (500, 700, 3)
    assert frame.dtype == np.uint8
    head = env.snake.get_head()
    food = env.food.pos
    middle = constants.BLOCK // 2
    assert tuple(frame[int(head.y) + middle, int(head.x) + middle]) == colors.SNAKE_HEAD
    assert tuple(frame[int(food.y) + middle, int(food.x) + middle]) == colors.FOOD


def test_render_without_render_mode_returns_none():
    env = SnakeEnv()
    env.reset(seed=0)
    assert env.render() is None
    assert env.display is None


def test_human_render_mode_draws_every_step():
    env = SnakeEnv(render_mode="human")
    env.reset(seed=0)
    assert env.display is not None
    env.step(0)
    env.close()
    assert env.display is None


def test_registered_with_gymnasium():
    import gymnasium as gym

    from snake_ai.rl import ENV_ID

    env = gym.make(ENV_ID, render_mode="rgb_array", max_episode_steps=5)
    obs, _ = env.reset(seed=1)
    assert env.observation_space.contains(obs)
    assert env.render().shape == (500, 700, 3)
    truncated = False
    for _ in range(5):
        _, _, terminated, truncated, _ = env.step(2)
    assert truncated and not terminated
    env.close()
