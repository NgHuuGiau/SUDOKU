"""Headless smoke test for the Pygame rendering pipeline."""

import os
from typing import cast

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

import game
import ui.board as board_ui
from config import game_text
from game import AppController, Game, GameState
from logic import export_puzzle
from persistence import LeaderboardData, load_best_times, load_daily_stats, load_game_state
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


def test_name_entry_submit_adds_leaderboard_entry(monkeypatch):
    from persistence import load_leaderboard

    state = GameState("easy")
    state.final_time = 95
    session = Game.__new__(Game)
    session.state = state
    session.text_input = None

    session._show_name_input_dialog()

    assert session.text_input is not None
    assert session.text_input["kind"] == "name"
    session.text_input["value"] = "Tester"
    session._submit_text_input()

    assert session.text_input is None
    assert load_leaderboard()["easy"] == [
        entry for entry in load_leaderboard()["easy"] if entry["name"] == "Tester"
    ]
    assert any(entry["time"] == 95 for entry in load_leaderboard()["easy"])


def test_name_entry_escape_cancels_without_saving(monkeypatch):
    from persistence import load_leaderboard

    state = GameState("easy")
    state.final_time = 95
    session = Game.__new__(Game)
    session.state = state
    session.text_input = None
    session.text_ok_rect = None
    session.text_cancel_rect = None

    session._show_name_input_dialog()
    assert session.text_input is not None
    session.text_input["value"] = "Nobody"
    escape = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE, unicode="")
    session._handle_text_input_event(escape)

    assert session.text_input is None
    assert load_leaderboard()["easy"] == []


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


def test_import_submit_replaces_game_state():
    state = GameState("easy")
    board = [row[:] for row in state.solution]
    board[0][0] = 0
    session = Game.__new__(Game)
    session.state = state
    session.toast_text = None

    session._handle_import()

    assert session.text_input is not None
    assert session.text_input["kind"] == "import"
    session.text_input["value"] = export_puzzle(board, state.solution)
    session._submit_text_input()

    assert session.text_input is None
    assert state.board == board
    assert state.original == board
    assert state.selected == [0, 0]
    assert not state.paused


def test_invalid_import_shows_error_and_keeps_game():
    state = GameState("easy")
    initial_board = [row[:] for row in state.board]
    session = Game.__new__(Game)
    session.state = state

    session._handle_import()
    assert session.text_input is not None
    session.text_input["value"] = "invalid"
    session._submit_text_input()

    assert state.board == initial_board
    assert session.text_input is not None
    assert session.text_input["error"] == "import_invalid"
    assert game_text("import_invalid") != "import_invalid"


def test_export_copies_puzzle_to_clipboard(monkeypatch):
    state = GameState("easy")
    session = Game.__new__(Game)
    session.state = state
    copied = []
    monkeypatch.setattr(pygame.scrap, "init", lambda: None)
    monkeypatch.setattr(pygame.scrap, "put", lambda kind, data: copied.append((kind, data)))

    session._handle_export()

    assert copied == [
        (
            pygame.SCRAP_TEXT,
            export_puzzle(state.board, state.solution).encode("utf-8"),
        )
    ]
    assert session.toast_text == game_text("export_copied")


def test_export_failure_shows_toast(monkeypatch):
    session = Game.__new__(Game)
    session.state = GameState("easy")
    monkeypatch.setattr(pygame.scrap, "init", lambda: None)

    def fail_put(_kind, _data):
        raise RuntimeError("no clipboard")

    monkeypatch.setattr(pygame.scrap, "put", fail_put)

    session._handle_export()

    assert session.toast_text == game_text("export_failed")


def _make_event_session(monkeypatch):
    """Bare Game session with every optional rect initialized."""
    session = Game.__new__(Game)
    session.state = GameState("easy")
    session.running = True
    session.go_to_menu = False
    session.show_help = False
    session.text_input = None
    session.text_ok_rect = None
    session.text_cancel_rect = None
    session.toast_text = None
    session.toast_until = 0
    session.particles = []
    session.header_pause_rect = None
    session.header_theme_rect = None
    session.header_sound_rect = None
    session.header_help_rect = None
    session.pause_resume_rect = None
    session.pause_restart_rect = None
    session.pause_save_quit_rect = None
    session.pause_quit_rect = None
    session.win_restart_rect = None
    session.win_quit_rect = None
    session.help_rects = None
    monkeypatch.setattr(game, "play_sound", lambda _sound: None)
    return session


