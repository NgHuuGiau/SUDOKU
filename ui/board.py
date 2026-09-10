"""Board rendering for Sudoku UI."""
import time

import pygame

from ui.colors import Colors
from ui.drawing import draw_rounded_card
from ui.geometry import BOARD_SIZE, BOARD_X, BOARD_Y, CELL_SIZE

try:
    from logic import is_valid_placement
except ImportError:
    is_valid_placement = None  # type: ignore[assignment]


# Animation state for cell pop-in effects
_cell_animations: dict[tuple[int, int], float] = {}  # (r, c) -> start_time
# Completion animations: list of {"type": str, "index": int, "start_time": float, "duration": float}
_completion_animations: list[dict] = []


def _trigger_cell_animation(r: int, c: int) -> None:
    """Trigger a pop-in animation for a cell."""
    _cell_animations[(r, c)] = time.monotonic()


def _get_cell_animation_progress(r: int, c: int) -> float:
    """Get animation progress (0.0 to 1.0) for a cell."""
    start_time = _cell_animations.get((r, c))
    if start_time is None:
        return 1.0
    elapsed = time.monotonic() - start_time
    # Animation lasts 300ms
    return min(1.0, elapsed / 0.3)


def trigger_number_placement_animation(r: int, c: int) -> None:
    """Public function to trigger animation when a number is placed."""
    _trigger_cell_animation(r, c)


def trigger_completion_animation(comp_type: str, index: int) -> None:
    """Trigger a celebration ripple animation for row, col, or box."""
    _completion_animations.append({
        "type": comp_type,
        "index": index,
        "start_time": time.monotonic(),
        "duration": 0.6,
    })


def draw_board(screen: pygame.Surface, fonts, state, selected_cell=None):
    board_rect = pygame.Rect(BOARD_X, BOARD_Y, BOARD_SIZE, BOARD_SIZE)
    draw_rounded_card(screen, board_rect, Colors.BG_BOARD, Colors.GRID_OUTER, border_width=2, radius=12)

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
                inner_pad = cell_rect.inflate(-4, -4)
                pygame.draw.rect(screen, Colors.SAME_NUMBER, inner_pad, border_radius=6)

            # Error highlight
            if state.board[r][c] != 0 and state.original[r][c] == 0:
                is_err = False
                if is_valid_placement is not None and not is_valid_placement(state.board, r, c, state.board[r][c]):
                    is_err = True
                elif state.show_errors and state.board[r][c] != state.solution[r][c]:
                    is_err = True
                if is_err:
                    inner_pad = cell_rect.inflate(-4, -4)
                    pygame.draw.rect(screen, Colors.ERROR_BG, inner_pad, border_radius=6)

            # Selected cell background
            if (r, c) == (r_sel, c_sel) and not state.paused:
                inner_pad = cell_rect.inflate(-2, -2)
                pygame.draw.rect(screen, Colors.SELECTED_BG, inner_pad, border_radius=6)

    # 2. Grid lines
    for i in range(10):
        is_thick = (i % 3 == 0)
        line_color = Colors.GRID_THICK if is_thick else Colors.GRID_THIN
        line_width = 3 if is_thick else 1

        x = BOARD_X + i * CELL_SIZE
        y = BOARD_Y + i * CELL_SIZE
        pygame.draw.line(screen, line_color, (x, BOARD_Y), (x, BOARD_Y + BOARD_SIZE), line_width)
        pygame.draw.line(screen, line_color, (BOARD_X, y), (BOARD_X + BOARD_SIZE, y), line_width)

    # 3. Selected cell modern glow & border
    if state.selected and not state.paused:
        sel_rect = pygame.Rect(BOARD_X + c_sel * CELL_SIZE, BOARD_Y + r_sel * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        # Outer soft glow
        glow_surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        ripple_c = getattr(Colors, 'RIPPLE', (79, 70, 229))
        pygame.draw.rect(glow_surf, (*ripple_c, 45), glow_surf.get_rect(), border_radius=8)
        screen.blit(glow_surf, sel_rect)
        # Sharp accent border
        pygame.draw.rect(screen, Colors.SELECTED_BORDER, sel_rect, width=2, border_radius=6)

    # 4. Completion ripple animations
    now = time.monotonic()
    active_anims = []
    for anim in _completion_animations:
        elapsed = now - anim["start_time"]
        if elapsed < anim["duration"]:
            active_anims.append(anim)
            progress = elapsed / anim["duration"]
            alpha = int(180 * (1.0 - progress))
            ripple_surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            ripple_c = getattr(Colors, 'RIPPLE', (56, 189, 248))
            pygame.draw.rect(ripple_surf, (*ripple_c, alpha), ripple_surf.get_rect(), border_radius=6)

            comp_type = anim["type"]
            idx = anim["index"]
            if comp_type == "row":
                for col in range(9):
                    crect = pygame.Rect(BOARD_X + col * CELL_SIZE, BOARD_Y + idx * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    screen.blit(ripple_surf, crect)
            elif comp_type == "col":
                for row in range(9):
                    crect = pygame.Rect(BOARD_X + idx * CELL_SIZE, BOARD_Y + row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    screen.blit(ripple_surf, crect)
            elif comp_type == "box":
                br, bc = (idx // 3) * 3, (idx % 3) * 3
                for dr in range(3):
                    for dc in range(3):
                        crect = pygame.Rect(BOARD_X + (bc + dc) * CELL_SIZE, BOARD_Y + (br + dr) * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                        screen.blit(ripple_surf, crect)
    _completion_animations[:] = active_anims

    # 5. Numbers and notes
    if not state.paused:
        for r in range(9):
            for c in range(9):
                cell_rect = pygame.Rect(BOARD_X + c * CELL_SIZE, BOARD_Y + r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                val = state.board[r][c]

                if val != 0:
                    is_fixed = (state.original[r][c] != 0)
                    if is_fixed:
                        color = Colors.FIXED_TEXT
                    elif is_valid_placement is not None and not is_valid_placement(state.board, r, c, val):
                        color = Colors.ERROR_TEXT
                    elif state.show_errors and val != state.solution[r][c]:
                        color = Colors.ERROR_TEXT
                    else:
                        color = Colors.USER_TEXT

                    # Pop-in animation for newly placed numbers (non-fixed)
                    anim_progress = 1.0
                    if not is_fixed:
                        anim_progress = _get_cell_animation_progress(r, c)
                        scale = 0.4 + 0.6 * anim_progress
                        alpha = int(255 * anim_progress)

                    font_to_use = fonts.cell_bold if is_fixed else fonts.cell
                    num_surf = font_to_use.render(str(val), True, color)

                    if not is_fixed and anim_progress < 1.0:
                        scaled_size = int(CELL_SIZE * scale)
                        scaled_surf = pygame.transform.smoothscale(num_surf, (scaled_size, scaled_size))
                        scaled_surf.set_alpha(alpha)
                        screen.blit(scaled_surf, scaled_surf.get_rect(center=cell_rect.center))
                    else:
                        screen.blit(num_surf, num_surf.get_rect(center=cell_rect.center))

                elif state.notes[r][c]:
                    # Draw subtle background for cells with notes according to theme
                    note_bg_rect = cell_rect.inflate(-4, -4)
                    note_bg_surf = pygame.Surface((note_bg_rect.width, note_bg_rect.height), pygame.SRCALPHA)
                    note_tint = Colors.SELECTED_BG
                    pygame.draw.rect(note_bg_surf, (*note_tint[:3], 80), note_bg_surf.get_rect(), border_radius=4)
                    screen.blit(note_bg_surf, note_bg_rect)

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
