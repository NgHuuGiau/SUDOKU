"""Persistence module: save/load game state, best times, daily challenge, statistics, leaderboard."""
import json
import os
from datetime import date
from typing import TYPE_CHECKING, Literal, TypedDict

if TYPE_CHECKING:
    from game import GameState

SAVE_FILE = os.path.join(os.path.dirname(__file__), "save_game.json")
BEST_TIMES_FILE = os.path.join(os.path.dirname(__file__), "best_times.json")
DAILY_STATS_FILE = os.path.join(os.path.dirname(__file__), "daily_stats.json")
STATS_FILE = os.path.join(os.path.dirname(__file__), "stats.json")
LEADERBOARD_FILE = os.path.join(os.path.dirname(__file__), "leaderboard.json")


# Type definitions
Difficulty = Literal["easy", "medium", "hard", "daily", "custom"]
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


def _load_json(filepath: str, default: dict) -> dict:
    if os.path.exists(filepath):
        try:
            with open(filepath, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return default


def _save_json(filepath: str, data: dict) -> None:
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def load_best_times() -> dict[Difficulty, int | None]:
    if os.path.exists(BEST_TIMES_FILE):
        try:
            with open(BEST_TIMES_FILE, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"easy": None, "medium": None, "hard": None}


def save_best_times(times: dict[Difficulty, int | None]) -> None:
    try:
        with open(BEST_TIMES_FILE, "w", encoding="utf-8") as f:
            json.dump(times, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


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
                "notes": [[list(s) for s in row] for row in notes]
            }
            for board, notes in state.undo_stack
        ],
        "redo_stack": [
            {
                "board": [list(row) for row in board],
                "notes": [[list(s) for s in row] for row in notes]
            }
            for board, notes in state.redo_stack
        ],
    }
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
    except Exception:
        pass


def load_game_state() -> "GameState | None":
    if not os.path.exists(SAVE_FILE):
        return None
    try:
        with open(SAVE_FILE, encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return None

    # Import GameState locally to avoid circular import
    from game import GameState

    state = GameState.__new__(GameState)
    state.difficulty = data["difficulty"]
    state.board = data["board"]
    state.solution = data["solution"]
    state.original = data["original"]
    state.selected = data["selected"]
    state.notes = [[set(s) for s in row] for row in data["notes"]]
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
    state.undo_stack = [
        (item["board"], [[set(s) for s in row] for row in item["notes"]])
        for item in data["undo_stack"]
    ]
    state.redo_stack = [
        (item["board"], [[set(s) for s in row] for row in item["notes"]])
        for item in data["redo_stack"]
    ]
    return state


def clear_save_file() -> None:
    try:
        os.remove(SAVE_FILE)
    except Exception:
        pass


def has_save_file() -> bool:
    return os.path.exists(SAVE_FILE)


# =============================================================================
# Daily Challenge Stats
# =============================================================================

def load_daily_stats() -> DailyStats:
    return _load_json(DAILY_STATS_FILE, {
        "last_completed_date": None,
        "streak": 0,
        "total_completed": 0,
        "best_streak": 0,
    })


def save_daily_stats(stats: DailyStats) -> None:
    _save_json(DAILY_STATS_FILE, stats)


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
        date.today().replace(day=date.today().day - 1) if date.today().day > 1 else (date.today().replace(month=date.today().month - 1, day=28) if date.today().month > 1 else date(date.today().year - 1, 12, 31))
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
    return _load_json(STATS_FILE, {
        "games_played": 0,
        "games_won": 0,
        "total_time": 0,
        "best_times": {"easy": None, "medium": None, "hard": None},
        "by_difficulty": {
            "easy": {"played": 0, "won": 0, "total_time": 0},
            "medium": {"played": 0, "won": 0, "total_time": 0},
            "hard": {"played": 0, "won": 0, "total_time": 0},
        },
        "current_streak": 0,
        "best_streak": 0,
        "last_win_date": None,
        "theme": "light",
    })


def save_stats(stats: GameStats) -> None:
    _save_json(STATS_FILE, stats)


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
    return _load_json(LEADERBOARD_FILE, {
        "easy": [],
        "medium": [],
        "hard": [],
    })


def save_leaderboard(leaderboard: LeaderboardData) -> None:
    _save_json(LEADERBOARD_FILE, leaderboard)


def add_leaderboard_entry(difficulty: Difficulty, name: str, elapsed: int, date_str: str | None = None) -> bool:
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


def get_leaderboard(difficulty: Difficulty | None = None) -> LeaderboardData | list[LeaderboardEntry]:
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
