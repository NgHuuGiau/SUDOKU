"""Headless smoke test for the Pygame rendering pipeline."""

import os
from typing import cast

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
import pytest

import game
import ui.board as board_ui
from game import AppController, Game, GameState
from persistence import LeaderboardData, load_daily_stats, load_game_state
from ui import create_game_screen, draw_game_view, load_fonts
from ui.geometry import (
    BOARD_SIZE,
    BOARD_X,
    BOARD_Y,
    CELL_SIZE,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    get_cell_from_pos,
    get_sidebar_layout,
)
from ui.icons import SmoothIcons
from ui.menu import draw_menu_view


def test_game_view_renders_headless():
    screen = create_game_screen()
    state = GameState("easy")
    draw_game_view(screen, load_fonts(), state, (0, 0))
    pygame.quit()


def test_board_validates_each_player_entry_once_per_frame(monkeypatch):
    screen = create_game_screen()
    state = GameState("easy")
    row, col = next((r, c) for r in range(9) for c in range(9) if state.board[r][c] == 0)
    state.board[row][col] = state.solution[row][col]

    calls = 0
    validate = board_ui.is_valid_placement

    def count_validations(board, r, c, value):
        nonlocal calls
        calls += 1
        return validate(board, r, c, value)

    monkeypatch.setattr(board_ui, "is_valid_placement", count_validations)
    board_ui.draw_board(screen, load_fonts(), state)

    assert calls == 1
    pygame.quit()


def test_menu_renders_headless():
    screen = create_game_screen()
    draw_menu_view(screen, load_fonts(), (0, 0))
    pygame.quit()


def test_custom_menu_card_hides_chevron_from_stepper_controls():
    from ui.colors import Colors
    from ui.drawing import draw_interactive_card

    pygame.font.init()
    screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    card = pygame.Rect(100, 100, 640, 58)
    draw_interactive_card(
        screen,
        card,
        (0, 0),
        "Tùy chỉnh",
        "Số ô trống",
        load_fonts(),
        Colors.BTN_PRIMARY,
        show_chevron=False,
    )

    chevron_area = pygame.Rect(card.right - 32, card.centery - 9, 18, 18)
    assert all(
        screen.get_at((x, y))[:3] == Colors.BG_CARD
        for x in range(chevron_area.left, chevron_area.right)
        for y in range(chevron_area.top, chevron_area.bottom)
    )


def test_menu_snapshot_avoids_reloading_persistence_each_frame(monkeypatch):
    import ui.menu as menu_ui

    def unexpected_disk_read(*_args, **_kwargs):
        raise AssertionError("menu should use the supplied snapshot")

    for name in ("load_best_times", "load_daily_stats", "has_save_file", "load_game_state"):
        monkeypatch.setattr(menu_ui, name, unexpected_disk_read)

    screen = create_game_screen()
    menu_data = {
        "best_times": {"easy": None, "medium": None, "hard": None},
        "daily_stats": {"streak": 0, "last_completed_date": None},
        "save_exists": False,
        "saved_game": None,
    }
    draw_menu_view(screen, load_fonts(), (0, 0), menu_data=menu_data)
    pygame.quit()


def test_leaderboard_snapshot_avoids_reloading_persistence_each_frame(monkeypatch):
    import persistence
    from config import game_text
    from ui.modals import draw_leaderboard_modal

    def unexpected_disk_read(*_args, **_kwargs):
        raise AssertionError("leaderboard should use the supplied snapshot")

    monkeypatch.setattr(persistence, "get_leaderboard", unexpected_disk_read)
    pygame.init()
    screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    leaderboard_data = cast(
        LeaderboardData,
        {difficulty: [] for difficulty in ("easy", "medium", "hard", "daily", "custom")},
    )

    draw_leaderboard_modal(
        screen,
        load_fonts(),
        (0, 0),
        game_text,
        leaderboard_data=leaderboard_data,
    )


def test_opening_leaderboard_loads_one_snapshot(monkeypatch):
    controller = AppController.__new__(AppController)
    controller.state = AppController.STATE_MENU
    controller.running = True
    snapshot = cast(
        LeaderboardData,
        {difficulty: [] for difficulty in ("easy", "medium", "hard", "daily", "custom")},
    )
    monkeypatch.setattr(game, "get_leaderboard", lambda: snapshot)
    stats_rect = pygame.Rect(10, 10, 30, 30)
    monkeypatch.setattr(
        pygame.event,
        "get",
        lambda: [pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=stats_rect.center)],
    )

    controller._handle_menu_events({"stats": stats_rect})

    assert controller.state == AppController.STATE_LEADERBOARD
    assert controller.leaderboard_data is snapshot


