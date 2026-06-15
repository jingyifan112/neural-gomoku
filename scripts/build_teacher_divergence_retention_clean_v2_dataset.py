#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import hashlib
from collections import Counter
from pathlib import Path
from typing import Any


OUT_DIR = Path("analysis/integration_eval")

BASELINE_DATASET = Path("analysis/integration_eval/teacher_divergence_retention_dataset.json")
CANDIDATE_G_DATASET = Path("analysis/integration_eval/candidate_g_teacher_seed_dataset.json")
SCOREGAP_CSV = Path("analysis/public_benchmark_eval/rapfi_teacher_scoregap_corpus8_selected.csv")

RETENTION_ANCHOR_PATHS = [
    Path("analysis/integration_eval/candidate_c_g2_m19_perspective_diagnostic_anchors.json"),
    Path("analysis/integration_eval/candidate_d_g2_m15_diagnostic_anchors.json"),
    Path("analysis/integration_eval/candidate_e_g2_m13_diagnostic_anchors.json"),
    Path("analysis/integration_eval/candidate_e_g2_m17_diagnostic_anchors.json"),
    Path("analysis/integration_eval/current_best_margin_candidate_c_anchors.json"),
    Path("analysis/integration_eval/current_best_margin_candidate_c_conservative_anchors.json"),
]

OUT_DATASET = OUT_DIR / "teacher_divergence_retention_clean_v2_dataset.json"
OUT_MANIFEST = OUT_DIR / "teacher_divergence_retention_clean_v2_manifest.csv"
OUT_AUDIT = OUT_DIR / "teacher_divergence_retention_clean_v2_source_audit.json"
OUT_REPORT = OUT_DIR / "teacher_divergence_retention_clean_v2_report.md"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def extract_rows(obj: Any) -> list[dict[str, Any]]:
    if isinstance(obj, list):
        return [r for r in obj if isinstance(r, dict)]
    if isinstance(obj, dict):
        for key in ["rows", "records", "positions", "examples", "items", "data", "anchors"]:
            if isinstance(obj.get(key), list):
                return [r for r in obj[key] if isinstance(r, dict)]
    return []


def read_json_rows(path: Path) -> list[dict[str, Any]]:
    return extract_rows(read_json(path))


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return [dict(row) for row in csv.DictReader(f)]


def stable_hash(obj: Any) -> str:
    s = json.dumps(obj, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:12]


def norm_scalar(x: Any) -> str:
    if x is None:
        return ""
    if isinstance(x, str):
        return x.strip()
    return str(x)


def norm_move(x: Any) -> str:
    if x is None:
        return ""
    if isinstance(x, str):
        s = x.strip()
        if not s:
            return ""
        return s.replace(" ", "")
    if isinstance(x, (list, tuple)) and len(x) >= 2:
        return f"{x[0]},{x[1]}"
    if isinstance(x, dict):
        for a, b in [("x", "y"), ("row", "col"), ("r", "c")]:
            if a in x and b in x:
                return f"{x[a]},{x[b]}"
    return norm_scalar(x).replace(" ", "")


def is_concrete_move(x: Any) -> bool:
    s = norm_move(x).lower()
    if not s:
        return False
    return s not in {
        "na", "n/a", "nan", "none", "null", "unknown",
        "no_move", "no_move_or_na", "pass", "resign",
        "[]", "{}",
    }


def moves_differ(a: Any, b: Any) -> bool:
    return is_concrete_move(a) and is_concrete_move(b) and norm_move(a).lower() != norm_move(b).lower()


def parse_float(x: Any) -> float | None:
    try:
        if x is None or x == "":
            return None
        return float(x)
    except Exception:
        return None


def board_from_row(row: dict[str, Any]) -> str:
    if "board" in row and row["board"] not in (None, ""):
        board = row["board"]
        if isinstance(board, str):
            return board
        return json.dumps(board, ensure_ascii=False)
    if "board_strings" in row and row["board_strings"] not in (None, ""):
        bs = row["board_strings"]
        if isinstance(bs, list):
            return "\n".join(str(x) for x in bs)
        if isinstance(bs, str):
            return bs
    return ""


