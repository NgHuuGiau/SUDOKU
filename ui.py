import pygame
import os

SCREEN_WIDTH = 850
SCREEN_HEIGHT = 650

BOARD_SIZE = 558
PANEL_WIDTH = 250
PADDING = 35
PANEL_OFFSET = 25
TOP_MARGIN = 30
BOTTOM_MARGIN = 100

SCREEN_WIDTH = PADDING + BOARD_SIZE + PANEL_OFFSET + PANEL_WIDTH + PADDING
SCREEN_HEIGHT = BOARD_SIZE + TOP_MARGIN + BOTTOM_MARGIN + 40

MENU_WIDTH = 650
MENU_HEIGHT = 450
CELL_SIZE = BOARD_SIZE // 9

class Colors:
    """Color palette for UI."""
    BG_MAIN = (240, 242, 245)
    BG_PANEL = (255, 255, 255)
    BG_BOARD = (255, 255, 255)
    WHITE = (255, 255, 255)
    GRID_NORMAL = (220, 225, 235)
    GRID_BOLD = (180, 190, 210)
    GRID_BORDER = (80, 120, 180)
    FIXED_TEXT = (45, 55, 72)
    USER_TEXT = (66, 133, 244)
    ERROR_TEXT = (255, 107, 107)
    HINT_TEXT = (76, 175, 80)
    SELECTED = (255, 235, 150)
    HIGHLIGHT = (220, 235, 255)
    SAME_NUMBER = (255, 230, 157)
    BTN_PRIMARY = (66, 133, 244)       # Blue
    BTN_PRIMARY_HOVER = (48, 111, 204) # Darker blue
    BTN_SECONDARY = (76, 175, 80)      # Green
    BTN_SECONDARY_HOVER = (56, 142, 60)
    BTN_WARNING = (255, 152, 0)        # Orange
    BTN_WARNING_HOVER = (255, 111, 0)
    BTN_DANGER = (244, 67, 54)         # Red
    BTN_DANGER_HOVER = (211, 47, 47)

    # Special
    NOTE_BG = (220, 235, 255)          # Light blue note background
    NOTE_TEXT = (100, 150, 200)        # Blue-gray notes
    TIMER_BG = (240, 245, 255)         # Very light blue timer
    TIMER_BORDER = (150, 180, 220)
    PAUSE_OVERLAY = (0, 0, 0, 180)
    WIN_GOLD = (255, 215, 0)

def init_display(screen_obj: pygame.Surface, fonts: tuple) -> None:
    pass  # Not needed since we pass screen directly

def draw_grid(screen: pygame.Surface) -> None:
    block_size = BOARD_SIZE // 9
    # Vertical lines
    for x in range(0, BOARD_SIZE + 1, block_size):
        thickness = 4 if x % (block_size * 3) == 0 else 2
        pygame.draw.line(screen, Colors.GRID_BOLD if thickness == 4 else Colors.GRID_NORMAL,
                        (x + PADDING, TOP_MARGIN),
                        (x + PADDING, BOARD_SIZE + TOP_MARGIN), thickness)
    # Horizontal lines
    for y in range(0, BOARD_SIZE + 1, block_size):
        thickness = 4 if y % (block_size * 3) == 0 else 2
        pygame.draw.line(screen, Colors.GRID_BOLD if thickness == 4 else Colors.GRID_NORMAL,
                        (PADDING, y + TOP_MARGIN),
                        (BOARD_SIZE + PADDING, y + TOP_MARGIN), thickness)

def draw_numbers(screen: pygame.Surface, font, note_font, board, original_board, solution, notes, show_errors=False, highlight_val=None):
    block_size = BOARD_SIZE // 9

    for row in range(9):
        for col in range(9):
            rect = pygame.Rect(col * block_size + PADDING,
                              row * block_size + TOP_MARGIN,
                              block_size, block_size)


            if highlight_val is not None and highlight_val != 0 and board[row][col] == highlight_val:
                pygame.draw.rect(screen, Colors.SAME_NUMBER, rect, border_radius=10)

            if board[row][col] != 0:
                is_fixed = original_board[row][col] != 0
                color = Colors.FIXED_TEXT if is_fixed else Colors.USER_TEXT

                if not is_fixed:
                    from logic import is_valid_placement
                    if not is_valid_placement(board, row, col, board[row][col]):
                        color = Colors.ERROR_TEXT
                    elif show_errors and board[row][col] != solution[row][col]:
                        color = Colors.ERROR_TEXT

                value = font.render(str(board[row][col]), True, color)
                screen.blit(value, value.get_rect(center=rect.center))
            elif notes[row][col]:
                sub_w = block_size // 3
                sub_h = block_size // 3
                for note_num in sorted(notes[row][col]):
                    sub_row = (note_num - 1) // 3
                    sub_col = (note_num - 1) % 3
                    note = note_font.render(str(note_num), True, Colors.NOTE_TEXT)
                    screen.blit(note, note.get_rect(
                        center=(rect.left + sub_col * sub_w + sub_w // 2,
                               rect.top + sub_row * sub_h + sub_h // 2)))

def draw_timer(screen: pygame.Surface, small_font, game_over, paused, final_time, start, paused_time, last_pause):
    if game_over:
        elapsed = final_time
    elif paused:
        elapsed = (last_pause - start - paused_time) // 1000
    else:
        elapsed = (pygame.time.get_ticks() - start - paused_time) // 1000

    minutes, seconds = divmod(max(0, elapsed), 60)
    text = small_font.render(f"{minutes:02}:{seconds:02}", True, Colors.FIXED_TEXT)

    panel_rect = pygame.Rect(PADDING + BOARD_SIZE + PANEL_OFFSET, TOP_MARGIN,
                            PANEL_WIDTH, 60)
    screen.blit(text, text.get_rect(center=panel_rect.center))
    return panel_rect

def draw_button(screen: pygame.Surface, rect, text, mouse_pos, font_to_use, color_scheme='primary'):
    """Draw a modern button with hover effect."""
    colors = {
        'primary': (Colors.BTN_PRIMARY, Colors.BTN_PRIMARY_HOVER),
        'secondary': (Colors.BTN_SECONDARY, Colors.BTN_SECONDARY_HOVER),
        'warning': (Colors.BTN_WARNING, Colors.BTN_WARNING_HOVER),
        'danger': (Colors.BTN_DANGER, Colors.BTN_DANGER_HOVER),
    }
    base_color, hover_color = colors.get(color_scheme, (Colors.BTN_PRIMARY, Colors.BTN_PRIMARY_HOVER))
    color = hover_color if rect.collidepoint(mouse_pos) else base_color


    pygame.draw.rect(screen, color, rect, border_radius=rect.height // 2)  # Perfectly rounded (pill shape)
    text_surface = font_to_use.render(text, True, (255, 255, 255))
    screen.blit(text_surface, text_surface.get_rect(center=rect.center))
    return rect