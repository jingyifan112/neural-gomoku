from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import torch

from gomoku_agent.board import BLACK, WHITE, Board
from gomoku_agent.checkpoint import load_compatible_checkpoint
from gomoku_agent.model import PolicyValueNet, masked_policy


SIDE_TO_PLAYER = {"black": BLACK, "white": WHITE}
STONE_TO_PLAYER = {"X": BLACK, "O": WHITE, ".": 0}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate a checkpoint's direct policy/value on the labeled Rapfi failure positions."
    )
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--repair-dataset-json", type=Path, default=None)
    parser.add_argument("--positions-json", type=Path, default=Path("analysis/rapfi_failure_board_snapshots.json"))
    parser.add_argument("--threat-csv", type=Path, default=Path("analysis/rapfi_failure_threat_analysis.csv"))
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--board-size", type=int, default=15)
    parser.add_argument("--win-length", type=int, default=5)
    parser.add_argument("--labels-csv", type=Path, default=Path("analysis/rapfi_failure_set_labeled.csv"))
    parser.add_argument("--channels", type=int, default=64)
    parser.add_argument("--blocks", type=int, default=4)
    return parser.parse_args()


def safe_checkpoint_name(path: Path) -> str:
    return path.stem.replace("/", "_")


def output_path(args: argparse.Namespace) -> Path:
    if args.out is not None:
        return args.out
    return Path(f"analysis/rapfi_failure_eval_{safe_checkpoint_name(args.checkpoint)}.csv")


def read_json(path: Path) -> list[dict[str, object]]:
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


def action_to_coord(action: int, board_size: int) -> str:
    row, col = divmod(int(action), board_size)
    return f"{col},{row}"


def moves_to_coords(actions: list[int], board_size: int) -> list[str]:
    return [action_to_coord(action, board_size) for action in actions]


def parse_coord_list(raw: str) -> set[str]:
    return {part.strip() for part in raw.split() if part.strip()}


def blocks_immediate_win(move: str, opponent_winning_moves: set[str]) -> bool:
    return bool(opponent_winning_moves) and move in opponent_winning_moves


def load_model(args: argparse.Namespace, device: torch.device) -> PolicyValueNet:
    model = PolicyValueNet(args.board_size, channels=args.channels, blocks=args.blocks).to(device)
    loaded = load_compatible_checkpoint(
        model,
        args.checkpoint,
        device,
        board_size=args.board_size,
        channels=args.channels,
        blocks=args.blocks,
    )
    if not loaded:
        raise ValueError(f"could not load compatible checkpoint: {args.checkpoint}")
    model.eval()
    return model


@torch.no_grad()
def evaluate_position(model: PolicyValueNet, board: Board, device: torch.device) -> tuple[str, float, float]:
    state = torch.tensor(board.encode()[None, ...], dtype=torch.float32, device=device)
    legal = torch.tensor(board.legal_mask()[None, ...], dtype=torch.float32, device=device)
    logits, value = model(state)
    probs = masked_policy(logits, legal, temperature=1.0)[0]
    action = int(torch.argmax(probs).item())
    return action_to_coord(action, board.size), float(probs[action].item()), float(value[0].item())


def output_fields() -> list[str]:
    return [
        "sample_id",
        "game_number",
        "move_count",
        "side_to_move",
        "opponent",
        "label_type",
        "value_target",
        "policy_target",
        "labeled_failure_type",
        "logged_value",
        "model_value_estimate",
        "direct_policy_top_move",
        "direct_policy_top_prob",
        "direct_blocks_opponent_immediate_win",
        "expected_blocking_moves",
        "opponent_immediate_winning_moves",
        "current_player_immediate_winning_moves",
        "logged_direct",
        "logged_policy_safety",
        "logged_mcts_raw",
        "logged_mcts_safety",
        "logged_final",
        "logged_final_blocks_immediate_win",
        "preliminary_failure_type",
    ]


