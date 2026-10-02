"""Color constants and theme system for Sudoku UI."""

from dataclasses import dataclass
from typing import Literal

from sudoku.persistence import get_preference, set_preference

ThemeMode = Literal["light", "dark", "frost", "cozy"]

THEME_ORDER: list[ThemeMode] = ["light", "dark", "frost", "cozy"]
THEME_ICONS = {
    # Keep these glyphs in the basic ASCII range so Windows font fallback
    # never renders a missing emoji as a square in the toolbar.
    "light": "L",
    "dark": "D",
    "frost": "F",
    "cozy": "C",
}


@dataclass(frozen=True)
class ThemeColors:
    """Color palette for a theme."""

    # Icon tokens (one accent per function, never hard-coded at call sites)
    ICON_UNDO: tuple
    ICON_NOTES: tuple
    ICON_HINT: tuple
    ICON_ERASE: tuple
    ICON_PAUSE: tuple
    ICON_TIMER: tuple
    ICON_MISTAKES: tuple
    ICON_STATS: tuple
    ICON_DAILY: tuple
    ICON_STREAK: tuple
    ICON_SETTINGS: tuple
    ICON_THEME: tuple
    ICON_SOUND: tuple
    ICON_LEADERBOARD: tuple
    ICON_VICTORY: tuple
    ICON_SUCCESS: tuple
    ICON_HOME: tuple

    # Background
    BG_MAIN: tuple
    BG_CARD: tuple
    BG_BOARD: tuple
    WHITE: tuple

    # Grid
    GRID_THIN: tuple
    GRID_THICK: tuple
    GRID_OUTER: tuple
    CARD_BORDER: tuple
    SHADOW: tuple

    # Text
    FIXED_TEXT: tuple
    USER_TEXT: tuple
    HINT_TEXT: tuple
    ERROR_TEXT: tuple
    NOTE_TEXT: tuple

    # Selection
    SELECTED_BG: tuple
    SELECTED_BORDER: tuple
    CROSSHAIR: tuple
    SAME_NUMBER: tuple
    ERROR_BG: tuple

    # Buttons
    BTN_PRIMARY: tuple
    BTN_PRIMARY_HOVER: tuple
    BTN_SECONDARY: tuple
    BTN_SECONDARY_HOVER: tuple
    BTN_SECONDARY_TEXT: tuple

    BTN_ACTIVE: tuple
    BTN_ACTIVE_BORDER: tuple
    BTN_ACTIVE_TEXT: tuple

    # Dark ink for bright (primary/success/warning/danger) buttons: white fails on them.
    BTN_VIVID_TEXT: tuple

    BTN_SUCCESS: tuple
    BTN_SUCCESS_HOVER: tuple
    BTN_WARNING: tuple
    BTN_WARNING_HOVER: tuple
    BTN_DANGER: tuple
    BTN_DANGER_HOVER: tuple

    # Numbers
    NUM_DONE_BG: tuple
    NUM_DONE_TEXT: tuple

    # Header
    HEADER_BG: tuple
    TIMER_TEXT: tuple
    STATUS_TEXT: tuple
    GOLD: tuple
    RIPPLE: tuple = (99, 102, 241)


