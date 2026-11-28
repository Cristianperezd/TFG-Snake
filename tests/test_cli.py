"""Tests for the command-line interface and for how games end."""

import random

import pygame
import pytest

from snake_ai import cli
from snake_ai.game.game import Game
from snake_ai.search.astar import AStarNode
from snake_ai.search.gbfs import GBFSNode

from helpers import new_game, read_golden

# snake-ai play: arguments


def test_play_defaults_to_one_astar_game_at_30_fps():
    args = cli.parse_args(["play"])
    assert args.agent == "astar"
    assert args.games == 1
    assert args.fps == 30
    assert args.seed is None
    assert args.headless is False
    assert args.max_steps is None


def test_play_parses_all_options():
    args = cli.parse_args(
        [
            "play",
            "--agent",
            "gbfs",
            "--games",
            "50",
            "--fps",
            "0",
            "--seed",
            "7",
            "--headless",
            "--max-steps",
            "100",
        ]
    )
    assert (args.agent, args.games, args.fps, args.seed, args.headless, args.max_steps) == (
        "gbfs",
        50,
        0,
        7,
        True,
        100,
    )


@pytest.mark.parametrize(
    "argv",
    [
        ["--agent", "ppo"],
        ["--games", "0"],
        ["--fps", "-1"],
        ["--max-steps", "0"],
        ["--agent", "human", "--headless"],
    ],
)
def test_play_rejects_invalid_arguments(argv):
    with pytest.raises(SystemExit):
        cli.parse_args(["play"] + argv)


# snake-ai play: running games


def test_headless_astar_run_plays_several_games(capsys):
    args = cli.parse_args(
        ["play", "--games", "3", "--max-steps", "200", "--seed", "1", "--headless"]
    )
    scores = cli.run_play(args)
    assert len(scores) == 3
    assert all(score > 0 for score in scores)
    out = capsys.readouterr().out
    assert "Game 3: score" in out
    assert "Games: 3  Mean:" in out


def test_seeded_run_reproduces_the_thesis_game():
    # The golden trace has 1,000 frames of the A* game with seed 1
    expected_score = int(read_golden("astar_seed1.txt")[-1].split()[0])
    args = cli.parse_args(["play", "--seed", "1", "--max-steps", "1000", "--headless"])
    assert cli.play(args) == [expected_score]


def test_gbfs_plays_through_the_game_loop():
    random.seed(0)
    score, reason = cli.play_game("gbfs", fps=0, render=False, max_steps=300)
    assert score > 0
    assert reason in ("step limit", "no path")


@pytest.mark.parametrize("name,node_class", [("astar", AStarNode), ("gbfs", GBFSNode)])
def test_agents_replan_with_their_own_node_type(name, node_class):
    game = new_game(0)
    agent = cli.make_agent(name, game)
    game.step(agent)
    assert type(agent.initial_node) is node_class


def test_human_agent_is_no_agent():
    assert cli.make_agent("human", new_game(0)) is None


# Game over


def test_collision_ends_the_game_without_exiting():
    game = new_game(0)
    frames = 0
    while not game.step():  # nobody presses a key: the snake hits the top wall
        frames += 1
    assert game.game_over
    assert game.end_reason == "collision"
    assert frames == 12
    assert pygame.get_init()  # the process and pygame are still running


def test_closing_the_window_ends_the_game():
    game = new_game(0)
    pygame.event.post(pygame.event.Event(pygame.QUIT))
    assert game.step() is True
    assert game.end_reason == "window closed"


def test_a_new_game_can_start_after_game_over():
    game = new_game(0)
    while not game.step():
        pass
    game = Game(fps=0)
    assert not game.game_over
    assert game.step() is False


# snake-ai train / evaluate (Stable Baselines 3 is only imported when they run)


def test_train_defaults_match_the_thesis_run():
    args = cli.parse_args(["train"])
    assert args.checkpoint_freq == 10_000
    assert args.timesteps == 499 * 10_000
    assert args.models_dir == "models" and args.logs_dir == "logs"
    assert args.run_name.startswith("PPO-")
    assert args.seed is None


def test_train_parses_options():
    args = cli.parse_args(
        [
            "train",
            "--timesteps",
            "1000",
            "--checkpoint-freq",
            "500",
            "--run-name",
            "test",
            "--models-dir",
            "m",
            "--logs-dir",
            "l",
            "--seed",
            "3",
        ]
    )
    assert (
        args.timesteps,
        args.checkpoint_freq,
        args.run_name,
        args.models_dir,
        args.logs_dir,
        args.seed,
    ) == (1000, 500, "test", "m", "l", 3)


