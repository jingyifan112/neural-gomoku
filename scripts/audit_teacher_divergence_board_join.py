from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from build_teacher_divergence_expanded_manifest import (
    board_from_row,
    board_hash,
    first_nonempty,
    load_rows,
    normalize_board,
    normalize_rc_cell,
    parse_rc,
)


BOARD_SOURCE_PATHS = [
    "analysis/public_benchmark_eval/corpus8_selected_board_snapshots.json",
    "analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected.json",
    "analysis/public_benchmark_eval/rapfi_teacher_policy_margin_dataset_corpus8_selected.json",
    "analysis/integration_eval/teacher_divergence_retention_safety_v3_dataset.json",
    "analysis/integration_eval/teacher_divergence_retention_clean_v2_dataset.json",
    "analysis/integration_eval/teacher_divergence_retention_dataset.json",
]

OUT_FIELDS = [
    "manifest_id",
    "primary_source_path",
    "source_class",
    "case_id",
    "source",
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
    "notes",
]


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Audit possible board joins for teacher-divergence manifest rows marked needs_board_join."
    )
    ap.add_argument(
        "--manifest",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_expanded_candidate_manifest_with_fills.csv"),
    )
    ap.add_argument(
        "--out-csv",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_board_join_audit.csv"),
    )
    ap.add_argument(
        "--out-report",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_board_join_audit.md"),
    )
    return ap.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def parse_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def row_case_id(row: dict[str, Any]) -> str:
    return parse_text(first_nonempty(row, ["case_id", "id", "name", "position_id"]))


def row_source(row: dict[str, Any]) -> str:
    return parse_text(first_nonempty(row, ["source", "source_file", "source_name", "label_type"]))


def row_game(row: dict[str, Any]) -> str:
    return parse_text(first_nonempty(row, ["game_number", "game", "game_id", "source_game"]))


def row_move(row: dict[str, Any]) -> str:
    return parse_text(first_nonempty(row, ["move_count", "ply", "move_number", "source_ply"]))


def row_target_rc(row: dict[str, Any]) -> str:
    value = first_nonempty(
        row,
        ["target_rc", "teacher_rc", "teacher_target_rc", "target_xy", "teacher_move", "move_rc"],
    )
    return normalize_rc_cell(value)


def manifest_target_rc(row: dict[str, str]) -> str:
    return normalize_rc_cell(row.get("target_rc", ""))


def make_board_record(path: str, raw: dict[str, Any], idx: int) -> dict[str, Any] | None:
    board = normalize_board(board_from_row(raw))
    if board is None:
        return None

    return {
        "source_path": path,
        "row_index": idx,
        "board_hash": board_hash(board),
        "case_id": row_case_id(raw),
        "source": row_source(raw),
        "game_number": row_game(raw),
        "move_count": row_move(raw),
        "target_rc": row_target_rc(raw),
    }


def add_index(index: dict[str, list[dict[str, Any]]], key: str, rec: dict[str, Any]) -> None:
    if not key:
        return
    index.setdefault(key, []).append(rec)


def build_board_index() -> tuple[list[dict[str, Any]], dict[str, list[dict[str, Any]]]]:
    records: list[dict[str, Any]] = []
    index: dict[str, list[dict[str, Any]]] = {}

    for path_str in BOARD_SOURCE_PATHS:
        path = Path(path_str)
        if not path.exists():
            continue
        rows = load_rows(path)
        for i, raw in enumerate(rows):
            rec = make_board_record(path_str, raw, i)
            if rec is None:
                continue
            records.append(rec)

            case_id = rec["case_id"]
            game = rec["game_number"]
            move = rec["move_count"]
            target = rec["target_rc"]

            add_index(index, f"case_id::{case_id}", rec)
            add_index(index, f"game_move_target::{game}::{move}::{target}", rec)
            add_index(index, f"game_move::{game}::{move}", rec)
            add_index(index, f"source_game_move_target::{rec['source']}::{game}::{move}::{target}", rec)

    return records, index


def candidate_keys(row: dict[str, str]) -> list[tuple[str, str]]:
    case_id = parse_text(row.get("case_id", ""))
    source = parse_text(row.get("source", ""))
    game = parse_text(row.get("game_number", ""))
    move = parse_text(row.get("move_count", ""))
    target = manifest_target_rc(row)

    keys: list[tuple[str, str]] = []
    if case_id:
        keys.append(("case_id", f"case_id::{case_id}"))
    if source and game and move and target:
        keys.append(("source_game_move_target", f"source_game_move_target::{source}::{game}::{move}::{target}"))
    if game and move and target:
        keys.append(("game_move_target", f"game_move_target::{game}::{move}::{target}"))
    if game and move:
        keys.append(("game_move", f"game_move::{game}::{move}"))
    return keys


