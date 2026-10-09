"""Screen initialization for Sudoku."""

import ctypes
import os
import sys

import pygame


def _fit_window_size(
    desktop_size: tuple[int, int], logical_size: tuple[int, int], margin: tuple[int, int] = (32, 80)
) -> tuple[int, int]:
    available_w = max(1, desktop_size[0] - margin[0])
    available_h = max(1, desktop_size[1] - margin[1])
    scale = min(1.0, available_w / logical_size[0], available_h / logical_size[1])
    return round(logical_size[0] * scale), round(logical_size[1] * scale)


def enable_high_dpi() -> None:
    if sys.platform != "win32":
        return

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
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, "assets", "icons", "SUDOKU.ico")
    project_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    return os.path.join(project_dir, "assets", "icons", "SUDOKU.ico")


def create_game_screen() -> pygame.Surface:
    from sudoku.config import APP_TITLE
    from sudoku.ui.geometry import SCREEN_HEIGHT, SCREEN_WIDTH

    enable_high_dpi()
    pygame.init()
    pygame.font.init()
    logical_size = (SCREEN_WIDTH, SCREEN_HEIGHT)
    desktop_sizes = pygame.display.get_desktop_sizes()
    if (
        os.environ.get("SDL_VIDEODRIVER") != "dummy"
        and desktop_sizes
        and _fit_window_size(desktop_sizes[0], logical_size) != logical_size
    ):
        screen = pygame.display.set_mode(logical_size, pygame.SCALED | pygame.RESIZABLE)
        try:
            from pygame._sdl2.video import Window

            window = Window.from_display_module()
            window.resizable = True
            window.size = _fit_window_size(desktop_sizes[0], logical_size)
            window.position = (0, 0)
        except Exception:
            screen = pygame.display.set_mode(logical_size, pygame.SCALED | pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode(logical_size)
    pygame.display.set_caption(APP_TITLE)
    try:
        icon_path = get_sudoku_icon_path()
        if os.path.exists(icon_path):
            pygame.display.set_icon(pygame.image.load(icon_path))
    except Exception:
        pass
    return screen