def read_board_file(path_text: str) -> str:
    if not path_text:
        return ""
    path = Path(path_text)
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def first_nonempty(row: dict[str, Any], keys: list[str]) -> Any:
    for key in keys:
        if key in row and row[key] not in (None, "", "NA", "nan"):
            return row[key]
    return ""


def make_dataset_row(
    *,
    row_id: str,
    split: str,
    role: str,
    bucket: str,
    source_path: str,
    source_id: str,
    board: str,
    game_number: Any,
    move_count: Any,
    side_to_move: Any,
    policy_target: Any,
    teacher_move: Any,
    suggested_weight: Any,
    heldout: bool,
    metadata: dict[str, Any],
) -> dict[str, Any]:
    return {
        "id": row_id,
        "split": split,
        "role": role,
        "bucket": bucket,
        "source_path": source_path,
        "source_id": norm_scalar(source_id),
        "board_size": 15,
        "win_length": 5,
        "game_number": game_number if game_number != "" else "",
        "move_count": move_count if move_count != "" else "",
        "side_to_move": norm_scalar(side_to_move),
        "board": board,
        "policy_target": norm_move(policy_target),
        "teacher_move": norm_move(teacher_move),
        "value_target": "",
        "label_type": "policy_teacher",
        "suggested_weight": suggested_weight,
        "heldout": bool(heldout),
        "metadata": metadata,
    }


def manifest_row(
    *,
    dataset_id: str,
    included: bool,
    skip_reason: str,
    split: str,
    role: str,
    bucket: str,
    source_path: str,
    source_id: str,
    game_number: Any = "",
    move_count: Any = "",
    side_to_move: Any = "",
    policy_target: Any = "",
    teacher_move: Any = "",
    current_best_direct_move: Any = "",
    current_best_matches_teacher: Any = "",
    labeled_failure_type: Any = "",
    numeric_gap_value: Any = "",
    suggested_weight: Any = "",
    board: str = "",
    duplicate_of: str = "",
    notes: str = "",
) -> dict[str, Any]:
    digest = stable_hash(board) if board else ""
    return {
        "dataset_id": dataset_id,
        "included": included,
        "skip_reason": skip_reason,
        "split": split,
        "role": role,
        "bucket": bucket,
        "source_path": source_path,
        "source_id": norm_scalar(source_id),
        "game_number": game_number,
        "move_count": move_count,
        "side_to_move": norm_scalar(side_to_move),
        "policy_target": norm_move(policy_target),
        "teacher_move": norm_move(teacher_move),
        "current_best_direct_move": norm_move(current_best_direct_move),
        "current_best_matches_teacher": current_best_matches_teacher,
        "labeled_failure_type": labeled_failure_type,
        "numeric_gap_value": numeric_gap_value,
        "suggested_weight": suggested_weight,
        "board_digest": digest,
        "duplicate_of": duplicate_of,
        "notes": notes,
    }


def scoregap_weight(gap_text: Any) -> float:
    gap = parse_float(gap_text)
    if gap is None:
        return 1.5
    agap = abs(gap)
    if agap >= 300:
        return 2.0
    if agap >= 100:
        return 1.5
    return 1.25


def get_existing_source_ids(rows: list[dict[str, Any]]) -> set[str]:
    ids = set()
    for r in rows:
        sid = norm_scalar(r.get("source_id"))
        if sid:
            ids.add(sid)
    return ids


def load_baseline() -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    rows = read_json_rows(BASELINE_DATASET)
    dataset_rows = []
    manifest = []

    for r in rows:
        rid = norm_scalar(r.get("id"))
        board = board_from_row(r)
        included = bool(board and is_concrete_move(r.get("teacher_move") or r.get("policy_target")))

        clean = dict(r)
        clean.setdefault("board_size", 15)
        clean.setdefault("win_length", 5)
        clean.setdefault("heldout", clean.get("split") == "heldout_retention")
        clean.setdefault("metadata", {})
        clean["metadata"] = {
            **(clean["metadata"] if isinstance(clean.get("metadata"), dict) else {}),
            "clean_v2_source": "canonical_baseline_dataset",
        }

        if included:
            dataset_rows.append(clean)

        manifest.append(manifest_row(
            dataset_id=rid,
            included=included,
            skip_reason="" if included else "missing_board_or_teacher_move",
            split=norm_scalar(clean.get("split")),
            role=norm_scalar(clean.get("role")),
            bucket=norm_scalar(clean.get("bucket")),
            source_path=str(BASELINE_DATASET),
            source_id=clean.get("source_id", ""),
            game_number=clean.get("game_number", ""),
            move_count=clean.get("move_count", ""),
            side_to_move=clean.get("side_to_move", ""),
            policy_target=clean.get("policy_target", ""),
            teacher_move=clean.get("teacher_move", ""),
            suggested_weight=clean.get("suggested_weight", ""),
            board=board,
            notes="canonical baseline row",
        ))

    audit = {
        "source_group": "canonical_baseline_dataset",
        "path": str(BASELINE_DATASET),
        "exists": BASELINE_DATASET.exists(),
        "rows_seen": len(rows),
        "rows_included": len(dataset_rows),
        "error": "",
    }
    return dataset_rows, manifest, audit


