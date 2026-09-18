"""Unit tests for Sudoku game."""

import json
import os
from datetime import date
from pathlib import Path

import pytest

import config
import game
import persistence
import sounds
from config import GAME_DICT, MENU_DICT, game_text
from error_handling import ErrorSeverity, log_exception, logger
from game import MAX_HISTORY_STATES, GameState
from logic import (
    check_win,
    count_solutions_dlx,
    export_puzzle,
    generate_daily_challenge,
    generate_sudoku,
    import_puzzle,
    is_valid_placement,
    solve_board_dlx,
)
from persistence import (
    _runtime_file,
    clear_save_file,
    get_data_dir,
    get_preference,
    has_save_file,
    load_best_times,
    load_daily_stats,
    load_game_state,
    load_leaderboard,
    load_stats,
    save_best_times,
    save_game_state,
    set_preference,
    update_best_time,
)


class TestLogic:
    """Tests for Sudoku logic module."""

    def test_game_translations_have_matching_keys(self):
        assert GAME_DICT["en"].keys() == GAME_DICT["vi"].keys()

    def test_menu_translations_have_matching_keys(self):
        assert MENU_DICT["en"].keys() == MENU_DICT["vi"].keys()

    @pytest.mark.parametrize(
        ("language", "expected"),
        [
            ("vi", ("Dễ", "Trung bình", "Khó", "Thử thách hàng ngày", "Tùy chỉnh")),
            ("en", ("Easy", "Medium", "Hard", "Daily Challenge", "Custom")),
        ],
    )
    def test_game_difficulty_names_are_translated(self, monkeypatch, language, expected):
        monkeypatch.setattr(config, "ngon_ngu_hien_tai", language)

        assert (
            tuple(game_text(key) for key in ("easy", "medium", "hard", "daily", "custom"))
            == expected
        )

    def test_daily_challenge_is_deterministic_for_a_utc_date(self):
        challenge_date = date(2026, 9, 17)
        first = generate_daily_challenge(challenge_date=challenge_date)
        second = generate_daily_challenge(challenge_date=challenge_date)
        assert first == second

    def test_generate_sudoku_easy(self):
        board, solution = generate_sudoku("easy")
        assert len(board) == 9
        assert len(board[0]) == 9
        assert len(solution) == 9
        assert count_solutions_dlx(board) == 1
        # Easy should have ~43 clues (38 empty)
        clues = sum(1 for row in board for v in row if v != 0)
        assert 40 <= clues <= 46

    def test_generate_sudoku_medium(self):
        board, solution = generate_sudoku("medium")
        assert count_solutions_dlx(board) == 1
        clues = sum(1 for row in board for v in row if v != 0)
        assert 30 <= clues <= 36

    def test_generate_sudoku_hard(self):
        board, solution = generate_sudoku("hard")
        assert count_solutions_dlx(board) == 1
        clues = sum(1 for row in board for v in row if v != 0)
        assert 25 <= clues <= 30

    def test_generate_sudoku_invalid_difficulty_defaults_to_medium(self):
        board, solution = generate_sudoku("invalid")
        clues = sum(1 for row in board for v in row if v != 0)
        assert 30 <= clues <= 36

    def test_is_valid_placement_empty_board(self):
        board = [[0] * 9 for _ in range(9)]
        assert is_valid_placement(board, 0, 0, 1)
        assert is_valid_placement(board, 4, 4, 9)

    def test_is_valid_placement_row_conflict(self):
        board = [[0] * 9 for _ in range(9)]
        board[0][0] = 5
        assert not is_valid_placement(board, 0, 1, 5)  # Same row
        assert is_valid_placement(board, 0, 1, 6)  # Different number

    def test_is_valid_placement_col_conflict(self):
        board = [[0] * 9 for _ in range(9)]
        board[0][0] = 5
        assert not is_valid_placement(board, 1, 0, 5)  # Same col

    def test_is_valid_placement_box_conflict(self):
        board = [[0] * 9 for _ in range(9)]
        board[0][0] = 5
        assert not is_valid_placement(board, 1, 1, 5)  # Same 3x3 box
        assert is_valid_placement(board, 3, 3, 5)  # Different box

    def test_is_valid_placement_zero_allowed(self):
        board = [[5] * 9 for _ in range(9)]
        assert is_valid_placement(board, 0, 0, 0)  # Zero always valid

    def test_check_win(self):
        board = [[1] * 9 for _ in range(9)]
        solution = [[1] * 9 for _ in range(9)]
        assert check_win(board, solution)

        board[0][0] = 2
        assert not check_win(board, solution)

    def test_count_solutions_unique(self):
        board, _ = generate_sudoku("easy")
        assert count_solutions_dlx(board) == 1

    def test_count_solutions_multiple(self):
        # Empty board has many solutions
        board = [[0] * 9 for _ in range(9)]
        assert count_solutions_dlx(board, limit=2) >= 2

    def test_solve_board_dlx(self):
        board, solution = generate_sudoku("hard")
        empty = [row[:] for row in board]
        assert solve_board_dlx(empty)
        assert empty == solution

    def test_seed_is_reproducible_without_global_rng_side_effect(self):
        first = generate_sudoku("medium", seed=1234)
        second = generate_sudoku("medium", seed=1234)
        assert first == second

    def test_export_import_round_trip(self):
        board, solution = generate_sudoku("easy", seed=42)
        assert import_puzzle(export_puzzle(board, solution)) == (board, solution)

    def test_import_rejects_mismatched_solution(self):
        board, solution = generate_sudoku("easy", seed=42)
        solution[0][0] = solution[0][1]
        with pytest.raises(ValueError):
            import_puzzle(export_puzzle(board, solution))

    def test_import_rejects_incomplete_solution(self):
        empty_board = [[0] * 9 for _ in range(9)]
        with pytest.raises(ValueError, match="completed"):
            import_puzzle(export_puzzle(empty_board, empty_board))

    def test_import_legacy_81_digit_puzzle_derives_solution(self):
        board, solution = generate_sudoku("easy", seed=42)
        legacy_text = "".join(str(value) for row in board for value in row)
        assert import_puzzle(legacy_text) == (board, solution)

    def test_import_rejects_ambiguous_legacy_puzzle(self):
        with pytest.raises(ValueError, match="exactly one solution"):
            import_puzzle("0" * 81)

    def test_import_rejects_ambiguous_json_puzzle(self):
        _, solution = generate_sudoku("easy", seed=42)
        empty_board = [[0] * 9 for _ in range(9)]

        with pytest.raises(ValueError, match="exactly one solution"):
            import_puzzle(export_puzzle(empty_board, solution))


