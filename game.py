import copy
import os
import random
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

Board = List[List[int]]
NotesBoard = List[List[Set[int]]]
Difficulty = str


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
        self.screen = create_game_screen()
        self._load_fonts()
        self.state = GameState(difficulty)
        self.particles: List[Particle] = []
        self.sounds = {}
        self._init_sounds()
        self.running = True
        self.quit_requested = False
        self.pause_resume_rect = None
        self.pause_quit_rect = None
        self.win_restart_rect = None
        self.win_quit_rect = None

    def _init_sounds(self) -> None:
        try:
            sound_files = {"win": "sounds/applause.wav"}
            for name, path in sound_files.items():
                if os.path.exists(path):
                    self.sounds[name] = pygame.mixer.Sound(path)
        except Exception:
            pass

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
            self._restart_game()
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
        if not self.state.paused and not self.state.game_over:
            cell = get_cell_from_pos(x, y)
            if cell:
                self.state.selected = list(cell)
                return

        layout = get_sidebar_layout(get_timer_rect().bottom)
        main_actions = [
            self._restart_game,
            self.state.give_hint,
            lambda: setattr(self.state, "show_errors", not self.state.show_errors),
            self.state.toggle_pause,
            lambda: setattr(self.state, "notes_mode", not self.state.notes_mode),
            self.state.fill_possible_notes,
        ]
        for rect, action in zip(layout["main_buttons"], main_actions):
            if rect.collidepoint(x, y):
                action()
                return

        if layout["undo"].collidepoint(x, y):
            self.state.undo()
            return
        if layout["redo"].collidepoint(x, y):
            self.state.redo()
            return

        for i, num_rect in enumerate(layout["numbers"]):
            if num_rect.collidepoint(x, y):
                self.state.place_number(i + 1)
                return

        if layout["clear"].collidepoint(x, y):
            self.state.clear_cell()
            return

    def _restart_game(self) -> None:
        self.particles.clear()
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
            self._spawn_win_fireworks()
            if "win" in self.sounds:
                self.sounds["win"].play()

    def render(self) -> None:
        mouse_pos = pygame.mouse.get_pos()
        overlay_rects = draw_game_view(self.screen, self.fonts, self.state, mouse_pos, self.particles)
        self.pause_resume_rect = overlay_rects["pause_resume"]
        self.pause_quit_rect = overlay_rects["pause_quit"]
        self.win_restart_rect = overlay_rects["win_restart"]
        self.win_quit_rect = overlay_rects["win_quit"]

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
