"""Main game view renderer - combines all UI components."""

import pygame

from sudoku.ui.board import draw_board
from sudoku.ui.colors import Colors
from sudoku.ui.fonts import GameFonts, load_fonts
from sudoku.ui.geometry import get_timer_rect
from sudoku.ui.icons import Particle
from sudoku.ui.modals import draw_footer_helper, draw_header, draw_pause_modal, draw_win_modal
from sudoku.ui.screen import create_game_screen
from sudoku.ui.sidebar import draw_sidebar


def draw_game_view(
    screen: pygame.Surface, fonts: GameFonts, state, mouse_pos, particles=None, translate=None
) -> dict:
    if translate is None:
        from sudoku.config import game_text

        translate = game_text

    overlay_rects: dict[str, pygame.Rect | None] = {
        "pause_resume": None,
        "pause_quit": None,
        "win_restart": None,
        "win_quit": None,
        "header_pause": None,
        "header_theme": None,
        "header_sound": None,
        "header_help": None,
    }

    screen.fill(Colors.BG_MAIN)

    # 1. Header
    header_res = draw_header(screen, fonts, state, mouse_pos, translate)
    overlay_rects.update(header_res)

    # 2. Board
    draw_board(screen, fonts, state)

    # 3. Sidebar & Footer (only when playing)
    if not state.game_over and not state.paused:
        draw_sidebar(screen, fonts, mouse_pos, translate, state)
        draw_footer_helper(screen, fonts, translate, getattr(state, "save_failed", False))

    # 4. Win Modal
    if state.game_over:
        win_rects = draw_win_modal(screen, fonts, mouse_pos, translate, state, particles)
        overlay_rects.update(win_rects)

    # 5. Pause Modal
    elif state.paused:
        pause_rects = draw_pause_modal(
            screen, fonts, mouse_pos, translate, getattr(state, "save_failed", False)
        )
        overlay_rects.update(pause_rects)

    pygame.display.flip()
    return overlay_rects


__all__ = [
    "create_game_screen",
    "load_fonts",
    "GameFonts",
    "draw_game_view",
    "Particle",
    "get_timer_rect",
    "draw_board",
    "draw_sidebar",
    "draw_header",
    "draw_footer_helper",
]


