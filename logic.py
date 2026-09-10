import copy
import random
from datetime import date
from typing import List, Optional, Tuple

Board = List[List[int]]


def generate_sudoku(difficulty: str = "medium", seed: Optional[int] = None, empty_cells: Optional[int] = None) -> Tuple[Board, Board]:
    """Generate a Sudoku puzzle.

    Args:
        difficulty: "easy", "medium", "hard", or "custom"
        seed: Optional seed for reproducible generation (e.g., for daily challenge)
        empty_cells: Number of empty cells for custom difficulty (20-60)
    """
    if seed is not None:
        random.seed(seed)

    base = 3
    side = base * base

    def pattern(r, c):
        return (base * (r % base) + r // base + c) % side

    def shuffle(s):
        return random.sample(s, len(s))

    r_base = range(base)
    rows = [g * base + r for g in shuffle(r_base) for r in shuffle(r_base)]
    cols = [g * base + c for g in shuffle(r_base) for c in shuffle(r_base)]
    nums = shuffle(range(1, side + 1))

    board = [[nums[pattern(r, c)] for c in cols] for r in rows]
    full_board_solution = copy.deepcopy(board)

    difficulties = {
        "easy": 38,       # 38 empty cells -> 43 clues left
        "medium": 48,     # 48 empty cells -> 33 clues left
        "hard": 54,       # 54 empty cells -> 27 clues left
    }

    if difficulty == "custom" and empty_cells is not None:
        target_empties = max(20, min(60, empty_cells))
    else:
        target_empties = difficulties.get(difficulty, 48)  # noqa: F821

    positions = list(range(side * side))
    random.shuffle(positions)

    removed = 0
    for pos in positions:
        if removed >= target_empties:
            break
        r, c = pos // side, pos % side
        val = board[r][c]
        board[r][c] = 0

        if count_solutions_dlx(board) == 1:
            removed += 1
        else:
            board[r][c] = val

    return board, full_board_solution


def generate_daily_challenge(difficulty: str = "medium", challenge_date: Optional[date] = None) -> Tuple[Board, Board, int]:
    """Generate a daily challenge puzzle seeded by date.

    Args:
        difficulty: "easy", "medium", or "hard"
        challenge_date: Date for the challenge (defaults to today)

    Returns:
        Tuple of (board, solution, seed_used)
    """
    if challenge_date is None:
        challenge_date = date.today()

    # Create deterministic seed from date: YYYYMMDD + difficulty hash
    seed = challenge_date.year * 10000 + challenge_date.month * 100 + challenge_date.day
    diff_hash = {"easy": 1, "medium": 2, "hard": 3}[difficulty]
    seed = seed * 10 + diff_hash

    board, solution = generate_sudoku(difficulty, seed=seed)
    return board, solution, seed


def get_daily_challenge_info(challenge_date: Optional[date] = None) -> dict:
    """Get info about today's daily challenge."""
    if challenge_date is None:
        challenge_date = date.today()

    return {
        "date": challenge_date.isoformat(),
        "date_str": challenge_date.strftime("%d/%m/%Y"),
        "weekday": challenge_date.strftime("%A"),
    }
    base = 3
    side = base * base

    def pattern(r, c):
        return (base * (r % base) + r // base + c) % side

    def shuffle(s):
        return random.sample(s, len(s))

    r_base = range(base)
    rows = [g * base + r for g in shuffle(r_base) for r in shuffle(r_base)]
    cols = [g * base + c for g in shuffle(r_base) for c in shuffle(r_base)]
    nums = shuffle(range(1, side + 1))

    board = [[nums[pattern(r, c)] for c in cols] for r in rows]
    full_board_solution = copy.deepcopy(board)

    difficulties: dict[str, int] = {
        "easy": 38,       # 38 empty cells -> 43 clues left
        "medium": 48,     # 48 empty cells -> 33 clues left
        "hard": 54,       # 54 empty cells -> 27 clues left
    }

    if difficulty == "custom" and empty_cells is not None:  # noqa: F821
        target_empties = max(20, min(60, empty_cells))  # noqa: F821
    else:
        target_empties = difficulties.get(difficulty, 48)  # noqa: F821

    positions = list(range(side * side))
    random.shuffle(positions)

    removed = 0
    for pos in positions:
        if removed >= target_empties:
            break
        r, c = pos // side, pos % side
        val = board[r][c]
        board[r][c] = 0

        if count_solutions_dlx(board) == 1:
            removed += 1
        else:
            board[r][c] = val

    return board, full_board_solution


# =============================================================================
# DLX (Dancing Links / Algorithm X) - Fast exact cover solver for Sudoku
# =============================================================================

class DLXNode:
    __slots__ = ('left', 'right', 'up', 'down', 'column', 'row_id', 'col_id', 'size')

    def __init__(self):
        self.left = self.right = self.up = self.down = self
        self.column = self
        self.row_id = -1
        self.col_id = -1
        self.size = 0


class DLX:
    """Dancing Links implementation for exact cover problem (Sudoku)."""

    def __init__(self, n_cols: int):
        self.header = DLXNode()
        self.columns: list[DLXNode] = [DLXNode() for _ in range(n_cols)]
        self.nodes: list[DLXNode] = []
        self.solution: list[int] = []
        self.solution_count = 0
        self.limit = 2

        # Link column headers
        prev = self.header
        for i, col in enumerate(self.columns):
            col.col_id = i
            col.up = col.down = col
            col.size = 0
            prev.right = col
            col.left = prev
            prev = col
        prev.right = self.header
        self.header.left = prev

    def add_row(self, row_id: int, cols: List[int]) -> None:
        """Add a row covering the given columns."""
        first = None
        for col_id in cols:
            node = DLXNode()
            node.row_id = row_id
            node.col_id = col_id
            node.column = self.columns[col_id]

            # Vertical links
            node.up = self.columns[col_id].up
            node.down = self.columns[col_id]
            self.columns[col_id].up.down = node
            self.columns[col_id].up = node
            self.columns[col_id].size += 1

            # Horizontal links
            if first is None:
                first = node
                node.left = node.right = node
            else:
                node.left = first.left
                node.right = first
                first.left.right = node
                first.left = node
            self.nodes.append(node)

    def cover(self, col: DLXNode) -> None:
        """Remove column from header list and all rows in that column."""
        col.right.left = col.left
        col.left.right = col.right
        row = col.down
        while row != col:
            node = row.right
            while node != row:
                node.down.up = node.up
                node.up.down = node.down
                node.column.size -= 1
                node = node.right
            row = row.down

    def uncover(self, col: DLXNode) -> None:
        """Restore column and rows."""
        row = col.up
        while row != col:
            node = row.left
            while node != row:
                node.column.size += 1
                node.down.up = node
                node.up.down = node
                node = node.left
            row = row.up
        col.right.left = col
        col.left.right = col

    def search(self, k: int = 0) -> bool:
        """Algorithm X with dancing links."""
        if self.header.right == self.header:
            self.solution_count += 1
            return self.solution_count >= self.limit

        # Choose column with minimum size (heuristic)
        col = self.header.right
        min_size = col.size
        c = col.right
        while c != self.header:
            if c.size < min_size:
                min_size = c.size
                col = c
            c = c.right

        if min_size == 0:
            return False

        self.cover(col)
        row = col.down
        while row != col:
            self.solution.append(row.row_id)
            node = row.right
            while node != row:
                self.cover(node.column)
                node = node.right

            if self.search(k + 1):
                return True

            self.solution.pop()
            node = row.left
            while node != row:
                self.uncover(node.column)
                node = node.left
            row = row.down

        self.uncover(col)
        return False

    def count_solutions(self, limit: int = 2) -> int:
        self.limit = limit
        self.solution_count = 0
        self.solution = []
        self.search()
        return self.solution_count


def build_dlx_matrix(board: Board) -> DLX:
    """Build DLX matrix for a Sudoku board.

    Constraints (4 types * 81 = 324 columns):
    1. Cell constraint: each cell has a number (81)
    2. Row constraint: each row has each number once (81)
    3. Col constraint: each col has each number once (81)
    4. Box constraint: each 3x3 box has each number once (81)
    """
    dlx = DLX(324)

    # Pre-filled cells as mandatory rows
    for r in range(9):
        for c in range(9):
            val = board[r][c]
            if val != 0:
                add_sudoku_row(dlx, r, c, val, is_given=True)

    # Empty cells - all possible values
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                for v in range(1, 10):
                    if is_valid_placement(board, r, c, v):
                        add_sudoku_row(dlx, r, c, v, is_given=False)

    return dlx


def add_sudoku_row(dlx: DLX, r: int, c: int, v: int, is_given: bool) -> None:
    """Add a row to DLX matrix for cell (r,c) = v.

    Row ID encodes: r*81 + c*9 + (v-1) for unique identification
    """
    row_id = r * 81 + c * 9 + (v - 1)

    # 4 constraints:
    # 1. Cell (r,c) has a value: 0-80
    cell_con = r * 9 + c
    # 2. Row r has value v: 81-161
    row_con = 81 + r * 9 + (v - 1)
    # 3. Col c has value v: 162-242
    col_con = 162 + c * 9 + (v - 1)
    # 4. Box b has value v: 243-323
    b = (r // 3) * 3 + (c // 3)
    box_con = 243 + b * 9 + (v - 1)

    dlx.add_row(row_id, [cell_con, row_con, col_con, box_con])


def count_solutions_dlx(board: Board, limit: int = 2) -> int:
    """Count solutions using DLX (much faster than backtracking)."""
    dlx = build_dlx_matrix(board)
    return dlx.count_solutions(limit)


def solve_board_dlx(board: Board) -> bool:
    """Solve board using DLX, modifying board in place."""
    dlx = build_dlx_matrix(board)
    if dlx.count_solutions(1) == 0:
        return False

    # Reconstruct solution
    for row_id in dlx.solution:
        r = row_id // 81
        c = (row_id % 81) // 9
        v = (row_id % 9) + 1
        board[r][c] = v
    return True


def count_solutions(board: Board, limit: int = 2) -> int:
    """Legacy backtracking solver (kept for compatibility)."""
    return count_solutions_dlx(board, limit)


def solve_board(board: Board) -> bool:
    """Legacy solver (kept for compatibility)."""
    return solve_board_dlx(board)


def is_valid_placement(board: Board, row: int, col: int, num: int) -> bool:
    if num == 0:
        return True

    for i in range(9):
        if (i != col and board[row][i] == num) or (i != row and board[i][col] == num):
            return False

    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for r in range(start_row, start_row + 3):
        for c in range(start_col, start_col + 3):
            if (r != row or c != col) and board[r][c] == num:
                return False
    return True


def check_win(board: Board, solution: Board) -> bool:
    return all(board[r][c] == solution[r][c] for r in range(9) for c in range(9))


# =============================================================================
# Import/Export Puzzle (81-character string format)
# =============================================================================

def board_to_string(board: Board) -> str:
    """Convert board to 81-character string (0 for empty cells)."""
    return ''.join(str(board[r][c]) for r in range(9) for c in range(9))


def string_to_board(s: str) -> Board:
    """Convert 81-character string to board (0 for empty cells)."""
    if len(s) != 81:
        raise ValueError("String must be exactly 81 characters")
    board = [[0] * 9 for _ in range(9)]
    for i, ch in enumerate(s):
        if ch not in '0123456789':
            raise ValueError(f"Invalid character: {ch}")
        r, c = divmod(i, 9)
        board[r][c] = int(ch)
    return board


def export_puzzle(board: Board, solution: Board) -> str:
    """Export puzzle as JSON string with board and solution."""
    import json
    data = {
        "board": board_to_string(board),
        "solution": board_to_string(solution),
    }
    return json.dumps(data)


def import_puzzle(data_str: str) -> tuple[Board, Board]:
    """Import puzzle from JSON string."""
    import json
    data = json.loads(data_str)
    board = string_to_board(data["board"])
    solution = string_to_board(data["solution"])
    return board, solution
