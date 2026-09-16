"""Sudoku entry point with an optional packaged-build smoke test."""

import os
import sys
from tempfile import TemporaryDirectory


def _run_smoke_test() -> None:
    """Headlessly render the packaged app and verify its bundled Tcl runtime."""
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    with TemporaryDirectory() as data_dir:
        os.environ["SUDOKU_DATA_DIR"] = data_dir

        import tkinter

        tkinter.Tcl().eval("info patchlevel")

        import pygame

        from config import game_text
        from game import GameState
        from ui import create_game_screen, draw_game_view, load_fonts
        from ui.menu import draw_menu_view
        from ui.modals import draw_help_modal

        screen = create_game_screen()
        try:
            fonts = load_fonts()
            draw_menu_view(screen, fonts, (0, 0))
            draw_game_view(screen, fonts, GameState("easy"), (0, 0))
            draw_help_modal(screen, fonts, (0, 0), game_text)
        finally:
            pygame.quit()


if __name__ == "__main__":
    if "--smoke-test" in sys.argv:
        _run_smoke_test()
    else:
        from ui import tao_nut_bat_dau

        tao_nut_bat_dau()