def _empty_selected(session):
    state = session.state
    row, col = next((r, c) for r in range(9) for c in range(9) if state.board[r][c] == 0)
    state.selected = [row, col]
    state.original[row][col] = 0
    return row, col


def test_mouse_selects_board_cell(monkeypatch):
    session = _make_event_session(monkeypatch)

    session._handle_mouse((BOARD_X + CELL_SIZE * 2 + 3, BOARD_Y + CELL_SIZE * 3 + 3))

    assert session.state.selected == [3, 2]


def test_mouse_sidebar_quick_actions(monkeypatch):
    session = _make_event_session(monkeypatch)
    _empty_selected(session)
    layout = get_sidebar_layout()

    session._handle_mouse(layout["quick_notes"].center)
    assert session.state.notes_mode
    session._handle_mouse(layout["quick_notes"].center)
    assert not session.state.notes_mode

    session._handle_mouse(layout["quick_check_errors"].center)
    assert session.state.show_errors

    session._handle_mouse(layout["quick_hint"].center)
    row, col = session.state.selected
    assert session.state.board[row][col] == session.state.solution[row][col]

    session._handle_mouse(layout["quick_undo"].center)
    assert session.state.board[row][col] == 0
    session._handle_mouse(layout["quick_redo"].center)
    assert session.state.board[row][col] == session.state.solution[row][col]


def test_mouse_number_pad_clear_and_auto_notes(monkeypatch):
    session = _make_event_session(monkeypatch)
    row, col = _empty_selected(session)
    layout = get_sidebar_layout()

    session._handle_mouse(layout["numbers"][3].center)
    assert session.state.board[row][col] == 4

    session._handle_mouse(layout["clear"].center)
    assert session.state.board[row][col] == 0

    session._handle_mouse(layout["auto_notes"].center)
    assert len(session.state.notes[row][col]) > 0


def test_mouse_header_buttons(monkeypatch):
    session = _make_event_session(monkeypatch)
    toggles = []
    monkeypatch.setattr(game, "toggle_sound", lambda: toggles.append(True))
    session.header_pause_rect = pygame.Rect(0, 0, 20, 20)
    session.header_theme_rect = pygame.Rect(25, 0, 20, 20)
    session.header_sound_rect = pygame.Rect(50, 0, 20, 20)
    session.header_help_rect = pygame.Rect(75, 0, 20, 20)

    session._handle_mouse((10, 10))
    assert session.state.paused
    session.state.toggle_pause()

    before_theme = game.get_theme_manager().theme
    session._handle_mouse((35, 10))
    assert game.get_theme_manager().theme != before_theme

    session._handle_mouse((60, 10))
    assert toggles == [True]

    session._handle_mouse((85, 10))
    assert session.show_help


def test_mouse_new_game_menu_and_dialog_shortcuts(monkeypatch):
    session = _make_event_session(monkeypatch)
    layout = get_sidebar_layout()
    first_board = [row[:] for row in session.state.board]

    session._handle_mouse(layout["new_game"].center)
    assert session.running
    assert not session.state.game_over

    session._handle_mouse(layout["export"].center)
    assert session.toast_text is not None

    session._handle_mouse(layout["import"].center)
    assert session.text_input is not None and session.text_input["kind"] == "import"
    session.text_input = None

    session._handle_mouse(layout["menu"].center)
    assert not session.running
    assert session.go_to_menu
    assert first_board  # silence unused-variable lint


def test_keyboard_moves_selects_digits_and_deletes():
    session = Game.__new__(Game)
    session.state = GameState("easy")
    session.state.selected = [4, 4]

    session._handle_keyboard(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP, mod=0))
    session._handle_keyboard(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT, mod=0))
    assert session.state.selected == [3, 3]

    row, col = _empty_selected(session)
    value = session.state.solution[row][col]
    session._handle_keyboard(
        pygame.event.Event(
            pygame.KEYDOWN, key=getattr(pygame, f"K_{value}"), unicode=str(value), mod=0
        )
    )
    assert session.state.board[row][col] == value
    session._handle_keyboard(
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_BACKSPACE, unicode="", mod=0)
    )
    assert session.state.board[row][col] == 0


