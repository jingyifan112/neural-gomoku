#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any

from fill_teacher_divergence_suppress_build_round2 import build_for_row, output_fields, select_rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build suppress candidates for legacy trainable current_best probe fill rows."
    )
    parser.add_argument(
        "--probe-fill-csv",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_legacy_trainable_current_best_probe_fill.csv"),
    )
    parser.add_argument(
        "--out-csv",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_legacy_trainable_suppress_fill.csv"),
    )
    parser.add_argument(
        "--out-report",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_legacy_trainable_suppress_fill_report.md"),
    )
    parser.add_argument("--expected-selected", type=int, default=9)
    parser.add_argument("--max-suppress", type=int, default=5)
    return parser.parse_args()


def write_report(args: argparse.Namespace, rows: list[dict[str, Any]], selected_count: int) -> None:
    status_counts = Counter(r["status_after"] for r in rows)
    bucket_counts = Counter(r["bucket_after"] for r in rows)
    notes_counts = Counter(r["notes"] for r in rows)
    suppress_counts = Counter(r["suppress_count"] for r in rows)

    lines = [
        "# Teacher-divergence legacy trainable suppress fill report",
        "",
        "## Branch",
        "",
        "`exp/15x15-teacher-divergence-legacy-trainable-probe-fill`",
        "",
        "## Scope",
        "",
        "- Builds suppress candidates only for legal legacy trainable probe rows.",
        "- Input is legacy trainable current_best probe fill CSV.",
        "- Does not process round2 already-exportable rows.",
        "- Does not process protected top10 rows.",
        "- Does not process tail rank > 50 rows.",
        "- No training.",
        "- No checkpoint save.",
        "- No C export.",
        "- No public benchmark.",
        "- No promotion.",
        "",
        "## Inputs",
        "",
        f"- legacy probe fill CSV: `{args.probe_fill_csv}`",
        f"- selected legal rows: {selected_count}",
        f"- max suppress candidates per row: {args.max_suppress}",
        "",
        "## Summary",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| selected needs_suppress_build rows | {selected_count} |",
        f"| output rows | {len(rows)} |",
        f"| ready_full_schema rows | {sum(1 for r in rows if r['status_after'] == 'ready_full_schema')} |",
        f"| suppress repair rows | {sum(1 for r in rows if r['status_after'] == 'needs_suppress_repair')} |",
        "",
        "## Status after suppress fill",
        "",
        "| status_after | rows |",
        "|---|---:|",
    ]

    for key, value in status_counts.most_common():
        lines.append(f"| {key} | {value} |")

    lines.extend([
        "",
        "## Bucket after suppress fill",
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
        "## Row preview",
        "",
        "| manifest_id | bucket_after | target_rc | target_rank | target_prob | suppress_rc | suppress_rank | suppress_prob | status_after | notes |",
        "|---|---|---|---:|---:|---|---:|---:|---|---|",
    ])

    for r in rows:
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

    lines.extend([
        "",
        "## Decision",
        "",
        "Use these rows in a later manifest normalization update only if all selected rows are ready_full_schema.",
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

    with args.probe_fill_csv.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

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

    print("input_rows:", len(rows))
    print("selected_rows:", len(selected))
    print("output_rows:", len(out_rows))
    print("status_after_counts:", json.dumps(dict(Counter(r["status_after"] for r in out_rows)), sort_keys=True))
    print("bucket_after_counts:", json.dumps(dict(Counter(r["bucket_after"] for r in out_rows)), sort_keys=True))
    print("out_csv:", args.out_csv)
    print("out_report:", args.out_report)
    print("no training; no checkpoint saved")


if __name__ == "__main__":
    main()
