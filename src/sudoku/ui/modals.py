"""Modal overlays (Pause, Win) for Sudoku UI."""

from functools import lru_cache
from typing import Any, cast

import pygame

from sudoku.ui.colors import Colors
from sudoku.ui.drawing import draw_badge, draw_modern_button, draw_rounded_card, fit_surface
from sudoku.ui.geometry import SCREEN_HEIGHT, SCREEN_WIDTH
from sudoku.ui.icons import SmoothIcons


@lru_cache(maxsize=6)
def _overlay_surface(size: tuple[int, int], alpha: int) -> pygame.Surface:
    surface = pygame.Surface(size, pygame.SRCALPHA)
    surface.fill((15, 23, 42, alpha))
    return surface


def _draw_overlay(screen: pygame.Surface, alpha: int) -> None:
    screen.blit(_overlay_surface(screen.get_size(), alpha), (0, 0))


def draw_win_modal(
    screen: pygame.Surface, fonts, mouse_pos, translate, state, particles
) -> dict[str, pygame.Rect | None]:
    overlay_rects: dict[str, pygame.Rect | None] = {"win_restart": None, "win_quit": None}

    _draw_overlay(screen, 170)

    if particles:
        for p in particles:
            p.draw(screen)

    card_w, card_h = 460, 320
    modal_rect = pygame.Rect(
        (SCREEN_WIDTH - card_w) // 2, (SCREEN_HEIGHT - card_h) // 2, card_w, card_h
    )
    draw_rounded_card(screen, modal_rect, Colors.BG_CARD, Colors.CARD_BORDER, radius=16)

    # Trophy
    trophy_surf = SmoothIcons.get("trophy", 48, Colors.GOLD)
    screen.blit(trophy_surf, trophy_surf.get_rect(center=(modal_rect.centerx, modal_rect.top + 50)))

    win_title = fonts.large.render(translate("chien_thang"), True, Colors.GOLD)
    screen.blit(win_title, win_title.get_rect(center=(modal_rect.centerx, modal_rect.top + 95)))

    sub_msg = fonts.small.render(translate("chuc_mung_thang"), True, Colors.STATUS_TEXT)
    screen.blit(sub_msg, sub_msg.get_rect(center=(modal_rect.centerx, modal_rect.top + 130)))

    mins, secs = divmod(max(0, state.final_time), 60)
    time_info = f"{translate('thoi_gian_hoan_thanh')}: {mins:02}:{secs:02}"
    time_surf = fit_surface(fonts.small.render(time_info, True, Colors.FIXED_TEXT), card_w - 60, 30)
    screen.blit(time_surf, time_surf.get_rect(center=(modal_rect.centerx, modal_rect.top + 160)))

    diff_surf = fonts.small.render(translate(state.difficulty), True, Colors.STATUS_TEXT)
    screen.blit(diff_surf, diff_surf.get_rect(center=(modal_rect.centerx, modal_rect.top + 186)))

    from sudoku.persistence import load_best_times

    best = load_best_times().get(state.difficulty)
    if best is not None:
        mins_b, secs_b = divmod(max(0, best), 60)
        best_surf = fonts.small.render(
            f"{translate('best_label')}: {mins_b:02}:{secs_b:02}", True, Colors.STATUS_TEXT
        )
        screen.blit(
            best_surf, best_surf.get_rect(center=(modal_rect.centerx, modal_rect.top + 206))
        )
        if state.final_time == best:
            badge_rect = pygame.Rect(modal_rect.centerx - 70, modal_rect.top + 220, 140, 24)
            draw_badge(
                screen,
                badge_rect,
                translate("ky_luc_moi"),
                fonts.badge,
                Colors.SELECTED_BG,
                Colors.ICON_VICTORY,
                radius=12,
            )

    # Restart & Menu buttons
    btn_w, btn_h = 180, 44
    btn_y = modal_rect.top + 256
    win_restart = pygame.Rect(modal_rect.centerx - btn_w - 12, btn_y, btn_w, btn_h)
    win_quit = pygame.Rect(modal_rect.centerx + 12, btn_y, btn_w, btn_h)

    draw_modern_button(
        screen,
        win_restart,
        translate("choi_tiep"),
        mouse_pos,
        fonts.small,
        variant="primary",
        icon_name="restart",
        icon_size=20,
    )
    draw_modern_button(
        screen,
        win_quit,
        translate("thoat_ve_menu"),
        mouse_pos,
        fonts.small,
        variant="secondary",
        icon_name="home",
        icon_size=20,
    )

    overlay_rects["win_restart"] = win_restart
    overlay_rects["win_quit"] = win_quit
    return overlay_rects


