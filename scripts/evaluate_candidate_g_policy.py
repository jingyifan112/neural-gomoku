from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import torch

from gomoku_agent.board import BLACK, WHITE, Board
from gomoku_agent.checkpoint import load_compatible_checkpoint
from gomoku_agent.mcts import MCTSConfig, run_mcts
from gomoku_agent.model import PolicyValueNet, masked_policy
from gomoku_agent.search_safety import filter_immediate_losses, forced_terminal_policy


@dataclass(frozen=True)
class TacticalCase:
    name: str
    current_player: int
    last_move: tuple[int, int]
    black: tuple[tuple[int, int], ...]
    white: tuple[tuple[int, int], ...]
    expected: tuple[tuple[int, int], ...]


TACTICAL_CASES: tuple[TacticalCase, ...] = (
    TacticalCase(
        "opponent_four_one_endpoint",
        BLACK,
        (4, 4),
        black=((4, 0),),
        white=((4, 1), (4, 2), (4, 3), (4, 4)),
        expected=((4, 5),),
    ),
    TacticalCase(
        "opponent_open_three",
        BLACK,
        (4, 4),
        black=((2, 2), (6, 6)),
        white=((4, 2), (4, 3), (4, 4)),
        expected=((4, 1), (4, 5)),
    ),
    TacticalCase(
        "model_four_can_win",
        BLACK,
        (3, 3),
        black=((3, 0), (3, 1), (3, 2), (3, 3)),
        white=((0, 0), (1, 1)),
        expected=((3, 4),),
    ),
    TacticalCase(
        "broken_four_pattern",
        BLACK,
        (5, 4),
        black=((5, 1), (5, 2), (5, 4), (5, 5)),
        white=((0, 8), (1, 8)),
        expected=((5, 3),),
    ),
    TacticalCase(
        "mcts_safety_must_block_four",
        BLACK,
        (2, 5),
        black=((2, 1), (7, 7)),
        white=((2, 2), (2, 3), (2, 4), (2, 5)),
        expected=((2, 6),),
    ),
    TacticalCase(
        "human_play_vertical_four_must_block",
        WHITE,
        (6, 3),
        black=((3, 3), (4, 2), (4, 3), (4, 4), (5, 3), (6, 3)),
        white=((2, 3), (2, 6), (5, 4), (6, 6), (7, 0), (8, 6)),
        expected=((7, 3),),
    ),
    TacticalCase(
        "human_play_prevent_open_four_fork",
        WHITE,
        (7, 4),
        black=((2, 3), (3, 2), (3, 3), (3, 4), (4, 2), (4, 3), (4, 4), (5, 1), (5, 3), (5, 5), (5, 6), (6, 0), (6, 5), (7, 4)),
        white=((1, 3), (1, 5), (2, 4), (2, 6), (3, 1), (4, 1), (5, 2), (5, 4), (6, 2), (6, 3), (6, 6), (7, 0), (8, 5)),
        expected=((4, 7),),
    ),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate Candidate G policy gates.")
    parser.add_argument(
        "--dataset",
        type=Path,
        default=Path("analysis/integration_eval/candidate_g_teacher_policy_dataset.json"),
    )
    parser.add_argument("--before-checkpoint", type=Path, required=True)
    parser.add_argument("--after-checkpoint", type=Path, required=True)
    parser.add_argument(
        "--output-csv",
        type=Path,
        default=Path("analysis/integration_eval/candidate_g_teacher_rank_comparison.csv"),
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=Path("analysis/integration_eval/candidate_g_teacher_policy_report.md"),
    )
    parser.add_argument("--board-size", type=int, default=15)
    parser.add_argument("--win-length", type=int, default=5)
    parser.add_argument("--channels", type=int, default=64)
    parser.add_argument("--blocks", type=int, default=4)
    parser.add_argument("--mcts-sims", type=int, default=32)
    return parser.parse_args()


def action_to_xy(action: int, board_size: int) -> str:
    row, col = divmod(int(action), board_size)
    return f"{col},{row}"


def xy_to_action(xy: list[int] | tuple[int, int], board_size: int) -> int:
    x, y = int(xy[0]), int(xy[1])
    return y * board_size + x


def rc_to_action(rc: tuple[int, int], board_size: int) -> int:
    row, col = rc
    return row * board_size + col


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
    model.eval()
    return model


def board_from_dataset_row(row: dict[str, Any], board_size: int, win_length: int) -> Board:
    board = Board(size=board_size, win_length=win_length)
    grid = row["board"]
    for y in range(board_size):
        for x in range(board_size):
            board.grid[y, x] = int(grid[y][x])
    board.current_player = int(row["current_player"])
    board.move_count = int((board.grid != 0).sum())
    last_move = row.get("last_move_rc")
    if last_move:
        board.last_move = (int(last_move[0]), int(last_move[1]))
    return board


def board_from_tactical_case(case: TacticalCase, board_size: int, win_length: int) -> Board:
    board = Board(size=board_size, win_length=win_length)
    for row, col in case.black:
        board.grid[row, col] = BLACK
    for row, col in case.white:
        board.grid[row, col] = WHITE
    board.current_player = case.current_player
    board.last_move = case.last_move
    board.move_count = len(case.black) + len(case.white)
    return board


@torch.no_grad()
def policy_probs(model: PolicyValueNet, board: Board, device: torch.device) -> tuple[np.ndarray, float]:
    state = torch.tensor(board.encode()[None, ...], dtype=torch.float32, device=device)
    legal = torch.tensor(board.legal_mask()[None, ...], dtype=torch.float32, device=device)
    logits, value = model(state)
    probs = masked_policy(logits, legal, temperature=1.0)[0].cpu().numpy()
    return probs, float(value[0].item())


def rank_of_action(probs: np.ndarray, board: Board, action: int) -> int:
    legal = [int(move) for move in board.legal_moves()]
    ranked = sorted(legal, key=lambda move: float(probs[move]), reverse=True)
    return ranked.index(int(action)) + 1


def rank_rows_for_model(
    label: str,
    model: PolicyValueNet,
    identity_samples: list[dict[str, Any]],
    args: argparse.Namespace,
    device: torch.device,
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for sample in identity_samples:
        board = board_from_dataset_row(sample, args.board_size, args.win_length)
        probs, value = policy_probs(model, board, device)
        top_action = int(np.argmax(probs))
        for index, target in enumerate(sample["policy_targets"]):
            action = xy_to_action(target["xy"], args.board_size)
            rows.append(
                {
                    "model": label,
                    "case_id": sample["base_case_id"],
                    "role": sample["role"],
                    "game_id": str(sample["game_id"]),
                    "ply": str(sample["ply"]),
                    "target_index": str(index),
                    "target_xy": f"{target['xy'][0]},{target['xy'][1]}",
                    "target_weight": f"{float(target['weight']):.2f}",
                    "target_rank": str(rank_of_action(probs, board, action)),
                    "target_prob": f"{float(probs[action]):.6f}",
                    "top_move": action_to_xy(top_action, args.board_size),
                    "top_prob": f"{float(probs[top_action]):.6f}",
                    "value": f"{value:.6f}",
                }
            )
    return rows


def safety_action(model: PolicyValueNet, board: Board, device: torch.device) -> int:
    forced = forced_terminal_policy(board, temperature=0.0)
    if forced is not None:
        return int(forced[0])
    probs, _ = policy_probs(model, board, device)
    filtered = filter_immediate_losses(board, probs)
    return int(np.argmax(filtered))


def tactical_rows_for_model(
    label: str,
    model: PolicyValueNet,
    args: argparse.Namespace,
    device: torch.device,
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for case in TACTICAL_CASES:
        board = board_from_tactical_case(case, args.board_size, args.win_length)
        expected = {rc_to_action(rc, args.board_size) for rc in case.expected}
        probs, _ = policy_probs(model, board, device)
        direct = int(np.argmax(probs))
        safe = safety_action(model, board, device)
        np.random.seed(2026)
        torch.manual_seed(2026)
        mcts_safe, _ = run_mcts(
            model,
            board,
            device,
            MCTSConfig(simulations=args.mcts_sims, c_puct=1.5, temperature=0.0, avoid_immediate_loss=True),
            add_noise=False,
        )
        rows.append(
            {
                "model": label,
                "case": case.name,
                "direct": action_to_xy(direct, args.board_size),
                "direct_pass": str(direct in expected),
                "safety": action_to_xy(safe, args.board_size),
                "safety_pass": str(safe in expected),
                "mcts_safety": action_to_xy(int(mcts_safe), args.board_size),
                "mcts_safety_pass": str(int(mcts_safe) in expected),
                "expected": " ".join(action_to_xy(action, args.board_size) for action in sorted(expected)),
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def pass_count(rows: list[dict[str, str]], key: str) -> int:
    return sum(1 for row in rows if row[key] == "True")


def find_rank(rows: list[dict[str, str]], model: str, ply: str, target_xy: str) -> int:
    matches = [row for row in rows if row["model"] == model and row["ply"] == ply and row["target_xy"] == target_xy]
    if len(matches) != 1:
        raise ValueError(f"expected one rank row for {model} ply={ply} target={target_xy}, found {len(matches)}")
    return int(matches[0]["target_rank"])


def write_report(
    path: Path,
    args: argparse.Namespace,
    rank_rows: list[dict[str, str]],
    tactical_before: list[dict[str, str]],
    tactical_after: list[dict[str, str]],
) -> None:
    before_p15 = find_rank(rank_rows, "before", "15", "7,9")
    after_p15 = find_rank(rank_rows, "after", "15", "7,9")
    before_p17 = find_rank(rank_rows, "before", "17", "9,9")
    after_p17 = find_rank(rank_rows, "after", "17", "9,9")
    repaired_after = find_rank(rank_rows, "after", "15", "7,10")

    before_direct = pass_count(tactical_before, "direct_pass")
    before_safety = pass_count(tactical_before, "safety_pass")
    before_mcts = pass_count(tactical_before, "mcts_safety_pass")
    after_direct = pass_count(tactical_after, "direct_pass")
    after_safety = pass_count(tactical_after, "safety_pass")
    after_mcts = pass_count(tactical_after, "mcts_safety_pass")

    gates = {
        "ply15_teacher_top3": after_p15 <= 3,
        "ply17_teacher_top10": after_p17 <= 10,
        "candidate_d_repair_visible": repaired_after <= 3,
        "tactical_direct_not_regressed": after_direct >= before_direct,
        "tactical_safety_not_regressed": after_safety >= before_safety,
        "tactical_mcts_safety_not_regressed": after_mcts >= before_mcts,
    }
    policy_gates_pass = all(gates.values())

    lines = [
        "# Candidate G teacher policy-distillation report",
        "",
        "## Setup",
        "",
        f"- dataset: `{args.dataset}`",
        f"- before checkpoint: `{args.before_checkpoint}`",
        f"- after checkpoint: `{args.after_checkpoint}`",
        "- training phase: policy-focused; no C export and no Rapfi smoke.",
        "",
        "## Teacher Rank Comparison",
        "",
        "| ply | target | before rank | after rank | gate |",
        "| ---: | --- | ---: | ---: | --- |",
        f"| 15 | 7,9 | {before_p15} | {after_p15} | {'PASS' if gates['ply15_teacher_top3'] else 'FAIL'} top-3 |",
        f"| 17 | 9,9 | {before_p17} | {after_p17} | {'PASS' if gates['ply17_teacher_top10'] else 'FAIL'} top-10 |",
        f"| 15 | 7,10 Candidate D repair anchor | NA | {repaired_after} | {'PASS' if gates['candidate_d_repair_visible'] else 'FAIL'} top-3 |",
        "",
        "## Tactical Gate",
        "",
        "| metric | before | after | gate |",
        "| --- | ---: | ---: | --- |",
        f"| direct policy | {before_direct}/7 | {after_direct}/7 | {'PASS' if gates['tactical_direct_not_regressed'] else 'FAIL'} |",
        f"| policy plus safety | {before_safety}/7 | {after_safety}/7 | {'PASS' if gates['tactical_safety_not_regressed'] else 'FAIL'} |",
        f"| MCTS plus safety | {before_mcts}/7 | {after_mcts}/7 | {'PASS' if gates['tactical_mcts_safety_not_regressed'] else 'FAIL'} |",
        "",
        "## Gate Decision",
        "",
    ]
    if policy_gates_pass:
        lines.append("Candidate G passes the policy-rank and no-regression gates. Proceed to value tuning next; do not export to C until the value-tuned candidate also passes these gates.")
    else:
        lines.append("Candidate G does not pass all policy-rank gates. Do not proceed to value tuning, C export, or Rapfi smoke yet.")

    lines.extend(
        [
            "",
            "## Recommendation",
            "",
        ]
    )
    if gates["ply15_teacher_top3"] and not gates["ply17_teacher_top10"]:
        lines.append("Increase ply17 teacher emphasis or unfreeze `policy_and_tower` for a short second pass, then rerun this evaluator.")
    elif policy_gates_pass:
        lines.append("Use this checkpoint as the policy-visible base for a small value-ranking/counterfactual phase focused on the same two divergences.")
    else:
        lines.append("Keep the current checkpoint as an experiment artifact only and tune the policy distillation recipe before any downstream evaluation.")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    data = json.loads(args.dataset.read_text(encoding="utf-8"))
    identity_samples = [row for row in data["samples"] if row["transform"] == "identity"]

    before = load_model(args.before_checkpoint, args, device)
    after = load_model(args.after_checkpoint, args, device)

    rank_rows = rank_rows_for_model("before", before, identity_samples, args, device)
    rank_rows.extend(rank_rows_for_model("after", after, identity_samples, args, device))
    write_csv(args.output_csv, rank_rows)

    tactical_before = tactical_rows_for_model("before", before, args, device)
    tactical_after = tactical_rows_for_model("after", after, args, device)
    tactical_csv = args.output_csv.with_name("candidate_g_tactical_gate.csv")
    write_csv(tactical_csv, tactical_before + tactical_after)

    write_report(args.output_md, args, rank_rows, tactical_before, tactical_after)
    print(f"device={device}")
    print(f"wrote {args.output_csv}")
    print(f"wrote {tactical_csv}")
    print(f"wrote {args.output_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
