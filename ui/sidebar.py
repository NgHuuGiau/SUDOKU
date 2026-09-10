"""Sidebar controls rendering for Sudoku UI."""
import pygame

from ui.colors import Colors
from ui.drawing import draw_modern_button
from ui.geometry import SIDEBAR_X, SIDEBAR_Y, get_remaining_counts, get_sidebar_layout
from ui.icons import SmoothIcons


def draw_sidebar(screen: pygame.Surface, fonts, mouse_pos, translate, state) -> dict:
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
    draw_modern_button(screen, layout["quick_undo"], "", mouse_pos, fonts.medium,
                       variant='secondary', subtext=translate("hoan_tac"), sub_font=fonts.badge,
                       icon_name='undo', icon_size=20)
    draw_modern_button(screen, layout["quick_redo"], "", mouse_pos, fonts.medium,
                       variant='secondary', subtext=translate("lam_lai"), sub_font=fonts.badge,
                       icon_name='redo', icon_size=20)

    # Notes toggle
    notes_active = state.notes_mode
    notes_subtext = f"{translate('ghi_chu')} {'ON' if notes_active else 'OFF'}"
    draw_modern_button(screen, layout["quick_notes"], "", mouse_pos, fonts.small,
                       variant='secondary', is_active=notes_active,
                       subtext=notes_subtext, sub_font=fonts.badge,
                       icon_name='pencil', icon_size=20)

    # Hint
    draw_modern_button(screen, layout["quick_hint"], "", mouse_pos, fonts.small,
                       variant='secondary', subtext=translate("goi_y"), sub_font=fonts.badge,
                       icon_name='hint', icon_size=20)

    # Check Errors toggle
    check_errors_active = state.show_errors
    check_errors_subtext = f"{translate('kiem_tra_loi')} {'ON' if check_errors_active else 'OFF'}"
    draw_modern_button(screen, layout["quick_check_errors"], "", mouse_pos, fonts.small,
                       variant='secondary', is_active=check_errors_active,
                       subtext=check_errors_subtext, sub_font=fonts.badge,
                       icon_name='check', icon_size=20)

    # 2. Tools (Clear, Auto Notes, Export, Import)
    draw_modern_button(screen, layout["clear"], translate('xoa_btn'), mouse_pos, fonts.small,
                       variant='danger', icon_name='erase', icon_size=16)
    draw_modern_button(screen, layout["auto_notes"], translate('ghi_chu_tu_dong'), mouse_pos, fonts.badge,
                       variant='secondary', icon_name='sparkles', icon_size=16)
    draw_modern_button(screen, layout["export"], translate('xuat_van'), mouse_pos, fonts.badge,
                       variant='secondary', icon_name='save', icon_size=16)
    draw_modern_button(screen, layout["import"], translate('nhap_van'), mouse_pos, fonts.badge,
                       variant='secondary', icon_name='home', icon_size=16)

    # 3. Number pad header
    num_title_y = layout["clear"].bottom + 10
    sec2_label = fonts.badge.render(translate("ban_phim_so"), True, Colors.STATUS_TEXT)
    screen.blit(sec2_label, (SIDEBAR_X + 2, num_title_y))

    # Number pad 1-9
    for i, num_rect in enumerate(layout["numbers"]):
        digit = i + 1
        rem = rem_counts[digit]
        is_done = (rem == 0)
        notes_for_digit = note_counts[digit]

        if is_done:
            sub_text = translate("con_lai_du")
            btn_variant = 'disabled'
        else:
            sub_text = translate("con_lai_fmt").replace("{n}", str(rem))
            btn_variant = 'secondary'

        draw_modern_button(screen, num_rect, str(digit), mouse_pos, fonts.medium,
                           variant=btn_variant, subtext=sub_text, sub_font=fonts.badge, radius=8)

        if is_done:
            chk_surf = SmoothIcons.get('check', 12, Colors.BTN_SUCCESS)
            screen.blit(chk_surf, chk_surf.get_rect(center=(num_rect.right - 12, num_rect.top + 12)))

        # Show note count indicator
        if notes_for_digit > 0 and not is_done:
            indicator_rect = pygame.Rect(num_rect.right - 18, num_rect.top + 2, 16, 16)
            pygame.draw.circle(screen, Colors.BTN_PRIMARY, indicator_rect.center, 7)
            count_surf = fonts.tiny.render(str(min(notes_for_digit, 9)), True, Colors.WHITE)
            screen.blit(count_surf, count_surf.get_rect(center=indicator_rect.center))

    # 4. Bottom actions (New Game & Menu)
    draw_modern_button(screen, layout["new_game"], translate('van_moi'), mouse_pos, fonts.small,
                       variant='warning', icon_name='restart', icon_size=16)
    draw_modern_button(screen, layout["menu"], translate('thoat_ve_menu'), mouse_pos, fonts.small,
                       variant='secondary', icon_name='home', icon_size=16)

    return layout