def draw_pause_modal(
    screen: pygame.Surface, fonts, mouse_pos, translate, save_failed: bool = False
) -> dict[str, pygame.Rect | None]:
    overlay_rects: dict[str, pygame.Rect | None] = {
        "pause_resume": None,
        "pause_quit": None,
        "pause_restart": None,
        "pause_save_quit": None,
    }

    _draw_overlay(screen, 180)

    card_w, card_h = 440, 320
    modal_rect = pygame.Rect(
        (SCREEN_WIDTH - card_w) // 2, (SCREEN_HEIGHT - card_h) // 2, card_w, card_h
    )
    draw_rounded_card(screen, modal_rect, Colors.BG_CARD, Colors.CARD_BORDER, radius=16)

    # Pause icon
    pause_surf = SmoothIcons.get("pause", 36, Colors.FIXED_TEXT)
    screen.blit(pause_surf, pause_surf.get_rect(center=(modal_rect.centerx, modal_rect.top + 45)))

    pause_title = fonts.large.render(translate("tam_dung"), True, Colors.FIXED_TEXT)
    screen.blit(pause_title, pause_title.get_rect(center=(modal_rect.centerx, modal_rect.top + 90)))
    if save_failed:
        # Two centered lines: the single-line warning overflows the card.
        warning_text = translate("save_failed")
        words = warning_text.split(" ")
        mid = len(warning_text) // 2
        cut = min(
            range(len(words)),
            key=lambda i: abs(len(" ".join(words[: i + 1])) - mid),
        )
        for offset, line_text in enumerate(
            (" ".join(words[: cut + 1]), " ".join(words[cut + 1 :]))
        ):
            if not line_text:
                continue
            warning = fonts.tiny.render(line_text, True, Colors.ERROR_TEXT)
            screen.blit(
                warning,
                warning.get_rect(center=(modal_rect.centerx, modal_rect.top + 138 + offset * 20)),
            )

    # 3 buttons: Resume, Restart, Save & Quit
    btn_w, btn_h = 132, 46
    btn_y = modal_rect.bottom - 70
    spacing = 8
    total_w = 3 * btn_w + 2 * spacing
    start_x = modal_rect.centerx - total_w // 2

    pause_resume = pygame.Rect(start_x, btn_y, btn_w, btn_h)
    pause_restart = pygame.Rect(start_x + btn_w + spacing, btn_y, btn_w, btn_h)
    pause_save_quit = pygame.Rect(start_x + 2 * (btn_w + spacing), btn_y, btn_w, btn_h)

    draw_modern_button(
        screen,
        pause_resume,
        translate("tiep_tuc"),
        mouse_pos,
        fonts.small,
        variant="primary",
        icon_name="play",
        icon_size=20,
    )
    draw_modern_button(
        screen,
        pause_restart,
        translate("choi_tiep"),
        mouse_pos,
        fonts.small,
        variant="warning",
        icon_name="restart",
        icon_size=20,
    )
    draw_modern_button(
        screen,
        pause_save_quit,
        translate("luu_va_thoat"),
        mouse_pos,
        fonts.small,
        variant="secondary",
        icon_name="save",
        icon_size=20,
    )

    overlay_rects["pause_resume"] = pause_resume
    overlay_rects["pause_restart"] = pause_restart
    overlay_rects["pause_save_quit"] = pause_save_quit
    overlay_rects["pause_quit"] = pause_save_quit  # alias for backward compat
    return overlay_rects