def test_keyboard_ctrl_undo_redo_and_notes_toggle():
    session = Game.__new__(Game)
    session.state = GameState("easy")
    row, col = _empty_selected(session)
    session.state.place_number(7)
    assert session.state.board[row][col] == 7

    session._handle_keyboard(
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_z, unicode="", mod=pygame.KMOD_CTRL)
    )
    assert session.state.board[row][col] == 0
    session._handle_keyboard(
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_y, unicode="", mod=pygame.KMOD_CTRL)
    )
    assert session.state.board[row][col] == 7
    session._handle_keyboard(
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE, unicode=" ", mod=0)
    )
    assert session.state.notes_mode


def test_text_input_mouse_ok_and_cancel(monkeypatch):
    session = _make_event_session(monkeypatch)
    board = [row[:] for row in session.state.solution]
    board[0][0] = 0
    session.text_ok_rect = pygame.Rect(0, 0, 40, 20)
    session.text_cancel_rect = pygame.Rect(50, 0, 40, 20)

    session._handle_import()
    session.text_input["value"] = export_puzzle(board, session.state.solution)
    session._handle_text_input_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(20, 10)))
    assert session.text_input is None
    assert session.state.board == board

    before = [row[:] for row in session.state.board]
    session._handle_import()
    session._handle_text_input_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(70, 10)))
    assert session.text_input is None
    assert session.state.board == before


def test_win_update_registers_score_and_clears_save(monkeypatch):
    session = _make_event_session(monkeypatch)
    session.state.board = [row[:] for row in session.state.solution]
    monkeypatch.setattr(session, "_spawn_win_fireworks", lambda: None)

    session.update()

    assert session.state.game_over
    assert session.text_input is not None
    session.text_input["value"] = "Winner"
    session._submit_text_input()
    leaderboard = cast(LeaderboardData, game.get_leaderboard())
    assert any(e["name"] == "Winner" for e in leaderboard["easy"])
    assert not game.has_save_file()


def test_gameover_click_restart_and_menu(monkeypatch):
    session = _make_event_session(monkeypatch)
    session.state.game_over = True
    session.win_restart_rect = pygame.Rect(0, 0, 40, 20)
    session.win_quit_rect = pygame.Rect(50, 0, 40, 20)

    session._handle_gameover_click((20, 10))
    assert not session.state.game_over

    session.state.game_over = True
    session._handle_gameover_click((70, 10))
    assert not session.running
    assert session.go_to_menu


def test_pause_click_restart_and_save_quit(monkeypatch):
    session = _make_event_session(monkeypatch)
    session.state.paused = True
    session.pause_resume_rect = pygame.Rect(0, 0, 40, 20)
    session.pause_restart_rect = pygame.Rect(50, 0, 40, 20)
    session.pause_save_quit_rect = pygame.Rect(100, 0, 40, 20)

    session._handle_pause_click((60, 10))
    assert not session.state.paused

    session.state.paused = True
    session._handle_pause_click((110, 10))
    assert not session.running
    assert session.go_to_menu

    fresh = _make_event_session(monkeypatch)
    fresh.state.paused = True
    fresh.pause_resume_rect = pygame.Rect(0, 0, 40, 20)
    fresh._handle_pause_click((20, 10))
    assert not fresh.state.paused


def test_help_click_closes_overlay(monkeypatch):
    session = _make_event_session(monkeypatch)
    session.show_help = True
    close_rect = pygame.Rect(10, 10, 30, 30)
    session.help_rects = {"help_close": close_rect}

    session._handle_help_click(close_rect.center)

    assert not session.show_help


def test_menu_resume_daily_and_preference_buttons(monkeypatch):
    saved = GameState("easy")
    assert saved.force_save()

    class StubGame:
        def __init__(self, difficulty, loaded_state=None, screen=None):
            self.difficulty = difficulty
            self.loaded_state = loaded_state

    monkeypatch.setattr(game, "Game", StubGame)
    monkeypatch.setattr(game, "toggle_sound", lambda: None)
    controller = AppController.__new__(AppController)
    controller.screen = pygame.Surface((1, 1))
    controller.state = AppController.STATE_MENU
    controller.running = True
    controller.custom_cells = 40
    controller.menu_focus_key = None

    def click(key):
        rect = pygame.Rect(0, 0, 20, 20)
        monkeypatch.setattr(
            pygame.event,
            "get",
            lambda: [pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=rect.center)],
        )
        controller._handle_menu_events({key: rect})

    click("resume")
    assert controller.state == AppController.STATE_PLAYING
    assert getattr(controller.game_session, "loaded_state", None) is not None

    controller.state = AppController.STATE_MENU
    click("daily")
    assert getattr(controller.game_session, "difficulty", None) == "daily"

    before_theme = game.get_theme_manager().theme
    click("theme")
    assert game.get_theme_manager().theme != before_theme

    click("sound")
    click("lang")
    click("help")
    assert controller.state == AppController.STATE_HELP


