"""Centered single-column home screen for the Sudoku app."""

from datetime import datetime, timezone

import pygame

from sudoku.config import menu_text
from sudoku.persistence import has_save_file, load_best_times, load_daily_stats, load_game_state
from sudoku.sounds import is_sound_enabled
from sudoku.ui.colors import Colors, get_theme_manager
from sudoku.ui.drawing import draw_badge, draw_interactive_card, draw_modern_button, soft_tint
from sudoku.ui.geometry import SCREEN_WIDTH
from sudoku.ui.icons import SmoothIcons


def _format_time(seconds: int | None) -> str:
    mins, secs = divmod(max(0, seconds or 0), 60)
    return f"{mins:02}:{secs:02}"


MENU_KEYS = (
    "resume",
    "daily",
    "easy",
    "medium",
    "hard",
    "custom",
    "custom_dec",
    "custom_inc",
    "theme",
    "sound",
    "lang",
    "stats",
    "help",
)


def draw_menu_view(
    screen: pygame.Surface,
    fonts,
    mouse_pos: tuple[int, int],
    custom_cells: int = 40,
    menu_data: dict | None = None,
) -> dict:
    """Render the centered menu and return all interactive hitboxes."""
    theme_mgr = get_theme_manager()
    if menu_data is None:
        best_times = load_best_times()
        daily_stats = load_daily_stats()
        save_file_exists = has_save_file()
        saved_state = load_game_state() if save_file_exists else None
        save_exists = saved_state is not None
        save_error = save_file_exists and saved_state is None
        saved_game = (
            (saved_state.difficulty, saved_state.get_elapsed_time()) if saved_state else None
        )
    else:
        best_times = menu_data["best_times"]
        daily_stats = menu_data["daily_stats"]
        save_exists = menu_data["save_exists"]
        save_error = menu_data.get("save_error", False)
        saved_game = menu_data["saved_game"]

    screen.fill(Colors.BG_MAIN)
    menu_rects: dict[str, pygame.Rect | None] = dict.fromkeys(MENU_KEYS)

    col_w = 560
    col_x = (SCREEN_WIDTH - col_w) // 2
    cx = col_x + col_w // 2

    # Logo block
    logo = SmoothIcons.get("grid_logo", 56, Colors.BTN_PRIMARY)
    screen.blit(logo, logo.get_rect(center=(cx, 56)))
    title = fonts.title.render("SUDOKU", True, Colors.FIXED_TEXT)
    screen.blit(title, title.get_rect(center=(cx, 100)))
    draw_badge(
        screen,
        pygame.Rect(cx - 80, 120, 160, 28),
        "PLAY SMART",
        fonts.badge,
        soft_tint(Colors.BTN_PRIMARY, Colors.BG_MAIN),
        Colors.BTN_PRIMARY,
        radius=14,
    )
    sub1 = fonts.badge.render(menu_text("thu_thach"), True, Colors.STATUS_TEXT)
    screen.blit(sub1, sub1.get_rect(center=(cx, 158)))
    streak = fonts.badge.render(
        menu_text("streak_label").format(n=daily_stats.get("streak", 0)),
        True,
        Colors.ICON_STREAK,
    )
    screen.blit(streak, streak.get_rect(center=(cx, 178)))

    # Cards
    y = 202
    if save_exists:
        saved_text = menu_text("tiep_tuc_van")
        saved_desc = menu_text("tiep_tuc_van_desc").split("(")[0].strip()
        if saved_game:
            saved_difficulty, elapsed = saved_game
            saved_desc = f"{saved_desc} ({saved_difficulty.title()} - {_format_time(elapsed)})"
        resume_rect = pygame.Rect(col_x, y, col_w, 76)
        draw_interactive_card(
            screen,
            resume_rect,
            mouse_pos,
            saved_text,
            saved_desc,
            fonts,
            Colors.BTN_PRIMARY,
            icon_name="play",
            badge_text=menu_text("resume_badge"),
            text_max_width=col_w - 64 - 160,
        )
        menu_rects["resume"] = resume_rect
        y += 88

    today_utc = datetime.now(timezone.utc).date().isoformat()
    completed_today = daily_stats.get("last_completed_date") == today_utc
    daily_rect = pygame.Rect(col_x, y, col_w, 76)
    draw_interactive_card(
        screen,
        daily_rect,
        mouse_pos,
        menu_text("daily_challenge"),
        menu_text("daily_challenge_desc"),
        fonts,
        Colors.BTN_SUCCESS if completed_today else Colors.GOLD,
        icon_name="flame",
        badge_text=(
            menu_text("daily_done_badge") if completed_today else menu_text("daily_today_badge")
        ),
        text_max_width=col_w - 64 - 160,
    )
    menu_rects["daily"] = daily_rect
    y += 88

    for index, (key, title_key, desc_key, icon, accent) in enumerate(
        [
            ("easy", "de", "de_desc", "star", Colors.BTN_SUCCESS),
            ("medium", "trung_binh", "trung_binh_desc", "sparkles", Colors.BTN_WARNING),
            ("hard", "kho", "kho_desc", "trophy", Colors.BTN_DANGER),
            ("custom", "custom", "custom_desc", "slider", Colors.RIPPLE),
        ]
    ):
        row_rect = pygame.Rect(col_x, y + index * 82, col_w, 72)
        best: int | None = {str(k): v for k, v in best_times.items()}.get(key)
        draw_interactive_card(
            screen,
            row_rect,
            mouse_pos,
            menu_text(title_key),
            menu_text(desc_key),
            fonts,
            accent,
            icon_name=icon,
            badge_text=_format_time(best) if best else None,
            show_chevron=key != "custom",
            text_max_width=col_w - 64 - (190 if key == "custom" else 130),
        )
        menu_rects[key] = row_rect

    custom_rect = menu_rects["custom"]
    assert custom_rect is not None
    step_y = custom_rect.centery - 14
    step_x = custom_rect.right - 12 - 28 - 4 - 54 - 4 - 28
    dec_rect = pygame.Rect(step_x, step_y, 28, 28)
    draw_modern_button(
        screen,
        dec_rect,
        "",
        mouse_pos,
        fonts.badge,
        variant="secondary",
        icon_name="minus",
        icon_size=14,
        radius=8,
    )
    menu_rects["custom_dec"] = dec_rect
    value_rect = pygame.Rect(step_x + 32, step_y, 54, 28)
    pygame.draw.rect(screen, Colors.SELECTED_BG, value_rect, border_radius=8)
    value_surface = fonts.badge.render(str(custom_cells), True, Colors.FIXED_TEXT)
    screen.blit(value_surface, value_surface.get_rect(center=value_rect.center))
    inc_rect = pygame.Rect(step_x + 90, step_y, 28, 28)
    draw_modern_button(
        screen,
        inc_rect,
        "",
        mouse_pos,
        fonts.badge,
        variant="secondary",
        icon_name="plus",
        icon_size=14,
        radius=8,
    )
    menu_rects["custom_inc"] = inc_rect

    # Bottom icon row
    buttons: list[tuple] = [
        ("help", "", "help", 22, {}),
        ("stats", "", "stats", 22, {}),
        (
            "sound",
            "",
            "sound" if is_sound_enabled() else "sound_mute",
            22,
            {"is_active": is_sound_enabled()},
        ),
        ("theme", menu_text(f"theme_{theme_mgr.theme}"), "palette", 20, {"width": 120}),
        ("lang", menu_text("ngon_ngu_btn"), "globe", 20, {"width": 84}),
    ]
    total_w = 48 * 3 + 120 + 84 + 4 * 10
    bx = (SCREEN_WIDTH - total_w) // 2
    for key, label, icon, icon_size, extra in buttons:
        width = extra.get("width", 48)
        rect = pygame.Rect(bx, 704, width, 48)
        draw_modern_button(
            screen,
            rect,
            label,
            mouse_pos,
            fonts.badge,
            variant="secondary",
            is_active=extra.get("is_active", False),
            icon_name=icon,
            icon_size=icon_size,
            icon_color={
                "help": Colors.ICON_SETTINGS,
                "stats": Colors.ICON_STATS,
                "sound": Colors.ICON_SOUND,
                "theme": Colors.ICON_THEME,
                "lang": Colors.ICON_SETTINGS,
            }[key],
        )
        menu_rects[key] = rect
        bx += width + 10

    if save_error:
        draw_badge(
            screen,
            pygame.Rect(col_x, 672, col_w, 22),
            menu_text("save_unavailable"),
            fonts.tiny,
            soft_tint(Colors.BTN_WARNING, Colors.BG_MAIN),
            Colors.BTN_WARNING,
            radius=11,
        )

    hint = fonts.tiny.render(
        "Tab / Shift+Tab: focus · Enter/Space: select", True, Colors.STATUS_TEXT
    )
    screen.blit(hint, hint.get_rect(center=(cx, 768)))
    return menu_rects


def tao_nut_bat_dau():
    """Entry point: launches the full Pygame Menu ↔ Game application."""
    from sudoku.game import AppController

    AppController().run()
