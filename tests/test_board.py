import numpy as np

from gomoku_ai.board import BLACK, WHITE, Board


def test_horizontal_win():
    board = Board(size=9, win_length=5)
    result = None
    for col in range(5):
        result = board.play(0, col)
        if col < 4:
            board.play(1, col)
    assert result is not None
    assert result.done
    assert result.winner == BLACK


def test_diagonal_win():
    board = Board(size=9, win_length=5)
    black_moves = [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4)]
    white_moves = [(0, 1), (0, 2), (0, 3), (0, 4)]
    result = None
    for idx, move in enumerate(black_moves):
        result = board.play(*move)
        if idx < len(white_moves):
            board.play(*white_moves[idx])
    assert result is not None
    assert result.done
    assert result.winner == BLACK


def test_encode_current_perspective_flips_after_move():
    board = Board(size=9, win_length=5)
    board.play(4, 4)
    encoded = board.encode()
    assert encoded.shape == (3, 9, 9)
    assert encoded[1, 4, 4] == 1.0
    assert board.current_player == WHITE


def test_legal_mask_updates():
    board = Board(size=9, win_length=5)
    assert np.sum(board.legal_mask()) == 81
    board.play(4, 4)
    assert np.sum(board.legal_mask()) == 80
    assert board.legal_mask()[4 * 9 + 4] == 0
