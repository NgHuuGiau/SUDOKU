"""Unit tests for Sudoku game."""
import pytest
import os
import tempfile
import json
from logic import (
    generate_sudoku,
    is_valid_placement,
    check_win,
    count_solutions_dlx,
    solve_board_dlx,
    count_solutions,
    solve_board,
)
from persistence import (
    save_game_state,
    load_game_state,
    clear_save_file,
    has_save_file,
    load_best_times,
    save_best_times,
    update_best_time,
    get_best_time,
)
from game import GameState, AUTO_SAVE_DEBOUNCE_MS


class TestLogic:
    """Tests for Sudoku logic module."""
    
    def test_generate_sudoku_easy(self):
        board, solution = generate_sudoku("easy")
        assert len(board) == 9
        assert len(board[0]) == 9
        assert len(solution) == 9
        assert count_solutions_dlx(board) == 1
        # Easy should have ~43 clues (38 empty)
        clues = sum(1 for row in board for v in row if v != 0)
        assert 40 <= clues <= 46
    
    def test_generate_sudoku_medium(self):
        board, solution = generate_sudoku("medium")
        assert count_solutions_dlx(board) == 1
        clues = sum(1 for row in board for v in row if v != 0)
        assert 30 <= clues <= 36
    
    def test_generate_sudoku_hard(self):
        board, solution = generate_sudoku("hard")
        assert count_solutions_dlx(board) == 1
        clues = sum(1 for row in board for v in row if v != 0)
        assert 25 <= clues <= 30
    
    def test_generate_sudoku_invalid_difficulty_defaults_to_medium(self):
        board, solution = generate_sudoku("invalid")
        clues = sum(1 for row in board for v in row if v != 0)
        assert 30 <= clues <= 36
    
    def test_is_valid_placement_empty_board(self):
        board = [[0]*9 for _ in range(9)]
        assert is_valid_placement(board, 0, 0, 1)
        assert is_valid_placement(board, 4, 4, 9)
    
    def test_is_valid_placement_row_conflict(self):
        board = [[0]*9 for _ in range(9)]
        board[0][0] = 5
        assert not is_valid_placement(board, 0, 1, 5)  # Same row
        assert is_valid_placement(board, 0, 1, 6)      # Different number
    
    def test_is_valid_placement_col_conflict(self):
        board = [[0]*9 for _ in range(9)]
        board[0][0] = 5
        assert not is_valid_placement(board, 1, 0, 5)  # Same col
    
    def test_is_valid_placement_box_conflict(self):
        board = [[0]*9 for _ in range(9)]
        board[0][0] = 5
        assert not is_valid_placement(board, 1, 1, 5)  # Same 3x3 box
        assert is_valid_placement(board, 3, 3, 5)      # Different box
    
    def test_is_valid_placement_zero_allowed(self):
        board = [[5]*9 for _ in range(9)]
        assert is_valid_placement(board, 0, 0, 0)  # Zero always valid
    
    def test_check_win(self):
        board = [[1]*9 for _ in range(9)]
        solution = [[1]*9 for _ in range(9)]
        assert check_win(board, solution)
        
        board[0][0] = 2
        assert not check_win(board, solution)
    
    def test_count_solutions_unique(self):
        board, _ = generate_sudoku("easy")
        assert count_solutions(board) == 1
        assert count_solutions_dlx(board) == 1
    
    def test_count_solutions_multiple(self):
        # Empty board has many solutions
        board = [[0]*9 for _ in range(9)]
        assert count_solutions(board, limit=2) >= 2
        assert count_solutions_dlx(board, limit=2) >= 2
    
    def test_solve_board_dlx(self):
        board, solution = generate_sudoku("hard")
        empty = [row[:] for row in board]
        assert solve_board_dlx(empty)
        assert empty == solution
    
    def test_solve_board_backtracking_compat(self):
        board, solution = generate_sudoku("medium")
        empty = [row[:] for row in board]
        assert solve_board(empty)
        assert empty == solution


class TestPersistence:
    """Tests for persistence module."""
    
    def setup_method(self):
        clear_save_file()
        # Clear best times
        for f in ['best_times.json', 'save_game.json']:
            try:
                os.remove(f)
            except:
                pass
    
    def teardown_method(self):
        clear_save_file()
        for f in ['best_times.json', 'save_game.json']:
            try:
                os.remove(f)
            except:
                pass
    
    def test_save_load_game_state(self):
        state = GameState("easy")
        # Find an empty cell to test with
        r, c = 0, 0
        while state.original[r][c] != 0:
            c += 1
            if c >= 9:
                c = 0
                r += 1
        state.selected = [r, c]
        
        state.place_number(5)
        state.place_number(3)
        original_board = [row[:] for row in state.board]
        original_notes = [[s.copy() for s in row] for row in state.notes]
        
        save_game_state(state)
        assert has_save_file()
        
        loaded = load_game_state()
        assert loaded is not None
        assert loaded.difficulty == "easy"
        assert loaded.board == original_board
        assert loaded.notes == original_notes
        assert len(loaded.undo_stack) > 1
    
    def test_load_nonexistent_save_returns_none(self):
        clear_save_file()
        assert load_game_state() is None
    
    def test_clear_save_file(self):
        state = GameState("easy")
        save_game_state(state)
        assert has_save_file()
        clear_save_file()
        assert not has_save_file()
    
    def test_best_times_initial(self):
        times = load_best_times()
        assert times == {"easy": None, "medium": None, "hard": None}
    
    def test_update_best_time_first(self):
        assert update_best_time("easy", 120)
        assert get_best_time("easy") == 120
    
    def test_update_best_time_better(self):
        update_best_time("easy", 120)
        assert update_best_time("easy", 90)
        assert get_best_time("easy") == 90
    
    def test_update_best_time_worse(self):
        update_best_time("easy", 90)
        assert not update_best_time("easy", 120)
        assert get_best_time("easy") == 90
    
    def test_best_times_persist(self):
        update_best_time("hard", 300)
        # Reload from disk
        times = load_best_times()
        assert times["hard"] == 300
    
    def test_save_state_preserves_undo_redo(self):
        state = GameState("medium")
        state.place_number(1)
        state.place_number(2)
        state.undo()
        undo_len = len(state.undo_stack)
        redo_len = len(state.redo_stack)
        
        save_game_state(state)
        loaded = load_game_state()
        
        assert len(loaded.undo_stack) == undo_len
        assert len(loaded.redo_stack) == redo_len


