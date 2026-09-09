"""Sudoku UI package - Modular UI components.

This package provides all UI components for the Sudoku game:
- colors: Color constants
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

from ui.colors import Colors, MENU_COLORS
from ui.fonts import load_fonts, GameFonts
from ui.icons import SmoothIcons, Particle
from ui.geometry import (
    SCREEN_WIDTH, SCREEN_HEIGHT, BOARD_SIZE, CELL_SIZE,
    BOARD_X, BOARD_Y, SIDEBAR_X, SIDEBAR_Y, SIDEBAR_WIDTH,
    get_timer_rect, get_cell_from_pos, get_sidebar_layout, get_remaining_counts
)
from ui.drawing import draw_rounded_card, draw_modern_button
from ui.board import draw_board
from ui.sidebar import draw_sidebar
from ui.modals import draw_header, draw_footer_helper, draw_win_modal, draw_pause_modal
from ui.screen import create_game_screen, enable_high_dpi, get_sudoku_icon_path
from ui.view import draw_game_view
from ui.menu import MenuSudoku, tao_nut_bat_dau

__all__ = [
    # Colors
    "Colors",
    "MENU_COLORS",
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
    "draw_sidebar",
    "draw_header",
    "draw_footer_helper",
    "draw_win_modal",
    "draw_pause_modal",
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