"""Color constants for Sudoku UI."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Colors:
    BG_MAIN = (248, 250, 252)         # Slate-50
    BG_CARD = (255, 255, 255)         # White
    BG_BOARD = (255, 255, 255)
    WHITE = (255, 255, 255)

    GRID_THIN = (226, 232, 240)       # Slate-200
    GRID_THICK = (51, 65, 85)         # Slate-700
    GRID_OUTER = (15, 23, 42)         # Slate-900
    CARD_BORDER = (226, 232, 240)
    SHADOW = (226, 232, 240)

    FIXED_TEXT = (15, 23, 42)         # Slate-900
    USER_TEXT = (37, 99, 235)         # Blue-600
    HINT_TEXT = (5, 150, 105)         # Emerald-600
    ERROR_TEXT = (220, 38, 38)        # Red-600
    NOTE_TEXT = (100, 116, 139)       # Slate-500

    SELECTED_BG = (238, 242, 255)     # Indigo-50
    SELECTED_BORDER = (79, 70, 229)   # Indigo-600
    CROSSHAIR = (241, 245, 249)       # Slate-100
    SAME_NUMBER = (254, 243, 199)     # Amber-100
    ERROR_BG = (254, 226, 226)        # Red-100

    BTN_PRIMARY = (79, 70, 229)       # Indigo-600
    BTN_PRIMARY_HOVER = (67, 56, 202) # Indigo-700
    BTN_SECONDARY = (241, 245, 249)   # Slate-100
    BTN_SECONDARY_HOVER = (226, 232, 240)
    BTN_SECONDARY_TEXT = (30, 41, 59)

    BTN_ACTIVE = (238, 242, 255)      # Indigo-50
    BTN_ACTIVE_BORDER = (79, 70, 229)
    BTN_ACTIVE_TEXT = (67, 56, 202)

    BTN_SUCCESS = (16, 185, 129)      # Emerald-500
    BTN_SUCCESS_HOVER = (5, 150, 105)
    BTN_WARNING = (245, 158, 11)      # Amber-500
    BTN_WARNING_HOVER = (217, 119, 6)
    BTN_DANGER = (239, 68, 68)        # Red-500
    BTN_DANGER_HOVER = (220, 38, 38)

    NUM_DONE_BG = (241, 245, 249)
    NUM_DONE_TEXT = (148, 163, 184)

    HEADER_BG = (255, 255, 255)
    TIMER_TEXT = (15, 23, 42)
    STATUS_TEXT = (71, 85, 105)
    GOLD = (234, 179, 8)


MENU_COLORS = {
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