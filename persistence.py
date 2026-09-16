"""Persistence module: save/load game state, best times, daily challenge, statistics, leaderboard."""

import copy
import json
import logging
import math
import os
import shutil
import sys
from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, TypedDict, cast

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game import GameState

LEGACY_DATA_DIR = Path(__file__).resolve().parent


def get_data_dir() -> Path:
    """Return the per-user data directory, overridable for tests."""
    override = os.environ.get("SUDOKU_DATA_DIR")
    if override:
        data_dir = Path(override)
    elif os.name == "nt":
        data_dir = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / "SudokuMaster"
    elif sys.platform == "darwin":
        data_dir = Path.home() / "Library" / "Application Support" / "SudokuMaster"
    else:
        data_dir = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")) / "SudokuMaster"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def _runtime_file(filename: str) -> str:
    """Return a runtime file path and migrate an old project-local file once."""
    target = get_data_dir() / filename
    legacy = LEGACY_DATA_DIR / filename
    if not target.exists() and legacy.exists() and target != legacy:
        try:
            shutil.copy2(legacy, target)
            logger.info("Migrated runtime data from %s to %s", legacy, target)
        except OSError as exc:
            logger.warning("Could not migrate %s: %s", legacy, exc)
    return str(target)


# Type definitions
Difficulty = Literal["easy", "medium", "hard", "daily", "custom"]
DIFFICULTIES: tuple[Difficulty, ...] = ("easy", "medium", "hard", "daily", "custom")
ThemeMode = Literal["light", "dark", "frost", "cozy"]


class LeaderboardEntry(TypedDict):
    name: str
    time: int
    date: str


class LeaderboardData(TypedDict):
    easy: list[LeaderboardEntry]
    medium: list[LeaderboardEntry]
    hard: list[LeaderboardEntry]
    daily: list[LeaderboardEntry]
    custom: list[LeaderboardEntry]


class DailyStats(TypedDict):
    last_completed_date: str | None
    streak: int
    total_completed: int
    best_streak: int


class GameStats(TypedDict):
    games_played: int
    games_won: int
    total_time: int
    best_times: dict[Difficulty, int | None]
    by_difficulty: dict[Difficulty, dict[str, int]]
    current_streak: int
    best_streak: int
    last_win_date: str | None
    theme: ThemeMode
    win_rate: float
    avg_time: float


class SaveGameState(TypedDict):
    difficulty: str
    board: list[list[int]]
    solution: list[list[int]]
    original: list[list[int]]
    selected: list[int]
    notes: list[list[list[int]]]
    notes_mode: bool
    game_over: bool
    paused: bool
    show_errors: bool
    start_time: int
    paused_time: int
    last_pause_start: int
    last_active_time: int
    final_time: int
    undo_stack: list[dict[str, list]]
    redo_stack: list[dict[str, list]]


def _load_json(filepath: str, default: dict[str, Any]) -> dict[str, Any]:
    if os.path.exists(filepath):
        try:
            with open(filepath, encoding="utf-8") as f:
                value = json.load(f)
                return value if isinstance(value, dict) else default
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning("Could not load %s: %s", filepath, exc)
    return default


def _save_json(filepath: str, data: dict[str, Any]) -> None:
    temp_path = f"{filepath}.tmp"
    try:
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(temp_path, filepath)
    except OSError as exc:
        logger.warning("Could not save %s: %s", filepath, exc)
        try:
            os.remove(temp_path)
        except OSError:
            pass


def _is_board(value: Any, *, complete: bool = False) -> bool:
    return (
        isinstance(value, list)
        and len(value) == 9
        and all(
            isinstance(row, list)
            and len(row) == 9
            and all(type(cell) is int and (1 <= cell <= 9 if complete else 0 <= cell <= 9) for cell in row)
            for row in value
        )
    )


def _is_notes(value: Any) -> bool:
    return (
        isinstance(value, list)
        and len(value) == 9
        and all(
            isinstance(row, list)
            and len(row) == 9
            and all(
                isinstance(cell, list)
                and all(type(note) is int and 1 <= note <= 9 for note in cell)
                for cell in row
            )
            for row in value
        )
    )


