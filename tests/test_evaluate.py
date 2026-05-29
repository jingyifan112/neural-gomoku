from gomoku_agent.board import BLACK, WHITE, Board
from gomoku_agent.evaluate import choose_greedy_win_block_move


def test_greedy_win_block_takes_immediate_win():
    board = Board(size=9, win_length=5)
    board.current_player = BLACK
    board.grid[4, 1] = BLACK
    board.grid[4, 2] = BLACK
    board.grid[4, 3] = BLACK
    board.grid[4, 4] = BLACK
    board.grid[4, 0] = WHITE
    board.move_count = 5

    action = choose_greedy_win_block_move(board, rng=None)

    assert action == 4 * 9 + 5


def test_greedy_win_block_blocks_opponent_immediate_win():
    board = Board(size=9, win_length=5)
    board.current_player = BLACK
    board.grid[4, 0] = BLACK
    board.grid[4, 1] = WHITE
    board.grid[4, 2] = WHITE
    board.grid[4, 3] = WHITE
    board.grid[4, 4] = WHITE
    board.move_count = 5

    action = choose_greedy_win_block_move(board, rng=None)

    assert action == 4 * 9 + 5