def test_sidebar_layout_has_no_overlapping_controls():
    layout = get_sidebar_layout()
    controls = [value for key, value in layout.items() if key != "numbers" and value is not None]
    controls.extend(layout["numbers"])

    assert all(0 <= rect.left and rect.right <= SCREEN_WIDTH for rect in controls)
    assert all(0 <= rect.top and rect.bottom <= SCREEN_HEIGHT for rect in controls)
    for index, rect in enumerate(controls):
        assert not any(rect.colliderect(other) for other in controls[index + 1 :])


def test_board_hitboxes_match_rendered_cell_edges():
    assert BOARD_SIZE == CELL_SIZE * 9
    for row in range(9):
        for column in range(9):
            x = BOARD_X + column * CELL_SIZE
            y = BOARD_Y + row * CELL_SIZE
            assert get_cell_from_pos(x, y) == (row, column)
            assert get_cell_from_pos(x + CELL_SIZE - 1, y + CELL_SIZE - 1) == (row, column)

    assert get_cell_from_pos(BOARD_X + BOARD_SIZE, BOARD_Y) is None
    assert get_cell_from_pos(BOARD_X, BOARD_Y + BOARD_SIZE) is None


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


def test_menu_keyboard_focus_activates_selected_difficulty(monkeypatch):
    controller = AppController.__new__(AppController)
    controller.state = AppController.STATE_MENU
    controller.running = True
    started: list[str] = []
    monkeypatch.setattr(controller, "_start_game", started.append)
    events = [
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_TAB, mod=0),
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_TAB, mod=0),
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN, mod=0),
    ]
    monkeypatch.setattr(pygame.event, "get", lambda: events)
    menu_rects = {
        "easy": pygame.Rect(0, 0, 20, 20),
        "medium": pygame.Rect(30, 0, 20, 20),
        "hard": pygame.Rect(60, 0, 20, 20),
    }

    controller._handle_menu_events(menu_rects)

    assert started == ["medium"]


def test_shift_tab_wraps_to_last_menu_action(monkeypatch):
    controller = AppController.__new__(AppController)
    controller.state = AppController.STATE_MENU
    controller.running = True
    started: list[str] = []
    monkeypatch.setattr(controller, "_start_game", started.append)
    events = [
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_TAB, mod=pygame.KMOD_SHIFT),
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE, mod=0),
    ]
    monkeypatch.setattr(pygame.event, "get", lambda: events)
    menu_rects = {
        "easy": pygame.Rect(0, 0, 20, 20),
        "medium": pygame.Rect(30, 0, 20, 20),
        "hard": pygame.Rect(60, 0, 20, 20),
    }

    controller._handle_menu_events(menu_rects)

    assert started == ["hard"]


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


def test_pause_save_failure_keeps_game_open_and_reports_failure(monkeypatch):
    state = GameState("easy")
    state.paused = True
    state.save_failed = True
    session = Game.__new__(Game)
    session.state = state
    session.running = True
    session.go_to_menu = False
    session.pause_resume_rect = None
    session.pause_restart_rect = None
    save_quit_rect = pygame.Rect(10, 10, 40, 40)
    session.pause_save_quit_rect = save_quit_rect
    session.pause_quit_rect = save_quit_rect
    force_save_calls: list[bool] = []

    def fail_save() -> bool:
        force_save_calls.append(True)
        return False

    monkeypatch.setattr(state, "force_save", fail_save)

    session._handle_pause_click(save_quit_rect.center)

    assert session.running
    assert not session.go_to_menu
    assert state.save_failed
    assert force_save_calls == [True]


def test_modern_icon_renderer_returns_visible_icon_at_requested_size():
    icon = SmoothIcons.get("grid_logo", 32, (30, 100, 180))

    assert icon.get_size() == (32, 32)
    assert icon.get_bounding_rect() != pygame.Rect(0, 0, 0, 0)


def test_start_new_game_and_resume_saved_game(monkeypatch):
    class StubGame:
        def __init__(self, difficulty, loaded_state=None, screen=None):
            self.loaded_state = loaded_state
            self.screen = screen

    monkeypatch.setattr(game, "Game", StubGame)
    controller = AppController.__new__(AppController)
    controller.screen = pygame.Surface((1, 1))
    controller.state = AppController.STATE_MENU

    controller._start_game("easy")
    assert isinstance(controller.game_session, StubGame)
    assert controller.game_session.screen is controller.screen

    saved_state = GameState("easy")
    controller._start_game("easy", loaded_state=saved_state)
    assert controller.game_session.loaded_state is saved_state


