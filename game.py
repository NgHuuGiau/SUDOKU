# Quản lý logic vòng lặp trò chơi, sự kiện người dùng và hiển thị chính
import pygame
import copy
import random
import os
from typing import List, Set, Tuple, Optional
from logic import generate_sudoku, is_valid_placement, check_win
from ui import (
    SCREEN_WIDTH, SCREEN_HEIGHT, BOARD_SIZE, PADDING, PANEL_OFFSET,
    TOP_MARGIN, BOTTOM_MARGIN, PANEL_WIDTH, CELL_SIZE, Colors, init_display,
    draw_grid, draw_numbers, draw_timer, draw_button
)
import config

GAME_DICT = {
    "en": {
        "move": "WASD: Move",
        "input": "1-9: Input",
        "delete": "Backspace: Delete",
        "chien_thang": "Victory!",
        "nhan_phim_bat_ky": "Press any key to return to Menu",
        "tam_dung": "PAUSED",
        "tiep_tuc": "RESUME",
        "van_moi": "New Game",
        "goi_y": "Hint",
        "kiem_tra": "Check",
        "tam_dung_btn": "Pause",
        "ghi_chu": "Notes",
        "nhap_so": "Input",
        "ghi_chu_tu_dong": "Auto Notes",
        "hoan_tac": "Undo",
        "lam_lai": "Redo",
        "xoa_btn": "Clear",
        "thoat": "Quit",
        "choi_tiep": "Play Again",
        "thoat_ve_menu": "Back to Menu",
    },
    "vi": {
        "move": "WASD: Di chuyển",
        "input": "1-9: Nhập",
        "delete": "Backspace: Xóa",
        "chien_thang": "Chiến Thắng!",
        "nhan_phim_bat_ky": "Nhấn phím bất kỳ để quay lại Menu",
        "tam_dung": "ĐANG TẠM DỪNG",
        "tiep_tuc": "TIẾP TỤC",
        "van_moi": "Ván mới",
        "goi_y": "Gợi ý",
        "kiem_tra": "Kiểm tra",
        "tam_dung_btn": "Tạm dừng",
        "ghi_chu": "Ghi chú",
        "nhap_so": "Nhập số",
        "ghi_chu_tu_dong": "Ghi chú tự động",
        "hoan_tac": "Hoàn tác",
        "lam_lai": "Làm lại",
        "xoa_btn": "Xóa",
        "thoat": "Thoát",
        "choi_tiep": "Chơi tiếp",
        "thoat_ve_menu": "Về Menu",
    },
}

def _(khoa):
    return GAME_DICT[config.ngon_ngu_hien_tai][khoa]

Board = List[List[int]]
NotesBoard = List[List[Set[int]]]
Difficulty = str

screen: pygame.Surface | None = None
font: pygame.font.Font | None = None
small_font: pygame.font.Font | None = None
medium_font: pygame.font.Font | None = None
large_font: pygame.font.Font | None = None
note_font: pygame.font.Font | None = None
tiny_font: pygame.font.Font | None = None

def init_display(screen_obj: pygame.Surface, fonts: tuple) -> None:
    global screen, font, small_font, medium_font, large_font, note_font, tiny_font
    screen = screen_obj
    font, small_font, medium_font, large_font, note_font, tiny_font = fonts

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
            alpha = int(self.lifetime * 255)
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 3)

