"""Modal overlays (Pause, Win) for Sudoku UI."""
import pygame

from ui.colors import Colors
from ui.drawing import draw_modern_button, draw_rounded_card
from ui.geometry import SCREEN_HEIGHT, SCREEN_WIDTH
from ui.icons import SmoothIcons


def draw_win_modal(screen: pygame.Surface, fonts, mouse_pos, translate, state, particles) -> dict:
    overlay_rects = {"win_restart": None, "win_quit": None}

    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((15, 23, 42, 170))
    screen.blit(overlay, (0, 0))

    if particles:
        for p in particles:
            p.draw(screen)

    card_w, card_h = 460, 320
    modal_rect = pygame.Rect((SCREEN_WIDTH - card_w) // 2, (SCREEN_HEIGHT - card_h) // 2, card_w, card_h)
    draw_rounded_card(screen, modal_rect, Colors.BG_CARD, Colors.CARD_BORDER, radius=16)

    # Trophy
    trophy_surf = SmoothIcons.get('trophy', 48, Colors.GOLD)
    screen.blit(trophy_surf, trophy_surf.get_rect(center=(modal_rect.centerx, modal_rect.top + 50)))

    win_title = fonts.large.render(translate('chien_thang'), True, Colors.GOLD)
    screen.blit(win_title, win_title.get_rect(center=(modal_rect.centerx, modal_rect.top + 95)))

    sub_msg = fonts.small.render(translate("chuc_mung_thang"), True, Colors.STATUS_TEXT)
    screen.blit(sub_msg, sub_msg.get_rect(center=(modal_rect.centerx, modal_rect.top + 130)))

    mins, secs = divmod(max(0, state.final_time), 60)
    time_info = f"{translate('thoi_gian_hoan_thanh')}: {mins:02}:{secs:02}"
    time_surf = fonts.medium.render(time_info, True, Colors.FIXED_TEXT)
    screen.blit(time_surf, time_surf.get_rect(center=(modal_rect.centerx, modal_rect.top + 165)))

    # Restart & Menu buttons
    btn_w, btn_h = 180, 48
    btn_y = modal_rect.bottom - 75
    win_restart = pygame.Rect(modal_rect.centerx - btn_w - 12, btn_y, btn_w, btn_h)
    win_quit = pygame.Rect(modal_rect.centerx + 12, btn_y, btn_w, btn_h)

    draw_modern_button(screen, win_restart, translate('choi_tiep'), mouse_pos, fonts.small,
                       variant='primary', icon_name='restart', icon_size=18)
    draw_modern_button(screen, win_quit, translate('thoat_ve_menu'), mouse_pos, fonts.small,
                       variant='secondary', icon_name='home', icon_size=18)

    overlay_rects["win_restart"] = win_restart
    overlay_rects["win_quit"] = win_quit
    return overlay_rects


def draw_pause_modal(screen: pygame.Surface, fonts, mouse_pos, translate) -> dict:
    overlay_rects = {"pause_resume": None, "pause_quit": None, "pause_restart": None, "pause_save_quit": None}

    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((15, 23, 42, 180))
    screen.blit(overlay, (0, 0))

    card_w, card_h = 420, 320
    modal_rect = pygame.Rect((SCREEN_WIDTH - card_w) // 2, (SCREEN_HEIGHT - card_h) // 2, card_w, card_h)
    draw_rounded_card(screen, modal_rect, Colors.BG_CARD, Colors.CARD_BORDER, radius=16)

    # Pause icon
    pause_surf = SmoothIcons.get('pause', 36, Colors.FIXED_TEXT)
    screen.blit(pause_surf, pause_surf.get_rect(center=(modal_rect.centerx, modal_rect.top + 45)))

    pause_title = fonts.large.render(translate('tam_dung'), True, Colors.FIXED_TEXT)
    screen.blit(pause_title, pause_title.get_rect(center=(modal_rect.centerx, modal_rect.top + 90)))

    # 3 buttons: Resume, Restart, Save & Quit
    btn_w, btn_h = 120, 44
    btn_y = modal_rect.bottom - 70
    spacing = 10
    total_w = 3 * btn_w + 2 * spacing
    start_x = modal_rect.centerx - total_w // 2

    pause_resume = pygame.Rect(start_x, btn_y, btn_w, btn_h)
    pause_restart = pygame.Rect(start_x + btn_w + spacing, btn_y, btn_w, btn_h)
    pause_save_quit = pygame.Rect(start_x + 2 * (btn_w + spacing), btn_y, btn_w, btn_h)

    draw_modern_button(screen, pause_resume, translate('tiep_tuc'), mouse_pos, fonts.small,
                       variant='primary', icon_name='play', icon_size=16)
    draw_modern_button(screen, pause_restart, translate('khoi_dong_lai'), mouse_pos, fonts.small,
                       variant='warning', icon_name='restart', icon_size=16)
    draw_modern_button(screen, pause_save_quit, translate('luu_va_thoat'), mouse_pos, fonts.small,
                       variant='secondary', icon_name='save', icon_size=16)

    overlay_rects["pause_resume"] = pause_resume
    overlay_rects["pause_restart"] = pause_restart
    overlay_rects["pause_save_quit"] = pause_save_quit
    overlay_rects["pause_quit"] = pause_save_quit  # alias for backward compat
    return overlay_rects


def draw_header(screen: pygame.Surface, fonts, state, mouse_pos, translate) -> dict:
    from sounds import is_sound_enabled
    from ui.geometry import BOARD_X

    header_rect = pygame.Rect(BOARD_X, 18, SCREEN_WIDTH - BOARD_X * 2, 60)
    draw_rounded_card(screen, header_rect, Colors.BG_CARD, Colors.CARD_BORDER, radius=14)

    # 1. Logo & Title
    logo_x = header_rect.left + 20
    logo_surf = SmoothIcons.get('grid_logo', 26, Colors.BTN_PRIMARY)
    screen.blit(logo_surf, logo_surf.get_rect(midleft=(logo_x, header_rect.centery)))

    title_text = fonts.title.render("SUDOKU", True, Colors.FIXED_TEXT)
    screen.blit(title_text, (logo_x + 36, header_rect.centery - title_text.get_height() // 2))

    # 2. Difficulty badge
    diff_key = state.difficulty
    diff_name = translate(diff_key)
    star_count = {"easy": 1, "medium": 2, "hard": 3, "daily": 2}.get(diff_key, 1)

    diff_badge_rect = pygame.Rect(header_rect.left + 195, header_rect.centery - 18, 140, 36)
    pygame.draw.rect(screen, Colors.SELECTED_BG, diff_badge_rect, border_radius=18)
    pygame.draw.rect(screen, Colors.SELECTED_BORDER, diff_badge_rect, width=1, border_radius=18)

    star_start_x = diff_badge_rect.left + 14
    for s_idx in range(star_count):
        star_surf = SmoothIcons.get('star', 13, Colors.GOLD)
        screen.blit(star_surf, star_surf.get_rect(center=(star_start_x + s_idx * 14, diff_badge_rect.centery)))

    diff_surf = fonts.small.render(diff_name, True, Colors.BTN_ACTIVE_TEXT)
    diff_text_x = star_start_x + star_count * 14 + 6
    screen.blit(diff_surf, (diff_text_x, diff_badge_rect.centery - diff_surf.get_height() // 2))

    # 3. Action buttons on right side
    # Pause button
    pause_btn_rect = pygame.Rect(header_rect.right - 105, header_rect.centery - 18, 95, 36)
    pause_label = translate("tiep_tuc") if state.paused else translate("tam_dung_btn")
    pause_variant = 'warning' if state.paused else 'secondary'
    pause_icon = 'play' if state.paused else 'pause'
    draw_modern_button(screen, pause_btn_rect, pause_label, mouse_pos, fonts.small,
                       variant=pause_variant, radius=10, icon_name=pause_icon, icon_size=16)

    # Sound button (🔊 / 🔇)
    sound_rect = pygame.Rect(pause_btn_rect.left - 44, header_rect.centery - 18, 38, 36)
    sound_on = is_sound_enabled()
    sound_icon = 'sound' if sound_on else 'sound_mute'
    draw_modern_button(screen, sound_rect, "", mouse_pos, fonts.small,
                       variant='secondary', radius=10, icon_name=sound_icon, icon_size=18)

    # Theme switcher button (🎨)
    theme_rect = pygame.Rect(sound_rect.left - 44, header_rect.centery - 18, 38, 36)
    draw_modern_button(screen, theme_rect, "", mouse_pos, fonts.small,
                       variant='secondary', radius=10, icon_name='palette', icon_size=18)

    # Help button (❓)
    help_rect = pygame.Rect(theme_rect.left - 44, header_rect.centery - 18, 38, 36)
    draw_modern_button(screen, help_rect, "", mouse_pos, fonts.small,
                       variant='secondary', radius=10, icon_name='help', icon_size=18)

    # 4. Timer Box
    elapsed = state.get_elapsed_time()
    mins, secs = divmod(max(0, elapsed), 60)
    time_str = f"{mins:02}:{secs:02}"
    timer_box_w = 110
    timer_x = help_rect.left - timer_box_w - 14

    timer_bg_rect = pygame.Rect(timer_x, header_rect.centery - 18, timer_box_w, 36)
    pygame.draw.rect(screen, Colors.BTN_SECONDARY, timer_bg_rect, border_radius=10)
    pygame.draw.rect(screen, Colors.CARD_BORDER, timer_bg_rect, width=1, border_radius=10)

    clock_surf = SmoothIcons.get('clock', 18, Colors.TIMER_TEXT)
    screen.blit(clock_surf, clock_surf.get_rect(midleft=(timer_bg_rect.left + 10, header_rect.centery)))

    timer_surf = fonts.medium.render(time_str, True, Colors.TIMER_TEXT)
    screen.blit(timer_surf, (timer_bg_rect.left + 36, header_rect.centery - timer_surf.get_height() // 2))

    return {
        "pause": pause_btn_rect,
        "header_pause": pause_btn_rect,
        "header_sound": sound_rect,
        "header_theme": theme_rect,
        "header_help": help_rect,
    }


def draw_footer_helper(screen: pygame.Surface, fonts, translate) -> None:
    from ui.geometry import BOARD_X, SCREEN_HEIGHT, SCREEN_WIDTH
    helper_rect = pygame.Rect(BOARD_X, SCREEN_HEIGHT - 44, SCREEN_WIDTH - BOARD_X * 2, 32)
    pygame.draw.rect(screen, Colors.BG_CARD, helper_rect, border_radius=8)
    pygame.draw.rect(screen, Colors.CARD_BORDER, helper_rect, width=1, border_radius=8)

    txt = f"{translate('move')}  |  {translate('input')}  |  {translate('notes_shortcut')}  |  {translate('delete')}"
    help_surf = fonts.tiny.render(txt, True, Colors.STATUS_TEXT)
    screen.blit(help_surf, help_surf.get_rect(center=helper_rect.center))


def draw_help_modal(screen: pygame.Surface, fonts, mouse_pos, translate) -> dict:
    """Draw keyboard shortcut help overlay (F1). Returns overlay rects for click handling."""
    from ui.geometry import SCREEN_HEIGHT, SCREEN_WIDTH

    overlay_rects = {"help_close": None}

    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((15, 23, 42, 180))
    screen.blit(overlay, (0, 0))

    card_w, card_h = 520, 480
    modal_rect = pygame.Rect((SCREEN_WIDTH - card_w) // 2, (SCREEN_HEIGHT - card_h) // 2, card_w, card_h)
    draw_rounded_card(screen, modal_rect, Colors.BG_CARD, Colors.CARD_BORDER, radius=16)

    # Title
    title_surf = fonts.large.render(translate("keyboard_shortcuts"), True, Colors.FIXED_TEXT)
    screen.blit(title_surf, title_surf.get_rect(center=(modal_rect.centerx, modal_rect.top + 40)))

    # Shortcut list
    shortcuts = [
        ("W / ↑", translate("shortcut_move_up")),
        ("S / ↓", translate("shortcut_move_down")),
        ("A / ←", translate("shortcut_move_left")),
        ("D / →", translate("shortcut_move_right")),
        ("1 - 9", translate("shortcut_input_number")),
        ("Backspace / Del", translate("shortcut_delete")),
        ("Space / N", translate("shortcut_toggle_notes")),
        ("Ctrl + Z", translate("shortcut_undo")),
        ("Ctrl + Shift + Z / Ctrl + Y", translate("shortcut_redo")),
        ("Esc / P", translate("shortcut_pause")),
        ("F1", translate("shortcut_help")),
    ]

    y_start = modal_rect.top + 90
    line_height = 36
    key_col_x = modal_rect.left + 60
    desc_col_x = modal_rect.left + 200

    for i, (key, desc) in enumerate(shortcuts):
        y = y_start + i * line_height
        # Key
        key_surf = fonts.medium.render(key, True, Colors.GOLD)
        screen.blit(key_surf, key_surf.get_rect(midleft=(key_col_x, y)))
        # Separator
        sep_surf = fonts.medium.render("→", True, Colors.STATUS_TEXT)
        screen.blit(sep_surf, sep_surf.get_rect(center=(modal_rect.centerx, y)))
        # Description
        desc_surf = fonts.medium.render(desc, True, Colors.FIXED_TEXT)
        screen.blit(desc_surf, desc_surf.get_rect(midleft=(desc_col_x, y)))

    # Close button
    btn_w, btn_h = 120, 44
    btn_y = modal_rect.bottom - 60
    help_close = pygame.Rect(modal_rect.centerx - btn_w // 2, btn_y, btn_w, btn_h)
    draw_modern_button(screen, help_close, translate('close'), mouse_pos, fonts.small,
                       variant='primary', icon_name='check', icon_size=16)

    overlay_rects["help_close"] = help_close
    return overlay_rects