def test_evaluate_defaults_to_the_pretrained_model():
    from snake_ai.rl import PRETRAINED_MODEL

    args = cli.parse_args(["evaluate"])
    assert args.model == str(PRETRAINED_MODEL)


def test_pretrained_model_is_shipped():
    from snake_ai.rl import PRETRAINED_MODEL

    assert PRETRAINED_MODEL.is_file()
    assert PRETRAINED_MODEL.stat().st_size < 1_000_000


def test_evaluate_reports_a_missing_model_file(tmp_path):
    with pytest.raises(SystemExit, match="Model file not found"):
        cli.main(["evaluate", str(tmp_path / "missing.zip"), "--no-render"])


def test_pretrained_model_plays(capsys):
    pytest.importorskip("stable_baselines3")  # Not installed on CI
    cli.main(["evaluate", "--episodes", "2", "--no-render", "--seed", "0", "--max-steps", "2000"])
    assert "Episodes: 2" in capsys.readouterr().out


def test_evaluate_defaults_and_options():
    args = cli.parse_args(["evaluate", "model.zip"])
    assert (args.model, args.episodes, args.render, args.seed, args.max_steps) == (
        "model.zip",
        50,
        True,
        None,
        None,
    )
    args = cli.parse_args(
        [
            "evaluate",
            "model.zip",
            "--episodes",
            "5",
            "--no-render",
            "--seed",
            "1",
            "--max-steps",
            "100",
        ]
    )
    assert (args.episodes, args.render, args.seed, args.max_steps) == (5, False, 1, 100)


# Window controls: pause, quit and the game-over message (drawing only)


def key_event(key):
    return pygame.event.Event(pygame.KEYDOWN, key=key)


def test_escape_ends_the_game_like_closing_the_window():
    game = new_game(0)
    pygame.event.post(key_event(pygame.K_ESCAPE))
    assert game.step() is True
    assert game.end_reason == "window closed"


def test_space_pauses_until_pressed_again_without_changing_the_game():
    random.seed(5)
    paused = Game(fps=0)
    random.seed(5)
    normal = Game(fps=0, render=False)
    pygame.event.clear()
    pygame.event.post(key_event(pygame.K_SPACE))
    # Resume after 100 ms
    pygame.time.set_timer(key_event(pygame.K_SPACE), 100, loops=1)
    start = pygame.time.get_ticks()
    assert paused.step() is False
    assert pygame.time.get_ticks() - start >= 90
    assert normal.step() is False
    assert paused.snake.body == normal.snake.body
    assert paused.food.pos == normal.food.pos


def test_escape_while_paused_quits():
    game = new_game(0)
    pygame.event.clear()
    pygame.event.post(key_event(pygame.K_SPACE))
    pygame.time.set_timer(key_event(pygame.K_ESCAPE), 50, loops=1)
    assert game.step() is True
    assert game.end_reason == "window closed"


def test_space_does_not_pause_without_a_window():
    random.seed(0)
    game = Game(fps=0, render=False)
    pygame.event.post(key_event(pygame.K_SPACE))
    assert game.step() is False


def test_game_over_message_waits_and_can_be_skipped_or_quit():
    game = new_game(0)
    while not game.step():
        pass
    assert game.show_game_over(0) is True  # just drawn
    pygame.event.post(key_event(pygame.K_RETURN))
    assert game.show_game_over(5) is True  # skipped at once
    pygame.event.post(key_event(pygame.K_ESCAPE))
    assert game.show_game_over(5) is False


def test_play_with_a_window_and_no_frame_limit_skips_the_game_over_delay(capsys):
    args = cli.parse_args(
        ["play", "--games", "2", "--max-steps", "50", "--seed", "1", "--fps", "0"]
    )
    assert args.game_over_delay == 1.5
    start = pygame.time.get_ticks()
    assert len(cli.play(args)) == 2
    assert pygame.time.get_ticks() - start < 1500
    assert "Game 2: score" in capsys.readouterr().out


def test_window_and_headless_runs_give_the_same_scores():
    argv = ["play", "--games", "2", "--max-steps", "300", "--seed", "4", "--fps", "0"]
    assert cli.play(cli.parse_args(argv)) == cli.play(cli.parse_args(argv + ["--headless"]))


def test_game_over_delay_must_not_be_negative():
    with pytest.raises(SystemExit):
        cli.parse_args(["play", "--game-over-delay", "-1"])
    assert cli.parse_args(["play", "--game-over-delay", "0"]).game_over_delay == 0
