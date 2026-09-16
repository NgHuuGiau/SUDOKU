"""Headless smoke test for the Pygame rendering pipeline."""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

import game
from game import AppController, Game, GameState
from persistence import get_stats, load_daily_stats, load_game_state, record_game_start
from ui import create_game_screen, draw_game_view, load_fonts
from ui.geometry import SCREEN_HEIGHT, SCREEN_WIDTH, get_sidebar_layout
from ui.icons import SmoothIcons
from ui.menu import draw_menu_view


def test_game_view_renders_headless():
    screen = create_game_screen()
    state = GameState("easy")
    draw_game_view(screen, load_fonts(), state, (0, 0))
    pygame.quit()


def test_menu_renders_headless():
    screen = create_game_screen()
    draw_menu_view(screen, load_fonts(), (0, 0))
    pygame.quit()


def test_sidebar_layout_has_no_overlapping_controls():
    layout = get_sidebar_layout()
    aliases = {"undo", "redo"}
    controls = [
        value
        for key, value in layout.items()
        if key not in {"numbers", *aliases} and value is not None
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


def test_pause_modal_buttons_are_visible_and_do_not_overlap():
    from ui.modals import draw_pause_modal

    pygame.init()
    screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    rects = draw_pause_modal(screen, load_fonts(), (0, 0), lambda key: key)
    buttons = [rects[key] for key in ("pause_resume", "pause_restart", "pause_save_quit")]
    visible_buttons = [rect for rect in buttons if rect is not None]

    assert len(visible_buttons) == len(buttons)
    assert all(screen.get_rect().contains(rect) for rect in visible_buttons)
    assert all(
        not first.colliderect(second)
        for i, first in enumerate(visible_buttons)
        for second in visible_buttons[i + 1 :]
    )
    assert rects["pause_quit"] == rects["pause_save_quit"]


def test_win_modal_buttons_are_visible_and_do_not_overlap():
    from ui.modals import draw_win_modal

    pygame.init()
    screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    state = GameState("easy")
    state.final_time = 125
    rects = draw_win_modal(screen, load_fonts(), (0, 0), lambda key: key, state, [])
    buttons = [rects["win_restart"], rects["win_quit"]]
    visible_buttons = [rect for rect in buttons if rect is not None]

    assert len(visible_buttons) == len(buttons)
    assert all(screen.get_rect().contains(rect) for rect in visible_buttons)
    assert not visible_buttons[0].colliderect(visible_buttons[1])


def test_leaderboard_custom_tab_is_visible_and_selectable(monkeypatch):
    controller = AppController.__new__(AppController)
    controller.running = True
    controller.state = AppController.STATE_LEADERBOARD
    controller.leaderboard_diff = "medium"
    custom_tab = pygame.Rect(20, 20, 40, 30)
    monkeypatch.setattr(
        pygame.event,
        "get",
        lambda: [pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=custom_tab.center)],
    )

    controller._handle_leaderboard_events({"tab_custom": custom_tab})

    assert controller.leaderboard_diff == "custom"


def test_pause_resume_button_unpauses_game(monkeypatch):
    state = GameState("easy")
    state.paused = True
    session = Game.__new__(Game)
    session.state = state
    resume_rect = pygame.Rect(10, 10, 40, 40)
    session.pause_resume_rect = resume_rect
    session.pause_restart_rect = None
    session.pause_save_quit_rect = None
    session.pause_quit_rect = None
    monkeypatch.setattr(game, "play_sound", lambda _sound: None)

    session._handle_pause_click(resume_rect.center)

    assert not state.paused


def test_modern_icon_renderer_returns_visible_icon_at_requested_size():
    icon = SmoothIcons.get("grid_logo", 32, (30, 100, 180))

    assert icon.get_size() == (32, 32)
    assert icon.get_bounding_rect() != pygame.Rect(0, 0, 0, 0)


def test_new_game_counts_once_and_resume_does_not_count_again(monkeypatch):
    class StubGame:
        def __init__(self, difficulty, loaded_state=None):
            self.loaded_state = loaded_state

        def _load_fonts(self):
            pass

    monkeypatch.setattr(game, "Game", StubGame)
    controller = AppController.__new__(AppController)
    controller.screen = pygame.Surface((1, 1))
    controller.state = AppController.STATE_MENU

    controller._start_game("easy")
    assert get_stats()["games_played"] == 1
    assert get_stats()["by_difficulty"]["easy"]["played"] == 1

    saved_state = GameState("easy")
    controller._start_game("easy", loaded_state=saved_state)
    assert get_stats()["games_played"] == 1


def test_restart_counts_a_new_game():
    session = Game.__new__(Game)
    session.particles = []
    session.state = GameState("easy")

    session._restart_game()

    assert get_stats()["games_played"] == 1
    assert get_stats()["by_difficulty"]["easy"]["played"] == 1


