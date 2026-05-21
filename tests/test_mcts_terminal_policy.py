import numpy as np

from gomoku_ai.board import Board
from gomoku_ai.search_safety import forced_terminal_policy


def test_forced_terminal_policy_blocks_opponent_win():
    board = Board(size=9, win_length=5)
    moves = [(4, 0), (0, 2), (4, 1), (0, 4), (4, 2), (1, 0), (4, 3)]
    for row, col in moves:
        board.play(row, col)

    forced = forced_terminal_policy(board, temperature=0)

    assert forced is not None
    action, probs = forced
    assert action == 4 * 9 + 4
    assert np.argmax(probs) == 4 * 9 + 4


def test_forced_terminal_policy_takes_own_win_first():
    board = Board(size=9, win_length=5)
    moves = [(0, 0), (4, 0), (0, 1), (4, 1), (0, 2), (4, 2), (0, 3)]
    for row, col in moves:
        board.play(row, col)

    forced = forced_terminal_policy(board, temperature=0)

    assert forced is not None
    action, _ = forced
    assert action == 0 * 9 + 4
