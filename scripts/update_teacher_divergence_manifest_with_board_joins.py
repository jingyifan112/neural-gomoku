from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


ADDED_FIELDS = [
    "board_join_status",
    "board_join_strength",
    "board_join_match_count",
    "board_join_unique_board_hash_count",
    "board_join_matched_sources",
    "board_join_matched_keys",
]


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Merge conservative board join fill results into expanded teacher-divergence manifest."
    )
    ap.add_argument(
        "--manifest",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_expanded_candidate_manifest_with_fills.csv"),
    )
    ap.add_argument(
        "--board-join-fill",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_board_join_fill.csv"),
    )
    ap.add_argument(
        "--out-csv",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_expanded_candidate_manifest_with_board_joins.csv"),
    )
    ap.add_argument(
        "--out-report",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_expanded_candidate_manifest_with_board_joins_report.md"),
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


def boolish(value: Any) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


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


def ensure_fields(fields: list[str]) -> list[str]:
    out = list(fields)
    for field in ADDED_FIELDS:
        if field not in out:
            out.append(field)
    return out


def apply_board_join(row: dict[str, Any], fill: dict[str, str]) -> None:
    row["status"] = fill["new_status"]

    row["board_available"] = "1"
    row["board_hash"] = fill["matched_board_hash"]

    row["needs_board_join"] = "0"
    row["needs_current_best_probe"] = fill["needs_current_best_probe_after"]
    row["needs_rapfi_requery"] = fill["needs_rapfi_requery_after"]

    # Board join alone does not create rank/prob or suppress fields.
    if fill["new_status"] == "needs_current_best_probe":
        row["rank_prob_available"] = "0"
        row["suppress_available"] = "0"
        row["needs_suppress_build"] = "0"
    elif fill["new_status"] == "needs_rapfi_requery":
        row["rank_prob_available"] = "0"
        row["suppress_available"] = "0"
        row["needs_suppress_build"] = "0"
    elif fill["new_status"] == "needs_suppress_build":
        row["rank_prob_available"] = "1"
        row["suppress_available"] = "0"
        row["needs_suppress_build"] = "1"

    row["board_join_status"] = fill["join_status"]
    row["board_join_strength"] = fill["join_strength"]
    row["board_join_match_count"] = fill["match_count"]
    row["board_join_unique_board_hash_count"] = fill["unique_board_hash_count"]
    row["board_join_matched_sources"] = fill["matched_sources"]
    row["board_join_matched_keys"] = fill["matched_keys"]

    row["validation_notes"] = append_note(row.get("validation_notes", ""), "board_join_fill_applied")


def retain_unfilled(row: dict[str, Any], fill: dict[str, str]) -> None:
    # Keep manifest incomplete; record why it was not joined.
    row["board_join_status"] = fill["join_status"]
    row["board_join_strength"] = fill["join_strength"]
    row["board_join_match_count"] = fill["match_count"]
    row["board_join_unique_board_hash_count"] = fill["unique_board_hash_count"]
    row["board_join_matched_sources"] = fill["matched_sources"]
    row["board_join_matched_keys"] = fill["matched_keys"]

    reason = fill.get("exclude_reason", "board_join_not_filled")
    row["validation_notes"] = append_note(row.get("validation_notes", ""), f"board_join_unfilled_{reason}")


def update_manifest(
    manifest_rows: list[dict[str, Any]],
    fill_rows: list[dict[str, str]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows_by_id = {row["manifest_id"]: row for row in manifest_rows}
    update_log: list[dict[str, Any]] = []

    for fill in fill_rows:
        manifest_id = fill["manifest_id"]
        row = rows_by_id.get(manifest_id)
        if row is None:
            update_log.append(
                {
                    "manifest_id": manifest_id,
                    "action": "missing_manifest_row",
                    "old_status": "",
                    "new_status": fill.get("new_status", ""),
                    "join_status": fill.get("join_status", ""),
                    "exclude_reason": fill.get("exclude_reason", ""),
                }
            )
            continue

        old_status = row.get("status", "")
        old_board_available = row.get("board_available", "")
        old_board_hash = row.get("board_hash", "")

        if str(fill.get("excluded", "")) == "0":
            apply_board_join(row, fill)
            action = "applied_board_join"
        else:
            retain_unfilled(row, fill)
            action = f"retained_unfilled_{fill.get('exclude_reason', 'unknown')}"

        update_log.append(
            {
                "manifest_id": manifest_id,
                "action": action,
                "old_status": old_status,
                "new_status": row.get("status", ""),
                "old_board_available": old_board_available,
                "new_board_available": row.get("board_available", ""),
                "old_board_hash": old_board_hash,
                "new_board_hash": row.get("board_hash", ""),
                "join_status": fill.get("join_status", ""),
                "join_strength": fill.get("join_strength", ""),
                "exclude_reason": fill.get("exclude_reason", ""),
            }
        )

    return manifest_rows, update_log


def write_update_log_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = [
        "manifest_id",
        "action",
        "old_status",
        "new_status",
        "old_board_available",
        "new_board_available",
        "old_board_hash",
        "new_board_hash",
        "join_status",
        "join_strength",
        "exclude_reason",
    ]
    write_csv(path, rows, fields)


def write_report(
    path: Path,
    args: argparse.Namespace,
    before: list[dict[str, Any]],
    after: list[dict[str, Any]],
    update_log: list[dict[str, Any]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    nondup_after = [r for r in after if r.get("status") != "duplicate"]
    applied = [r for r in update_log if r.get("action") == "applied_board_join"]
    retained = [r for r in update_log if str(r.get("action", "")).startswith("retained_unfilled_")]

    lines: list[str] = []
    lines += ["# Teacher-divergence expanded manifest with board joins report", ""]
    lines += ["## Branch", "", "`exp/15x15-teacher-divergence-manifest-update-with-board-joins`", ""]
    lines += ["## Scope", ""]
    lines += [
        "- Manifest update only.",
        "- Merges conservative board join fill results.",
        "- Does not run current_best probe.",
        "- Does not run Rapfi requery.",
        "- Does not build suppress candidates.",
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
        f"- board join fill: `{args.board_join_fill}`",
        "",
    ]

    lines += ["## Update summary", ""]
    lines += ["| metric | value |", "|---|---:|"]
    lines += [
        f"| total manifest rows | {len(after)} |",
        f"| non-duplicate rows | {len(nondup_after)} |",
        f"| update log rows | {len(update_log)} |",
        f"| applied board joins | {len(applied)} |",
        f"| retained unfilled rows | {len(retained)} |",
        "",
    ]

    lines += ["## Status counts before", ""]
    lines += ["| status | rows |", "|---|---:|"]
    for key, n in count_by(before, "status").items():
        lines.append(f"| {key} | {n} |")
    lines.append("")

    lines += ["## Status counts after", ""]
    lines += ["| status | rows |", "|---|---:|"]
    for key, n in count_by(after, "status").items():
        lines.append(f"| {key} | {n} |")
    lines.append("")

    lines += ["## Non-duplicate status counts after", ""]
    lines += ["| status | rows |", "|---|---:|"]
    for key, n in count_by(nondup_after, "status").items():
        lines.append(f"| {key} | {n} |")
    lines.append("")

    lines += ["## Update actions", ""]
    lines += ["| action | rows |", "|---|---:|"]
    for key, n in count_by(update_log, "action").items():
        lines.append(f"| {key} | {n} |")
    lines.append("")

    lines += ["## Join strength for applied rows", ""]
    lines += ["| join_strength | rows |", "|---|---:|"]
    for key, n in count_by(applied, "join_strength").items():
        lines.append(f"| {key or 'none'} | {n} |")
    lines.append("")

    lines += ["## Interpretation", ""]
    lines += [
        "The manifest now records conservative board joins for unique-join rows.",
        "",
        "Most newly joined rows now require current_best rank/prob probing. They are not training-ready.",
        "",
        "Rows retained as no_join or ambiguous_join remain incomplete and must not be included in future training datasets.",
        "",
    ]

    lines += ["## Decision", ""]
    lines += [
        "No current_best probe on this branch.",
        "",
        "No Rapfi requery on this branch.",
        "",
        "No suppress build on this branch.",
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
    ]

    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    args = parse_args()

    manifest_rows, manifest_fields = read_csv(args.manifest)
    fill_rows, _ = read_csv(args.board_join_fill)

    before = [dict(r) for r in manifest_rows]
    after, update_log = update_manifest(manifest_rows, fill_rows)

    out_fields = ensure_fields(manifest_fields)
    write_csv(args.out_csv, after, out_fields)

    update_log_path = args.out_csv.with_name(args.out_csv.stem + "_update_log.csv")
    write_update_log_csv(update_log_path, update_log)

    write_report(args.out_report, args, before, after, update_log)

    nondup_after = [r for r in after if r.get("status") != "duplicate"]
    print("manifest_rows:", len(after))
    print("non_duplicate_rows:", len(nondup_after))
    print("update_actions:", json.dumps(count_by(update_log, "action"), sort_keys=True))
    print("status_counts_after:", json.dumps(count_by(after, "status"), sort_keys=True))
    print("non_duplicate_status_counts_after:", json.dumps(count_by(nondup_after, "status"), sort_keys=True))
    print("out_csv:", args.out_csv)
    print("update_log:", update_log_path)
    print("out_report:", args.out_report)
    print("no probe; no requery; no training; no checkpoint saved")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
