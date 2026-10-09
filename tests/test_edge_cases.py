"""Regression tests for application edge cases and failure paths."""

import copy
import json
import os
import runpy
import sys

import pygame
import pytest

import sudoku.game as game_module
import sudoku.persistence as persistence
import sudoku.sounds as sounds
import sudoku.ui.board as board_ui
from sudoku.game import Game, GameState
from sudoku.ui.fonts import load_fonts
from sudoku.ui.geometry import SCREEN_HEIGHT, SCREEN_WIDTH


@pytest.fixture(autouse=True)
def reset_sound_manager_after_test():
    yield
    sounds._sound_manager = None


def test_sound_generation_and_manager_failure_paths(monkeypatch):
    captured = []

    class Sound:
        def __init__(self, buffer):
            captured.append(buffer)

        def play(self):
            return None

    monkeypatch.setattr(sounds.pygame.mixer, "Sound", Sound)
    for generate in (
        sounds.generate_tone,
        sounds.generate_click,
        sounds.generate_pop,
        sounds.generate_success,
        sounds.generate_hint,
        sounds.generate_undo,
    ):
        generate(50, 0.1, sample_rate=1000) if generate is sounds.generate_tone else generate()
    assert [len(samples) for samples in captured] == [100, 2205, 3528, 22050, 13230, 6615]
    assert all(any(samples) for samples in captured)

    monkeypatch.setattr(sounds, "get_preference", lambda *_: "invalid")
    monkeypatch.setattr(
        sounds, "generate_click", lambda: (_ for _ in ()).throw(pygame.error("no device"))
    )
    manager = sounds.SoundManager()
    assert manager.is_enabled() and manager.sounds == {}
    manager.play("missing")

    monkeypatch.setattr(sounds, "get_sound_manager", lambda: manager)
    assert sounds.get_sound_manager() is manager
    sounds.play_sound("missing")
    sounds.toggle_sound()
    assert sounds.is_sound_enabled() == manager.is_enabled()


def test_board_draws_notes_errors_and_each_completion_animation(monkeypatch):
    pygame.init()
    state = GameState("easy")
    state.paused = False
    state.selected = [0, 0]
    row, col = next((r, c) for r in range(9) for c in range(9) if state.original[r][c] == 0)
    state.selected = [row, col]
    state.board[row][col] = state.solution[row][col] % 9 + 1
    state.show_errors = True
    state.notes[(row + 1) % 9][(col + 1) % 9].update(range(1, 10))
    note_cell = next(
        (r, c)
        for r in range(9)
        for c in range(9)
        if state.board[r][c] == 0 and (r, c) != (row, col)
    )
    state.notes[note_cell[0]][note_cell[1]].update(range(1, 10))
    times = iter([10.0, 10.1, 10.2, 10.3])
    monkeypatch.setattr(board_ui.time, "monotonic", lambda: next(times, 10.3))
    board_ui._cell_animations.clear()
    board_ui._cell_animations[(row, col)] = 10.0
    board_ui._completion_animations[:] = [
        {"type": shape, "index": i, "start_time": 10.0, "duration": 0.6}
        for i, shape in enumerate(("row", "col", "box"))
    ]
    board_ui.trigger_completion_animation("row", 2)
    screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    board_ui.draw_board(screen, load_fonts(), state)
    assert len(board_ui._completion_animations) >= 3
    assert board_ui._get_cell_animation_progress(8, 8) == 1
    monkeypatch.setattr(board_ui.time, "monotonic", lambda: 10.1)
    assert 0 < board_ui._get_cell_animation_progress(row, col) < 1
    monkeypatch.setattr(board_ui.time, "monotonic", lambda: 10.4)
    assert board_ui._get_cell_animation_progress(row, col) == 1

    state.paused = True
    monkeypatch.setattr(board_ui.time, "monotonic", lambda: 11.0)
    board_ui.draw_board(screen, load_fonts(), state)
    assert board_ui._completion_animations == []


def test_persistence_json_io_failure_paths(monkeypatch, tmp_path):
    path = tmp_path / "data.json"
    monkeypatch.setattr(persistence, "_runtime_file", lambda _name: str(path))
    assert persistence._load_json(str(path), {"default": True}) == {"default": True}
    path.write_text("[]", encoding="utf-8")
    assert persistence._load_json(str(path), {"default": True}) == {"default": True}
    path.write_text("{", encoding="utf-8")
    assert persistence._load_json(str(path), {}) == {}

    with monkeypatch.context() as scoped:
        scoped.setattr(
            persistence.os, "replace", lambda *_: (_ for _ in ()).throw(OSError("locked"))
        )
        assert persistence._save_json(str(path), {"ok": True}) is False
    with monkeypatch.context() as scoped:
        scoped.setattr(
            persistence.os, "replace", lambda *_: (_ for _ in ()).throw(OSError("locked"))
        )
        scoped.setattr(
            persistence.os, "remove", lambda *_: (_ for _ in ()).throw(OSError("locked"))
        )
        assert persistence._save_json(str(path), {"ok": True}) is False