def load_best_times() -> dict[Difficulty, int | None]:
    filepath = _runtime_file("best_times.json")
    if os.path.exists(filepath):
        try:
            with open(filepath, encoding="utf-8") as f:
                return cast(dict[Difficulty, int | None], json.load(f))
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning("Could not load %s: %s", filepath, exc)
    return {"easy": None, "medium": None, "hard": None}


def save_best_times(times: dict[Difficulty, int | None]) -> None:
    filepath = _runtime_file("best_times.json")
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(times, f, ensure_ascii=False, indent=2)
    except OSError as exc:
        logger.warning("Could not save %s: %s", filepath, exc)


def update_best_time(difficulty: Difficulty, elapsed: int) -> bool:
    times = load_best_times()
    current = times.get(difficulty)
    if current is None or elapsed < current:
        times[difficulty] = elapsed
        save_best_times(times)
        return True
    return False


def get_best_time(difficulty: Difficulty) -> int | None:
    return load_best_times().get(difficulty)


def save_game_state(state: "GameState") -> None:
    filepath = _runtime_file("save_game.json")
    data = {
        "difficulty": state.difficulty,
        "board": state.board,
        "solution": state.solution,
        "original": state.original,
        "selected": state.selected,
        "notes": [[list(s) for s in row] for row in state.notes],
        "notes_mode": state.notes_mode,
        "game_over": state.game_over,
        "paused": state.paused,
        "show_errors": state.show_errors,
        "start_time": state.start_time,
        "paused_time": state.paused_time,
        "last_pause_start": state.last_pause_start,
        "last_active_time": state.last_active_time,
        "final_time": state.final_time,
        "_last_auto_save_time": state._last_auto_save_time,
        "undo_stack": [
            {
                "board": [list(row) for row in board],
                "notes": [[list(s) for s in row] for row in notes],
            }
            for board, notes in state.undo_stack
        ],
        "redo_stack": [
            {
                "board": [list(row) for row in board],
                "notes": [[list(s) for s in row] for row in notes],
            }
            for board, notes in state.redo_stack
        ],
    }
    _save_json(filepath, data)


def load_game_state() -> "GameState | None":
    filepath = _runtime_file("save_game.json")
    if not os.path.exists(filepath):
        return None
    try:
        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)
        from logic import count_solutions_dlx

        if not isinstance(data, dict):
            raise ValueError("Save data must be an object")
        difficulty = data["difficulty"]
        board, solution, original = data["board"], data["solution"], data["original"]
        selected, notes = data["selected"], data["notes"]
        if difficulty not in ("easy", "medium", "hard", "daily", "custom"):
            raise ValueError("Unknown difficulty")
        if not all(_is_board(item) for item in (board, original)) or not _is_board(solution, complete=True):
            raise ValueError("Invalid saved board")
        if count_solutions_dlx(solution, limit=1) != 1 or any(
            original[r][c] and original[r][c] != solution[r][c]
            for r in range(9)
            for c in range(9)
        ):
            raise ValueError("Invalid saved solution")
        if any(
            original[r][c] and board[r][c] != original[r][c]
            for r in range(9)
            for c in range(9)
        ):
            raise ValueError("Saved board changed an original clue")
        if not (
            isinstance(selected, list)
            and len(selected) == 2
            and all(type(index) is int and 0 <= index < 9 for index in selected)
            and _is_notes(notes)
        ):
            raise ValueError("Invalid saved selection or notes")
        if any(type(data.get(key)) is not bool for key in ("notes_mode", "game_over", "paused", "show_errors")):
            raise ValueError("Invalid saved game flags")
        timer_fields = ("start_time", "paused_time", "last_pause_start", "last_active_time", "final_time")
        if any(type(data.get(key)) is not int or data[key] < 0 for key in timer_fields):
            raise ValueError("Invalid saved game timer")
        autosave_time = data.get("_last_auto_save_time", 0.0)
        if (
            type(autosave_time) not in (int, float)
            or not math.isfinite(autosave_time)
            or autosave_time < 0
        ):
            raise ValueError("Invalid saved autosave timer")

        # Import GameState locally to avoid circular import.
        from game import GameState

        state = GameState.__new__(GameState)
        state.difficulty = difficulty
        state.board = board
        state.solution = solution
        state.original = original
        state.selected = selected
        state.notes = [[set(cell) for cell in row] for row in notes]
        state.notes_mode = data["notes_mode"]
        state.game_over = data["game_over"]
        state.paused = data["paused"]
        state.show_errors = data["show_errors"]
        state.start_time = data["start_time"]
        state.paused_time = data["paused_time"]
        state.last_pause_start = data["last_pause_start"]
        state.last_active_time = data["last_active_time"]
        state.final_time = data["final_time"]
        state._last_auto_save_time = data.get("_last_auto_save_time", 0.0)

        def restore_history(items: Any) -> list[tuple[list[list[int]], list[list[set[int]]]]]:
            if not isinstance(items, list):
                raise ValueError("Invalid undo history")
            restored = []
            for item in items:
                if (
                    not isinstance(item, dict)
                    or not _is_board(item.get("board"))
                    or not _is_notes(item.get("notes"))
                ):
                    raise ValueError("Invalid undo history entry")
                restored.append(
                    (item["board"], [[set(cell) for cell in row] for row in item["notes"]])
                )
            return restored

        state.undo_stack = restore_history(data.get("undo_stack", []))
        state.redo_stack = restore_history(data.get("redo_stack", []))
        if not state.undo_stack:
            state.undo_stack = [(copy.deepcopy(board), copy.deepcopy(state.notes))]
        return state
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError, IndexError) as exc:
        logger.warning("Could not load saved game: %s", exc)
        return None


