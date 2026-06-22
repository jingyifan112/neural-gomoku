#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build suppress candidates for teacher-divergence current_best probe fill round2 rows."
    )
    parser.add_argument(
        "--probe-fill-csv",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_current_best_probe_fill_round2.csv"),
    )
    parser.add_argument(
        "--out-csv",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_suppress_build_fill_round2.csv"),
    )
    parser.add_argument(
        "--out-report",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_suppress_build_fill_round2_report.md"),
    )
    parser.add_argument("--expected-selected", type=int, default=97)
    parser.add_argument("--max-suppress", type=int, default=5)
    return parser.parse_args()


def parse_json_list(value: str) -> list[Any]:
    if value is None:
        return []
    s = str(value).strip()
    if not s:
        return []
    obj = json.loads(s)
    if not isinstance(obj, list):
        return []
    return obj


def norm_rc(value: Any) -> tuple[int, int] | None:
    if value is None:
        return None
    if isinstance(value, str):
        value = parse_json_list(value)
    if isinstance(value, list) and len(value) == 2:
        return (int(value[0]), int(value[1]))
    return None


def as_float(value: Any) -> float | None:
    try:
        if value is None or str(value).strip() == "":
            return None
        return float(value)
    except Exception:
        return None


def as_int(value: Any) -> int | None:
    try:
        if value is None or str(value).strip() == "":
            return None
        return int(float(value))
    except Exception:
        return None


def select_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        r for r in rows
        if r.get("status_after") == "needs_suppress_build"
        and r.get("target_legal") == "1"
        and r.get("excluded") == "0"
    ]


def output_fields() -> list[str]:
    return [
        "manifest_id",
        "status_before",
        "status_after",
        "bucket_after",
        "primary_source_path",
        "source_class",
        "case_id",
        "game_number",
        "move_count",
        "current_player",
        "target_rc",
        "target_action",
        "before_target_rank",
        "before_target_prob",
        "current_best_direct_rc",
        "current_best_direct_prob",
        "suppress_rc",
        "suppress_rank_in_top_policy",
        "suppress_prob",
        "suppress_prob_gap",
        "suppress_prob_ratio",
        "suppress_candidates_rcs",
        "suppress_candidates_probs",
        "suppress_candidates_ranks",
        "suppress_count",
        "board_hash",
        "probe_source",
        "suppress_source",
        "ready_full_schema_after",
        "excluded",
        "exclude_reason",
        "notes",
    ]