def test_handle_events_escape_f1_and_text_modal_priority(monkeypatch):
    session = _make_event_session(monkeypatch)
    monkeypatch.setattr(
        pygame.event, "get", lambda: [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_F1)]
    )
    assert session.handle_events()
    assert session.show_help

    session._handle_import()
    paused_before = session.state.paused
    monkeypatch.setattr(
        pygame.event,
        "get",
        lambda: [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE, unicode="")],
    )
    assert session.handle_events()
    assert session.text_input is None
    assert session.state.paused == paused_before


def test_text_input_modal_buttons_are_visible_and_do_not_overlap():
    from ui.modals import draw_text_input_modal

    pygame.init()
    screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    rects = draw_text_input_modal(
        screen, load_fonts(), (0, 0), game_text, "Title", "Prompt", "value", "Error"
    )
    buttons = [rects["text_ok"], rects["text_cancel"]]

    assert all(rect is not None for rect in buttons)
    assert all(screen.get_rect().contains(rect) for rect in buttons)
    assert not buttons[0].colliderect(buttons[1])


def test_soft_tint_blends_icon_color_toward_card():
    from ui.drawing import soft_tint

    tint = soft_tint((255, 0, 0), (255, 255, 255))
    assert tint == (255, 214, 214)
    assert all(card >= channel for card, channel in zip((255, 255, 255), tint, strict=True))


def test_icon_tile_renders_visible_glyph():
    from ui.colors import Colors
    from ui.drawing import draw_icon_tile

    pygame.init()
    screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.fill((0, 0, 0))
    tile = pygame.Rect(100, 100, 52, 52)
    draw_icon_tile(screen, tile, "hint", Colors.ICON_HINT, icon_size=24)

    assert any(
        screen.get_at((x, y))[:3] != (0, 0, 0)
        for x in range(tile.left, tile.right)
        for y in range(tile.top, tile.bottom)
    )


def test_modern_button_renders_icon_in_icon_color():
    from ui.colors import Colors
    from ui.drawing import draw_modern_button

    pygame.init()
    screen = pygame.Surface((120, 60))
    screen.fill(Colors.BG_CARD)
    rect = pygame.Rect(10, 5, 100, 50)
    draw_modern_button(
        screen,
        rect,
        "",
        (-1, -1),
        load_fonts().small,
        variant="secondary",
        icon_name="erase",
        icon_size=22,
        icon_color=Colors.ICON_ERASE,
    )

    icon_pixels = [
        tuple(screen.get_at((x, y))[:3])
        for x in range(rect.left, rect.right)
        for y in range(rect.top, rect.bottom)
    ]
    assert any(red > 180 and green < 120 for red, green, _blue in icon_pixels)


def test_win_modal_shows_best_time_and_new_best_badge(monkeypatch):
    import persistence
    from ui.modals import draw_win_modal

    state = GameState("easy")
    state.final_time = 125
    monkeypatch.setattr(persistence, "load_best_times", lambda: {**load_best_times(), "easy": 125})

    pygame.init()
    screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    rects = draw_win_modal(screen, load_fonts(), (0, 0), game_text, state, [])

    assert rects["win_restart"] is not None
    assert rects["win_quit"] is not None


def test_sidebar_renders_mistakes_pill_with_wrong_cells(monkeypatch):
    from ui.colors import Colors
    from ui.sidebar import draw_sidebar

    session = _make_event_session(monkeypatch)
    row, col = next((r, c) for r in range(9) for c in range(9) if session.state.original[r][c] == 0)
    session.state.board[row][col] = session.state.solution[row][col] % 9 + 1

    pygame.init()
    screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.fill(Colors.BG_MAIN)
    layout = draw_sidebar(screen, load_fonts(), (0, 0), game_text, session.state)

    assert layout["quick_notes"] is not None
    assert layout["numbers"] is not None
    # Mistakes pill sits right of the number-pad header: tinted pixels there.
    pill_zone = [
        screen.get_at((x, y))[:3]
        for x in range(layout["numbers"][-1].right - 110, layout["numbers"][-1].right)
        for y in range(layout["numbers"][0].top - 34, layout["numbers"][0].top - 2)
    ]
    assert any(px != Colors.BG_CARD[:3] for px in pill_zone)
