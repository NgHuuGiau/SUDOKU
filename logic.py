# Chứa logic xử lý chính cho trò chơi Sudoku: tạo bảng, kiểm tra tính hợp lệ và giải thuật
import random
import copy
from typing import List, Tuple

Board = List[List[int]]

def generate_sudoku(difficulty: str = "medium") -> Tuple[Board, Board]:
    # Tạo bảng Sudoku ngẫu nhiên dựa trên độ khó được chọn
    base = 3
    side = base * base
    def pattern(r, c): return (base * (r % base) + r // base + c) % side
    def shuffle(s): return random.sample(s, len(s))

    rBase = range(base)
    rows = [g * base + r for g in shuffle(rBase) for r in shuffle(rBase)]
    cols = [g * base + c for g in shuffle(rBase) for c in shuffle(rBase)]
    nums = shuffle(range(1, side + 1))

    # Tạo bảng hoàn chỉnh (đã giải xong)
    board = [[nums[pattern(r, c)] for c in cols] for r in rows]
    full_board_solution = copy.deepcopy(board)

    # Thiết lập số lượng ô trống dựa theo mức độ khó
    difficulties = {
        "easy": side * side * 1 // 2,
        "medium": side * side * 3 // 4,
        "hard": side * side * 7 // 8
    }
    empties = difficulties.get(difficulty, side * side * 3 // 4)

    # Xóa ngẫu nhiên các ô để tạo câu đố
    for p in random.sample(range(side * side), empties):
        board[p // side][p % side] = 0

    return board, full_board_solution

def is_valid_placement(board: Board, row: int, col: int, num: int) -> bool:
    # Kiểm tra xem việc đặt một con số vào vị trí (row, col) có hợp lệ không
    if num == 0:
        return True

    # Kiểm tra tính hợp lệ trên hàng và cột
    for i in range(9):
        if (i != col and board[row][i] == num) or (i != row and board[i][col] == num):
            return False

    # Kiểm tra tính hợp lệ trong khối 3x3
    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for r in range(start_row, start_row + 3):
        for c in range(start_col, start_col + 3):
            if (r != row or c != col) and board[r][c] == num:
                return False
    return True

def solve_board(board: Board) -> bool:
    # Giải bảng Sudoku bằng thuật toán quay lui (Backtracking)
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
    # So sánh bảng hiện tại với lời giải để kiểm tra điều kiện thắng
    return all(board[r][c] == solution[r][c] for r in range(9) for c in range(9))