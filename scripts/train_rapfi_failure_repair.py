from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch
from torch.nn import functional as F
from torch.utils.data import DataLoader, TensorDataset

from gomoku_agent.board import BLACK, WHITE, Board
from gomoku_agent.checkpoint import load_compatible_checkpoint
from gomoku_agent.model import PolicyValueNet


SIDE_TO_PLAYER = {"black": BLACK, "white": WHITE}
STONE_TO_PLAYER = {"X": BLACK, "O": WHITE, ".": 0}


@dataclass(frozen=True)
class RepairSample:
    sample_id: str
    game_number: str
    move_count: str
    label_type: str
    source: str
    state: np.ndarray
    policy_target: np.ndarray
    policy_mask: float
    policy_target_move: str
    value_target: float
    value_mask: float


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Small targeted supervised repair pass for Rapfi failure positions."
    )
    parser.add_argument("--init-checkpoint", type=Path, default=Path("checkpoints/15x15_v12_candidate.pt"))
    parser.add_argument("--out-checkpoint", type=Path, default=Path("checkpoints/15x15_v12b_candidate.pt"))
    parser.add_argument("--repair-dataset-json", type=Path, default=None)
    parser.add_argument("--positions-json", type=Path, default=Path("analysis/rapfi_failure_board_snapshots.json"))
    parser.add_argument("--threat-csv", type=Path, default=Path("analysis/rapfi_failure_threat_analysis.csv"))
    parser.add_argument("--labels-csv", type=Path, default=Path("analysis/rapfi_failure_set_labeled.csv"))
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--lr", type=float, default=5e-5)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--policy-loss-weight", type=float, default=1.0)
    parser.add_argument("--value-loss-weight", type=float, default=1.0)
    parser.add_argument("--board-size", type=int, default=15)
    parser.add_argument("--win-length", type=int, default=5)
    parser.add_argument("--channels", type=int, default=64)
    parser.add_argument("--blocks", type=int, default=4)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def read_positions(path: Path) -> list[dict[str, object]]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a JSON list")
    return data


