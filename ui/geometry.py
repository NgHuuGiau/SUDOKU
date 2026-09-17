"""Geometry constants and layout calculations for Sudoku UI."""

import pygame

# Screen dimensions
SCREEN_WIDTH = 1120
SCREEN_HEIGHT = 800

BOARD_SIZE = 600
CELL_SIZE = BOARD_SIZE // 9  # 66px

BOARD_X = 40
BOARD_Y = 104

SIDEBAR_X = BOARD_X + BOARD_SIZE + 28  # 668
SIDEBAR_Y = BOARD_Y
SIDEBAR_WIDTH = SCREEN_WIDTH - SIDEBAR_X - 36  # 416


def get_timer_rect() -> pygame.Rect:
    return pygame.Rect(SCREEN_WIDTH - 250, 22, 115, 46)


def get_cell_from_pos(x: int, y: int):
    if not (BOARD_X <= x < BOARD_X + BOARD_SIZE and BOARD_Y <= y < BOARD_Y + BOARD_SIZE):
        return None
    row = (y - BOARD_Y) * 9 // BOARD_SIZE
    col = (x - BOARD_X) * 9 // BOARD_SIZE
    return (row, col) if 0 <= row < 9 and 0 <= col < 9 else None


def get_sidebar_layout() -> dict:
    x = SIDEBAR_X
    w = SIDEBAR_WIDTH
    y = SIDEBAR_Y

    # 1. Quick Actions (3 + 2 buttons, so labels stay readable)
    quick_btn_w = (w - 12) // 3
    quick_btn_h = 52
    quick_buttons = []
    for i in range(5):
        col = i % 3
        row = i // 3
        bx = x + col * (quick_btn_w + 6)
        by = y + row * (quick_btn_h + 8)
        quick_buttons.append(pygame.Rect(bx, by, quick_btn_w, quick_btn_h))

    y += 2 * quick_btn_h + 8 + 12

    # 2. Tools (2 x 2 grid, so translated labels do not get clipped)
    tool_btn_w = (w - 6) // 2
    tool_btn_h = 38
    clear_rect = pygame.Rect(x, y, tool_btn_w, tool_btn_h)
    auto_notes_rect = pygame.Rect(x + tool_btn_w + 6, y, tool_btn_w, tool_btn_h)
    export_rect = pygame.Rect(x, y + tool_btn_h + 6, tool_btn_w, tool_btn_h)
    import_rect = pygame.Rect(x + tool_btn_w + 6, y + tool_btn_h + 6, tool_btn_w, tool_btn_h)

    y += 2 * tool_btn_h + 6 + 18

    # 3. Number pad (3x3 grid)
    num_grid_y = y + 18
    num_btn_w = (w - 16) // 3
    num_btn_h = 58
    number_buttons = []
    for i in range(9):
        col = i % 3
        row = i // 3
        number_buttons.append(
            pygame.Rect(
                x + col * (num_btn_w + 8),
                num_grid_y + row * (num_btn_h + 8),
                num_btn_w,
                num_btn_h,
            )
        )

    y = num_grid_y + 3 * (num_btn_h + 8) + 14

    # 4. Bottom actions (New Game, Menu)
    action_btn_w = (w - 10) // 2
    action_btn_h = 46
    new_game_rect = pygame.Rect(x, y, action_btn_w, action_btn_h)
    menu_rect = pygame.Rect(x + action_btn_w + 10, y, action_btn_w, action_btn_h)

    return {
        "quick_undo": quick_buttons[0],
        "quick_redo": quick_buttons[1],
        "quick_notes": quick_buttons[2],
        "quick_hint": quick_buttons[3],
        "quick_check_errors": quick_buttons[4],
        "clear": clear_rect,
        "auto_notes": auto_notes_rect,
        "export": export_rect,
        "import": import_rect,
        "numbers": number_buttons,
        "new_game": new_game_rect,
        "menu": menu_rect,
    }


def get_remaining_counts(board) -> dict:
    counts = dict.fromkeys(range(1, 10), 0)
    for row in board:
        for val in row:
            if 1 <= val <= 9:
                counts[val] += 1
    return {num: max(0, 9 - counts[num]) for num in range(1, 10)}
