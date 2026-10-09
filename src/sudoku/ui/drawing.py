"""Drawing primitives for Sudoku UI."""

import pygame

from sudoku.ui.colors import Colors


def fit_surface(
    surface: pygame.Surface, max_width: int, max_height: int | None = None
) -> pygame.Surface:
    """Keep a rendered label inside its button without changing its font globally."""
    width, height = surface.get_size()
    scale = min(1.0, max_width / max(1, width))
    if max_height is not None:
        scale = min(scale, max_height / max(1, height))
    if scale >= 1.0:
        return surface
    return pygame.transform.smoothscale(
        surface, (max(1, int(width * scale)), max(1, int(height * scale)))
    )


def soft_tint(fg, bg, amount: float = 0.16) -> tuple:
    """Blend a vivid icon color toward the card background for tile fills."""
    return tuple(int(f * amount + b * (1.0 - amount)) for f, b in zip(fg, bg, strict=False))


def draw_icon_tile(
    screen: pygame.Surface,
    rect: pygame.Rect,
    icon_name: str,
    color,
    icon_size: int = 24,
    radius: int = 12,
    bg=None,
) -> None:
    """Colored glyph on a soft tinted tile (auto-adapts to light/dark themes)."""
    from sudoku.ui.icons import SmoothIcons

    tile_bg = soft_tint(color, bg or Colors.BG_CARD) if bg != "transparent" else None
    if tile_bg is not None:
        pygame.draw.rect(screen, tile_bg, rect, border_radius=radius)
    icon_surf = SmoothIcons.get(icon_name, icon_size, color)
    screen.blit(icon_surf, icon_surf.get_rect(center=rect.center))


def draw_rounded_card(
    screen: pygame.Surface,
    rect: pygame.Rect,
    bg_color,
    border_color=None,
    border_width=1,
    radius=14,
    shadow=False,
):
    if shadow:
        shadow_rect = rect.move(0, 3)
        pygame.draw.rect(screen, Colors.SHADOW, shadow_rect, border_radius=radius)
    pygame.draw.rect(screen, bg_color, rect, border_radius=radius)
    if border_color and border_width > 0:
        pygame.draw.rect(screen, border_color, rect, width=border_width, border_radius=radius)


