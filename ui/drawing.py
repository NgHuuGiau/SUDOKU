"""Drawing primitives for Sudoku UI."""

import pygame

from ui.colors import Colors


def _fit_surface(
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


def draw_rounded_card(
    screen: pygame.Surface,
    rect: pygame.Rect,
    bg_color,
    border_color=None,
    border_width=1,
    radius=12,
    shadow=True,
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
    from ui.icons import SmoothIcons

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
    radius=14,
    show_chevron=True,
) -> bool:
    """Draw a rich modern card with hover lift, left accent stripe, icon, title, desc and chevron."""
    from ui.icons import SmoothIcons

    is_hover = rect.collidepoint(mouse_pos)
    draw_rect = rect.move(0, -2) if is_hover else rect

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
        icon_size = 28
        i_surf = SmoothIcons.get(icon_name, icon_size, accent_color)
        screen.blit(i_surf, (cur_x, draw_rect.centery - icon_size // 2))
        cur_x += icon_size + 14

    # Text container
    title_surf = fonts.medium.render(title, True, Colors.FIXED_TEXT)
    desc_surf = fonts.badge.render(desc, True, Colors.STATUS_TEXT)

    total_text_h = title_surf.get_height() + desc_surf.get_height() + 4
    top_y = draw_rect.centery - total_text_h // 2
    screen.blit(title_surf, (cur_x, top_y))
    screen.blit(desc_surf, (cur_x, top_y + title_surf.get_height() + 4))

    # Right side: badge if any + chevron
    right_x = draw_rect.right - 18
    if show_chevron:
        ch_surf = SmoothIcons.get(
            "arrow_right", 18, accent_color if is_hover else Colors.STATUS_TEXT
        )
        screen.blit(ch_surf, (right_x - 14, draw_rect.centery - 9))

    if badge_text:
        badge_w = len(badge_text) * 8 + 16
        b_rect = pygame.Rect(right_x - 30 - badge_w, draw_rect.centery - 11, badge_w, 22)
        draw_badge(
            screen, b_rect, badge_text, fonts.badge, Colors.SELECTED_BG, accent_color, radius=6
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
    radius=10,
    icon_name=None,
    icon_size=20,
):
    from ui.icons import SmoothIcons

    is_hover = rect.collidepoint(mouse_pos)

    if is_active:
        bg_color = Colors.BTN_ACTIVE
        border_color = Colors.BTN_ACTIVE_BORDER
        text_color = Colors.BTN_ACTIVE_TEXT
        border_w = 2
    elif variant == "primary":
        bg_color = Colors.BTN_PRIMARY_HOVER if is_hover else Colors.BTN_PRIMARY
        border_color = None
        text_color = Colors.WHITE
        border_w = 0
    elif variant == "success":
        bg_color = Colors.BTN_SUCCESS_HOVER if is_hover else Colors.BTN_SUCCESS
        border_color = None
        text_color = Colors.WHITE
        border_w = 0
    elif variant == "warning":
        bg_color = Colors.BTN_WARNING_HOVER if is_hover else Colors.BTN_WARNING
        border_color = None
        text_color = Colors.WHITE
        border_w = 0
    elif variant == "danger":
        bg_color = Colors.BTN_DANGER_HOVER if is_hover else Colors.BTN_DANGER
        border_color = None
        text_color = Colors.WHITE
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

    if variant != "disabled":
        shadow_rect = rect.move(0, 2 if not is_hover else 3)
        pygame.draw.rect(screen, Colors.SHADOW, shadow_rect, border_radius=radius)

    pygame.draw.rect(screen, bg_color, rect, border_radius=radius)
    if border_color and border_w > 0:
        pygame.draw.rect(screen, border_color, rect, width=border_w, border_radius=radius)

    if icon_name and subtext and sub_font:
        icon_surf = SmoothIcons.get(icon_name, icon_size, text_color)
        icon_rect = icon_surf.get_rect(center=(rect.centerx, rect.top + 17))
        screen.blit(icon_surf, icon_rect)
        s_surf = sub_font.render(subtext, True, text_color)
        s_surf = _fit_surface(s_surf, rect.width - 10, rect.height - icon_size - 8)
        screen.blit(s_surf, s_surf.get_rect(center=(rect.centerx, rect.bottom - 11)))
        return rect

    elif icon_name and text:
        icon_surf = SmoothIcons.get(icon_name, icon_size, text_color)
        t_surf = font_to_use.render(text, True, text_color)
        t_surf = _fit_surface(t_surf, rect.width - icon_size - 12, rect.height - 8)
        total_w = icon_size + 8 + t_surf.get_width()
        start_x = rect.centerx - total_w // 2
        icon_rect = icon_surf.get_rect(midleft=(start_x, rect.centery))
        screen.blit(icon_surf, icon_rect)
        screen.blit(t_surf, (icon_rect.right + 8, rect.centery - t_surf.get_height() // 2))
        return rect

    elif subtext and sub_font:
        t_surf = font_to_use.render(text, True, text_color)
        s_surf = sub_font.render(subtext, True, text_color)
        t_surf = _fit_surface(t_surf, rect.width - 10, rect.height // 2 - 2)
        s_surf = _fit_surface(s_surf, rect.width - 10, rect.height // 2 - 2)
        total_h = t_surf.get_height() + s_surf.get_height() + 2
        start_y = rect.centery - total_h // 2
        screen.blit(
            t_surf, t_surf.get_rect(center=(rect.centerx, start_y + t_surf.get_height() // 2))
        )
        screen.blit(
            s_surf,
            s_surf.get_rect(
                center=(rect.centerx, start_y + t_surf.get_height() + s_surf.get_height() // 2)
            ),
        )
        return rect

    elif text:
        t_surf = font_to_use.render(text, True, text_color)
        t_surf = _fit_surface(t_surf, rect.width - 12, rect.height - 8)
        screen.blit(t_surf, t_surf.get_rect(center=rect.center))
        return rect

    elif icon_name:
        icon_surf = SmoothIcons.get(icon_name, icon_size, text_color)
        screen.blit(icon_surf, icon_surf.get_rect(center=rect.center))
        return rect

    return rect
