from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import torch

from .board import Board
from .model import PolicyValueNet, masked_policy
from .search_safety import filter_unavoidable_terminal_replies, forced_terminal_policy


@dataclass
class MCTSConfig:
    simulations: int = 64
    c_puct: float = 1.5
    temperature: float = 1.0
    dirichlet_alpha: float = 0.3
    exploration_fraction: float = 0.25
    avoid_immediate_loss: bool = True


@dataclass
class Node:
    prior: float
    player: int
    visit_count: int = 0
    value_sum: float = 0.0
    children: dict[int, "Node"] = field(default_factory=dict)

    @property
    def expanded(self) -> bool:
        return len(self.children) > 0

    @property
    def value(self) -> float:
        if self.visit_count == 0:
            return 0.0
        return self.value_sum / self.visit_count


@torch.no_grad()
def run_mcts(
    model: PolicyValueNet,
    board: Board,
    device: torch.device,
    config: MCTSConfig,
    add_noise: bool = False,
) -> tuple[int, np.ndarray]:
    if config.avoid_immediate_loss:
        forced = forced_terminal_policy(board, config.temperature)
        if forced is not None:
            return forced

    root = Node(prior=1.0, player=board.current_player)
    _expand(root, board, model, device)
    if add_noise:
        _add_dirichlet_noise(root, config)

    for _ in range(config.simulations):
        scratch = board.clone()
        _search(root, scratch, model, device, config)

    visits = np.zeros(board.size * board.size, dtype=np.float32)
    for action, child in root.children.items():
        visits[action] = child.visit_count

    if visits.sum() == 0:
        visits[board.legal_moves()] = 1.0

    if config.avoid_immediate_loss:
        visits = filter_unavoidable_terminal_replies(board, visits)

    probs = _visits_to_probs(visits, config.temperature)
    action = int(np.random.choice(np.arange(board.size * board.size), p=probs))
    return action, probs


def _search(
    node: Node,
    board: Board,
    model: PolicyValueNet,
    device: torch.device,
    config: MCTSConfig,
) -> float:
    if not node.expanded:
        value = _expand(node, board, model, device)
        node.visit_count += 1
        node.value_sum += value
        return value

    action, child = _select_child(node, config)
    player = board.current_player
    result = board.play_flat(action)

    if result.done:
        if result.winner is None:
            child_value = 0.0
        else:
            child_value = -1.0 if result.winner == player else 1.0
        child.visit_count += 1
        child.value_sum += child_value
    else:
        child_value = _search(child, board, model, device, config)

    value = -child_value
    node.visit_count += 1
    node.value_sum += value
    return value


def _select_child(node: Node, config: MCTSConfig) -> tuple[int, Node]:
    best_score = -float("inf")
    best_action = -1
    best_child: Node | None = None

    parent_sqrt = np.sqrt(max(1, node.visit_count))
    for action, child in node.children.items():
        q_value = -child.value
        u_value = config.c_puct * child.prior * parent_sqrt / (1 + child.visit_count)
        score = q_value + u_value
        if score > best_score:
            best_score = score
            best_action = action
            best_child = child

    if best_child is None:
        raise RuntimeError("cannot select from an unexpanded node")
    return best_action, best_child


@torch.no_grad()
def _expand(node: Node, board: Board, model: PolicyValueNet, device: torch.device) -> float:
    state = torch.tensor(board.encode()[None, ...], dtype=torch.float32, device=device)
    legal = torch.tensor(board.legal_mask()[None, ...], dtype=torch.float32, device=device)
    logits, value = model(state)
    priors = masked_policy(logits, legal)[0].cpu().numpy()

    for action in board.legal_moves():
        node.children[int(action)] = Node(prior=float(priors[action]), player=-board.current_player)
    return float(value.item())


def _add_dirichlet_noise(root: Node, config: MCTSConfig) -> None:
    actions = list(root.children)
    if not actions:
        return
    noise = np.random.dirichlet([config.dirichlet_alpha] * len(actions))
    for action, sample in zip(actions, noise):
        child = root.children[action]
        child.prior = (1 - config.exploration_fraction) * child.prior + config.exploration_fraction * float(sample)


def _visits_to_probs(visits: np.ndarray, temperature: float) -> np.ndarray:
    if temperature <= 0:
        probs = np.zeros_like(visits, dtype=np.float32)
        probs[int(np.argmax(visits))] = 1.0
        return probs

    adjusted = visits.astype(np.float64) ** (1.0 / temperature)
    total = adjusted.sum()
    if total <= 0:
        return np.ones_like(visits, dtype=np.float32) / len(visits)
    return (adjusted / total).astype(np.float32)
