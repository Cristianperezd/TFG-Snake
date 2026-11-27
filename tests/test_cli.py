"""Tests for the command-line entry points and for how games end."""
import random

import pygame
import pytest

import evaluate_ppo
import main
import train_ppo
from astar_node import AStarNode
from game import Game
from gbfs_node import GBFSNode
from helpers import new_game, read_golden


# main.py: arguments

def test_main_defaults_play_one_astar_game_at_30_fps():
    args = main.parse_args([])
    assert args.agent == 'astar'
    assert args.games == 1
    assert args.fps == 30
    assert args.seed is None
    assert args.headless is False
    assert args.max_steps is None


def test_main_parses_all_options():
    args = main.parse_args(['--agent', 'gbfs', '--games', '50', '--fps', '0',
                            '--seed', '7', '--headless', '--max-steps', '100'])
    assert (args.agent, args.games, args.fps, args.seed, args.headless, args.max_steps) == \
        ('gbfs', 50, 0, 7, True, 100)


@pytest.mark.parametrize("argv", [
    ['--agent', 'ppo'],
    ['--games', '0'],
    ['--fps', '-1'],
    ['--max-steps', '0'],
    ['--agent', 'human', '--headless'],
])
def test_main_rejects_invalid_arguments(argv):
    with pytest.raises(SystemExit):
        main.parse_args(argv)


# main.py: running games

def test_headless_astar_run_plays_several_games(capsys):
    scores = main.main(['--games', '3', '--max-steps', '200', '--seed', '1', '--headless'])
    assert len(scores) == 3
    assert all(score > 0 for score in scores)
    out = capsys.readouterr().out
    assert "Game 3: score" in out
    assert "Games: 3  Mean:" in out


def test_seeded_run_reproduces_the_thesis_game():
    # The golden trace has 1,000 frames of the A* game with seed 1
    expected_score = int(read_golden("astar_seed1.txt")[-1].split()[0])
    args = main.parse_args(['--seed', '1', '--max-steps', '1000', '--headless'])
    assert main.run(args) == [expected_score]


def test_gbfs_plays_through_the_game_loop():
    random.seed(0)
    score, reason = main.play_game('gbfs', fps=0, render=False, max_steps=300)
    assert score > 0
    assert reason in ('step limit', 'no path')


@pytest.mark.parametrize("name,node_class", [('astar', AStarNode), ('gbfs', GBFSNode)])
def test_agents_replan_with_their_own_node_type(name, node_class):
    game = new_game(0)
    agent = main.make_agent(name, game)
    game.step(agent)
    assert type(agent.initial_node) is node_class


def test_human_agent_is_no_agent():
    assert main.make_agent('human', new_game(0)) is None


# Game over

def test_collision_ends_the_game_without_exiting():
    game = new_game(0)
    frames = 0
    while not game.step():  # nobody presses a key: the snake hits the top wall
        frames += 1
    assert game.game_over
    assert game.end_reason == 'collision'
    assert frames == 12
    assert pygame.get_init()  # the process and pygame are still running


def test_closing_the_window_ends_the_game():
    game = new_game(0)
    pygame.event.post(pygame.event.Event(pygame.QUIT))
    assert game.step() is True
    assert game.end_reason == 'window closed'


def test_a_new_game_can_start_after_game_over():
    game = new_game(0)
    while not game.step():
        pass
    game = Game(fps=0)
    assert not game.game_over
    assert game.step() is False


# PPO scripts (Stable Baselines 3 is only imported when they run)

def test_train_defaults_match_the_thesis_run():
    args = train_ppo.parse_args([])
    assert args.checkpoint_freq == 10_000
    assert args.timesteps == 499 * 10_000
    assert args.models_dir == 'models' and args.logs_dir == 'logs'
    assert args.run_name.startswith('PPO-')
    assert args.seed is None


def test_train_parses_options():
    args = train_ppo.parse_args(['--timesteps', '1000', '--checkpoint-freq', '500',
                                 '--run-name', 'test', '--models-dir', 'm', '--logs-dir', 'l',
                                 '--seed', '3'])
    assert (args.timesteps, args.checkpoint_freq, args.run_name, args.models_dir,
            args.logs_dir, args.seed) == (1000, 500, 'test', 'm', 'l', 3)


def test_evaluate_needs_a_model_path():
    with pytest.raises(SystemExit):
        evaluate_ppo.parse_args([])


def test_evaluate_defaults_and_options():
    args = evaluate_ppo.parse_args(['model.zip'])
    assert (args.model, args.episodes, args.render, args.seed, args.max_steps) == \
        ('model.zip', 50, True, None, None)
    args = evaluate_ppo.parse_args(['model.zip', '--episodes', '5', '--no-render',
                                    '--seed', '1', '--max-steps', '100'])
    assert (args.episodes, args.render, args.seed, args.max_steps) == (5, False, 1, 100)
