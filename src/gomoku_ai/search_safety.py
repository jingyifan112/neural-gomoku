from __future__ import annotations

import numpy as np

from .board import Board


def filter_immediate_losses(board: Board, visits: np.ndarray) -> np.ndarray:
    winning_moves = board.immediate_winning_moves(board.current_player)
    if winning_moves:
        return _restrict_to_moves(visits, winning_moves)

    legal_moves = board.legal_moves()
    if len(legal_moves) <= 1:
        return visits

    safe_moves: list[int] = []

    for action in legal_moves:
        scratch = board.clone()
        result = scratch.play_flat(int(action))
        if result.done or not opponent_has_forcing_terminal_reply(scratch):
            safe_moves.append(int(action))

    if safe_moves:
        return _restrict_to_moves(visits, safe_moves)
    return visits


def filter_unavoidable_terminal_replies(board: Board, visits: np.ndarray) -> np.ndarray:
    return filter_immediate_losses(board, visits)


def opponent_has_forcing_terminal_reply(board_after_our_move: Board) -> bool:
    opponent = board_after_our_move.current_player
    if board_after_our_move.immediate_winning_moves(opponent):
        return True

    for reply in board_after_our_move.legal_moves():
        scratch = board_after_our_move.clone()
        result = scratch.play_flat(int(reply))
        if result.done:
            return True

        future_wins = scratch.immediate_winning_moves(opponent)
        if len(future_wins) >= 2:
            return True

    return False


def forced_terminal_policy(board: Board, temperature: float) -> tuple[int, np.ndarray] | None:
    own_wins = board.immediate_winning_moves(board.current_player)
    if own_wins:
        probs = moves_to_probs(board, own_wins, temperature)
        action = int(np.random.choice(np.arange(board.size * board.size), p=probs))
        return action, probs

    opponent_wins = board.immediate_winning_moves(-board.current_player)
    if opponent_wins:
        probs = moves_to_probs(board, opponent_wins, temperature)
        action = int(np.random.choice(np.arange(board.size * board.size), p=probs))
        return action, probs

    return None


def moves_to_probs(board: Board, moves: list[int], temperature: float) -> np.ndarray:
    probs = np.zeros(board.size * board.size, dtype=np.float32)
    if temperature <= 0 or len(moves) == 1:
        probs[int(moves[0])] = 1.0
        return probs

    for action in moves:
        probs[int(action)] = 1.0 / len(moves)
    return probs


def _restrict_to_moves(visits: np.ndarray, moves: list[int]) -> np.ndarray:
    restricted = np.zeros_like(visits, dtype=np.float32)
    for action in moves:
        restricted[action] = visits[action]

    if restricted.sum() > 0:
        return restricted

    for action in moves:
        restricted[action] = 1.0
    return restricted