def test_game_reuses_supplied_screen_without_reinitializing_display(monkeypatch):
    screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

    def unexpected_screen_creation():
        raise AssertionError("Game should reuse the controller's display")

    monkeypatch.setattr(game, "create_game_screen", unexpected_screen_creation)

    session = Game("easy", loaded_state=GameState("easy"), screen=screen)

    assert session.screen is screen


def test_highscore_dialog_closes_tk_root_when_prompt_raises(monkeypatch):
    import tkinter
    from tkinter import simpledialog

    class FakeRoot:
        destroyed = False

        def withdraw(self):
            pass

        def attributes(self, *_args):
            pass

        def destroy(self):
            self.destroyed = True

    root = FakeRoot()
    monkeypatch.setattr(tkinter, "Tk", lambda: root)

    def fail_prompt(*_args, **_kwargs):
        raise RuntimeError("dialog failed")

    monkeypatch.setattr(simpledialog, "askstring", fail_prompt)
    session = Game.__new__(Game)
    session.state = GameState("easy")

    with pytest.raises(RuntimeError, match="dialog failed"):
        session._show_name_input_dialog()

    assert root.destroyed


def test_restart_resets_session_flags():
    session = Game.__new__(Game)
    session.particles = []
    session.state = GameState("easy")
    session.state.game_over = True
    session.state.paused = True

    session._restart_game()

    assert not session.state.game_over
    assert not session.state.paused


def test_winning_daily_game_updates_daily_stats(monkeypatch):
    class StubGame(Game):
        def _spawn_win_fireworks(self):
            pass

    state = GameState("daily")
    state.board = [row[:] for row in state.solution]

    session = StubGame.__new__(StubGame)
    session.state = state
    session.particles = []
    monkeypatch.setattr(game, "play_sound", lambda _sound: None)
    monkeypatch.setattr("persistence.is_top_10_time", lambda _difficulty, _elapsed: False)

    session.update()

    assert state.game_over
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


def test_unicode_digit_does_not_crash_keyboard_input(monkeypatch):
    state = GameState("easy")
    session = Game.__new__(Game)
    session.state = state
    session.show_help = False
    row, column = next((r, c) for r in range(9) for c in range(9) if state.original[r][c] == 0)
    state.selected = [row, column]
    event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UNKNOWN, unicode="²", mod=0)
    monkeypatch.setattr(pygame.event, "get", lambda: [event])

    assert session.handle_events()
    assert state.board[row][column] == 0


def test_backspace_with_empty_unicode_clears_selected_cell(monkeypatch):
    state = GameState("easy")
    session = Game.__new__(Game)
    session.state = state
    session.show_help = False
    row, column = next((r, c) for r in range(9) for c in range(9) if state.original[r][c] == 0)
    state.selected = [row, column]
    state.board[row][column] = state.solution[row][column]
    event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_BACKSPACE, unicode="", mod=0)
    monkeypatch.setattr(pygame.event, "get", lambda: [event])

    assert session.handle_events()
    assert state.board[row][column] == 0


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


def test_window_close_keeps_game_open_when_save_fails(monkeypatch):
    state = GameState("easy")
    state.save_failed = True
    session = Game.__new__(Game)
    session.state = state
    session.running = True
    monkeypatch.setattr(state, "force_save", lambda: False)
    monkeypatch.setattr(pygame.event, "get", lambda: [pygame.event.Event(pygame.QUIT)])

    assert session.handle_events()
    assert session.running
    assert state.save_failed


def test_window_close_does_not_retry_save_after_game_is_complete(monkeypatch):
    state = GameState("easy")
    state.game_over = True
    state.save_failed = True
    session = Game.__new__(Game)
    session.state = state
    session.running = True

    def unexpected_save():
        raise AssertionError("completed games need no save")

    monkeypatch.setattr(state, "force_save", unexpected_save)
    monkeypatch.setattr(pygame.event, "get", lambda: [pygame.event.Event(pygame.QUIT)])

    assert not session.handle_events()
    assert not session.running


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
    assert errors and errors[0] == (
        "Nhập ván",
        "Bảng Sudoku không hợp lệ hoặc không có đúng một lời giải.",
    )
    assert root.destroyed
