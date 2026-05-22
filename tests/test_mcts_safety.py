import numpy as np

from gomoku_agent.board import BLACK, Board
from gomoku_agent.search_safety import filter_immediate_losses, filter_unavoidable_terminal_replies


def test_immediate_winning_moves():
    board = Board(size=9, win_length=5)
    for col in range(4):
        board.play(4, col)
        board.play(0, col)

    wins = board.immediate_winning_moves(BLACK)

    assert 4 * 9 + 4 in wins


def test_filter_removes_moves_that_allow_next_turn_win():
    board = Board(size=9, win_length=5)
    for col in range(4):
        board.play(4, col)
        board.play(0, col)

    visits = np.ones(81, dtype=np.float32)
    visits[board.legal_mask() == 0] = 0

    filtered = filter_immediate_losses(board, visits)

    assert filtered[4 * 9 + 4] > 0
    assert filtered[5 * 9 + 5] == 0


def test_filter_keeps_unvisited_blocking_move_when_all_visits_are_unsafe():
    board = Board(size=9, win_length=5)
    for col in range(4):
        board.play(4, col)
        board.play(0, col)

    visits = np.zeros(81, dtype=np.float32)
    visits[5 * 9 + 5] = 10

    filtered = filter_immediate_losses(board, visits)

    assert filtered[4 * 9 + 4] > 0
    assert filtered[5 * 9 + 5] == 0


def test_filter_prefers_current_player_immediate_win():
    board = Board(size=9, win_length=5)
    for col in range(4):
        board.play(4, col)
        board.play(0, col)
    board.play(7, 7)

    visits = np.ones(81, dtype=np.float32)
    filtered = filter_immediate_losses(board, visits)

    assert filtered[0 * 9 + 4] > 0
    assert filtered[5 * 9 + 5] == 0


def test_filter_prevents_open_four_fork_before_it_is_too_late():
    board = Board(size=9, win_length=5)
    moves = [(4, 1), (0, 0), (4, 2), (0, 1), (4, 3)]
    for row, col in moves:
        board.play(row, col)

    visits = np.ones(81, dtype=np.float32)
    visits[board.legal_mask() == 0] = 0
    filtered = filter_unavoidable_terminal_replies(board, visits)

    assert filtered[4 * 9 + 0] > 0
    assert filtered[4 * 9 + 4] > 0
    assert filtered[0 * 9 + 2] == 0
