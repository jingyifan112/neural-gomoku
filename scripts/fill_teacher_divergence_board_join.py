from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


OUT_FIELDS = [
    "manifest_id",
    "old_status",
    "new_status",
    "source_class",
    "case_id",
    "game_number",
    "move_count",
    "target_rc",
    "join_status",
    "join_strength",
    "match_count",
    "unique_board_hash_count",
    "matched_board_hash",
    "matched_sources",
    "matched_keys",
    "board_available_after",
    "needs_board_join_after",
    "needs_current_best_probe_after",
    "needs_rapfi_requery_after",
    "excluded",
    "exclude_reason",
    "notes",
]


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Conservative board join fill from board join audit results."
    )
    ap.add_argument(
        "--manifest",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_expanded_candidate_manifest_with_fills.csv"),
    )
    ap.add_argument(
        "--board-join-audit",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_board_join_audit.csv"),
    )
    ap.add_argument(
        "--out-csv",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_board_join_fill.csv"),
    )
    ap.add_argument(
        "--out-report",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_board_join_fill_report.md"),
    )
    return ap.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def boolish(value: Any) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def by_manifest_id(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row["manifest_id"]: row for row in rows}


def classify_fill(manifest_row: dict[str, str], audit_row: dict[str, str]) -> dict[str, Any]:
    join_status = audit_row.get("join_status", "")
    unique_hash_count = int(audit_row.get("unique_board_hash_count", "0") or 0)
    matched_hash = audit_row.get("matched_board_hash", "")

    base = {
        "manifest_id": audit_row["manifest_id"],
        "old_status": manifest_row.get("status", ""),
        "source_class": audit_row.get("source_class", ""),
        "case_id": audit_row.get("case_id", ""),
        "game_number": audit_row.get("game_number", ""),
        "move_count": audit_row.get("move_count", ""),
        "target_rc": audit_row.get("target_rc", ""),
        "join_status": join_status,
        "join_strength": audit_row.get("join_strength", ""),
        "match_count": audit_row.get("match_count", ""),
        "unique_board_hash_count": audit_row.get("unique_board_hash_count", ""),
        "matched_board_hash": matched_hash,
        "matched_sources": audit_row.get("matched_sources", ""),
        "matched_keys": audit_row.get("matched_keys", ""),
    }

    if join_status == "ambiguous_join":
        base.update(
            {
                "new_status": "needs_board_join",
                "board_available_after": 0,
                "needs_board_join_after": 1,
                "needs_current_best_probe_after": 0,
                "needs_rapfi_requery_after": 0,
                "excluded": 1,
                "exclude_reason": "ambiguous_join",
                "notes": "not filled because multiple board hashes matched",
            }
        )
        return base

    if join_status == "no_join":
        base.update(
            {
                "new_status": "needs_board_join",
                "board_available_after": 0,
                "needs_board_join_after": 1,
                "needs_current_best_probe_after": 0,
                "needs_rapfi_requery_after": 0,
                "excluded": 1,
                "exclude_reason": "no_join",
                "notes": "not filled because no board source matched",
            }
        )
        return base

    if join_status != "unique_join" or unique_hash_count != 1 or not matched_hash:
        base.update(
            {
                "new_status": "needs_board_join",
                "board_available_after": 0,
                "needs_board_join_after": 1,
                "needs_current_best_probe_after": 0,
                "needs_rapfi_requery_after": 0,
                "excluded": 1,
                "exclude_reason": "not_conservative_unique_join",
                "notes": "not filled because unique join criteria failed",
            }
        )
        return base

    side_available = boolish(manifest_row.get("side_available", "0"))
    target_available = boolish(manifest_row.get("target_available", "0"))
    teacher_eval_available = boolish(manifest_row.get("teacher_eval_available", "0"))
    rank_prob_available = boolish(manifest_row.get("rank_prob_available", "0"))
    suppress_available = boolish(manifest_row.get("suppress_available", "0"))

    if not side_available or not target_available:
        new_status = "skipped_invalid"
        needs_current_best_probe = 0
        needs_rapfi_requery = 0
        note = "board joined but side/target missing"
    elif not teacher_eval_available:
        new_status = "needs_rapfi_requery"
        needs_current_best_probe = 0
        needs_rapfi_requery = 1
        note = "board joined; teacher eval missing"
    elif not rank_prob_available:
        new_status = "needs_current_best_probe"
        needs_current_best_probe = 1
        needs_rapfi_requery = 0
        note = "board joined; rank/prob probe needed"
    elif not suppress_available:
        new_status = "needs_suppress_build"
        needs_current_best_probe = 0
        needs_rapfi_requery = 0
        note = "board joined; suppress build needed"
    else:
        new_status = "ready_full_schema"
        needs_current_best_probe = 0
        needs_rapfi_requery = 0
        note = "board joined; row already complete"

    base.update(
        {
            "new_status": new_status,
            "board_available_after": 1,
            "needs_board_join_after": 0,
            "needs_current_best_probe_after": needs_current_best_probe,
            "needs_rapfi_requery_after": needs_rapfi_requery,
            "excluded": 0,
            "exclude_reason": "",
            "notes": note,
        }
    )
    return base