@pytest.mark.parametrize(
    "mutate",
    [
        lambda d: d.update(difficulty="unknown"),
        lambda d: d.update(board=[]),
        lambda d: d.update(solution=[[0] * 9 for _ in range(9)]),
        lambda d: d.update(selected=[9, 0]),
        lambda d: d.update(notes_mode=1),
        lambda d: d.update(paused_time=-1),
        lambda d: d.update(elapsed_time=-1),
        lambda d: d.update(custom_empty_cells=61),
        lambda d: d.update(undo_stack=[None]),
        lambda d: d.update(redo_stack="bad"),
    ],
)
def test_load_game_rejects_each_invalid_save_section(mutate, tmp_path, monkeypatch):
    board, solution = game_module.generate_sudoku("easy", seed=17)
    data = {
        "difficulty": "easy",
        "custom_empty_cells": 40,
        "board": board,
        "solution": solution,
        "original": copy.deepcopy(board),
        "selected": [0, 0],
        "notes": [[[] for _ in range(9)] for _ in range(9)],
        "notes_mode": False,
        "game_over": False,
        "paused": False,
        "show_errors": False,
        "start_time": 0,
        "paused_time": 0,
        "last_pause_start": 0,
        "last_active_time": 0,
        "final_time": 0,
        "elapsed_time": 0,
        "undo_stack": [],
        "redo_stack": [],
    }
    mutate(data)
    path = tmp_path / "save.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    monkeypatch.setattr(persistence, "_runtime_file", lambda _name: str(path))
    assert persistence.load_game_state() is None


def test_game_state_mutations_and_save_debounce(monkeypatch):
    state = GameState("easy")
    state.selected = list(
        next((r, c) for r in range(9) for c in range(9) if state.board[r][c] == 0)
    )
    r, c = state.selected
    state.notes_mode = True
    state.place_number(1)
    assert 1 in state.notes[r][c]
    state.place_number(1)
    assert 1 not in state.notes[r][c]
    state.clear_cell()
    state.give_hint()
    assert state.board[r][c] == state.solution[r][c]
    state.undo()
    state.redo()
    state.fill_possible_notes()
    state.toggle_pause()
    state.toggle_pause()

    monkeypatch.setattr(game_module.time, "monotonic", lambda: 100)
    calls = []

    def save_ok(_state):
        calls.append(1)
        return True

    monkeypatch.setattr(game_module, "save_game_state", save_ok)
    state._last_auto_save_time = 100_000
    state.auto_save()
    assert calls == []
    state.force_save()
    assert calls == [1]
    state.game_over = True
    assert state.force_save()
    state.save_failed = True
    assert not state.force_save()
    state.auto_save()


def test_game_event_input_mouse_and_render_branches(monkeypatch):
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    session = Game("easy", screen=screen)
    session.render()
    session._show_toast("toast")
    session._draw_toast()
    session._draw_toast()
    session._open_text_input("import", "title", "prompt")
    session.text_input["value"] = "abc"
    session._handle_text_input_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_BACKSPACE))
    assert session.text_input["value"] == "ab"
    session._handle_text_input_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))

    session.state.selected = [0, 0]
    for key in (pygame.K_DOWN, pygame.K_RIGHT, pygame.K_UP, pygame.K_LEFT, pygame.K_SPACE):
        session._handle_keyboard(pygame.event.Event(pygame.KEYDOWN, key=key, mod=0, unicode=""))
    session._handle_mouse((0, 0))
    session.state.paused = True
    session._handle_pause_click((0, 0))
    session.state.game_over = True
    session._handle_gameover_click((0, 0))
    session.show_help = True
    session.help_rects = {"help_close": pygame.Rect(0, 0, 10, 10)}
    session._handle_help_click((1, 1))
    session._spawn_firework_burst(5, 5, 1)
    assert len(session.particles) == 1


def test_game_render_flips_after_all_overlays(monkeypatch):
    pygame.init()
    order = []
    overlay_rects = dict.fromkeys(
        (
            "pause_resume",
            "pause_quit",
            "win_restart",
            "win_quit",
            "header_pause",
            "header_theme",
            "header_sound",
            "header_help",
        )
    )

    def record(name, result=None):
        order.append(name)
        return result

    sidebar_snapshots = []

    def draw_game_view(*_args, **kwargs):
        sidebar_snapshots.append(kwargs["sidebar_data"])
        return record("view", overlay_rects)

    monkeypatch.setattr(game_module, "draw_game_view", draw_game_view)
    monkeypatch.setattr(game_module, "draw_help_modal", lambda *_args: record("help", {}))
    monkeypatch.setattr(
        game_module,
        "draw_text_input_modal",
        lambda *_args: record("input", {"text_ok": None, "text_cancel": None}),
    )
    monkeypatch.setattr(pygame.display, "flip", lambda: order.append("flip"))

    session = Game(loaded_state=object(), screen=pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)))
    session.show_help = True
    session.text_input = {"title": "title", "prompt": "prompt", "value": "", "error": None}
    monkeypatch.setattr(session, "_draw_toast", lambda: order.append("toast"))
    session.render()

    assert order == ["view", "help", "toast", "input", "flip"]
    assert sidebar_snapshots == [session.sidebar_data]


def test_screen_scaling_and_icon_path(monkeypatch):
    import sys

    import sudoku.ui.screen as screen_ui

    assert screen_ui._fit_window_size((1, 1), (100, 100)) == (1, 1)
    monkeypatch.setattr(sys, "_MEIPASS", "bundle", raising=False)
    assert screen_ui.get_sudoku_icon_path().endswith(os.path.join("assets", "icons", "SUDOKU.ico"))