class GameState:
    def __init__(self, difficulty: Difficulty):
        self.difficulty = difficulty
        self.board, self.solution = generate_sudoku(difficulty)
        self.original = [row[:] for row in self.board]
        self.selected = [0, 0]
        self.notes: List[List[Set[int]]] = [[set() for _ in range(9)] for _ in range(9)]
        self.notes_mode = False
        self.game_over = False
        self.paused = False
        self.show_errors = False
        self.start_time = pygame.time.get_ticks()
        self.paused_time = 0
        self.last_pause_start = 0
        self.last_active_time = 0
        self.final_time = 0
        self.undo_stack: List[Tuple[Board, List[List[Set[int]]]]] = [
            (copy.deepcopy(self.board), copy.deepcopy(self.notes))
        ]
        self.redo_stack: List[Tuple[Board, List[List[Set[int]]]]] = []

    def get_cell_from_pos(self, x: int, y: int) -> Optional[Tuple[int, int]]:
        if not (PADDING <= x < PADDING + BOARD_SIZE and TOP_MARGIN <= y < TOP_MARGIN + BOARD_SIZE):
            return None
        row = (y - TOP_MARGIN) * 9 // BOARD_SIZE
        col = (x - PADDING) * 9 // BOARD_SIZE
        return (row, col) if 0 <= row < 9 and 0 <= col < 9 else None

    def save_state(self) -> None:
        current = (copy.deepcopy(self.board), copy.deepcopy(self.notes))
        if not self.undo_stack or self.undo_stack[-1] != current:
            self.undo_stack.append(current)
            self.redo_stack.clear()

    def undo(self) -> None:
        if len(self.undo_stack) > 1:
            self.redo_stack.append((copy.deepcopy(self.board), copy.deepcopy(self.notes)))
            self.board, self.notes = self.undo_stack.pop()
            self.board = copy.deepcopy(self.board)
            for r in range(9):
                for c in range(9):
                    self.notes[r][c] = copy.deepcopy(self.notes[r][c])

    def redo(self) -> None:
        if self.redo_stack:
            board_state, notes_state = self.redo_stack.pop()
            self.undo_stack.append((copy.deepcopy(self.board), copy.deepcopy(self.notes)))
            self.board = board_state
            self.notes = copy.deepcopy(notes_state)

    def place_number(self, num: int) -> None:
        r, c = self.selected
        if self.original[r][c] != 0:
            return
        if self.notes_mode:
            if num in self.notes[r][c]:
                self.notes[r][c].remove(num)
            else:
                self.notes[r][c].add(num)
        else:
            self.board[r][c] = num
            self.notes[r][c].clear()
            self.save_state()

    def clear_cell(self) -> None:
        r, c = self.selected
        if self.original[r][c] != 0:
            return
        if self.notes_mode:
            self.notes[r][c].clear()
        else:
            self.board[r][c] = 0
            self.save_state()

    def give_hint(self) -> None:
        r, c = self.selected
        if self.original[r][c] == 0 and self.board[r][c] == 0:
            self.board[r][c] = self.solution[r][c]
            self.notes[r][c].clear()
            self.save_state()

    def fill_possible_notes(self) -> None:
        for r in range(9):
            for c in range(9):
                self.notes[r][c].clear()
        for r in range(9):
            for c in range(9):
                if self.board[r][c] == 0:
                    for num in range(1, 10):
                        if is_valid_placement(self.board, r, c, num):
                            self.notes[r][c].add(num)
        self.save_state()

    def toggle_pause(self) -> None:
        self.paused = not self.paused
        if self.paused:
            self.last_pause_start = pygame.time.get_ticks()
        else:
            self.paused_time += pygame.time.get_ticks() - self.last_pause_start

    def restart(self, difficulty: Difficulty) -> None:
        self.difficulty = difficulty
        self.board, self.solution = generate_sudoku(difficulty)
        self.original = [row[:] for row in self.board]
        self.selected = [0, 0]
        self.notes = [[set() for _ in range(9)] for _ in range(9)]
        self.notes_mode = False
        self.game_over = False
        self.paused = False
        self.show_errors = False
        self.start_time = pygame.time.get_ticks()
        self.paused_time = 0
        self.last_pause_start = 0
        self.last_active_time = 0
        self.final_time = 0
        self.undo_stack = [(copy.deepcopy(self.board), copy.deepcopy(self.notes))]
        self.redo_stack.clear()

    def get_elapsed_time(self) -> int:
        if self.game_over:
            return self.final_time
        if self.paused:
            return max(0, (self.last_pause_start - self.start_time - self.paused_time) // 1000)
        return max(0, (pygame.time.get_ticks() - self.start_time - self.paused_time) // 1000)

class Game:
    def __init__(self, difficulty: Difficulty = "medium"):
        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Sudoku")
        self._load_icon()
        self._load_fonts()
        self.state = GameState(difficulty)
        self.particles: List[Particle] = []
        self.sounds = {}
        self._init_sounds()
        self.running = True
        self.quit_requested = False
        # Rects for overlay buttons
        self.pause_resume_rect = None
        self.pause_quit_rect = None
        self.win_restart_rect = None
        self.win_quit_rect = None

    def _init_sounds(self) -> None:
        try:
            sound_files = {'win': 'sounds/applause.wav'}
            for name, path in sound_files.items():
                if os.path.exists(path):
                    self.sounds[name] = pygame.mixer.Sound(path)
        except Exception:
            pass

    def _load_icon(self) -> None:
        try:
            icon_path = f"Picture/SUDOKU.ico"
            pygame.display.set_icon(pygame.image.load(icon_path))
        except Exception:
            pass

    def _load_fonts(self) -> None:
        custom_font_path = "VN-Times.ttf"
        system_font_names = ["segoe ui", "tahoma", "arial"]
        def get_font(size: int, is_bold: bool = False, is_italic: bool = False) -> pygame.font.Font:
            try:
                if os.path.exists(custom_font_path):
                    return pygame.font.Font(custom_font_path, size)
            except Exception:
                pass
            return pygame.font.SysFont(system_font_names, size, bold=is_bold, italic=is_italic)
        self.font = get_font(BOARD_SIZE // 11)
        self.small_font = get_font(26)
        self.medium_font = get_font(38)
        self.large_font = get_font(50)
        self.note_font = get_font(18)
        self.tiny_font = get_font(22)

    def handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return False

            if self.state.game_over:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self._handle_gameover_click(event.pos)
                continue

            if self.state.paused:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self._handle_pause_click(event.pos)
                continue

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.state.toggle_pause()
                return True

            if event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_mouse(event.pos)

            if event.type == pygame.KEYDOWN:
                self._handle_keyboard(event)

        return True

    def _handle_gameover_click(self, pos):
        x, y = pos
        if self.win_restart_rect and self.win_restart_rect.collidepoint(x, y):
            self.state.restart(self.state.difficulty)
        if self.win_quit_rect and self.win_quit_rect.collidepoint(x, y):
            self.running = False
            self.quit_requested = True

    def _handle_pause_click(self, pos):
        x, y = pos
        if self.pause_resume_rect and self.pause_resume_rect.collidepoint(x, y):
            self.state.toggle_pause()
        if self.pause_quit_rect and self.pause_quit_rect.collidepoint(x, y):
            self.running = False
            self.quit_requested = True

    def _handle_mouse(self, pos: Tuple[int, int]) -> None:
        x, y = pos
        timer_rect = pygame.Rect(PADDING + BOARD_SIZE + PANEL_OFFSET, TOP_MARGIN, PANEL_WIDTH, 60)
        restart_rect = pygame.Rect(PADDING + BOARD_SIZE + PANEL_OFFSET + 15,
                                    timer_rect.bottom + 10, PANEL_WIDTH - 30, 42)
        if restart_rect.collidepoint(x, y):
            self.state.restart(self.state.difficulty)
            return
        if not self.state.paused and not self.state.game_over:
            cell = self.state.get_cell_from_pos(x, y)
            if cell:
                self.state.selected = list(cell)
                return
        btn_w = PANEL_WIDTH - 20
        btn_h = 38
        spacing = 8
        current_y = restart_rect.bottom + 8
        buttons = [
            self.state.give_hint,
            lambda: setattr(self.state, 'show_errors', not self.state.show_errors),
            self.state.toggle_pause,
            lambda: setattr(self.state, 'notes_mode', not self.state.notes_mode),
            self.state.fill_possible_notes,
        ]
        for action in buttons:
            rect = pygame.Rect(PADDING + BOARD_SIZE + PANEL_OFFSET + 15,
                              current_y, btn_w, btn_h)
            if rect.collidepoint(x, y):
                action()
                return
            current_y = rect.bottom + spacing
        undo_w = (btn_w - 8) // 2
        undo_rect = pygame.Rect(PADDING + BOARD_SIZE + PANEL_OFFSET + 15,
                                current_y, undo_w, 40)
        redo_rect = pygame.Rect(undo_rect.right + 8, current_y, undo_w, 40)
        if undo_rect.collidepoint(x, y):
            self.state.undo()
            return
        if redo_rect.collidepoint(x, y):
            self.state.redo()
            return
        num_y = undo_rect.bottom + 20
        num_btn_w = (PANEL_WIDTH - 40) // 3
        num_btn_h = 44
        num_pad = 8
        for i in range(9):
            num = i + 1
            col_idx = i % 3
            row_idx = i // 3
            num_rect = pygame.Rect(
                PADDING + BOARD_SIZE + PANEL_OFFSET + 15 + (num_btn_w + num_pad) * col_idx,
                num_y + (num_btn_h + num_pad) * row_idx,
                num_btn_w, num_btn_h)
            if num_rect.collidepoint(x, y):
                self.state.place_number(num)
                return
        clear_rect = pygame.Rect(
            PADDING + BOARD_SIZE + PANEL_OFFSET + 15 + (num_btn_w + num_pad) * 1,
            num_y + (num_btn_h + num_pad) * 3,
            num_btn_w + 20, num_btn_h)
        if clear_rect.collidepoint(x, y):
            self.state.clear_cell()
            return

    def _handle_keyboard(self, event) -> None:
        r, c = self.state.selected
        key = event.key
        if key in (pygame.K_UP, pygame.K_w) and r > 0:
            self.state.selected[0] -= 1
        elif key in (pygame.K_DOWN, pygame.K_s) and r < 8:
            self.state.selected[0] += 1
        elif key in (pygame.K_LEFT, pygame.K_a) and c > 0:
            self.state.selected[1] -= 1
        elif key in (pygame.K_RIGHT, pygame.K_d) and c < 8:
            self.state.selected[1] += 1
        elif self.state.original[r][c] == 0:
            if event.unicode.isdigit() and 1 <= int(event.unicode) <= 9:
                self.state.place_number(int(event.unicode))
            elif key in (pygame.K_BACKSPACE, pygame.K_DELETE, pygame.K_KP0):
                self.state.clear_cell()

    def update(self) -> None:
        if self.state.game_over:
            if random.random() < 0.15:
                color = (random.randint(150, 255), random.randint(150, 255), random.randint(150, 255))
                x, y = random.randint(50, SCREEN_WIDTH-50), random.randint(50, SCREEN_HEIGHT-150)
                for _ in range(30):
                    self.particles.append(Particle(x, y, color))
            for p in self.particles[:]:
                p.update()
                if p.lifetime <= 0:
                    self.particles.remove(p)
        if not self.state.game_over and check_win(self.state.board, self.state.solution):
            self.state.game_over = True
            self.state.final_time = self.state.get_elapsed_time()
            if 'win' in self.sounds:
                self.sounds['win'].play()

    def render(self) -> None:
        self.screen.fill(Colors.BG_MAIN)
        panel_rect = pygame.Rect(PADDING + BOARD_SIZE + PANEL_OFFSET - 10,
                                  TOP_MARGIN - 10, PANEL_WIDTH + 20, SCREEN_HEIGHT - TOP_MARGIN)
        pygame.draw.rect(self.screen, Colors.BG_PANEL, panel_rect, border_radius=20)
        draw_grid(self.screen)
        if self.state.selected and not self.state.paused and not self.state.game_over:
            r, c = self.state.selected
            rect = pygame.Rect(c * CELL_SIZE + PADDING, r * CELL_SIZE + TOP_MARGIN, CELL_SIZE, CELL_SIZE)
            color = (Colors.SELECTED if self.state.original[r][c] == 0 else Colors.HIGHLIGHT)
            pygame.draw.rect(self.screen, color, rect, border_radius=12)
        if not self.state.game_over:
            r_sel, c_sel = self.state.selected
            highlight_num = self.state.board[r_sel][c_sel]
            draw_numbers(self.screen, self.font, self.note_font, self.state.board, self.state.original, self.state.solution,
                        self.state.notes, self.state.show_errors, highlight_val=highlight_num)
            if self.state.selected and not self.state.paused:
                rect = pygame.Rect(c_sel * CELL_SIZE + PADDING, r_sel * CELL_SIZE + TOP_MARGIN, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(self.screen, Colors.WIN_GOLD, rect, 4, border_radius=12)
        mouse_pos = pygame.mouse.get_pos()
        timer_rect = draw_timer(self.screen, self.small_font, self.state.game_over, self.state.paused,
                               self.state.final_time, self.state.start_time,
                               self.state.paused_time, self.state.last_pause_start)
        if not self.state.game_over and not self.state.paused:
            self._draw_controls(mouse_pos, timer_rect.bottom)
            help_text = f"{_('move')}  |  {_('input')}  |  {_('delete')}"
            text = self.tiny_font.render(help_text, True, (100, 110, 120))
            self.screen.blit(text, text.get_rect(
                center=(PADDING + BOARD_SIZE // 2, SCREEN_HEIGHT - BOTTOM_MARGIN // 2)))
        # Game Over overlay
        if self.state.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0, 0))
            win_text = self.large_font.render(_("chien_thang"), True, Colors.WIN_GOLD)
            self.screen.blit(win_text, win_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60)))
            btn_w = 220
            btn_h = 50
            gap = 20
            total_w = btn_w * 2 + gap
            start_x = (SCREEN_WIDTH - total_w) // 2
            start_y = SCREEN_HEIGHT // 2 + 10
            self.win_restart_rect = pygame.Rect(start_x, start_y, btn_w, btn_h)
            self.win_quit_rect = pygame.Rect(start_x + btn_w + gap, start_y, btn_w, btn_h)
            draw_button(self.screen, self.win_restart_rect, _("choi_tiep"), mouse_pos, self.small_font, 'warning')
            draw_button(self.screen, self.win_quit_rect, _("thoat_ve_menu"), mouse_pos, self.small_font, 'danger')
        # Pause overlay
        if self.state.paused:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill(Colors.PAUSE_OVERLAY)
            self.screen.blit(overlay, (0, 0))
            pause_text = self.large_font.render(_("tam_dung"), True, Colors.WHITE)
            self.screen.blit(pause_text, pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)))
            btn_w = 200
            btn_h = 50
            gap = 20
            total_w = btn_w * 2 + gap
            start_x = (SCREEN_WIDTH - total_w) // 2
            start_y = SCREEN_HEIGHT // 2 + 20
            self.pause_resume_rect = pygame.Rect(start_x, start_y, btn_w, btn_h)
            self.pause_quit_rect = pygame.Rect(start_x + btn_w + gap, start_y, btn_w, btn_h)
            draw_button(self.screen, self.pause_resume_rect, _("tiep_tuc"), mouse_pos, self.small_font, 'warning')
            draw_button(self.screen, self.pause_quit_rect, _("thoat"), mouse_pos, self.small_font, 'danger')
        pygame.display.flip()

    def _draw_controls(self, mouse_pos, start_y):
        y = start_y + 15
        buttons_list = [
            (_('van_moi'), lambda: self.state.restart(self.state.difficulty), 'warning'),
            (_('goi_y'), self.state.give_hint, 'secondary'),
            (_('kiem_tra'), lambda: setattr(self.state, 'show_errors', not self.state.show_errors), 'secondary'),
            (_('tam_dung_btn') if not self.state.paused else _('tiep_tuc'), self.state.toggle_pause, 'warning'),
            (_('ghi_chu') if not self.state.notes_mode else _('nhap_so'), lambda: setattr(self.state, 'notes_mode', not self.state.notes_mode), 'primary'),
            (_('ghi_chu_tu_dong'), self.state.fill_possible_notes, 'secondary'),
        ]
        btn_w = PANEL_WIDTH - 20
        btn_h = 38
        for text, action, color_scheme in buttons_list:
            rect = draw_button(self.screen, pygame.Rect(PADDING + BOARD_SIZE + PANEL_OFFSET + 15, y, btn_w, btn_h),
                              text, mouse_pos, self.small_font, color_scheme)
            y = rect.bottom + 8
        hoan_tac_rong = (btn_w - 8) // 2
        hoan_tac_hcn = draw_button(self.screen, pygame.Rect(PADDING + BOARD_SIZE + PANEL_OFFSET + 15, y, hoan_tac_rong, 40),
                                _('hoan_tac'), mouse_pos, self.tiny_font, 'primary')
        draw_button(self.screen, pygame.Rect(hoan_tac_hcn.right + 8, y, hoan_tac_rong, 40),
                    _('lam_lai'), mouse_pos, self.tiny_font, 'primary')
        y = hoan_tac_hcn.bottom + 20
        num_btn_w = (PANEL_WIDTH - 40) // 3
        num_btn_h = 44
        num_pad = 8
        num_colors = ['primary', 'primary', 'primary', 'secondary', 'secondary', 'secondary', 'warning', 'warning', 'warning']
        for i in range(9):
            num = i + 1
            col = i % 3
            row = i // 3
            x = PADDING + BOARD_SIZE + PANEL_OFFSET + 15 + (num_btn_w + num_pad) * col
            rect = pygame.Rect(x, y + (num_btn_h + num_pad) * row, num_btn_w, num_btn_h)
            draw_button(self.screen, rect, str(num), mouse_pos, self.medium_font, num_colors[i])
        clear_rect = pygame.Rect(PADDING + BOARD_SIZE + PANEL_OFFSET + 15 + (num_btn_w + num_pad) * 1,
                                  y + (num_btn_h + num_pad) * 3, num_btn_w + 20, num_btn_h)
        draw_button(self.screen, clear_rect, _('xoa_btn'), mouse_pos, self.small_font, 'danger')

    def run(self) -> bool:
        clock = pygame.time.Clock()
        while self.running:
            if not self.handle_events():
                break
            self.update()
            self.render()
            clock.tick(60)
        pygame.quit()
        return self.state.game_over and not self.quit_requested

def start_game(root, difficulty: str = "medium") -> bool:
    game = Game(difficulty)
    return game.run()
