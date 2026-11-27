"""Regression tests against the original thesis code.

The files in tests/golden/ were recorded by running the code at tag v1.1.0
(the thesis implementation) with fixed random seeds. These tests check that
the current code still produces exactly the same games, paths and
observations, so refactors cannot silently change the agents' behaviour.
"""

import contextlib
import io
import random

import pytest

from snake_ai.rl.snake_env import SnakeEnv
from snake_ai.search.gbfs import GBFS, GBFSNode

from helpers import new_game, play_astar, read_golden


@pytest.mark.parametrize("seed", [1, 7, 42])
def test_astar_game_matches_thesis_code(seed):
    expected = read_golden(f"astar_seed{seed}.txt")
    actual = play_astar(seed, frames=len(expected))
    for frame, (exp, act) in enumerate(zip(expected, actual)):
        assert act == exp, f"first difference at frame {frame}"
    assert len(actual) == len(expected)


def test_gbfs_paths_match_thesis_code():
    for line in read_golden("gbfs_paths.txt"):
        seed, expected_path = line.split()
        game = new_game(int(seed))
        with contextlib.redirect_stdout(io.StringIO()):
            path = GBFS(GBFSNode(game.board, game.snake, game.food)).search()
        assert ",".join(path) == expected_path, f"seed {seed}"


def greedy_action(obs, rng):
    """Simple policy that moves towards the food when it is safe, so that the
    recorded episodes include eating, growing and dying."""
    wanted = [
        a for a, f in [(2, obs[0]), (3, obs[1]), (0, obs[2]), (1, obs[3])] if f and obs[5 + a]
    ]
    safe = [a for a in range(4) if obs[5 + a]]
    return rng.choice(wanted or safe or [0])


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_env_episode_matches_thesis_code(seed):
    expected = read_golden(f"env_seed{seed}.txt")

    random.seed(seed)
    rng = random.Random(seed + 100)
    env = SnakeEnv()
    obs, _ = env.reset()
    actual = [" ".join(str(int(v)) for v in obs)]
    for _ in range(500):
        obs, reward, done, _, _ = env.step(greedy_action(obs, rng))
        actual.append(f"{' '.join(str(int(v)) for v in obs)} {reward} {int(done)}")
        if done:
            break

    assert actual == expected
