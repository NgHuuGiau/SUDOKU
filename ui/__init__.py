"""Sudoku UI package - Modular UI components.

This package provides all UI components for the Sudoku game:
- colors: Color constants & theme system
- fonts: Font loading
- icons: Smooth supersampled icons & particles
- geometry: Layout calculations & constants
- drawing: Drawing primitives (cards, buttons)
- board: Board rendering
- sidebar: Sidebar controls
- modals: Pause/Win modals & header/footer
- screen: Screen initialization
- view: Main game view renderer
- menu: Tkinter-based main menu
"""

from ui.board import draw_board, trigger_completion_animation, trigger_number_placement_animation
from ui.colors import (
    COZY_THEME,
    DARK_THEME,
    FROST_THEME,
    LIGHT_THEME,
    MENU_COLORS,
    Colors,
    ThemeColors,
    ThemeManager,
    get_current_colors,
    get_current_menu_colors,
    get_theme_manager,
)
from ui.drawing import draw_modern_button, draw_rounded_card
from ui.fonts import GameFonts, load_fonts
from ui.geometry import (
    BOARD_SIZE,
    BOARD_X,
    BOARD_Y,
    CELL_SIZE,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SIDEBAR_WIDTH,
    SIDEBAR_X,
    SIDEBAR_Y,
    get_cell_from_pos,
    get_remaining_counts,
    get_sidebar_layout,
    get_timer_rect,
)
from ui.icons import Particle, SmoothIcons
from ui.menu import MenuSudoku, tao_nut_bat_dau
from ui.modals import (
    draw_footer_helper,
    draw_header,
    draw_help_modal,
    draw_pause_modal,
    draw_win_modal,
)
from ui.screen import create_game_screen, enable_high_dpi, get_sudoku_icon_path
from ui.sidebar import draw_sidebar
from ui.view import draw_game_view

__all__ = [
    # Colors & Themes
    "Colors",
    "MENU_COLORS",
    "ThemeColors",
    "LIGHT_THEME",
    "DARK_THEME",
    "FROST_THEME",
    "COZY_THEME",
    "ThemeManager",
    "get_theme_manager",
    "get_current_colors",
    "get_current_menu_colors",
    # Fonts
    "load_fonts",
    "GameFonts",
    # Icons
    "SmoothIcons",
    "Particle",
    # Geometry
    "SCREEN_WIDTH",
    "SCREEN_HEIGHT",
    "BOARD_SIZE",
    "CELL_SIZE",
    "BOARD_X",
    "BOARD_Y",
    "SIDEBAR_X",
    "SIDEBAR_Y",
    "SIDEBAR_WIDTH",
    "get_timer_rect",
    "get_cell_from_pos",
    "get_sidebar_layout",
    "get_remaining_counts",
    # Drawing
    "draw_rounded_card",
    "draw_modern_button",
    # Components
    "draw_board",
    "trigger_number_placement_animation",
    "trigger_completion_animation",
    "draw_sidebar",
    "draw_header",
    "draw_footer_helper",
    "draw_win_modal",
    "draw_pause_modal",
    "draw_help_modal",
    # Screen
    "create_game_screen",
    "enable_high_dpi",
    "get_sudoku_icon_path",
    # View
    "draw_game_view",
    # Menu
    "MenuSudoku",
    "tao_nut_bat_dau",
]
