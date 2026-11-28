"""Drawing code shared by the game window, the RL environment and GIF recording.

It only reads the game state: it never changes it and never draws random
numbers, so rendering cannot change the games or the agents' decisions.

A frame is the board (the 25 x 25 playfield, at the top left, in the same
pixel coordinates as the game) plus a side panel to its right with the agent's
name and some statistics.
"""

import pygame

from snake_ai.game import colors, constants

BOARD_RECT = pygame.Rect(0, 0, constants.WIDTH, constants.HEIGHT)
PANEL_RECT = pygame.Rect(constants.WIDTH, 0, constants.PANEL_WIDTH, constants.HEIGHT)
WINDOW_SIZE = (constants.WINDOW_WIDTH, constants.WINDOW_HEIGHT)

B = constants.BLOCK
UNIT_VECTORS = {"UP": (0, -1), "DOWN": (0, 1), "LEFT": (-1, 0), "RIGHT": (1, 0)}


def blend(start, end, t):
    """Colour between `start` (t = 0) and `end` (t = 1)."""
    return tuple(round(a + (b - a) * t) for a, b in zip(start, end))


def heading(snake):
    """Unit vector (dx, dy) of the direction the head last moved in."""
    if len(snake.body) > 1:
        dx = snake.body[0].x - snake.body[1].x
        dy = snake.body[0].y - snake.body[1].y
        if abs(dx) + abs(dy) == B:
            return int(dx // B), int(dy // B)
    return UNIT_VECTORS[snake.direction]


def format_mean(mean):
    return "-" if mean is None else f"{mean:.1f}"


def stat_rows(score, length, number=None, total=None, best=None, mean=None, fps=None, label="Game"):
    """Rows (label, value) for the side panel.

    `number` / `total` is the current game (or episode), `best` and `mean` are
    over the finished ones (None before the first one ends) and `fps` is the
    measured frame rate, if known.
    """
    rows = [("Score", str(score)), ("Length", str(length))]
    if number is not None:
        rows.append((label, f"{number} / {total}" if total else str(number)))
        rows.append(("Best", str(max(score, best or 0))))
        rows.append(("Average", format_mean(mean)))
    if fps is not None:
        rows.append(("FPS", f"{fps:.0f}"))
    return rows


class Renderer:
    """Draws frames on a pygame surface of at least WINDOW_SIZE pixels.

    Each game (or environment) owns one: fonts are tied to pygame's font
    module and cannot be reused after `pygame.quit()`.
    """

    def __init__(self):
        if not pygame.font.get_init():
            pygame.font.init()
        self.title_font = pygame.font.Font(None, 46)
        self.label_font = pygame.font.Font(None, 22)
        self.value_font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 19)
        self.board_background = self._make_board_background()

    @staticmethod
    def _make_board_background():
        surface = pygame.Surface(BOARD_RECT.size)
        surface.fill(colors.BOARD_DARK)
        for row in range(constants.GRID_ROWS):
            for col in range(row % 2, constants.GRID_COLS, 2):
                surface.fill(colors.BOARD_LIGHT, (col * B, row * B, B, B))
        return surface

    # Board

    def draw_board(self, surface, snake, food):
        """Draw the board on `surface`, a surface with the board's coordinates."""
        surface.blit(self.board_background, (0, 0))
        self.draw_food(surface, food)
        self.draw_snake(surface, snake)

    def draw_food(self, surface, food):
        cx, cy = int(food.pos.x) + B // 2, int(food.pos.y) + B // 2 + 1
        radius = B // 2 - 2
        pygame.draw.line(surface, colors.FOOD_STEM, (cx, cy - radius), (cx + 1, cy - radius - 3), 2)
        pygame.draw.ellipse(surface, colors.FOOD_LEAF, (cx + 1, cy - radius - 5, 7, 4))
        pygame.draw.circle(surface, colors.FOOD, (cx, cy), radius)
        pygame.draw.circle(surface, colors.FOOD_HIGHLIGHT, (cx - 3, cy - 3), 2)

    def draw_snake(self, surface, snake):
        body = snake.body
        inset = 2
        size = B - 2 * inset
        last = max(len(body) - 1, 1)
        # Tail first, so the head is drawn on top
        for index in range(len(body) - 1, -1, -1):
            block = body[index]
            color = blend(colors.SNAKE_HEAD, colors.SNAKE_TAIL, index / last)
            x, y = int(block.x), int(block.y)
            if index == 0:
                pygame.draw.rect(surface, color, (x + 1, y + 1, B - 2, B - 2), border_radius=7)
            else:
                rect = (x + inset, y + inset, size, size)
                pygame.draw.rect(surface, color, rect, border_radius=6)
                # Join the segment to the next one towards the head
                towards = body[index - 1]
                dx, dy = int(towards.x) - x, int(towards.y) - y
                if abs(dx) + abs(dy) == B:
                    left, top = min(x, x + dx) + B // 2, min(y, y + dy) + B // 2
                    if dx:
                        pygame.draw.rect(surface, color, (left, y + inset, B, size))
                    else:
                        pygame.draw.rect(surface, color, (x + inset, top, size, B))
        self._draw_eyes(surface, snake)

    @staticmethod
    def _draw_eyes(surface, snake):
        head = snake.body[0]
        dx, dy = heading(snake)
        cx, cy = head.x + B / 2, head.y + B / 2
        side_x, side_y = -dy, dx  # perpendicular to the heading
        for sign in (-1, 1):
            ex = cx + dx * 3 + side_x * 4.5 * sign
            ey = cy + dy * 3 + side_y * 4.5 * sign
            pygame.draw.circle(surface, colors.EYE, (round(ex), round(ey)), 3)
            pygame.draw.circle(surface, colors.PUPIL, (round(ex + dx), round(ey + dy)), 1)

    # Side panel

    def draw_panel(self, surface, title, rows, hints=()):
        """Draw the side panel: `title` (the agent), `rows` of (label, value)
        and a few `hints` (short lines of help) at the bottom."""
        panel = surface.subsurface(PANEL_RECT)
        panel.fill(colors.PANEL)
        pygame.draw.line(panel, colors.PANEL_BORDER, (0, 0), (0, PANEL_RECT.height), 2)
        margin = 18
        width = PANEL_RECT.width - 2 * margin

        label = self.label_font.render("SNAKE AI", True, colors.TEXT_MUTED)
        panel.blit(label, (margin, 20))
        panel.blit(self.title_font.render(title, True, colors.ACCENT), (margin, 40))
        y = 92
        pygame.draw.line(panel, colors.PANEL_BORDER, (margin, y), (margin + width, y))

        y += 16
        for name, value in rows:
            text = self.label_font.render(name, True, colors.TEXT_MUTED)
            panel.blit(text, (margin, y + 6))
            text = self.value_font.render(value, True, colors.TEXT)
            panel.blit(text, (margin + width - text.get_width(), y))
            y += 38

        y = PANEL_RECT.height - 14 - len(hints) * 18
        for hint in hints:
            panel.blit(self.small_font.render(hint, True, colors.TEXT_MUTED), (margin, y))
            y += 18

    # Pause and game-over messages

    def draw_overlay(self, surface, title, subtitle=None):
        """Darken the board and write `title` (and `subtitle`) in its middle."""
        shade = pygame.Surface(BOARD_RECT.size, pygame.SRCALPHA)
        shade.fill(colors.OVERLAY)
        surface.blit(shade, BOARD_RECT.topleft)
        texts = [self.title_font.render(title, True, colors.TEXT)]
        if subtitle:
            texts.append(self.value_font.render(subtitle, True, colors.ACCENT))
        y = BOARD_RECT.centery - sum(text.get_height() + 8 for text in texts) // 2
        for text in texts:
            surface.blit(text, (BOARD_RECT.centerx - text.get_width() // 2, y))
            y += text.get_height() + 8

    # Whole frame

    def draw_frame(self, surface, snake, food, title, rows, hints=(), overlay=None):
        """Draw the board and the panel. `overlay` is an optional (title,
        subtitle) message drawn over the board, e.g. when paused."""
        surface.fill(colors.BACKGROUND)
        self.draw_board(surface.subsurface(BOARD_RECT), snake, food)
        self.draw_panel(surface, title, rows, hints)
        if overlay is not None:
            self.draw_overlay(surface, *overlay)
