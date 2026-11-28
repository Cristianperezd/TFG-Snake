"""Tests for the browser version's state machine (snake_ai.browser), run without a browser."""

import random

import pygame
import pytest

from snake_ai import browser
from snake_ai.browser import App
from snake_ai.search.astar import AStar
from snake_ai.search.gbfs import GBFS

from helpers import read_golden


def press(app, key, now=0):
    app.handle_event(pygame.event.Event(pygame.KEYDOWN, key=key), now)


def started(agent_name, seed=0):
    app = App()
    random.seed(seed)
    app.choose(agent_name, 0)
    return app


def play_frames(app, frames, start=0):
    """Call `update` so that exactly one game frame is due each time. Return the time reached."""
    now = start
    for _ in range(frames):
        app.update(now)
        now += app.frame_ms()
    return now


def test_starts_in_the_menu_and_draws_it():
    app = App()
    assert app.state == browser.MENU
    assert app.update(0) is True  # first frame drawn
    assert app.update(10) is False  # nothing changed, nothing redrawn


def test_menu_ignores_other_keys():
    app = App()
    for key in (pygame.K_SPACE, pygame.K_r, pygame.K_p, pygame.K_4, pygame.K_UP):
        press(app, key)
    assert app.state == browser.MENU
    assert app.agent_name is None


@pytest.mark.parametrize(
    "key,name,agent_class,fps",
    [
        (pygame.K_1, "human", None, 10),
        (pygame.K_2, "astar", AStar, 30),
        (pygame.K_3, "gbfs", GBFS, 30),
    ],
)
def test_number_keys_choose_who_plays(key, name, agent_class, fps):
    app = App()
    press(app, key)
    assert app.state == browser.PLAYING
    assert app.agent_name == name
    assert app.fps == fps
    if agent_class is None:
        assert app.agent is None
    else:
        assert type(app.agent) is agent_class
    assert app.game.hud["agent"] == browser.AGENT_NAMES[name]


def test_plays_the_same_game_as_the_desktop():
    """Frame by frame, the browser loop plays the golden A* game of seed 1."""
    expected = read_golden("astar_seed1.txt")
    app = App()
    random.seed(1)
    app.choose("astar", 0)
    now = 0
    for frame, line in enumerate(expected):
        app.update(now)
        now += app.frame_ms()
        game = app.game
        head = game.snake.body[0]
        actual = (
            f"{game.score} {len(game.snake.body)} "
            f"{int(head.x)},{int(head.y)} {int(game.food.pos.x)},{int(game.food.pos.y)}"
        )
        assert actual == line, f"first difference at frame {frame}"


def count_frames(app):
    """Make `app.game` count its frames; return the list the count goes in."""
    calls = []
    advance = app.game.advance

    def counting_advance(agent=None):
        calls.append(agent)
        return advance(agent)

    app.game.advance = counting_advance
    return calls


def test_frames_follow_the_speed_and_catch_up_a_little_at_most():
    app = started("astar")
    frames = count_frames(app)
    app.update(0)
    assert len(frames) == 1
    app.update(20)  # the next frame is due at 33 ms
    assert len(frames) == 1
    app.update(34)
    assert len(frames) == 2
    # After a long stall (e.g. a slow search) it plays a few frames, then goes on from now
    app.update(5000)
    assert len(frames) == 2 + browser.MAX_FRAMES_PER_UPDATE
    assert app.next_frame_ms == 5000


def test_space_pauses_and_resumes_without_moving_the_snake():
    app = started("astar")
    now = play_frames(app, 3)
    press(app, pygame.K_SPACE, now)
    assert app.state == browser.PAUSED
    body = list(app.game.snake.body)
    app.update(now + 10_000)
    assert app.game.snake.body == body
    assert app.overlay() == browser.controls.PAUSED
    press(app, pygame.K_SPACE, now + 10_000)
    assert app.state == browser.PLAYING
    app.update(now + 10_000)
    assert app.game.snake.body != body


