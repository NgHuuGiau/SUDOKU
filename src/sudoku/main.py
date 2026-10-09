"""Sudoku entry point with an optional packaged-build smoke test."""

import logging
import os
import sys
from tempfile import TemporaryDirectory


def _run_smoke_test() -> None:
    """Headlessly render the packaged app to verify the build works."""
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    with TemporaryDirectory() as data_dir:
        os.environ["SUDOKU_DATA_DIR"] = data_dir

        import pygame

        from sudoku.config import game_text
        from sudoku.game import GameState
        from sudoku.ui import create_game_screen, draw_game_view, load_fonts
        from sudoku.ui.menu import draw_menu_view
        from sudoku.ui.modals import draw_help_modal

        screen = create_game_screen()
        try:
            fonts = load_fonts()
            draw_menu_view(screen, fonts, (0, 0))
            draw_game_view(screen, fonts, GameState("easy"), (0, 0))
            draw_help_modal(screen, fonts, (0, 0), game_text)
        finally:
            pygame.quit()
            # Release log files held open inside the temp data dir,
            # otherwise cleanup fails on Windows (open files can't be deleted).
            logging.shutdown()


if __name__ == "__main__":
    if "--smoke-test" in sys.argv:
        _run_smoke_test()
    else:
        from sudoku.ui import tao_nut_bat_dau

        tao_nut_bat_dau()
