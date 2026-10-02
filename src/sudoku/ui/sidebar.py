"""Sidebar controls rendering for Sudoku UI."""

import pygame

from sudoku.logic import count_mistakes
from sudoku.persistence import load_best_times, load_daily_stats
from sudoku.ui.colors import Colors
from sudoku.ui.drawing import draw_icon_tile, draw_modern_button, draw_rounded_card, soft_tint
from sudoku.ui.geometry import (
    SIDEBAR_WIDTH,
    SIDEBAR_X,
    SIDEBAR_Y,
    get_remaining_counts,
    get_sidebar_layout,
)
from sudoku.ui.icons import SmoothIcons


def _format_clock(total_seconds: int | None) -> str:
    if total_seconds is None:
        return "--:--"
    mins, secs = divmod(max(0, total_seconds), 60)
    return f"{mins:02}:{secs:02}"


def draw_sidebar(screen: pygame.Surface, fonts, mouse_pos: tuple[int, int], translate, state) -> dict[str, pygame.Rect | list[pygame.Rect]]:
    layout = get_sidebar_layout()
    rem_counts = get_remaining_counts(state.board)

    # Calculate note counts per digit
    note_counts = dict.fromkeys(range(1, 10), 0)
    for r in range(9):
        for c in range(9):
            for d in state.notes[r][c]:
                note_counts[d] += 1

    # 1. Quick Actions header
    sec1_label = fonts.badge.render(translate("thao_tac_nhanh"), True, Colors.STATUS_TEXT)
    screen.blit(sec1_label, (SIDEBAR_X + 2, SIDEBAR_Y - 20))

    # Undo & Redo
    draw_modern_button(
        screen,
        layout["quick_undo"],
        "",
        mouse_pos,
        fonts.medium,
        variant="secondary",
        subtext=translate("hoan_tac"),
        sub_font=fonts.badge,
        icon_name="undo",
        icon_size=26,
        icon_color=Colors.ICON_UNDO,
    )
    draw_modern_button(
        screen,
        layout["quick_redo"],
        "",
        mouse_pos,
        fonts.medium,
        variant="secondary",
        subtext=translate("lam_lai"),
        sub_font=fonts.badge,
        icon_name="redo",
        icon_size=26,
        icon_color=Colors.ICON_UNDO,
    )

    # Notes toggle
    notes_active = state.notes_mode
    notes_subtext = f"{translate('ghi_chu')} {'ON' if notes_active else 'OFF'}"
    draw_modern_button(
        screen,
        layout["quick_notes"],
        "",
        mouse_pos,
        fonts.small,
        variant="secondary",
        is_active=notes_active,
        subtext=notes_subtext,
        sub_font=fonts.badge,
        icon_name="pencil",
        icon_size=26,
        icon_color=Colors.ICON_NOTES,
    )

    # Hint
    draw_modern_button(
        screen,
        layout["quick_hint"],
        "",
        mouse_pos,
        fonts.small,
        variant="secondary",
        subtext=translate("goi_y"),
        sub_font=fonts.badge,
        icon_name="hint",
        icon_size=26,
        icon_color=Colors.ICON_HINT,
    )

    # Check Errors toggle
    check_errors_active = state.show_errors
    check_errors_subtext = f"{translate('kiem_tra_loi')} {'ON' if check_errors_active else 'OFF'}"
    draw_modern_button(
        screen,
        layout["quick_check_errors"],
        "",
        mouse_pos,
        fonts.small,
        variant="secondary",
        is_active=check_errors_active,
        subtext=check_errors_subtext,
        sub_font=fonts.badge,
        icon_name="check",
        icon_size=26,
        icon_color=Colors.ICON_SUCCESS,
    )

    # 2. Tools (Clear, Auto Notes, Export, Import)
    draw_modern_button(
        screen,
        layout["clear"],
        translate("xoa_btn"),
        mouse_pos,
        fonts.small,
        variant="danger",
        icon_name="erase",
        icon_size=22,
        icon_color=Colors.BTN_VIVID_TEXT,
    )
    draw_modern_button(
        screen,
        layout["auto_notes"],
        translate("ghi_chu_tu_dong"),
        mouse_pos,
        fonts.badge,
        variant="secondary",
        icon_name="sparkles",
        icon_size=22,
        icon_color=Colors.ICON_THEME,
    )
    draw_modern_button(
        screen,
        layout["export"],
        translate("xuat_van"),
        mouse_pos,
        fonts.badge,
        variant="secondary",
        icon_name="upload",
        icon_size=22,
        icon_color=Colors.ICON_STATS,
    )
    draw_modern_button(
        screen,
        layout["import"],
        translate("nhap_van"),
        mouse_pos,
        fonts.badge,
        variant="secondary",
        icon_name="download",
        icon_size=22,
        icon_color=Colors.ICON_THEME,
    )

    # 3. Number pad header + live mistakes pill
    num_title_y = layout["import"].bottom + 12
    sec2_label = fonts.badge.render(translate("ban_phim_so"), True, Colors.STATUS_TEXT)
    screen.blit(sec2_label, (SIDEBAR_X + 2, num_title_y))

    mistakes = count_mistakes(state.board, state.solution)
    pill_txt = fonts.badge.render(str(mistakes), True, Colors.FIXED_TEXT)
    pill_w = 20 + 16 + pill_txt.get_width() + 12
    pill_rect = pygame.Rect(layout["numbers"][-1].right - pill_w, num_title_y - 2, pill_w, 22)
    pygame.draw.rect(
        screen, soft_tint(Colors.ICON_MISTAKES, Colors.BG_CARD), pill_rect, border_radius=11
    )
    shield = SmoothIcons.get("shield", 14, Colors.ICON_MISTAKES)
    screen.blit(shield, shield.get_rect(midleft=(pill_rect.left + 8, pill_rect.centery)))
    screen.blit(pill_txt, pill_txt.get_rect(midleft=(pill_rect.left + 26, pill_rect.centery)))

    # Number pad 1-9: big digit + remaining count on two lines, dimmed when done
    for i, num_rect in enumerate(layout["numbers"]):
        digit = i + 1
        rem = rem_counts[digit]
        is_done = rem == 0
        notes_for_digit = note_counts[digit]

        draw_modern_button(
            screen,
            num_rect,
            str(digit),
            mouse_pos,
            fonts.large,
            variant="disabled" if is_done else "secondary",
            subtext=translate("con_lai_du") if is_done else f"x{rem}",
            sub_font=fonts.badge,
            radius=12,
        )
        if is_done:
            chk_surf = SmoothIcons.get("check", 14, Colors.BTN_SUCCESS)
            screen.blit(
                chk_surf, chk_surf.get_rect(center=(num_rect.right - 14, num_rect.top + 14))
            )
        elif notes_for_digit > 0:
            indicator_rect = pygame.Rect(num_rect.right - 18, num_rect.top + 3, 16, 16)
            pygame.draw.circle(screen, Colors.BTN_PRIMARY, indicator_rect.center, 7)
            count_surf = fonts.tiny.render(
                str(min(notes_for_digit, 9)), True, Colors.BTN_VIVID_TEXT
            )
            screen.blit(count_surf, count_surf.get_rect(center=indicator_rect.center))

    # 4. Info card fills the middle: difficulty, best time, streak
    info_rect = pygame.Rect(SIDEBAR_X, 576, SIDEBAR_WIDTH, 150)
    draw_rounded_card(
        screen, info_rect, Colors.BG_CARD, Colors.CARD_BORDER, radius=14, shadow=False
    )
    best = load_best_times().get(state.difficulty)
    streak = load_daily_stats().get("streak", 0)
    for index, (label, value, icon, color) in enumerate(
        [
            (translate("do_kho"), translate(state.difficulty), "slider", Colors.ICON_THEME),
            (translate("best_label"), _format_clock(best), "trophy", Colors.ICON_VICTORY),
            (translate("streak"), str(streak), "flame", Colors.ICON_STREAK),
        ]
    ):
        row_y = info_rect.top + 10 + index * 48
        draw_icon_tile(
            screen,
            pygame.Rect(info_rect.left + 12, row_y + 2, 40, 40),
            icon,
            color,
            icon_size=24,
            radius=12,
        )
        label_surf = fonts.badge.render(label, True, Colors.STATUS_TEXT)
        screen.blit(label_surf, (info_rect.left + 62, row_y + 4))
        value_surf = fonts.medium.render(value, True, Colors.FIXED_TEXT)
        screen.blit(
            value_surf,
            value_surf.get_rect(midright=(info_rect.right - 16, row_y + 28)),
        )

    # 5. Bottom actions (New Game & Menu)
    draw_modern_button(
        screen,
        layout["new_game"],
        translate("van_moi"),
        mouse_pos,
        fonts.small,
        variant="warning",
        icon_name="restart",
        icon_size=22,
        icon_color=Colors.BTN_VIVID_TEXT,
        radius=12,
    )
    draw_modern_button(
        screen,
        layout["menu"],
        translate("thoat_ve_menu"),
        mouse_pos,
        fonts.small,
        variant="secondary",
        icon_name="home",
        icon_size=22,
        icon_color=Colors.ICON_HOME,
        radius=12,
    )

    return layout  # type: ignore[no-any-return]