def clear_save_file() -> None:
    filepath = _runtime_file("save_game.json")
    try:
        os.remove(filepath)
    except FileNotFoundError:
        return
    except OSError as exc:
        logger.warning("Could not remove save file: %s", exc)


def has_save_file() -> bool:
    return os.path.exists(_runtime_file("save_game.json"))


# =============================================================================
# Daily Challenge Stats
# =============================================================================


def load_daily_stats() -> DailyStats:
    filepath = _runtime_file("daily_stats.json")
    return cast(DailyStats, _load_json(
        filepath,
        {
            "last_completed_date": None,
            "streak": 0,
            "total_completed": 0,
            "best_streak": 0,
        },
    ))


def save_daily_stats(stats: DailyStats) -> None:
    _save_json(_runtime_file("daily_stats.json"), cast(dict[str, Any], stats))


def mark_daily_challenge_completed(elapsed: int, difficulty: Difficulty) -> DailyStats:
    """Mark today's daily challenge as completed. Returns updated stats."""
    today = date.today().isoformat()
    stats = load_daily_stats()

    if stats["last_completed_date"] == today:
        # Already completed today
        return stats

    # Update streak
    last_date = stats["last_completed_date"]
    if last_date:
        last = date.fromisoformat(last_date)
        # Simple streak logic: if last completed was yesterday, increment
        # For simplicity, we just check if it's a new day
        if (date.today() - last).days == 1:
            stats["streak"] += 1
        else:
            stats["streak"] = 1
    else:
        stats["streak"] = 1

    stats["last_completed_date"] = today
    stats["total_completed"] += 1
    stats["best_streak"] = max(stats["best_streak"], stats["streak"])

    save_daily_stats(stats)
    return stats


def get_daily_stats() -> DailyStats:
    return load_daily_stats()


# =============================================================================
# General Statistics
# =============================================================================


def load_stats() -> GameStats:
    filepath = _runtime_file("stats.json")
    defaults: dict[str, Any] = {
        "games_played": 0,
        "games_won": 0,
        "total_time": 0,
        "best_times": dict.fromkeys(DIFFICULTIES),
        "by_difficulty": {
            difficulty: {"played": 0, "won": 0, "total_time": 0}
            for difficulty in DIFFICULTIES
        },
        "current_streak": 0,
        "best_streak": 0,
        "last_win_date": None,
        "theme": "light",
    }
    stored = _load_json(filepath, {})
    stats = {**defaults, **stored}
    stored_best = stored.get("best_times")
    stats["best_times"] = {
        **defaults["best_times"],
        **(stored_best if isinstance(stored_best, dict) else {}),
    }
    stored_difficulties = stored.get("by_difficulty")
    stats["by_difficulty"] = {
        difficulty: {
            **defaults["by_difficulty"][difficulty],
            **(
                stored_difficulties.get(difficulty, {})
                if isinstance(stored_difficulties, dict)
                and isinstance(stored_difficulties.get(difficulty), dict)
                else {}
            ),
        }
        for difficulty in DIFFICULTIES
    }
    return cast(GameStats, stats)


