from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import torch
from torch.nn import functional as F

from gomoku_agent.checkpoint import load_compatible_checkpoint
from gomoku_agent.model import PolicyValueNet


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train Candidate G teacher policy-distillation checkpoint.")
    parser.add_argument(
        "--dataset",
        type=Path,
        default=Path("analysis/integration_eval/candidate_g_teacher_policy_dataset.json"),
    )
    parser.add_argument("--init-checkpoint", type=Path, required=True)
    parser.add_argument(
        "--out-checkpoint",
        type=Path,
        default=Path("checkpoints/15x15_candidate_g_teacher_policy.pt"),
    )
    parser.add_argument("--epochs", type=int, default=80)
    parser.add_argument("--lr", type=float, default=5e-4)
    parser.add_argument("--kl-weight", type=float, default=0.15)
    parser.add_argument("--weight-decay", type=float, default=1e-4)
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument("--print-every", type=int, default=10)
    parser.add_argument("--board-size", type=int, default=15)
    parser.add_argument("--win-length", type=int, default=5)
    parser.add_argument("--channels", type=int, default=64)
    parser.add_argument("--blocks", type=int, default=4)
    parser.add_argument(
        "--train-scope",
        choices=("policy_head", "policy_and_tower", "all"),
        default="policy_head",
    )
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def coord_to_action_xy(xy: list[int], board_size: int) -> int:
    x, y = int(xy[0]), int(xy[1])
    return y * board_size + x


def encode_state(row: dict[str, Any], board_size: int) -> np.ndarray:
    board = np.asarray(row["board"], dtype=np.int8)
    current_player = int(row["current_player"])
    current = (board == current_player).astype(np.float32)
    opponent = (board == -current_player).astype(np.float32)
    last = np.zeros_like(current, dtype=np.float32)
    last_move = row.get("last_move_rc")
    if last_move:
        last[int(last_move[0]), int(last_move[1])] = 1.0
    if current.shape != (board_size, board_size):
        raise ValueError(f"{row['id']}: expected {board_size}x{board_size} board")
    return np.stack([current, opponent, last], axis=0)


def legal_mask(row: dict[str, Any], board_size: int) -> np.ndarray:
    board = np.asarray(row["board"], dtype=np.int8)
    if board.shape != (board_size, board_size):
        raise ValueError(f"{row['id']}: expected {board_size}x{board_size} board")
    return (board.reshape(-1) == 0).astype(np.float32)


def policy_target(row: dict[str, Any], board_size: int) -> np.ndarray:
    target = np.zeros(board_size * board_size, dtype=np.float32)
    for item in row["policy_targets"]:
        action = coord_to_action_xy(item["xy"], board_size)
        target[action] += float(item["weight"])
    total = float(target.sum())
    if total <= 0:
        raise ValueError(f"{row['id']}: empty policy target")
    return target / total