def draw_header(screen: pygame.Surface, fonts, state, mouse_pos, translate) -> dict:
    from sudoku.sounds import is_sound_enabled
    from sudoku.ui.geometry import BOARD_X

    header_rect = pygame.Rect(BOARD_X, 18, SCREEN_WIDTH - BOARD_X * 2, 60)
    draw_rounded_card(screen, header_rect, Colors.HEADER_BG, Colors.CARD_BORDER, radius=20)

    # 1. Logo & Title (header uses medium so it never collides with badge)
    logo_x = header_rect.left + 20
    logo_surf = SmoothIcons.get("grid_logo", 32, Colors.BTN_PRIMARY)
    screen.blit(logo_surf, logo_surf.get_rect(midleft=(logo_x, header_rect.centery)))

    title_text = fonts.medium.render("SUDOKU", True, Colors.FIXED_TEXT)
    screen.blit(title_text, (logo_x + 40, header_rect.centery - title_text.get_height() // 2))

    # 2. Difficulty badge (auto-sized to text, no more huge empty pill)
    diff_key = state.difficulty
    diff_name = translate(diff_key)
    star_count = {"easy": 1, "medium": 2, "hard": 3, "daily": 2}.get(diff_key, 1)

    _diff_surf = fonts.badge.render(diff_name, True, Colors.BTN_ACTIVE_TEXT)
    diff_badge_w = star_count * 18 + _diff_surf.get_width() + 40
    diff_badge_rect = pygame.Rect(
        header_rect.left + 212, header_rect.centery - 16, diff_badge_w, 32
    )
    pygame.draw.rect(screen, Colors.SELECTED_BG, diff_badge_rect, border_radius=16)
    pygame.draw.rect(screen, Colors.SELECTED_BORDER, diff_badge_rect, width=1, border_radius=16)

    star_start_x = diff_badge_rect.left + 14
    for s_idx in range(star_count):
        star_surf = SmoothIcons.get("star", 15, Colors.GOLD)
        screen.blit(
            star_surf,
            star_surf.get_rect(center=(star_start_x + s_idx * 18, diff_badge_rect.centery)),
        )

    diff_text_x = star_start_x + star_count * 18 + 4
    diff_surf = fit_surface(
        _diff_surf,
        diff_badge_rect.right - diff_text_x - 10,
    )
    screen.blit(diff_surf, (diff_text_x, diff_badge_rect.centery - diff_surf.get_height() // 2))

    # 3. Action buttons on right side
    # Pause button (wide enough for "Tạm dừng" + icon without shrinking)
    pause_btn_rect = pygame.Rect(header_rect.right - 150, header_rect.centery - 19, 140, 38)
    pause_label = translate("tiep_tuc") if state.paused else translate("tam_dung_btn")
    pause_variant = "warning" if state.paused else "secondary"
    pause_icon = "play" if state.paused else "pause"
    draw_modern_button(
        screen,
        pause_btn_rect,
        pause_label,
        mouse_pos,
        fonts.small,
        variant=pause_variant,
        icon_name=pause_icon,
        icon_size=20,
        icon_color=Colors.ICON_PAUSE,
    )

    # Sound button (🔊 / 🔇)
    sound_rect = pygame.Rect(pause_btn_rect.left - 48, header_rect.centery - 19, 42, 38)
    sound_on = is_sound_enabled()
    sound_icon = "sound" if sound_on else "sound_mute"
    draw_modern_button(
        screen,
        sound_rect,
        "",
        mouse_pos,
        fonts.small,
        variant="secondary",
        icon_name=sound_icon,
        icon_size=22,
        icon_color=Colors.ICON_SOUND,
    )

    # Theme switcher button (🎨)
    theme_rect = pygame.Rect(sound_rect.left - 48, header_rect.centery - 19, 42, 38)
    draw_modern_button(
        screen,
        theme_rect,
        "",
        mouse_pos,
        fonts.small,
        variant="secondary",
        icon_name="palette",
        icon_size=22,
        icon_color=Colors.ICON_THEME,
    )

    # Help button (❓)
    help_rect = pygame.Rect(theme_rect.left - 48, header_rect.centery - 19, 42, 38)
    draw_modern_button(
        screen,
        help_rect,
        "",
        mouse_pos,
        fonts.small,
        variant="secondary",
        icon_name="help",
        icon_size=22,
        icon_color=Colors.ICON_SETTINGS,
    )

    # 4. Timer Box
    elapsed = state.get_elapsed_time()
    mins, secs = divmod(max(0, elapsed), 60)
    time_str = f"{mins:02}:{secs:02}"
    timer_box_w = 128
    timer_x = help_rect.left - timer_box_w - 14

    timer_bg_rect = pygame.Rect(timer_x, header_rect.centery - 19, timer_box_w, 38)
    pygame.draw.rect(screen, Colors.BTN_ACTIVE, timer_bg_rect, border_radius=12)
    pygame.draw.rect(screen, Colors.BTN_ACTIVE_BORDER, timer_bg_rect, width=1, border_radius=12)

    clock_surf = SmoothIcons.get("clock", 22, Colors.TIMER_TEXT)
    screen.blit(
        clock_surf, clock_surf.get_rect(midleft=(timer_bg_rect.left + 10, header_rect.centery))
    )

    timer_surf = fonts.small.render(time_str, True, Colors.TIMER_TEXT)
    screen.blit(
        timer_surf, (timer_bg_rect.left + 38, header_rect.centery - timer_surf.get_height() // 2)
    )

    return {
        "header_pause": pause_btn_rect,
        "header_sound": sound_rect,
        "header_theme": theme_rect,
        "header_help": help_rect,
    }


def draw_footer_helper(screen: pygame.Surface, fonts, translate, save_failed: bool = False) -> None:
    from sudoku.ui.geometry import BOARD_SIZE, BOARD_X, SCREEN_HEIGHT

    # Board width only: a full-width bar would cover the sidebar session buttons.
    helper_rect = pygame.Rect(BOARD_X, SCREEN_HEIGHT - 44, BOARD_SIZE, 32)
    pygame.draw.rect(screen, Colors.BG_CARD, helper_rect, border_radius=12)
    pygame.draw.rect(screen, Colors.CARD_BORDER, helper_rect, width=1, border_radius=12)

    txt = (
        translate("save_failed")
        if save_failed
        else f"{translate('move')}  |  {translate('input')}  |  {translate('notes_shortcut')}  |  {translate('delete')}"
    )
    color = Colors.ERROR_TEXT if save_failed else Colors.STATUS_TEXT
    help_surf = fonts.tiny.render(txt, True, color)
    screen.blit(help_surf, help_surf.get_rect(center=helper_rect.center))


def draw_help_modal(screen: pygame.Surface, fonts, mouse_pos, translate) -> dict:
    """Draw keyboard shortcut help overlay (F1). Returns overlay rects for click handling."""
    from sudoku.ui.geometry import SCREEN_HEIGHT, SCREEN_WIDTH

    overlay_rects: dict[str, pygame.Rect | None] = {"help_close": None}

    _draw_overlay(screen, 180)

    card_w, card_h = 640, 520
    modal_rect = pygame.Rect(
        (SCREEN_WIDTH - card_w) // 2, (SCREEN_HEIGHT - card_h) // 2, card_w, card_h
    )
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

    y_start = modal_rect.top + 80
    line_height = 30
    key_col_x = modal_rect.left + 32
    desc_col_x = modal_rect.centerx + 30

    for i, (key, desc) in enumerate(shortcuts):
        y = y_start + i * line_height
        # Key
        key_surf = fit_surface(
            fonts.small.render(key, True, Colors.GOLD), modal_rect.width // 2 - 64, line_height
        )
        screen.blit(key_surf, key_surf.get_rect(midleft=(key_col_x, y)))
        # Separator
        sep_surf = fonts.small.render("→", True, Colors.STATUS_TEXT)
        screen.blit(sep_surf, sep_surf.get_rect(center=(modal_rect.centerx, y)))
        # Description
        desc_surf = fit_surface(
            fonts.small.render(desc, True, Colors.FIXED_TEXT),
            modal_rect.width // 2 - 64,
            line_height,
        )
        screen.blit(desc_surf, desc_surf.get_rect(midleft=(desc_col_x, y)))

    # Close button
    btn_w, btn_h = 120, 44
    btn_y = modal_rect.bottom - 60
    help_close = pygame.Rect(modal_rect.centerx - btn_w // 2, btn_y, btn_w, btn_h)
    draw_modern_button(
        screen,
        help_close,
        translate("close"),
        mouse_pos,
        fonts.small,
        variant="primary",
        icon_name="check",
        icon_size=16,
    )

    overlay_rects["help_close"] = help_close
    return overlay_rects


def draw_leaderboard_modal(
    screen: pygame.Surface,
    fonts,
    mouse_pos,
    translate,
    active_diff="medium",
    leaderboard_data=None,
) -> dict:
    """Draw high scores leaderboard modal. Returns interactive rects."""
    if leaderboard_data is None:
        from sudoku.persistence import get_leaderboard

        leaderboard = get_leaderboard()
    else:
        leaderboard = leaderboard_data

    _draw_overlay(screen, 190)

    card_w, card_h = 560, 520
    modal_rect = pygame.Rect(
        (SCREEN_WIDTH - card_w) // 2, (SCREEN_HEIGHT - card_h) // 2, card_w, card_h
    )
    draw_rounded_card(screen, modal_rect, Colors.BG_CARD, Colors.CARD_BORDER, radius=16)

    # Crown icon & title
    cr_icon = SmoothIcons.get("crown", 32, Colors.GOLD)
    screen.blit(cr_icon, cr_icon.get_rect(center=(modal_rect.centerx, modal_rect.top + 36)))

    title_surf = fonts.large.render(translate("leaderboard"), True, Colors.FIXED_TEXT)
    screen.blit(title_surf, title_surf.get_rect(center=(modal_rect.centerx, modal_rect.top + 72)))

    # Difficulty tabs (daily gets a wider tab: its label is the longest)
    diff_tabs = [
        ("easy", translate("de"), 70),
        ("medium", translate("trung_binh"), 92),
        ("hard", translate("kho"), 70),
        ("daily", translate("daily_challenge"), 150),
        ("custom", translate("custom"), 92),
    ]
    tab_h = 32
    tab_gap = 6
    tab_start_x = modal_rect.centerx - (sum(w for _, _, w in diff_tabs) + tab_gap * 4) // 2
    tab_y = modal_rect.top + 104

    overlay_rects: dict[str, pygame.Rect | None] = {"leaderboard_close": None}
    cursor_x = tab_start_x
    for d_key, d_name, tab_w in diff_tabs:
        t_rect = pygame.Rect(cursor_x, tab_y, tab_w, tab_h)
        cursor_x += tab_w + tab_gap
        is_sel = d_key == active_diff
        draw_modern_button(
            screen,
            t_rect,
            d_name,
            mouse_pos,
            fonts.badge,
            variant="secondary",
            is_active=is_sel,
            radius=6,
        )
        overlay_rects[f"tab_{d_key}"] = t_rect

    # Table Header
    th_y = tab_y + 44
    th_bg = pygame.Rect(modal_rect.left + 30, th_y, card_w - 60, 28)
    pygame.draw.rect(screen, Colors.SELECTED_BG, th_bg, border_radius=6)

    screen.blit(
        fonts.badge.render(translate("rank"), True, Colors.STATUS_TEXT), (th_bg.left + 16, th_y + 6)
    )
    screen.blit(
        fonts.badge.render(translate("name"), True, Colors.STATUS_TEXT), (th_bg.left + 80, th_y + 6)
    )
    screen.blit(
        fonts.badge.render(translate("time"), True, Colors.STATUS_TEXT),
        (th_bg.right - 180, th_y + 6),
    )
    screen.blit(
        fonts.badge.render(translate("date"), True, Colors.STATUS_TEXT),
        (th_bg.right - 90, th_y + 6),
    )

    # Entries list
    entries = cast(Any, leaderboard).get(active_diff, [])[:10]
    row_y = th_y + 34
    row_h = 28
    if not entries:
        no_data = fonts.small.render(translate("no_records"), True, Colors.STATUS_TEXT)
        screen.blit(no_data, no_data.get_rect(center=(modal_rect.centerx, row_y + 50)))
    else:
        for i, entry in enumerate(entries):
            cur_y = row_y + i * row_h
            # Rank with medal color for top 3
            rank_color = (
                Colors.GOLD
                if i == 0
                else (
                    (200, 200, 210)
                    if i == 1
                    else ((205, 127, 50) if i == 2 else Colors.STATUS_TEXT)
                )
            )
            rank_surf = fonts.badge.render(f"#{i + 1}", True, rank_color)
            screen.blit(rank_surf, (th_bg.left + 18, cur_y + 4))

            # Name
            name_surf = fonts.badge.render(
                entry.get("name", "Player")[:14], True, Colors.FIXED_TEXT
            )
            screen.blit(name_surf, (th_bg.left + 80, cur_y + 4))

            # Time
            t_sec = entry.get("time", 0)
            mins, secs = divmod(max(0, t_sec), 60)
            time_surf = fonts.badge.render(
                f"{mins:02}:{secs:02}", True, Colors.GOLD if i == 0 else Colors.FIXED_TEXT
            )
            screen.blit(time_surf, (th_bg.right - 180, cur_y + 4))

            # Date
            d_str = entry.get("date", "")[:10]
            date_surf = fonts.tiny.render(d_str, True, Colors.STATUS_TEXT)
            screen.blit(date_surf, (th_bg.right - 90, cur_y + 5))

    # Close button
    btn_w, btn_h = 120, 42
    btn_y = modal_rect.bottom - 54
    lb_close = pygame.Rect(modal_rect.centerx - btn_w // 2, btn_y, btn_w, btn_h)
    draw_modern_button(
        screen,
        lb_close,
        translate("close"),
        mouse_pos,
        fonts.small,
        variant="primary",
        icon_name="check",
        icon_size=16,
    )

    overlay_rects["leaderboard_close"] = lb_close
    return overlay_rects


def draw_text_input_modal(
    screen: pygame.Surface,
    fonts,
    mouse_pos,
    translate,
    title: str,
    prompt: str,
    value: str,
    error: str | None = None,
) -> dict:
    """Draw an in-game text input dialog. Returns clickable rects."""
    overlay_rects: dict[str, pygame.Rect | None] = {"text_ok": None, "text_cancel": None}

    _draw_overlay(screen, 190)

    card_w, card_h = 560, 320
    modal_rect = pygame.Rect(
        (SCREEN_WIDTH - card_w) // 2, (SCREEN_HEIGHT - card_h) // 2, card_w, card_h
    )
    draw_rounded_card(screen, modal_rect, Colors.BG_CARD, Colors.CARD_BORDER, radius=16)

    title_surf = fonts.large.render(title, True, Colors.FIXED_TEXT)
    screen.blit(title_surf, title_surf.get_rect(center=(modal_rect.centerx, modal_rect.top + 44)))

    prompt_surf = fit_surface(fonts.small.render(prompt, True, Colors.STATUS_TEXT), card_w - 80, 28)
    screen.blit(prompt_surf, prompt_surf.get_rect(center=(modal_rect.centerx, modal_rect.top + 92)))

    input_rect = pygame.Rect(modal_rect.left + 40, modal_rect.top + 116, card_w - 80, 46)
    pygame.draw.rect(screen, Colors.BTN_SECONDARY, input_rect, border_radius=10)
    pygame.draw.rect(screen, Colors.SELECTED_BORDER, input_rect, width=2, border_radius=10)

    shown = f"{value}_" if len(value) < 60 else f"…{value[-59:]}_"
    value_surf = fit_surface(
        fonts.medium.render(shown, True, Colors.FIXED_TEXT), input_rect.width - 24, 30
    )
    screen.blit(value_surf, value_surf.get_rect(midleft=(input_rect.left + 12, input_rect.centery)))

    btn_w, btn_h = 150, 44
    btn_y = modal_rect.bottom - 62
    if error:
        error_surf = fit_surface(fonts.tiny.render(error, True, Colors.ERROR_TEXT), card_w - 80, 24)
        screen.blit(error_surf, error_surf.get_rect(center=(modal_rect.centerx, btn_y - 22)))
    text_ok = pygame.Rect(modal_rect.centerx - btn_w - 10, btn_y, btn_w, btn_h)
    text_cancel = pygame.Rect(modal_rect.centerx + 10, btn_y, btn_w, btn_h)
    draw_modern_button(screen, text_ok, translate("ok"), mouse_pos, fonts.small, variant="primary")
    draw_modern_button(
        screen, text_cancel, translate("cancel"), mouse_pos, fonts.small, variant="secondary"
    )

    overlay_rects["text_ok"] = text_ok
    overlay_rects["text_cancel"] = text_cancel
    return overlay_rects