def build_for_row(row: dict[str, str], max_suppress: int) -> dict[str, Any]:
    target = norm_rc(row.get("target_rc"))
    top_rcs_raw = parse_json_list(row.get("current_best_top_policy_rcs", "[]"))
    top_probs_raw = parse_json_list(row.get("current_best_top_policy_probs", "[]"))

    top_rcs = [norm_rc(x) for x in top_rcs_raw]
    top_probs = [as_float(x) for x in top_probs_raw]

    candidates: list[tuple[tuple[int, int], float, int]] = []
    for idx, (rc, prob) in enumerate(zip(top_rcs, top_probs), start=1):
        if rc is None or prob is None:
            continue
        if target is not None and rc == target:
            continue
        candidates.append((rc, prob, idx))

    candidates = candidates[:max_suppress]

    target_prob = as_float(row.get("before_target_prob"))
    target_rank = as_int(row.get("before_target_rank"))

    base = {
        "manifest_id": row.get("manifest_id", ""),
        "status_before": row.get("status_after", ""),
        "bucket_after": row.get("bucket_after", ""),
        "primary_source_path": row.get("primary_source_path", ""),
        "source_class": row.get("source_class", ""),
        "case_id": row.get("case_id", ""),
        "game_number": row.get("game_number", ""),
        "move_count": row.get("move_count", ""),
        "current_player": row.get("current_player", ""),
        "target_rc": row.get("target_rc", ""),
        "target_action": row.get("target_action", ""),
        "before_target_rank": row.get("before_target_rank", ""),
        "before_target_prob": row.get("before_target_prob", ""),
        "current_best_direct_rc": row.get("current_best_direct_rc", ""),
        "current_best_direct_prob": row.get("current_best_direct_prob", ""),
        "board_hash": row.get("board_hash", ""),
        "probe_source": row.get("probe_source", ""),
        "suppress_source": "current_best_top_policy_excluding_target",
    }

    if not candidates:
        return {
            **base,
            "status_after": "needs_suppress_repair",
            "suppress_rc": "",
            "suppress_rank_in_top_policy": "",
            "suppress_prob": "",
            "suppress_prob_gap": "",
            "suppress_prob_ratio": "",
            "suppress_candidates_rcs": "[]",
            "suppress_candidates_probs": "[]",
            "suppress_candidates_ranks": "[]",
            "suppress_count": "0",
            "ready_full_schema_after": "0",
            "excluded": "1",
            "exclude_reason": "no_non_target_top_policy_candidate",
            "notes": "suppress_repair_needed",
        }

    primary_rc, primary_prob, primary_rank = candidates[0]

    gap = ""
    ratio = ""
    if target_prob is not None:
        gap = str(primary_prob - target_prob)
        if target_prob > 0:
            ratio = str(primary_prob / target_prob)

    notes = "suppress_candidates_built"
    if target_rank is not None:
        if target_rank <= 10:
            notes = "suppress_candidates_built_protected_top10"
        elif target_rank <= 50:
            notes = "suppress_candidates_built_trainable_rank_11_50"
        else:
            notes = "suppress_candidates_built_tail_rank_gt50"

    return {
        **base,
        "status_after": "ready_full_schema",
        "suppress_rc": json.dumps(list(primary_rc)),
        "suppress_rank_in_top_policy": str(primary_rank),
        "suppress_prob": str(primary_prob),
        "suppress_prob_gap": gap,
        "suppress_prob_ratio": ratio,
        "suppress_candidates_rcs": json.dumps([list(rc) for rc, _prob, _rank in candidates]),
        "suppress_candidates_probs": json.dumps([prob for _rc, prob, _rank in candidates]),
        "suppress_candidates_ranks": json.dumps([rank for _rc, _prob, rank in candidates]),
        "suppress_count": str(len(candidates)),
        "ready_full_schema_after": "1",
        "excluded": "0",
        "exclude_reason": "",
        "notes": notes,
    }


