import numpy as np

from snake_env import SnakeEnv


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