def save_stats(stats: GameStats) -> None:
    _save_json(_runtime_file("stats.json"), cast(dict[str, Any], stats))


def record_game_start(difficulty: Difficulty) -> None:
    stats = load_stats()
    stats["games_played"] += 1
    stats["by_difficulty"][difficulty]["played"] += 1
    save_stats(stats)


def record_game_win(difficulty: Difficulty, elapsed: int) -> GameStats:
    stats = load_stats()
    stats["games_won"] += 1
    stats["total_time"] += elapsed
    stats["by_difficulty"][difficulty]["won"] += 1
    stats["by_difficulty"][difficulty]["total_time"] += elapsed

    # Update best time
    current_best = stats["best_times"].get(difficulty)
    if current_best is None or elapsed < current_best:
        stats["best_times"][difficulty] = elapsed

    # Update streak
    today = date.today().isoformat()
    if stats["last_win_date"] == today:
        pass  # Already counted today
    else:
        last_win = stats["last_win_date"]
        if last_win:
            last = date.fromisoformat(last_win)
            if (date.today() - last).days == 1:
                stats["current_streak"] += 1
            else:
                stats["current_streak"] = 1
        else:
            stats["current_streak"] = 1
        stats["last_win_date"] = today
        stats["best_streak"] = max(stats["best_streak"], stats["current_streak"])

    save_stats(stats)
    return stats


def get_stats() -> GameStats:
    stats = load_stats()
    # Compute derived stats
    if stats["games_played"] > 0:
        stats["win_rate"] = stats["games_won"] / stats["games_played"] * 100
    else:
        stats["win_rate"] = 0
    if stats["games_won"] > 0:
        stats["avg_time"] = stats["total_time"] / stats["games_won"]
    else:
        stats["avg_time"] = 0
    return stats


# =============================================================================
# Leaderboard (Top 10 per difficulty)
# =============================================================================

LEADERBOARD_MAX_ENTRIES = 10


def load_leaderboard() -> LeaderboardData:
    filepath = _runtime_file("leaderboard.json")
    return cast(LeaderboardData, _load_json(
        filepath,
        {
            "easy": [],
            "medium": [],
            "hard": [],
            "daily": [],
            "custom": [],
        },
    ))


def save_leaderboard(leaderboard: LeaderboardData) -> None:
    _save_json(_runtime_file("leaderboard.json"), cast(dict[str, Any], leaderboard))


def add_leaderboard_entry(
    difficulty: Difficulty, name: str, elapsed: int, date_str: str | None = None
) -> bool:
    """Add a new entry to the leaderboard. Returns True if entry made top 10."""
    if date_str is None:
        date_str = date.today().isoformat()

    leaderboard = load_leaderboard()
    entries = leaderboard.get(difficulty, [])

    new_entry: LeaderboardEntry = {
        "name": name[:20],  # Limit name length
        "time": elapsed,
        "date": date_str,
    }

    entries.append(new_entry)
    # Sort by time ascending (best first)
    entries.sort(key=lambda x: x["time"])
    # Keep only top 10
    entries = entries[:LEADERBOARD_MAX_ENTRIES]
    leaderboard[difficulty] = entries

    save_leaderboard(leaderboard)

    # Return True if entry is in top 10
    return new_entry in entries


def get_leaderboard(
    difficulty: Difficulty | None = None,
) -> LeaderboardData | list[LeaderboardEntry]:
    """Get leaderboard for specific difficulty or all."""
    leaderboard = load_leaderboard()
    if difficulty:
        return leaderboard.get(difficulty, [])
    return leaderboard


def is_top_10_time(difficulty: Difficulty, elapsed: int) -> bool:
    """Check if a time would make the top 10 leaderboard."""
    leaderboard = load_leaderboard()
    entries = leaderboard.get(difficulty, [])
    if len(entries) < LEADERBOARD_MAX_ENTRIES:
        return True
    return elapsed < entries[-1]["time"]
