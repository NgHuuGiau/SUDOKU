import pygame
import os

try:
    from logic import is_valid_placement
except ImportError:
    is_valid_placement = None

# Định nghĩa các thông số kích thước giao diện
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
    # Bảng màu hiện đại cho giao diện Sudoku (Hệ màu Slate/Blue)
    BG_MAIN = (248, 250, 252)          # Slate 50
    BG_PANEL = (255, 255, 255)
    BG_BOARD = (255, 255, 255)
    WHITE = (255, 255, 255)
    GRID_NORMAL = (226, 232, 240)      # Slate 200
    GRID_BOLD = (71, 85, 105)          # Slate 600
    GRID_BORDER = (15, 23, 42)         # Slate 900
    FIXED_TEXT = (30, 41, 59)          # Slate 800
    USER_TEXT = (37, 99, 235)          # Blue 600
    ERROR_TEXT = (220, 38, 38)         # Red 600
    HINT_TEXT = (5, 150, 105)          # Emerald 600
    SELECTED = (191, 219, 254)         # Blue 200
    HIGHLIGHT = (241, 245, 249)        # Slate 100 (For row/col highlight)
    SAME_NUMBER = (254, 240, 138)      # Yellow 200
    BTN_PRIMARY = (37, 99, 235)        # Blue 600
    BTN_PRIMARY_HOVER = (48, 111, 204) # Darker blue
    BTN_SECONDARY = (16, 185, 129)     # Emerald 500
    BTN_SECONDARY_HOVER = (56, 142, 60)
    BTN_WARNING = (245, 158, 11)       # Amber 500
    BTN_WARNING_HOVER = (255, 111, 0)
    BTN_DANGER = (239, 68, 68)         # Red 500
    BTN_DANGER_HOVER = (211, 47, 47)

    # Màu sắc cho các thành phần đặc biệt
    NOTE_BG = (220, 235, 255)          # Light blue note background
    NOTE_TEXT = (100, 150, 200)        # Blue-gray notes
    TIMER_BG = (240, 245, 255)         # Very light blue timer
    TIMER_BORDER = (150, 180, 220)
    PAUSE_OVERLAY = (0, 0, 0, 180)
    WIN_GOLD = (255, 215, 0)

def init_display(screen_obj: pygame.Surface, fonts: tuple) -> None:
    pass

def draw_grid(screen: pygame.Surface) -> None:
    # Vẽ lưới bảng Sudoku với các đường kẻ đậm nhạt phân chia khối 3x3
    block_size = BOARD_SIZE // 9
    # Vẽ các đường dọc
    for x in range(0, BOARD_SIZE + 1, block_size):
        thickness = 3 if x % (block_size * 3) == 0 else 1
        pygame.draw.line(screen, Colors.GRID_BOLD if thickness == 3 else Colors.GRID_NORMAL,
                        (x + PADDING, TOP_MARGIN),
                        (x + PADDING, BOARD_SIZE + TOP_MARGIN), thickness)
    # Vẽ các đường ngang
    for y in range(0, BOARD_SIZE + 1, block_size):
        thickness = 3 if y % (block_size * 3) == 0 else 1
        pygame.draw.line(screen, Colors.GRID_BOLD if thickness == 3 else Colors.GRID_NORMAL,
                        (PADDING, y + TOP_MARGIN),
                        (BOARD_SIZE + PADDING, y + TOP_MARGIN), thickness)

def draw_numbers(screen: pygame.Surface, font, note_font, board, original_board, solution, notes, show_errors=False, highlight_val=None, selected_cell=None):
    # Vẽ các con số và ghi chú lên bảng Sudoku, bao gồm hiệu ứng highlight
    block_size = BOARD_SIZE // 9

    for row in range(9):
        for col in range(9):
            rect = pygame.Rect(col * block_size + PADDING,
                              row * block_size + TOP_MARGIN,
                              block_size, block_size)

            # Hiệu ứng làm nổi bật hàng, cột và khối của ô đang chọn (Cross-Highlighting)
            if selected_cell:
                s_row, s_col = selected_cell
                if row == s_row or col == s_col or (row//3 == s_row//3 and col//3 == s_col//3):
                    pygame.draw.rect(screen, Colors.HIGHLIGHT, rect)

            # Vẽ nền cho ô đang được chọn trực tiếp (Selected Cell)
            if selected_cell == (row, col):
                pygame.draw.rect(screen, Colors.SELECTED, rect)

            # Làm nổi bật các ô có cùng giá trị với ô đang chọn (Same Number Highlight)
            if highlight_val is not None and highlight_val != 0 and board[row][col] == highlight_val:
                pygame.draw.rect(screen, Colors.SAME_NUMBER, rect)

            # Xử lý vẽ số (Số mặc định, số người dùng nhập, hoặc lỗi)
            if board[row][col] != 0:
                is_fixed = original_board[row][col] != 0
                color = Colors.FIXED_TEXT if is_fixed else Colors.USER_TEXT

                if not is_fixed:
                    if is_valid_placement and not is_valid_placement(board, row, col, board[row][col]):
                        color = Colors.ERROR_TEXT
                    elif show_errors and board[row][col] != solution[row][col]:
                        color = Colors.ERROR_TEXT

                value = font.render(str(board[row][col]), True, color)
                screen.blit(value, value.get_rect(center=rect.center))
            # Vẽ các ghi chú nhỏ trong ô trống
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
    # Vẽ đồng hồ bấm giờ và khung chứa thời gian
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
    pygame.draw.rect(screen, Colors.TIMER_BG, panel_rect, border_radius=12)
    pygame.draw.rect(screen, Colors.TIMER_BORDER, panel_rect, width=2, border_radius=12)
    screen.blit(text, text.get_rect(center=panel_rect.center))
    return panel_rect

def draw_button(screen: pygame.Surface, rect, text, mouse_pos, font_to_use, color_scheme='primary'):
    # Vẽ các nút bấm chức năng với hiệu ứng khi di chuột qua (hover)
    colors = {
        'primary': (Colors.BTN_PRIMARY, Colors.BTN_PRIMARY_HOVER),
        'secondary': (Colors.BTN_SECONDARY, Colors.BTN_SECONDARY_HOVER),
        'warning': (Colors.BTN_WARNING, Colors.BTN_WARNING_HOVER),
        'danger': (Colors.BTN_DANGER, Colors.BTN_DANGER_HOVER),
    }
    base_color, hover_color = colors.get(color_scheme, (Colors.BTN_PRIMARY, Colors.BTN_PRIMARY_HOVER))
    color = hover_color if rect.collidepoint(mouse_pos) else base_color

    # Vẽ nút hình viên thuốc (bo tròn hoàn toàn)
    pygame.draw.rect(screen, color, rect, border_radius=rect.height // 2)
    text_surface = font_to_use.render(text, True, (255, 255, 255))
    screen.blit(text_surface, text_surface.get_rect(center=rect.center))
    return rect