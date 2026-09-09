"""Board rendering for Sudoku UI."""
import pygame
from ui.colors import Colors
from ui.geometry import CELL_SIZE, BOARD_X, BOARD_Y, BOARD_SIZE
from ui.drawing import draw_rounded_card
from ui.icons import SmoothIcons
try:
    from logic import is_valid_placement
except ImportError:
    is_valid_placement = None


def draw_board(screen: pygame.Surface, fonts, state, selected_cell=None):
    board_rect = pygame.Rect(BOARD_X, BOARD_Y, BOARD_SIZE, BOARD_SIZE)
    draw_rounded_card(screen, board_rect, Colors.BG_BOARD, Colors.GRID_OUTER, border_width=2, radius=10)

    r_sel, c_sel = (selected_cell if selected_cell else state.selected)
    highlight_num = state.board[r_sel][c_sel] if state.selected else 0

    # 1. Background highlights
    for r in range(9):
        for c in range(9):
            cell_rect = pygame.Rect(BOARD_X + c * CELL_SIZE, BOARD_Y + r * CELL_SIZE, CELL_SIZE, CELL_SIZE)

            # Crosshair
            if state.selected and not state.paused:
                if r == r_sel or c == c_sel or (r // 3 == r_sel // 3 and c // 3 == c_sel // 3):
                    pygame.draw.rect(screen, Colors.CROSSHAIR, cell_rect)

            # Same number highlight
            if highlight_num != 0 and state.board[r][c] == highlight_num and not state.paused:
                pygame.draw.rect(screen, Colors.SAME_NUMBER, cell_rect)

            # Error highlight
            if state.board[r][c] != 0 and state.original[r][c] == 0:
                is_err = False
                if is_valid_placement and not is_valid_placement(state.board, r, c, state.board[r][c]):
                    is_err = True
                elif state.show_errors and state.board[r][c] != state.solution[r][c]:
                    is_err = True
                if is_err:
                    pygame.draw.rect(screen, Colors.ERROR_BG, cell_rect)

            # Selected cell
            if (r, c) == (r_sel, c_sel) and not state.paused:
                pygame.draw.rect(screen, Colors.SELECTED_BG, cell_rect)

    # 2. Grid lines
    for i in range(10):
        is_thick = (i % 3 == 0)
        line_color = Colors.GRID_THICK if is_thick else Colors.GRID_THIN
        line_width = 3 if is_thick else 1

        x = BOARD_X + i * CELL_SIZE
        y = BOARD_Y + i * CELL_SIZE
        pygame.draw.line(screen, line_color, (x, BOARD_Y), (x, BOARD_Y + BOARD_SIZE), line_width)
        pygame.draw.line(screen, line_color, (BOARD_X, y), (BOARD_X + BOARD_SIZE, y), line_width)

    # 3. Selected cell glow border
    if state.selected and not state.paused:
        sel_rect = pygame.Rect(BOARD_X + c_sel * CELL_SIZE, BOARD_Y + r_sel * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, Colors.SELECTED_BORDER, sel_rect, width=3, border_radius=4)

    # 4. Numbers and notes
    if not state.paused:
        for r in range(9):
            for c in range(9):
                cell_rect = pygame.Rect(BOARD_X + c * CELL_SIZE, BOARD_Y + r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                val = state.board[r][c]

                if val != 0:
                    is_fixed = (state.original[r][c] != 0)
                    if is_fixed:
                        color = Colors.FIXED_TEXT
                    elif is_valid_placement and not is_valid_placement(state.board, r, c, val):
                        color = Colors.ERROR_TEXT
                    elif state.show_errors and val != state.solution[r][c]:
                        color = Colors.ERROR_TEXT
                    else:
                        color = Colors.USER_TEXT

                    font_to_use = fonts.cell_bold if is_fixed else fonts.cell
                    num_surf = font_to_use.render(str(val), True, color)
                    screen.blit(num_surf, num_surf.get_rect(center=cell_rect.center))
                elif state.notes[r][c]:
                    sub_size = CELL_SIZE // 3
                    for note_digit in sorted(state.notes[r][c]):
                        nr = (note_digit - 1) // 3
                        nc = (note_digit - 1) % 3
                        note_center = (
                            cell_rect.left + nc * sub_size + sub_size // 2,
                            cell_rect.top + nr * sub_size + sub_size // 2,
                        )
                        note_surf = fonts.note.render(str(note_digit), True, Colors.NOTE_TEXT)
                        screen.blit(note_surf, note_surf.get_rect(center=note_center))