def read_csv_index(path: Path) -> dict[tuple[str, str], dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return {(row["game_number"], row["move_count"]): row for row in rows}


def parse_board(snapshot: str, board_size: int, win_length: int, side_to_move: str) -> Board:
    board = Board(size=board_size, win_length=win_length)
    rows: list[list[str]] = []
    for line in snapshot.splitlines():
        tokens = line.strip().split()
        if len(tokens) == board_size and all(token in STONE_TO_PLAYER for token in tokens):
            rows.append(tokens)

    if len(rows) != board_size:
        raise ValueError(f"expected {board_size} board rows, found {len(rows)}")

    for row_index, row in enumerate(rows):
        for col_index, token in enumerate(row):
            board.grid[row_index, col_index] = STONE_TO_PLAYER[token]

    board.current_player = SIDE_TO_PLAYER[side_to_move]
    board.move_count = int((board.grid != 0).sum())
    board.last_move = None
    return board


def parse_dataset_board(board_text: str, board_size: int, win_length: int, side_to_move: str) -> Board:
    board = Board(size=board_size, win_length=win_length)
    rows: list[list[str]] = []
    for line in board_text.splitlines():
        tokens = line.strip().split()
        if len(tokens) == board_size and all(token in STONE_TO_PLAYER for token in tokens):
            rows.append(tokens)

    if len(rows) != board_size:
        raise ValueError(f"expected {board_size} board rows, found {len(rows)}")

    for row_index, row in enumerate(rows):
        for col_index, token in enumerate(row):
            board.grid[row_index, col_index] = STONE_TO_PLAYER[token]

    board.current_player = SIDE_TO_PLAYER[side_to_move]
    board.move_count = int((board.grid != 0).sum())
    board.last_move = None
    return board


def coord_to_action(coord: str, board_size: int) -> int:
    x_text, y_text = coord.split(",", maxsplit=1)
    x = int(x_text)
    y = int(y_text)
    return y * board_size + x


def parse_move_list(raw: str) -> list[str]:
    return [part.strip() for part in raw.split() if part.strip()]


def one_hot_policy(board_size: int, move: str) -> np.ndarray:
    policy = np.zeros(board_size * board_size, dtype=np.float32)
    policy[coord_to_action(move, board_size)] = 1.0
    return policy


def choose_targets(
    position: dict[str, object],
    threat_row: dict[str, str],
    label_row: dict[str, str],
    board_size: int,
) -> tuple[np.ndarray, float, str, float, float]:
    opponent_wins = parse_move_list(threat_row.get("opponent_immediate_winning_moves", ""))
    failure_type = label_row.get("failure_type", str(position.get("failure_type", "")))

    policy_target_move = ""
    policy_mask = 0.0
    if len(opponent_wins) == 1:
        policy_target_move = opponent_wins[0]
        policy_mask = 1.0
    elif len(opponent_wins) > 1:
        policy_target_move = opponent_wins[0]
        policy_mask = 1.0

    if policy_target_move:
        policy_target = one_hot_policy(board_size, policy_target_move)
    else:
        policy_target = np.zeros(board_size * board_size, dtype=np.float32)

    value_target = 0.0
    value_mask = 0.0
    if len(opponent_wins) > 1 or "value_miscalibration" in failure_type:
        value_target = -1.0
        value_mask = 1.0

    return policy_target, policy_mask, policy_target_move, value_target, value_mask


def build_samples(args: argparse.Namespace) -> list[RepairSample]:
    if args.repair_dataset_json is not None:
        return build_samples_from_repair_dataset(args)

    positions = read_positions(args.positions_json)
    threats = read_csv_index(args.threat_csv)
    labels = read_csv_index(args.labels_csv)
    samples: list[RepairSample] = []

    for position in positions:
        key = (str(position["game_number"]), str(position["move_count"]))
        threat_row = threats.get(key)
        label_row = labels.get(key)
        if threat_row is None:
            raise ValueError(f"missing threat row for game {key[0]} move_count {key[1]}")
        if label_row is None:
            raise ValueError(f"missing label row for game {key[0]} move_count {key[1]}")

        board = parse_board(
            str(position["board_snapshot_before_decision"]),
            board_size=args.board_size,
            win_length=args.win_length,
            side_to_move=str(position["side_to_move"]),
        )
        policy_target, policy_mask, policy_target_move, value_target, value_mask = choose_targets(
            position,
            threat_row,
            label_row,
            board_size=args.board_size,
        )
        samples.append(
            RepairSample(
                sample_id=f"legacy_g{key[0]}_m{key[1]}",
                game_number=key[0],
                move_count=key[1],
                label_type=label_row["failure_type"],
                source="legacy_rapfi_failure_set",
                state=board.encode().astype(np.float32),
                policy_target=policy_target,
                policy_mask=policy_mask,
                policy_target_move=policy_target_move,
                value_target=value_target,
                value_mask=value_mask,
            )
        )

    return samples


def build_samples_from_repair_dataset(args: argparse.Namespace) -> list[RepairSample]:
    with args.repair_dataset_json.open("r", encoding="utf-8") as handle:
        dataset = json.load(handle)
    if not isinstance(dataset, list):
        raise ValueError(f"{args.repair_dataset_json} must contain a JSON list")

    samples: list[RepairSample] = []
    for row in dataset:
        if not isinstance(row, dict):
            raise ValueError("repair dataset rows must be JSON objects")

        board_size = int(row.get("board_size", args.board_size))
        if board_size != args.board_size:
            raise ValueError(f"dataset row {row.get('id')} has board_size={board_size}, expected {args.board_size}")

        board = parse_dataset_board(
            str(row["board"]),
            board_size=args.board_size,
            win_length=args.win_length,
            side_to_move=str(row["side_to_move"]),
        )

        policy_target_move = str(row.get("policy_target", "") or "")
        if policy_target_move:
            policy_target = one_hot_policy(args.board_size, policy_target_move)
            policy_mask = 1.0
        else:
            policy_target = np.zeros(args.board_size * args.board_size, dtype=np.float32)
            policy_mask = 0.0

        raw_value = row.get("value_target", "")
        if raw_value == "" or raw_value is None:
            value_target = 0.0
            value_mask = 0.0
        else:
            value_target = float(raw_value)
            value_mask = 1.0

        sample_id = str(row["id"])
        move_count = str(row["move_count"])
        game_number = sample_id.split("_m", maxsplit=1)[0].split("_g")[-1] if "_g" in sample_id else ""

        samples.append(
            RepairSample(
                sample_id=sample_id,
                game_number=game_number,
                move_count=move_count,
                label_type=str(row["label_type"]),
                source=str(row.get("source", "")),
                state=board.encode().astype(np.float32),
                policy_target=policy_target,
                policy_mask=policy_mask,
                policy_target_move=policy_target_move,
                value_target=value_target,
                value_mask=value_mask,
            )
        )

    return samples


def load_model(args: argparse.Namespace, device: torch.device) -> PolicyValueNet:
    model = PolicyValueNet(args.board_size, channels=args.channels, blocks=args.blocks).to(device)
    loaded = load_compatible_checkpoint(
        model,
        args.init_checkpoint,
        device,
        board_size=args.board_size,
        channels=args.channels,
        blocks=args.blocks,
    )
    if not loaded:
        raise ValueError(f"could not load compatible checkpoint: {args.init_checkpoint}")
    return model


def print_dry_run(samples: list[RepairSample]) -> None:
    policy_count = sum(1 for sample in samples if sample.policy_mask > 0)
    value_count = sum(1 for sample in samples if sample.value_mask > 0)
    print(f"positions loaded: {len(samples)}")
    print(f"policy repair targets: {policy_count}")
    print(f"value repair targets: {value_count}")
    for sample in samples:
        policy_target = sample.policy_target_move or "none"
        value_target = f"{sample.value_target:.2f}".rstrip("0").rstrip(".") if sample.value_mask > 0 else "none"
        print(
            "target "
            f"id={sample.sample_id} "
            f"source={sample.source} "
            f"game={sample.game_number} move_count={sample.move_count} "
            f"label_type={sample.label_type} "
            f"policy_target={policy_target} value_target={value_target}"
        )


def train_on_samples(
    model: PolicyValueNet,
    samples: list[RepairSample],
    args: argparse.Namespace,
    device: torch.device,
) -> None:
    states = torch.tensor(np.stack([sample.state for sample in samples]), dtype=torch.float32)
    policies = torch.tensor(np.stack([sample.policy_target for sample in samples]), dtype=torch.float32)
    policy_masks = torch.tensor([sample.policy_mask for sample in samples], dtype=torch.float32)
    values = torch.tensor([sample.value_target for sample in samples], dtype=torch.float32)
    value_masks = torch.tensor([sample.value_mask for sample in samples], dtype=torch.float32)

    loader = DataLoader(
        TensorDataset(states, policies, policy_masks, values, value_masks),
        batch_size=args.batch_size,
        shuffle=True,
    )
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)

    model.train()
    for epoch in range(args.epochs):
        total_loss = 0.0
        total_policy_loss = 0.0
        total_value_loss = 0.0
        total_rows = 0
        for batch_states, batch_policies, batch_policy_masks, batch_values, batch_value_masks in loader:
            batch_states = batch_states.to(device)
            batch_policies = batch_policies.to(device)
            batch_policy_masks = batch_policy_masks.to(device)
            batch_values = batch_values.to(device)
            batch_value_masks = batch_value_masks.to(device)

            logits, predicted_values = model(batch_states)
            per_row_policy = -(batch_policies * F.log_softmax(logits, dim=-1)).sum(dim=-1)
            if batch_policy_masks.sum() > 0:
                policy_loss = (per_row_policy * batch_policy_masks).sum() / batch_policy_masks.sum()
            else:
                policy_loss = torch.zeros((), device=device)

            per_row_value = F.mse_loss(predicted_values, batch_values, reduction="none")
            if batch_value_masks.sum() > 0:
                value_loss = (per_row_value * batch_value_masks).sum() / batch_value_masks.sum()
            else:
                value_loss = torch.zeros((), device=device)

            loss = args.policy_loss_weight * policy_loss + args.value_loss_weight * value_loss
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_loss += float(loss.item()) * len(batch_states)
            total_policy_loss += float(policy_loss.item()) * len(batch_states)
            total_value_loss += float(value_loss.item()) * len(batch_states)
            total_rows += len(batch_states)

        print(
            f"epoch {epoch + 1}/{args.epochs}: "
            f"policy_loss={total_policy_loss / total_rows:.4f} "
            f"value_loss={total_value_loss / total_rows:.4f} "
            f"weighted_loss={total_loss / total_rows:.4f}",
            flush=True,
        )


def save_checkpoint(model: PolicyValueNet, args: argparse.Namespace) -> None:
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


def main() -> int:
    args = parse_args()
    samples = build_samples(args)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"device={device}", flush=True)
    model = load_model(args, device)

    if args.dry_run:
        print_dry_run(samples)
        print("dry-run: checkpoint not saved")
        return 0

    train_on_samples(model, samples, args, device)
    save_checkpoint(model, args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
