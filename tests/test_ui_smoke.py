"""Headless smoke test for the Pygame rendering pipeline."""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from game import AppController, GameState
from ui import create_game_screen, draw_game_view, load_fonts
from ui.geometry import SCREEN_HEIGHT, SCREEN_WIDTH, get_sidebar_layout
from ui.icons import SmoothIcons


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


def test_menu_help_opens_help_overlay_and_escape_returns_to_menu(monkeypatch):
    controller = AppController.__new__(AppController)
    controller.state = AppController.STATE_MENU
    controller.running = True
    help_rect = pygame.Rect(10, 10, 30, 30)
    monkeypatch.setattr(
        pygame.event,
        "get",
        lambda: [pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=help_rect.center)],
    )

    controller._handle_menu_events({"help": help_rect})
    assert controller.state == AppController.STATE_HELP

    monkeypatch.setattr(
        pygame.event,
        "get",
        lambda: [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)],
    )
    controller._handle_help_events({"help_close": pygame.Rect(0, 0, 1, 1)})
    assert controller.state == AppController.STATE_MENU


def test_help_modal_close_button_stays_on_screen():
    from config import game_text
    from ui.modals import draw_help_modal

    pygame.init()
    screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    rects = draw_help_modal(screen, load_fonts(), (0, 0), game_text)
    close_rect = rects["help_close"]
    assert close_rect is not None
    assert screen.get_rect().contains(close_rect)


def test_modern_icon_renderer_returns_visible_icon_at_requested_size():
    icon = SmoothIcons.get("grid_logo", 32, (30, 100, 180))

    assert icon.get_size() == (32, 32)
    assert icon.get_bounding_rect() != pygame.Rect(0, 0, 0, 0)
