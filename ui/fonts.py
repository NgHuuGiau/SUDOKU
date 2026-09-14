"""Font loading for Sudoku UI."""

from dataclasses import dataclass

import pygame


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
    hero: pygame.font.Font
    hero_large: pygame.font.Font


def load_fonts() -> GameFonts:
    """Load all game fonts with fallback chain."""

    def get_font(size: int, is_bold: bool = False, is_italic: bool = False) -> pygame.font.Font:
        for font_name in ("segoe ui", "tahoma", "helvetica", "arial"):
            matched_font = pygame.font.match_font(font_name, bold=is_bold, italic=is_italic)
            if matched_font:
                return pygame.font.Font(matched_font, size)
        return pygame.font.SysFont("arial", size, bold=is_bold, italic=is_italic)

    return GameFonts(
        cell=get_font(42, is_bold=True),
        cell_bold=get_font(46, is_bold=True),
        small=get_font(18, is_bold=True),
        medium=get_font(22, is_bold=True),
        large=get_font(36, is_bold=True),
        title=get_font(28, is_bold=True),
        note=get_font(14, is_bold=True),
        tiny=get_font(14),
        badge=get_font(14, is_bold=True),
        hero=get_font(32, is_bold=True),
        hero_large=get_font(40, is_bold=True),
    )