# 1. Light theme (Nắng - cream + coral + sunny, flat candy style)
LIGHT_THEME = ThemeColors(
    BG_MAIN=(255, 247, 237),
    BG_CARD=(255, 255, 255),
    BG_BOARD=(255, 255, 255),
    WHITE=(255, 255, 255),
    GRID_THIN=(240, 224, 205),
    GRID_THICK=(60, 55, 75),
    GRID_OUTER=(45, 40, 60),
    CARD_BORDER=(243, 230, 212),
    SHADOW=(243, 230, 212),
    FIXED_TEXT=(58, 48, 60),
    USER_TEXT=(215, 60, 70),
    HINT_TEXT=(22, 160, 120),
    ERROR_TEXT=(230, 60, 80),
    NOTE_TEXT=(140, 104, 78),
    SELECTED_BG=(255, 226, 205),
    SELECTED_BORDER=(255, 120, 90),
    CROSSHAIR=(255, 243, 230),
    SAME_NUMBER=(255, 238, 170),
    ERROR_BG=(255, 215, 215),
    BTN_PRIMARY=(250, 100, 100),
    BTN_PRIMARY_HOVER=(235, 80, 80),
    BTN_SECONDARY=(255, 238, 224),
    BTN_SECONDARY_HOVER=(255, 226, 200),
    BTN_SECONDARY_TEXT=(90, 60, 50),
    BTN_ACTIVE=(255, 226, 205),
    BTN_ACTIVE_BORDER=(255, 112, 112),
    BTN_ACTIVE_TEXT=(190, 50, 55),
    BTN_VIVID_TEXT=(88, 20, 26),
    BTN_SUCCESS=(46, 200, 140),
    BTN_SUCCESS_HOVER=(30, 175, 120),
    BTN_WARNING=(251, 146, 60),
    BTN_WARNING_HOVER=(235, 125, 40),
    BTN_DANGER=(255, 107, 107),
    BTN_DANGER_HOVER=(235, 85, 85),
    NUM_DONE_BG=(255, 238, 224),
    NUM_DONE_TEXT=(128, 100, 82),
    HEADER_BG=(255, 252, 246),
    TIMER_TEXT=(58, 48, 60),
    STATUS_TEXT=(125, 102, 88),
    GOLD=(255, 180, 30),
    RIPPLE=(255, 112, 112),
    ICON_UNDO=(124, 93, 250),
    ICON_NOTES=(59, 130, 246),
    ICON_HINT=(190, 120, 10),
    ICON_ERASE=(240, 90, 90),
    ICON_PAUSE=(139, 92, 246),
    ICON_TIMER=(8, 145, 178),
    ICON_MISTAKES=(245, 120, 70),
    ICON_STATS=(59, 130, 246),
    ICON_DAILY=(245, 130, 40),
    ICON_STREAK=(235, 100, 60),
    ICON_SETTINGS=(100, 116, 139),
    ICON_THEME=(139, 92, 246),
    ICON_SOUND=(30, 140, 210),
    ICON_LEADERBOARD=(210, 140, 10),
    ICON_VICTORY=(185, 115, 5),
    ICON_SUCCESS=(15, 140, 100),
    ICON_HOME=(110, 110, 150),
)

# 2. Dark theme (Đêm - grape + coral pop on deep plum)
DARK_THEME = ThemeColors(
    BG_MAIN=(28, 25, 45),
    BG_CARD=(42, 38, 68),
    BG_BOARD=(42, 38, 68),
    WHITE=(255, 255, 255),
    GRID_THIN=(60, 55, 90),
    GRID_THICK=(150, 140, 190),
    GRID_OUTER=(255, 140, 120),
    CARD_BORDER=(60, 55, 90),
    SHADOW=(18, 16, 30),
    FIXED_TEXT=(255, 244, 230),
    USER_TEXT=(255, 150, 130),
    HINT_TEXT=(110, 230, 180),
    ERROR_TEXT=(255, 130, 130),
    NOTE_TEXT=(170, 160, 200),
    SELECTED_BG=(95, 65, 110),
    SELECTED_BORDER=(255, 150, 130),
    CROSSHAIR=(38, 34, 60),
    SAME_NUMBER=(150, 115, 60),
    ERROR_BG=(120, 40, 55),
    BTN_PRIMARY=(235, 95, 100),
    BTN_PRIMARY_HOVER=(245, 115, 120),
    BTN_SECONDARY=(55, 50, 85),
    BTN_SECONDARY_HOVER=(70, 64, 105),
    BTN_SECONDARY_TEXT=(255, 240, 225),
    BTN_ACTIVE=(80, 55, 90),
    BTN_ACTIVE_BORDER=(255, 150, 130),
    BTN_ACTIVE_TEXT=(255, 180, 160),
    BTN_VIVID_TEXT=(70, 20, 30),
    BTN_SUCCESS=(52, 220, 160),
    BTN_SUCCESS_HOVER=(80, 235, 180),
    BTN_WARNING=(255, 180, 80),
    BTN_WARNING_HOVER=(255, 200, 120),
    BTN_DANGER=(255, 110, 120),
    BTN_DANGER_HOVER=(255, 140, 150),
    NUM_DONE_BG=(38, 34, 60),
    NUM_DONE_TEXT=(160, 150, 185),
    HEADER_BG=(42, 38, 68),
    TIMER_TEXT=(255, 244, 230),
    STATUS_TEXT=(175, 165, 205),
    GOLD=(255, 200, 70),
    RIPPLE=(255, 150, 130),
    ICON_UNDO=(170, 140, 255),
    ICON_NOTES=(120, 170, 255),
    ICON_HINT=(255, 200, 80),
    ICON_ERASE=(255, 140, 130),
    ICON_PAUSE=(180, 150, 255),
    ICON_TIMER=(80, 200, 230),
    ICON_MISTAKES=(255, 150, 110),
    ICON_STATS=(130, 170, 255),
    ICON_DAILY=(255, 170, 90),
    ICON_STREAK=(255, 140, 100),
    ICON_SETTINGS=(170, 175, 200),
    ICON_THEME=(180, 150, 255),
    ICON_SOUND=(110, 180, 255),
    ICON_LEADERBOARD=(255, 205, 90),
    ICON_VICTORY=(255, 205, 90),
    ICON_SUCCESS=(90, 230, 170),
    ICON_HOME=(180, 175, 210),
)


