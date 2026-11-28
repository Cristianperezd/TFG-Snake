"""The browser version: a menu to choose who plays, then games that follow each other.

The page runs Python compiled to WebAssembly (pygbag), where the program must
give control back to the browser every frame: nothing here may block, so the
desktop's waiting loops (pause, game-over message, `clock.tick`) are replaced
by states. `App` is that state machine. The page loop (`web/main.py`) passes
it every pygame event (`handle_event`) and calls `update` once per browser
frame; `update` moves the game on when the next game frame is due and redraws.

The games themselves are the desktop ones: `Game.advance` and `Game.steer`
are the parts of `Game.step` that neither read events nor wait. There is no
PPO agent: it needs PyTorch, which does not run in the browser.

Keys: 1 / 2 / 3 choose Human, A* or GBFS in the menu. While playing, the
arrow keys steer (Human), P shows the search agent's path, + / - change the
speed, Space pauses, R starts a new game and M or Esc goes back to the menu.
After a game over, Enter or Space starts the next one; the agents start it
on their own after a moment.
"""

# No `statistics` here: pygbag would take it for a package to download from PyPI
import pygame

from snake_ai.agents import AGENT_NAMES, make_agent
from snake_ai.game import colors, controls
from snake_ai.game.game import Game
from snake_ai.game.render import BOARD_RECT

MENU = "menu"
PLAYING = "playing"
PAUSED = "paused"
GAME_OVER = "game over"

MENU_KEYS = {pygame.K_1: "human", pygame.K_2: "astar", pygame.K_3: "gbfs"}
MENU_CHOICES = (("1", "Human (arrow keys)"), ("2", "A* search"), ("3", "GBFS search"))
MENU_NOTE = "PPO needs PyTorch: desktop only"
MENU_CARD_RECT = pygame.Rect(0, 0, 340, 290)
MENU_CARD_RECT.center = BOARD_RECT.center

# Game frames per second that + / - choose from. Humans start slower than the
# desktop default (30) so the game is playable; the agents start at 30.
SPEEDS = (5, 10, 15, 20, 30, 45, 60, 90, 120)
START_SPEED = {"human": 10, "astar": 30, "gbfs": 30}

# How long the game-over message stays before an agent starts the next game
GAME_OVER_MS = 1500

# Most game frames played in one browser frame, to catch up after a slow one
MAX_FRAMES_PER_UPDATE = 4

FASTER_KEYS = (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS)
SLOWER_KEYS = (pygame.K_MINUS, pygame.K_KP_MINUS)
MENU_BACK_KEYS = (pygame.K_m, pygame.K_ESCAPE)

MENU_HINTS = ("1 / 2 / 3  choose",)
HUMAN_HINTS = ("Arrows  steer", "+ / -  speed", "Space  pause", "R  restart   M  menu")
AGENT_HINTS = ("P  show path", "+ / -  speed", "Space  pause", "R  restart   M  menu")
GAME_OVER_HINTS = ("Enter  next game", "M  menu")


