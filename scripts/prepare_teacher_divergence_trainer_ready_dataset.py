#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from fill_teacher_divergence_current_best_probe_round2 import BOARD_SOURCE_PATHS, load_board_map


LEGACY_IDS = {
    "td_exp_00008", "td_exp_00009", "td_exp_00013", "td_exp_00015", "td_exp_00019",
    "td_exp_00021", "td_exp_00024", "td_exp_00055", "td_exp_00058",
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--dryrun-json", type=Path, required=True)
    p.add_argument("--out-json", type=Path, required=True)
    p.add_argument("--out-report", type=Path, required=True)
    p.add_argument("--expected-samples", type=int, default=44)
    return p.parse_args()


def check_rc(value: Any, field: str, mid: str) -> list[int]:
    if not isinstance(value, list) or len(value) != 2:
        raise ValueError(f"{mid}: {field} must be [row, col], got {value!r}")
    rc = [int(value[0]), int(value[1])]
    if not (0 <= rc[0] < 15 and 0 <= rc[1] < 15):
        raise ValueError(f"{mid}: {field} out of range: {rc}")
    return rc


def main() -> None:
    args = parse_args()

    dryrun = json.loads(args.dryrun_json.read_text(encoding="utf-8"))
    samples = dryrun["samples"]

    if len(samples) != args.expected_samples:
        raise RuntimeError(f"expected {args.expected_samples} samples, got {len(samples)}")

    board_map = load_board_map(BOARD_SOURCE_PATHS)

    trainer_samples = []
    group_counts = Counter()
    source_counts = Counter()
    rank_counts = Counter()

    for sample in samples:
        mid = sample["manifest_id"]
        board_hash = sample["board_hash"]
        record = board_map.get(board_hash)

        if record is None:
            raise RuntimeError(f"{mid}: board_hash not found: {board_hash}")

        board = record["board"]
        target_rc = check_rc(sample["target_rc"], "target_rc", mid)
        suppress_rc = check_rc(sample["suppress_rc"], "suppress_rc", mid)

        if target_rc == suppress_rc:
            raise RuntimeError(f"{mid}: target_rc equals suppress_rc")
        if int(board[target_rc[0]][target_rc[1]]) != 0:
            raise RuntimeError(f"{mid}: target_rc not legal: {target_rc}")
        if int(board[suppress_rc[0]][suppress_rc[1]]) != 0:
            raise RuntimeError(f"{mid}: suppress_rc not legal: {suppress_rc}")

        current_player = int(sample["current_player"])
        if current_player not in {-1, 1}:
            raise RuntimeError(f"{mid}: bad current_player {current_player}")

        rank = int(sample["before_target_rank"])
        if not (11 <= rank <= 50):
            raise RuntimeError(f"{mid}: bad rank {rank}")

        group = "legacy_normalized" if mid in LEGACY_IDS else "round2_or_existing"

        trainer_samples.append({
            "case_id": sample.get("case_id") or mid,
            "manifest_id": mid,
            "board_hash": board_hash,
            "board": board,
            "current_player": current_player,
            "target_rc": target_rc,
            "suppress_rc": suppress_rc,
            "sample_weight": float(sample.get("weight", sample.get("sample_weight", 1.0))),
            "metadata": {
                "ready_bucket": sample["ready_bucket"],
                "source_class": sample.get("source_class", ""),
                "primary_source_path": sample.get("primary_source_path", ""),
                "before_target_rank": rank,
                "before_target_prob": float(sample["before_target_prob"]),
                "suppress_prob": float(sample["suppress_prob"]),
                "suppress_candidates_rcs": sample["suppress_candidates_rcs"],
                "suppress_candidates_probs": sample["suppress_candidates_probs"],
                "group": group,
                "board_source": record["source"],
            },
        })

        group_counts[group] += 1
        source_counts[str(sample.get("source_class") or sample.get("primary_source_path") or "")] += 1
        rank_counts[str(rank)] += 1

    if len(trainer_samples) != args.expected_samples:
        raise RuntimeError(f"expected {args.expected_samples} trainer samples, got {len(trainer_samples)}")

    ids = [s["manifest_id"] for s in trainer_samples]
    if len(ids) != len(set(ids)):
        raise RuntimeError("duplicate manifest_id")

    payload = {
        "metadata": {
            "name": "teacher_divergence_round2_trainable_trainer_ready_dataset",
            "source_dryrun_json": str(args.dryrun_json),
            "board_size": 15,
            "sample_count": len(trainer_samples),
            "schema": "single_suppress_policy_margin_with_board",
            "not_c_export": True,
            "not_public_benchmark": True,
            "not_promotion": True,
        },
        "samples": trainer_samples,
    }

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# Teacher-divergence trainer-ready dataset adapter",
        "",
        "## Summary",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| dry-run samples | {len(samples)} |",
        f"| trainer-ready samples | {len(trainer_samples)} |",
        f"| board records indexed | {len(board_map)} |",
        "",
        "## Legacy split",
        "",
        "| group | rows |",
        "|---|---:|",
    ]
    for k, v in group_counts.most_common():
        lines.append(f"| {k} | {v} |")

    lines += [
        "",
        "## Source counts",
        "",
        "| source | rows |",
        "|---|---:|",
    ]
    for k, v in source_counts.most_common():
        lines.append(f"| {k} | {v} |")

    lines += [
        "",
        "## Target rank distribution",
        "",
        "| target rank | rows |",
        "|---|---:|",
    ]
    for k, v in sorted(rank_counts.items(), key=lambda kv: int(kv[0])):
        lines.append(f"| {k} | {v} |")

    lines += [
        "",
        "## Decision",
        "",
        "Ready for tiny isolated training probe.",
        "",
        "No C export.",
        "",
        "No public benchmark.",
        "",
        "No promotion.",
        "",
    ]

    args.out_report.parent.mkdir(parents=True, exist_ok=True)
    args.out_report.write_text("\n".join(lines), encoding="utf-8")

    print("dryrun_samples:", len(samples))
    print("trainer_ready_samples:", len(trainer_samples))
    print("board_records_indexed:", len(board_map))
    print("group_counts:", dict(group_counts))
    print("source_counts:", dict(source_counts))
    print("out_json:", args.out_json)
    print("out_report:", args.out_report)


if __name__ == "__main__":
    main()
