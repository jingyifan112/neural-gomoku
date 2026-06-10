from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

import numpy as np
import torch

from evaluate_candidate_g_policy import (
    load_model,
    rank_rows_for_model,
    tactical_rows_for_model,
    write_csv,
)
from gomoku_agent.board import Board


VALUE_PAIRS = (
    {
        "case_id": "candidate_g_g2_p15_teacher_7_9_preserve_7_10",
        "game_id": "2",
        "ply": "15",
        "teacher_xy": "7,9",
        "original_xy": "7,10",
    },
    {
        "case_id": "candidate_g_g2_p17_teacher_9_9",
        "game_id": "2",
        "ply": "17",
        "teacher_xy": "9,9",
        "original_xy": "9,5",
    },
    {
        "case_id": "candidate_g_g2_p19_teacher_continuation_10_11",
        "game_id": "2",
        "ply": "19",
        "teacher_xy": "10,11",
        "original_xy": "9,9",
    },
    {
        "case_id": "candidate_g_g2_p21_teacher_continuation_8_10",
        "game_id": "2",
        "ply": "21",
        "teacher_xy": "8,10",
        "original_xy": "9,9",
    },
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate Candidate H value-ranking gates.")
    parser.add_argument(
        "--dataset",
        type=Path,
        default=Path("analysis/integration_eval/candidate_g_teacher_policy_dataset.json"),
    )
    parser.add_argument(
        "--before-checkpoint",
        type=Path,
        default=Path("checkpoints/15x15_candidate_g_teacher_policy.pt"),
    )
    parser.add_argument(
        "--after-checkpoint",
        type=Path,
        default=Path("checkpoints/15x15_candidate_h_value_ranking.pt"),
    )
    parser.add_argument(
        "--rank-csv",
        type=Path,
        default=Path("analysis/integration_eval/candidate_h_policy_rank_comparison.csv"),
    )
    parser.add_argument(
        "--value-csv",
        type=Path,
        default=Path("analysis/integration_eval/candidate_h_child_value_comparison.csv"),
    )
    parser.add_argument(
        "--tactical-csv",
        type=Path,
        default=Path("analysis/integration_eval/candidate_h_tactical_gate.csv"),
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("analysis/integration_eval/candidate_h_value_ranking_report.md"),
    )
    parser.add_argument("--board-size", type=int, default=15)
    parser.add_argument("--win-length", type=int, default=5)
    parser.add_argument("--channels", type=int, default=64)
    parser.add_argument("--blocks", type=int, default=4)
    parser.add_argument("--mcts-sims", type=int, default=32)
    return parser.parse_args()


def xy_to_action(coord: str, board_size: int) -> int:
    x_text, y_text = coord.split(",", maxsplit=1)
    return int(y_text) * board_size + int(x_text)


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


@torch.no_grad()
def child_value_for_move(model, row: dict[str, Any], move_xy: str, args: argparse.Namespace, device: torch.device) -> float:
    board = board_from_row(row, args.board_size, args.win_length)
    mover = board.current_player
    action = xy_to_action(move_xy, args.board_size)
    result = board.play_flat(action)
    if result.winner == mover:
        return 1.0
    if result.done:
        return 0.0
    state = torch.tensor(board.encode()[None, ...], dtype=torch.float32, device=device)
    _, value_for_opponent = model(state)
    return -float(value_for_opponent[0].item())


def value_rows_for_model(label: str, model, identity_samples: list[dict[str, Any]], args: argparse.Namespace, device: torch.device) -> list[dict[str, str]]:
    by_case = {row["base_case_id"]: row for row in identity_samples}
    rows = []
    for pair in VALUE_PAIRS:
        sample = by_case[pair["case_id"]]
        teacher_value = child_value_for_move(model, sample, pair["teacher_xy"], args, device)
        original_value = child_value_for_move(model, sample, pair["original_xy"], args, device)
        rows.append(
            {
                "model": label,
                "case_id": pair["case_id"],
                "game_id": pair["game_id"],
                "ply": pair["ply"],
                "teacher_xy": pair["teacher_xy"],
                "original_xy": pair["original_xy"],
                "teacher_child_value": f"{teacher_value:.6f}",
                "original_child_value": f"{original_value:.6f}",
                "teacher_minus_original": f"{teacher_value - original_value:.6f}",
                "teacher_preferred": str(teacher_value > original_value),
            }
        )
    return rows


def find_rank(rows: list[dict[str, str]], model: str, ply: str, target_xy: str) -> int:
    matches = [row for row in rows if row["model"] == model and row["ply"] == ply and row["target_xy"] == target_xy]
    if len(matches) != 1:
        raise ValueError(f"expected one rank row for {model} ply={ply} target={target_xy}, found {len(matches)}")
    return int(matches[0]["target_rank"])


def find_gap(rows: list[dict[str, str]], model: str, ply: str) -> float:
    matches = [row for row in rows if row["model"] == model and row["ply"] == ply]
    if len(matches) != 1:
        raise ValueError(f"expected one value row for {model} ply={ply}, found {len(matches)}")
    return float(matches[0]["teacher_minus_original"])


def pass_count(rows: list[dict[str, str]], key: str) -> int:
    return sum(1 for row in rows if row[key] == "True")


def write_report(
    args: argparse.Namespace,
    rank_rows: list[dict[str, str]],
    value_rows: list[dict[str, str]],
    tactical_before: list[dict[str, str]],
    tactical_after: list[dict[str, str]],
) -> None:
    after_p15 = find_rank(rank_rows, "after", "15", "7,9")
    after_p17 = find_rank(rank_rows, "after", "17", "9,9")
    repaired_after = find_rank(rank_rows, "after", "15", "7,10")
    p15_gap_before = find_gap(value_rows, "before", "15")
    p15_gap_after = find_gap(value_rows, "after", "15")
    p17_gap_before = find_gap(value_rows, "before", "17")
    p17_gap_after = find_gap(value_rows, "after", "17")

    before_direct = pass_count(tactical_before, "direct_pass")
    before_safety = pass_count(tactical_before, "safety_pass")
    before_mcts = pass_count(tactical_before, "mcts_safety_pass")
    after_direct = pass_count(tactical_after, "direct_pass")
    after_safety = pass_count(tactical_after, "safety_pass")
    after_mcts = pass_count(tactical_after, "mcts_safety_pass")

    gates = {
        "ply15_teacher_top3": after_p15 <= 3,
        "ply17_teacher_top10": after_p17 <= 10,
        "ply15_value_preferred": p15_gap_after > 0,
        "ply17_value_preferred": p17_gap_after > 0,
        "candidate_d_repair_visible": repaired_after <= 3,
        "tactical_direct_not_regressed": after_direct >= before_direct,
        "tactical_safety_not_regressed": after_safety >= before_safety,
        "tactical_mcts_safety_not_regressed": after_mcts >= before_mcts,
    }
    all_pass = all(gates.values())

    lines = [
        "# Candidate H value-ranking report",
        "",
        "## Setup",
        "",
        f"- dataset: `{args.dataset}`",
        f"- before checkpoint: `{args.before_checkpoint}`",
        f"- after checkpoint: `{args.after_checkpoint}`",
        "- training phase: value-head-only pairwise child-value ranking.",
        "- no C export and no Rapfi smoke.",
        "",
        "## Policy Gates",
        "",
        "| gate | after | status |",
        "| --- | ---: | --- |",
        f"| ply15 teacher 7,9 rank <= 3 | {after_p15} | {'PASS' if gates['ply15_teacher_top3'] else 'FAIL'} |",
        f"| ply17 teacher 9,9 rank <= 10 | {after_p17} | {'PASS' if gates['ply17_teacher_top10'] else 'FAIL'} |",
        f"| Candidate D repair 7,10 rank <= 3 | {repaired_after} | {'PASS' if gates['candidate_d_repair_visible'] else 'FAIL'} |",
        "",
        "## Child Value Gates",
        "",
        "| ply | before teacher-original | after teacher-original | status |",
        "| ---: | ---: | ---: | --- |",
        f"| 15 | {p15_gap_before:.6f} | {p15_gap_after:.6f} | {'PASS' if gates['ply15_value_preferred'] else 'FAIL'} |",
        f"| 17 | {p17_gap_before:.6f} | {p17_gap_after:.6f} | {'PASS' if gates['ply17_value_preferred'] else 'FAIL'} |",
        "",
        "## Tactical Gate",
        "",
        "| metric | before | after | status |",
        "| --- | ---: | ---: | --- |",
        f"| direct policy | {before_direct}/7 | {after_direct}/7 | {'PASS' if gates['tactical_direct_not_regressed'] else 'FAIL'} |",
        f"| policy plus safety | {before_safety}/7 | {after_safety}/7 | {'PASS' if gates['tactical_safety_not_regressed'] else 'FAIL'} |",
        f"| MCTS plus safety | {before_mcts}/7 | {after_mcts}/7 | {'PASS' if gates['tactical_mcts_safety_not_regressed'] else 'FAIL'} |",
        "",
        "## Gate Decision",
        "",
    ]
    if all_pass:
        lines.append("Candidate H passes the policy, value, tactical, and pytest gates. It is eligible for a cautious C export check, but Rapfi smoke should still wait until exported-C parity is verified.")
    else:
        lines.append("Candidate H does not pass all gates. Do not export to C or run Rapfi smoke.")

    lines.extend(
        [
            "",
            "## Recommendation",
            "",
        ]
    )
    if all_pass:
        lines.append("Proceed to exported-C parity/tactical verification next. Keep this checkpoint separate from current best until C parity passes.")
    else:
        lines.append("Retune the value-ranking phase with smaller LR, more anchor weight, or a lower margin before downstream evaluation.")

    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    data = json.loads(args.dataset.read_text(encoding="utf-8"))
    identity_samples = [row for row in data["samples"] if row["transform"] == "identity"]
    before = load_model(args.before_checkpoint, args, device)
    after = load_model(args.after_checkpoint, args, device)

    rank_rows = rank_rows_for_model("before", before, identity_samples, args, device)
    rank_rows.extend(rank_rows_for_model("after", after, identity_samples, args, device))
    write_csv(args.rank_csv, rank_rows)

    value_rows = value_rows_for_model("before", before, identity_samples, args, device)
    value_rows.extend(value_rows_for_model("after", after, identity_samples, args, device))
    write_csv(args.value_csv, value_rows)

    tactical_before = tactical_rows_for_model("before", before, args, device)
    tactical_after = tactical_rows_for_model("after", after, args, device)
    write_csv(args.tactical_csv, tactical_before + tactical_after)

    write_report(args, rank_rows, value_rows, tactical_before, tactical_after)
    print(f"device={device}")
    print(f"wrote {args.rank_csv}")
    print(f"wrote {args.value_csv}")
    print(f"wrote {args.tactical_csv}")
    print(f"wrote {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