# 3. Frost theme (Bạc hà - mint + turquoise + coral pop)
FROST_THEME = ThemeColors(
    BG_MAIN=(230, 248, 242),
    BG_CARD=(255, 255, 255),
    BG_BOARD=(255, 255, 255),
    WHITE=(255, 255, 255),
    GRID_THIN=(200, 230, 220),
    GRID_THICK=(20, 95, 95),
    GRID_OUTER=(10, 70, 75),
    CARD_BORDER=(205, 232, 222),
    SHADOW=(205, 232, 222),
    FIXED_TEXT=(16, 70, 75),
    USER_TEXT=(210, 60, 85),
    HINT_TEXT=(10, 170, 130),
    ERROR_TEXT=(225, 60, 90),
    NOTE_TEXT=(95, 122, 112),
    SELECTED_BG=(200, 240, 225),
    SELECTED_BORDER=(20, 180, 160),
    CROSSHAIR=(240, 250, 245),
    SAME_NUMBER=(255, 240, 190),
    ERROR_BG=(255, 215, 220),
    BTN_PRIMARY=(10, 160, 145),
    BTN_PRIMARY_HOVER=(8, 140, 128),
    BTN_SECONDARY=(215, 240, 232),
    BTN_SECONDARY_HOVER=(195, 230, 220),
    BTN_SECONDARY_TEXT=(20, 80, 75),
    BTN_ACTIVE=(200, 240, 225),
    BTN_ACTIVE_BORDER=(18, 190, 170),
    BTN_ACTIVE_TEXT=(5, 115, 105),
    BTN_VIVID_TEXT=(70, 25, 30),
    BTN_SUCCESS=(40, 200, 140),
    BTN_SUCCESS_HOVER=(25, 180, 120),
    BTN_WARNING=(250, 150, 60),
    BTN_WARNING_HOVER=(235, 130, 40),
    BTN_DANGER=(240, 100, 120),
    BTN_DANGER_HOVER=(220, 80, 100),
    NUM_DONE_BG=(215, 240, 232),
    NUM_DONE_TEXT=(74, 108, 98),
    HEADER_BG=(245, 252, 248),
    TIMER_TEXT=(16, 70, 75),
    STATUS_TEXT=(85, 125, 115),
    GOLD=(250, 175, 40),
    RIPPLE=(18, 190, 170),
    ICON_UNDO=(124, 93, 250),
    ICON_NOTES=(25, 125, 200),
    ICON_HINT=(170, 105, 5),
    ICON_ERASE=(235, 90, 110),
    ICON_PAUSE=(139, 92, 246),
    ICON_TIMER=(8, 150, 160),
    ICON_MISTAKES=(240, 120, 80),
    ICON_STATS=(30, 140, 220),
    ICON_DAILY=(240, 130, 50),
    ICON_STREAK=(235, 100, 70),
    ICON_SETTINGS=(110, 140, 150),
    ICON_THEME=(139, 92, 246),
    ICON_SOUND=(25, 140, 200),
    ICON_LEADERBOARD=(205, 135, 15),
    ICON_VICTORY=(185, 115, 5),
    ICON_SUCCESS=(15, 140, 100),
    ICON_HOME=(120, 140, 150),
)


