from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch
from torch.nn import functional as F
from torch.utils.data import DataLoader, TensorDataset

from gomoku_agent.board import Board
from gomoku_agent.checkpoint import load_compatible_checkpoint
from gomoku_agent.model import PolicyValueNet, masked_policy
from gomoku_agent.self_play import GameSample


def parse_args():
    p = argparse.ArgumentParser(description="v9 greedy sparring training for 15x15 Gomoku.")
    p.add_argument("--init-checkpoint", type=Path, required=True)
    p.add_argument("--out-checkpoint", type=Path, required=True)
    p.add_argument("--board-size", type=int, default=15)
    p.add_argument("--win-length", type=int, default=5)
    p.add_argument("--channels", type=int, default=64)
    p.add_argument("--blocks", type=int, default=4)
    p.add_argument("--games", type=int, default=200)
    p.add_argument("--epochs", type=int, default=3)
    p.add_argument("--batch-size", type=int, default=64)
    p.add_argument("--lr", type=float, default=3e-4)
    p.add_argument("--seed", type=int, default=9)
    p.add_argument("--max-moves", type=int, default=225)
    return p.parse_args()


def longest_line_score(board: Board, action: int, player: int) -> float:
    row, col = divmod(int(action), board.size)

    if board.grid[row, col] != 0:
        return -1e9

    score = 0.0
    center = (board.size - 1) / 2.0
    center_dist = abs(row - center) + abs(col - center)
    score += 0.01 * (board.size - center_dist)

    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]

    board.grid[row, col] = player
    try:
        for dr, dc in directions:
            count = 1

            r, c = row + dr, col + dc
            while 0 <= r < board.size and 0 <= c < board.size and board.grid[r, c] == player:
                count += 1
                r += dr
                c += dc

            r, c = row - dr, col - dc
            while 0 <= r < board.size and 0 <= c < board.size and board.grid[r, c] == player:
                count += 1
                r -= dr
                c -= dc

            score = max(score, float(count * count))
    finally:
        board.grid[row, col] = 0

    return score


def greedy_win_block_action(board: Board) -> int:
    player = board.current_player
    opponent = -player

    # 1. win immediately
    wins = board.immediate_winning_moves(player)
    if wins:
        return int(wins[0])

    # 2. block opponent immediate win
    blocks = board.immediate_winning_moves(opponent)
    if blocks:
        return int(blocks[0])

    # 3. otherwise extend strongest own line, with center tie-break
    legal = [int(a) for a in board.legal_moves()]
    best = max(legal, key=lambda a: longest_line_score(board, a, player))
    return int(best)


@torch.no_grad()
def model_action_and_policy(model, board: Board, device: torch.device, temperature: float = 1.0):
    state = torch.tensor(board.encode()[None, ...], dtype=torch.float32, device=device)
    legal = torch.tensor(board.legal_mask()[None, ...], dtype=torch.float32, device=device)
    logits, _ = model(state)
    probs = masked_policy(logits, legal, temperature=temperature)[0].cpu().numpy()
    action = int(np.random.choice(np.arange(board.size * board.size), p=probs))
    return action, probs.astype(np.float32)


def one_hot_policy(board: Board, action: int) -> np.ndarray:
    p = np.zeros(board.size * board.size, dtype=np.float32)
    p[int(action)] = 1.0
    return p


def play_sparring_game(model, board_size: int, win_length: int, device: torch.device, model_player: int):
    board = Board(size=board_size, win_length=win_length)
    trajectory = []

    while True:
        player = board.current_player
        state = board.encode()

        if player == model_player:
            action, policy = model_action_and_policy(model, board, device, temperature=1.0)
        else:
            action = greedy_win_block_action(board)
            policy = one_hot_policy(board, action)

        trajectory.append((state, policy, player))
        result = board.play_flat(action)

        if result.done:
            winner = result.winner
            break

    samples = []
    for state, policy, player in trajectory:
        if winner is None:
            value = 0.0
        else:
            value = 1.0 if player == winner else -1.0
        samples.append(GameSample(state=state, policy=policy, value=value))

    return samples, winner, board.move_count


def train_on_samples(model, optimizer, samples, batch_size, epochs, device):
    states = torch.tensor(np.stack([s.state for s in samples]), dtype=torch.float32)
    policies = torch.tensor(np.stack([s.policy for s in samples]), dtype=torch.float32)
    values = torch.tensor([s.value for s in samples], dtype=torch.float32)

    loader = DataLoader(
        TensorDataset(states, policies, values),
        batch_size=batch_size,
        shuffle=True,
    )

    model.train()
    for epoch in range(epochs):
        total = 0.0
        for batch_states, batch_policies, batch_values in loader:
            batch_states = batch_states.to(device)
            batch_policies = batch_policies.to(device)
            batch_values = batch_values.to(device)

            logits, pred_values = model(batch_states)
            policy_loss = -(batch_policies * F.log_softmax(logits, dim=-1)).sum(dim=-1).mean()
            value_loss = F.mse_loss(pred_values, batch_values)
            loss = policy_loss + value_loss

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total += float(loss.item()) * len(batch_states)

        print(f"epoch {epoch + 1}/{epochs}: loss={total / len(samples):.4f}", flush=True)


def main():
    args = parse_args()

    torch.manual_seed(args.seed)
    np.random.seed(args.seed)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"device={device}", flush=True)

    model = PolicyValueNet(args.board_size, args.channels, args.blocks).to(device)

    load_compatible_checkpoint(
        model,
        args.init_checkpoint,
        device,
        board_size=args.board_size,
        channels=args.channels,
        blocks=args.blocks,
    )

    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)

    all_samples = []
    model_wins = 0
    greedy_wins = 0
    draws = 0
    move_counts = []

    for g in range(args.games):
        model_player = 1 if g % 2 == 0 else -1
        samples, winner, moves = play_sparring_game(
            model,
            board_size=args.board_size,
            win_length=args.win_length,
            device=device,
            model_player=model_player,
        )

        all_samples.extend(samples)
        move_counts.append(moves)

        if winner is None:
            draws += 1
            outcome = "draw"
        elif winner == model_player:
            model_wins += 1
            outcome = "model_win"
        else:
            greedy_wins += 1
            outcome = "greedy_win"

        print(
            f"game {g + 1}/{args.games}: {outcome}, moves={moves}, "
            f"model_player={'black' if model_player == 1 else 'white'}",
            flush=True,
        )

    print(
        f"sparring summary: model_wins={model_wins}, greedy_wins={greedy_wins}, "
        f"draws={draws}, avg_moves={np.mean(move_counts):.2f}, samples={len(all_samples)}",
        flush=True,
    )

    train_on_samples(model, optimizer, all_samples, args.batch_size, args.epochs, device)

    args.out_checkpoint.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "model": model.state_dict(),
            "board_size": args.board_size,
            "win_length": args.win_length,
            "channels": args.channels,
            "blocks": args.blocks,
        },
        args.out_checkpoint,
    )
    print(f"saved {args.out_checkpoint}", flush=True)


if __name__ == "__main__":
    main()