def test_game_event_queue_and_input_validation(monkeypatch):
    pygame.init()
    session = Game("easy", screen=pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)))
    session._open_text_input("import", "title", "prompt")
    events = [
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_BACKSPACE),
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_a, unicode="é"),
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_a, unicode="\n"),
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE),
    ]
    monkeypatch.setattr(pygame.event, "get", lambda: events[:])
    session.handle_events()
    assert session.text_input is None

    session._open_text_input("import", "title", "prompt")
    assert session.text_input is not None
    session.text_input["value"] = "  "
    session._submit_text_input()
    assert session.text_input is None
    session._open_text_input("import", "title", "prompt")
    assert session.text_input is not None
    session.text_input["value"] = "invalid"
    session._submit_text_input()
    assert session.text_input is not None
    assert session.text_input["error"] == "import_invalid"

    session.text_ok_rect = pygame.Rect(0, 0, 20, 20)
    session._open_text_input("name", "title", "prompt")
    assert session.text_input is not None
    session.text_input["value"] = "  Ada  "
    names = []
    monkeypatch.setattr(game_module, "add_leaderboard_entry", lambda *args: names.append(args))
    session._submit_text_input()
    assert names and names[0][1] == "Ada"

    state = session.state
    state.paused = True
    monkeypatch.setattr(
        pygame.event,
        "get",
        lambda: [
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_p),
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(0, 0)),
            pygame.event.Event(pygame.QUIT),
        ],
    )
    assert session.handle_events() is False
    assert session.running is False


def test_app_controller_menu_help_leaderboard_and_loop(monkeypatch):
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    monkeypatch.setattr(game_module, "create_game_screen", lambda: screen)
    controller = game_module.AppController()
    starts = []
    monkeypatch.setattr(
        controller, "_start_game", lambda difficulty, **kwargs: starts.append((difficulty, kwargs))
    )
    rects = {
        key: pygame.Rect(index * 30, 0, 20, 20)
        for index, key in enumerate(controller.MENU_FOCUS_ORDER)
    }
    monkeypatch.setattr(
        pygame.event,
        "get",
        lambda: [
            pygame.event.Event(pygame.MOUSEMOTION, pos=(1, 1)),
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_1, mod=0),
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_2, mod=0),
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_3, mod=0),
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_TAB, mod=pygame.KMOD_SHIFT),
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_TAB, mod=0),
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN, mod=0),
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=rects["custom"].center),
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=rects["custom_dec"].center),
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=rects["custom_inc"].center),
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=rects["easy"].center),
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE, mod=0),
        ],
    )
    controller._handle_menu_events(rects)
    assert starts[:3] == [("easy", {}), ("medium", {}), ("hard", {})]

    for handler, events, rects_arg in (
        (controller._handle_help_events, [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_F1)], {}),
        (
            controller._handle_help_events,
            [pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(5, 5))],
            {"help_close": pygame.Rect(0, 0, 10, 10)},
        ),
        (
            controller._handle_leaderboard_events,
            [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)],
            {},
        ),
        (
            controller._handle_leaderboard_events,
            [pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(5, 5))],
            {
                "tab_custom": pygame.Rect(0, 0, 10, 10),
                "leaderboard_close": pygame.Rect(0, 0, 10, 10),
            },
        ),
    ):
        monkeypatch.setattr(pygame.event, "get", lambda events=events: events)
        handler(rects_arg)

    controller.running = True
    controller.state = controller.STATE_MENU
    monkeypatch.setattr(game_module, "draw_menu_view", lambda *args, **kwargs: {})
    monkeypatch.setattr(
        controller, "_handle_menu_events", lambda _rects: setattr(controller, "running", False)
    )
    controller.run()


def test_app_controller_game_loop_exit_and_main_entry(monkeypatch):
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    monkeypatch.setattr(game_module, "create_game_screen", lambda: screen)
    controller = game_module.AppController()

    class Session:
        running = True

        def handle_events(self):
            self.running = False
            return True

        def update(self):
            pass

        def render(self):
            pass

    controller.game_session = Session()
    controller._run_game_session()
    assert controller.state == controller.STATE_MENU and controller.game_session is None

    main_path = os.path.join(os.path.dirname(game_module.__file__), "main.py")
    import sudoku.ui as ui

    calls = []
    monkeypatch.setattr(ui, "tao_nut_bat_dau", lambda: calls.append("start"))
    monkeypatch.setattr(sys, "argv", [main_path])
    runpy.run_path(main_path, run_name="__main__")
    assert calls == ["start"]


