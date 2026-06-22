from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path
from typing import Any


SOURCE_SPECS = [
    {
        "path": "analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected.json",
        "source_class": "canonical_full_schema_seed",
        "priority": 100,
        "include_as_row_source": True,
    },
    {
        "path": "analysis/public_benchmark_eval/rapfi_teacher_policy_margin_dataset_corpus8_selected.json",
        "source_class": "margin_dataset_crosscheck",
        "priority": 80,
        "include_as_row_source": True,
    },
    {
        "path": "analysis/integration_eval/teacher_divergence_retention_safety_v3_dataset.json",
        "source_class": "retention_candidate_dataset",
        "priority": 70,
        "include_as_row_source": True,
    },
    {
        "path": "analysis/integration_eval/teacher_divergence_retention_clean_v2_dataset.json",
        "source_class": "retention_candidate_dataset",
        "priority": 65,
        "include_as_row_source": True,
    },
    {
        "path": "analysis/integration_eval/teacher_divergence_retention_dataset.json",
        "source_class": "retention_candidate_dataset",
        "priority": 60,
        "include_as_row_source": True,
    },
    {
        "path": "analysis/integration_eval/teacher_divergence_retention_clean_v2_manifest.csv",
        "source_class": "retention_metadata_manifest",
        "priority": 45,
        "include_as_row_source": True,
    },
    {
        "path": "analysis/integration_eval/teacher_divergence_retention_manifest.csv",
        "source_class": "retention_metadata_manifest",
        "priority": 40,
        "include_as_row_source": True,
    },
    {
        "path": "analysis/public_benchmark_eval/rapfi_teacher_policy_candidates_corpus8_selected.csv",
        "source_class": "corpus8_teacher_candidate_csv",
        "priority": 55,
        "include_as_row_source": True,
    },
]

DERIVED_REFERENCE_ONLY = [
    "analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_protected_train_11_50_weightcap3.json",
]

ROW_CONTAINER_KEYS = ["samples", "rows", "data", "protected_eval_samples", "tail_eval_samples"]

OUT_FIELDS = [
    "manifest_id",
    "status",
    "bucket",
    "source_priority",
    "source_class",
    "primary_source_path",
    "duplicate_of",
    "duplicate_sources",
    "case_id",
    "source",
    "game_number",
    "move_count",
    "board_hash",
    "board_available",
    "side_available",
    "target_available",
    "teacher_eval_available",
    "rank_prob_available",
    "suppress_available",
    "current_player",
    "side_to_move",
    "target_rc",
    "target_xy",
    "teacher_move",
    "teacher_eval_kind",
    "teacher_eval_before",
    "numeric_gap_available",
    "numeric_gap_value",
    "before_target_rank",
    "before_target_prob",
    "current_best_direct_rc",
    "current_best_direct_move",
    "suppress_count",
    "suppress_rcs",
    "source_bucket",
    "validation_notes",
    "needs_current_best_probe",
    "needs_suppress_build",
    "needs_rapfi_requery",
    "needs_board_join",
    "skip_reason",
]


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Build an expanded teacher-divergence candidate manifest from selected tracked sources."
    )
    ap.add_argument(
        "--out-csv",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_expanded_candidate_manifest.csv"),
    )
    ap.add_argument(
        "--out-report",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_expanded_candidate_manifest_report.md"),
    )
    return ap.parse_args()


def read_json_rows(path: Path) -> list[dict[str, Any]]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    rows: list[Any]
    if isinstance(obj, list):
        rows = obj
    elif isinstance(obj, dict):
        rows = []
        for key in ROW_CONTAINER_KEYS:
            value = obj.get(key)
            if isinstance(value, list):
                rows.extend(value)
    else:
        rows = []
    return [r for r in rows if isinstance(r, dict)]


