#!/usr/bin/env python3
import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path
from types import SimpleNamespace

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import numpy as np
import torch

from gomoku_agent.board import Board
from scripts.evaluate_candidate_g_policy import load_model, policy_probs, safety_action


def action_to_xy(action: int, board_size: int) -> tuple[int, int]:
    return int(action) % board_size, int(action) // board_size


def xy_to_action(x: int, y: int, board_size: int) -> int:
    return int(y) * board_size + int(x)


def fmt_action(action: int | None, board_size: int) -> str:
    if action is None:
        return ""
    x, y = action_to_xy(action, board_size)
    return f"{x},{y}"


def make_board(board_size: int) -> Board:
    return Board(size=board_size, win_length=5)


def play_action(board: Board, action: int) -> None:
    board.play_flat(int(action))


def replay_case(case: dict) -> Board:
    board_size = int(case["board_size"])
    board = make_board(board_size)

    for move in case["moves_before_blunder"]:
        action = xy_to_action(move["x"], move["y"], board_size)
        play_action(board, action)

    return board


def legal_actions(board: Board) -> list[int]:
    return [int(a) for a in board.legal_moves()]


def immediate_winning_actions(board: Board, player: int) -> list[int]:
    return [int(a) for a in board.immediate_winning_moves(player)]


def rank_of_action(probs: np.ndarray, legal: list[int], action: int) -> int:
    ordered = sorted(legal, key=lambda a: float(probs[a]), reverse=True)
    try:
        return ordered.index(action) + 1
    except ValueError:
        return -1


def load_cases(path: Path) -> list[dict]:
    return json.loads(path.read_text())


def evaluate_case(case: dict, model, device: torch.device) -> dict[str, str]:
    board_size = int(case["board_size"])
    board = replay_case(case)

    target = xy_to_action(
        case["target_block_move"]["x"],
        case["target_block_move"]["y"],
        board_size,
    )
    actual_blunder = xy_to_action(
        case["actual_neural_move"]["x"],
        case["actual_neural_move"]["y"],
        board_size,
    )

    legal = legal_actions(board)
    if target not in legal:
        raise ValueError(f"{case['case_id']}: target block is not legal")
    if actual_blunder not in legal:
        raise ValueError(f"{case['case_id']}: actual neural blunder is not legal")

    probs, value = policy_probs(model, board, device)
    probs = np.asarray(probs)

    direct = max(legal, key=lambda a: float(probs[a]))

    try:
        safe = int(safety_action(model, board, device))
    except Exception as e:
        safe = None
        safe_error = repr(e)
    else:
        safe_error = ""

    current_player = int(board.current_player)
    opponent = -current_player

    own_wins = immediate_winning_actions(board, current_player)
    opponent_wins = immediate_winning_actions(board, opponent)

    direct_blocks = direct in opponent_wins
    safe_blocks = safe in opponent_wins if safe is not None else False

    return {
        "case_id": case["case_id"],
        "game": str(case["game"]),
        "neural_color": case["neural_color"],
        "category": case["category"],
        "line_direction": case["line_direction"],
        "phase": case["phase"],
        "position_ply_before_blunder": str(case["position_ply_before_blunder"]),
        "current_player": str(current_player),
        "target_block_move": fmt_action(target, board_size),
        "actual_neural_move": fmt_action(actual_blunder, board_size),
        "direct_move": fmt_action(direct, board_size),
        "policy_safety_move": fmt_action(safe, board_size),
        "direct_target": str(direct == target),
        "policy_safety_target": str(safe == target),
        "direct_blocks_immediate_win": str(direct_blocks),
        "policy_safety_blocks_immediate_win": str(safe_blocks),
        "target_policy_rank": str(rank_of_action(probs, legal, target)),
        "target_policy_prob": f"{float(probs[target]):.8f}",
        "actual_blunder_policy_rank": str(rank_of_action(probs, legal, actual_blunder)),
        "actual_blunder_policy_prob": f"{float(probs[actual_blunder]):.8f}",
        "direct_policy_prob": f"{float(probs[direct]):.8f}",
        "policy_value": f"{float(value):.8f}",
        "own_immediate_winning_moves": " ".join(fmt_action(a, board_size) for a in own_wins),
        "opponent_immediate_winning_moves": " ".join(fmt_action(a, board_size) for a in opponent_wins),
        "safe_error": safe_error,
    }


