"""Screen initialization for Sudoku."""
import os
import ctypes
import pygame


def enable_high_dpi() -> None:
    try:
        ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
    except Exception:
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass


def get_sudoku_icon_path() -> str:
    return os.path.join(os.path.dirname(__file__), "..", "Picture", "SUDOKU.ico")


def create_game_screen() -> pygame.Surface:
    from ui.geometry import SCREEN_WIDTH, SCREEN_HEIGHT
    from config import APP_TITLE

    enable_high_dpi()
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(APP_TITLE)
    try:
        icon_path = get_sudoku_icon_path()
        if os.path.exists(icon_path):
            pygame.display.set_icon(pygame.image.load(icon_path))
    except Exception:
        pass
    return screen