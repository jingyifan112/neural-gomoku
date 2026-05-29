import numpy as np

from gomoku_agent.board import BLACK, WHITE
from gomoku_agent.tactical_data import (
    case_to_sample,
    generate_tactical_cases,
    make_diagonal_two_step_fork_prevention_case,
    make_diamond_cross_case,
)


def test_diamond_cross_case_targets_center_before_fork():
    case = make_diamond_cross_case(board_size=9)

    assert case.name == "diamond_to_cross_fork"
    assert case.board.current_player == WHITE
    assert case.board.grid[4, 3] == 0
    assert case.board.grid[3, 3] == BLACK
    assert case.board.grid[4, 2] == BLACK
    assert case.board.grid[4, 4] == BLACK
    assert case.board.grid[5, 3] == BLACK
    assert case.target_moves == (4 * 9 + 3,)

    sample = case_to_sample(case)
    assert sample.state.shape == (3, 9, 9)
    assert sample.policy[4 * 9 + 3] == 1.0
    assert np.isclose(sample.policy.sum(), 1.0)


def test_diagonal_two_step_fork_case_targets_setup_points():
    case = make_diagonal_two_step_fork_prevention_case(board_size=9)

    assert case.name == "diagonal_two_step_fork_prevention"
    assert case.board.current_player == WHITE
    assert case.board.grid[2, 6] == 0
    assert case.board.grid[5, 3] == 0
    assert case.target_moves == (2 * 9 + 6, 5 * 9 + 3)

    sample = case_to_sample(case)
    assert sample.policy[2 * 9 + 6] == 0.5
    assert sample.policy[5 * 9 + 3] == 0.5
    assert np.isclose(sample.policy.sum(), 1.0)


def test_generated_tactical_cases_have_legal_targets():
    cases = generate_tactical_cases(18, board_size=9, seed=123)

    assert len(cases) == 18
    assert "diagonal_two_step_fork_prevention" in {case.name for case in cases}
    for case in cases:
        legal = set(case.board.legal_moves())
        assert set(case.target_moves).issubset(legal)
