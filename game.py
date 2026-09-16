import copy
import random
import time
from typing import List, Literal, Set, Tuple, cast

import pygame

from error_handling import (
    ErrorSeverity,
    log_exception,
)
from logic import check_win, export_puzzle, generate_sudoku, import_puzzle, is_valid_placement
from persistence import (
    clear_save_file,
    load_game_state,
    mark_daily_challenge_completed,
    record_game_start,
    record_game_win,
    save_game_state,
    update_best_time,
)
from sounds import get_sound_manager, play_sound
from ui import (
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    Particle,
    create_game_screen,
    draw_game_view,
    get_cell_from_pos,
    get_sidebar_layout,
    load_fonts,
    trigger_number_placement_animation,
)

Board = List[List[int]]
NotesBoard = List[List[Set[int]]]
Difficulty = Literal["easy", "medium", "hard", "daily", "custom"]

AUTO_SAVE_DEBOUNCE_MS = 500
MAX_HISTORY_STATES = 200


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
        self.elapsed_before_session = 0
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
            if len(self.undo_stack) > MAX_HISTORY_STATES:
                self.undo_stack.pop(0)
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
            play_sound("undo")
        self.auto_save()

    def redo(self) -> None:
        if self.redo_stack:
            board_state, notes_state = self.redo_stack.pop()
            self.undo_stack.append((copy.deepcopy(self.board), copy.deepcopy(self.notes)))
            self.board = board_state
            self.notes = copy.deepcopy(notes_state)
            play_sound("pop")
        self.auto_save()

    @log_exception(ErrorSeverity.MEDIUM, user_action="place_number")
    def place_number(self, num: int) -> None:
        r, c = self.selected
        if self.original[r][c] != 0:
            return
        if self.notes_mode:
            if num in self.notes[r][c]:
                self.notes[r][c].remove(num)
            else:
                self.notes[r][c].add(num)
            self.save_state()
        else:
            self.board[r][c] = num
            self.notes[r][c].clear()
            self.save_state()
            play_sound("pop")
            trigger_number_placement_animation(r, c)
            self._check_completion_ripple(r, c)
        self.auto_save()

    def _check_completion_ripple(self, r: int, c: int) -> None:
        try:
            from ui.board import trigger_completion_animation

            # Check row r
            if all(self.board[r][col] == self.solution[r][col] for col in range(9)):
                trigger_completion_animation("row", r)
            # Check col c
            if all(self.board[row][c] == self.solution[row][c] for row in range(9)):
                trigger_completion_animation("col", c)
            # Check 3x3 box
            br, bc = (r // 3) * 3, (c // 3) * 3
            box_idx = (r // 3) * 3 + (c // 3)
            if all(
                self.board[br + dr][bc + dc] == self.solution[br + dr][bc + dc]
                for dr in range(3)
                for dc in range(3)
            ):
                trigger_completion_animation("box", box_idx)
        except Exception:
            pass

    @log_exception(ErrorSeverity.MEDIUM, user_action="clear_cell")
    def clear_cell(self) -> None:
        r, c = self.selected
        if self.original[r][c] != 0:
            return
        if self.notes_mode:
            if self.notes[r][c]:
                self.notes[r][c].clear()
                self.save_state()
        else:
            self.board[r][c] = 0
            self.save_state()
            play_sound("click")
        self.auto_save()

    @log_exception(ErrorSeverity.MEDIUM, user_action="give_hint")
    def give_hint(self) -> None:
        r, c = self.selected
        if self.original[r][c] == 0 and self.board[r][c] == 0:
            self.board[r][c] = self.solution[r][c]
            self.notes[r][c].clear()
            self.save_state()
            play_sound("hint")
        self.auto_save()

    @log_exception(ErrorSeverity.MEDIUM, user_action="fill_possible_notes")
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
        play_sound("click")
        self.auto_save()

    @log_exception(ErrorSeverity.LOW, user_action="toggle_pause")
    def toggle_pause(self) -> None:
        self.paused = not self.paused
        if self.paused:
            self.last_pause_start = pygame.time.get_ticks()
        else:
            self.paused_time += pygame.time.get_ticks() - self.last_pause_start
        play_sound("click")

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
        self.elapsed_before_session = 0
        self.last_active_time = 0
        self.final_time = 0
        self.undo_stack = [(copy.deepcopy(self.board), copy.deepcopy(self.notes))]
        self.redo_stack.clear()
        self._last_auto_save_time = 0.0
        save_game_state(self)
        play_sound("click")

    def set_puzzle(self, board: Board, solution: Board) -> None:
        """Replace the active puzzle and reset all state tied to the previous board."""
        self.board = copy.deepcopy(board)
        self.solution = copy.deepcopy(solution)
        self.original = copy.deepcopy(board)
        self.selected = next(
            ([r, c] for r in range(9) for c in range(9) if board[r][c] == 0), [0, 0]
        )
        self.notes = [[set() for _ in range(9)] for _ in range(9)]
        self.notes_mode = False
        self.game_over = False
        self.paused = False
        self.show_errors = False
        self.start_time = pygame.time.get_ticks()
        self.paused_time = 0
        self.last_pause_start = 0
        self.elapsed_before_session = 0
        self.last_active_time = 0
        self.final_time = 0
        self.undo_stack = [(copy.deepcopy(self.board), copy.deepcopy(self.notes))]
        self.redo_stack = []
        self._last_auto_save_time = 0.0
        save_game_state(self)

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
            elapsed = self.last_pause_start - self.start_time - self.paused_time
        else:
            elapsed = pygame.time.get_ticks() - self.start_time - self.paused_time
        return self.elapsed_before_session + max(0, elapsed // 1000)


class Game:
    """Full game session (PLAYING state). Manages one Sudoku game."""

    def __init__(self, difficulty: Difficulty = "medium", loaded_state=None):
        self.screen = create_game_screen()
        self._load_fonts()
        if loaded_state:
            self.state = loaded_state
        else:
            self.state = GameState(difficulty)
        self.particles: List[Particle] = []
        self.sound_manager = get_sound_manager()
        self.running = True
        self.quit_requested = False
        self.go_to_menu = False
        self.pause_resume_rect: pygame.Rect | None = None
        self.pause_restart_rect: pygame.Rect | None = None
        self.pause_save_quit_rect: pygame.Rect | None = None
        self.pause_quit_rect: pygame.Rect | None = None
        self.win_restart_rect: pygame.Rect | None = None
        self.win_quit_rect: pygame.Rect | None = None
        self.header_pause_rect: pygame.Rect | None = None
        self.header_theme_rect: pygame.Rect | None = None
        self.header_sound_rect: pygame.Rect | None = None
        self.header_help_rect: pygame.Rect | None = None
        self.help_rects: dict[str, pygame.Rect] | None = None
        self.show_help = False

    @log_exception(ErrorSeverity.HIGH, user_action="_load_fonts")
    def _load_fonts(self) -> None:
        self.fonts = load_fonts()

    @log_exception(ErrorSeverity.HIGH, user_action="handle_events")
    def handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.state.force_save()
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
            self.go_to_menu = True

    def _handle_pause_click(self, pos):
        x, y = pos
        if self.pause_resume_rect and self.pause_resume_rect.collidepoint(x, y):
            self.state.toggle_pause()
        if self.pause_restart_rect is not None and self.pause_restart_rect.collidepoint(x, y):
            self._restart_game()
        if self.pause_save_quit_rect is not None and self.pause_save_quit_rect.collidepoint(x, y):
            self.state.force_save()
            self.running = False
            self.go_to_menu = True
        # Backward compat
        if self.pause_quit_rect and self.pause_quit_rect.collidepoint(x, y):
            self.state.force_save()
            self.running = False
            self.go_to_menu = True

    def _handle_help_click(self, pos):
        x, y = pos
        if (
            self.help_rects
            and self.help_rects.get("help_close")
            and self.help_rects["help_close"].collidepoint(x, y)
        ):
            self.show_help = False

    def _handle_mouse(self, pos: Tuple[int, int]) -> None:
        x, y = pos

        # 1. Header buttons
        if self.header_pause_rect and self.header_pause_rect.collidepoint(x, y):
            self.state.toggle_pause()
            return
        if self.header_theme_rect is not None and self.header_theme_rect.collidepoint(x, y):
            from ui.colors import get_theme_manager

            get_theme_manager().cycle_theme()
            play_sound("pop")
            return
        if self.header_sound_rect is not None and self.header_sound_rect.collidepoint(x, y):
            from sounds import toggle_sound

            toggle_sound()
            return
        if self.header_help_rect is not None and self.header_help_rect.collidepoint(x, y):
            self.show_help = not self.show_help
            return

        if not self.state.paused and not self.state.game_over:
            # 2. Board cell selection
            cell = get_cell_from_pos(x, y)
            if cell:
                self.state.selected = list(cell)
                return

            # 3. Sidebar buttons
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
                self.state.force_save()
                self.running = False
                self.go_to_menu = True
                return

            # Export / Import
            if layout.get("export") and layout["export"].collidepoint(x, y):
                self._handle_export()
                return
            if layout.get("import") and layout["import"].collidepoint(x, y):
                self._handle_import()
                return

    def _handle_export(self) -> None:
        import tkinter as tk
        from tkinter import messagebox

        root = tk.Tk()
        root.withdraw()
        try:
            root.clipboard_clear()
            root.clipboard_append(export_puzzle(self.state.board, self.state.solution))
            root.update()
            messagebox.showinfo("Export Puzzle", "Puzzle copied to clipboard.", parent=root)
        finally:
            root.destroy()

    def _handle_import(self) -> None:
        import tkinter as tk
        from tkinter import messagebox, simpledialog

        root = tk.Tk()
        root.withdraw()
        try:
            puzzle_text = simpledialog.askstring(
                "Import Puzzle", "Paste exported puzzle JSON or an 81-digit puzzle:", parent=root
            )
            if not puzzle_text:
                return
            try:
                board, solution = import_puzzle(puzzle_text)
            except ValueError as exc:
                messagebox.showerror("Import Puzzle", str(exc), parent=root)
                return
            self.state.set_puzzle(board, solution)
            messagebox.showinfo("Import Puzzle", "Puzzle imported.", parent=root)
        finally:
            root.destroy()

    def _restart_game(self) -> None:
        self.particles.clear()
        clear_save_file()
        self.state.restart(self.state.difficulty)
        record_game_start(self.state.difficulty)

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
        root.attributes("-topmost", True)

        name = simpledialog.askstring(
            game_text("new_highscore"), game_text("enter_name"), parent=root
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

        if key in (pygame.K_UP, pygame.K_w) and r > 0:
            self.state.selected[0] -= 1
        elif key in (pygame.K_DOWN, pygame.K_s) and r < 8:
            self.state.selected[0] += 1
        elif key in (pygame.K_LEFT, pygame.K_a) and c > 0:
            self.state.selected[1] -= 1
        elif key in (pygame.K_RIGHT, pygame.K_d) and c < 8:
            self.state.selected[1] += 1

        elif key in (pygame.K_SPACE, pygame.K_n):
            self.state.notes_mode = not self.state.notes_mode

        elif key == pygame.K_z and (event.mod & pygame.KMOD_CTRL):
            if event.mod & pygame.KMOD_SHIFT:
                self.state.redo()
            else:
                self.state.undo()
        elif key == pygame.K_y and (event.mod & pygame.KMOD_CTRL):
            self.state.redo()

        elif self.state.original[r][c] == 0:
            if (
                hasattr(event, "unicode")
                and event.unicode.isdigit()
                and 1 <= int(event.unicode) <= 9
            ):
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
            update_best_time(self.state.difficulty, self.state.final_time)
            record_game_win(self.state.difficulty, self.state.final_time)
            if self.state.difficulty == "daily":
                mark_daily_challenge_completed(self.state.final_time, self.state.difficulty)
            from persistence import is_top_10_time

            if is_top_10_time(self.state.difficulty, self.state.final_time):
                self._show_name_input_dialog()
            clear_save_file()
            self._spawn_win_fireworks()
            play_sound("success")

    def render(self) -> None:
        mouse_pos = pygame.mouse.get_pos()
        overlay_rects = draw_game_view(
            self.screen, self.fonts, self.state, mouse_pos, self.particles
        )
        self.pause_resume_rect = overlay_rects["pause_resume"]
        self.pause_restart_rect = overlay_rects.get("pause_restart")
        self.pause_save_quit_rect = overlay_rects.get("pause_save_quit")
        self.pause_quit_rect = overlay_rects["pause_quit"]
        self.win_restart_rect = overlay_rects["win_restart"]
        self.win_quit_rect = overlay_rects["win_quit"]
        self.header_pause_rect = overlay_rects.get("header_pause")
        self.header_theme_rect = overlay_rects.get("header_theme")
        self.header_sound_rect = overlay_rects.get("header_sound")
        self.header_help_rect = overlay_rects.get("header_help")

        if self.show_help:
            from config import game_text
            from ui.modals import draw_help_modal

            self.help_rects = draw_help_modal(
                self.screen, self.fonts, pygame.mouse.get_pos(), game_text
            )

    def run(self) -> str:
        """Run the game session. Returns 'menu' or 'quit'."""
        clock = pygame.time.Clock()
        while self.running:
            if not self.handle_events():
                return "quit"
            self.update()
            self.render()
            clock.tick(60)
        return "menu" if self.go_to_menu else "quit"


# ──────────────────────────────────────────────
#  MAIN APPLICATION CONTROLLER
# ──────────────────────────────────────────────
class AppController:
    """Full Pygame application: Menu ↔ Game, all in one window, 60 FPS."""

    # App states
    STATE_MENU = "menu"
    STATE_PLAYING = "playing"
    STATE_LEADERBOARD = "leaderboard"
    STATE_HELP = "help"

    def __init__(self):
        # create_game_screen handles enable_high_dpi + pygame.init internally
        self.screen = create_game_screen()
        self.fonts = load_fonts()
        self.clock = pygame.time.Clock()
        self.state = self.STATE_MENU
        self.running = True

        # Menu state
        self.custom_cells = 40
        self.leaderboard_diff = "medium"

        # Active game session
        self.game_session: Game | None = None

    def _handle_menu_events(self, menu_rects: dict) -> None:
        from config import chuyen_ngon_ngu
        from sounds import toggle_sound
        from ui.colors import get_theme_manager

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    self._start_game("easy")
                elif event.key == pygame.K_2:
                    self._start_game("medium")
                elif event.key == pygame.K_3:
                    self._start_game("hard")
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
            if event.type != pygame.MOUSEBUTTONDOWN:
                continue

            pos = event.pos

            if menu_rects.get("resume") and menu_rects["resume"].collidepoint(pos):
                saved = load_game_state()
                self._start_game(saved.difficulty if saved else "medium", loaded_state=saved)

            elif menu_rects.get("daily") and menu_rects["daily"].collidepoint(pos):
                self._start_game("daily")

            elif menu_rects.get("easy") and menu_rects["easy"].collidepoint(pos):
                self._start_game("easy")
            elif menu_rects.get("medium") and menu_rects["medium"].collidepoint(pos):
                self._start_game("medium")
            elif menu_rects.get("hard") and menu_rects["hard"].collidepoint(pos):
                self._start_game("hard")

            elif menu_rects.get("custom") and menu_rects["custom"].collidepoint(pos):
                # Only start if not clicking stepper buttons
                if not (
                    menu_rects.get("custom_dec") and menu_rects["custom_dec"].collidepoint(pos)
                ) and not (
                    menu_rects.get("custom_inc") and menu_rects["custom_inc"].collidepoint(pos)
                ):
                    self._start_game("custom", custom_cells=self.custom_cells)

            elif menu_rects.get("custom_dec") and menu_rects["custom_dec"].collidepoint(pos):
                self.custom_cells = max(20, self.custom_cells - 2)
            elif menu_rects.get("custom_inc") and menu_rects["custom_inc"].collidepoint(pos):
                self.custom_cells = min(60, self.custom_cells + 2)

            elif menu_rects.get("theme") and menu_rects["theme"].collidepoint(pos):
                get_theme_manager().cycle_theme()
                play_sound("pop")
            elif menu_rects.get("sound") and menu_rects["sound"].collidepoint(pos):
                toggle_sound()
            elif menu_rects.get("lang") and menu_rects["lang"].collidepoint(pos):
                chuyen_ngon_ngu()
            elif menu_rects.get("stats") and menu_rects["stats"].collidepoint(pos):
                self.state = self.STATE_LEADERBOARD
            elif menu_rects.get("help") and menu_rects["help"].collidepoint(pos):
                self.state = self.STATE_HELP

    def _handle_help_events(self, help_rects: dict) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_F1):
                self.state = self.STATE_MENU
                return
            if event.type == pygame.MOUSEBUTTONDOWN and help_rects.get("help_close"):
                if help_rects["help_close"].collidepoint(event.pos):
                    self.state = self.STATE_MENU
                    return

    def _start_game(self, difficulty: str, loaded_state=None, custom_cells: int = 40) -> None:
        from logic import generate_sudoku

        is_new_game = loaded_state is None
        if difficulty == "custom" and loaded_state is None:
            board, solution = generate_sudoku("custom", empty_cells=custom_cells)
            gs = GameState.__new__(GameState)
            gs.difficulty = "custom"
            gs.board = board
            gs.solution = solution
            gs.original = [row[:] for row in board]
            gs.selected = [0, 0]
            gs.notes = [[set() for _ in range(9)] for _ in range(9)]
            gs.notes_mode = False
            gs.game_over = False
            gs.paused = False
            gs.show_errors = False
            gs.start_time = pygame.time.get_ticks()
            gs.paused_time = 0
            gs.last_pause_start = 0
            gs.elapsed_before_session = 0
            gs.last_active_time = 0
            gs.final_time = 0
            gs._last_auto_save_time = 0.0
            import copy

            gs.undo_stack = [(copy.deepcopy(board), copy.deepcopy(gs.notes))]
            gs.redo_stack = []
            loaded_state = gs

        self.game_session = Game(cast(Difficulty, difficulty), loaded_state=loaded_state)
        if is_new_game:
            record_game_start(cast(Difficulty, difficulty))
        assert self.game_session is not None
        self.game_session.screen = self.screen
        self.game_session._load_fonts()
        self.state = self.STATE_PLAYING

    def _run_game_session(self) -> None:
        """Run one Game session tick-by-tick and return to menu when done."""
        assert self.game_session is not None
        clock = self.clock
        while self.game_session.running:
            if not self.game_session.handle_events():
                self.running = False
                return
            self.game_session.update()
            self.game_session.render()
            clock.tick(60)
        # Session ended - go back to menu
        self.state = self.STATE_MENU
        self.game_session = None

    def _handle_leaderboard_events(self, lb_rects: dict) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.state = self.STATE_MENU
                return
            if event.type != pygame.MOUSEBUTTONDOWN:
                continue
            pos = event.pos
            if lb_rects.get("leaderboard_close") and lb_rects["leaderboard_close"].collidepoint(
                pos
            ):
                self.state = self.STATE_MENU
            for d in ("easy", "medium", "hard", "daily"):
                if lb_rects.get(f"tab_{d}") and lb_rects[f"tab_{d}"].collidepoint(pos):
                    self.leaderboard_diff = d

    def run(self) -> None:
        """Main application loop."""
        from config import game_text
        from ui.menu import draw_menu_view
        from ui.modals import draw_help_modal, draw_leaderboard_modal

        while self.running:
            mouse_pos = pygame.mouse.get_pos()

            if self.state == self.STATE_MENU:
                menu_rects = draw_menu_view(
                    self.screen, self.fonts, mouse_pos, custom_cells=self.custom_cells
                )
                pygame.display.flip()
                self._handle_menu_events(menu_rects)

            elif self.state == self.STATE_PLAYING:
                if self.game_session:
                    self._run_game_session()
                else:
                    self.state = self.STATE_MENU

            elif self.state == self.STATE_LEADERBOARD:
                lb_rects = draw_leaderboard_modal(
                    self.screen, self.fonts, mouse_pos, game_text, active_diff=self.leaderboard_diff
                )
                pygame.display.flip()
                self._handle_leaderboard_events(lb_rects)

            elif self.state == self.STATE_HELP:
                help_rects = draw_help_modal(self.screen, self.fonts, mouse_pos, game_text)
                pygame.display.flip()
                self._handle_help_events(help_rects)

            self.clock.tick(60)

        pygame.quit()


def start_game(root=None, difficulty: str = "medium", loaded_state=None) -> bool:
    """Legacy entry point: runs one game session and returns win status."""
    if loaded_state is None:
        record_game_start(cast(Difficulty, difficulty))
    game = Game(cast(Difficulty, difficulty), loaded_state=loaded_state)
    result = game.run()
    return result != "quit"