def audit_row(row: dict[str, str], index: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    keys = candidate_keys(row)
    matches_by_id: dict[tuple[str, int], dict[str, Any]] = {}
    matched_keys: list[str] = []

    strongest = ""
    strength_rank = {
        "case_id": 4,
        "source_game_move_target": 3,
        "game_move_target": 2,
        "game_move": 1,
    }

    for key_type, key in keys:
        hits = index.get(key, [])
        if hits:
            matched_keys.append(f"{key_type}:{key}")
            if not strongest or strength_rank[key_type] > strength_rank.get(strongest, 0):
                strongest = key_type
        for hit in hits:
            matches_by_id[(hit["source_path"], hit["row_index"])] = hit

    matches = list(matches_by_id.values())
    hashes = sorted({m["board_hash"] for m in matches if m["board_hash"]})

    if not matches:
        status = "no_join"
        matched_hash = ""
        notes = "no board source match"
    elif len(hashes) == 1:
        status = "unique_join"
        matched_hash = hashes[0]
        notes = "unique board hash matched"
    else:
        status = "ambiguous_join"
        matched_hash = ""
        notes = "multiple board hashes matched"

    return {
        "manifest_id": row["manifest_id"],
        "primary_source_path": row["primary_source_path"],
        "source_class": row["source_class"],
        "case_id": row.get("case_id", ""),
        "source": row.get("source", ""),
        "game_number": row.get("game_number", ""),
        "move_count": row.get("move_count", ""),
        "target_rc": row.get("target_rc", ""),
        "join_status": status,
        "join_strength": strongest,
        "match_count": len(matches),
        "unique_board_hash_count": len(hashes),
        "matched_board_hash": matched_hash,
        "matched_sources": json.dumps(sorted({m["source_path"] for m in matches}), ensure_ascii=False),
        "matched_keys": json.dumps(matched_keys, ensure_ascii=False),
        "notes": notes,
    }


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


def write_report(
    path: Path,
    manifest_rows: list[dict[str, str]],
    selected: list[dict[str, str]],
    board_records: list[dict[str, Any]],
    audit_rows: list[dict[str, Any]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    unique_join = [r for r in audit_rows if r["join_status"] == "unique_join"]
    ambiguous = [r for r in audit_rows if r["join_status"] == "ambiguous_join"]
    no_join = [r for r in audit_rows if r["join_status"] == "no_join"]

    lines: list[str] = []
    lines += ["# Teacher-divergence board join audit", ""]
    lines += ["## Branch", "", "`exp/15x15-teacher-divergence-board-join-audit`", ""]
    lines += ["## Scope", ""]
    lines += [
        "- Board join audit only.",
        "- Does not update the manifest.",
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
        "- manifest: `analysis/integration_eval/teacher_divergence_expanded_candidate_manifest_with_fills.csv`",
        "- selected rows: non-duplicate rows with status `needs_board_join`",
        "",
    ]

    lines += ["## Summary", ""]
    lines += ["| metric | value |", "|---|---:|"]
    lines += [
        f"| manifest rows | {len(manifest_rows)} |",
        f"| needs_board_join selected rows | {len(selected)} |",
        f"| board source records loaded | {len(board_records)} |",
        f"| unique joins | {len(unique_join)} |",
        f"| ambiguous joins | {len(ambiguous)} |",
        f"| no joins | {len(no_join)} |",
        "",
    ]

    lines += ["## Join status counts", ""]
    lines += ["| join_status | rows |", "|---|---:|"]
    for key, n in count_by(audit_rows, "join_status").items():
        lines.append(f"| {key} | {n} |")
    lines.append("")

    lines += ["## Join strength counts", ""]
    lines += ["| join_strength | rows |", "|---|---:|"]
    for key, n in count_by(audit_rows, "join_strength").items():
        lines.append(f"| {key or 'none'} | {n} |")
    lines.append("")

    lines += ["## Join status by source class", ""]
    lines += ["| source_class | join_status | rows |", "|---|---|---:|"]
    combo: dict[tuple[str, str], int] = {}
    for row in audit_rows:
        key = (row["source_class"], row["join_status"])
        combo[key] = combo.get(key, 0) + 1
    for (source_class, status), n in sorted(combo.items(), key=lambda kv: (kv[0][0], kv[0][1])):
        lines.append(f"| {source_class} | {status} | {n} |")
    lines.append("")

    lines += ["## Unique-join rows preview", ""]
    lines += ["| manifest_id | source_class | strength | target_rc | matched_hash |", "|---|---|---|---|---|"]
    for row in unique_join[:40]:
        lines.append(
            f"| {row['manifest_id']} | {row['source_class']} | {row['join_strength']} | "
            f"`{row['target_rc']}` | `{row['matched_board_hash']}` |"
        )
    if len(unique_join) > 40:
        lines.append(f"| ... | ... | ... | ... | {len(unique_join) - 40} more |")
    lines.append("")

    lines += ["## Interpretation", ""]
    lines += [
        "Rows with `unique_join` are candidates for a later manifest board-join fill branch.",
        "",
        "Rows with `ambiguous_join` need source-specific disambiguation before any board is attached.",
        "",
        "Rows with `no_join` require additional board sources or should remain incomplete.",
        "",
        "This audit intentionally does not modify the manifest because a wrong board join would corrupt all downstream rank/prob and suppress labels.",
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

    manifest_rows = read_csv(args.manifest)
    selected = [
        row for row in manifest_rows
        if row.get("status") == "needs_board_join"
        and row.get("duplicate_of", "") == ""
    ]

    board_records, index = build_board_index()
    audit_rows = [audit_row(row, index) for row in selected]

    write_csv(args.out_csv, audit_rows)
    write_report(args.out_report, manifest_rows, selected, board_records, audit_rows)

    print("manifest_rows:", len(manifest_rows))
    print("needs_board_join_rows:", len(selected))
    print("board_source_records:", len(board_records))
    print("join_status_counts:", json.dumps(count_by(audit_rows, "join_status"), sort_keys=True))
    print("join_strength_counts:", json.dumps(count_by(audit_rows, "join_strength"), sort_keys=True))
    print("out_csv:", args.out_csv)
    print("out_report:", args.out_report)
    print("no manifest update; no training; no checkpoint saved")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
