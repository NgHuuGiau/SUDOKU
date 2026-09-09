import copy
import random
import time
from typing import List, Set, Tuple

import pygame

from logic import check_win, generate_sudoku, is_valid_placement
from ui import (
    Particle,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    create_game_screen,
    draw_game_view,
    get_cell_from_pos,
    get_sidebar_layout,
    get_timer_rect,
    load_fonts,
)
from persistence import (
    load_best_times,
    save_best_times,
    update_best_time,
    get_best_time,
    save_game_state,
    load_game_state,
    clear_save_file,
    has_save_file,
    record_game_win,
    is_top_10_time,
)
from sounds import get_sound_manager, play_sound

Board = List[List[int]]
NotesBoard = List[List[Set[int]]]
Difficulty = str

AUTO_SAVE_DEBOUNCE_MS = 500


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
        self._last_auto_save_time = 0.0
        save_game_state(self)

    def save_state(self) -> None:
        current = (copy.deepcopy(self.board), copy.deepcopy(self.notes))
        if not self.undo_stack or self.undo_stack[-1] != current:
            self.undo_stack.append(current)
            self.redo_stack.clear()

    def undo(self) -> None:
        if len(self.undo_stack) > 1:
            self.redo_stack.append((copy.deepcopy(self.board), copy.deepcopy(self.notes)))
            self.undo_stack.pop()
            self.board, self.notes = self.undo_stack[-1]
            self.board = copy.deepcopy(self.board)
            for r in range(9):
                for c in range(9):
                    self.notes[r][c] = copy.deepcopy(self.notes[r][c])
            play_sound('undo')
        self.auto_save()

    def redo(self) -> None:
        if self.redo_stack:
            board_state, notes_state = self.redo_stack.pop()
            self.undo_stack.append((copy.deepcopy(self.board), copy.deepcopy(self.notes)))
            self.board = board_state
            self.notes = copy.deepcopy(notes_state)
            play_sound('pop')
        self.auto_save()

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
            play_sound('pop')
        self.auto_save()

    def clear_cell(self) -> None:
        r, c = self.selected
        if self.original[r][c] != 0:
            return
        if self.notes_mode:
            self.notes[r][c].clear()
        else:
            self.board[r][c] = 0
            self.save_state()
            play_sound('click')
        self.auto_save()

    def give_hint(self) -> None:
        r, c = self.selected
        if self.original[r][c] == 0 and self.board[r][c] == 0:
            self.board[r][c] = self.solution[r][c]
            self.notes[r][c].clear()
            self.save_state()
            play_sound('hint')
        self.auto_save()

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
        play_sound('click')
        self.auto_save()

    def toggle_pause(self) -> None:
        self.paused = not self.paused
        if self.paused:
            self.last_pause_start = pygame.time.get_ticks()
        else:
            self.paused_time += pygame.time.get_ticks() - self.last_pause_start
        play_sound('click')

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
        self._last_auto_save_time = 0.0
        save_game_state(self)
        play_sound('click')

    def auto_save(self) -> None:
        if self.game_over:
            return
        now = time.monotonic() * 1000
        if now - self._last_auto_save_time >= AUTO_SAVE_DEBOUNCE_MS:
            save_game_state(self)
            self._last_auto_save_time = now

    def force_save(self) -> None:
        """Immediate save without debounce (for critical moments)."""
        if not self.game_over:
            save_game_state(self)
            self._last_auto_save_time = time.monotonic() * 1000

    def get_elapsed_time(self) -> int:
        if self.game_over:
            return self.final_time
        if self.paused:
            return max(0, (self.last_pause_start - self.start_time - self.paused_time) // 1000)
        return max(0, (pygame.time.get_ticks() - self.start_time - self.paused_time) // 1000)


class Game:
    def __init__(self, difficulty: Difficulty = "medium"):
        self.screen = create_game_screen()
        self._load_fonts()
        self.state = GameState(difficulty)
        self.particles: List[Particle] = []
        self.sound_manager = get_sound_manager()
        self.running = True
        self.quit_requested = False
        self.pause_resume_rect = None
        self.pause_quit_rect = None
        self.win_restart_rect = None
        self.win_quit_rect = None
        self.header_pause_rect = None
        self.help_rects = None
        self.show_help = False

    def _load_fonts(self) -> None:
        self.fonts = load_fonts()

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
                if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_p):
                    self.state.toggle_pause()
                continue

            if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_p):
                self.state.toggle_pause()
                return True

            if event.type == pygame.KEYDOWN and event.key == pygame.K_F1:
                self.show_help = not self.show_help
                return True

            if self.show_help:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self._handle_help_click(event.pos)
                continue

            if event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_mouse(event.pos)

            if event.type == pygame.KEYDOWN:
                self._handle_keyboard(event)

        return True

    def _handle_gameover_click(self, pos):
        x, y = pos
        if self.win_restart_rect and self.win_restart_rect.collidepoint(x, y):
            self._restart_game()
        if self.win_quit_rect and self.win_quit_rect.collidepoint(x, y):
            self.running = False
            self.quit_requested = True

    def _handle_pause_click(self, pos):
        x, y = pos
        if self.pause_resume_rect and self.pause_resume_rect.collidepoint(x, y):
            self.state.toggle_pause()
        if self.pause_restart_rect and self.pause_restart_rect.collidepoint(x, y):
            self._restart_game()
        if self.pause_save_quit_rect and self.pause_save_quit_rect.collidepoint(x, y):
            self.state.force_save()
            self.running = False
            self.quit_requested = True
        # Backward compat
        if self.pause_quit_rect and self.pause_quit_rect.collidepoint(x, y):
            self.running = False
            self.quit_requested = True

    def _handle_help_click(self, pos):
        x, y = pos
        if self.help_rects and self.help_rects.get("help_close") and self.help_rects["help_close"].collidepoint(x, y):
            self.show_help = False

    def _handle_mouse(self, pos: Tuple[int, int]) -> None:
        x, y = pos

        # 1. Nút Tạm dừng trên thanh Header
        if self.header_pause_rect and self.header_pause_rect.collidepoint(x, y):
            self.state.toggle_pause()
            return

        if not self.state.paused and not self.state.game_over:
            # 2. Chọn ô trên bàn cờ
            cell = get_cell_from_pos(x, y)
            if cell:
                self.state.selected = list(cell)
                return

            # 3. Các nút trên Sidebar
            layout = get_sidebar_layout()

            if layout["quick_undo"].collidepoint(x, y):
                self.state.undo()
                return
            if layout["quick_redo"].collidepoint(x, y):
                self.state.redo()
                return
            if layout["quick_notes"].collidepoint(x, y):
                self.state.notes_mode = not self.state.notes_mode
                return
            if layout["quick_hint"].collidepoint(x, y):
                self.state.give_hint()
                return
            if layout["quick_check_errors"].collidepoint(x, y):
                self.state.show_errors = not self.state.show_errors
                self.state.auto_save()
                return

            if layout["clear"].collidepoint(x, y):
                self.state.clear_cell()
                return
            if layout["auto_notes"].collidepoint(x, y):
                self.state.fill_possible_notes()
                return

            for i, num_rect in enumerate(layout["numbers"]):
                if num_rect.collidepoint(x, y):
                    self.state.place_number(i + 1)
                    return

            if layout["new_game"].collidepoint(x, y):
                self._restart_game()
                return
            if layout["menu"].collidepoint(x, y):
                self.running = False
                self.quit_requested = True
                return

    def _restart_game(self) -> None:
        self.particles.clear()
        clear_save_file()
        self.state.restart(self.state.difficulty)

    def _spawn_firework_burst(self, x: int, y: int, count: int = 38) -> None:
        colors = [
            (255, 215, 0),
            (96, 165, 250),
            (244, 114, 182),
            (52, 211, 153),
            (251, 146, 60),
            (248, 113, 113),
        ]
        for _ in range(count):
            self.particles.append(Particle(x, y, random.choice(colors)))

    def _show_name_input_dialog(self) -> None:
        """Show tkinter dialog to enter name for leaderboard."""
        import tkinter as tk
        from tkinter import simpledialog
        from config import game_text
        
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        
        name = simpledialog.askstring(
            game_text("new_highscore"),
            game_text("enter_name"),
            parent=root
        )
        root.destroy()
        
        if name and name.strip():
            from persistence import add_leaderboard_entry
            add_leaderboard_entry(self.state.difficulty, name.strip(), self.state.final_time)

    def _spawn_win_fireworks(self) -> None:
        burst_points = [
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 120),
            (SCREEN_WIDTH // 2 - 190, SCREEN_HEIGHT // 2 - 80),
            (SCREEN_WIDTH // 2 + 190, SCREEN_HEIGHT // 2 - 90),
            (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 - 175),
            (SCREEN_WIDTH // 2 + 85, SCREEN_HEIGHT // 2 - 170),
        ]
        for x, y in burst_points:
            self._spawn_firework_burst(x, y, 34)

    def _handle_keyboard(self, event) -> None:
        r, c = self.state.selected
        key = event.key

        # Di chuyển ô chọn
        if key in (pygame.K_UP, pygame.K_w) and r > 0:
            self.state.selected[0] -= 1
        elif key in (pygame.K_DOWN, pygame.K_s) and r < 8:
            self.state.selected[0] += 1
        elif key in (pygame.K_LEFT, pygame.K_a) and c > 0:
            self.state.selected[1] -= 1
        elif key in (pygame.K_RIGHT, pygame.K_d) and c < 8:
            self.state.selected[1] += 1

        # Bật/Tắt chế độ ghi chú nhanh bằng Space hoặc N
        elif key in (pygame.K_SPACE, pygame.K_n):
            self.state.notes_mode = not self.state.notes_mode

        # Hoàn tác / Làm lại bằng phím tắt
        elif key == pygame.K_z and (pygame.key.get_mods() & pygame.KMOD_CTRL):
            if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                self.state.redo()
            else:
                self.state.undo()
        elif key == pygame.K_y and (pygame.key.get_mods() & pygame.KMOD_CTRL):
            self.state.redo()

        # Nhập số hoặc xóa
        elif self.state.original[r][c] == 0:
            if event.unicode.isdigit() and 1 <= int(event.unicode) <= 9:
                self.state.place_number(int(event.unicode))
            elif key in (pygame.K_BACKSPACE, pygame.K_DELETE, pygame.K_KP0):
                self.state.clear_cell()

    def update(self) -> None:
        if self.state.game_over:
            if random.random() < 0.045:
                x = random.randint(70, SCREEN_WIDTH - 70)
                y = random.randint(70, SCREEN_HEIGHT // 2)
                self._spawn_firework_burst(x, y, 26)
            for p in self.particles[:]:
                p.update()
                if p.lifetime <= 0:
                    self.particles.remove(p)
        if not self.state.game_over and check_win(self.state.board, self.state.solution):
            self.state.game_over = True
            self.state.final_time = self.state.get_elapsed_time()
            is_new_best = update_best_time(self.state.difficulty, self.state.final_time)
            # Record win for statistics
            record_game_win(self.state.difficulty, self.state.final_time)
            # Check if top 10 leaderboard time
            from persistence import is_top_10_time
            if is_top_10_time(self.state.difficulty, self.state.final_time):
                self._show_name_input_dialog()
            clear_save_file()
            self._spawn_win_fireworks()
            play_sound('success')

    def render(self) -> None:
        mouse_pos = pygame.mouse.get_pos()
        overlay_rects = draw_game_view(self.screen, self.fonts, self.state, mouse_pos, self.particles)
        self.pause_resume_rect = overlay_rects["pause_resume"]
        self.pause_quit_rect = overlay_rects["pause_quit"]
        self.win_restart_rect = overlay_rects["win_restart"]
        self.win_quit_rect = overlay_rects["win_quit"]
        self.header_pause_rect = overlay_rects.get("header_pause")

        # Draw help modal if active
        if self.show_help:
            from ui.modals import draw_help_modal
            from config import game_text
            self.help_rects = draw_help_modal(self.screen, self.fonts, pygame.mouse.get_pos(), game_text)

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


def start_game(root, difficulty: str = "medium", loaded_state=None) -> bool:
    game = Game(difficulty)
    if loaded_state:
        game.state = loaded_state
    return game.run()
