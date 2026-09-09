"""Color constants and theme system for Sudoku UI."""
from dataclasses import dataclass
from typing import Literal
from persistence import get_daily_stats, load_stats


ThemeMode = Literal["light", "dark"]


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


# Light theme (default)
LIGHT_THEME = ThemeColors(
    BG_MAIN=(248, 250, 252),
    BG_CARD=(255, 255, 255),
    BG_BOARD=(255, 255, 255),
    WHITE=(255, 255, 255),

    GRID_THIN=(226, 232, 240),
    GRID_THICK=(51, 65, 85),
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
)


# Dark theme
DARK_THEME = ThemeColors(
    BG_MAIN=(15, 23, 42),
    BG_CARD=(30, 41, 59),
    BG_BOARD=(30, 41, 59),
    WHITE=(255, 255, 255),

    GRID_THIN=(51, 65, 85),
    GRID_THICK=(148, 163, 184),
    GRID_OUTER=(226, 232, 240),
    CARD_BORDER=(51, 65, 85),
    SHADOW=(0, 0, 0),

    FIXED_TEXT=(248, 250, 252),
    USER_TEXT=(96, 165, 250),
    HINT_TEXT=(52, 211, 153),
    ERROR_TEXT=(248, 113, 113),
    NOTE_TEXT=(148, 163, 184),

    SELECTED_BG=(51, 65, 85),
    SELECTED_BORDER=(96, 165, 250),
    CROSSHAIR=(30, 41, 59),
    SAME_NUMBER=(79, 70, 229),
    ERROR_BG=(127, 29, 29),

    BTN_PRIMARY=(96, 165, 250),
    BTN_PRIMARY_HOVER=(129, 184, 255),
    BTN_SECONDARY=(51, 65, 85),
    BTN_SECONDARY_HOVER=(71, 85, 105),
    BTN_SECONDARY_TEXT=(226, 232, 240),

    BTN_ACTIVE=(51, 65, 85),
    BTN_ACTIVE_BORDER=(96, 165, 250),
    BTN_ACTIVE_TEXT=(129, 184, 255),

    BTN_SUCCESS=(16, 185, 129),
    BTN_SUCCESS_HOVER=(52, 211, 153),
    BTN_WARNING=(245, 158, 11),
    BTN_WARNING_HOVER=(251, 191, 36),
    BTN_DANGER=(239, 68, 68),
    BTN_DANGER_HOVER=(252, 130, 130),

    NUM_DONE_BG=(51, 65, 85),
    NUM_DONE_TEXT=(148, 163, 184),

    HEADER_BG=(30, 41, 59),
    TIMER_TEXT=(248, 250, 252),
    STATUS_TEXT=(148, 163, 184),
    GOLD=(234, 179, 8),
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
    'bg': '#0f172a',
    'hero': '#f8fafc',
    'card': '#1e293b',
    'primary': '#60a5fa',
    'primary_hover': '#93c5fd',
    'secondary': '#34d399',
    'secondary_hover': '#6ee7b7',
    'warning': '#fbbf24',
    'warning_hover': '#fcd34d',
    'danger': '#f87171',
    'danger_hover': '#fca5a5',
    'text_dark': '#f8fafc',
    'text_muted': '#94a3b8',
    'text_light': '#0f172a',
    'border': '#334155',
    'badge_bg': '#1e3a5f',
    'badge_fg': '#93c5fd',
}


def get_menu_colors(theme: ThemeMode = "light") -> dict:
    """Get menu colors for the given theme."""
    return MENU_COLORS_DARK if theme == "dark" else MENU_COLORS_LIGHT


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
            self._theme = stats.get("theme", "light")
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
        self._theme = value
        self._save_theme()
    
    def toggle(self):
        self._theme = "dark" if self._theme == "light" else "light"
        self._save_theme()
    
    @property
    def colors(self) -> ThemeColors:
        return DARK_THEME if self._theme == "dark" else LIGHT_THEME
    
    @property
    def menu_colors(self) -> dict:
        return get_menu_colors(self._theme)
    
    @property
    def is_dark(self) -> bool:
        return self._theme == "dark"


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