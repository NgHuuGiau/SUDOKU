"""Drawing primitives for Sudoku UI."""
import pygame
from ui.colors import Colors


def draw_rounded_card(screen: pygame.Surface, rect: pygame.Rect, bg_color, border_color=None, border_width=1, radius=12, shadow=True):
    if shadow:
        shadow_rect = rect.move(0, 3)
        pygame.draw.rect(screen, Colors.SHADOW, shadow_rect, border_radius=radius)
    pygame.draw.rect(screen, bg_color, rect, border_radius=radius)
    if border_color and border_width > 0:
        pygame.draw.rect(screen, border_color, rect, width=border_width, border_radius=radius)


def draw_modern_button(screen: pygame.Surface, rect: pygame.Rect, text: str, mouse_pos, font_to_use,
                       variant='secondary', is_active=False, subtext=None, sub_font=None, radius=10, icon_name=None, icon_size=20):
    from ui.icons import SmoothIcons
    is_hover = rect.collidepoint(mouse_pos)

    if is_active:
        bg_color = Colors.BTN_ACTIVE
        border_color = Colors.BTN_ACTIVE_BORDER
        text_color = Colors.BTN_ACTIVE_TEXT
        border_w = 2
    elif variant == 'primary':
        bg_color = Colors.BTN_PRIMARY_HOVER if is_hover else Colors.BTN_PRIMARY
        border_color = None
        text_color = Colors.WHITE
        border_w = 0
    elif variant == 'success':
        bg_color = Colors.BTN_SUCCESS_HOVER if is_hover else Colors.BTN_SUCCESS
        border_color = None
        text_color = Colors.WHITE
        border_w = 0
    elif variant == 'warning':
        bg_color = Colors.BTN_WARNING_HOVER if is_hover else Colors.BTN_WARNING
        border_color = None
        text_color = Colors.WHITE
        border_w = 0
    elif variant == 'danger':
        bg_color = Colors.BTN_DANGER_HOVER if is_hover else Colors.BTN_DANGER
        border_color = None
        text_color = Colors.WHITE
        border_w = 0
    elif variant == 'disabled':
        bg_color = Colors.NUM_DONE_BG
        border_color = Colors.CARD_BORDER
        text_color = Colors.NUM_DONE_TEXT
        border_w = 1
    else:  # secondary
        bg_color = Colors.BTN_SECONDARY_HOVER if is_hover else Colors.BTN_SECONDARY
        border_color = Colors.CARD_BORDER
        text_color = Colors.BTN_SECONDARY_TEXT
        border_w = 1

    if variant != 'disabled':
        shadow_rect = rect.move(0, 2 if not is_hover else 3)
        pygame.draw.rect(screen, Colors.SHADOW, shadow_rect, border_radius=radius)

    pygame.draw.rect(screen, bg_color, rect, border_radius=radius)
    if border_color and border_w > 0:
        pygame.draw.rect(screen, border_color, rect, width=border_w, border_radius=radius)

    if icon_name and subtext and sub_font:
        icon_surf = SmoothIcons.get(icon_name, icon_size, text_color)
        icon_rect = icon_surf.get_rect(center=(rect.centerx, rect.top + 20))
        screen.blit(icon_surf, icon_rect)
        s_surf = sub_font.render(subtext, True, text_color)
        screen.blit(s_surf, s_surf.get_rect(center=(rect.centerx, rect.bottom - 13)))
        return rect

    elif icon_name and text:
        icon_surf = SmoothIcons.get(icon_name, icon_size, text_color)
        t_surf = font_to_use.render(text, True, text_color)
        total_w = icon_size + 8 + t_surf.get_width()
        start_x = rect.centerx - total_w // 2
        icon_rect = icon_surf.get_rect(midleft=(start_x, rect.centery))
        screen.blit(icon_surf, icon_rect)
        screen.blit(t_surf, (icon_rect.right + 8, rect.centery - t_surf.get_height() // 2))
        return rect

    elif subtext and sub_font:
        t_surf = font_to_use.render(text, True, text_color)
        s_surf = sub_font.render(subtext, True, text_color)
        total_h = t_surf.get_height() + s_surf.get_height() + 2
        start_y = rect.centery - total_h // 2
        screen.blit(t_surf, t_surf.get_rect(center=(rect.centerx, start_y + t_surf.get_height() // 2)))
        screen.blit(s_surf, s_surf.get_rect(center=(rect.centerx, start_y + t_surf.get_height() + s_surf.get_height() // 2)))
        return rect

    elif text:
        t_surf = font_to_use.render(text, True, text_color)
        screen.blit(t_surf, t_surf.get_rect(center=rect.center))
        return rect

    elif icon_name:
        icon_surf = SmoothIcons.get(icon_name, icon_size, text_color)
        screen.blit(icon_surf, icon_surf.get_rect(center=rect.center))
        return rect

    return rect