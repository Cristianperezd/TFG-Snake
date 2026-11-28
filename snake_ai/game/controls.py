"""Keyboard and window events shared by the game window and the RL environment.

Space pauses and resumes, Esc or closing the window quits. Only used when
the game is drawn in a window: headless runs never read these events.
"""

import pygame

# Short help shown at the bottom of the side panel
HINTS = ("Space  pause / resume", "Esc  quit")

PAUSED = ("Paused", "Press Space to resume")

# Why a game ended -> text of the game-over overlay
END_REASONS = {
    "collision": "The snake crashed",
    "no path": "No path to the food",
    "step limit": "Step limit reached",
}


def is_quit(event):
    return event.type == pygame.QUIT or (
        event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
    )


def is_pause(event):
    return event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE


def wait(clock, seconds=None, skip_keys=(pygame.K_SPACE, pygame.K_RETURN)):
    """Keep the window responsive for `seconds` (None = until a key in
    `skip_keys` is pressed). Return False if the user quits, True otherwise."""
    elapsed_ms = 0
    while seconds is None or elapsed_ms < seconds * 1000:
        for event in pygame.event.get():
            if is_quit(event):
                return False
            if event.type == pygame.KEYDOWN and event.key in skip_keys:
                return True
        elapsed_ms += clock.tick(30)
    return True


def game_over_text(reason):
    return ("Game over", END_REASONS.get(reason, reason))
