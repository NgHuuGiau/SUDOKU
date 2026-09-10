"""Color constants and theme system for Sudoku UI."""
from dataclasses import dataclass
from typing import Literal

from persistence import load_stats

ThemeMode = Literal["light", "dark", "frost", "cozy"]

THEME_ORDER: list[ThemeMode] = ["light", "dark", "frost", "cozy"]
THEME_NAMES = {
    "light": "Sáng Tối Giản",
    "dark": "Cyber Midnight",
    "frost": "Nordic Frost",
    "cozy": "Cozy Paper",
}
THEME_ICONS = {
    "light": "☀️",
    "dark": "🌙",
    "frost": "❄️",
    "cozy": "☕",
}


@dataclass(frozen=True)
class ThemeColors:
    """Color palette for a theme."""
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


# 1. Light theme (Modern Minimalist Light)
LIGHT_THEME = ThemeColors(
    BG_MAIN=(248, 250, 252),
    BG_CARD=(255, 255, 255),
    BG_BOARD=(255, 255, 255),
    WHITE=(255, 255, 255),

    GRID_THIN=(226, 232, 240),
    GRID_THICK=(71, 85, 105),
    GRID_OUTER=(15, 23, 42),
    CARD_BORDER=(226, 232, 240),
    SHADOW=(226, 232, 240),

    FIXED_TEXT=(15, 23, 42),
    USER_TEXT=(37, 99, 235),
    HINT_TEXT=(5, 150, 105),
    ERROR_TEXT=(220, 38, 38),
    NOTE_TEXT=(100, 116, 139),

    SELECTED_BG=(238, 242, 255),
    SELECTED_BORDER=(79, 70, 229),
    CROSSHAIR=(241, 245, 249),
    SAME_NUMBER=(254, 243, 199),
    ERROR_BG=(254, 226, 226),

    BTN_PRIMARY=(79, 70, 229),
    BTN_PRIMARY_HOVER=(67, 56, 202),
    BTN_SECONDARY=(241, 245, 249),
    BTN_SECONDARY_HOVER=(226, 232, 240),
    BTN_SECONDARY_TEXT=(30, 41, 59),

    BTN_ACTIVE=(238, 242, 255),
    BTN_ACTIVE_BORDER=(79, 70, 229),
    BTN_ACTIVE_TEXT=(67, 56, 202),

    BTN_SUCCESS=(16, 185, 129),
    BTN_SUCCESS_HOVER=(5, 150, 105),
    BTN_WARNING=(245, 158, 11),
    BTN_WARNING_HOVER=(217, 119, 6),
    BTN_DANGER=(239, 68, 68),
    BTN_DANGER_HOVER=(220, 38, 38),

    NUM_DONE_BG=(241, 245, 249),
    NUM_DONE_TEXT=(148, 163, 184),

    HEADER_BG=(255, 255, 255),
    TIMER_TEXT=(15, 23, 42),
    STATUS_TEXT=(71, 85, 105),
    GOLD=(234, 179, 8),
    RIPPLE=(99, 102, 241),
)


