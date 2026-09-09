"""Geometry constants and layout calculations for Sudoku UI."""
import pygame


# Screen dimensions
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 740

BOARD_SIZE = 558
CELL_SIZE = BOARD_SIZE // 9  # 62px

BOARD_X = 36
BOARD_Y = 100

SIDEBAR_X = BOARD_X + BOARD_SIZE + 28  # 622
SIDEBAR_Y = BOARD_Y
SIDEBAR_WIDTH = SCREEN_WIDTH - SIDEBAR_X - 36  # 302


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

    # 1. Quick Actions (5 buttons)
    quick_btn_w = (w - 24) // 5
    quick_btn_h = 58
    quick_buttons = []
    for i in range(5):
        bx = x + i * (quick_btn_w + 6)
        quick_buttons.append(pygame.Rect(bx, y, quick_btn_w, quick_btn_h))

    y += quick_btn_h + 12

    # 2. Tools (Clear, Auto Notes)
    tool_btn_w = (w - 10) // 2
    tool_btn_h = 42
    clear_rect = pygame.Rect(x, y, tool_btn_w, tool_btn_h)
    auto_notes_rect = pygame.Rect(x + tool_btn_w + 10, y, tool_btn_w, tool_btn_h)

    y += tool_btn_h + 18

    # 3. Number pad (3x3 grid)
    num_grid_y = y + 18
    num_btn_w = (w - 16) // 3
    num_btn_h = 58
    number_buttons = []
    for i in range(9):
        col = i % 3
        row = i // 3
        number_buttons.append(pygame.Rect(
            x + col * (num_btn_w + 8),
            num_grid_y + row * (num_btn_h + 8),
            num_btn_w,
            num_btn_h,
        ))

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
        "numbers": number_buttons,
        "new_game": new_game_rect,
        "menu": menu_rect,
        "undo": quick_buttons[0],
        "redo": quick_buttons[1],
    }


def get_remaining_counts(board) -> dict:
    counts = {num: 0 for num in range(1, 10)}
    for row in board:
        for val in row:
            if 1 <= val <= 9:
                counts[val] += 1
    return {num: max(0, 9 - counts[num]) for num in range(1, 10)}