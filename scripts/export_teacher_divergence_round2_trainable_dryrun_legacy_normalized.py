#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any

from export_teacher_divergence_round2_trainable_dryrun import (
    build_sample,
    has_export_schema,
    is_blank,
    read_csv,
    ready_bucket,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Dry-run export for legacy-normalized teacher-divergence trainable rows."
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_expanded_candidate_manifest_legacy_suppress_normalized.csv"),
    )
    parser.add_argument(
        "--out-json",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_round2_trainable_dryrun_dataset_legacy_normalized.json"),
    )
    parser.add_argument(
        "--out-report",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_round2_trainable_dryrun_legacy_normalized_report.md"),
    )
    parser.add_argument("--expected-exportable", type=int, default=44)
    parser.add_argument("--expected-excluded", type=int, default=0)
    return parser.parse_args()


def is_non_duplicate(row: dict[str, str]) -> bool:
    return is_blank(row.get("duplicate_of"))


def main() -> None:
    args = parse_args()

    _fields, rows = read_csv(args.manifest)
    nondup = [r for r in rows if is_non_duplicate(r)]

    ready_trainable = [
        r for r in nondup
        if r.get("status") == "ready_full_schema"
        and ready_bucket(r) == "trainable_rank_11_50"
    ]

    exportable_rows = [r for r in ready_trainable if has_export_schema(r)]
    excluded_rows = [r for r in ready_trainable if not has_export_schema(r)]

    if len(exportable_rows) != args.expected_exportable:
        raise RuntimeError(f"expected {args.expected_exportable} exportable rows, got {len(exportable_rows)}")
    if len(excluded_rows) != args.expected_excluded:
        raise RuntimeError(f"expected {args.expected_excluded} excluded rows, got {len(excluded_rows)}")

    samples = [build_sample(r) for r in exportable_rows]

    manifest_ids = [s["manifest_id"] for s in samples]
    if len(manifest_ids) != len(set(manifest_ids)):
        raise RuntimeError("duplicate manifest_id in dry-run samples")

    source_counts = Counter(s["source_class"] or s["primary_source_path"] for s in samples)
    rank_counts = Counter(str(s["before_target_rank"]) for s in samples)
    suppress_count_distribution = Counter(str(len(s["suppress_candidates_rcs"])) for s in samples)
    legacy_action_counts = Counter(
        "legacy_normalized" if s.get("manifest_id") in {
            "td_exp_00008", "td_exp_00009", "td_exp_00013", "td_exp_00015", "td_exp_00019",
            "td_exp_00021", "td_exp_00024", "td_exp_00055", "td_exp_00058",
        } else "round2_or_existing"
        for s in samples
    )

    payload: dict[str, Any] = {
        "metadata": {
            "name": "teacher_divergence_round2_trainable_dryrun_dataset_legacy_normalized",
            "manifest": str(args.manifest),
            "board_size": 15,
            "sample_count": len(samples),
            "selection": {
                "status": "ready_full_schema",
                "ready_bucket": "trainable_rank_11_50",
                "requires_suppress_fields": True,
                "excluded_count": len(excluded_rows),
            },
            "not_training": True,
            "not_checkpoint": True,
            "not_c_export": True,
            "not_public_benchmark": True,
            "not_promotion": True,
        },
        "samples": samples,
        "excluded_from_dryrun_export": [],
    }

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# Teacher-divergence round2 trainable dry-run export after legacy normalization",
        "",
        "## Branch",
        "",
        "`exp/15x15-teacher-divergence-legacy-suppress-manifest-update`",
        "",
        "## Scope",
        "",
        "- Dry-run export only.",
        "- Uses the legacy-normalized manifest.",
        "- Selects `status == ready_full_schema` and `ready_bucket == trainable_rank_11_50`.",
        "- Requires target rank/prob and suppress fields.",
        "- Expects all 44 trainable rows to be export-schema-complete.",
        "- No training.",
        "- No checkpoint save.",
        "- No C export.",
        "- No public benchmark.",
        "- No promotion.",
        "",
        "## Input",
        "",
        f"- manifest: `{args.manifest}`",
        "",
        "## Summary",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| ready trainable rows | {len(ready_trainable)} |",
        f"| exportable dry-run samples | {len(samples)} |",
        f"| excluded rows | {len(excluded_rows)} |",
        "",
        "## Legacy normalization split",
        "",
        "| group | rows |",
        "|---|---:|",
    ]

    for key, value in legacy_action_counts.most_common():
        lines.append(f"| {key} | {value} |")

    lines.extend([
        "",
        "## Source counts",
        "",
        "| source | rows |",
        "|---|---:|",
    ])

    for key, value in source_counts.most_common():
        lines.append(f"| {key} | {value} |")

    lines.extend([
        "",
        "## Suppress candidate count distribution",
        "",
        "| suppress candidate count | rows |",
        "|---|---:|",
    ])

    for key, value in sorted(suppress_count_distribution.items(), key=lambda kv: int(kv[0])):
        lines.append(f"| {key} | {value} |")

    lines.extend([
        "",
        "## Target rank distribution",
        "",
        "| target rank | rows |",
        "|---|---:|",
    ])

    for key, value in sorted(rank_counts.items(), key=lambda kv: int(kv[0])):
        lines.append(f"| {key} | {value} |")

    lines.extend([
        "",
        "## Outputs",
        "",
        f"- `{args.out_json}`",
        f"- `{args.out_report}`",
        "",
        "## Decision",
        "",
        "The 44-row trainable dry-run dataset validates after legacy normalization.",
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

    print("manifest_rows:", len(rows))
    print("non_duplicate_rows:", len(nondup))
    print("ready_trainable_rows:", len(ready_trainable))
    print("exportable_dryrun_samples:", len(samples))
    print("excluded_rows:", len(excluded_rows))
    print("legacy_action_counts:", json.dumps(dict(legacy_action_counts), sort_keys=True))
    print("source_counts:", json.dumps(dict(source_counts), sort_keys=True))
    print("out_json:", args.out_json)
    print("out_report:", args.out_report)
    print("no training; no checkpoint saved")


if __name__ == "__main__":
    main()