# 4. Cozy theme (Đào - peach + berry on cream)
COZY_THEME = ThemeColors(
    BG_MAIN=(255, 240, 228),
    BG_CARD=(255, 250, 242),
    BG_BOARD=(255, 250, 242),
    WHITE=(255, 255, 255),
    GRID_THIN=(242, 214, 190),
    GRID_THICK=(120, 70, 60),
    GRID_OUTER=(80, 45, 40),
    CARD_BORDER=(242, 214, 190),
    SHADOW=(242, 214, 190),
    FIXED_TEXT=(75, 45, 40),
    USER_TEXT=(200, 55, 85),
    HINT_TEXT=(30, 150, 110),
    ERROR_TEXT=(210, 50, 60),
    NOTE_TEXT=(140, 102, 78),
    SELECTED_BG=(255, 220, 200),
    SELECTED_BORDER=(245, 120, 70),
    CROSSHAIR=(255, 244, 232),
    SAME_NUMBER=(255, 235, 180),
    ERROR_BG=(255, 215, 215),
    BTN_PRIMARY=(245, 120, 70),
    BTN_PRIMARY_HOVER=(225, 100, 55),
    BTN_SECONDARY=(250, 228, 205),
    BTN_SECONDARY_HOVER=(242, 215, 190),
    BTN_SECONDARY_TEXT=(100, 60, 45),
    BTN_ACTIVE=(255, 220, 200),
    BTN_ACTIVE_BORDER=(245, 120, 70),
    BTN_ACTIVE_TEXT=(175, 65, 38),
    BTN_VIVID_TEXT=(62, 15, 20),
    BTN_SUCCESS=(50, 190, 130),
    BTN_SUCCESS_HOVER=(35, 170, 115),
    BTN_WARNING=(245, 150, 50),
    BTN_WARNING_HOVER=(230, 130, 35),
    BTN_DANGER=(230, 90, 90),
    BTN_DANGER_HOVER=(210, 70, 70),
    NUM_DONE_BG=(250, 228, 205),
    NUM_DONE_TEXT=(128, 95, 72),
    HEADER_BG=(255, 248, 238),
    TIMER_TEXT=(75, 45, 40),
    STATUS_TEXT=(140, 105, 90),
    GOLD=(245, 165, 35),
    RIPPLE=(245, 120, 70),
    ICON_UNDO=(130, 95, 230),
    ICON_NOTES=(50, 130, 220),
    ICON_HINT=(175, 110, 10),
    ICON_ERASE=(225, 85, 85),
    ICON_PAUSE=(145, 95, 235),
    ICON_TIMER=(10, 145, 160),
    ICON_MISTAKES=(240, 115, 65),
    ICON_STATS=(50, 130, 220),
    ICON_DAILY=(240, 125, 45),
    ICON_STREAK=(230, 95, 65),
    ICON_SETTINGS=(140, 120, 105),
    ICON_THEME=(145, 95, 235),
    ICON_SOUND=(40, 135, 205),
    ICON_LEADERBOARD=(210, 135, 20),
    ICON_VICTORY=(190, 120, 10),
    ICON_SUCCESS=(25, 150, 105),
    ICON_HOME=(150, 130, 115),
)


class ThemeManager:
    """Manages theme state and provides current theme colors."""

    _instance = None
    _theme: ThemeMode = "light"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_theme()
        return cls._instance

    def _load_theme(self):
        """Load theme from persistent storage."""
        theme = get_preference("theme", "light")
        self._theme = theme if theme in THEME_ORDER else "light"

    def _save_theme(self):
        """Save theme to persistent storage."""
        set_preference("theme", self._theme)

    @property
    def theme(self) -> ThemeMode:
        return self._theme

    @theme.setter
    def theme(self, value: ThemeMode):
        if value in THEME_ORDER:
            self._theme = value
            self._save_theme()

    def cycle_theme(self) -> ThemeMode:
        """Cycle to next theme in order."""
        curr_idx = THEME_ORDER.index(self._theme) if self._theme in THEME_ORDER else 0
        next_idx = (curr_idx + 1) % len(THEME_ORDER)
        self._theme = THEME_ORDER[next_idx]
        self._save_theme()
        return self._theme

    @property
    def theme_icon(self) -> str:
        return THEME_ICONS.get(self._theme, "L")

    @property
    def colors(self) -> ThemeColors:
        if self._theme == "dark":
            return DARK_THEME
        elif self._theme == "frost":
            return FROST_THEME
        elif self._theme == "cozy":
            return COZY_THEME
        return LIGHT_THEME


class _ColorsProxy:
    """Backward-compatible proxy for Colors class."""

    def __getattr__(self, name):
        return getattr(get_theme_manager().colors, name)


Colors = _ColorsProxy()


def get_theme_manager() -> ThemeManager:
    """Get the global theme manager instance."""
    return ThemeManager()