def test_remaining_ui_draw_paths(monkeypatch):
    from sudoku.config import game_text
    from sudoku.ui.colors import COZY_THEME, DARK_THEME, FROST_THEME, LIGHT_THEME, ThemeManager
    from sudoku.ui.drawing import (
        draw_badge,
        draw_icon_tile,
        draw_interactive_card,
        draw_modern_button,
        draw_rounded_card,
        fit_surface,
    )
    from sudoku.ui.icons import _MODERN_ICON_NAMES, Particle, SmoothIcons
    from sudoku.ui.modals import (
        draw_help_modal,
        draw_leaderboard_modal,
        draw_pause_modal,
        draw_text_input_modal,
        draw_win_modal,
    )
    from sudoku.ui.sidebar import draw_sidebar
    from sudoku.ui.view import draw_game_view

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    fonts = load_fonts()
    rect = pygame.Rect(10, 10, 180, 72)
    assert fit_surface(fonts.hero.render("long text" * 5, True, (1, 2, 3)), 20, 8).get_width() <= 20
    draw_icon_tile(screen, rect, "help", (20, 30, 40), bg="transparent")
    draw_icon_tile(screen, rect, "plus", (20, 30, 40))
    draw_rounded_card(screen, rect, (1, 2, 3), shadow=True)
    draw_badge(screen, rect, "A", fonts.badge, (1, 2, 3), (4, 5, 6), icon_name="star")
    draw_interactive_card(
        screen,
        rect,
        rect.center,
        "title",
        "description",
        fonts,
        (10, 20, 30),
        "calendar",
        "NEW",
        text_max_width=60,
    )
    for variant in ("primary", "success", "warning", "danger", "disabled", "secondary"):
        draw_modern_button(
            screen,
            rect,
            "action",
            rect.center,
            fonts.badge,
            variant=variant,
            is_active=variant == "secondary",
        )
    draw_modern_button(screen, rect, "", (0, 0), fonts.badge, icon_name="check")
    draw_modern_button(
        screen, rect, "headline", rect.center, fonts.badge, subtext="detail", sub_font=fonts.tiny
    )
    draw_modern_button(
        screen,
        rect,
        "very long headline",
        rect.center,
        fonts.badge,
        icon_name="help",
        subtext="very long detail",
        sub_font=fonts.tiny,
    )
    draw_modern_button(screen, rect, "headline", rect.center, fonts.badge, icon_name="home")
    draw_modern_button(screen, rect, "", rect.center, fonts.badge)
    assert all(SmoothIcons.get(name, 28, (70, 120, 200)) for name in _MODERN_ICON_NAMES)
    SmoothIcons.get("unlisted", 28, (70, 120, 200))
    particle = Particle(5, 5, (200, 30, 20))
    particle.update()
    particle.draw(screen)
    particle.lifetime = 0
    particle.draw(screen)

    for theme, expected in (
        ("light", LIGHT_THEME),
        ("dark", DARK_THEME),
        ("frost", FROST_THEME),
        ("cozy", COZY_THEME),
        ("unknown", LIGHT_THEME),
    ):
        manager = object.__new__(ThemeManager)
        manager._theme = theme
        assert manager.colors == expected

    state = GameState("easy")
    draw_win_modal(screen, fonts, (0, 0), game_text, state, [particle])
    draw_pause_modal(screen, fonts, (0, 0), game_text, save_failed=True)
    draw_pause_modal(
        screen,
        fonts,
        (0, 0),
        lambda key: "x" if key == "save_failed" else game_text(key),
        save_failed=True,
    )
    empty_lb: dict[str, list[dict[str, object]]] = {
        key: [] for key in ("easy", "medium", "hard", "daily", "custom")
    }
    draw_leaderboard_modal(screen, fonts, (0, 0), game_text, "overview", None)
    draw_leaderboard_modal(screen, fonts, (0, 0), game_text, "overview", empty_lb, {}, {}, {})
    draw_leaderboard_modal(screen, fonts, (0, 0), game_text, "easy", empty_lb)
    populated = dict(empty_lb)
    populated["easy"] = [
        {"name": "A", "time": 1, "date": "2026-01-01"},
        {"name": "B", "time": 2},
        {"name": "C", "time": 3},
    ]
    draw_leaderboard_modal(screen, fonts, (0, 0), game_text, "easy", populated)
    draw_help_modal(screen, fonts, (0, 0), game_text)
    draw_text_input_modal(screen, fonts, (0, 0), game_text, "title", "prompt", "bad text", "error")
    draw_sidebar(screen, fonts, (0, 0), game_text, state)
    state.paused = True
    draw_game_view(screen, fonts, state, (0, 0))
    state.paused = False
    state.game_over = True
    draw_game_view(screen, fonts, state, (0, 0))