# 2. Dark theme (Cyber Midnight / AMOLED)
DARK_THEME = ThemeColors(
    BG_MAIN=(11, 15, 25),
    BG_CARD=(19, 27, 46),
    BG_BOARD=(19, 27, 46),
    WHITE=(255, 255, 255),

    GRID_THIN=(30, 41, 59),
    GRID_THICK=(100, 116, 139),
    GRID_OUTER=(56, 189, 248),
    CARD_BORDER=(30, 41, 59),
    SHADOW=(5, 8, 15),

    FIXED_TEXT=(248, 250, 252),
    USER_TEXT=(56, 189, 248),
    HINT_TEXT=(52, 211, 153),
    ERROR_TEXT=(248, 113, 113),
    NOTE_TEXT=(148, 163, 184),

    SELECTED_BG=(30, 58, 95),
    SELECTED_BORDER=(56, 189, 248),
    CROSSHAIR=(19, 35, 55),
    SAME_NUMBER=(49, 46, 129),
    ERROR_BG=(127, 29, 29),

    BTN_PRIMARY=(56, 189, 248),
    BTN_PRIMARY_HOVER=(14, 165, 233),
    BTN_SECONDARY=(30, 41, 59),
    BTN_SECONDARY_HOVER=(51, 65, 85),
    BTN_SECONDARY_TEXT=(241, 245, 249),

    BTN_ACTIVE=(12, 74, 110),
    BTN_ACTIVE_BORDER=(56, 189, 248),
    BTN_ACTIVE_TEXT=(56, 189, 248),

    BTN_SUCCESS=(16, 185, 129),
    BTN_SUCCESS_HOVER=(52, 211, 153),
    BTN_WARNING=(245, 158, 11),
    BTN_WARNING_HOVER=(251, 191, 36),
    BTN_DANGER=(239, 68, 68),
    BTN_DANGER_HOVER=(248, 113, 113),

    NUM_DONE_BG=(23, 32, 54),
    NUM_DONE_TEXT=(100, 116, 139),

    HEADER_BG=(19, 27, 46),
    TIMER_TEXT=(248, 250, 252),
    STATUS_TEXT=(148, 163, 184),
    GOLD=(234, 179, 8),
    RIPPLE=(56, 189, 248),
)


# 3. Frost theme (Nordic Frost)
FROST_THEME = ThemeColors(
    BG_MAIN=(14, 23, 38),
    BG_CARD=(22, 34, 56),
    BG_BOARD=(22, 34, 56),
    WHITE=(255, 255, 255),

    GRID_THIN=(31, 52, 84),
    GRID_THICK=(125, 211, 252),
    GRID_OUTER=(45, 212, 191),
    CARD_BORDER=(31, 52, 84),
    SHADOW=(7, 12, 20),

    FIXED_TEXT=(240, 253, 250),
    USER_TEXT=(45, 212, 191),
    HINT_TEXT=(110, 231, 183),
    ERROR_TEXT=(251, 113, 133),
    NOTE_TEXT=(148, 163, 184),

    SELECTED_BG=(19, 78, 74),
    SELECTED_BORDER=(45, 212, 191),
    CROSSHAIR=(22, 46, 74),
    SAME_NUMBER=(6, 95, 70),
    ERROR_BG=(136, 19, 55),

    BTN_PRIMARY=(45, 212, 191),
    BTN_PRIMARY_HOVER=(20, 184, 166),
    BTN_SECONDARY=(26, 46, 74),
    BTN_SECONDARY_HOVER=(41, 71, 112),
    BTN_SECONDARY_TEXT=(226, 232, 240),

    BTN_ACTIVE=(15, 118, 110),
    BTN_ACTIVE_BORDER=(45, 212, 191),
    BTN_ACTIVE_TEXT=(204, 251, 241),

    BTN_SUCCESS=(20, 184, 166),
    BTN_SUCCESS_HOVER=(45, 212, 191),
    BTN_WARNING=(251, 146, 60),
    BTN_WARNING_HOVER=(253, 186, 116),
    BTN_DANGER=(244, 63, 94),
    BTN_DANGER_HOVER=(251, 113, 133),

    NUM_DONE_BG=(20, 36, 58),
    NUM_DONE_TEXT=(100, 116, 139),

    HEADER_BG=(22, 34, 56),
    TIMER_TEXT=(240, 253, 250),
    STATUS_TEXT=(125, 211, 252),
    GOLD=(250, 204, 21),
    RIPPLE=(45, 212, 191),
)


