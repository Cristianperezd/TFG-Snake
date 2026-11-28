"""Tests for the drawing code: frames have the expected look and size, and
drawing never changes the games."""

import random

import pygame
from pygame.math import Vector2

from snake_ai.game import colors, constants
from snake_ai.game.food import Food
from snake_ai.game.game import Game
from snake_ai.game.render import WINDOW_SIZE, Renderer, heading, stat_rows
from snake_ai.game.snake import Snake
from snake_ai.search.astar import AStar, AStarNode

B = constants.BLOCK


def play_trace(seed, frames, render):
    random.seed(seed)
    game = Game(fps=0, render=render)
    agent = AStar(AStarNode(game.board, game.snake, game.food))
    trace = []
    for _ in range(frames):
        over = game.step(agent)
        trace.append((game.score, tuple(game.snake.body[0]), tuple(game.food.pos)))
        if over:
            break
    return trace, random.getstate()


def test_window_is_the_board_plus_the_side_panel():
    game = Game(fps=0)
    assert game.display.get_size() == WINDOW_SIZE == (700, 500)
    assert constants.GRID_COLS == constants.GRID_ROWS == 25


def test_drawing_does_not_change_the_game():
    # Same frames and same random state with and without drawing
    assert play_trace(3, 300, render=True) == play_trace(3, 300, render=False)


def test_drawing_does_not_draw_random_numbers():
    surface = pygame.Surface(WINDOW_SIZE)
    random.seed(0)
    snake, food = Snake(), Food()
    state = random.getstate()
    Renderer().draw_frame(surface, snake, food, "A*", stat_rows(0, 3))
    assert random.getstate() == state


def test_frame_shows_the_snake_the_apple_and_the_panel():
    surface = pygame.Surface(WINDOW_SIZE)
    random.seed(0)
    snake, food = Snake(), Food()
    Renderer().draw_frame(surface, snake, food, "A*", stat_rows(0, 3))
    head, tail = snake.body[0], snake.body[-1]
    assert surface.get_at((int(head.x) + B // 2, int(head.y) + B // 2))[:3] == colors.SNAKE_HEAD
    assert surface.get_at((int(tail.x) + B // 2, int(tail.y) + B // 2))[:3] == colors.SNAKE_TAIL
    assert surface.get_at((int(food.pos.x) + B // 2, int(food.pos.y) + B // 2))[:3] == colors.FOOD
    assert surface.get_at((constants.WIDTH + 100, constants.HEIGHT - 5))[:3] == colors.PANEL


def test_heading_follows_the_last_move():
    snake = Snake()
    assert heading(snake) == (0, -1)
    snake.direction = "LEFT"
    snake.move()
    assert heading(snake) == (-1, 0)
    snake.body = [Vector2(0, 0)]
    snake.direction = "DOWN"
    assert heading(snake) == (0, 1)


def test_stat_rows():
    assert stat_rows(4, 7) == [("Score", "4"), ("Length", "7")]
    rows = dict(stat_rows(4, 7, number=2, total=5, best=10, mean=6.25, fps=29.6))
    assert rows == {
        "Score": "4",
        "Length": "7",
        "Game": "2 / 5",
        "Best": "10",
        "Average": "6.2",
        "FPS": "30",
    }
    # Before the first game ends: the best is the current score, no average yet
    rows = dict(stat_rows(4, 7, number=1, total=5, label="Episode"))
    assert rows["Episode"] == "1 / 5" and rows["Best"] == "4" and rows["Average"] == "-"


# --show-path


def test_search_agents_expose_their_path_and_explored_cells():
    random.seed(2)
    game = Game(fps=0, show_path=True)
    agent = AStar(AStarNode(game.board, game.snake, game.food))
    assert game.search_overlay() is None  # before the first step
    game.step(agent)
    path, explored = game.search_overlay()
    head = game.snake.get_head()
    assert path[-1] == game.food.pos  # the path ends on the apple
    assert abs(path[0].x - head.x) + abs(path[0].y - head.y) == B
    assert len(explored) >= len(path)
    assert all(
        0 <= cell.x < constants.WIDTH and 0 <= cell.y < constants.HEIGHT for cell in explored
    )


def test_show_path_does_not_change_the_game():
    def trace(**options):
        random.seed(6)
        game = Game(fps=0, **options)
        agent = AStar(AStarNode(game.board, game.snake, game.food))
        frames = []
        for _ in range(200):
            over = game.step(agent)
            frames.append((over, [tuple(b) for b in game.snake.body], tuple(game.food.pos)))
        return frames, random.getstate()

    assert trace(show_path=True) == trace(render=False)


def test_path_is_drawn_on_the_board():
    random.seed(2)
    game = Game(fps=0, show_path=True)
    agent = AStar(AStarNode(game.board, game.snake, game.food))
    game.step(agent)
    path, _ = game.search_overlay()
    cell = path[len(path) // 2]
    point = (int(cell.x) + B // 2, int(cell.y) + B // 2)
    with_path = game.display.get_at(point)[:3]
    game.show_path = False
    game.draw()
    assert game.display.get_at(point)[:3] != with_path


def test_hud_can_hide_the_frame_rate():
    shown = dict(Game(fps=0, hud={"agent": "A*", "game": 1, "games": 1}).hud_rows())
    hidden = dict(Game(fps=0, hud={"agent": "A*", "game": 1, "games": 1, "fps": False}).hud_rows())
    assert "FPS" in shown and "FPS" not in hidden
