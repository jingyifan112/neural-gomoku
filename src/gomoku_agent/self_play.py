from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import torch

from .board import Board
from .mcts import MCTSConfig, run_mcts
from .model import PolicyValueNet, masked_policy


@dataclass
class GameSample:
    state: np.ndarray
    policy: np.ndarray
    value: float


@torch.no_grad()
def choose_action(
    model: PolicyValueNet,
    board: Board,
    device: torch.device,
    temperature: float = 1.0,
    sample: bool = True,
) -> tuple[int, np.ndarray]:
    state = torch.tensor(board.encode()[None, ...], dtype=torch.float32, device=device)
    legal = torch.tensor(board.legal_mask()[None, ...], dtype=torch.float32, device=device)
    logits, _ = model(state)
    probs = masked_policy(logits, legal, temperature=temperature)[0].cpu().numpy()
    if sample:
        action = int(np.random.choice(np.arange(board.size * board.size), p=probs))
    else:
        action = int(np.argmax(probs))
    return action, probs.astype(np.float32)


def play_game(
    model: PolicyValueNet,
    board_size: int,
    win_length: int,
    device: torch.device,
    temperature: float = 1.0,
    mcts_config: MCTSConfig | None = None,
) -> list[GameSample]:
    board = Board(size=board_size, win_length=win_length)
    trajectory: list[tuple[np.ndarray, np.ndarray, int]] = []

    while True:
        player = board.current_player
        state = board.encode()
        if mcts_config is None:
            action, policy = choose_action(model, board, device, temperature=temperature)
        else:
            action, policy = run_mcts(model, board, device, mcts_config, add_noise=True)
        trajectory.append((state, policy, player))
        result = board.play_flat(action)
        if result.done:
            winner = result.winner
            break

    samples: list[GameSample] = []
    for state, policy, player in trajectory:
        if winner is None:
            value = 0.0
        else:
            value = 1.0 if player == winner else -1.0
        samples.append(GameSample(state=state, policy=policy, value=value))
    return samples