def test_winning_daily_game_updates_daily_and_game_stats(monkeypatch):
    class StubGame(Game):
        def _spawn_win_fireworks(self):
            pass

    state = GameState("daily")
    state.board = [row[:] for row in state.solution]
    record_game_start("daily")

    session = StubGame.__new__(StubGame)
    session.state = state
    session.particles = []
    monkeypatch.setattr(game, "play_sound", lambda _sound: None)
    monkeypatch.setattr("persistence.is_top_10_time", lambda _difficulty, _elapsed: False)

    session.update()

    assert state.game_over
    assert get_stats()["games_won"] == 1
    assert load_daily_stats()["total_completed"] == 1
    assert load_daily_stats()["streak"] == 1


def test_keyboard_places_solution_value_in_selected_empty_cell(monkeypatch):
    state = GameState("easy")
    session = Game.__new__(Game)
    session.state = state
    session.show_help = False
    row, column = next((r, c) for r in range(9) for c in range(9) if state.original[r][c] == 0)
    state.selected = [row, column]
    value = state.solution[row][column]
    event = pygame.event.Event(
        pygame.KEYDOWN, key=getattr(pygame, f"K_{value}"), unicode=str(value), mod=0
    )
    monkeypatch.setattr(pygame.event, "get", lambda: [event])

    assert session.handle_events()
    assert state.board[row][column] == value


def test_escape_pauses_and_resumes_game(monkeypatch):
    state = GameState("easy")
    session = Game.__new__(Game)
    session.state = state
    session.show_help = False
    escape = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
    events = [escape]
    monkeypatch.setattr(pygame.event, "get", lambda: events)

    assert session.handle_events()
    assert state.paused

    assert session.handle_events()
    assert not state.paused


def test_window_close_saves_latest_game_state(monkeypatch):
    state = GameState("easy")
    row, column = next((r, c) for r in range(9) for c in range(9) if state.original[r][c] == 0)
    state.board[row][column] = state.solution[row][column]
    session = Game.__new__(Game)
    session.state = state
    session.running = True
    monkeypatch.setattr(pygame.event, "get", lambda: [pygame.event.Event(pygame.QUIT)])

    assert not session.handle_events()
    restored = load_game_state()
    assert restored is not None
    assert restored.board[row][column] == state.solution[row][column]


def test_return_to_menu_saves_latest_game_state():
    state = GameState("easy")
    row, column = next((r, c) for r in range(9) for c in range(9) if state.original[r][c] == 0)
    state.board[row][column] = state.solution[row][column]
    session = Game.__new__(Game)
    session.state = state
    session.running = True
    session.go_to_menu = False
    session.header_pause_rect = None
    session.header_theme_rect = None
    session.header_sound_rect = None
    session.header_help_rect = None

    session._handle_mouse(get_sidebar_layout()["menu"].center)

    assert not session.running
    restored = load_game_state()
    assert restored is not None
    assert restored.board[row][column] == state.solution[row][column]


def test_import_puzzle_replaces_game_state_and_closes_dialog(monkeypatch):
    import tkinter
    from tkinter import messagebox, simpledialog

    from logic import export_puzzle

    class FakeRoot:
        destroyed = False

        def withdraw(self):
            pass

        def destroy(self):
            self.destroyed = True

    root = FakeRoot()
    monkeypatch.setattr(tkinter, "Tk", lambda: root)
    state = GameState("easy")
    board = [row[:] for row in state.solution]
    board[0][0] = 0
    puzzle_text = export_puzzle(board, state.solution)
    monkeypatch.setattr(simpledialog, "askstring", lambda *_args, **_kwargs: puzzle_text)
    monkeypatch.setattr(messagebox, "showinfo", lambda *_args, **_kwargs: None)
    session = Game.__new__(Game)
    session.state = state

    session._handle_import()

    assert state.board == board
    assert state.original == board
    assert state.selected == [0, 0]
    assert not state.paused
    assert root.destroyed


def test_invalid_puzzle_import_keeps_current_game_and_closes_dialog(monkeypatch):
    import tkinter
    from tkinter import messagebox, simpledialog

    class FakeRoot:
        destroyed = False

        def withdraw(self):
            pass

        def destroy(self):
            self.destroyed = True

    root = FakeRoot()
    monkeypatch.setattr(tkinter, "Tk", lambda: root)
    state = GameState("easy")
    initial_board = [row[:] for row in state.board]
    errors = []
    monkeypatch.setattr(simpledialog, "askstring", lambda *_args, **_kwargs: "invalid")
    monkeypatch.setattr(
        messagebox, "showerror", lambda title, message, **_kwargs: errors.append((title, message))
    )
    session = Game.__new__(Game)
    session.state = state

    session._handle_import()

    assert state.board == initial_board
    assert errors and errors[0][0] == "Import Puzzle"
    assert root.destroyed
