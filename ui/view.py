"""Main game view renderer - combines all UI components."""
import pygame

from ui.board import draw_board
from ui.colors import Colors
from ui.fonts import GameFonts, load_fonts
from ui.geometry import get_timer_rect
from ui.icons import Particle
from ui.modals import draw_footer_helper, draw_header, draw_pause_modal, draw_win_modal
from ui.screen import create_game_screen
from ui.sidebar import draw_sidebar


def draw_game_view(screen: pygame.Surface, fonts: GameFonts, state, mouse_pos, particles=None, translate=None) -> dict:
    if translate is None:
        from config import game_text
        translate = game_text

    overlay_rects = {
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
        draw_footer_helper(screen, fonts, translate)

    # 4. Win Modal
    if state.game_over:
        win_rects = draw_win_modal(screen, fonts, mouse_pos, translate, state, particles)
        overlay_rects.update(win_rects)

    # 5. Pause Modal
    elif state.paused:
        pause_rects = draw_pause_modal(screen, fonts, mouse_pos, translate)
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