def test_small_logic_persistence_and_ui_edges(monkeypatch, tmp_path):
    import importlib
    import types
    from datetime import datetime, timedelta, timezone

    import sudoku.error_handling as error_handling
    import sudoku.logic as logic
    import sudoku.ui.colors as colors
    import sudoku.ui.fonts as fonts_module
    import sudoku.ui.geometry as geometry
    import sudoku.ui.menu as menu_module
    import sudoku.ui.sidebar as sidebar_module
    from sudoku.ui.view import draw_game_view

    monkeypatch.delenv("SUDOKU_DATA_DIR", raising=False)
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setattr(persistence.Path, "home", lambda: home)
    with monkeypatch.context() as scoped:
        scoped.setattr(persistence, "os", types.SimpleNamespace(name="posix", environ=os.environ))
        scoped.setattr(persistence.sys, "platform", "darwin")
        assert (
            persistence.get_data_dir() == home / "Library" / "Application Support" / "SudokuMaster"
        )
    with monkeypatch.context() as scoped:
        scoped.setattr(persistence, "os", types.SimpleNamespace(name="posix", environ=os.environ))
        scoped.setattr(persistence.sys, "platform", "linux")
        scoped.setenv("XDG_DATA_HOME", os.fspath(tmp_path / "xdg"))
        assert persistence.get_data_dir() == tmp_path / "xdg" / "SudokuMaster"
    with monkeypatch.context() as scoped:
        scoped.setenv("SUDOKU_DATA_DIR", os.fspath(tmp_path / "blocked"))
        scoped.setattr(
            persistence.Path,
            "mkdir",
            lambda *_args, **_kwargs: (_ for _ in ()).throw(OSError("read only")),
        )
        with pytest.raises(OSError, match="read only"):
            persistence.get_data_dir()

    board, solution = logic.generate_sudoku("custom", seed=2, empty_cells=99)
    assert sum(cell == 0 for row in board for cell in row) <= 60
    with pytest.raises(ValueError):
        logic.string_to_board("too short")
    with pytest.raises(ValueError, match="Invalid character"):
        logic.string_to_board("0" * 80 + "x")
    with pytest.raises(ValueError, match="board and solution strings"):
        logic.import_puzzle("{}")
    with pytest.raises(ValueError, match="clues do not match"):
        logic.import_puzzle(logic.export_puzzle([[1] * 9 for _ in range(9)], solution))
    with monkeypatch.context() as scoped:
        scoped.setattr(logic.DLX, "count_solutions", lambda *_args, **_kwargs: 0)
        assert not logic.solve_board_dlx([[0] * 9 for _ in range(9)])
    with monkeypatch.context() as scoped:
        scoped.setattr(logic, "count_solutions_dlx", lambda *_args, **_kwargs: 1)
        scoped.setattr(logic, "solve_board_dlx", lambda _board: False)
        with pytest.raises(ValueError, match="no valid solution"):
            logic.import_puzzle("0" * 81)

    assert geometry.get_timer_rect().width > 0
    assert sidebar_module._format_clock(None) == "--:--"
    assert sidebar_module._format_clock(-3) == "00:00"
    manager = object.__new__(colors.ThemeManager)
    manager._theme = "unknown"
    assert manager.theme_icon == "L"
    pygame.init()
    monkeypatch.setattr(fonts_module.pygame.font, "match_font", lambda *args, **kwargs: None)
    assert fonts_module.load_fonts().cell is not None

    runtime_file = persistence._runtime_file
    monkeypatch.setattr(persistence, "_runtime_file", lambda filename: str(tmp_path / filename))
    monkeypatch.setattr(persistence, "LEGACY_DATA_DIR", tmp_path / "legacy")
    persistence.LEGACY_DATA_DIR.mkdir()
    (persistence.LEGACY_DATA_DIR / "migration.json").write_text("old", encoding="utf-8")
    with monkeypatch.context() as scoped:
        scoped.setattr(persistence, "_runtime_file", runtime_file)
        scoped.setattr(persistence, "get_data_dir", lambda: tmp_path)
        scoped.setattr(
            persistence.shutil, "copy2", lambda *_: (_ for _ in ()).throw(OSError("locked"))
        )
        persistence._runtime_file("migration.json")
    assert (tmp_path / ".migration.json.migrated").exists() is False

    path = tmp_path / "save_game.json"
    state = GameState("easy")
    persistence.save_game_state(state)
    saved = json.loads(path.read_text(encoding="utf-8"))
    row, col = next((r, c) for r in range(9) for c in range(9) if saved["original"][r][c])
    saved["board"][row][col] = saved["solution"][row][col] % 9 + 1
    path.write_text(json.dumps(saved), encoding="utf-8")
    assert persistence.load_game_state() is None
    path.write_text("[]", encoding="utf-8")
    assert persistence.load_game_state() is None
    persistence.save_game_state(state)
    saved = json.loads(path.read_text(encoding="utf-8"))
    saved["solution"] = [[1] * 9 for _ in range(9)]
    path.write_text(json.dumps(saved), encoding="utf-8")
    assert persistence.load_game_state() is None
    persistence.save_game_state(state)
    saved = json.loads(path.read_text(encoding="utf-8"))
    saved["undo_stack"] = []
    path.write_text(json.dumps(saved), encoding="utf-8")
    assert persistence.load_game_state().undo_stack

    today = datetime.now(timezone.utc).date()
    monkeypatch.setattr(
        persistence,
        "datetime",
        type(
            "Clock",
            (),
            {
                "now": staticmethod(
                    lambda _tz: datetime.combine(today, datetime.min.time(), timezone.utc)
                )
            },
        ),
    )
    daily: dict[str, object] = {
        "last_completed_date": None,
        "streak": 0,
        "total_completed": 0,
        "best_streak": 0,
    }
    monkeypatch.setattr(persistence, "load_daily_stats", lambda: daily.copy())
    monkeypatch.setattr(persistence, "save_daily_stats", lambda stats: daily.update(stats))
    assert persistence.mark_daily_challenge_completed()["streak"] == 1
    assert persistence.mark_daily_challenge_completed()["total_completed"] == 1
    daily.update(
        {
            "last_completed_date": (today - timedelta(days=1)).isoformat(),
            "streak": 4,
            "total_completed": 1,
            "best_streak": 4,
        }
    )
    assert persistence.mark_daily_challenge_completed()["streak"] == 5
    daily.update(
        {
            "last_completed_date": (today - timedelta(days=2)).isoformat(),
            "streak": 4,
            "total_completed": 1,
            "best_streak": 4,
        }
    )
    assert persistence.mark_daily_challenge_completed()["streak"] == 1

    with pytest.raises(ValueError, match="Unsupported"):
        persistence.increment_stat("bad")
    with monkeypatch.context() as scoped:
        scoped.setattr(persistence, "load_stats", lambda: (_ for _ in ()).throw(OSError("locked")))
        assert persistence.get_preference("x", 7) == 7
        assert not persistence.set_preference("x", 7)
    persistence.save_leaderboard({key: [] for key in persistence.DIFFICULTIES})
    assert persistence.get_leaderboard("invalid") == []
    for value in range(10):
        persistence.add_leaderboard_entry("easy", str(value), value)
    assert not persistence.is_top_10_time("easy", 100)
    assert persistence.is_top_10_time("easy", 0)
    with monkeypatch.context() as scoped:
        scoped.setattr(
            persistence.os, "remove", lambda *_: (_ for _ in ()).throw(OSError("locked"))
        )
        persistence.clear_save_file()
    (tmp_path / "leaderboard.json").write_text(json.dumps({"easy": ["bad"]}), encoding="utf-8")
    assert persistence.load_leaderboard()["easy"] == []

    saved_handlers = error_handling.logger.handlers[:]
    for handler in saved_handlers:
        error_handling.logger.removeHandler(handler)
    with monkeypatch.context() as scoped:
        scoped.setattr(
            persistence, "get_data_dir", lambda: (_ for _ in ()).throw(OSError("read only"))
        )
        importlib.reload(error_handling)
    importlib.reload(error_handling)
    error_handling.logger.handlers[:] = saved_handlers

    calls = []
    monkeypatch.setattr(
        game_module,
        "AppController",
        lambda: type("App", (), {"run": lambda self: calls.append(True)})(),
    )
    menu_module.tao_nut_bat_dau()
    assert calls == [True]

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    fonts = load_fonts()
    full_state = GameState("easy")
    full_state.board = copy.deepcopy(full_state.solution)
    full_state.notes[0][0].add(5)
    sidebar_module.draw_sidebar(screen, fonts, (0, 0), lambda key: key, full_state)
    wrong_state = GameState("easy")
    wrong_cell = next((r, c) for r in range(9) for c in range(9) if wrong_state.original[r][c] == 0)
    wrong_state.board[wrong_cell[0]][wrong_cell[1]] = wrong_state.solution[wrong_cell[0]][
        wrong_cell[1]
    ]
    wrong_state.solution[wrong_cell[0]][wrong_cell[1]] = (
        wrong_state.board[wrong_cell[0]][wrong_cell[1]] % 9
    ) + 1
    wrong_state.show_errors = True
    board_ui.draw_board(screen, fonts, wrong_state)
    invalid_state = GameState("easy")
    invalid_cell = next(
        (r, c) for r in range(9) for c in range(9) if invalid_state.original[r][c] == 0
    )
    invalid_state.board[invalid_cell[0]][invalid_cell[1]] = next(
        invalid_state.original[invalid_cell[0]][peer]
        for peer in range(9)
        if invalid_state.original[invalid_cell[0]][peer]
    )
    board_ui.draw_board(screen, fonts, invalid_state)
    note_state = GameState("easy")
    note_cell = next((r, c) for r in range(9) for c in range(9) if note_state.original[r][c] == 0)
    note_state.notes[note_cell[0]][note_cell[1]].add(5)
    sidebar_module.draw_sidebar(screen, fonts, (0, 0), lambda key: key, note_state)
    full_state.paused = True
    draw_game_view(screen, fonts, full_state, (0, 0))
    full_state.paused = False
    full_state.game_over = True
    draw_game_view(screen, fonts, full_state, (0, 0))


