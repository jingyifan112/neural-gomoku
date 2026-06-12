#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
for _path in (REPO_ROOT, REPO_ROOT / "src"):
    _s = str(_path)
    if _s not in sys.path:
        sys.path.insert(0, _s)


REPO_ROOT = Path(__file__).resolve().parents[1]
for _path in (REPO_ROOT, REPO_ROOT / "src"):
    _s = str(_path)
    if _s not in sys.path:
        sys.path.insert(0, _s)


BOARD_SIZE = 15


def load_census_module(path: Path):
    spec = importlib.util.spec_from_file_location("candidate_d_teacher_disagreement_census", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def rc_to_xy(rc: list[int] | None) -> str | None:
    if rc is None:
        return None
    row, col = rc
    return f"{col},{row}"


def count_stones(board: list[list[int]]) -> dict[str, int]:
    black = 0
    white = 0
    empty = 0
    for row in board:
        for v in row:
            if int(v) == 1:
                black += 1
            elif int(v) == -1:
                white += 1
            else:
                empty += 1
    return {"black": black, "white": white, "empty": empty, "total_stones": black + white}


def board_to_strings(board: list[list[int]]) -> list[str]:
    out = []
    for row in board:
        chars = []
        for v in row:
            iv = int(v)
            if iv == 1:
                chars.append("X")
            elif iv == -1:
                chars.append("O")
            else:
                chars.append(".")
        out.append("".join(chars))
    return out


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Build Candidate G teacher seed board-state dataset dry run. No training is run."
    )
    ap.add_argument(
        "--manifest",
        type=Path,
        default=Path("analysis/integration_eval/candidate_g_teacher_seed_manifest.json"),
    )
    ap.add_argument(
        "--debug-log",
        type=Path,
        default=Path("eval_logs/rapfi_smoke/candidate_d_move15_mcts32_debug_vs_rapfi_fast_g2.log"),
    )
    ap.add_argument(
        "--census-script",
        type=Path,
        default=Path("scripts/candidate_d_teacher_disagreement_census.py"),
    )
    ap.add_argument(
        "--output-json",
        type=Path,
        default=Path("analysis/integration_eval/candidate_g_teacher_seed_dataset.json"),
    )
    ap.add_argument(
        "--output-md",
        type=Path,
        default=Path("analysis/integration_eval/candidate_g_teacher_seed_dataset.md"),
    )
    args = ap.parse_args()

    manifest = json.loads(args.manifest.read_text())
    census_mod = load_census_module(args.census_script)
    decisions = census_mod.replay_decision_boards(args.debug_log)

    dataset_rows: list[dict[str, Any]] = []
    missing: list[dict[str, Any]] = []
    side_mismatches: list[dict[str, Any]] = []

    for row in manifest["rows"]:
        key = (int(row["game"]), int(row["ply"]))
        decision = decisions.get(key)
        if decision is None:
            missing.append(row)
            continue

        if decision.side_to_move != row["side"]:
            side_mismatches.append(
                {
                    "id": row["id"],
                    "manifest_side": row["side"],
                    "replayed_side": decision.side_to_move,
                    "game": row["game"],
                    "ply": row["ply"],
                }
            )

        board = decision.board
        stones = count_stones(board)

        dataset_rows.append(
            {
                "id": row["id"],
                "role": row["role"],
                "reason": row["reason"],
                "weight": row["weight"],
                "game": row["game"],
                "ply": row["ply"],
                "side_to_move": decision.side_to_move,
                "manifest_side": row["side"],
                "board_size": BOARD_SIZE,
                "board": board,
                "board_strings": board_to_strings(board),
                "last_move_rc": decision.last_move_rc,
                "last_move_xy": rc_to_xy(decision.last_move_rc),
                "model_move": row["model_move"],
                "teacher_move": row["teacher_move"],
                "policy_target_move": row["teacher_move"],
                "teacher_move_policy_rank": row["teacher_move_policy_rank"],
                "model_move_policy_rank": row["model_move_policy_rank"],
                "teacher_policy_prob": row["teacher_policy_prob"],
                "model_policy_prob": row["model_policy_prob"],
                "policy_probability_gap_teacher_minus_model": row["policy_probability_gap_teacher_minus_model"],
                "policy_logit_gap_teacher_minus_model": row["policy_logit_gap_teacher_minus_model"],
                "value_current_position": row["value_current_position"],
                "value_original_move": row["value_original_move"],
                "value_teacher_move": row["value_teacher_move"],
                "teacher_value_disfavored": row["teacher_value_disfavored"],
                "teacher_top3_policy": row["teacher_top3_policy"],
                "strong_teacher_continuation_preference": row["strong_teacher_continuation_preference"],
                "diverges": row["diverges"],
                "teacher_eval_current": row["teacher_eval_current"],
                "teacher_bestline_current": row["teacher_bestline_current"],
                "rapfi_after_original_eval": row["rapfi_after_original_eval"],
                "rapfi_after_original_move": row["rapfi_after_original_move"],
                "rapfi_after_original_bestline": row["rapfi_after_original_bestline"],
                "rapfi_after_teacher_eval": row["rapfi_after_teacher_eval"],
                "rapfi_after_teacher_move": row["rapfi_after_teacher_move"],
                "rapfi_after_teacher_bestline": row["rapfi_after_teacher_bestline"],
                "stone_counts": stones,
            }
        )

    dataset_rows = sorted(dataset_rows, key=lambda r: (r["game"], r["ply"], r["role"]))

    role_counts: dict[str, int] = {}
    for row in dataset_rows:
        role_counts[row["role"]] = role_counts.get(row["role"], 0) + 1

    output = {
        "name": "candidate_g_teacher_seed_dataset",
        "purpose": "board-state dry-run dataset for Candidate G teacher distillation; not trained yet",
        "source_manifest": str(args.manifest),
        "source_debug_log": str(args.debug_log),
        "notes": [
            "No training was run.",
            "No export was run.",
            "No promotion was run.",
            "Rows include replayed board state and last-move coordinates.",
            "This is still a dry-run dataset pending review before any training command.",
        ],
        "summary": {
            "manifest_rows": len(manifest["rows"]),
            "dataset_rows": len(dataset_rows),
            "missing_replay_rows": len(missing),
            "side_mismatches": len(side_mismatches),
            "role_counts": role_counts,
        },
        "missing": missing,
        "side_mismatches": side_mismatches,
        "rows": dataset_rows,
    }

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(output, indent=2) + "\n")

    lines = [
        "# Candidate G teacher seed dataset",
        "",
        "## Scope",
        "",
        "This is a board-state dry-run dataset for Candidate G teacher distillation.",
        "",
        "- no training",
        "- no export",
        "- no promotion",
        "- no smoke match",
        "",
        "Rows were selected from the Candidate G teacher seed manifest and joined with replayed board state from the Candidate D mcts32 debug log.",
        "",
        "## Summary",
        "",
        f"- manifest rows: {len(manifest['rows'])}",
        f"- dataset rows: {len(dataset_rows)}",
        f"- missing replay rows: {len(missing)}",
        f"- side mismatches: {len(side_mismatches)}",
        "",
        "## Role counts",
        "",
    ]

    for role, count in sorted(role_counts.items()):
        lines.append(f"- {role}: {count}")

    lines += [
        "",
        "## Selected dataset rows",
        "",
        "| role | game | ply | side | last move | model | teacher | teacher rank | weight | stones |",
        "|---|---:|---:|---|---|---|---|---:|---:|---:|",
    ]

    for row in dataset_rows:
        lines.append(
            f"| {row['role']} | {row['game']} | {row['ply']} | {row['side_to_move']} | "
            f"{row['last_move_xy']} | {row['model_move']} | {row['teacher_move']} | "
            f"{row['teacher_move_policy_rank']} | {float(row['weight']):.2f} | "
            f"{row['stone_counts']['total_stones']} |"
        )

    if missing:
        lines += ["", "## Missing replay rows", ""]
        for row in missing:
            lines.append(f"- {row['id']}")

    if side_mismatches:
        lines += ["", "## Side mismatches", ""]
        for row in side_mismatches:
            lines.append(
                f"- {row['id']}: manifest={row['manifest_side']} replayed={row['replayed_side']}"
            )

    lines += [
        "",
        "## Next step",
        "",
        "Review this dry-run dataset before converting it into a trainable tensor dataset or launching any Candidate G training run.",
        "",
    ]

    args.output_md.write_text("\n".join(lines))

    print("wrote", args.output_json)
    print("wrote", args.output_md)
    print(json.dumps(output["summary"], indent=2))

    if missing or side_mismatches:
        raise SystemExit("dataset built with missing rows or side mismatches; review required")


if __name__ == "__main__":
    main()
