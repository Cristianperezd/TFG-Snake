from pygame.math import Vector2

from snake_ai.game import constants
from snake_ai.game.food import Food
from snake_ai.game.snake import Snake, is_out_of_bounds, next_position

B = constants.BLOCK


def test_next_position_moves_one_block():
    p = Vector2(100, 100)
    assert next_position(p, 'UP') == Vector2(100, 100 - B)
    assert next_position(p, 'DOWN') == Vector2(100, 100 + B)
    assert next_position(p, 'LEFT') == Vector2(100 - B, 100)
    assert next_position(p, 'RIGHT') == Vector2(100 + B, 100)


def test_bounds():
    assert not is_out_of_bounds(Vector2(0, 0))
    assert not is_out_of_bounds(Vector2(constants.WIDTH - B, constants.HEIGHT - B))
    assert is_out_of_bounds(Vector2(-B, 0))
    assert is_out_of_bounds(Vector2(constants.WIDTH, 0))
    assert is_out_of_bounds(Vector2(0, constants.HEIGHT))


def test_snake_starts_in_the_middle_facing_up():
    snake = Snake()
    assert len(snake.body) == 3
    assert snake.direction == 'UP'
    assert snake.get_head() == Vector2((constants.GRID_COLS // 2) * B, (constants.GRID_ROWS // 2) * B)


def test_snake_move_adds_new_head():
    snake = Snake()
    head = Vector2(snake.head)
    snake.move()
    assert snake.get_head() == next_position(head, 'UP')
    assert len(snake.body) == 4  # the game removes the tail when no food is eaten


def test_collision_with_wall():
    snake = Snake()
    for _ in range(constants.GRID_ROWS // 2):
        snake.move()
        snake.body.pop()
        assert not snake.check_collision()
    snake.move()
    assert snake.check_collision()


def test_collision_with_own_body():
    snake = Snake()
    snake.body = [Vector2(100, 100), Vector2(100, 120), Vector2(120, 120), Vector2(120, 100), Vector2(100, 100)]
    snake.head = snake.body[0]
    assert snake.check_collision()


def test_food_respawns_outside_the_snake():
    for seed in range(50):
        import random
        random.seed(seed)
        snake = Snake()
        food = Food()
        food.pos = Vector2(snake.head)
        assert food.detect_collision(snake)
        assert food.pos not in snake.body
        assert 0 <= food.pos.x < constants.WIDTH and 0 <= food.pos.y < constants.HEIGHT


def test_no_collision_when_food_elsewhere():
    snake = Snake()
    food = Food()
    food.pos = Vector2(0, 0)
    assert not food.detect_collision(snake)