def test_platform_screen_paths_and_packaged_smoke(monkeypatch, tmp_path):
    import logging
    import types

    import sudoku.main as main_module
    import sudoku.ui as ui_module
    import sudoku.ui.menu as menu_module
    import sudoku.ui.modals as modals_module
    import sudoku.ui.screen as screen_module

    pygame.init()
    screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    fonts = load_fonts()
    enable_high_dpi = screen_module.enable_high_dpi
    monkeypatch.setattr(screen_module, "enable_high_dpi", lambda: None)
    monkeypatch.setattr(pygame.display, "get_desktop_sizes", lambda: [(640, 480)])
    monkeypatch.setattr(pygame.display, "set_mode", lambda *_args, **_kwargs: screen)
    monkeypatch.setattr(pygame.display, "set_caption", lambda *_: None)
    monkeypatch.setattr(pygame.display, "set_icon", lambda *_: None)
    monkeypatch.setattr(pygame.image, "load", lambda *_: screen)
    monkeypatch.setattr(screen_module.os.path, "exists", lambda _path: True)
    monkeypatch.delenv("SDL_VIDEODRIVER", raising=False)
    screen_module.create_game_screen()

    old_meipass = getattr(sys, "_MEIPASS", None)
    monkeypatch.delattr(sys, "_MEIPASS", raising=False)
    assert screen_module.get_sudoku_icon_path().endswith("SUDOKU.ico")
    if old_meipass is not None:
        monkeypatch.setattr(sys, "_MEIPASS", old_meipass, raising=False)

    monkeypatch.setattr(screen_module, "enable_high_dpi", enable_high_dpi)
    monkeypatch.setattr(sys, "platform", "linux")
    screen_module.enable_high_dpi()
    monkeypatch.setattr(sys, "platform", "win32")
    fake_user32 = types.SimpleNamespace(
        SetProcessDpiAwarenessContext=lambda *_: (_ for _ in ()).throw(OSError("unsupported")),
        SetProcessDPIAware=lambda: (_ for _ in ()).throw(OSError("unsupported")),
    )
    fake_shcore = types.SimpleNamespace(
        SetProcessDpiAwareness=lambda *_: (_ for _ in ()).throw(OSError("unsupported"))
    )
    monkeypatch.setattr(
        screen_module.ctypes,
        "windll",
        types.SimpleNamespace(user32=fake_user32, shcore=fake_shcore),
        raising=False,
    )
    screen_module.enable_high_dpi()

    video_module = types.ModuleType("pygame._sdl2.video")
    video_module.__dict__["Window"] = type(
        "Window",
        (),
        {
            "from_display_module": staticmethod(
                lambda: (_ for _ in ()).throw(RuntimeError("no window"))
            )
        },
    )
    monkeypatch.setitem(sys.modules, "pygame._sdl2.video", video_module)
    monkeypatch.setattr(
        pygame.image, "load", lambda *_: (_ for _ in ()).throw(pygame.error("bad icon"))
    )
    screen_module.create_game_screen()

    monkeypatch.setattr(
        main_module,
        "TemporaryDirectory",
        lambda: type(
            "Temp",
            (),
            {"__enter__": lambda self: os.fspath(tmp_path), "__exit__": lambda *args: None},
        )(),
    )
    monkeypatch.setattr(ui_module, "create_game_screen", lambda: screen)
    monkeypatch.setattr(ui_module, "load_fonts", lambda: fonts)
    monkeypatch.setattr(ui_module, "draw_game_view", lambda *args: None)
    monkeypatch.setattr(menu_module, "draw_menu_view", lambda *args: None)
    monkeypatch.setattr(modals_module, "draw_help_modal", lambda *args: None)
    monkeypatch.setattr(game_module, "GameState", lambda *_args: object())
    monkeypatch.setattr(pygame, "quit", lambda: None)
    monkeypatch.setattr(logging, "shutdown", lambda: None)
    main_module._run_smoke_test()