def load_dataset(path: Path, board_size: int) -> tuple[list[dict[str, Any]], torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
    data = json.loads(path.read_text(encoding="utf-8"))
    samples = data["samples"]
    states = np.stack([encode_state(row, board_size) for row in samples])
    masks = np.stack([legal_mask(row, board_size) for row in samples])
    targets = np.stack([policy_target(row, board_size) for row in samples])
    weights = np.asarray([float(row.get("sample_weight", 1.0)) for row in samples], dtype=np.float32)
    return (
        samples,
        torch.tensor(states, dtype=torch.float32),
        torch.tensor(masks, dtype=torch.float32),
        torch.tensor(targets, dtype=torch.float32),
        torch.tensor(weights, dtype=torch.float32),
    )


def load_model(path: Path, args: argparse.Namespace, device: torch.device) -> PolicyValueNet:
    model = PolicyValueNet(args.board_size, channels=args.channels, blocks=args.blocks).to(device)
    loaded = load_compatible_checkpoint(
        model,
        path,
        device,
        board_size=args.board_size,
        channels=args.channels,
        blocks=args.blocks,
    )
    if not loaded:
        raise RuntimeError(f"could not load compatible checkpoint: {path}")
    return model


def configure_trainable(model: PolicyValueNet, train_scope: str) -> list[torch.nn.Parameter]:
    for name, parameter in model.named_parameters():
        if train_scope == "all":
            parameter.requires_grad = True
        elif train_scope == "policy_head":
            parameter.requires_grad = name.startswith("policy")
        elif train_scope == "policy_and_tower":
            parameter.requires_grad = name.startswith(("stem", "tower", "policy"))
        else:
            raise ValueError(train_scope)

    trainable = [(name, parameter) for name, parameter in model.named_parameters() if parameter.requires_grad]
    if not trainable:
        raise ValueError("no trainable parameters selected")
    print(f"train_scope={train_scope}")
    print(f"trainable_parameters={sum(parameter.numel() for _, parameter in trainable)}")
    for name, _ in trainable:
        print(f"  trainable: {name}")
    return [parameter for _, parameter in trainable]


def set_training_mode(model: PolicyValueNet, train_scope: str) -> None:
    model.eval()
    if train_scope == "all":
        model.train()
    elif train_scope == "policy_head":
        model.policy.train()
    elif train_scope == "policy_and_tower":
        model.stem.train()
        model.tower.train()
        model.policy.train()
    else:
        raise ValueError(train_scope)


def masked_log_softmax(logits: torch.Tensor, masks: torch.Tensor) -> torch.Tensor:
    return F.log_softmax(logits.masked_fill(masks <= 0, -1e9), dim=-1)


@torch.no_grad()
def print_identity_diagnostics(
    label: str,
    model: PolicyValueNet,
    samples: list[dict[str, Any]],
    states: torch.Tensor,
    masks: torch.Tensor,
    targets: torch.Tensor,
    device: torch.device,
) -> None:
    model.eval()
    logits, values = model(states.to(device))
    probs = torch.exp(masked_log_softmax(logits, masks.to(device))).cpu()
    print("=" * 100)
    print(label)
    for index, sample in enumerate(samples):
        if sample["transform"] != "identity":
            continue
        legal = torch.nonzero(masks[index] > 0, as_tuple=False).flatten()
        legal_probs = probs[index, legal]
        ranked = legal[torch.argsort(legal_probs, descending=True)].tolist()
        target_actions = torch.nonzero(targets[index] > 0, as_tuple=False).flatten().tolist()
        parts = []
        for action in target_actions:
            rank = ranked.index(int(action)) + 1
            prob = float(probs[index, action].item())
            parts.append(f"action={action} rank={rank} prob={prob:.6f} weight={float(targets[index, action].item()):.2f}")
        top_action = int(ranked[0])
        print(
            f"{sample['id']} value={float(values[index].item()):.6f} "
            f"top={top_action} targets: {'; '.join(parts)}"
        )


def train(args: argparse.Namespace) -> None:
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    samples, states_cpu, masks_cpu, targets_cpu, weights_cpu = load_dataset(args.dataset, args.board_size)
    print(f"device={device}")
    print(f"dataset={args.dataset}")
    print(f"samples={len(samples)}")
    print(f"init_checkpoint={args.init_checkpoint}")

    model = load_model(args.init_checkpoint, args, device)
    reference = load_model(args.init_checkpoint, args, device)
    reference.eval()
    for parameter in reference.parameters():
        parameter.requires_grad = False

    states = states_cpu.to(device)
    masks = masks_cpu.to(device)
    targets = targets_cpu.to(device)
    weights = weights_cpu.to(device)

    print_identity_diagnostics("BEFORE", model, samples, states_cpu, masks_cpu, targets_cpu, device)
    if args.dry_run:
        print("dry-run: no training or checkpoint write")
        return

    optimizer = torch.optim.AdamW(configure_trainable(model, args.train_scope), lr=args.lr, weight_decay=args.weight_decay)
    with torch.no_grad():
        ref_logits, _ = reference(states)
        ref_probs = torch.exp(masked_log_softmax(ref_logits, masks))

    for epoch in range(1, args.epochs + 1):
        set_training_mode(model, args.train_scope)
        logits, _values = model(states)
        log_probs = masked_log_softmax(logits, masks)
        ce_per_row = -(targets * log_probs).sum(dim=-1)
        ce_loss = (ce_per_row * weights).sum() / weights.sum()
        kl_per_row = (ref_probs * (torch.log(ref_probs.clamp_min(1e-12)) - log_probs)).sum(dim=-1)
        kl_loss = (kl_per_row * weights).sum() / weights.sum()
        loss = ce_loss + args.kl_weight * kl_loss

        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()

        if epoch == 1 or epoch == args.epochs or epoch % args.print_every == 0:
            print(
                f"epoch {epoch:03d}/{args.epochs} "
                f"loss={float(loss.item()):.6f} "
                f"policy_ce={float(ce_loss.item()):.6f} "
                f"kl={float(kl_loss.item()):.6f}",
                flush=True,
            )

    print_identity_diagnostics("AFTER", model, samples, states_cpu, masks_cpu, targets_cpu, device)
    args.out_checkpoint.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "model": model.state_dict(),
            "board_size": args.board_size,
            "win_length": args.win_length,
            "channels": args.channels,
            "blocks": args.blocks,
            "candidate_g_teacher_policy": {
                "init_checkpoint": str(args.init_checkpoint),
                "dataset": str(args.dataset),
                "epochs": args.epochs,
                "lr": args.lr,
                "kl_weight": args.kl_weight,
                "train_scope": args.train_scope,
                "value_tuning": "frozen/no value loss in Candidate G policy phase",
            },
        },
        args.out_checkpoint,
    )
    print(f"saved {args.out_checkpoint}")


def main() -> int:
    train(parse_args())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
