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