# 4. Cozy theme (Cozy Paper / Vintage Coffee)
COZY_THEME = ThemeColors(
    BG_MAIN=(253, 251, 247),
    BG_CARD=(247, 242, 233),
    BG_BOARD=(251, 248, 242),
    WHITE=(255, 255, 255),

    GRID_THIN=(230, 222, 209),
    GRID_THICK=(146, 64, 14),
    GRID_OUTER=(69, 26, 3),
    CARD_BORDER=(230, 222, 209),
    SHADOW=(220, 210, 195),

    FIXED_TEXT=(43, 26, 13),
    USER_TEXT=(194, 65, 12),
    HINT_TEXT=(21, 128, 61),
    ERROR_TEXT=(185, 28, 28),
    NOTE_TEXT=(140, 115, 93),

    SELECTED_BG=(255, 237, 213),
    SELECTED_BORDER=(234, 88, 12),
    CROSSHAIR=(243, 236, 224),
    SAME_NUMBER=(254, 215, 170),
    ERROR_BG=(254, 226, 226),

    BTN_PRIMARY=(234, 88, 12),
    BTN_PRIMARY_HOVER=(194, 65, 12),
    BTN_SECONDARY=(239, 231, 216),
    BTN_SECONDARY_HOVER=(222, 210, 190),
    BTN_SECONDARY_TEXT=(56, 34, 17),

    BTN_ACTIVE=(255, 237, 213),
    BTN_ACTIVE_BORDER=(234, 88, 12),
    BTN_ACTIVE_TEXT=(194, 65, 12),

    BTN_SUCCESS=(22, 163, 74),
    BTN_SUCCESS_HOVER=(34, 197, 94),
    BTN_WARNING=(217, 119, 6),
    BTN_WARNING_HOVER=(245, 158, 11),
    BTN_DANGER=(220, 38, 38),
    BTN_DANGER_HOVER=(239, 68, 68),

    NUM_DONE_BG=(235, 227, 213),
    NUM_DONE_TEXT=(168, 150, 130),

    HEADER_BG=(247, 242, 233),
    TIMER_TEXT=(43, 26, 13),
    STATUS_TEXT=(120, 95, 75),
    GOLD=(217, 119, 6),
    RIPPLE=(234, 88, 12),
)


# Backward compatibility - use light theme as default
Colors = LIGHT_THEME


# Menu colors for tkinter
MENU_COLORS_LIGHT = {
    'bg': '#f8fafc',
    'hero': '#1e293b',
    'card': '#ffffff',
    'primary': '#4f46e5',
    'primary_hover': '#4338ca',
    'secondary': '#10b981',
    'secondary_hover': '#059669',
    'warning': '#f59e0b',
    'warning_hover': '#d97706',
    'danger': '#ef4444',
    'danger_hover': '#dc2626',
    'text_dark': '#0f172a',
    'text_muted': '#64748b',
    'text_light': '#ffffff',
    'border': '#e2e8f0',
    'badge_bg': '#eef2ff',
    'badge_fg': '#4338ca',
}

MENU_COLORS_DARK = {
    'bg': '#0b0f19',
    'hero': '#f8fafc',
    'card': '#131b2e',
    'primary': '#38bdf8',
    'primary_hover': '#0ea5e9',
    'secondary': '#34d399',
    'secondary_hover': '#10b981',
    'warning': '#fbbf24',
    'warning_hover': '#f59e0b',
    'danger': '#f87171',
    'danger_hover': '#ef4444',
    'text_dark': '#f8fafc',
    'text_muted': '#94a3b8',
    'text_light': '#0b0f19',
    'border': '#1e293b',
    'badge_bg': '#1e3a5f',
    'badge_fg': '#38bdf8',
}

MENU_COLORS_FROST = {
    'bg': '#0e1726',
    'hero': '#f0fdfa',
    'card': '#162238',
    'primary': '#2dd4bf',
    'primary_hover': '#14b8a6',
    'secondary': '#38bdf8',
    'secondary_hover': '#0284c7',
    'warning': '#fb923c',
    'warning_hover': '#f97316',
    'danger': '#fb7185',
    'danger_hover': '#f43f5e',
    'text_dark': '#f0fdfa',
    'text_muted': '#7dd3fc',
    'text_light': '#0e1726',
    'border': '#1f3454',
    'badge_bg': '#0f766e',
    'badge_fg': '#ccfbf1',
}

