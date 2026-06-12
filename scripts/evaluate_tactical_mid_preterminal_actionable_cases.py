#!/usr/bin/env python3
import argparse
import csv
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import torch


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
for path in (REPO_ROOT, SRC_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from gomoku_agent.board import Board
from scripts.evaluate_candidate_g_policy import load_model, policy_probs, safety_action


DIRECTIONS = [(1, 0), (0, 1), (1, 1), (1, -1)]


def other_color(color: str) -> str:
    if color == "B":
        return "W"
    if color == "W":
        return "B"
    raise ValueError(f"bad color: {color}")


def xy_to_action(x: int, y: int, board_size: int) -> int:
    return y * board_size + x


def action_to_xy(action: int, board_size: int) -> tuple[int, int]:
    return int(action) % board_size, int(action) // board_size


def fmt_action(action: int | None, board_size: int) -> str:
    if action is None:
        return ""
    x, y = action_to_xy(action, board_size)
    return f"{x},{y}"


def xy_to_str(x: int, y: int) -> str:
    return f"{x},{y}"


def move_to_str(move: dict) -> str:
    return xy_to_str(int(move["x"]), int(move["y"]))


def make_board(board_size: int) -> Board:
    return Board(size=board_size, win_length=5)


def replay_board(case: dict) -> Board:
    board_size = int(case["board_size"])
    board = make_board(board_size)
    for move in case["moves_before_decision"]:
        board.play_flat(xy_to_action(int(move["x"]), int(move["y"]), board_size))
    return board


def board_dict_after(moves: list[dict]) -> dict[tuple[int, int], str]:
    board = {}
    for m in moves:
        x = int(m["x"])
        y = int(m["y"])
        key = (x, y)
        if key in board:
            raise ValueError(f"duplicate move at {key}")
        board[key] = m["color"]
    return board


def legal_xy(board: dict[tuple[int, int], str], board_size: int) -> list[tuple[int, int]]:
    return [
        (x, y)
        for y in range(board_size)
        for x in range(board_size)
        if (x, y) not in board
    ]


def play_xy(
    board: dict[tuple[int, int], str],
    x: int,
    y: int,
    color: str,
) -> dict[tuple[int, int], str]:
    if (x, y) in board:
        raise ValueError(f"occupied move: {(x, y)}")
    out = dict(board)
    out[(x, y)] = color
    return out


def move_wins(
    board: dict[tuple[int, int], str],
    board_size: int,
    x: int,
    y: int,
    color: str,
) -> bool:
    if (x, y) in board:
        return False

    for dx, dy in DIRECTIONS:
        count = 1
        for sign in (1, -1):
            nx = x + sign * dx
            ny = y + sign * dy
            while 0 <= nx < board_size and 0 <= ny < board_size and board.get((nx, ny)) == color:
                count += 1
                nx += sign * dx
                ny += sign * dy
        if count >= 5:
            return True

    return False


def immediate_winning_moves(
    board: dict[tuple[int, int], str],
    board_size: int,
    color: str,
) -> list[str]:
    wins = []
    for x, y in legal_xy(board, board_size):
        if move_wins(board, board_size, x, y, color):
            wins.append(xy_to_str(x, y))
    return wins


def opponent_double_threat_replies_after_move(
    case: dict,
    move_s: str,
) -> list[dict[str, object]]:
    board_size = int(case["board_size"])
    neural_color = case["neural_color"]
    opponent_color = other_color(neural_color)

    x, y = [int(v) for v in move_s.split(",")]
    board = board_dict_after(case["moves_before_decision"])
    after_neural = play_xy(board, x, y, neural_color)

    replies = []
    for rx, ry in legal_xy(after_neural, board_size):
        after_reply = play_xy(after_neural, rx, ry, opponent_color)
        wins = immediate_winning_moves(after_reply, board_size, opponent_color)
        if len(wins) >= 2:
            replies.append({
                "move": xy_to_str(rx, ry),
                "immediate_win_count_after": len(wins),
                "immediate_wins_after": wins,
            })

    replies.sort(key=lambda r: (-int(r["immediate_win_count_after"]), str(r["move"])))
    return replies


def rank_of_action(probs: np.ndarray, legal: list[int], action: int) -> int:
    ordered = sorted(legal, key=lambda a: float(probs[a]), reverse=True)
    try:
        return ordered.index(action) + 1
    except ValueError:
        return -1


def evaluate_case(case: dict, model, device: torch.device, sample_limit: int) -> dict[str, str]:
    board_size = int(case["board_size"])
    board = replay_board(case)

    legal = [int(a) for a in board.legal_moves()]
    probs, value = policy_probs(model, board, device)
    probs = np.asarray(probs)

    direct = max(legal, key=lambda a: float(probs[a]))
    try:
        safe = int(safety_action(model, board, device))
        safe_error = ""
    except Exception as e:
        safe = None
        safe_error = repr(e)

    target_actions = [
        xy_to_action(int(m["x"]), int(m["y"]), board_size)
        for m in case["target_prevention_moves"]
    ]
    observed_action = xy_to_action(
        int(case["observed_neural_move"]["x"]),
        int(case["observed_neural_move"]["y"]),
        board_size,
    )

    direct_s = fmt_action(direct, board_size)
    safe_s = fmt_action(safe, board_size)
    observed_s = fmt_action(observed_action, board_size)
    target_s = " ".join(fmt_action(a, board_size) for a in target_actions)

    direct_replies = opponent_double_threat_replies_after_move(case, direct_s)
    observed_replies = opponent_double_threat_replies_after_move(case, observed_s)
    if safe_s:
        safe_replies = opponent_double_threat_replies_after_move(case, safe_s)
    else:
        safe_replies = []

    first_target = target_actions[0]

    return {
        "case_id": case["case_id"],
        "source_case_id": case["source_case_id"],
        "game": str(case["game"]),
        "category": case["category"],
        "back_ply": str(case["back_ply"]),
        "prefix_ply": str(case["prefix_ply"]),
        "neural_color": case["neural_color"],
        "target_prevention_moves": target_s,
        "observed_neural_move": observed_s,
        "direct_move": direct_s,
        "policy_safety_move": safe_s,
        "direct_in_target_prevention": str(direct in target_actions),
        "policy_safety_in_target_prevention": str(safe in target_actions if safe is not None else False),
        "direct_same_as_observed": str(direct == observed_action),
        "policy_safety_same_as_observed": str(safe == observed_action if safe is not None else False),
        "target_policy_rank": str(rank_of_action(probs, legal, first_target)),
        "target_policy_prob": f"{float(probs[first_target]):.8f}",
        "observed_policy_rank": str(rank_of_action(probs, legal, observed_action)),
        "observed_policy_prob": f"{float(probs[observed_action]):.8f}",
        "direct_policy_prob": f"{float(probs[direct]):.8f}",
        "policy_value": f"{float(value):.8f}",
        "observed_opponent_double_threat_reply_count": str(len(observed_replies)),
        "direct_opponent_double_threat_reply_count": str(len(direct_replies)),
        "policy_safety_opponent_double_threat_reply_count": str(len(safe_replies)),
        "observed_opponent_double_threat_replies_sample": json.dumps(observed_replies[:sample_limit]),
        "direct_opponent_double_threat_replies_sample": json.dumps(direct_replies[:sample_limit]),
        "policy_safety_opponent_double_threat_replies_sample": json.dumps(safe_replies[:sample_limit]),
        "safe_error": safe_error,
    }


def write_md(path: Path, rows: list[dict[str, str]], args: argparse.Namespace) -> None:
    n = len(rows)
    direct_target = sum(r["direct_in_target_prevention"] == "True" for r in rows)
    safe_target = sum(r["policy_safety_in_target_prevention"] == "True" for r in rows)
    direct_safe = sum(int(r["direct_opponent_double_threat_reply_count"]) == 0 for r in rows)
    safe_safe = sum(int(r["policy_safety_opponent_double_threat_reply_count"]) == 0 for r in rows)

    lines = []
    lines.append("# Tactical-mid Preterminal Actionable Evaluation")
    lines.append("")
    lines.append(f"- checkpoint: `{args.checkpoint}`")
    lines.append(f"- cases: `{args.cases}`")
    lines.append(f"- total cases: `{n}`")
    lines.append("- interpretation: these are the small actionable subset where a neural prevention move exists.")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Metric | Count | Rate |")
    lines.append("|---|---:|---:|")
    lines.append(f"| direct selects target prevention | {direct_target}/{n} | {direct_target/n:.3f} |")
    lines.append(f"| policy_safety selects target prevention | {safe_target}/{n} | {safe_target/n:.3f} |")
    lines.append(f"| direct leaves zero opponent double-threat replies | {direct_safe}/{n} | {direct_safe/n:.3f} |")
    lines.append(f"| policy_safety leaves zero opponent double-threat replies | {safe_safe}/{n} | {safe_safe/n:.3f} |")
    lines.append("")
    lines.append("## Case details")
    lines.append("")
    lines.append("| Case | Target | Observed | Direct | Safety | Target rank | Observed rank | Direct target | Safety target | Direct reply count | Safety reply count |")
    lines.append("|---|---|---|---|---|---:|---:|---|---|---:|---:|")
    for r in rows:
        lines.append(
            f"| `{r['case_id']}` | `{r['target_prevention_moves']}` | `{r['observed_neural_move']}` | "
            f"`{r['direct_move']}` | `{r['policy_safety_move']}` | "
            f"{r['target_policy_rank']} | {r['observed_policy_rank']} | "
            f"{r['direct_in_target_prevention']} | {r['policy_safety_in_target_prevention']} | "
            f"{r['direct_opponent_double_threat_reply_count']} | {r['policy_safety_opponent_double_threat_reply_count']} |"
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
    ap.add_argument("--sample-limit", type=int, default=12)
    args = ap.parse_args()

    device = torch.device(args.device)
    model_args = SimpleNamespace(
        board_size=args.board_size,
        channels=args.channels,
        blocks=args.blocks,
    )
    model = load_model(args.checkpoint, model_args, device)
    model.eval()

    cases = json.loads(args.cases.read_text())
    rows = [evaluate_case(case, model, device, args.sample_limit) for case in cases]

    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.out_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    write_md(args.out_md, rows, args)

    n = len(rows)
    print(f"wrote {args.out_csv}")
    print(f"wrote {args.out_md}")
    print(f"cases={n}")
    print(f"direct_target={sum(r['direct_in_target_prevention'] == 'True' for r in rows)}/{n}")
    print(f"policy_safety_target={sum(r['policy_safety_in_target_prevention'] == 'True' for r in rows)}/{n}")
    print(f"direct_zero_double_threat_replies={sum(int(r['direct_opponent_double_threat_reply_count']) == 0 for r in rows)}/{n}")
    print(f"policy_safety_zero_double_threat_replies={sum(int(r['policy_safety_opponent_double_threat_reply_count']) == 0 for r in rows)}/{n}")


if __name__ == "__main__":
    main()