def test_game_renderer_fireworks_and_event_substates(monkeypatch):

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    session = Game("easy", screen=screen)
    session.state.selected = next(
        [r, c] for r in range(9) for c in range(9) if session.state.original[r][c] == 0
    )
    fixed = next((r, c) for r in range(9) for c in range(9) if session.state.original[r][c])
    session.state.selected = list(fixed)
    session.state.place_number(9)
    session.state.clear_cell()

    monkeypatch.setattr(
        game_module,
        "draw_game_view",
        lambda *_args, **_kwargs: {
            "pause_resume": None,
            "pause_quit": None,
            "win_restart": None,
            "win_quit": None,
        },
    )
    monkeypatch.setattr(
        game_module, "draw_help_modal", lambda *_args: {"help_close": pygame.Rect(0, 0, 1, 1)}
    )
    monkeypatch.setattr(
        game_module,
        "draw_text_input_modal",
        lambda *_args: {"text_ok": pygame.Rect(0, 0, 2, 2), "text_cancel": pygame.Rect(0, 0, 2, 2)},
    )
    session.show_help = True
    session._open_text_input("import", "title", "prompt")
    session.render()
    assert session.help_rects is not None and session.text_ok_rect is not None

    session._handle_text_input_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(0, 0)))
    assert session.text_input is None
    session._handle_text_input_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
    session._submit_text_input()

    session.state.paused = True
    monkeypatch.setattr(
        pygame.event, "get", lambda: [pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(0, 0))]
    )
    session.handle_events()
    session.state.game_over = True
    monkeypatch.setattr(
        pygame.event, "get", lambda: [pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(0, 0))]
    )
    session.handle_events()
    session._handle_keyboard(
        pygame.event.Event(
            pygame.KEYDOWN, key=pygame.K_z, mod=pygame.KMOD_CTRL | pygame.KMOD_SHIFT, unicode=""
        )
    )
    session._spawn_win_fireworks()
    assert len(session.particles) == 170
    session.particles.clear()
    session.show_help = True
    session.state.game_over = False
    session.state.paused = False
    monkeypatch.setattr(
        pygame.event,
        "get",
        lambda: [
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(0, 0)),
            pygame.event.Event(pygame.USEREVENT),
        ],
    )
    session.handle_events()
    layout: dict[str, pygame.Rect | list[pygame.Rect]] = {
        key: pygame.Rect(200, 200, 10, 10)
        for key in (
            "quick_undo",
            "quick_redo",
            "quick_notes",
            "quick_hint",
            "quick_check_errors",
            "clear",
            "auto_notes",
            "new_game",
            "menu",
            "export",
            "import",
        )
    }
    layout["numbers"] = []
    layout["menu"] = pygame.Rect(0, 0, 20, 20)
    monkeypatch.setattr(game_module, "get_sidebar_layout", lambda: layout)
    monkeypatch.setattr(session.state, "force_save", lambda: False)
    session.state.paused = False
    session.state.game_over = False
    session._handle_mouse((1, 1))

    session.text_input = None
    session._handle_text_input_event(
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_a, unicode="a")
    )
    session._submit_text_input()

    class Expired:
        lifetime = 0

        def update(self):
            pass

    session.particles = [Expired()]
    session.show_help = False
    session.state.game_over = True
    monkeypatch.setattr(game_module.random, "random", lambda: 0)
    monkeypatch.setattr(game_module.random, "randint", lambda low, _high: low)
    session.update()
    assert len(session.particles) == 26
    session.state.game_over = False