def count_by(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
    out: dict[str, int] = {}
    for row in rows:
        value = str(row.get(key, ""))
        out[value] = out.get(value, 0) + 1
    return dict(sorted(out.items(), key=lambda kv: (-kv[1], kv[0])))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUT_FIELDS, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in OUT_FIELDS})


def write_report(path: Path, args: argparse.Namespace, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    filled = [r for r in rows if str(r.get("excluded", "")) == "0"]
    excluded = [r for r in rows if str(r.get("excluded", "")) == "1"]

    lines: list[str] = []
    lines += ["# Teacher-divergence board join fill report", ""]
    lines += ["## Branch", "", "`exp/15x15-teacher-divergence-board-join-fill`", ""]
    lines += ["## Scope", ""]
    lines += [
        "- Board join fill only.",
        "- Uses conservative `unique_join` rows from board join audit.",
        "- Does not update the manifest directly.",
        "- Does not run current_best probe.",
        "- No training.",
        "- No checkpoint save.",
        "- No C export.",
        "- No public benchmark.",
        "- No promotion.",
        "",
    ]

    lines += ["## Inputs", ""]
    lines += [
        f"- manifest: `{args.manifest}`",
        f"- board_join_audit: `{args.board_join_audit}`",
        "",
    ]

    lines += ["## Summary", ""]
    lines += ["| metric | value |", "|---|---:|"]
    lines += [
        f"| input audit rows | {len(rows)} |",
        f"| filled rows | {len(filled)} |",
        f"| excluded/unfilled rows | {len(excluded)} |",
        "",
    ]

    lines += ["## New status counts", ""]
    lines += ["| new_status | rows |", "|---|---:|"]
    for key, n in count_by(rows, "new_status").items():
        lines.append(f"| {key} | {n} |")
    lines.append("")

    lines += ["## Join status counts", ""]
    lines += ["| join_status | rows |", "|---|---:|"]
    for key, n in count_by(rows, "join_status").items():
        lines.append(f"| {key} | {n} |")
    lines.append("")

    lines += ["## Exclusion reasons", ""]
    lines += ["| exclude_reason | rows |", "|---|---:|"]
    for key, n in count_by(excluded, "exclude_reason").items():
        lines.append(f"| {key} | {n} |")
    lines.append("")

    lines += ["## Filled status by join strength", ""]
    lines += ["| join_strength | new_status | rows |", "|---|---|---:|"]
    combo: dict[tuple[str, str], int] = {}
    for row in filled:
        key = (row.get("join_strength", ""), row.get("new_status", ""))
        combo[key] = combo.get(key, 0) + 1
    for (strength, status), n in sorted(combo.items(), key=lambda kv: (kv[0][0], kv[0][1])):
        lines.append(f"| {strength or 'none'} | {status} | {n} |")
    lines.append("")

    lines += ["## Filled rows preview", ""]
    lines += ["| manifest_id | new_status | join_strength | matched_hash | notes |", "|---|---|---|---|---|"]
    for row in filled[:60]:
        lines.append(
            f"| {row['manifest_id']} | {row['new_status']} | {row['join_strength']} | "
            f"`{row['matched_board_hash']}` | {row['notes']} |"
        )
    if len(filled) > 60:
        lines.append(f"| ... | ... | ... | ... | {len(filled) - 60} more |")
    lines.append("")

    lines += ["## Interpretation", ""]
    lines += [
        "Rows filled here have a unique board hash from the board join audit.",
        "",
        "Most filled rows should proceed to current_best rank/prob probing, not training.",
        "",
        "Rows excluded because of ambiguous or missing joins remain incomplete and must not be silently included in any future dataset.",
        "",
    ]

    lines += ["## Decision", ""]
    lines += [
        "No manifest update in this branch.",
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

    manifest_rows = read_csv(args.manifest)
    audit_rows = read_csv(args.board_join_audit)
    manifest_by_id = by_manifest_id(manifest_rows)

    out_rows: list[dict[str, Any]] = []
    for audit_row in audit_rows:
        manifest_id = audit_row["manifest_id"]
        manifest_row = manifest_by_id.get(manifest_id)
        if manifest_row is None:
            raise RuntimeError(f"manifest row not found for {manifest_id}")
        out_rows.append(classify_fill(manifest_row, audit_row))

    write_csv(args.out_csv, out_rows)
    write_report(args.out_report, args, out_rows)

    print("input_rows:", len(out_rows))
    print("filled_rows:", sum(1 for r in out_rows if str(r.get("excluded")) == "0"))
    print("excluded_rows:", sum(1 for r in out_rows if str(r.get("excluded")) == "1"))
    print("new_status_counts:", json.dumps(count_by(out_rows, "new_status"), sort_keys=True))
    print("join_status_counts:", json.dumps(count_by(out_rows, "join_status"), sort_keys=True))
    print("exclude_reason_counts:", json.dumps(count_by([r for r in out_rows if str(r.get("excluded")) == "1"], "exclude_reason"), sort_keys=True))
    print("out_csv:", args.out_csv)
    print("out_report:", args.out_report)
    print("no manifest update; no training; no checkpoint saved")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
