from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Merge current_best probe fill and suppress build fill results into expanded candidate manifest."
    )
    ap.add_argument(
        "--manifest",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_expanded_candidate_manifest.csv"),
    )
    ap.add_argument(
        "--probe-fill",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_current_best_probe_fill.csv"),
    )
    ap.add_argument(
        "--suppress-fill",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_suppress_build_fill.csv"),
    )
    ap.add_argument(
        "--out-csv",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_expanded_candidate_manifest_with_fills.csv"),
    )
    ap.add_argument(
        "--out-report",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_expanded_candidate_manifest_with_fills_report.md"),
    )
    return ap.parse_args()


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader), list(reader.fieldnames or [])


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def by_manifest_id(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row["manifest_id"]: row for row in rows}


def count_by(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
    out: dict[str, int] = {}
    for row in rows:
        value = str(row.get(key, ""))
        out[value] = out.get(value, 0) + 1
    return dict(sorted(out.items(), key=lambda kv: (-kv[1], kv[0])))


def append_note(old: str, note: str) -> str:
    parts = [p for p in str(old or "").split(",") if p]
    if note and note not in parts:
        parts.append(note)
    return ",".join(parts)


def update_ready_row(
    row: dict[str, Any],
    probe: dict[str, str],
    suppress: dict[str, str],
) -> None:
    row["status"] = "ready_full_schema"
    row["bucket"] = suppress["bucket_after"]

    row["rank_prob_available"] = "1"
    row["suppress_available"] = "1"
    row["needs_current_best_probe"] = "0"
    row["needs_suppress_build"] = "0"
    row["needs_rapfi_requery"] = "0"
    row["needs_board_join"] = "0"

    row["before_target_rank"] = probe["before_target_rank"]
    row["before_target_prob"] = probe["before_target_prob"]
    row["current_best_direct_rc"] = probe["current_best_direct_rc"]
    row["current_best_direct_move"] = probe["current_best_direct_rc"]

    row["suppress_count"] = suppress["suppress_count"]
    row["suppress_rcs"] = suppress["suppress_rcs"]

    row["skip_reason"] = ""
    row["validation_notes"] = append_note(row.get("validation_notes", ""), "current_best_probe_and_suppress_fill_applied")


def update_excluded_row(
    row: dict[str, Any],
    probe: dict[str, str],
    suppress: dict[str, str],
) -> None:
    row["status"] = "skipped_invalid"
    row["bucket"] = "unknown_rank"

    row["rank_prob_available"] = "0"
    row["suppress_available"] = "0"
    row["needs_current_best_probe"] = "0"
    row["needs_suppress_build"] = "0"
    row["needs_rapfi_requery"] = "0"

    row["before_target_rank"] = ""
    row["before_target_prob"] = probe.get("before_target_prob", "")
    row["current_best_direct_rc"] = probe.get("current_best_direct_rc", "")
    row["current_best_direct_move"] = probe.get("current_best_direct_rc", "")

    row["suppress_count"] = ""
    row["suppress_rcs"] = ""

    row["skip_reason"] = suppress.get("exclude_reason", "excluded")
    row["validation_notes"] = append_note(row.get("validation_notes", ""), "excluded_after_probe_fill")


def update_manifest(
    manifest_rows: list[dict[str, Any]],
    probe_rows: list[dict[str, str]],
    suppress_rows: list[dict[str, str]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    probe_by_id = by_manifest_id(probe_rows)
    suppress_by_id = by_manifest_id(suppress_rows)

    update_log: list[dict[str, Any]] = []
    rows_by_id = {row["manifest_id"]: row for row in manifest_rows}

    for manifest_id, suppress in suppress_by_id.items():
        row = rows_by_id.get(manifest_id)
        probe = probe_by_id.get(manifest_id)

        if row is None:
            update_log.append(
                {
                    "manifest_id": manifest_id,
                    "action": "missing_manifest_row",
                    "status_after": suppress.get("status_after", ""),
                    "bucket_after": suppress.get("bucket_after", ""),
                }
            )
            continue

        if probe is None:
            update_log.append(
                {
                    "manifest_id": manifest_id,
                    "action": "missing_probe_fill_row",
                    "status_after": suppress.get("status_after", ""),
                    "bucket_after": suppress.get("bucket_after", ""),
                }
            )
            continue

        old_status = row.get("status", "")
        old_bucket = row.get("bucket", "")
        fill_status = suppress.get("status_after", "")

        if fill_status == "ready_full_schema":
            update_ready_row(row, probe, suppress)
            action = "promoted_ready_full_schema"
        elif fill_status.startswith("excluded_"):
            update_excluded_row(row, probe, suppress)
            action = "excluded_skipped_invalid"
        else:
            action = "left_unchanged_unexpected_status"

        update_log.append(
            {
                "manifest_id": manifest_id,
                "action": action,
                "old_status": old_status,
                "new_status": row.get("status", ""),
                "old_bucket": old_bucket,
                "new_bucket": row.get("bucket", ""),
                "fill_status": fill_status,
                "fill_bucket": suppress.get("bucket_after", ""),
            }
        )

    return manifest_rows, update_log


def write_update_log_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = [
        "manifest_id",
        "action",
        "old_status",
        "new_status",
        "old_bucket",
        "new_bucket",
        "fill_status",
        "fill_bucket",
        "status_after",
        "bucket_after",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def write_report(
    path: Path,
    args: argparse.Namespace,
    rows_before: list[dict[str, Any]],
    rows_after: list[dict[str, Any]],
    update_log: list[dict[str, Any]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    nondup_before = [r for r in rows_before if r.get("status") != "duplicate"]
    nondup_after = [r for r in rows_after if r.get("status") != "duplicate"]
    ready_after = [r for r in nondup_after if r.get("status") == "ready_full_schema"]

    promoted = [r for r in update_log if r.get("action") == "promoted_ready_full_schema"]
    excluded = [r for r in update_log if r.get("action") == "excluded_skipped_invalid"]

    lines: list[str] = []
    lines += ["# Teacher-divergence expanded manifest with fills report", ""]
    lines += ["## Branch", "", "`exp/15x15-teacher-divergence-manifest-update-with-fills`", ""]
    lines += ["## Scope", ""]
    lines += [
        "- Manifest update only.",
        "- Merges current_best probe fill and suppress build fill outputs.",
        "- No training.",
        "- No checkpoint save.",
        "- No C export.",
        "- No public benchmark.",
        "- No promotion.",
        "",
    ]

    lines += ["## Inputs", ""]
    lines += [
        f"- base manifest: `{args.manifest}`",
        f"- probe fill: `{args.probe_fill}`",
        f"- suppress fill: `{args.suppress_fill}`",
        "",
    ]

    lines += ["## Update summary", ""]
    lines += ["| metric | value |", "|---|---:|"]
    lines += [
        f"| total manifest rows | {len(rows_after)} |",
        f"| non-duplicate rows | {len(nondup_after)} |",
        f"| update actions | {len(update_log)} |",
        f"| promoted ready_full_schema | {len(promoted)} |",
        f"| excluded/skipped invalid | {len(excluded)} |",
        "",
    ]

    lines += ["## Status counts before", ""]
    lines += ["| status | rows |", "|---|---:|"]
    for key, n in count_by(rows_before, "status").items():
        lines.append(f"| {key} | {n} |")
    lines.append("")

    lines += ["## Status counts after", ""]
    lines += ["| status | rows |", "|---|---:|"]
    for key, n in count_by(rows_after, "status").items():
        lines.append(f"| {key} | {n} |")
    lines.append("")

    lines += ["## Bucket counts after for non-duplicate rows", ""]
    lines += ["| bucket | rows |", "|---|---:|"]
    for key, n in count_by(nondup_after, "bucket").items():
        lines.append(f"| {key} | {n} |")
    lines.append("")

    lines += ["## Ready full-schema bucket counts after", ""]
    lines += ["| bucket | rows |", "|---|---:|"]
    for key, n in count_by(ready_after, "bucket").items():
        lines.append(f"| {key} | {n} |")
    lines.append("")

    lines += ["## Update actions", ""]
    lines += ["| action | rows |", "|---|---:|"]
    for key, n in count_by(update_log, "action").items():
        lines.append(f"| {key} | {n} |")
    lines.append("")

    lines += ["## Interpretation", ""]
    lines += [
        "The current_best probe fill and suppress build fill have been merged into an updated manifest.",
        "",
        "This increases ready_full_schema rows for diagnostics, but it does not create a training dataset.",
        "",
        "Protected top10 rows remain eval/protection only. Tail rank_gt50 rows remain diagnostic-only. The trainable rank 11-50 bucket is still far below the minimum sample target for training.",
        "",
    ]

    lines += ["## Decision", ""]
    lines += [
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
    ]

    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    args = parse_args()

    manifest_rows, manifest_fields = read_csv(args.manifest)
    probe_rows, _ = read_csv(args.probe_fill)
    suppress_rows, _ = read_csv(args.suppress_fill)

    rows_before = [dict(r) for r in manifest_rows]
    rows_after, update_log = update_manifest(manifest_rows, probe_rows, suppress_rows)

    write_csv(args.out_csv, rows_after, manifest_fields)
    log_path = args.out_csv.with_name(args.out_csv.stem + "_update_log.csv")
    write_update_log_csv(log_path, update_log)
    write_report(args.out_report, args, rows_before, rows_after, update_log)

    print("manifest_rows:", len(rows_after))
    print("non_duplicate_rows:", sum(1 for r in rows_after if r.get("status") != "duplicate"))
    print("update_actions:", json.dumps(count_by(update_log, "action"), sort_keys=True))
    print("status_counts_after:", json.dumps(count_by(rows_after, "status"), sort_keys=True))
    ready = [r for r in rows_after if r.get("status") == "ready_full_schema" and r.get("duplicate_of", "") == ""]
    print("ready_bucket_counts_after:", json.dumps(count_by(ready, "bucket"), sort_keys=True))
    print("out_csv:", args.out_csv)
    print("update_log:", log_path)
    print("out_report:", args.out_report)
    print("no training; no checkpoint saved")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
