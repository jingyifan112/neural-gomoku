#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


REQUIRED_EXPORT_FIELDS = [
    "manifest_id",
    "board_hash",
    "current_player",
    "target_rc",
    "target_action",
    "before_target_rank",
    "before_target_prob",
    "suppress_rc",
    "suppress_prob",
    "suppress_candidates_rcs",
    "suppress_candidates_probs",
]

COPY_FROM_PROBE = [
    "target_action",
    "target_legal",
    "before_target_rank",
    "before_target_prob",
    "current_best_direct_rc",
    "current_best_direct_prob",
    "current_best_top_policy_rcs",
    "current_best_top_policy_probs",
    "probe_source",
]

COPY_FROM_SUPPRESS = [
    "target_action",
    "target_legal",
    "before_target_rank",
    "before_target_prob",
    "current_best_direct_rc",
    "current_best_direct_prob",
    "current_best_top_policy_rcs",
    "current_best_top_policy_probs",
    "suppress_rc",
    "suppress_prob",
    "suppress_rank_in_top_policy",
    "suppress_count",
    "suppress_candidates_rcs",
    "suppress_candidates_probs",
    "suppress_prob_gap",
    "suppress_prob_ratio",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Merge legacy trainable suppress fill into teacher-divergence manifest."
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_expanded_candidate_manifest_with_suppress_round2.csv"),
    )
    parser.add_argument(
        "--legacy-probe-fill-csv",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_legacy_trainable_current_best_probe_fill.csv"),
    )
    parser.add_argument(
        "--legacy-suppress-fill-csv",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_legacy_trainable_suppress_fill.csv"),
    )
    parser.add_argument(
        "--out-csv",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_expanded_candidate_manifest_legacy_suppress_normalized.csv"),
    )
    parser.add_argument(
        "--out-report",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_legacy_suppress_manifest_update_report.md"),
    )
    parser.add_argument("--expected-legacy-rows", type=int, default=9)
    return parser.parse_args()


def is_blank(value: Any) -> bool:
    if value is None:
        return True
    s = str(value).strip()
    return s == "" or s.lower() in {"none", "nan", "na", "null"}


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def ready_bucket(row: dict[str, str]) -> str:
    return row.get("ready_bucket") or row.get("bucket") or ""


def is_nondup(row: dict[str, str]) -> bool:
    return is_blank(row.get("duplicate_of"))


def export_schema_complete(row: dict[str, str]) -> bool:
    return all(not is_blank(row.get(field)) for field in REQUIRED_EXPORT_FIELDS)


def index_by_id(rows: list[dict[str, str]], label: str) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for row in rows:
        mid = row.get("manifest_id", "").strip()
        if not mid:
            raise RuntimeError(f"{label}: missing manifest_id")
        if mid in out:
            raise RuntimeError(f"{label}: duplicate manifest_id {mid}")
        out[mid] = row
    return out


def add_field(fields: list[str], field: str) -> None:
    if field not in fields:
        fields.append(field)