class App:
    """Menu, games and their statistics, driven by `handle_event` and `update`.

    Times (`now`) are in milliseconds, e.g. `pygame.time.get_ticks()`.
    """

    def __init__(self):
        self.state = MENU
        self.agent_name = None
        self.agent = None
        self.show_path = False
        self.fps = 30
        self.scores = []
        self.next_frame_ms = 0
        self.game_over_ms = 0
        self.dirty = True  # Something changed since the last frame was drawn
        self.game = Game(render=False)  # The menu shows the board of a new game

    @property
    def is_search_agent(self):
        return self.agent_name not in (None, "human")

    # Events

    def handle_event(self, event, now):
        if event.type != pygame.KEYDOWN:
            return
        key = event.key
        if self.state == MENU:
            if key in MENU_KEYS:
                self.choose(MENU_KEYS[key], now)
            return

        self.dirty = True
        if key in MENU_BACK_KEYS:
            self.to_menu()
        elif key == pygame.K_r:
            self.new_game(now)
        elif key == pygame.K_p and self.is_search_agent:
            self.show_path = not self.show_path
            self.game.show_path = self.show_path
        elif key in FASTER_KEYS or key in SLOWER_KEYS:
            self.change_speed(1 if key in FASTER_KEYS else -1)
        elif self.state == GAME_OVER:
            if key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self.new_game(now)
        elif key == pygame.K_SPACE:
            self.toggle_pause(now)
        elif self.state == PLAYING and self.agent is None:
            self.game.steer(event)

    def choose(self, agent_name, now):
        """Start playing with `agent_name` ('human', 'astar' or 'gbfs'), with new statistics."""
        self.agent_name = agent_name
        self.fps = START_SPEED[agent_name]
        self.show_path = False
        self.scores = []
        self.new_game(now)

    def to_menu(self):
        self.state = MENU
        self.agent_name = None
        self.agent = None
        self.game = Game(render=False)
        self.dirty = True

    def change_speed(self, direction):
        index = min(range(len(SPEEDS)), key=lambda i: abs(SPEEDS[i] - self.fps))
        self.fps = SPEEDS[max(0, min(len(SPEEDS) - 1, index + direction))]

    def toggle_pause(self, now):
        if self.state == PLAYING:
            self.state = PAUSED
        elif self.state == PAUSED:
            self.state = PLAYING
            self.next_frame_ms = now

    # Games

    def new_game(self, now):
        """Start a new game with the chosen player (an unfinished one is not counted)."""
        hud = {
            "agent": AGENT_NAMES[self.agent_name],
            "game": len(self.scores) + 1,
            "best": max(self.scores) if self.scores else None,
            "mean": sum(self.scores) / len(self.scores) if self.scores else None,
        }
        self.game = Game(fps=0, render=False, hud=hud, show_path=self.show_path)
        self.agent = make_agent(self.agent_name, self.game)
        self.state = PLAYING
        self.next_frame_ms = now
        self.dirty = True

    def frame_ms(self):
        return 1000 / self.fps

    def update(self, now):
        """Play the game frames that are due by `now` and redraw if anything changed.
        Return True if a frame was drawn."""
        if self.state == PLAYING:
            frames = 0
            while now >= self.next_frame_ms and frames < MAX_FRAMES_PER_UPDATE:
                frames += 1
                self.next_frame_ms += self.frame_ms()
                if self.game.advance(self.agent):
                    self.finish_game(now)
                    break
            if frames:
                self.game.clock.tick()  # Only measures the frame rate shown in the panel
                self.dirty = True
            if self.state == PLAYING and now - self.next_frame_ms > self.frame_ms():
                self.next_frame_ms = now  # Too far behind (e.g. a slow search): do not rush
        elif self.state == GAME_OVER and self.agent is not None:
            if now - self.game_over_ms >= GAME_OVER_MS:
                self.new_game(now)

        if not self.dirty:
            return False
        self.draw()
        self.dirty = False
        return True

    def finish_game(self, now):
        self.scores.append(self.game.score)
        self.state = GAME_OVER
        self.game_over_ms = now
        self.dirty = True

    # Drawing

    def hints(self):
        if self.state == MENU:
            return MENU_HINTS
        if self.state == GAME_OVER and self.agent is None:
            return GAME_OVER_HINTS
        return AGENT_HINTS if self.is_search_agent else HUMAN_HINTS

    def overlay(self):
        if self.state == PAUSED:
            return controls.PAUSED
        if self.state == GAME_OVER:
            return controls.game_over_text(self.game.end_reason)
        return None

    def draw(self):
        if self.state == MENU:
            self.draw_menu()
            return
        self.game.hints = self.hints()
        self.game.draw(overlay=self.overlay())

    def draw_menu(self):
        game = self.game
        surface = game.display
        renderer = game.renderer
        renderer.draw_frame(surface, game.snake, game.food, "Menu", [], hints=self.hints())
        card = MENU_CARD_RECT
        pygame.draw.rect(surface, colors.PANEL, card, border_radius=12)
        pygame.draw.rect(surface, colors.PANEL_BORDER, card, width=2, border_radius=12)
        title = renderer.title_font.render("Who plays?", True, colors.TEXT)
        surface.blit(title, (card.centerx - title.get_width() // 2, card.top + 26))
        y = card.top + 90
        for key, name in MENU_CHOICES:
            key_text = renderer.value_font.render(key, True, colors.ACCENT)
            name_text = renderer.value_font.render(name, True, colors.TEXT)
            surface.blit(key_text, (card.left + 40, y))
            surface.blit(name_text, (card.left + 70, y))
            y += 38
        note = renderer.small_font.render(MENU_NOTE, True, colors.TEXT_MUTED)
        surface.blit(note, (card.centerx - note.get_width() // 2, card.bottom - 34))
        pygame.display.flip()