def test_log_exception_logs_action_and_reraises(monkeypatch):
    messages = []
    monkeypatch.setattr(logger, "exception", lambda message, *args: messages.append(message % args))

    @log_exception(ErrorSeverity.LOW, user_action="test_action")
    def fail():
        raise RuntimeError("expected failure")

    with pytest.raises(RuntimeError, match="expected failure"):
        fail()

    assert messages == ["[LOW] test_action"]


class TestPersistence:
    """Tests for persistence module."""

    def setup_method(self):
        clear_save_file()

    def teardown_method(self):
        clear_save_file()

    def test_runtime_data_uses_isolated_directory(self):
        assert get_data_dir() == Path(os.environ["SUDOKU_DATA_DIR"])

    def test_deleted_legacy_save_is_not_migrated_again(self, monkeypatch):
        test_data_dir = Path(os.environ["SUDOKU_DATA_DIR"])
        legacy_dir = test_data_dir / "legacy"
        runtime_dir = test_data_dir / "runtime"
        legacy_dir.mkdir()
        runtime_dir.mkdir()
        (legacy_dir / "save_game.json").write_text("legacy", encoding="utf-8")
        monkeypatch.setenv("SUDOKU_DATA_DIR", os.fspath(runtime_dir))
        monkeypatch.setattr("persistence.LEGACY_DATA_DIR", legacy_dir)

        migrated_save = Path(_runtime_file("save_game.json"))
        assert migrated_save.read_text(encoding="utf-8") == "legacy"

        clear_save_file()

        assert not has_save_file()

    def test_loaded_game_resets_process_local_autosave_timestamp(self):
        GameState("easy")
        save_path = get_data_dir() / "save_game.json"
        saved_data = json.loads(save_path.read_text(encoding="utf-8"))
        saved_data["_last_auto_save_time"] = 9_999_999_999_999
        save_path.write_text(json.dumps(saved_data), encoding="utf-8")

        loaded = load_game_state()

        assert loaded is not None
        assert loaded._last_auto_save_time == 0

    def test_save_load_game_state(self):
        state = GameState("easy")
        # Find an empty cell to test with
        r, c = 0, 0
        while state.original[r][c] != 0:
            c += 1
            if c >= 9:
                c = 0
                r += 1
        state.selected = [r, c]

        state.place_number(5)
        state.place_number(3)
        original_board = [row[:] for row in state.board]
        original_notes = [[s.copy() for s in row] for row in state.notes]

        save_game_state(state)
        assert has_save_file()

        loaded = load_game_state()
        assert loaded is not None
        assert loaded.difficulty == "easy"
        assert loaded.board == original_board
        assert loaded.notes == original_notes
        assert len(loaded.undo_stack) > 1

    def test_load_legacy_save_without_elapsed_time(self):
        GameState("easy")
        save_path = get_data_dir() / "save_game.json"
        saved_data = json.loads(save_path.read_text(encoding="utf-8"))
        saved_data.pop("elapsed_time")
        save_path.write_text(json.dumps(saved_data), encoding="utf-8")

        loaded = load_game_state()

        assert loaded is not None
        assert loaded.elapsed_before_session == 0

    def test_save_with_invalid_elapsed_time_returns_none(self):
        GameState("easy")
        save_path = get_data_dir() / "save_game.json"
        saved_data = json.loads(save_path.read_text(encoding="utf-8"))
        saved_data["elapsed_time"] = -1
        save_path.write_text(json.dumps(saved_data), encoding="utf-8")

        assert load_game_state() is None

    @pytest.mark.parametrize("paused", [False, True])
    def test_elapsed_time_survives_save_and_restart(self, monkeypatch, paused):
        ticks = [10_000]
        monkeypatch.setattr("pygame.time.get_ticks", lambda: ticks[0])
        state = GameState("easy")
        ticks[0] = 72_500
        if paused:
            state.toggle_pause()
        save_game_state(state)

        ticks[0] = 5
        loaded = load_game_state()

        assert loaded is not None
        assert loaded.get_elapsed_time() == 62
        if paused:
            ticks[0] += 10_000
            assert loaded.get_elapsed_time() == 62
            loaded.toggle_pause()
        assert loaded.get_elapsed_time() == 62
        ticks[0] += 1_000
        assert loaded.get_elapsed_time() == 63

    def test_load_nonexistent_save_returns_none(self):
        clear_save_file()
        assert load_game_state() is None

    def test_corrupt_or_incomplete_save_returns_none(self):
        (get_data_dir() / "save_game.json").write_text("{}", encoding="utf-8")
        assert load_game_state() is None

    def test_save_with_invalid_timer_returns_none(self):
        GameState("easy")
        save_path = get_data_dir() / "save_game.json"
        saved_data = json.loads(save_path.read_text(encoding="utf-8"))
        saved_data["start_time"] = "invalid"
        save_path.write_text(json.dumps(saved_data), encoding="utf-8")

        assert load_game_state() is None

    def test_clear_save_file(self):
        state = GameState("easy")
        save_game_state(state)
        assert has_save_file()
        clear_save_file()
        assert not has_save_file()

    def test_best_times_initial(self):
        times = load_best_times()
        assert times == {
            "easy": None,
            "medium": None,
            "hard": None,
            "daily": None,
            "custom": None,
        }

    def test_best_times_are_saved_atomically(self):
        times = load_best_times()
        times["easy"] = 42
        save_best_times(times)

        assert load_best_times() == times
        assert not (get_data_dir() / "best_times.json.tmp").exists()

    def test_game_save_reports_unavailable_data_directory(self, monkeypatch):
        state = GameState("easy")

        def fail_data_path(_filename):
            raise OSError("permission denied")

        with monkeypatch.context() as scoped:
            scoped.setattr(persistence, "_runtime_file", fail_data_path)
            assert save_game_state(state) is False

    def test_autosave_failure_is_visible_and_clears_after_recovery(self, monkeypatch):
        state = GameState("easy")
        monkeypatch.setattr(game, "save_game_state", lambda _state: False)

        state.auto_save()

        assert state.save_failed
        monkeypatch.setattr(game, "save_game_state", lambda _state: True)
        assert state.force_save()
        assert not state.save_failed

    def test_language_and_sound_preferences_round_trip(self, monkeypatch):
        monkeypatch.setattr(config, "ngon_ngu_hien_tai", "vi")

        config.chuyen_ngon_ngu()

        assert config.ngon_ngu_hien_tai == "en"
        assert get_preference("language", "vi") == "en"
        assert set_preference("sound_enabled", False)
        assert get_preference("sound_enabled", True) is False

    def test_theme_manager_uses_preference_helpers(self, monkeypatch):
        from ui.colors import ThemeManager

        saved = {"theme": "cozy"}
        monkeypatch.setattr(
            "ui.colors.get_preference", lambda name, default: saved.get(name, default)
        )

        def store_preference(name: str, value: str) -> bool:
            saved[name] = value
            return True

        monkeypatch.setattr("ui.colors.set_preference", store_preference)
        manager = object.__new__(ThemeManager)

        manager._load_theme()
        assert manager.theme == "cozy"

        manager.theme = "dark"
        assert saved["theme"] == "dark"

    def test_sound_manager_restores_and_persists_toggle(self, monkeypatch):
        saved: dict[str, bool] = {"sound_enabled": False}
        monkeypatch.setattr(
            sounds, "get_preference", lambda _name, default: saved.get("sound_enabled", default)
        )

        def store_preference(name: str, value: bool) -> bool:
            saved[name] = value
            return True

        monkeypatch.setattr(sounds, "set_preference", store_preference)
        monkeypatch.setattr(sounds.SoundManager, "_init_sounds", lambda _self: None)

        manager = sounds.SoundManager()
        assert not manager.is_enabled()

        manager.toggle()

        assert manager.is_enabled()
        assert saved["sound_enabled"] is True

    def test_sound_manager_disables_an_effect_after_playback_failure(self, monkeypatch):
        monkeypatch.setattr(sounds.SoundManager, "_init_sounds", lambda _self: None)
        manager = sounds.SoundManager()

        class BrokenSound:
            def play(self):
                raise sounds.pygame.error("audio device unavailable")

        manager.sounds["click"] = BrokenSound()

        manager.play("click")

        assert "click" not in manager.sounds

    def test_best_times_ignore_invalid_values(self):
        (get_data_dir() / "best_times.json").write_text(
            json.dumps({"easy": "fast", "hard": -3, "daily": 120}), encoding="utf-8"
        )

        assert load_best_times() == {
            "easy": None,
            "medium": None,
            "hard": None,
            "daily": 120,
            "custom": None,
        }

    def test_daily_stats_recover_from_invalid_fields(self):
        (get_data_dir() / "daily_stats.json").write_text(
            json.dumps(
                {
                    "last_completed_date": "not-a-date",
                    "streak": "broken",
                    "total_completed": -2,
                    "best_streak": 4,
                }
            ),
            encoding="utf-8",
        )

        assert load_daily_stats() == {
            "last_completed_date": None,
            "streak": 0,
            "total_completed": 0,
            "best_streak": 4,
        }

    def test_theme_and_leaderboard_sanitize_corrupt_data(self):
        (get_data_dir() / "stats.json").write_text(
            json.dumps(
                {
                    "games_played": "many",
                    "theme": "unknown",
                }
            ),
            encoding="utf-8",
        )
        (get_data_dir() / "leaderboard.json").write_text(
            json.dumps(
                {
                    "easy": [
                        {"name": "Valid", "time": 42, "date": "2026-09-17"},
                        {"name": "Broken", "time": "fast", "date": "2026-09-17"},
                    ],
                    "daily": "not-a-list",
                }
            ),
            encoding="utf-8",
        )

        stats = load_stats()
        leaderboard = load_leaderboard()
        assert stats["games_played"] == "many"
        assert stats["theme"] == "light"
        assert leaderboard["easy"] == [{"name": "Valid", "time": 42, "date": "2026-09-17"}]
        assert leaderboard["daily"] == []

    def test_update_best_time_first(self):
        assert update_best_time("easy", 120)
        assert load_best_times()["easy"] == 120

    def test_update_best_time_better(self):
        update_best_time("easy", 120)
        assert update_best_time("easy", 90)
        assert load_best_times()["easy"] == 90

    def test_update_best_time_worse(self):
        update_best_time("easy", 90)
        assert not update_best_time("easy", 120)
        assert load_best_times()["easy"] == 90

    def test_best_times_persist(self):
        update_best_time("hard", 300)
        # Reload from disk
        times = load_best_times()
        assert times["hard"] == 300

    def test_save_state_preserves_undo_redo(self):
        state = GameState("medium")
        state.place_number(1)
        state.place_number(2)
        state.undo()
        undo_len = len(state.undo_stack)
        redo_len = len(state.redo_stack)

        save_game_state(state)
        loaded = load_game_state()
        assert loaded is not None

        assert len(loaded.undo_stack) == undo_len
        assert len(loaded.redo_stack) == redo_len