def main() -> None:
    args = parse_args()

    fields, manifest_rows = read_csv(args.manifest)
    _probe_fields, probe_rows = read_csv(args.legacy_probe_fill_csv)
    _suppress_fields, suppress_rows = read_csv(args.legacy_suppress_fill_csv)

    if len(probe_rows) != args.expected_legacy_rows:
        raise RuntimeError(f"expected {args.expected_legacy_rows} legacy probe rows, got {len(probe_rows)}")
    if len(suppress_rows) != args.expected_legacy_rows:
        raise RuntimeError(f"expected {args.expected_legacy_rows} legacy suppress rows, got {len(suppress_rows)}")

    probe_by_id = index_by_id(probe_rows, "legacy probe fill")
    suppress_by_id = index_by_id(suppress_rows, "legacy suppress fill")

    if set(probe_by_id) != set(suppress_by_id):
        raise RuntimeError("legacy probe/suppress manifest_id sets differ")

    legacy_ids = sorted(suppress_by_id)

    for row in probe_rows:
        if row.get("status_after") != "needs_suppress_build":
            raise RuntimeError(f"{row.get('manifest_id')}: probe row not needs_suppress_build")
        if row.get("target_legal") != "1":
            raise RuntimeError(f"{row.get('manifest_id')}: probe target not legal")

    for row in suppress_rows:
        if row.get("status_after") != "ready_full_schema":
            raise RuntimeError(f"{row.get('manifest_id')}: suppress row not ready_full_schema")
        if row.get("ready_full_schema_after") != "1":
            raise RuntimeError(f"{row.get('manifest_id')}: suppress row ready_full_schema_after != 1")
        if ready_bucket(row) != "trainable_rank_11_50" and row.get("bucket_after") != "trainable_rank_11_50":
            raise RuntimeError(f"{row.get('manifest_id')}: suppress row not trainable bucket")

    manifest_by_id = index_by_id(manifest_rows, "manifest")

    for mid in legacy_ids:
        if mid not in manifest_by_id:
            raise RuntimeError(f"legacy id missing from manifest: {mid}")
        row = manifest_by_id[mid]
        if not is_nondup(row):
            raise RuntimeError(f"{mid}: selected row is duplicate")
        if row.get("status") != "ready_full_schema":
            raise RuntimeError(f"{mid}: expected ready_full_schema before update, got {row.get('status')}")
        if ready_bucket(row) != "trainable_rank_11_50":
            raise RuntimeError(f"{mid}: expected trainable_rank_11_50 before update, got {ready_bucket(row)}")

    for field in COPY_FROM_PROBE + COPY_FROM_SUPPRESS + [
        "legacy_normalization_action",
        "legacy_probe_status_after",
        "legacy_suppress_status_after",
        "legacy_manifest_update_notes",
    ]:
        add_field(fields, field)

    before_trainable = [
        r for r in manifest_rows
        if is_nondup(r)
        and r.get("status") == "ready_full_schema"
        and ready_bucket(r) == "trainable_rank_11_50"
    ]
    before_trainable_complete = [r for r in before_trainable if export_schema_complete(r)]

    update_count = 0
    update_preview: list[dict[str, str]] = []

    for row in manifest_rows:
        mid = row.get("manifest_id", "").strip()
        if mid not in suppress_by_id:
            continue

        probe = probe_by_id[mid]
        suppress = suppress_by_id[mid]

        before_missing = [f for f in REQUIRED_EXPORT_FIELDS if is_blank(row.get(f))]

        for field in COPY_FROM_PROBE:
            if field in probe and not is_blank(probe.get(field)):
                row[field] = probe[field]

        for field in COPY_FROM_SUPPRESS:
            if field in suppress and not is_blank(suppress.get(field)):
                row[field] = suppress[field]

        row["status"] = "ready_full_schema"
        row["ready_bucket"] = "trainable_rank_11_50"
        if "bucket" in row:
            row["bucket"] = "trainable_rank_11_50"

        row["legacy_normalization_action"] = "merged_legacy_probe_and_suppress_fill"
        row["legacy_probe_status_after"] = probe.get("status_after", "")
        row["legacy_suppress_status_after"] = suppress.get("status_after", "")
        row["legacy_manifest_update_notes"] = "legacy_trainable_row_schema_completed_from_current_best_probe_and_suppress_fill"

        after_missing = [f for f in REQUIRED_EXPORT_FIELDS if is_blank(row.get(f))]
        if after_missing:
            raise RuntimeError(f"{mid}: still missing export fields after update: {after_missing}")

        update_count += 1
        update_preview.append({
            "manifest_id": mid,
            "before_missing": json.dumps(before_missing),
            "after_missing": json.dumps(after_missing),
            "target_action": row.get("target_action", ""),
            "suppress_rc": row.get("suppress_rc", ""),
            "suppress_prob": row.get("suppress_prob", ""),
            "suppress_count": row.get("suppress_count", ""),
        })

    if update_count != args.expected_legacy_rows:
        raise RuntimeError(f"expected {args.expected_legacy_rows} updated rows, got {update_count}")

    after_nondup = [r for r in manifest_rows if is_nondup(r)]
    after_status_counts = Counter(r.get("status", "") for r in after_nondup)
    after_ready = [r for r in after_nondup if r.get("status") == "ready_full_schema"]
    after_bucket_counts = Counter(ready_bucket(r) for r in after_ready)
    after_trainable = [
        r for r in after_nondup
        if r.get("status") == "ready_full_schema"
        and ready_bucket(r) == "trainable_rank_11_50"
    ]
    after_trainable_complete = [r for r in after_trainable if export_schema_complete(r)]

    if after_status_counts["ready_full_schema"] != 133:
        raise RuntimeError(f"ready_full_schema count changed unexpectedly: {after_status_counts}")
    if after_bucket_counts["trainable_rank_11_50"] != 44:
        raise RuntimeError(f"trainable bucket count changed unexpectedly: {after_bucket_counts}")
    if len(after_trainable_complete) != 44:
        missing_ids = [
            r.get("manifest_id", "")
            for r in after_trainable
            if not export_schema_complete(r)
        ]
        raise RuntimeError(f"expected 44 export-schema-complete trainable rows, got {len(after_trainable_complete)} missing={missing_ids}")

    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(manifest_rows)

    lines = [
        "# Teacher-divergence legacy suppress manifest update",
        "",
        "## Branch",
        "",
        "`exp/15x15-teacher-divergence-legacy-suppress-manifest-update`",
        "",
        "## Scope",
        "",
        "- Merges 9 legacy trainable current_best probe/suppress fill rows into a new normalized manifest.",
        "- Keeps status and bucket counts stable.",
        "- Completes export schema for all `trainable_rank_11_50` rows.",
        "- Does not modify the original round2 manifest in place.",
        "- No training.",
        "- No checkpoint save.",
        "- No C export.",
        "- No public benchmark.",
        "- No promotion.",
        "",
        "## Inputs",
        "",
        f"- manifest: `{args.manifest}`",
        f"- legacy probe fill CSV: `{args.legacy_probe_fill_csv}`",
        f"- legacy suppress fill CSV: `{args.legacy_suppress_fill_csv}`",
        "",
        "## Summary",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| manifest rows | {len(manifest_rows)} |",
        f"| non-duplicate rows | {len(after_nondup)} |",
        f"| legacy rows updated | {update_count} |",
        f"| trainable ready rows before | {len(before_trainable)} |",
        f"| trainable export-schema-complete before | {len(before_trainable_complete)} |",
        f"| trainable ready rows after | {len(after_trainable)} |",
        f"| trainable export-schema-complete after | {len(after_trainable_complete)} |",
        "",
        "## Status counts after update",
        "",
        "| status | rows |",
        "|---|---:|",
    ]

    for key, value in after_status_counts.most_common():
        lines.append(f"| {key} | {value} |")

    lines.extend([
        "",
        "## Ready bucket counts after update",
        "",
        "| ready_bucket | rows |",
        "|---|---:|",
    ])

    for key, value in after_bucket_counts.most_common():
        lines.append(f"| {key} | {value} |")

    lines.extend([
        "",
        "## Updated legacy rows",
        "",
        "| manifest_id | before_missing | target_action | suppress_rc | suppress_prob | suppress_count |",
        "|---|---|---:|---|---:|---:|",
    ])

    for r in update_preview:
        lines.append(
            f"| {r['manifest_id']} | `{r['before_missing']}` | {r['target_action']} | `{r['suppress_rc']}` | {r['suppress_prob']} | {r['suppress_count']} |"
        )

    lines.extend([
        "",
        "## Output",
        "",
        f"- normalized manifest: `{args.out_csv}`",
        f"- report: `{args.out_report}`",
        "",
        "## Decision",
        "",
        "The normalized manifest is ready for a 44-row dry-run export validation.",
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

    print("manifest_rows:", len(manifest_rows))
    print("non_duplicate_rows:", len(after_nondup))
    print("legacy_rows_updated:", update_count)
    print("status_counts_after:", json.dumps(dict(after_status_counts), sort_keys=True))
    print("ready_bucket_counts_after:", json.dumps(dict(after_bucket_counts), sort_keys=True))
    print("trainable_export_schema_complete_before:", len(before_trainable_complete))
    print("trainable_export_schema_complete_after:", len(after_trainable_complete))
    print("out_csv:", args.out_csv)
    print("out_report:", args.out_report)
    print("no training; no checkpoint saved")


if __name__ == "__main__":
    main()
