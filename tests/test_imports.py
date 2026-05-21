def test_import_board_without_torch():
    from gomoku_ai.board import Board

    assert Board(size=9).size == 9