MENU_COLORS_COZY = {
    'bg': '#fdfbf7',
    'hero': '#2b1a0d',
    'card': '#f7f2e9',
    'primary': '#ea580c',
    'primary_hover': '#c2410c',
    'secondary': '#16a34a',
    'secondary_hover': '#15803d',
    'warning': '#d97706',
    'warning_hover': '#b45309',
    'danger': '#dc2626',
    'danger_hover': '#b91c1c',
    'text_dark': '#2b1a0d',
    'text_muted': '#8c735d',
    'text_light': '#ffffff',
    'border': '#e6ded1',
    'badge_bg': '#fed7aa',
    'badge_fg': '#9a3412',
}


def get_menu_colors(theme: ThemeMode = "light") -> dict:
    """Get menu colors for the given theme."""
    if theme == "dark":
        return MENU_COLORS_DARK
    elif theme == "frost":
        return MENU_COLORS_FROST
    elif theme == "cozy":
        return MENU_COLORS_COZY
    return MENU_COLORS_LIGHT


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
        try:
            stats = load_stats()
            t = stats.get("theme", "light")
            self._theme = t if t in THEME_ORDER else "light"
        except Exception:
            self._theme = "light"

    def _save_theme(self):
        """Save theme to persistent storage."""
        try:
            stats = load_stats()
            stats["theme"] = self._theme
            from persistence import save_stats
            save_stats(stats)
        except Exception:
            pass

    @property
    def theme(self) -> ThemeMode:
        return self._theme

    @theme.setter
    def theme(self, value: ThemeMode):
        if value in THEME_ORDER:
            self._theme = value
            self._save_theme()

    def toggle(self):
        """Cycle to the next theme."""
        self.cycle_theme()

    def cycle_theme(self) -> ThemeMode:
        """Cycle to next theme in order."""
        curr_idx = THEME_ORDER.index(self._theme) if self._theme in THEME_ORDER else 0
        next_idx = (curr_idx + 1) % len(THEME_ORDER)
        self._theme = THEME_ORDER[next_idx]
        self._save_theme()
        return self._theme

    @property
    def theme_name(self) -> str:
        return THEME_NAMES.get(self._theme, "Sáng Tối Giản")

    @property
    def theme_icon(self) -> str:
        return THEME_ICONS.get(self._theme, "☀️")

    @property
    def colors(self) -> ThemeColors:
        if self._theme == "dark":
            return DARK_THEME
        elif self._theme == "frost":
            return FROST_THEME
        elif self._theme == "cozy":
            return COZY_THEME
        return LIGHT_THEME

    @property
    def menu_colors(self) -> dict:
        return get_menu_colors(self._theme)

    @property
    def is_dark(self) -> bool:
        return self._theme in ("dark", "frost")


# Backward compatibility - dynamic properties
def _get_current_theme_manager() -> ThemeManager:
    return get_theme_manager()


class _ColorsProxy:
    """Backward-compatible proxy for Colors class."""
    def __getattr__(self, name):
        return getattr(get_theme_manager().colors, name)


class _MenuColorsProxy:
    """Backward-compatible proxy for MENU_COLORS dict."""
    def __getitem__(self, key):
        return get_theme_manager().menu_colors[key]

    def get(self, key, default=None):
        return get_theme_manager().menu_colors.get(key, default)

    def __contains__(self, key):
        return key in get_theme_manager().menu_colors

    def keys(self):
        return get_theme_manager().menu_colors.keys()

    def values(self):
        return get_theme_manager().menu_colors.values()

    def items(self):
        return get_theme_manager().menu_colors.items()


Colors = _ColorsProxy()
MENU_COLORS = _MenuColorsProxy()


def get_theme_manager() -> ThemeManager:
    """Get the global theme manager instance."""
    return ThemeManager()


def get_current_colors() -> ThemeColors:
    """Get current theme colors (for backward compatibility)."""
    return get_theme_manager().colors


def get_current_menu_colors() -> dict:
    """Get current menu colors (for backward compatibility)."""
    return get_theme_manager().menu_colors