def test_app_controller_all_run_states_and_menu_exit_paths(monkeypatch):

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    monkeypatch.setattr(game_module, "create_game_screen", lambda: screen)
    controller = game_module.AppController()
    monkeypatch.setattr(pygame.display, "flip", lambda: None)
    controller.clock = type("Clock", (), {"tick": lambda self, *_: None})()
    monkeypatch.setattr(pygame.mouse, "get_pos", lambda: (0, 0))

    focus_seen = []
    controller._menu_rects = {"help": pygame.Rect(10, 10, 20, 20)}
    controller.menu_focus_key = "help"

    def draw_focused_menu(_screen, _fonts, pos, **_kwargs):
        focus_seen.append(pos)
        return {}

    monkeypatch.setattr(game_module, "draw_menu_view", draw_focused_menu)
    monkeypatch.setattr(pygame.event, "get", lambda: [pygame.event.Event(pygame.QUIT)])
    controller.run()
    assert focus_seen == [(20, 20)]
    controller.menu_focus_key = None
    monkeypatch.setattr(
        pygame.event,
        "get",
        lambda: [
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN, mod=0),
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_a, mod=0),
            pygame.event.Event(pygame.USEREVENT),
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(-5, -5)),
        ],
    )
    controller._handle_menu_events({})

    for app_state, draw_fn in (
        (controller.STATE_LEADERBOARD, "draw_leaderboard_modal"),
        (controller.STATE_HELP, "draw_help_modal"),
    ):
        controller.running = True
        controller.state = app_state
        monkeypatch.setattr(game_module, draw_fn, lambda *_args, **_kwargs: {})
        monkeypatch.setattr(pygame.event, "get", lambda: [pygame.event.Event(pygame.QUIT)])
        controller.run()

    controller.running = True
    controller.state = controller.STATE_PLAYING
    controller.game_session = None
    calls = []

    def draw_menu(_screen, _fonts, _mouse_pos, **_kwargs):
        calls.append("menu")
        return {}

    monkeypatch.setattr(game_module, "draw_menu_view", draw_menu)
    monkeypatch.setattr(
        controller, "_handle_menu_events", lambda _rects: setattr(controller, "running", False)
    )
    controller.run()
    assert calls == ["menu"]

    controller.running = True
    controller.state = controller.STATE_MENU
    monkeypatch.setattr(pygame.event, "get", lambda: [pygame.event.Event(pygame.QUIT)])
    controller._handle_help_events({})
    controller._handle_leaderboard_events({})
    monkeypatch.setattr(
        pygame.event, "get", lambda: [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_a)]
    )
    controller._handle_leaderboard_events({})

    pygame.init()
    custom_state = GameState("custom")
    controller._start_game("custom", loaded_state=custom_state)
    assert controller.custom_cells == custom_state.custom_empty_cells
    monkeypatch.setattr(game_module, "GameState", lambda *_args, **_kwargs: custom_state)
    monkeypatch.setattr(game_module, "Game", lambda *_args, **_kwargs: custom_state)
    controller._start_game("custom", custom_cells=44)
    controller.running = True
    controller.state = controller.STATE_PLAYING
    controller.game_session = object()
    monkeypatch.setattr(
        controller, "_run_game_session", lambda: setattr(controller, "running", False)
    )
    controller.run()
    monkeypatch.setattr(game_module, "GameState", lambda *_args, **_kwargs: custom_state)
    monkeypatch.setattr(game_module, "Game", lambda *_args, **_kwargs: custom_state)
    controller._start_game("custom", custom_cells=44)
    controller.game_session = type(
        "Session", (), {"running": True, "handle_events": lambda self: False}
    )()
    game_module.AppController._run_game_session(controller)
    sounds._sound_manager = None


def test_sidebar_uses_cached_stats_without_disk_reads(monkeypatch):
    import sudoku.ui.sidebar as sidebar_ui

    def unexpected_disk_read():
        raise AssertionError("sidebar should use the game stats snapshot")

    monkeypatch.setattr(sidebar_ui, "load_best_times", unexpected_disk_read)
    monkeypatch.setattr(sidebar_ui, "load_daily_stats", unexpected_disk_read)
    pygame.init()
    state = GameState("easy")
    screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

    sidebar_ui.draw_sidebar(
        screen, load_fonts(), (0, 0), lambda key: key, state, ({}, {"streak": 2})
    )
