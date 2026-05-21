from gomoku_ai.board import Board
from gomoku_ai.search_safety import forced_terminal_policy


def test_play_entry_forced_policy_blocks_open_end_after_model_side_move():
    board = Board(size=9, win_length=5)
    moves = [(4, 1), (4, 0), (4, 2), (0, 2), (4, 3), (0, 4), (4, 4)]
    for row, col in moves:
        board.play(row, col)

    forced = forced_terminal_policy(board, temperature=0)

    assert forced is not None
    action, _ = forced
    assert divmod(action, board.size) == (4, 5)
