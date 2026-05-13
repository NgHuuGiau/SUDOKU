import copy
import random
from typing import List, Tuple

Board = List[List[int]]


def generate_sudoku(difficulty: str = "medium") -> Tuple[Board, Board]:
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
        "easy": side * side * 1 // 2,
        "medium": side * side * 3 // 4,
        "hard": side * side * 7 // 8,
    }
    empties = difficulties.get(difficulty, side * side * 3 // 4)

    for p in random.sample(range(side * side), empties):
        board[p // side][p % side] = 0

    return board, full_board_solution


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


def solve_board(board: Board) -> bool:
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                for num in range(1, 10):
                    if is_valid_placement(board, r, c, num):
                        board[r][c] = num
                        if solve_board(board):
                            return True
                        board[r][c] = 0
                return False
    return True


def check_win(board: Board, solution: Board) -> bool:
    return all(board[r][c] == solution[r][c] for r in range(9) for c in range(9))