def load_candidate_g(existing_source_ids: set[str]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    rows = read_json_rows(CANDIDATE_G_DATASET)
    dataset_rows = []
    manifest = []

    seen = set(existing_source_ids)

    for r in rows:
        source_id = norm_scalar(r.get("id")) or f"candidate_g_{stable_hash(r)}"
        teacher = r.get("teacher_move")
        model = r.get("model_move")
        role_raw = norm_scalar(r.get("role"))
        diverges = bool(r.get("diverges")) or moves_differ(teacher, model) or role_raw == "seed_teacher_divergence"
        board = board_from_row(r)

        row_id = f"tdiv_candidate_g_{source_id}"

        skip_reason = ""
        included = True

        if not diverges:
            included = False
            skip_reason = "candidate_g_nondivergent_anchor"
        elif source_id in seen:
            included = False
            skip_reason = "duplicate_source_id"
        elif not board:
            included = False
            skip_reason = "missing_board"
        elif not is_concrete_move(teacher):
            included = False
            skip_reason = "missing_teacher_move"

        if included:
            seen.add(source_id)
            dataset_rows.append(make_dataset_row(
                row_id=row_id,
                split="train_candidate",
                role="teacher_divergence",
                bucket="candidate_g_seed_teacher_divergence",
                source_path=str(CANDIDATE_G_DATASET),
                source_id=source_id,
                board=board,
                game_number=r.get("game", ""),
                move_count=r.get("ply", ""),
                side_to_move=first_nonempty(r, ["side_to_move", "side"]),
                policy_target=teacher,
                teacher_move=teacher,
                suggested_weight=r.get("weight", 2.0),
                heldout=False,
                metadata={
                    "clean_v2_source": "candidate_g_seed_dataset",
                    "model_move": norm_move(model),
                    "teacher_move_policy_rank": r.get("teacher_move_policy_rank", ""),
                    "model_move_policy_rank": r.get("model_move_policy_rank", ""),
                    "teacher_policy_prob": r.get("teacher_policy_prob", ""),
                    "model_policy_prob": r.get("model_policy_prob", ""),
                    "policy_probability_gap_teacher_minus_model": r.get("policy_probability_gap_teacher_minus_model", ""),
                    "policy_logit_gap_teacher_minus_model": r.get("policy_logit_gap_teacher_minus_model", ""),
                    "value_current_position": r.get("value_current_position", ""),
                    "value_original_move": r.get("value_original_move", ""),
                    "value_teacher_move": r.get("value_teacher_move", ""),
                    "teacher_value_disfavored": r.get("teacher_value_disfavored", ""),
                    "role_raw": role_raw,
                    "reason": r.get("reason", ""),
                },
            ))

        manifest.append(manifest_row(
            dataset_id=row_id,
            included=included,
            skip_reason=skip_reason,
            split="train_candidate" if diverges else "audit_only",
            role="teacher_divergence" if diverges else "candidate_g_anchor_audit",
            bucket="candidate_g_seed_teacher_divergence" if diverges else "candidate_g_nondivergent_anchor",
            source_path=str(CANDIDATE_G_DATASET),
            source_id=source_id,
            game_number=r.get("game", ""),
            move_count=r.get("ply", ""),
            side_to_move=first_nonempty(r, ["side_to_move", "side"]),
            policy_target=teacher,
            teacher_move=teacher,
            current_best_direct_move=model,
            current_best_matches_teacher=(not moves_differ(teacher, model)) if is_concrete_move(teacher) and is_concrete_move(model) else "",
            suggested_weight=r.get("weight", ""),
            board=board,
            notes=f"role_raw={role_raw}; teacher_rank={r.get('teacher_move_policy_rank', '')}",
        ))

    audit = {
        "source_group": "candidate_g_seed_dataset",
        "path": str(CANDIDATE_G_DATASET),
        "exists": CANDIDATE_G_DATASET.exists(),
        "rows_seen": len(rows),
        "rows_included": len(dataset_rows),
        "error": "",
    }
    return dataset_rows, manifest, audit


def load_scoregap(existing_source_ids: set[str]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    rows = read_csv_rows(SCOREGAP_CSV)
    dataset_rows = []
    manifest = []

    seen = set(existing_source_ids)

    for r in rows:
        source_id = norm_scalar(r.get("sample_id")) or f"scoregap_{stable_hash(r)}"
        teacher = r.get("rapfi_best_move_before", "")
        model = r.get("model_direct_move", "")
        gap = r.get("provisional_root_pov_gap_best_minus_model", "")
        status_before = norm_scalar(r.get("rapfi_query_status_before"))
        status_after = norm_scalar(r.get("rapfi_query_status_after_model"))
        apply_status = norm_scalar(r.get("model_direct_apply_status"))
        match_text = norm_scalar(r.get("model_matches_rapfi_best_before"))
        board = read_board_file(norm_scalar(r.get("rapfi_before_query_file", "")))

        row_id = f"tdiv_scoregap_{source_id}"

        skip_reason = ""
        included = True

        if source_id in seen:
            included = False
            skip_reason = "duplicate_source_id_already_in_baseline_or_seed"
        elif status_before != "concrete_move":
            included = False
            skip_reason = f"rapfi_before_not_concrete:{status_before}"
        elif apply_status and apply_status != "ok":
            included = False
            skip_reason = f"model_apply_not_ok:{apply_status}"
        elif not is_concrete_move(teacher):
            included = False
            skip_reason = "missing_rapfi_teacher_move"
        elif not is_concrete_move(model):
            included = False
            skip_reason = "missing_model_direct_move"
        elif not moves_differ(teacher, model):
            included = False
            skip_reason = "model_matches_teacher"
        elif match_text.lower() == "true":
            included = False
            skip_reason = "model_matches_rapfi_best_before_true"
        elif not board:
            included = False
            skip_reason = "missing_before_board_file"

        if included:
            seen.add(source_id)
            dataset_rows.append(make_dataset_row(
                row_id=row_id,
                split="train_candidate",
                role="teacher_divergence",
                bucket="rapfi_scoregap_current_best_disagreement",
                source_path=str(SCOREGAP_CSV),
                source_id=source_id,
                board=board,
                game_number=r.get("game_number", ""),
                move_count=r.get("move_count", ""),
                side_to_move=r.get("side_to_move", ""),
                policy_target=teacher,
                teacher_move=teacher,
                suggested_weight=scoregap_weight(gap),
                heldout=False,
                metadata={
                    "clean_v2_source": "rapfi_teacher_scoregap_corpus8_selected",
                    "model_direct_move": norm_move(model),
                    "model_direct_prob": r.get("model_direct_prob", ""),
                    "model_value_estimate": r.get("model_value_estimate", ""),
                    "rapfi_eval_before": r.get("rapfi_eval_before", ""),
                    "rapfi_pv_before": r.get("rapfi_pv_before", ""),
                    "rapfi_best_move_after_model": r.get("rapfi_best_move_after_model", ""),
                    "rapfi_eval_after_model_next_player_pov": r.get("rapfi_eval_after_model_next_player_pov", ""),
                    "rapfi_pv_after_model": r.get("rapfi_pv_after_model", ""),
                    "rapfi_query_status_before": status_before,
                    "rapfi_query_status_after_model": status_after,
                    "model_matches_rapfi_best_before": match_text,
                    "provisional_root_pov_gap_best_minus_model": gap,
                    "labeled_failure_type": r.get("labeled_failure_type", ""),
                    "rapfi_before_depth": r.get("rapfi_before_depth", ""),
                    "rapfi_after_depth": r.get("rapfi_after_depth", ""),
                    "rapfi_before_query_file": r.get("rapfi_before_query_file", ""),
                    "rapfi_after_query_file": r.get("rapfi_after_query_file", ""),
                },
            ))

        manifest.append(manifest_row(
            dataset_id=row_id,
            included=included,
            skip_reason=skip_reason,
            split="train_candidate",
            role="teacher_divergence",
            bucket="rapfi_scoregap_current_best_disagreement",
            source_path=str(SCOREGAP_CSV),
            source_id=source_id,
            game_number=r.get("game_number", ""),
            move_count=r.get("move_count", ""),
            side_to_move=r.get("side_to_move", ""),
            policy_target=teacher,
            teacher_move=teacher,
            current_best_direct_move=model,
            current_best_matches_teacher=match_text,
            labeled_failure_type=r.get("labeled_failure_type", ""),
            numeric_gap_value=gap,
            suggested_weight=scoregap_weight(gap),
            board=board,
            notes=f"status_before={status_before}; status_after={status_after}; apply={apply_status}",
        ))

    audit = {
        "source_group": "rapfi_scoregap_current_best",
        "path": str(SCOREGAP_CSV),
        "exists": SCOREGAP_CSV.exists(),
        "rows_seen": len(rows),
        "rows_included": len(dataset_rows),
        "error": "",
    }
    return dataset_rows, manifest, audit


def load_retention_anchors(existing_source_ids: set[str]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    dataset_rows = []
    manifest = []
    audits = []
    seen = set(existing_source_ids)

    for path in RETENTION_ANCHOR_PATHS:
        if not path.exists():
            audits.append({
                "source_group": "external_retention_anchors",
                "path": str(path),
                "exists": False,
                "rows_seen": 0,
                "rows_included": 0,
                "error": "",
            })
            continue

        try:
            rows = read_json_rows(path)
            included_count = 0

            for idx, r in enumerate(rows):
                raw_id = norm_scalar(first_nonempty(r, ["id", "source_id", "case_id", "position_id", "name"]))
                source_id = raw_id or f"{path.stem}_{idx}_{stable_hash(r)}"

                board = board_from_row(r)
                target = first_nonempty(r, [
                    "policy_target",
                    "teacher_move",
                    "target_move",
                    "model_move",
                    "current_best_move",
                    "logged_direct",
                    "move",
                ])
                side = first_nonempty(r, ["side_to_move", "side", "color"])
                game_number = first_nonempty(r, ["game_number", "game"])
                move_count = first_nonempty(r, ["move_count", "ply", "move_index"])
                weight = first_nonempty(r, ["suggested_weight", "weight"])
                if weight == "":
                    weight = 1.0

                row_id = f"retention_external_{source_id}"

                skip_reason = ""
                included = True

                if source_id in seen:
                    included = False
                    skip_reason = "duplicate_source_id"
                elif not board:
                    included = False
                    skip_reason = "missing_board"
                elif not is_concrete_move(target):
                    included = False
                    skip_reason = "missing_policy_target"

                if included:
                    seen.add(source_id)
                    included_count += 1
                    dataset_rows.append(make_dataset_row(
                        row_id=row_id,
                        split="heldout_retention",
                        role="heldout_retention_anchor",
                        bucket="external_current_best_retention_anchor",
                        source_path=str(path),
                        source_id=source_id,
                        board=board,
                        game_number=game_number,
                        move_count=move_count,
                        side_to_move=side,
                        policy_target=target,
                        teacher_move=target,
                        suggested_weight=weight,
                        heldout=True,
                        metadata={
                            "clean_v2_source": "external_retention_anchor",
                            "raw_role": r.get("role", ""),
                            "raw_label": r.get("label", ""),
                            "raw_bucket": r.get("bucket", ""),
                        },
                    ))

                manifest.append(manifest_row(
                    dataset_id=row_id,
                    included=included,
                    skip_reason=skip_reason,
                    split="heldout_retention",
                    role="heldout_retention_anchor",
                    bucket="external_current_best_retention_anchor",
                    source_path=str(path),
                    source_id=source_id,
                    game_number=game_number,
                    move_count=move_count,
                    side_to_move=side,
                    policy_target=target,
                    teacher_move=target,
                    suggested_weight=weight,
                    board=board,
                    notes="external retention anchor; held out from training",
                ))

            audits.append({
                "source_group": "external_retention_anchors",
                "path": str(path),
                "exists": True,
                "rows_seen": len(rows),
                "rows_included": included_count,
                "error": "",
            })

        except Exception as e:
            audits.append({
                "source_group": "external_retention_anchors",
                "path": str(path),
                "exists": True,
                "rows_seen": 0,
                "rows_included": 0,
                "error": repr(e),
            })

    return dataset_rows, manifest, audits


def write_outputs(dataset_rows: list[dict[str, Any]], manifest_rows: list[dict[str, Any]], audits: list[dict[str, Any]]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    dataset_rows = sorted(dataset_rows, key=lambda r: (r.get("split", ""), r.get("role", ""), r.get("id", "")))
    manifest_rows = sorted(manifest_rows, key=lambda r: (str(r.get("source_path")), str(r.get("dataset_id"))))

    role_counts = Counter(r.get("role", "") for r in dataset_rows)
    split_counts = Counter(r.get("split", "") for r in dataset_rows)
    bucket_counts = Counter(r.get("bucket", "") for r in dataset_rows)
    source_counts = Counter(r.get("metadata", {}).get("clean_v2_source", "unknown") for r in dataset_rows)

    out_obj = {
        "note": "Clean v2 teacher-divergence / held-out retention dataset. Data/report only; no training/export/benchmark run.",
        "counts": {
            "dataset_rows": len(dataset_rows),
            "role_counts": dict(role_counts),
            "split_counts": dict(split_counts),
            "bucket_counts": dict(bucket_counts),
            "source_counts": dict(source_counts),
        },
        "rows": dataset_rows,
    }

    OUT_DATASET.write_text(json.dumps(out_obj, indent=2, ensure_ascii=False), encoding="utf-8")
    OUT_AUDIT.write_text(json.dumps({"sources": audits}, indent=2, ensure_ascii=False), encoding="utf-8")

    fields = [
        "dataset_id", "included", "skip_reason", "split", "role", "bucket",
        "source_path", "source_id", "game_number", "move_count", "side_to_move",
        "policy_target", "teacher_move", "current_best_direct_move",
        "current_best_matches_teacher", "labeled_failure_type", "numeric_gap_value",
        "suggested_weight", "board_digest", "duplicate_of", "notes",
    ]

    with OUT_MANIFEST.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for r in manifest_rows:
            writer.writerow({k: r.get(k, "") for k in fields})

    included_manifest = [r for r in manifest_rows if r["included"]]
    skipped_manifest = [r for r in manifest_rows if not r["included"]]

    md = []
    md.append("# Clean v2 teacher-divergence / held-out retention dataset report")
    md.append("")
    md.append("This step only builds dataset/manifest/report artifacts. It does not train, export, benchmark, or modify model weights.")
    md.append("")
    md.append("## Summary")
    md.append("")
    md.append(f"- dataset rows: {len(dataset_rows)}")
    md.append(f"- manifest rows: {len(manifest_rows)}")
    md.append(f"- manifest included rows: {len(included_manifest)}")
    md.append(f"- manifest skipped/audit rows: {len(skipped_manifest)}")
    md.append("")
    md.append("## Dataset split counts")
    md.append("")
    md.append("| split | count |")
    md.append("|---|---:|")
    for k, v in split_counts.most_common():
        md.append(f"| {k} | {v} |")
    md.append("")
    md.append("## Dataset role counts")
    md.append("")
    md.append("| role | count |")
    md.append("|---|---:|")
    for k, v in role_counts.most_common():
        md.append(f"| {k} | {v} |")
    md.append("")
    md.append("## Dataset bucket counts")
    md.append("")
    md.append("| bucket | count |")
    md.append("|---|---:|")
    for k, v in bucket_counts.most_common():
        md.append(f"| {k} | {v} |")
    md.append("")
    md.append("## Dataset source counts")
    md.append("")
    md.append("| clean_v2_source | count |")
    md.append("|---|---:|")
    for k, v in source_counts.most_common():
        md.append(f"| {k} | {v} |")
    md.append("")
    md.append("## Source audit")
    md.append("")
    md.append("| source_group | path | exists | rows_seen | rows_included | error |")
    md.append("|---|---|---:|---:|---:|---|")
    for a in audits:
        md.append(
            f"| {a['source_group']} | `{a['path']}` | {a['exists']} | "
            f"{a['rows_seen']} | {a['rows_included']} | {a.get('error','')} |"
        )
    md.append("")
    md.append("## Included train candidates")
    md.append("")
    md.append("| id | source_id | bucket | side | teacher | model/current_best | gap/rank | weight |")
    md.append("|---|---|---|---|---|---|---:|---:|")
    for r in dataset_rows:
        if r.get("split") != "train_candidate":
            continue
        meta = r.get("metadata", {})
        model = meta.get("model_direct_move", meta.get("model_move", ""))
        gap_or_rank = meta.get("provisional_root_pov_gap_best_minus_model", meta.get("teacher_move_policy_rank", ""))
        md.append(
            f"| `{r['id']}` | `{r['source_id']}` | {r['bucket']} | {r['side_to_move']} | "
            f"`{r['teacher_move']}` | `{model}` | {gap_or_rank} | {r['suggested_weight']} |"
        )
    md.append("")
    md.append("## Skipped score-gap rows")
    md.append("")
    md.append("| source_id | skip_reason | teacher | model | gap |")
    md.append("|---|---|---|---|---:|")
    for r in manifest_rows:
        if r["source_path"] != str(SCOREGAP_CSV) or r["included"]:
            continue
        md.append(
            f"| `{r['source_id']}` | {r['skip_reason']} | `{r['teacher_move']}` | "
            f"`{r['current_best_direct_move']}` | {r['numeric_gap_value']} |"
        )
    md.append("")
    md.append("## Interpretation")
    md.append("")
    md.append("- Canonical baseline rows come only from `teacher_divergence_retention_dataset.json`.")
    md.append("- Old manifest/probe/validation files are no longer treated as sample sources, avoiding double-counting.")
    md.append("- Score-gap rows are added only when Rapfi has a concrete teacher move, current-best disagrees, and the before-board file is available.")
    md.append("- Retention anchors are held out and should not be mixed into the teacher-divergence training split.")
    md.append("")

    OUT_REPORT.write_text("\n".join(md) + "\n", encoding="utf-8")


def main() -> None:
    dataset_rows = []
    manifest_rows = []
    audits = []

    baseline_rows, baseline_manifest, baseline_audit = load_baseline()
    dataset_rows.extend(baseline_rows)
    manifest_rows.extend(baseline_manifest)
    audits.append(baseline_audit)

    existing_ids = get_existing_source_ids(dataset_rows)

    candidate_rows, candidate_manifest, candidate_audit = load_candidate_g(existing_ids)
    dataset_rows.extend(candidate_rows)
    manifest_rows.extend(candidate_manifest)
    audits.append(candidate_audit)

    existing_ids = get_existing_source_ids(dataset_rows)

    scoregap_rows, scoregap_manifest, scoregap_audit = load_scoregap(existing_ids)
    dataset_rows.extend(scoregap_rows)
    manifest_rows.extend(scoregap_manifest)
    audits.append(scoregap_audit)

    existing_ids = get_existing_source_ids(dataset_rows)

    retention_rows, retention_manifest, retention_audits = load_retention_anchors(existing_ids)
    dataset_rows.extend(retention_rows)
    manifest_rows.extend(retention_manifest)
    audits.extend(retention_audits)

    write_outputs(dataset_rows, manifest_rows, audits)

    print("wrote", OUT_DATASET)
    print("wrote", OUT_MANIFEST)
    print("wrote", OUT_AUDIT)
    print("wrote", OUT_REPORT)
    print()

    print("dataset_rows", len(dataset_rows))
    print("split_counts", dict(Counter(r.get("split", "") for r in dataset_rows)))
    print("role_counts", dict(Counter(r.get("role", "") for r in dataset_rows)))
    print("bucket_counts", dict(Counter(r.get("bucket", "") for r in dataset_rows)))
    print("source_counts", dict(Counter(r.get("metadata", {}).get("clean_v2_source", "unknown") for r in dataset_rows)))

    included = [r for r in manifest_rows if r["included"]]
    skipped = [r for r in manifest_rows if not r["included"]]
    print("manifest_rows", len(manifest_rows))
    print("manifest_included", len(included))
    print("manifest_skipped", len(skipped))


if __name__ == "__main__":
    main()
