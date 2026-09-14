"""Headless smoke test for the Pygame rendering pipeline."""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from game import GameState
from ui import create_game_screen, draw_game_view, load_fonts


def test_game_view_renders_headless():
    screen = create_game_screen()
    state = GameState("easy")
    draw_game_view(screen, load_fonts(), state, (0, 0))
    pygame.quit()