def write_report(args: argparse.Namespace, rows: list[dict[str, Any]], input_count: int) -> None:
    status_counts = Counter(r["status_after"] for r in rows)
    bucket_counts = Counter(r["bucket_after"] for r in rows)
    notes_counts = Counter(r["notes"] for r in rows)
    suppress_counts = Counter(r["suppress_count"] for r in rows)

    lines = [
        "# Teacher-divergence suppress build fill round2 report",
        "",
        "## Branch",
        "",
        "`exp/15x15-teacher-divergence-suppress-build-fill-round2`",
        "",
        "## Scope",
        "",
        "- Input is current_best probe fill round2 CSV.",
        "- Selects only rows with `status_after == needs_suppress_build`.",
        "- Selects only legal target rows.",
        "- Builds suppress candidates from current_best top-policy moves excluding the teacher target.",
        "- Does not process skipped/invalid rows.",
        "- Does not process `needs_rapfi_requery` rows.",
        "- Does not process `needs_board_join` rows.",
        "- No training.",
        "- No checkpoint save.",
        "- No C export.",
        "- No public benchmark.",
        "- No promotion.",
        "",
        "## Inputs",
        "",
        f"- probe fill CSV: `{args.probe_fill_csv}`",
        f"- selected rows: {input_count}",
        f"- max suppress candidates per row: {args.max_suppress}",
        "",
        "## Summary",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| selected needs_suppress_build rows | {input_count} |",
        f"| output rows | {len(rows)} |",
        f"| ready_full_schema rows | {sum(1 for r in rows if r['status_after'] == 'ready_full_schema')} |",
        f"| suppress repair rows | {sum(1 for r in rows if r['status_after'] == 'needs_suppress_repair')} |",
        "",
        "## Status after suppress build",
        "",
        "| status_after | rows |",
        "|---|---:|",
    ]

    for key, value in status_counts.most_common():
        lines.append(f"| {key} | {value} |")

    lines.extend([
        "",
        "## Bucket after suppress build",
        "",
        "| bucket_after | rows |",
        "|---|---:|",
    ])

    for key, value in bucket_counts.most_common():
        lines.append(f"| {key} | {value} |")

    lines.extend([
        "",
        "## Suppress count distribution",
        "",
        "| suppress_count | rows |",
        "|---|---:|",
    ])

    for key, value in sorted(suppress_counts.items(), key=lambda kv: int(kv[0])):
        lines.append(f"| {key} | {value} |")

    lines.extend([
        "",
        "## Notes distribution",
        "",
        "| notes | rows |",
        "|---|---:|",
    ])

    for key, value in notes_counts.most_common():
        lines.append(f"| {key} | {value} |")

    lines.extend([
        "",
        "## Preview",
        "",
        "| manifest_id | bucket_after | target_rc | target_rank | target_prob | suppress_rc | suppress_rank | suppress_prob | status_after | notes |",
        "|---|---|---|---:|---:|---|---:|---:|---|---|",
    ])

    for r in rows[:80]:
        lines.append(
            "| {manifest_id} | {bucket_after} | `{target_rc}` | {target_rank} | {target_prob} | `{suppress_rc}` | {suppress_rank} | {suppress_prob} | {status_after} | {notes} |".format(
                manifest_id=r["manifest_id"],
                bucket_after=r["bucket_after"],
                target_rc=r["target_rc"],
                target_rank=r["before_target_rank"],
                target_prob=r["before_target_prob"],
                suppress_rc=r["suppress_rc"],
                suppress_rank=r["suppress_rank_in_top_policy"],
                suppress_prob=r["suppress_prob"],
                status_after=r["status_after"],
                notes=r["notes"],
            )
        )

    if len(rows) > 80:
        lines.append(f"| . | . | . | . | . | . | . | . | . | {len(rows) - 80} more rows in CSV |")

    lines.extend([
        "",
        "## Interpretation",
        "",
        "Rows with suppress candidates now have full current_best target/suppress policy fields and can be merged into the manifest as full-schema rows.",
        "",
        "Protected top10 rows should remain protection/eval rows unless a later training export deliberately excludes them from trainable data.",
        "",
        "Tail rank > 50 rows should remain diagnostic-only unless a later design explicitly allows them.",
        "",
        "Trainable rank 11-50 rows are the primary candidates for a later dry-run dataset export after manifest merge.",
        "",
        "## Decision",
        "",
        "No training.",
        "",
        "No checkpoint.",
        "",
        "No C export.",
        "",
        "No public benchmark.",
        "",
        "No promotion.",
        "",
    ])

    args.out_report.parent.mkdir(parents=True, exist_ok=True)
    args.out_report.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()

    rows = list(csv.DictReader(args.probe_fill_csv.open(newline="", encoding="utf-8")))
    selected = select_rows(rows)

    if len(selected) != args.expected_selected:
        raise RuntimeError(f"expected {args.expected_selected} selected rows, got {len(selected)}")

    out_rows = [build_for_row(row, args.max_suppress) for row in selected]

    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=output_fields(), lineterminator="\n")
        writer.writeheader()
        writer.writerows(out_rows)

    write_report(args, out_rows, len(selected))

    print(f"input_rows: {len(rows)}")
    print(f"selected_rows: {len(selected)}")
    print(f"output_rows: {len(out_rows)}")
    print(f"status_after_counts: {dict(Counter(r['status_after'] for r in out_rows))}")
    print(f"bucket_after_counts: {dict(Counter(r['bucket_after'] for r in out_rows))}")
    print(f"out_csv: {args.out_csv}")
    print(f"out_report: {args.out_report}")
    print("no training; no checkpoint saved")


if __name__ == "__main__":
    main()
