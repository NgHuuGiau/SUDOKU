"""Font loading for Sudoku UI."""
import pygame
from dataclasses import dataclass


@dataclass(frozen=True)
class GameFonts:
    cell: pygame.font.Font
    cell_bold: pygame.font.Font
    small: pygame.font.Font
    medium: pygame.font.Font
    large: pygame.font.Font
    title: pygame.font.Font
    note: pygame.font.Font
    tiny: pygame.font.Font
    badge: pygame.font.Font


def load_fonts() -> GameFonts:
    """Load all game fonts with fallback chain."""
    def get_font(size: int, is_bold: bool = False, is_italic: bool = False) -> pygame.font.Font:
        for font_name in ("segoe ui", "tahoma", "helvetica", "arial"):
            matched_font = pygame.font.match_font(font_name, bold=is_bold, italic=is_italic)
            if matched_font:
                return pygame.font.Font(matched_font, size)
        return pygame.font.SysFont("arial", size, bold=is_bold, italic=is_italic)

    return GameFonts(
        cell=get_font(38, is_bold=True),
        cell_bold=get_font(42, is_bold=True),
        small=get_font(16, is_bold=True),
        medium=get_font(24, is_bold=True),
        large=get_font(36, is_bold=True),
        title=get_font(24, is_bold=True),
        note=get_font(13, is_bold=True),
        tiny=get_font(13),
        badge=get_font(12, is_bold=True),
    )