def test_p_toggles_the_path_for_search_agents_only():
    app = started("astar")
    press(app, pygame.K_p)
    assert app.show_path and app.game.show_path
    app.new_game(0)  # it stays on for the next games
    assert app.game.show_path
    press(app, pygame.K_p)
    assert not app.game.show_path

    human = started("human")
    press(human, pygame.K_p)
    assert not human.show_path


def test_plus_and_minus_change_the_speed_within_limits():
    app = started("astar")
    press(app, pygame.K_PLUS)
    assert app.fps == 45
    press(app, pygame.K_MINUS)
    press(app, pygame.K_MINUS)
    assert app.fps == 20
    for _ in range(20):
        press(app, pygame.K_KP_MINUS)
    assert app.fps == browser.SPEEDS[0]
    for _ in range(20):
        press(app, pygame.K_EQUALS)
    assert app.fps == browser.SPEEDS[-1]


def test_arrow_keys_steer_the_human_snake():
    app = started("human")
    assert app.game.snake.direction == "UP"
    press(app, pygame.K_LEFT)
    assert app.game.snake.direction == "LEFT"
    press(app, pygame.K_RIGHT)  # cannot turn back on itself
    assert app.game.snake.direction == "LEFT"


def test_arrow_keys_do_not_steer_the_agents():
    app = started("astar")
    direction = app.game.snake.direction
    press(app, pygame.K_LEFT if direction != "LEFT" else pygame.K_DOWN)
    assert app.game.snake.direction == direction


def test_human_game_over_waits_for_enter_and_keeps_the_statistics():
    app = started("human")
    now = play_frames(app, 20)  # nobody steers: the snake hits the top wall
    assert app.state == browser.GAME_OVER
    assert app.game.end_reason == "collision"
    assert app.scores == [0]
    assert app.overlay() == ("Game over", "The snake crashed")
    assert app.hints() == browser.GAME_OVER_HINTS
    app.update(now + 60_000)
    assert app.state == browser.GAME_OVER  # humans are not hurried
    press(app, pygame.K_RETURN, now)
    assert app.state == browser.PLAYING
    assert app.game.hud["game"] == 2
    assert app.game.hud["best"] == 0 and app.game.hud["mean"] == 0


def test_agents_start_the_next_game_on_their_own():
    app = started("astar")
    play_frames(app, 2)
    app.finish_game(1000)
    assert app.state == browser.GAME_OVER
    app.update(1000 + browser.GAME_OVER_MS - 1)
    assert app.state == browser.GAME_OVER
    app.update(1000 + browser.GAME_OVER_MS)
    assert app.state == browser.PLAYING
    assert app.game.hud["game"] == 2


def test_r_restarts_without_counting_the_unfinished_game():
    app = started("gbfs")
    play_frames(app, 3)
    press(app, pygame.K_r)
    assert app.state == browser.PLAYING
    assert app.scores == []
    assert app.game.score == 0 and app.game.hud["game"] == 1


@pytest.mark.parametrize("key", [pygame.K_m, pygame.K_ESCAPE])
def test_m_or_escape_go_back_to_the_menu_and_reset_the_statistics(key):
    app = started("astar")
    app.finish_game(0)
    press(app, key)
    assert app.state == browser.MENU
    assert app.agent is None
    assert app.update(0) is True
    press(app, pygame.K_2)
    assert app.scores == []


def test_every_state_can_be_drawn():
    app = App()
    app.update(0)
    for name in ("human", "astar"):
        app.choose(name, 0)
        press(app, pygame.K_p)
        assert app.update(0)
        press(app, pygame.K_SPACE)
        assert app.update(0)
        app.finish_game(0)
        assert app.update(0)


def test_the_web_build_ships_the_game_without_the_rl_code(tmp_path, monkeypatch):
    from web import build

    monkeypatch.setattr(build, "APP_DIR", tmp_path / "app")
    build.assemble()
    files = {
        path.relative_to(tmp_path / "app").as_posix() for path in (tmp_path / "app").rglob("*")
    }
    assert {"main.py", "snake_ai/browser.py", "snake_ai/game/game.py", "snake_ai/search"} <= files
    assert not any(name.startswith("snake_ai/rl") or "__pycache__" in name for name in files)