def draw_badge(
    screen: pygame.Surface,
    rect: pygame.Rect,
    text: str,
    font,
    bg_color,
    text_color,
    icon_name=None,
    icon_size=14,
    radius=6,
):
    """Draw a compact pill badge with optional icon."""
    from sudoku.ui.icons import SmoothIcons

    pygame.draw.rect(screen, bg_color, rect, border_radius=radius)
    t_surf = font.render(text, True, text_color)
    if icon_name:
        i_surf = SmoothIcons.get(icon_name, icon_size, text_color)
        total_w = icon_size + 6 + t_surf.get_width()
        start_x = rect.centerx - total_w // 2
        screen.blit(i_surf, (start_x, rect.centery - icon_size // 2))
        screen.blit(t_surf, (start_x + icon_size + 6, rect.centery - t_surf.get_height() // 2))
    else:
        screen.blit(t_surf, t_surf.get_rect(center=rect.center))


def draw_interactive_card(
    screen: pygame.Surface,
    rect: pygame.Rect,
    mouse_pos,
    title: str,
    desc: str,
    fonts,
    accent_color,
    icon_name=None,
    badge_text=None,
    radius=16,
    show_chevron=True,
    text_max_width: int | None = None,
) -> bool:
    """Draw a rich modern card with hover lift, left accent stripe, icon, title, desc and chevron."""
    from sudoku.ui.icons import SmoothIcons

    is_hover = rect.collidepoint(mouse_pos)
    draw_rect = rect.move(0, -2) if is_hover else rect

    if is_hover:
        glow_rect = draw_rect.inflate(4, 4)
        pygame.draw.rect(
            screen,
            soft_tint(accent_color, Colors.BG_MAIN, 0.2),
            glow_rect,
            width=2,
            border_radius=radius + 2,
        )

    # Shadow
    shadow_rect = draw_rect.move(0, 4 if is_hover else 2)
    pygame.draw.rect(screen, Colors.SHADOW, shadow_rect, border_radius=radius)

    # Card background
    card_bg = Colors.BG_CARD
    pygame.draw.rect(screen, card_bg, draw_rect, border_radius=radius)

    # Border: normal or accent on hover
    border_c = accent_color if is_hover else Colors.CARD_BORDER
    border_w = 2 if is_hover else 1
    pygame.draw.rect(screen, border_c, draw_rect, width=border_w, border_radius=radius)

    # Left accent vertical bar
    bar_rect = pygame.Rect(draw_rect.left, draw_rect.top, 6, draw_rect.height)
    pygame.draw.rect(
        screen,
        accent_color,
        bar_rect,
        border_top_left_radius=radius,
        border_bottom_left_radius=radius,
    )

    # Leading icon
    cur_x = draw_rect.left + 22
    if icon_name:
        icon_size = 32
        i_surf = SmoothIcons.get(icon_name, icon_size, accent_color)
        screen.blit(i_surf, (cur_x, draw_rect.centery - icon_size // 2))
        cur_x += icon_size + 14

    # Text container
    title_surf = fonts.medium.render(title, True, Colors.FIXED_TEXT)
    desc_surf = fonts.badge.render(desc, True, Colors.STATUS_TEXT)
    if text_max_width is not None:
        title_surf = fit_surface(title_surf, text_max_width)
        desc_surf = fit_surface(desc_surf, text_max_width)

    total_text_h = title_surf.get_height() + desc_surf.get_height() + 4
    top_y = draw_rect.centery - total_text_h // 2
    screen.blit(title_surf, (cur_x, top_y))
    screen.blit(desc_surf, (cur_x, top_y + title_surf.get_height() + 4))

    # Right side: badge if any + chevron
    right_x = draw_rect.right - 18
    if show_chevron:
        ch_surf = SmoothIcons.get(
            "arrow_right", 20, accent_color if is_hover else Colors.STATUS_TEXT
        )
        screen.blit(ch_surf, (right_x - 16, draw_rect.centery - 10))

    if badge_text:
        badge_w = len(badge_text) * 9 + 20
        chevron_space = 30 if show_chevron else 6
        b_rect = pygame.Rect(right_x - chevron_space - badge_w, draw_rect.centery - 12, badge_w, 24)
        draw_badge(
            screen, b_rect, badge_text, fonts.badge, Colors.SELECTED_BG, accent_color, radius=8
        )

    return is_hover


def draw_modern_button(
    screen: pygame.Surface,
    rect: pygame.Rect,
    text: str,
    mouse_pos,
    font_to_use,
    variant="secondary",
    is_active=False,
    subtext=None,
    sub_font=None,
    radius=14,
    icon_name=None,
    icon_size=22,
    icon_color=None,
):
    from sudoku.ui.icons import SmoothIcons

    is_hover = rect.collidepoint(mouse_pos)

    if is_active:
        bg_color = Colors.BTN_ACTIVE
        border_color = Colors.BTN_ACTIVE_BORDER
        text_color = Colors.BTN_ACTIVE_TEXT
        border_w = 2
    elif variant in ("primary", "success", "warning", "danger"):
        if variant == "primary":
            bg_color = Colors.BTN_PRIMARY_HOVER if is_hover else Colors.BTN_PRIMARY
        elif variant == "success":
            bg_color = Colors.BTN_SUCCESS_HOVER if is_hover else Colors.BTN_SUCCESS
        elif variant == "warning":
            bg_color = Colors.BTN_WARNING_HOVER if is_hover else Colors.BTN_WARNING
        else:
            bg_color = Colors.BTN_DANGER_HOVER if is_hover else Colors.BTN_DANGER
        border_color = None
        text_color = Colors.BTN_VIVID_TEXT
        border_w = 0
    elif variant == "disabled":
        bg_color = Colors.NUM_DONE_BG
        border_color = Colors.CARD_BORDER
        text_color = Colors.NUM_DONE_TEXT
        border_w = 1
    else:  # secondary
        bg_color = Colors.BTN_SECONDARY_HOVER if is_hover else Colors.BTN_SECONDARY
        border_color = Colors.CARD_BORDER
        text_color = Colors.BTN_SECONDARY_TEXT
        border_w = 1

    if is_hover and variant != "disabled" and not is_active:
        border_color = Colors.SELECTED_BORDER
        border_w = 2

    # Draw shadow
    if variant != "disabled":
        shadow_offset = 3 if is_hover else 1
        shadow_rect = rect.move(0, shadow_offset)
        pygame.draw.rect(screen, Colors.SHADOW, shadow_rect, border_radius=radius)

    # Hover lift
    draw_rect = rect.move(0, -1) if is_hover else rect

    pygame.draw.rect(screen, bg_color, draw_rect, border_radius=radius)
    if border_color and border_w > 0:
        pygame.draw.rect(screen, border_color, draw_rect, width=border_w, border_radius=radius)

    # Use draw_rect for content positioning instead of rect for button internals
    # But wait, replacing rect with draw_rect for text/icon placement might break the signature if we don't update below. Let's just update `rect` variable.
    rect = draw_rect

    if icon_name and subtext and sub_font:
        icon_surf = SmoothIcons.get(icon_name, icon_size, icon_color or text_color)
        s_surf = sub_font.render(subtext, True, text_color)
        s_surf = fit_surface(s_surf, rect.width - 8, rect.height - icon_size - 8)

        total_h = icon_size + 2 + s_surf.get_height()
        start_y = rect.centery - total_h // 2

        icon_rect = icon_surf.get_rect(center=(rect.centerx, start_y + icon_size // 2))
        screen.blit(icon_surf, icon_rect)
        screen.blit(
            s_surf,
            s_surf.get_rect(
                center=(rect.centerx, start_y + icon_size + 2 + s_surf.get_height() // 2)
            ),
        )
        return rect

    elif icon_name and text:
        icon_surf = SmoothIcons.get(icon_name, icon_size, icon_color or text_color)
        t_surf = font_to_use.render(text, True, text_color)
        t_surf = fit_surface(t_surf, rect.width - icon_size - 12, rect.height - 8)
        total_w = icon_size + 8 + t_surf.get_width()
        start_x = rect.centerx - total_w // 2
        icon_rect = icon_surf.get_rect(midleft=(start_x, rect.centery))
        screen.blit(icon_surf, icon_rect)
        screen.blit(t_surf, (icon_rect.right + 8, rect.centery - t_surf.get_height() // 2))
        return rect

    elif subtext and sub_font:
        t_surf = font_to_use.render(text, True, text_color)
        s_surf = sub_font.render(subtext, True, text_color)

        # Don't restrict the large number to half height; let it take most of the space
        s_surf = fit_surface(s_surf, rect.width - 8, rect.height // 3)
        t_surf = fit_surface(t_surf, rect.width - 8, rect.height - s_surf.get_height() - 4)

        total_h = t_surf.get_height() + s_surf.get_height() - 4
        start_y = rect.centery - total_h // 2
        screen.blit(
            t_surf, t_surf.get_rect(center=(rect.centerx, start_y + t_surf.get_height() // 2))
        )
        screen.blit(
            s_surf,
            s_surf.get_rect(
                center=(rect.centerx, start_y + t_surf.get_height() - 4 + s_surf.get_height() // 2)
            ),
        )
        return rect

    elif text:
        t_surf = font_to_use.render(text, True, text_color)
        t_surf = fit_surface(t_surf, rect.width - 12, rect.height - 8)
        screen.blit(t_surf, t_surf.get_rect(center=rect.center))
        return rect

    elif icon_name:
        icon_surf = SmoothIcons.get(icon_name, icon_size, icon_color or text_color)
        screen.blit(icon_surf, icon_surf.get_rect(center=rect.center))
        return rect

    return rect
