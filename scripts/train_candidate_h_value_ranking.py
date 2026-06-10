from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import torch
from torch.nn import functional as F

from gomoku_agent.board import Board
from gomoku_agent.checkpoint import load_compatible_checkpoint
from gomoku_agent.model import PolicyValueNet


PAIR_MOVES_XY = {
    "candidate_g_g2_p15_teacher_7_9_preserve_7_10": {"teacher": (7, 9), "original": (7, 10), "weight": 2.0},
    "candidate_g_g2_p17_teacher_9_9": {"teacher": (9, 9), "original": (9, 5), "weight": 3.0},
    "candidate_g_g2_p19_teacher_continuation_10_11": {"teacher": (10, 11), "original": (9, 9), "weight": 1.0},
    "candidate_g_g2_p21_teacher_continuation_8_10": {"teacher": (8, 10), "original": (9, 9), "weight": 1.0},
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train Candidate H value-ranking phase from Candidate G.")
    parser.add_argument(
        "--dataset",
        type=Path,
        default=Path("analysis/integration_eval/candidate_g_teacher_policy_dataset.json"),
    )
    parser.add_argument(
        "--init-checkpoint",
        type=Path,
        default=Path("checkpoints/15x15_candidate_g_teacher_policy.pt"),
    )
    parser.add_argument(
        "--out-checkpoint",
        type=Path,
        default=Path("checkpoints/15x15_candidate_h_value_ranking.pt"),
    )
    parser.add_argument("--epochs", type=int, default=60)
    parser.add_argument("--lr", type=float, default=1e-5)
    parser.add_argument("--margin", type=float, default=0.20)
    parser.add_argument("--pair-loss-weight", type=float, default=1.0)
    parser.add_argument("--anchor-value-weight", type=float, default=0.25)
    parser.add_argument("--seed", type=int, default=23)
    parser.add_argument("--print-every", type=int, default=10)
    parser.add_argument("--board-size", type=int, default=15)
    parser.add_argument("--win-length", type=int, default=5)
    parser.add_argument("--channels", type=int, default=64)
    parser.add_argument("--blocks", type=int, default=4)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def transform_xy(xy: tuple[int, int], transform: str, size: int) -> tuple[int, int]:
    x, y = xy
    last = size - 1
    if transform == "identity":
        return x, y
    if transform == "rot90":
        return last - y, x
    if transform == "rot180":
        return last - x, last - y
    if transform == "rot270":
        return y, last - x
    if transform == "flip_x":
        return last - x, y
    if transform == "flip_y":
        return x, last - y
    if transform == "diag":
        return y, x
    if transform == "anti_diag":
        return last - y, last - x
    raise ValueError(f"unknown transform: {transform}")


def xy_to_action(xy: tuple[int, int], board_size: int) -> int:
    x, y = xy
    return y * board_size + x


def board_from_row(row: dict[str, Any], board_size: int, win_length: int) -> Board:
    board = Board(size=board_size, win_length=win_length)
    for y in range(board_size):
        for x in range(board_size):
            board.grid[y, x] = int(row["board"][y][x])
    board.current_player = int(row["current_player"])
    board.move_count = int((board.grid != 0).sum())
    last_move = row.get("last_move_rc")
    if last_move:
        board.last_move = (int(last_move[0]), int(last_move[1]))
    return board


def encode_board(board: Board) -> np.ndarray:
    return board.encode().astype(np.float32)


def child_state_after(row: dict[str, Any], move_xy: tuple[int, int], board_size: int, win_length: int) -> np.ndarray:
    board = board_from_row(row, board_size, win_length)
    action = xy_to_action(move_xy, board_size)
    result = board.play_flat(action)
    if result.done:
        raise ValueError(f"{row['id']}: pair move {move_xy} ended the game; expected non-terminal child")
    return encode_board(board)


def root_state(row: dict[str, Any], board_size: int, win_length: int) -> np.ndarray:
    return encode_board(board_from_row(row, board_size, win_length))


def load_dataset(path: Path, board_size: int, win_length: int) -> tuple[list[dict[str, Any]], torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
    data = json.loads(path.read_text(encoding="utf-8"))
    samples = data["samples"]
    teacher_states: list[np.ndarray] = []
    original_states: list[np.ndarray] = []
    pair_weights: list[float] = []
    anchor_states: list[np.ndarray] = []

    for row in samples:
        base_case_id = row["base_case_id"]
        if base_case_id in PAIR_MOVES_XY:
            spec = PAIR_MOVES_XY[base_case_id]
            transform = row["transform"]
            teacher_xy = transform_xy(spec["teacher"], transform, board_size)
            original_xy = transform_xy(spec["original"], transform, board_size)
            teacher_states.append(child_state_after(row, teacher_xy, board_size, win_length))
            original_states.append(child_state_after(row, original_xy, board_size, win_length))
            pair_weights.append(float(spec["weight"]) * float(row.get("sample_weight", 1.0)))

        if row["role"] in {"strong_teacher_divergence", "nearby_teacher_continuation", "tactical_regression_anchor"}:
            anchor_states.append(root_state(row, board_size, win_length))

    if not teacher_states:
        raise ValueError("no value-ranking pairs built")
    return (
        samples,
        torch.tensor(np.stack(teacher_states), dtype=torch.float32),
        torch.tensor(np.stack(original_states), dtype=torch.float32),
        torch.tensor(pair_weights, dtype=torch.float32),
        torch.tensor(np.stack(anchor_states), dtype=torch.float32),
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


def configure_value_head_only(model: PolicyValueNet) -> list[torch.nn.Parameter]:
    for name, parameter in model.named_parameters():
        parameter.requires_grad = name.startswith(("value_conv", "value_fc"))
    trainable = [(name, parameter) for name, parameter in model.named_parameters() if parameter.requires_grad]
    print(f"trainable_parameters={sum(parameter.numel() for _, parameter in trainable)}")
    for name, _ in trainable:
        print(f"  trainable: {name}")
    return [parameter for _, parameter in trainable]


@torch.no_grad()
def value_from_mover_perspective(model: PolicyValueNet, states: torch.Tensor) -> torch.Tensor:
    _, values = model(states)
    return -values


@torch.no_grad()
def print_pair_diagnostics(
    label: str,
    model: PolicyValueNet,
    teacher_states: torch.Tensor,
    original_states: torch.Tensor,
    pair_weights: torch.Tensor,
) -> None:
    model.eval()
    teacher_values = value_from_mover_perspective(model, teacher_states)
    original_values = value_from_mover_perspective(model, original_states)
    gaps = teacher_values - original_values
    print("=" * 100)
    print(label)
    print(f"pairs={len(gaps)} avg_gap={float(gaps.mean().item()):.6f} min_gap={float(gaps.min().item()):.6f}")
    print(f"weighted_avg_gap={float((gaps * pair_weights).sum().item() / pair_weights.sum().item()):.6f}")


def train(args: argparse.Namespace) -> None:
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    samples, teacher_cpu, original_cpu, weights_cpu, anchors_cpu = load_dataset(
        args.dataset,
        args.board_size,
        args.win_length,
    )
    print(f"device={device}")
    print(f"dataset={args.dataset}")
    print(f"samples={len(samples)} pairs={len(teacher_cpu)} anchors={len(anchors_cpu)}")
    print(f"init_checkpoint={args.init_checkpoint}")

    model = load_model(args.init_checkpoint, args, device)
    reference = load_model(args.init_checkpoint, args, device)
    model.eval()
    reference.eval()
    for parameter in reference.parameters():
        parameter.requires_grad = False

    teacher_states = teacher_cpu.to(device)
    original_states = original_cpu.to(device)
    pair_weights = weights_cpu.to(device)
    anchor_states = anchors_cpu.to(device)

    print_pair_diagnostics("BEFORE", model, teacher_states, original_states, pair_weights)
    if args.dry_run:
        print("dry-run: no training or checkpoint write")
        return

    optimizer = torch.optim.AdamW(configure_value_head_only(model), lr=args.lr, weight_decay=1e-5)
    with torch.no_grad():
        _, ref_anchor_values = reference(anchor_states)

    for epoch in range(1, args.epochs + 1):
        model.eval()
        _, teacher_child_values_opponent = model(teacher_states)
        _, original_child_values_opponent = model(original_states)
        teacher_values = -teacher_child_values_opponent
        original_values = -original_child_values_opponent
        gaps = teacher_values - original_values
        pair_losses = F.relu(args.margin - gaps)
        pair_loss = (pair_losses * pair_weights).sum() / pair_weights.sum()

        _, anchor_values = model(anchor_states)
        anchor_value_loss = F.mse_loss(anchor_values, ref_anchor_values)
        loss = args.pair_loss_weight * pair_loss + args.anchor_value_weight * anchor_value_loss

        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()

        if epoch == 1 or epoch == args.epochs or epoch % args.print_every == 0:
            print(
                f"epoch {epoch:03d}/{args.epochs} "
                f"loss={float(loss.item()):.6f} "
                f"pair_loss={float(pair_loss.item()):.6f} "
                f"anchor_value_loss={float(anchor_value_loss.item()):.6f} "
                f"min_gap={float(gaps.min().item()):.6f}",
                flush=True,
            )

    print_pair_diagnostics("AFTER", model, teacher_states, original_states, pair_weights)
    args.out_checkpoint.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "model": model.state_dict(),
            "board_size": args.board_size,
            "win_length": args.win_length,
            "channels": args.channels,
            "blocks": args.blocks,
            "candidate_h_value_ranking": {
                "init_checkpoint": str(args.init_checkpoint),
                "dataset": str(args.dataset),
                "epochs": args.epochs,
                "lr": args.lr,
                "margin": args.margin,
                "pair_loss_weight": args.pair_loss_weight,
                "anchor_value_weight": args.anchor_value_weight,
                "train_scope": "value_head_only",
                "policy_preservation": "policy/tower parameters frozen",
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