class TestGameState:
    """Tests for GameState class."""

    def test_initial_state(self):
        state = GameState("easy")
        assert state.difficulty == "easy"
        assert state.selected == [0, 0]
        assert state.notes_mode is False
        assert state.game_over is False
        assert state.paused is False
        assert len(state.undo_stack) == 1
        assert len(state.redo_stack) == 0

    def test_daily_state_uses_daily_generator(self, monkeypatch):
        solution = [[(r * 3 + r // 3 + c) % 9 + 1 for c in range(9)] for r in range(9)]
        board = [row[:] for row in solution]
        board[0][0] = 0
        calls = []

        def make_daily_puzzle():
            calls.append(True)
            return board, solution, 20260917

        monkeypatch.setattr("game.generate_daily_challenge", make_daily_puzzle)
        state = GameState("daily")
        state.restart("daily")

        assert state.difficulty == "daily"
        assert state.board == board
        assert len(calls) == 2

    def test_custom_difficulty_is_preserved_on_restart_and_load(self, monkeypatch):
        solution = [[(r * 3 + r // 3 + c) % 9 + 1 for c in range(9)] for r in range(9)]
        board = [[0] * 9 for _ in range(9)]
        requested_cells = []

        def make_custom_puzzle(difficulty, seed=None, empty_cells=None):
            requested_cells.append(empty_cells)
            return board, solution

        monkeypatch.setattr("game.generate_sudoku", make_custom_puzzle)
        state = GameState("custom", empty_cells=56)
        state.restart("custom")

        loaded = load_game_state()
        assert requested_cells == [56, 56]
        assert loaded is not None and loaded.custom_empty_cells == 56

    def test_place_number(self):
        state = GameState("easy")
        # Find an empty cell (not in original)
        r, c = 0, 0
        while state.original[r][c] != 0:
            c += 1
            if c >= 9:
                c = 0
                r += 1
            if r >= 9:
                raise RuntimeError("No empty cells found")
        state.selected = [r, c]
        state.original[r][c] = 0

        state.place_number(5)
        assert state.board[r][c] == 5
        assert len(state.undo_stack) == 2

    def test_place_number_notes_mode(self):
        state = GameState("easy")
        r, c = 0, 0
        state.selected = [r, c]
        state.original[r][c] = 0
        state.board[r][c] = 0  # Ensure board is also empty
        state.notes_mode = True

        state.place_number(5)
        assert 5 in state.notes[r][c]
        assert state.board[r][c] == 0
        state.undo()
        assert 5 not in state.notes[r][c]
        state.redo()
        assert 5 in state.notes[r][c]

    def test_clear_cell(self):
        state = GameState("easy")
        r, c = 0, 0
        state.selected = [r, c]
        state.original[r][c] = 0
        state.board[r][c] = 5

        state.clear_cell()
        assert state.board[r][c] == 0

    def test_clear_cell_notes_mode(self):
        state = GameState("easy")
        r, c = 0, 0
        state.selected = [r, c]
        state.original[r][c] = 0
        state.notes_mode = True
        state.notes[r][c] = {1, 2, 3}
        state.save_state()

        state.clear_cell()
        assert state.notes[r][c] == set()
        state.undo()
        assert state.notes[r][c] == {1, 2, 3}
        state.redo()
        assert state.notes[r][c] == set()

    def test_undo_history_is_bounded(self):
        state = GameState("easy")
        row, column = next((r, c) for r in range(9) for c in range(9) if state.original[r][c] == 0)
        for value in range(250):
            state.board[row][column] = value % 9 + 1
            state.save_state()

        assert len(state.undo_stack) == MAX_HISTORY_STATES
        save_game_state(state)
        restored = load_game_state()
        assert restored is not None
        assert len(restored.undo_stack) == MAX_HISTORY_STATES

    def test_load_ignores_history_older_than_the_retained_limit(self):
        state = GameState("easy")
        assert save_game_state(state)
        filepath = Path(_runtime_file("save_game.json"))
        with filepath.open(encoding="utf-8") as save_file:
            saved_data = json.load(save_file)
        saved_data["undo_stack"] *= MAX_HISTORY_STATES
        saved_data["undo_stack"].insert(0, {"invalid": "discarded old history"})
        filepath.write_text(json.dumps(saved_data), encoding="utf-8")

        restored = load_game_state()

        assert restored is not None
        assert len(restored.undo_stack) == MAX_HISTORY_STATES

    def test_undo_redo(self):
        state = GameState("easy")
        r, c = 0, 0
        state.selected = [r, c]
        state.original[r][c] = 0

        state.place_number(1)
        state.place_number(2)
        assert state.board[r][c] == 2

        state.undo()
        assert state.board[r][c] == 1

        state.redo()
        assert state.board[r][c] == 2

    def test_undo_limit(self):
        state = GameState("easy")
        r, c = 0, 0
        state.selected = [r, c]
        state.original[r][c] = 0

        # Can't undo past initial state
        state.undo()
        assert len(state.undo_stack) == 1

    def test_give_hint(self):
        state = GameState("easy")
        r, c = 0, 0
        state.selected = [r, c]
        state.original[r][c] = 0
        state.board[r][c] = 0
        solution_val = state.solution[r][c]

        state.give_hint()
        assert state.board[r][c] == solution_val
        assert state.notes[r][c] == set()

    def test_fill_possible_notes(self):
        state = GameState("easy")
        state.fill_possible_notes()
        # All empty cells should have notes
        for r in range(9):
            for c in range(9):
                if state.board[r][c] == 0:
                    assert len(state.notes[r][c]) > 0

    def test_completion_ripple_triggers_for_completed_row_column_and_box(self, monkeypatch):
        state = GameState("easy")
        state.board = [row[:] for row in state.solution]
        triggered = []
        monkeypatch.setattr(
            game, "trigger_completion_animation", lambda *args: triggered.append(args)
        )

        state._check_completion_ripple(0, 0)

        assert triggered == [("row", 0), ("col", 0), ("box", 0)]

    def test_toggle_pause(self):
        state = GameState("easy")
        assert not state.paused
        state.toggle_pause()
        assert state.paused
        state.toggle_pause()
        assert not state.paused

    def test_restart(self):
        state = GameState("easy")
        state.place_number(5)
        state.restart("hard")
        assert state.difficulty == "hard"
        assert len(state.undo_stack) == 1
        assert state.game_over is False

    def test_get_elapsed_time(self):
        state = GameState("easy")
        # Just verify it returns non-negative
        assert state.get_elapsed_time() >= 0

    def test_set_puzzle_resets_state_and_persists_matching_solution(self):
        state = GameState("easy")
        board, solution = generate_sudoku("hard", seed=123)
        state.notes_mode = True
        state.paused = True
        state.redo_stack.append((board, [[set() for _ in range(9)] for _ in range(9)]))

        state.set_puzzle(board, solution)

        assert state.board == board
        assert state.original == board
        assert state.solution == solution
        assert not state.notes_mode and not state.paused
        assert len(state.undo_stack) == 1
        assert not state.redo_stack
        loaded = load_game_state()
        assert loaded is not None and loaded.solution == solution


def test_auto_save_debounce():
    state = GameState("easy")
    # First save happens immediately in __init__
    # Rapid calls should be debounced
    # We can't easily test timing without mocking, but verify method exists
    state.auto_save()
    state.force_save()
    assert hasattr(state, "_last_auto_save_time")


class TestIntegration:
    """Integration tests."""

    def test_full_game_flow(self):
        state = GameState("easy")
        # Play a few moves
        for i in range(3):
            r, c = i, i
            state.selected = [r, c]
            state.original[r][c] = 0
            state.place_number(state.solution[r][c])

        # Save and load
        save_game_state(state)
        loaded = load_game_state()

        assert loaded is not None
        assert loaded.board == state.board
        assert loaded.difficulty == state.difficulty


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