def read_csv_rows(path: Path) -> list[dict[str, Any]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    if path.suffix.lower() == ".json":
        return read_json_rows(path)
    if path.suffix.lower() == ".csv":
        return read_csv_rows(path)
    return []


def first_nonempty(row: dict[str, Any], keys: list[str]) -> Any:
    for key in keys:
        if key in row and row[key] not in (None, "", [], {}):
            return row[key]
    return ""


def to_json_cell(value: Any) -> str:
    if value in (None, ""):
        return ""
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def parse_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(value)
    except Exception:
        try:
            return int(float(value))
        except Exception:
            return None


def parse_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except Exception:
        return None


def parse_rc(value: Any) -> tuple[int, int] | None:
    if value in (None, "", []):
        return None
    if isinstance(value, (list, tuple)) and len(value) == 2:
        a = parse_int(value[0])
        b = parse_int(value[1])
        if a is not None and b is not None:
            return (a, b)
    if isinstance(value, str):
        s = value.strip()
        if not s:
            return None
        try:
            obj = json.loads(s)
            parsed = parse_rc(obj)
            if parsed is not None:
                return parsed
        except Exception:
            pass
        nums = re.findall(r"-?\d+", s)
        if len(nums) >= 2:
            return (int(nums[0]), int(nums[1]))
    return None


def normalize_rc_cell(value: Any) -> str:
    rc = parse_rc(value)
    if rc is None:
        return to_json_cell(value)
    return json.dumps([rc[0], rc[1]])


def parse_suppress_list(value: Any) -> list[tuple[int, int]]:
    if value in (None, "", []):
        return []
    raw = value
    if isinstance(value, str):
        try:
            raw = json.loads(value)
        except Exception:
            nums = re.findall(r"-?\d+", value)
            if len(nums) >= 2 and len(nums) % 2 == 0:
                return [(int(nums[i]), int(nums[i + 1])) for i in range(0, len(nums), 2)]
            return []
    if isinstance(raw, list):
        out: list[tuple[int, int]] = []
        for item in raw:
            if isinstance(item, dict):
                rc = parse_rc(first_nonempty(item, ["rc", "move_rc", "suppress_rc", "xy"]))
            else:
                rc = parse_rc(item)
            if rc is not None:
                out.append(rc)
        return out
    return []


def board_from_row(row: dict[str, Any]) -> Any:
    return first_nonempty(
        row,
        [
            "board",
            "board_snapshot_before_decision",
            "state",
            "position",
        ],
    )


def normalize_board(board: Any) -> list[list[int]] | None:
    if board in (None, "", []):
        return None
    if isinstance(board, str):
        try:
            board = json.loads(board)
        except Exception:
            return None
    if not isinstance(board, list) or len(board) != 15:
        return None
    norm: list[list[int]] = []
    for line in board:
        if not isinstance(line, list) or len(line) != 15:
            return None
        row: list[int] = []
        for value in line:
            iv = parse_int(value)
            if iv is None:
                return None
            row.append(iv)
        norm.append(row)
    return norm


def board_hash(board: list[list[int]] | None) -> str:
    if board is None:
        return ""
    payload = json.dumps(board, separators=(",", ":"), sort_keys=False)
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()


def normalize_player(value: Any, side: Any) -> str:
    iv = parse_int(value)
    if iv in {1, -1}:
        return str(iv)
    if isinstance(side, str):
        s = side.strip().lower()
        if s in {"black", "b", "1"}:
            return "1"
        if s in {"white", "w", "-1"}:
            return "-1"
    iv2 = parse_int(side)
    if iv2 in {1, -1}:
        return str(iv2)
    return to_json_cell(value) or to_json_cell(side)


def source_trace(row: dict[str, Any]) -> tuple[str, str, str, str]:
    case_id = str(first_nonempty(row, ["case_id", "id", "name", "position_id"]))
    source = str(first_nonempty(row, ["source", "source_file", "source_name", "label_type"]))
    game_number = str(first_nonempty(row, ["game_number", "game", "game_id", "source_game"]))
    move_count = str(first_nonempty(row, ["move_count", "ply", "move_number", "source_ply"]))
    return case_id, source, game_number, move_count


def infer_target(row: dict[str, Any]) -> tuple[str, str, str]:
    target_raw = first_nonempty(
        row,
        [
            "target_rc",
            "teacher_rc",
            "teacher_target_rc",
            "target_xy",
            "teacher_move",
            "move_rc",
        ],
    )
    target_rc = normalize_rc_cell(target_raw)
    target_xy = normalize_rc_cell(first_nonempty(row, ["target_xy", "teacher_xy"]))
    teacher_move = to_json_cell(first_nonempty(row, ["teacher_move", "teacher_rc", "target_rc"]))
    return target_rc, target_xy, teacher_move


def infer_rank_prob(row: dict[str, Any]) -> tuple[str, str]:
    rank = first_nonempty(row, ["before_target_rank", "target_rank", "teacher_rank", "rank"])
    prob = first_nonempty(row, ["before_target_prob", "target_prob", "teacher_prob", "prob"])
    return str(rank) if rank != "" else "", str(prob) if prob != "" else ""


def infer_suppress(row: dict[str, Any]) -> tuple[int, str]:
    raw = first_nonempty(
        row,
        [
            "suppress_rcs",
            "suppress_candidates",
            "suppress_rc",
            "primary_suppress_rc",
            "candidate_suppress_rcs",
        ],
    )
    parsed = parse_suppress_list(raw)
    if parsed:
        return len(parsed), json.dumps([[r, c] for r, c in parsed])
    single = parse_rc(raw)
    if single is not None:
        return 1, json.dumps([[single[0], single[1]]])
    return 0, to_json_cell(raw)


def infer_teacher_eval(row: dict[str, Any]) -> tuple[str, str, str, str]:
    kind = first_nonempty(row, ["teacher_eval_kind", "eval_kind", "label_type"])
    before = first_nonempty(row, ["teacher_eval_before", "teacher_score_before", "teacher_before"])
    gap_available = first_nonempty(row, ["numeric_gap_available", "has_numeric_gap"])
    gap_value = first_nonempty(row, ["numeric_gap_value", "gap", "score_gap", "teacher_gap"])
    return (
        str(kind) if kind != "" else "",
        str(before) if before != "" else "",
        str(gap_available) if gap_available != "" else "",
        str(gap_value) if gap_value != "" else "",
    )


def infer_direct(row: dict[str, Any]) -> tuple[str, str]:
    direct_rc = first_nonempty(
        row,
        [
            "current_best_direct_rc",
            "model_move_rc",
            "model_rc",
            "before_direct_rc",
            "primary_suppress_rc",
        ],
    )
    direct_move = first_nonempty(
        row,
        [
            "current_best_direct_move",
            "model_move",
            "before_direct_move",
            "primary_suppress_rc",
        ],
    )
    return normalize_rc_cell(direct_rc), to_json_cell(direct_move)


def source_bucket(row: dict[str, Any]) -> str:
    return str(first_nonempty(row, ["bucket", "suggested_bucket", "protected_objective_role", "role", "label_type"]))


def rank_bucket(rank_text: str) -> str:
    r = parse_int(rank_text)
    if r is None:
        return "unknown_rank"
    if r <= 10:
        return "protected_top10"
    if r <= 50:
        return "trainable_rank_11_50"
    return "tail_rank_gt50"


def normalize_row(raw: dict[str, Any], spec: dict[str, Any], idx: int) -> dict[str, Any]:
    board_norm = normalize_board(board_from_row(raw))
    bh = board_hash(board_norm)

    side_to_move = first_nonempty(raw, ["side_to_move", "side", "player_to_move"])
    current_player = normalize_player(first_nonempty(raw, ["current_player", "player"]), side_to_move)

    target_rc, target_xy, teacher_move = infer_target(raw)
    before_rank, before_prob = infer_rank_prob(raw)
    suppress_count, suppress_rcs = infer_suppress(raw)
    teacher_eval_kind, teacher_eval_before, numeric_gap_available, numeric_gap_value = infer_teacher_eval(raw)
    current_best_direct_rc, current_best_direct_move = infer_direct(raw)
    case_id, source, game_number, move_count = source_trace(raw)

    board_available = int(board_norm is not None)
    side_available = int(bool(current_player or side_to_move))
    target_available = int(bool(parse_rc(target_rc)))
    rank_prob_available = int(bool(before_rank and before_prob))
    suppress_available = int(suppress_count > 0)
    teacher_eval_available = int(bool(teacher_eval_kind or teacher_eval_before or numeric_gap_value))

    needs_board_join = int(not board_available)
    needs_current_best_probe = int(not rank_prob_available)
    needs_suppress_build = int(not suppress_available)
    needs_rapfi_requery = int(not teacher_eval_available)

    notes: list[str] = []
    skip_reason = ""

    if not board_available:
        notes.append("missing_or_invalid_board")
    if not side_available:
        notes.append("missing_side")
    if not target_available:
        notes.append("missing_or_invalid_target")
    if board_available and board_norm is not None:
        flat = {v for row in board_norm for v in row}
        if not flat.issubset({-1, 0, 1}):
            notes.append("board_has_unexpected_values")

    if not side_available or not target_available:
        status = "skipped_invalid"
        skip_reason = ",".join(notes)
    elif needs_board_join:
        status = "needs_board_join"
    elif needs_rapfi_requery:
        status = "needs_rapfi_requery"
    elif needs_current_best_probe:
        status = "needs_current_best_probe"
    elif needs_suppress_build:
        status = "needs_suppress_build"
    else:
        status = "ready_full_schema"

    return {
        "manifest_id": f"td_exp_{idx:05d}",
        "status": status,
        "bucket": rank_bucket(before_rank),
        "source_priority": spec["priority"],
        "source_class": spec["source_class"],
        "primary_source_path": spec["path"],
        "duplicate_of": "",
        "duplicate_sources": "",
        "case_id": case_id,
        "source": source,
        "game_number": game_number,
        "move_count": move_count,
        "board_hash": bh,
        "board_available": board_available,
        "side_available": side_available,
        "target_available": target_available,
        "teacher_eval_available": teacher_eval_available,
        "rank_prob_available": rank_prob_available,
        "suppress_available": suppress_available,
        "current_player": current_player,
        "side_to_move": to_json_cell(side_to_move),
        "target_rc": target_rc,
        "target_xy": target_xy,
        "teacher_move": teacher_move,
        "teacher_eval_kind": teacher_eval_kind,
        "teacher_eval_before": teacher_eval_before,
        "numeric_gap_available": numeric_gap_available,
        "numeric_gap_value": numeric_gap_value,
        "before_target_rank": before_rank,
        "before_target_prob": before_prob,
        "current_best_direct_rc": current_best_direct_rc,
        "current_best_direct_move": current_best_direct_move,
        "suppress_count": suppress_count,
        "suppress_rcs": suppress_rcs,
        "source_bucket": source_bucket(raw),
        "validation_notes": ",".join(notes),
        "needs_current_best_probe": needs_current_best_probe,
        "needs_suppress_build": needs_suppress_build,
        "needs_rapfi_requery": needs_rapfi_requery,
        "needs_board_join": needs_board_join,
        "skip_reason": skip_reason,
    }


def coverage_score(row: dict[str, Any]) -> tuple[int, int]:
    flags = [
        "board_available",
        "side_available",
        "target_available",
        "teacher_eval_available",
        "rank_prob_available",
        "suppress_available",
    ]
    return (sum(int(row[f]) for f in flags), int(row["source_priority"]))


def dedup_key(row: dict[str, Any]) -> str:
    if row["board_hash"] and row["current_player"] and row["target_rc"]:
        return f"board:{row['board_hash']}|player:{row['current_player']}|target:{row['target_rc']}"
    trace = "|".join(
        [
            row["primary_source_path"],
            row["case_id"],
            row["game_number"],
            row["move_count"],
            row["target_rc"],
        ]
    )
    return f"trace:{trace}"


def apply_dedup(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    best_by_key: dict[str, dict[str, Any]] = {}
    grouped: dict[str, list[dict[str, Any]]] = {}

    for row in rows:
        key = dedup_key(row)
        grouped.setdefault(key, []).append(row)
        best = best_by_key.get(key)
        if best is None or coverage_score(row) > coverage_score(best):
            best_by_key[key] = row

    for key, members in grouped.items():
        best = best_by_key[key]
        sources = sorted({m["primary_source_path"] for m in members})
        best["duplicate_sources"] = json.dumps(sources, ensure_ascii=False)
        for member in members:
            if member is best:
                continue
            member["status"] = "duplicate"
            member["duplicate_of"] = best["manifest_id"]
            member["duplicate_sources"] = json.dumps(sources, ensure_ascii=False)

    return rows


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=OUT_FIELDS, lineterminator="\n")
        w.writeheader()
        for row in rows:
            w.writerow({field: row.get(field, "") for field in OUT_FIELDS})


def count_by(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
    out: dict[str, int] = {}
    for row in rows:
        value = str(row.get(key, ""))
        out[value] = out.get(value, 0) + 1
    return dict(sorted(out.items(), key=lambda kv: (-kv[1], kv[0])))


def sum_int(rows: list[dict[str, Any]], key: str) -> int:
    return sum(int(row.get(key, 0) or 0) for row in rows)


def write_report(path: Path, rows: list[dict[str, Any]], source_counts: list[tuple[str, int]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    nondup = [r for r in rows if r["status"] != "duplicate"]

    lines: list[str] = []
    lines += ["# Teacher-divergence expanded candidate manifest report", ""]
    lines += ["## Branch", "", "`exp/15x15-teacher-divergence-expanded-manifest-builder`", ""]
    lines += ["## Scope", ""]
    lines += [
        "- Manifest builder only.",
        "- Selected tracked sources only.",
        "- No training.",
        "- No checkpoint save.",
        "- No C export.",
        "- No public benchmark.",
        "- No promotion.",
        "",
    ]

    lines += ["## Source rows loaded", ""]
    lines += ["| source | rows_loaded |", "|---|---:|"]
    for source, n in source_counts:
        lines.append(f"| `{source}` | {n} |")
    lines.append("")

    lines += ["## Manifest summary", ""]
    lines += ["| metric | value |", "|---|---:|"]
    lines += [
        f"| total manifest rows | {len(rows)} |",
        f"| non-duplicate rows | {len(nondup)} |",
        f"| duplicate rows | {sum(1 for r in rows if r['status'] == 'duplicate')} |",
        f"| board_available rows | {sum_int(nondup, 'board_available')} |",
        f"| side_available rows | {sum_int(nondup, 'side_available')} |",
        f"| target_available rows | {sum_int(nondup, 'target_available')} |",
        f"| teacher_eval_available rows | {sum_int(nondup, 'teacher_eval_available')} |",
        f"| rank_prob_available rows | {sum_int(nondup, 'rank_prob_available')} |",
        f"| suppress_available rows | {sum_int(nondup, 'suppress_available')} |",
        "",
    ]

    lines += ["## Status counts", ""]
    lines += ["| status | rows |", "|---|---:|"]
    for status, n in count_by(rows, "status").items():
        lines.append(f"| {status} | {n} |")
    lines.append("")

    lines += ["## Bucket counts for non-duplicate rows", ""]
    lines += ["| bucket | rows |", "|---|---:|"]
    for bucket, n in count_by(nondup, "bucket").items():
        lines.append(f"| {bucket} | {n} |")
    lines.append("")

    lines += ["## Source class counts for non-duplicate rows", ""]
    lines += ["| source_class | rows |", "|---|---:|"]
    for cls, n in count_by(nondup, "source_class").items():
        lines.append(f"| {cls} | {n} |")
    lines.append("")

    lines += ["## Interpretation", ""]
    lines += [
        "This manifest is a candidate inventory, not a training dataset.",
        "",
        "Rows marked `ready_full_schema` are immediately usable for diagnostics. Rows marked `needs_current_best_probe`, `needs_suppress_build`, `needs_rapfi_requery`, or `needs_board_join` require additional processing before they can feed any training dataset.",
        "",
        "Duplicate rows are retained with `duplicate_of` pointers so source overlap remains auditable.",
        "",
    ]

    lines += ["## Decision", ""]
    lines += [
        "No training should run from this branch.",
        "",
        "The next branch should inspect the manifest and decide which missing-field fill step comes first.",
        "",
        "Likely next step: current_best rank/prob probe for non-duplicate rows with board, side, and target but missing rank/prob.",
        "",
    ]

    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    args = parse_args()

    rows: list[dict[str, Any]] = []
    source_counts: list[tuple[str, int]] = []
    idx = 1

    for spec in SOURCE_SPECS:
        path = Path(spec["path"])
        if not spec["include_as_row_source"]:
            continue
        raw_rows = load_rows(path)
        source_counts.append((spec["path"], len(raw_rows)))
        for raw in raw_rows:
            rows.append(normalize_row(raw, spec, idx))
            idx += 1

    rows = apply_dedup(rows)

    write_csv(args.out_csv, rows)
    write_report(args.out_report, rows, source_counts)

    print("source_files:", len(SOURCE_SPECS))
    print("total_manifest_rows:", len(rows))
    print("non_duplicate_rows:", sum(1 for r in rows if r["status"] != "duplicate"))
    print("status_counts:", json.dumps(count_by(rows, "status"), sort_keys=True))
    print("bucket_counts_non_duplicate:", json.dumps(count_by([r for r in rows if r["status"] != "duplicate"], "bucket"), sort_keys=True))
    print("out_csv:", args.out_csv)
    print("out_report:", args.out_report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
