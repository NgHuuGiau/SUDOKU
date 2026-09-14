"""Headless smoke test for the Pygame rendering pipeline."""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from game import GameState
from ui import create_game_screen, draw_game_view, load_fonts
from ui.geometry import SCREEN_HEIGHT, SCREEN_WIDTH, get_sidebar_layout


def test_game_view_renders_headless():
    screen = create_game_screen()
    state = GameState("easy")
    draw_game_view(screen, load_fonts(), state, (0, 0))
    pygame.quit()


def test_sidebar_layout_has_no_overlapping_controls():
    layout = get_sidebar_layout()
    aliases = {"undo", "redo"}
    controls = [
        value for key, value in layout.items() if key not in {"numbers", *aliases} and value is not None
    ]
    controls.extend(layout["numbers"])

    assert all(0 <= rect.left and rect.right <= SCREEN_WIDTH for rect in controls)
    assert all(0 <= rect.top and rect.bottom <= SCREEN_HEIGHT for rect in controls)
    for index, rect in enumerate(controls):
        assert not any(rect.colliderect(other) for other in controls[index + 1 :])