def build_rows(args: argparse.Namespace, model: PolicyValueNet, device: torch.device) -> list[dict[str, str]]:
    if args.repair_dataset_json is not None:
        return build_rows_from_repair_dataset(args, model, device)

    positions = read_json(args.positions_json)
    threats = read_csv_index(args.threat_csv)
    labels = read_csv_index(args.labels_csv) if args.labels_csv.exists() else {}

    rows: list[dict[str, str]] = []
    for position in positions:
        game_number = str(position["game_number"])
        move_count = str(position["move_count"])
        key = (game_number, move_count)
        side_to_move = str(position["side_to_move"])
        opponent = "white" if side_to_move == "black" else "black"

        board = parse_board(
            str(position["board_snapshot_before_decision"]),
            board_size=args.board_size,
            win_length=args.win_length,
            side_to_move=side_to_move,
        )
        top_move, top_prob, model_value = evaluate_position(model, board, device)

        opponent_immediate = moves_to_coords(
            board.immediate_winning_moves(SIDE_TO_PLAYER[opponent]),
            args.board_size,
        )
        current_immediate = moves_to_coords(
            board.immediate_winning_moves(SIDE_TO_PLAYER[side_to_move]),
            args.board_size,
        )

        threat_row = threats.get(key, {})
        label_row = labels.get(key, {})
        expected_blocks = parse_coord_list(
            threat_row.get("opponent_immediate_winning_moves", " ".join(opponent_immediate))
        )
        if not expected_blocks:
            expected_blocks = set(opponent_immediate)

        rows.append(
            {
                "sample_id": f"legacy_g{game_number}_m{move_count}",
                "game_number": game_number,
                "move_count": move_count,
                "side_to_move": side_to_move,
                "opponent": opponent,
                "label_type": "",
                "value_target": "",
                "policy_target": "",
                "labeled_failure_type": label_row.get("failure_type", position.get("failure_type", "")),
                "logged_value": str(position["value"]),
                "model_value_estimate": f"{model_value:.6f}",
                "direct_policy_top_move": top_move,
                "direct_policy_top_prob": f"{top_prob:.6f}",
                "direct_blocks_opponent_immediate_win": str(blocks_immediate_win(top_move, expected_blocks)),
                "expected_blocking_moves": " ".join(sorted(expected_blocks)),
                "opponent_immediate_winning_moves": " ".join(opponent_immediate),
                "current_player_immediate_winning_moves": " ".join(current_immediate),
                "logged_direct": str(position["direct"]),
                "logged_policy_safety": str(position["policy_safety"]),
                "logged_mcts_raw": str(position["mcts_raw"]),
                "logged_mcts_safety": str(position["mcts_safety"]),
                "logged_final": str(position["final"]),
                "logged_final_blocks_immediate_win": threat_row.get("final_blocks_immediate_win", ""),
                "preliminary_failure_type": threat_row.get("preliminary_failure_type", ""),
            }
        )

    return rows


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


def split_dataset_id(sample_id: str) -> tuple[str, str]:
    if "_g" not in sample_id or "_m" not in sample_id:
        return "", ""
    game_part = sample_id.split("_m", maxsplit=1)[0]
    move_part = sample_id.split("_m", maxsplit=1)[1]
    return game_part.split("_g", maxsplit=1)[1], move_part


def build_rows_from_repair_dataset(
    args: argparse.Namespace,
    model: PolicyValueNet,
    device: torch.device,
) -> list[dict[str, str]]:
    dataset = read_json(args.repair_dataset_json)
    rows: list[dict[str, str]] = []

    for sample in dataset:
        sample_id = str(sample["id"])
        game_number, move_count = split_dataset_id(sample_id)
        side_to_move = str(sample["side_to_move"])
        opponent = "white" if side_to_move == "black" else "black"
        board = parse_dataset_board(
            str(sample["board"]),
            board_size=args.board_size,
            win_length=args.win_length,
            side_to_move=side_to_move,
        )
        top_move, top_prob, model_value = evaluate_position(model, board, device)

        opponent_immediate = moves_to_coords(
            board.immediate_winning_moves(SIDE_TO_PLAYER[opponent]),
            args.board_size,
        )
        current_immediate = moves_to_coords(
            board.immediate_winning_moves(SIDE_TO_PLAYER[side_to_move]),
            args.board_size,
        )
        expected_blocks = set(opponent_immediate)
        policy_target = str(sample.get("policy_target", "") or "")
        if policy_target:
            expected_blocks.add(policy_target)

        rows.append(
            {
                "sample_id": sample_id,
                "game_number": game_number,
                "move_count": str(sample["move_count"]),
                "side_to_move": side_to_move,
                "opponent": opponent,
                "label_type": str(sample["label_type"]),
                "value_target": str(sample.get("value_target", "")),
                "policy_target": policy_target,
                "labeled_failure_type": str(sample["label_type"]),
                "logged_value": "",
                "model_value_estimate": f"{model_value:.6f}",
                "direct_policy_top_move": top_move,
                "direct_policy_top_prob": f"{top_prob:.6f}",
                "direct_blocks_opponent_immediate_win": str(blocks_immediate_win(top_move, expected_blocks)),
                "expected_blocking_moves": " ".join(sorted(expected_blocks)),
                "opponent_immediate_winning_moves": " ".join(opponent_immediate),
                "current_player_immediate_winning_moves": " ".join(current_immediate),
                "logged_direct": "",
                "logged_policy_safety": "",
                "logged_mcts_raw": "",
                "logged_mcts_safety": "",
                "logged_final": "",
                "logged_final_blocks_immediate_win": "",
                "preliminary_failure_type": "",
            }
        )

    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=output_fields())
        writer.writeheader()
        writer.writerows(rows)


def print_gate_summary(rows: list[dict[str, str]]) -> None:
    old_blocks = [row for row in rows if row.get("label_type") == "old_immediate_block_regression"]
    if old_blocks:
        hits = sum(1 for row in old_blocks if row["direct_blocks_opponent_immediate_win"] == "True")
        print(f"old immediate-block direct accuracy: {hits}/{len(old_blocks)}")

    for label_type in (
        "verified_double_threat_loss",
        "early_forcing_value_negative",
        "pre_double_threat_warning",
    ):
        group = [row for row in rows if row.get("label_type") == label_type]
        if not group:
            continue
        values = [float(row["model_value_estimate"]) for row in group]
        avg_value = sum(values) / len(values)
        print(f"{label_type} value avg: {avg_value:.6f} n={len(values)}")


def main() -> int:
    args = parse_args()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = load_model(args, device)
    rows = build_rows(args, model, device)
    out = output_path(args)
    write_csv(out, rows)
    print(f"device={device}")
    print(f"evaluated positions: {len(rows)}")
    print_gate_summary(rows)
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
