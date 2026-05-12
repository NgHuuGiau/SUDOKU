import pygame
import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont
import os
import ctypes
import random
from dataclasses import dataclass
from config import (
    APP_TITLE, MENU_HEADING, MENU_TITLE, VERSION_TEXT,
    chuyen_ngon_ngu, game_text, menu_text
)

try:
    from logic import is_valid_placement
except ImportError:
    is_valid_placement = None

def enable_high_dpi() -> None:
    try:
        ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
    except Exception:
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass

# Định nghĩa các thông số kích thước giao diện
def get_sudoku_icon_path() -> str:
    return os.path.join(os.path.dirname(__file__), "Picture", "SUDOKU.ico")


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


@dataclass(frozen=True)
class GameFonts:
    cell: pygame.font.Font
    small: pygame.font.Font
    medium: pygame.font.Font
    large: pygame.font.Font
    note: pygame.font.Font
    tiny: pygame.font.Font


class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.vx = random.uniform(-4, 4)
        self.vy = random.uniform(-10, 2)
        self.lifetime = 1.0

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.2
        self.lifetime -= 0.02

    def draw(self, screen):
        if self.lifetime > 0:
            alpha = max(0, min(255, int(self.lifetime * 255)))
            radius = max(2, int(4 * self.lifetime))
            glow_radius = radius * 3
            surface_size = glow_radius * 2
            particle_surface = pygame.Surface((surface_size, surface_size), pygame.SRCALPHA)
            center = (glow_radius, glow_radius)
            pygame.draw.circle(particle_surface, (*self.color, alpha // 4), center, glow_radius)
            pygame.draw.circle(particle_surface, (*self.color, alpha), center, radius)
            screen.blit(particle_surface, (int(self.x) - glow_radius, int(self.y) - glow_radius))


def load_fonts() -> GameFonts:
    def get_font(size: int, is_bold: bool = False, is_italic: bool = False) -> pygame.font.Font:
        for font_name in ("segoe ui", "tahoma", "arial"):
            matched_font = pygame.font.match_font(font_name, bold=is_bold, italic=is_italic)
            if matched_font:
                return pygame.font.Font(matched_font, size)
        return pygame.font.SysFont("arial", size, bold=is_bold, italic=is_italic)

    return GameFonts(
        cell=get_font(54, is_bold=True),
        small=get_font(24, is_bold=True),
        medium=get_font(34, is_bold=True),
        large=get_font(48, is_bold=True),
        note=get_font(18, is_bold=True),
        tiny=get_font(18),
    )


def create_game_screen() -> pygame.Surface:
    enable_high_dpi()
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(APP_TITLE)
    try:
        icon_path = os.path.join(os.path.dirname(__file__), "Picture", "SUDOKU.ico")
        pygame.display.set_icon(pygame.image.load(icon_path))
    except Exception:
        pass
    return screen

class Colors:
    # Bảng màu hiện đại cho giao diện Sudoku (Hệ màu Slate/Blue)
    BG_MAIN = (243, 246, 250)
    BG_PANEL = (255, 255, 255)
    BG_BOARD = (255, 255, 255)
    WHITE = (255, 255, 255)
    GRID_NORMAL = (203, 213, 225)
    GRID_BOLD = (51, 65, 85)
    GRID_BORDER = (15, 23, 42)         # Slate 900
    PANEL_BORDER = (203, 213, 225)
    BOARD_SHADOW = (214, 221, 230)
    FIXED_TEXT = (17, 24, 39)
    USER_TEXT = (29, 78, 216)
    ERROR_TEXT = (190, 18, 60)
    HINT_TEXT = (4, 120, 87)
    SELECTED = (186, 230, 253)
    HIGHLIGHT = (232, 240, 254)
    SAME_NUMBER = (254, 249, 195)
    HELP_TEXT = (71, 85, 105)
    BTN_PRIMARY = (29, 78, 216)
    BTN_PRIMARY_HOVER = (30, 64, 175)
    BTN_SECONDARY = (4, 120, 87)
    BTN_SECONDARY_HOVER = (6, 95, 70)
    BTN_WARNING = (180, 83, 9)
    BTN_WARNING_HOVER = (146, 64, 14)
    BTN_DANGER = (185, 28, 28)
    BTN_DANGER_HOVER = (153, 27, 27)
    BUTTON_BORDER = (15, 23, 42)

    # Màu sắc cho các thành phần đặc biệt
    NOTE_BG = (220, 235, 255)          # Light blue note background
    NOTE_TEXT = (71, 85, 105)
    TIMER_BG = (255, 255, 255)
    TIMER_BORDER = (100, 116, 139)
    PAUSE_OVERLAY = (0, 0, 0, 180)
    WIN_GOLD = (255, 215, 0)


MENU_COLORS = {
    'bg': '#f3f6fa',
    'frame': '#1d4ed8',
    'card': '#ffffff',
    'primary': '#1d4ed8',
    'primary_dark': '#1e40af',
    'secondary': '#047857',
    'secondary_dark': '#065f46',
    'warning': '#b45309',
    'warning_dark': '#92400e',
    'danger': '#b91c1c',
    'danger_dark': '#991b1b',
    'text_dark': '#111827',
    'text_muted': '#475569',
    'text_light': '#ffffff',
    'border': '#cbd5e1',
}


def get_timer_rect() -> pygame.Rect:
    return pygame.Rect(PADDING + BOARD_SIZE + PANEL_OFFSET, TOP_MARGIN, PANEL_WIDTH, 60)


def get_cell_from_pos(x: int, y: int):
    if not (PADDING <= x < PADDING + BOARD_SIZE and TOP_MARGIN <= y < TOP_MARGIN + BOARD_SIZE):
        return None
    row = (y - TOP_MARGIN) * 9 // BOARD_SIZE
    col = (x - PADDING) * 9 // BOARD_SIZE
    return (row, col) if 0 <= row < 9 and 0 <= col < 9 else None


def get_sidebar_layout(timer_bottom: int) -> dict:
    x = PADDING + BOARD_SIZE + PANEL_OFFSET + 15
    btn_w = PANEL_WIDTH - 30
    btn_h = 40
    spacing = 8
    y = timer_bottom + 15

    main_buttons = []
    for _ in range(6):
        rect = pygame.Rect(x, y, btn_w, btn_h)
        main_buttons.append(rect)
        y = rect.bottom + spacing

    undo_w = (btn_w - 8) // 2
    undo_rect = pygame.Rect(x, y, undo_w, 40)
    redo_rect = pygame.Rect(undo_rect.right + 8, y, undo_w, 40)

    num_y = undo_rect.bottom + 20
    num_btn_w = (btn_w - 16) // 3
    num_btn_h = 44
    num_pad = 8
    number_buttons = []
    for i in range(9):
        col = i % 3
        row = i // 3
        number_buttons.append(pygame.Rect(
            x + (num_btn_w + num_pad) * col,
            num_y + (num_btn_h + num_pad) * row,
            num_btn_w,
            num_btn_h,
        ))

    clear_w = num_btn_w + 24
    clear_rect = pygame.Rect(x + (btn_w - clear_w) // 2,
                             num_y + (num_btn_h + num_pad) * 3,
                             clear_w, num_btn_h)

    return {
        "main_buttons": main_buttons,
        "undo": undo_rect,
        "redo": redo_rect,
        "numbers": number_buttons,
        "clear": clear_rect,
    }


def get_overlay_button_layout() -> dict:
    win_btn_w = 230
    overlay_btn_h = 52
    gap = 16
    win_total_w = win_btn_w * 2 + gap
    win_start_x = (SCREEN_WIDTH - win_total_w) // 2
    win_start_y = SCREEN_HEIGHT // 2 + 24

    pause_btn_w = 210
    pause_total_w = pause_btn_w * 2 + gap
    pause_start_x = (SCREEN_WIDTH - pause_total_w) // 2
    pause_start_y = SCREEN_HEIGHT // 2 + 24

    return {
        "win_restart": pygame.Rect(win_start_x, win_start_y, win_btn_w, overlay_btn_h),
        "win_quit": pygame.Rect(win_start_x + win_btn_w + gap, win_start_y, win_btn_w, overlay_btn_h),
        "pause_resume": pygame.Rect(pause_start_x, pause_start_y, pause_btn_w, overlay_btn_h),
        "pause_quit": pygame.Rect(pause_start_x + pause_btn_w + gap, pause_start_y, pause_btn_w, overlay_btn_h),
    }


def draw_board_background(screen: pygame.Surface) -> None:
    panel_rect = pygame.Rect(PADDING + BOARD_SIZE + PANEL_OFFSET - 10,
                             TOP_MARGIN - 10, PANEL_WIDTH + 20, SCREEN_HEIGHT - TOP_MARGIN)
    pygame.draw.rect(screen, Colors.BG_PANEL, panel_rect, border_radius=12)
    pygame.draw.rect(screen, Colors.PANEL_BORDER, panel_rect, width=1, border_radius=12)
    board_rect = pygame.Rect(PADDING, TOP_MARGIN, BOARD_SIZE, BOARD_SIZE)
    pygame.draw.rect(screen, Colors.BOARD_SHADOW, board_rect.move(0, 3), border_radius=4)
    pygame.draw.rect(screen, Colors.BG_BOARD, board_rect)

def draw_grid(screen: pygame.Surface) -> None:
    block_size = BOARD_SIZE // 9
    board_rect = pygame.Rect(PADDING, TOP_MARGIN, BOARD_SIZE, BOARD_SIZE)
    for index in range(10):
        thickness = 3 if index % 3 == 0 else 1
        color = Colors.GRID_BOLD if index % 3 == 0 else Colors.GRID_NORMAL
        x = PADDING + index * block_size
        y = TOP_MARGIN + index * block_size
        pygame.draw.line(screen, color, (x, TOP_MARGIN), (x, TOP_MARGIN + BOARD_SIZE), thickness)
        pygame.draw.line(screen, color, (PADDING, y), (PADDING + BOARD_SIZE, y), thickness)
    pygame.draw.rect(screen, Colors.GRID_BORDER, board_rect, width=4)

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

            # Làm nổi bật các ô có cùng giá trị với ô đang chọn (Same Number Highlight)
            if highlight_val is not None and highlight_val != 0 and board[row][col] == highlight_val:
                pygame.draw.rect(screen, Colors.SAME_NUMBER, rect)

            # Vẽ nền cho ô đang được chọn trực tiếp sau cùng để luôn nổi bật.
            if selected_cell == (row, col):
                pygame.draw.rect(screen, Colors.SELECTED, rect)

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
    pygame.draw.rect(screen, Colors.TIMER_BG, panel_rect, border_radius=8)
    pygame.draw.rect(screen, Colors.TIMER_BORDER, panel_rect, width=2, border_radius=8)
    screen.blit(text, text.get_rect(center=panel_rect.center))
    return panel_rect

def _render_fitting_text(text, font_to_use, color, max_width, max_height):
    text_surface = font_to_use.render(text, True, color)
    if text_surface.get_width() <= max_width and text_surface.get_height() <= max_height:
        return text_surface

    start_size = max(12, font_to_use.get_height() - 4)
    for size in range(start_size, 11, -1):
        fallback_font = pygame.font.SysFont("segoe ui", size, bold=True)
        text_surface = fallback_font.render(text, True, color)
        if text_surface.get_width() <= max_width and text_surface.get_height() <= max_height:
            return text_surface
    return text_surface

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

    shadow_rect = rect.move(0, 2)
    pygame.draw.rect(screen, (190, 198, 210), shadow_rect, border_radius=8)
    pygame.draw.rect(screen, color, rect, border_radius=8)
    pygame.draw.rect(screen, Colors.BUTTON_BORDER, rect, width=1, border_radius=8)
    text_surface = _render_fitting_text(text, font_to_use, Colors.WHITE, rect.width - 18, rect.height - 8)
    screen.blit(text_surface, text_surface.get_rect(center=rect.center))
    return rect


def draw_fireworks(screen: pygame.Surface, particles) -> None:
    for particle in particles:
        particle.draw(screen)


def draw_controls(screen: pygame.Surface, fonts: GameFonts, mouse_pos, translate, state, timer_bottom: int) -> dict:
    layout = get_sidebar_layout(timer_bottom)
    buttons_list = [
        (translate('van_moi'), 'warning'),
        (translate('goi_y'), 'secondary'),
        (translate('kiem_tra'), 'secondary'),
        (translate('tam_dung_btn') if not state.paused else translate('tiep_tuc'), 'warning'),
        (translate('ghi_chu') if not state.notes_mode else translate('nhap_so'), 'primary'),
        (translate('ghi_chu_tu_dong'), 'secondary'),
    ]

    for rect, (text, color_scheme) in zip(layout["main_buttons"], buttons_list):
        draw_button(screen, rect, text, mouse_pos, fonts.small, color_scheme)

    draw_button(screen, layout["undo"], translate('hoan_tac'), mouse_pos, fonts.tiny, 'primary')
    draw_button(screen, layout["redo"], translate('lam_lai'), mouse_pos, fonts.tiny, 'primary')

    num_colors = ['primary', 'primary', 'primary', 'secondary', 'secondary', 'secondary', 'warning', 'warning', 'warning']
    for i, rect in enumerate(layout["numbers"]):
        draw_button(screen, rect, str(i + 1), mouse_pos, fonts.medium, num_colors[i])

    draw_button(screen, layout["clear"], translate('xoa_btn'), mouse_pos, fonts.small, 'danger')
    return layout


def draw_game_view(screen: pygame.Surface, fonts: GameFonts, state, mouse_pos, particles=None, translate=game_text) -> dict:
    overlay_rects = {
        "pause_resume": None,
        "pause_quit": None,
        "win_restart": None,
        "win_quit": None,
    }

    screen.fill(Colors.BG_MAIN)
    draw_board_background(screen)

    if not state.game_over:
        r_sel, c_sel = state.selected
        highlight_num = state.board[r_sel][c_sel]
        draw_numbers(screen, fonts.cell, fonts.note, state.board, state.original, state.solution,
                     state.notes, state.show_errors, highlight_val=highlight_num,
                     selected_cell=tuple(state.selected))
        draw_grid(screen)
        if state.selected and not state.paused:
            rect = pygame.Rect(c_sel * CELL_SIZE + PADDING, r_sel * CELL_SIZE + TOP_MARGIN, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, Colors.WIN_GOLD, rect, 4)
    else:
        draw_grid(screen)

    timer_rect = draw_timer(screen, fonts.small, state.game_over, state.paused,
                            state.final_time, state.start_time,
                            state.paused_time, state.last_pause_start)

    if not state.game_over and not state.paused:
        draw_controls(screen, fonts, mouse_pos, translate, state, timer_rect.bottom)
        help_text = f"{translate('move')}  |  {translate('input')}  |  {translate('delete')}"
        text = fonts.tiny.render(help_text, True, Colors.HELP_TEXT)
        screen.blit(text, text.get_rect(center=(PADDING + BOARD_SIZE // 2, SCREEN_HEIGHT - BOTTOM_MARGIN // 2)))

    if state.game_over:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        if particles:
            draw_fireworks(screen, particles)
        win_text = fonts.large.render(translate("chien_thang"), True, Colors.WIN_GOLD)
        screen.blit(win_text, win_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60)))

        overlay_layout = get_overlay_button_layout()
        overlay_rects["win_restart"] = overlay_layout["win_restart"]
        overlay_rects["win_quit"] = overlay_layout["win_quit"]
        draw_button(screen, overlay_layout["win_restart"], translate("choi_tiep"), mouse_pos, fonts.small, 'warning')
        draw_button(screen, overlay_layout["win_quit"], translate("thoat_ve_menu"), mouse_pos, fonts.small, 'danger')

    if state.paused:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill(Colors.PAUSE_OVERLAY)
        screen.blit(overlay, (0, 0))
        pause_text = fonts.large.render(translate("tam_dung"), True, Colors.WHITE)
        screen.blit(pause_text, pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)))

        overlay_layout = get_overlay_button_layout()
        overlay_rects["pause_resume"] = overlay_layout["pause_resume"]
        overlay_rects["pause_quit"] = overlay_layout["pause_quit"]
        draw_button(screen, overlay_layout["pause_resume"], translate("tiep_tuc"), mouse_pos, fonts.small, 'warning')
        draw_button(screen, overlay_layout["pause_quit"], translate("thoat"), mouse_pos, fonts.small, 'danger')

    pygame.display.flip()
    return overlay_rects


class MenuSudoku:
    def __init__(self, start_game_func):
        self.start_game_func = start_game_func
        self.root = tk.Tk()
        self.root.title(MENU_TITLE)
        self.root.configure(bg=MENU_COLORS['bg'])
        self.root.resizable(False, False)
        self._tao_font_menu()
        try:
            icon_path = os.path.join(os.path.dirname(__file__), "Picture", "SUDOKU.ico")
            self.root.iconbitmap(icon_path)
        except Exception:
            pass
        self._cai_dat_kieu()
        self._tao_cac_widget()
        self._canh_giua_cua_so()

    def _tao_font_menu(self):
        self.menu_fonts = {
            "default": tkfont.Font(root=self.root, family="Segoe UI", size=10),
            "button": tkfont.Font(root=self.root, family="Segoe UI", size=12, weight="bold"),
            "title": tkfont.Font(root=self.root, family="Segoe UI", size=34, weight="bold"),
            "subtitle": tkfont.Font(root=self.root, family="Segoe UI", size=13),
            "section": tkfont.Font(root=self.root, family="Segoe UI", size=18, weight="bold"),
            "footer": tkfont.Font(root=self.root, family="Segoe UI", size=10),
            "version": tkfont.Font(root=self.root, family="Segoe UI", size=8),
        }
        self.root.option_add("*Font", self.menu_fonts["default"])

    def _cai_dat_kieu(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('.', font=self.menu_fonts["default"])

        def configure_button(style_name, bg, active_bg):
            style.configure(style_name, font=self.menu_fonts["button"],
                            background=bg, foreground=MENU_COLORS['text_light'],
                            borderwidth=1, focusthickness=1, focuscolor=active_bg,
                            padding=(14, 10))
            style.map(style_name,
                      background=[('active', active_bg), ('pressed', active_bg)],
                      foreground=[('disabled', '#e5e7eb'), ('active', MENU_COLORS['text_light'])])

        configure_button('Easy.TButton', MENU_COLORS['secondary'], MENU_COLORS['secondary_dark'])
        configure_button('Medium.TButton', MENU_COLORS['warning'], MENU_COLORS['warning_dark'])
        configure_button('Hard.TButton', MENU_COLORS['danger'], MENU_COLORS['danger_dark'])
        configure_button('Language.TButton', MENU_COLORS['primary'], MENU_COLORS['primary_dark'])

    def _tao_cac_widget(self):
        main_frame = tk.Frame(self.root, bg=MENU_COLORS['bg'])
        main_frame.pack(expand=True, fill=tk.BOTH)
        top_bar = tk.Frame(main_frame, bg=MENU_COLORS['frame'], height=5)
        top_bar.pack(fill=tk.X)
        card = tk.Frame(main_frame, bg=MENU_COLORS['card'], padx=42, pady=24,
                        highlightbackground=MENU_COLORS['border'], highlightthickness=1)
        card.pack(expand=True, fill=tk.BOTH, padx=28, pady=(24, 26))
        title_label = tk.Label(card, text=MENU_HEADING,
                               font=self.menu_fonts["title"], bg=MENU_COLORS['card'],
                               fg=MENU_COLORS['text_dark'])
        title_label.pack(pady=(0, 8))
        self.phu_de = tk.Label(card, text=menu_text("thu_thach"), font=self.menu_fonts["subtitle"],
                               bg=MENU_COLORS['card'], fg=MENU_COLORS['text_muted'])
        self.phu_de.pack(pady=(0, 15))
        dai_phan_cach = tk.Frame(card, height=1, bg=MENU_COLORS['border'])
        dai_phan_cach.pack(fill=tk.X, pady=(0, 25))
        self.nhan_chon_do_kho = tk.Label(card, text=menu_text("chon_do_kho"),
                                          font=self.menu_fonts["section"],
                                          bg=MENU_COLORS['card'], fg=MENU_COLORS['text_dark'])
        self.nhan_chon_do_kho.pack(pady=(0, 20))
        chieu_rong_nut = 20
        self.nut_de = ttk.Button(card, text=menu_text('de'),
                                 command=lambda: self._bat_dau_tro_choi("easy"),
                                 style='Easy.TButton', width=chieu_rong_nut, takefocus=False)
        self.nut_de.pack(pady=5)
        self.nut_trung_binh = ttk.Button(card, text=menu_text('trung_binh'),
                                         command=lambda: self._bat_dau_tro_choi("medium"),
                                         style='Medium.TButton', width=chieu_rong_nut, takefocus=False)
        self.nut_trung_binh.pack(pady=5)
        self.nut_kho = ttk.Button(card, text=menu_text('kho'),
                                  command=lambda: self._bat_dau_tro_choi("hard"),
                                  style='Hard.TButton', width=chieu_rong_nut, takefocus=False)
        self.nut_kho.pack(pady=5)
        self.nut_ngon_ngu = ttk.Button(card, text=menu_text('ngon_ngu'),
                                       command=self._chuyen_ngon_ngu,
                                       style='Language.TButton', width=chieu_rong_nut, takefocus=False)
        self.nut_ngon_ngu.pack(pady=5)
        khung_chan_trang = tk.Frame(card, bg=MENU_COLORS['card'])
        khung_chan_trang.pack(pady=(15, 0))
        self.chan_trang = tk.Label(khung_chan_trang, text=menu_text("chuc_vui_ve"),
                                   font=self.menu_fonts["footer"],
                                   bg=MENU_COLORS['card'], fg=MENU_COLORS['text_muted'])
        self.chan_trang.pack()
        phien_ban = tk.Label(khung_chan_trang, text=VERSION_TEXT, font=self.menu_fonts["version"],
                             bg=MENU_COLORS['card'], fg='#94a3b8')
        phien_ban.pack()

    def _chuyen_ngon_ngu(self):
        chuyen_ngon_ngu()
        self._cap_nhat_van_ban()

    def _cap_nhat_van_ban(self):
        self.phu_de.config(text=menu_text("thu_thach"))
        self.nhan_chon_do_kho.config(text=menu_text("chon_do_kho"))
        self.nut_de.config(text=menu_text('de'))
        self.nut_trung_binh.config(text=menu_text('trung_binh'))
        self.nut_kho.config(text=menu_text('kho'))
        self.chan_trang.config(text=menu_text("chuc_vui_ve"))
        self.nut_ngon_ngu.config(text=menu_text('ngon_ngu'))

    def _canh_giua_cua_so(self):
        self.root.update_idletasks()
        chieu_rong = 550
        chieu_cao = 650
        x = (self.root.winfo_screenwidth() // 2) - (chieu_rong // 2)
        y = (self.root.winfo_screenheight() // 2) - (chieu_cao // 2)
        self.root.geometry(f'{chieu_rong}x{chieu_cao}+{x}+{y}')

    def _bat_dau_tro_choi(self, do_kho):
        self.root.withdraw()
        thang = self.start_game_func(self.root, do_kho)
        self.root.deiconify()
        if thang:
            if not messagebox.askyesno(menu_text("chien_thang"), menu_text("chuc_mung")):
                self.root.destroy()

    def chay(self):
        self.root.mainloop()


def tao_nut_bat_dau(start_game_func=None):
    enable_high_dpi()
    if start_game_func is None:
        from game import start_game
        start_game_func = start_game
    menu = MenuSudoku(start_game_func)
    menu.chay()