def write_md(path: Path, rows: list[dict[str, str]], checkpoint: Path, cases_path: Path) -> None:
    n = len(rows)

    def count_true(field: str) -> int:
        return sum(r[field] == "True" for r in rows)

    direct_target = count_true("direct_target")
    safe_target = count_true("policy_safety_target")
    direct_blocks = count_true("direct_blocks_immediate_win")
    safe_blocks = count_true("policy_safety_blocks_immediate_win")

    category_counts = Counter(r["category"] for r in rows)
    miss_rows = [r for r in rows if r["policy_safety_blocks_immediate_win"] != "True"]

    lines = []
    lines.append("# Tactical-mid Must-block Evaluation")
    lines.append("")
    lines.append(f"- checkpoint: `{checkpoint}`")
    lines.append(f"- cases: `{cases_path}`")
    lines.append(f"- total cases: `{n}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Metric | Count | Rate |")
    lines.append("|---|---:|---:|")
    lines.append(f"| direct selects exact target | {direct_target}/{n} | {direct_target/n:.3f} |")
    lines.append(f"| policy_safety selects exact target | {safe_target}/{n} | {safe_target/n:.3f} |")
    lines.append(f"| direct blocks immediate win | {direct_blocks}/{n} | {direct_blocks/n:.3f} |")
    lines.append(f"| policy_safety blocks immediate win | {safe_blocks}/{n} | {safe_blocks/n:.3f} |")
    lines.append("")
    lines.append("## Category counts")
    lines.append("")
    lines.append("| Category | Count |")
    lines.append("|---|---:|")
    for k, v in category_counts.most_common():
        lines.append(f"| `{k}` | {v} |")

    lines.append("")
    lines.append("## Case details")
    lines.append("")
    lines.append("| Case | Category | Target | Direct | Safety | Target rank | Blunder rank | Direct blocks | Safety blocks |")
    lines.append("|---|---|---|---|---|---:|---:|---|---|")
    for r in rows:
        lines.append(
            f"| `{r['case_id']}` | `{r['category']}` | `{r['target_block_move']}` | "
            f"`{r['direct_move']}` | `{r['policy_safety_move']}` | "
            f"{r['target_policy_rank']} | {r['actual_blunder_policy_rank']} | "
            f"{r['direct_blocks_immediate_win']} | {r['policy_safety_blocks_immediate_win']} |"
        )

    if miss_rows:
        lines.append("")
        lines.append("## Policy-safety misses")
        lines.append("")
        lines.append("| Case | Category | Target | Safety | Opponent immediate wins |")
        lines.append("|---|---|---|---|---|")
        for r in miss_rows:
            lines.append(
                f"| `{r['case_id']}` | `{r['category']}` | `{r['target_block_move']}` | "
                f"`{r['policy_safety_move']}` | `{r['opponent_immediate_winning_moves']}` |"
            )

    path.write_text("\n".join(lines) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", type=Path, required=True)
    ap.add_argument("--cases", type=Path, required=True)
    ap.add_argument("--out-csv", type=Path, required=True)
    ap.add_argument("--out-md", type=Path, required=True)
    ap.add_argument("--board-size", type=int, default=15)
    ap.add_argument("--channels", type=int, default=64)
    ap.add_argument("--blocks", type=int, default=4)
    ap.add_argument("--device", default="cpu")
    args = ap.parse_args()

    device = torch.device(args.device)
    model_args = SimpleNamespace(
        board_size=args.board_size,
        channels=args.channels,
        blocks=args.blocks,
    )

    model = load_model(args.checkpoint, model_args, device)
    model.eval()

    cases = load_cases(args.cases)
    rows = [evaluate_case(case, model, device) for case in cases]

    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.out_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    write_md(args.out_md, rows, args.checkpoint, args.cases)

    n = len(rows)
    print(f"wrote {args.out_csv}")
    print(f"wrote {args.out_md}")
    print(f"cases={n}")
    print(
        "direct_target="
        f"{sum(r['direct_target'] == 'True' for r in rows)}/{n}"
    )
    print(
        "policy_safety_target="
        f"{sum(r['policy_safety_target'] == 'True' for r in rows)}/{n}"
    )
    print(
        "direct_blocks="
        f"{sum(r['direct_blocks_immediate_win'] == 'True' for r in rows)}/{n}"
    )
    print(
        "policy_safety_blocks="
        f"{sum(r['policy_safety_blocks_immediate_win'] == 'True' for r in rows)}/{n}"
    )


if __name__ == "__main__":
    main()
