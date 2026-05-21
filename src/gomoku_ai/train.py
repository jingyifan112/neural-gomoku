from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import torch
from torch.nn import functional as F
from torch.utils.data import DataLoader, TensorDataset

from .checkpoint import load_compatible_checkpoint
from .mcts import MCTSConfig
from .model import PolicyValueNet
from .self_play import play_game


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train a neural Gomoku policy-value model with self-play.")
    parser.add_argument("--board-size", type=int, default=15)
    parser.add_argument("--win-length", type=int, default=5)
    parser.add_argument("--games", type=int, default=100)
    parser.add_argument("--iterations", type=int, default=5)
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--channels", type=int, default=64)
    parser.add_argument("--blocks", type=int, default=4)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--replay-size", type=int, default=20000)
    parser.add_argument("--temperature", type=float, default=1.0)
    parser.add_argument("--mcts-sims", type=int, default=64)
    parser.add_argument("--c-puct", type=float, default=1.5)
    parser.add_argument("--dirichlet-alpha", type=float, default=0.3)
    parser.add_argument("--exploration-fraction", type=float, default=0.25)
    parser.add_argument("--allow-immediate-loss", action="store_true")
    parser.add_argument("--checkpoint", type=Path, default=Path("checkpoints/latest.pt"))
    parser.add_argument("--seed", type=int, default=7)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = PolicyValueNet(args.board_size, args.channels, args.blocks).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)

    load_compatible_checkpoint(
        model,
        args.checkpoint,
        device,
        board_size=args.board_size,
        channels=args.channels,
        blocks=args.blocks,
    )

    replay = []
    for iteration in range(args.iterations):
        model.eval()
        fresh_samples = []
        mcts_config = None
        if args.mcts_sims > 0:
            mcts_config = MCTSConfig(
                simulations=args.mcts_sims,
                c_puct=args.c_puct,
                temperature=args.temperature,
                dirichlet_alpha=args.dirichlet_alpha,
                exploration_fraction=args.exploration_fraction,
                avoid_immediate_loss=not args.allow_immediate_loss,
            )
        for game_idx in range(args.games):
            game_samples = play_game(
                model,
                board_size=args.board_size,
                win_length=args.win_length,
                device=device,
                temperature=args.temperature,
                mcts_config=mcts_config,
            )
            fresh_samples.extend(game_samples)
            print(
                f"iteration {iteration + 1}/{args.iterations} "
                f"self-play game {game_idx + 1}/{args.games}: {len(game_samples)} moves",
                flush=True,
            )

        replay.extend(fresh_samples)
        replay = replay[-args.replay_size :]
        print(
            f"iteration {iteration + 1}/{args.iterations}: "
            f"training on {len(replay)} replay samples",
            flush=True,
        )
        train_on_samples(model, optimizer, replay, args.batch_size, args.epochs, device)

    args.checkpoint.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "model": model.state_dict(),
            "board_size": args.board_size,
            "win_length": args.win_length,
            "channels": args.channels,
            "blocks": args.blocks,
        },
        args.checkpoint,
    )
    print(f"saved {args.checkpoint}", flush=True)


def train_on_samples(
    model: PolicyValueNet,
    optimizer: torch.optim.Optimizer,
    samples: list,
    batch_size: int,
    epochs: int,
    device: torch.device,
) -> None:
    states = torch.tensor(np.stack([s.state for s in samples]), dtype=torch.float32)
    policies = torch.tensor(np.stack([s.policy for s in samples]), dtype=torch.float32)
    values = torch.tensor([s.value for s in samples], dtype=torch.float32)
    loader = DataLoader(TensorDataset(states, policies, values), batch_size=batch_size, shuffle=True)

    model.train()
    for epoch in range(epochs):
        total_loss = 0.0
        for batch_states, batch_policies, batch_values in loader:
            batch_states = batch_states.to(device)
            batch_policies = batch_policies.to(device)
            batch_values = batch_values.to(device)

            logits, predicted_values = model(batch_states)
            policy_loss = -(batch_policies * F.log_softmax(logits, dim=-1)).sum(dim=-1).mean()
            value_loss = F.mse_loss(predicted_values, batch_values)
            loss = policy_loss + value_loss

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total_loss += float(loss.item()) * len(batch_states)

        print(f"epoch {epoch + 1}/{epochs}: loss={total_loss / len(samples):.4f}", flush=True)


if __name__ == "__main__":
    main()
