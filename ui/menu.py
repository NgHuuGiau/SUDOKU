"""Modern Pygame-based Menu for Sudoku UI."""

from datetime import datetime, timezone

import pygame

from config import (
    menu_text,
)
from persistence import (
    get_daily_stats,
    has_save_file,
    load_best_times,
    load_game_state,
)
from sounds import is_sound_enabled
from ui.colors import Colors, get_theme_manager
from ui.drawing import draw_badge, draw_interactive_card, draw_modern_button, draw_rounded_card
from ui.geometry import SCREEN_HEIGHT, SCREEN_WIDTH
from ui.icons import SmoothIcons
from ui.screen import enable_high_dpi


def _format_time(seconds: int) -> str:
    mins, secs = divmod(max(0, seconds), 60)
    return f"{mins:02}:{secs:02}"


def draw_menu_view(
    screen: pygame.Surface,
    fonts,
    mouse_pos: tuple[int, int],
    custom_cells: int = 40,
) -> dict:
    """Render the full modern Sudoku main menu in Pygame.

    Returns a dictionary of interactive Rects for click/hover handling.
    """
    theme_mgr = get_theme_manager()
    best_times = load_best_times()
    daily_stats = get_daily_stats()
    save_exists = has_save_file()

    # Fill background
    screen.fill(Colors.BG_MAIN)

    menu_rects: dict[str, pygame.Rect | None] = {
        "resume": None,
        "daily": None,
        "easy": None,
        "medium": None,
        "hard": None,
        "custom": None,
        "custom_dec": None,
        "custom_inc": None,
        "theme": None,
        "sound": None,
        "lang": None,
        "stats": None,
        "help": None,
        "quit": None,
    }

    # ==================== 1. TOP BAR ====================
    top_y = 16
    bar_h = 42

    # Left: Game branding
    logo_icon = SmoothIcons.get("grid_logo", 26, Colors.BTN_PRIMARY)
    screen.blit(logo_icon, (24, top_y + (bar_h - 26) // 2))

    title_surf = fonts.title.render("SUDOKU MASTER", True, Colors.FIXED_TEXT)
    screen.blit(title_surf, (58, top_y + (bar_h - title_surf.get_height()) // 2))

    badge_rect = pygame.Rect(58 + title_surf.get_width() + 10, top_y + 11, 48, 20)
    draw_badge(
        screen, badge_rect, "v2.0", fonts.badge, Colors.SELECTED_BG, Colors.BTN_PRIMARY, radius=5
    )

    # Right: Quick action buttons
    btn_size = 38
    btn_gap = 8
    cur_right = SCREEN_WIDTH - 24

    # Help button
    help_rect = pygame.Rect(cur_right - btn_size, top_y + 2, btn_size, btn_size)
    draw_modern_button(
        screen,
        help_rect,
        "",
        mouse_pos,
        fonts.badge,
        variant="secondary",
        icon_name="help",
        icon_size=18,
        radius=8,
    )
    menu_rects["help"] = help_rect
    cur_right -= btn_size + btn_gap

    # Leaderboard / Stats button
    stats_rect = pygame.Rect(cur_right - btn_size, top_y + 2, btn_size, btn_size)
    draw_modern_button(
        screen,
        stats_rect,
        "",
        mouse_pos,
        fonts.badge,
        variant="secondary",
        icon_name="crown",
        icon_size=18,
        radius=8,
    )
    menu_rects["stats"] = stats_rect
    cur_right -= btn_size + btn_gap

    # Sound toggle button
    sound_active = is_sound_enabled()
    sound_icon = "sound" if sound_active else "sound_mute"
    sound_rect = pygame.Rect(cur_right - btn_size, top_y + 2, btn_size, btn_size)
    draw_modern_button(
        screen,
        sound_rect,
        "",
        mouse_pos,
        fonts.badge,
        variant="secondary",
        is_active=sound_active,
        icon_name=sound_icon,
        icon_size=18,
        radius=8,
    )
    menu_rects["sound"] = sound_rect
    cur_right -= btn_size + btn_gap

    # Theme toggle button
    theme_btn_w = 110
    theme_rect = pygame.Rect(cur_right - theme_btn_w, top_y + 2, theme_btn_w, btn_size)
    draw_modern_button(
        screen,
        theme_rect,
        f"{theme_mgr.theme_icon} {theme_mgr.theme_name[:8]}",
        mouse_pos,
        fonts.badge,
        variant="secondary",
        radius=8,
    )
    menu_rects["theme"] = theme_rect
    cur_right -= theme_btn_w + btn_gap

    # Language toggle button
    lang_btn_w = 76
    lang_rect = pygame.Rect(cur_right - lang_btn_w, top_y + 2, lang_btn_w, btn_size)
    draw_modern_button(
        screen,
        lang_rect,
        menu_text("ngon_ngu_btn"),
        mouse_pos,
        fonts.badge,
        variant="secondary",
        icon_name="globe",
        icon_size=16,
        radius=8,
    )
    menu_rects["lang"] = lang_rect

    # ==================== 2. HERO CARD ====================
    hero_w = 640
    hero_h = 76
    hero_x = (SCREEN_WIDTH - hero_w) // 2
    hero_y = 66

    hero_rect = pygame.Rect(hero_x, hero_y, hero_w, hero_h)
    draw_rounded_card(screen, hero_rect, Colors.BG_CARD, Colors.CARD_BORDER, radius=14)

    # Hero title
    hero_title = fonts.hero.render("SUDOKU", True, Colors.FIXED_TEXT)
    screen.blit(hero_title, (hero_x + 24, hero_y + 12))

    # Hero subtitle
    hero_sub = fonts.badge.render(menu_text("thu_thach"), True, Colors.STATUS_TEXT)
    screen.blit(hero_sub, (hero_x + 24, hero_y + 44))

    # Streak badge on the right of hero card
    streak_val = daily_stats.get("streak", 0)
    streak_txt = f"{streak_val} ngày" if menu_text("easy") == "Dễ" else f"{streak_val} days"
    streak_w = 120
    streak_rect = pygame.Rect(hero_rect.right - streak_w - 20, hero_y + 22, streak_w, 32)
    draw_badge(
        screen,
        streak_rect,
        streak_txt,
        fonts.badge,
        Colors.SELECTED_BG,
        Colors.GOLD,
        icon_name="flame",
        icon_size=16,
        radius=16,
    )

    # ==================== 3. SECTION HEADING ====================
    sec_y = hero_rect.bottom + 12
    sec_title = fonts.badge.render(menu_text("chon_do_kho").upper(), True, Colors.STATUS_TEXT)
    screen.blit(sec_title, (hero_x + 4, sec_y))

    # ==================== 4. CARDS STACK ====================
    card_w = hero_w
    card_h = 58
    card_gap = 9
    cur_y = sec_y + 22

    # A. Resume Game Card (if save exists)
    if save_exists:
        resume_rect = pygame.Rect(hero_x, cur_y, card_w, card_h)
        saved = load_game_state()
        if saved:
            diff_label = {
                "easy": menu_text("de"),
                "medium": menu_text("trung_binh"),
                "hard": menu_text("kho"),
            }.get(saved.difficulty, saved.difficulty)
            elapsed = saved.get_elapsed_time()
            time_str = _format_time(elapsed)
            desc_str = f"{diff_label} • {menu_text('thoi_gian')}: {time_str}"
        else:
            desc_str = menu_text("tiep_tuc_van")
        draw_interactive_card(
            screen,
            resume_rect,
            mouse_pos,
            title=menu_text("tiep_tuc_van"),
            desc=desc_str,
            fonts=fonts,
            accent_color=Colors.BTN_PRIMARY,
            icon_name="play",
            badge_text="RESUME" if menu_text("easy") != "Dễ" else "ĐANG CHƠI",
        )
        menu_rects["resume"] = resume_rect
        cur_y += card_h + card_gap

    # B. Daily Challenge Card
    daily_rect = pygame.Rect(hero_x, cur_y, card_w, card_h)
    today_utc = datetime.now(timezone.utc).date().isoformat()
    completed_today = daily_stats.get("last_completed_date") == today_utc
    if completed_today:
        daily_badge = "✓ XONG" if menu_text("easy") == "Dễ" else "✓ DONE"
        daily_accent = Colors.BTN_SUCCESS
    else:
        daily_badge = "HÔM NAY" if menu_text("easy") == "Dễ" else "TODAY"
        daily_accent = Colors.GOLD

    draw_interactive_card(
        screen,
        daily_rect,
        mouse_pos,
        title=menu_text("daily_challenge"),
        desc=menu_text("daily_challenge_desc"),
        fonts=fonts,
        accent_color=daily_accent,
        icon_name="flame",
        badge_text=daily_badge,
    )
    menu_rects["daily"] = daily_rect
    cur_y += card_h + card_gap

    # C. Easy Difficulty Card
    easy_rect = pygame.Rect(hero_x, cur_y, card_w, card_h)
    easy_best = best_times.get("easy")
    easy_badge = f"★ {_format_time(easy_best)}" if easy_best else None
    draw_interactive_card(
        screen,
        easy_rect,
        mouse_pos,
        title=f"1. {menu_text('de')}",
        desc=menu_text("de_desc"),
        fonts=fonts,
        accent_color=Colors.BTN_SUCCESS,
        icon_name="star",
        badge_text=easy_badge,
    )
    menu_rects["easy"] = easy_rect
    cur_y += card_h + card_gap

    # D. Medium Difficulty Card
    med_rect = pygame.Rect(hero_x, cur_y, card_w, card_h)
    med_best = best_times.get("medium")
    med_badge = f"★ {_format_time(med_best)}" if med_best else None
    draw_interactive_card(
        screen,
        med_rect,
        mouse_pos,
        title=f"2. {menu_text('trung_binh')}",
        desc=menu_text("trung_binh_desc"),
        fonts=fonts,
        accent_color=Colors.BTN_WARNING,
        icon_name="sparkles",
        badge_text=med_badge,
    )
    menu_rects["medium"] = med_rect
    cur_y += card_h + card_gap

    # E. Hard Difficulty Card
    hard_rect = pygame.Rect(hero_x, cur_y, card_w, card_h)
    hard_best = best_times.get("hard")
    hard_badge = f"★ {_format_time(hard_best)}" if hard_best else None
    draw_interactive_card(
        screen,
        hard_rect,
        mouse_pos,
        title=f"3. {menu_text('kho')}",
        desc=menu_text("kho_desc"),
        fonts=fonts,
        accent_color=Colors.BTN_DANGER,
        icon_name="trophy",
        badge_text=hard_badge,
    )
    menu_rects["hard"] = hard_rect
    cur_y += card_h + card_gap

    # F. Custom Difficulty Card with Stepper (+ / -)
    cust_rect = pygame.Rect(hero_x, cur_y, card_w, card_h)
    draw_interactive_card(
        screen,
        cust_rect,
        mouse_pos,
        title=f"4. {menu_text('custom')}",
        desc=menu_text("custom_desc"),
        fonts=fonts,
        accent_color=getattr(Colors, "RIPPLE", (99, 102, 241)),
        icon_name="slider",
    )
    menu_rects["custom"] = cust_rect

    # Stepper buttons [-] [count] [+] inside Custom card
    stepper_y = cust_rect.centery - 14
    step_btn_w = 28
    step_box_w = 54
    stepper_x = cust_rect.right - 145

    dec_rect = pygame.Rect(stepper_x, stepper_y, step_btn_w, 28)
    draw_modern_button(
        screen,
        dec_rect,
        "",
        mouse_pos,
        fonts.badge,
        variant="secondary",
        icon_name="minus",
        icon_size=14,
        radius=6,
    )
    menu_rects["custom_dec"] = dec_rect

    val_rect = pygame.Rect(stepper_x + step_btn_w + 4, stepper_y, step_box_w, 28)
    pygame.draw.rect(screen, Colors.SELECTED_BG, val_rect, border_radius=6)
    val_surf = fonts.badge.render(str(custom_cells), True, Colors.FIXED_TEXT)
    screen.blit(val_surf, val_surf.get_rect(center=val_rect.center))

    inc_rect = pygame.Rect(stepper_x + step_btn_w + step_box_w + 8, stepper_y, step_btn_w, 28)
    draw_modern_button(
        screen,
        inc_rect,
        "",
        mouse_pos,
        fonts.badge,
        variant="secondary",
        icon_name="plus",
        icon_size=14,
        radius=6,
    )
    menu_rects["custom_inc"] = inc_rect

    # ==================== 5. FOOTER ====================
    footer_y = SCREEN_HEIGHT - 38
    footer_txt = menu_text("chuc_vui_ve")
    f_surf = fonts.badge.render(footer_txt, True, Colors.STATUS_TEXT)
    screen.blit(f_surf, f_surf.get_rect(center=(SCREEN_WIDTH // 2, footer_y)))

    return menu_rects


class MenuSudoku:
    """Controller for running the Pygame Sudoku application."""

    def __init__(self, start_game_func=None):
        self.start_game_func = start_game_func

    def chay(self):
        if self.start_game_func:
            self.start_game_func()
        else:
            from game import AppController

            AppController().run()


def tao_nut_bat_dau(start_game_func=None):
    """Entry point: launches the full Pygame Menu ↔ Game application."""
    enable_high_dpi()
    if start_game_func is None:
        from game import AppController

        AppController().run()
    else:
        start_game_func()