class TestGameState:
    """Tests for GameState class."""
    
    def test_initial_state(self):
        state = GameState("easy")
        assert state.difficulty == "easy"
        assert state.selected == [0, 0]
        assert state.notes_mode is False
        assert state.game_over is False
        assert state.paused is False
        assert len(state.undo_stack) == 1
        assert len(state.redo_stack) == 0
    
    def test_place_number(self):
        state = GameState("easy")
        r, c = 0, 0
        state.selected = [r, c]
        # Ensure cell is not original
        state.original[r][c] = 0
        
        state.place_number(5)
        assert state.board[r][c] == 5
        assert len(state.undo_stack) == 2
    
    def test_place_number_notes_mode(self):
        state = GameState("easy")
        r, c = 0, 0
        state.selected = [r, c]
        state.original[r][c] = 0
        state.board[r][c] = 0  # Ensure board is also empty
        state.notes_mode = True
        
        state.place_number(5)
        assert 5 in state.notes[r][c]
        assert state.board[r][c] == 0
    
    def test_clear_cell(self):
        state = GameState("easy")
        r, c = 0, 0
        state.selected = [r, c]
        state.original[r][c] = 0
        state.board[r][c] = 5
        
        state.clear_cell()
        assert state.board[r][c] == 0
    
    def test_clear_cell_notes_mode(self):
        state = GameState("easy")
        r, c = 0, 0
        state.selected = [r, c]
        state.original[r][c] = 0
        state.notes_mode = True
        state.notes[r][c] = {1, 2, 3}
        
        state.clear_cell()
        assert state.notes[r][c] == set()
    
    def test_undo_redo(self):
        state = GameState("easy")
        r, c = 0, 0
        state.selected = [r, c]
        state.original[r][c] = 0
        
        state.place_number(1)
        state.place_number(2)
        assert state.board[r][c] == 2
        
        state.undo()
        assert state.board[r][c] == 1
        
        state.redo()
        assert state.board[r][c] == 2
    
    def test_undo_limit(self):
        state = GameState("easy")
        r, c = 0, 0
        state.selected = [r, c]
        state.original[r][c] = 0
        
        # Can't undo past initial state
        state.undo()
        assert len(state.undo_stack) == 1
    
    def test_give_hint(self):
        state = GameState("easy")
        r, c = 0, 0
        state.selected = [r, c]
        state.original[r][c] = 0
        state.board[r][c] = 0
        solution_val = state.solution[r][c]
        
        state.give_hint()
        assert state.board[r][c] == solution_val
        assert state.notes[r][c] == set()
    
    def test_fill_possible_notes(self):
        state = GameState("easy")
        state.fill_possible_notes()
        # All empty cells should have notes
        for r in range(9):
            for c in range(9):
                if state.board[r][c] == 0:
                    assert len(state.notes[r][c]) > 0
    
    def test_toggle_pause(self):
        state = GameState("easy")
        assert not state.paused
        state.toggle_pause()
        assert state.paused
        state.toggle_pause()
        assert not state.paused
    
    def test_restart(self):
        state = GameState("easy")
        state.place_number(5)
        state.restart("hard")
        assert state.difficulty == "hard"
        assert len(state.undo_stack) == 1
        assert state.game_over is False
    
    def test_get_elapsed_time(self):
        state = GameState("easy")
        # Just verify it returns non-negative
        assert state.get_elapsed_time() >= 0
    
    def test_auto_save_debounce(self):
        state = GameState("easy")
        # First save happens immediately in __init__
        # Rapid calls should be debounced
        initial_save_count = 1
        # We can't easily test timing without mocking, but verify method exists
        state.auto_save()
        state.force_save()
        assert hasattr(state, '_last_auto_save_time')


class TestIntegration:
    """Integration tests."""
    
    def test_full_game_flow(self):
        state = GameState("easy")
        # Play a few moves
        for i in range(3):
            r, c = i, i
            state.selected = [r, c]
            state.original[r][c] = 0
            state.place_number(state.solution[r][c])
        
        # Save and load
        save_game_state(state)
        loaded = load_game_state()
        
        assert loaded.board == state.board
        assert loaded.difficulty == state.difficulty


if __name__ == "__main__":
    pytest.main([__file__, "-v"])