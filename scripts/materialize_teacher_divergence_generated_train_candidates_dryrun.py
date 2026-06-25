#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any


OUT_DIR = Path("analysis/integration_eval/teacher_divergence_generated_train_candidate_materialization")
OUT_DATASET = Path(
    "analysis/public_benchmark_eval/"
    "rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_conservative_plus_generated_tail_guards_plus_generated_train_candidates_dryrun.json"
)
OUT_MANIFEST = OUT_DIR / "generated_train_candidate_materialization_manifest.csv"
OUT_SUMMARY = OUT_DIR / "generated_train_candidate_materialization_summary.json"
OUT_REPORT = OUT_DIR / "generated_train_candidate_materialization_report.md"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=(
            "Materialize generated P1 train candidates into samples. "
            "Dry-run dataset build only; no training/checkpoint/export/benchmark/promotion."
        )
    )
    p.add_argument(
        "--base-dataset",
        type=Path,
        default=Path(
            "analysis/public_benchmark_eval/"
            "rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_conservative_plus_generated_tail_guards_dryrun.json"
        ),
    )
    p.add_argument(
        "--candidate-source",
        type=Path,
        default=Path(
            "analysis/integration_eval/"
            "teacher_divergence_train_candidate_generation/"
            "train_candidate_source.json"
        ),
    )
    p.add_argument("--board-size", type=int, default=15)
    p.add_argument("--max-new-train-candidates", type=int, default=8)
    p.add_argument("--min-new-train-candidates", type=int, default=8)
    p.add_argument("--train-rank-min", type=int, default=11)
    p.add_argument("--train-rank-max", type=int, default=50)
    return p.parse_args()


def read_json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def validate_rc(rc: Any, board_size: int) -> tuple[int, int]:
    if not isinstance(rc, list) or len(rc) != 2:
        raise ValueError(f"bad rc: {rc!r}")
    r, c = int(rc[0]), int(rc[1])
    if not (0 <= r < board_size and 0 <= c < board_size):
        raise ValueError(f"rc out of range: {rc!r}")
    return r, c


def validate_board(board: Any, board_size: int) -> list[list[int]]:
    if not isinstance(board, list) or len(board) != board_size:
        raise ValueError("board must be board_size x board_size list")
    out: list[list[int]] = []
    for row in board:
        if not isinstance(row, list) or len(row) != board_size:
            raise ValueError("board row has wrong length")
        out.append([int(x) for x in row])
    return out


def board_hash(board: list[list[int]]) -> str:
    raw = json.dumps(board, separators=(",", ":"), sort_keys=False)
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]


def row_identity(row: dict[str, Any], board_size: int) -> str:
    board = validate_board(row["board"], board_size)
    target_rc = validate_rc(row["target_rc"], board_size)
    return f"{board_hash(board)}:{target_rc[0]}:{target_rc[1]}"


def legal_empty(board: list[list[int]], rc: tuple[int, int]) -> bool:
    r, c = rc
    return int(board[r][c]) == 0


def collect_existing(base: dict[str, Any], board_size: int) -> tuple[set[str], set[str]]:
    case_ids: set[str] = set()
    identities: set[str] = set()

    for group in ["samples", "protected_eval_samples", "tail_eval_samples", "quarantine_samples"]:
        for row in base.get(group, []) or []:
            if not isinstance(row, dict):
                continue
            if row.get("case_id"):
                case_ids.add(str(row["case_id"]))
            try:
                identities.add(row_identity(row, board_size))
            except Exception:
                pass

    return case_ids, identities


def validate_candidate(
    row: dict[str, Any],
    *,
    existing_case_ids: set[str],
    existing_identities: set[str],
    board_size: int,
    train_rank_min: int,
    train_rank_max: int,
) -> tuple[bool, str]:
    case_id = str(row.get("case_id", ""))
    if not case_id:
        return False, "missing_case_id"
    if case_id in existing_case_ids:
        return False, "case_id_already_exists"

    if row.get("candidate_bucket") != "P1_train_candidate":
        return False, f"not_p1_train_candidate:{row.get('candidate_bucket')}"
    if row.get("training_allowed") is not True:
        return False, "training_allowed_not_true"

    try:
        rank = int(row.get("before_target_rank"))
    except Exception:
        return False, "bad_rank"
    if not (train_rank_min <= rank <= train_rank_max):
        return False, "rank_outside_train_band"

    try:
        board = validate_board(row.get("board"), board_size)
        target_rc = validate_rc(row.get("target_rc"), board_size)
        primary_suppress_rc = validate_rc(row.get("primary_suppress_rc"), board_size)
        suppress_rcs = row.get("suppress_rcs")
        if not isinstance(suppress_rcs, list) or len(suppress_rcs) < 1:
            return False, "missing_suppress_rcs"
        for rc in suppress_rcs:
            validate_rc(rc, board_size)
    except Exception as exc:
        return False, f"schema_invalid:{type(exc).__name__}"

    if not legal_empty(board, target_rc):
        return False, "target_not_empty"
    if not legal_empty(board, primary_suppress_rc):
        return False, "primary_suppress_not_empty"
    for rc in suppress_rcs:
        if not legal_empty(board, validate_rc(rc, board_size)):
            return False, "suppress_not_empty"

    try:
        ident = row_identity(row, board_size)
    except Exception as exc:
        return False, f"identity_failed:{type(exc).__name__}"

    if ident in existing_identities:
        return False, "board_target_identity_already_exists"

    return True, "accepted_generated_train_candidate"


def materialize_row(row: dict[str, Any]) -> dict[str, Any]:
    out = deepcopy(row)
    out["source"] = "generated_train_candidate_materialization_dryrun"
    out["source_candidate_generation"] = "teacher_divergence_train_candidate_generation"
    out["label_type"] = "generated_train_candidate"
    out["suggested_bucket"] = "trainable_rank_11_50_generated"
    out["split"] = "train"
    out["training_allowed"] = True
    out["materialization_status"] = "dryrun_materialized_generated_train_candidate"
    out["materialization_notes"] = (
        "Generated P1 train candidate materialized into samples by dry-run only. "
        "Requires no-save gate before any checkpoint-producing route."
    )
    out["sample_weight"] = float(out.get("sample_weight", 1.0))
    out["effective_sample_weight"] = float(out.get("effective_sample_weight", out["sample_weight"]))
    return out


def main() -> int:
    args = parse_args()

    base = read_json(args.base_dataset)
    if not isinstance(base, dict):
        raise ValueError("base dataset must be dict")

    for key in ["samples", "protected_eval_samples", "tail_eval_samples", "quarantine_samples"]:
        if key not in base or not isinstance(base[key], list):
            raise ValueError(f"base dataset missing list group: {key}")

    source = read_json(args.candidate_source)
    if not isinstance(source, dict):
        raise ValueError("candidate source must be dict")

    source_train_candidates = source.get("train_candidates")
    if not isinstance(source_train_candidates, list):
        raise ValueError("candidate source missing train_candidates list")

    existing_case_ids, existing_identities = collect_existing(base, args.board_size)

    review_rows: list[dict[str, Any]] = []
    accepted_rows: list[dict[str, Any]] = []

    sorted_candidates = sorted(
        source_train_candidates,
        key=lambda r: (
            -int(r.get("before_target_rank", 0)),
            float(r.get("before_target_prob", 999.0)),
            str(r.get("case_id", "")),
        ),
    )

    for row in sorted_candidates:
        ok, decision = validate_candidate(
            row,
            existing_case_ids=existing_case_ids,
            existing_identities=existing_identities,
            board_size=args.board_size,
            train_rank_min=args.train_rank_min,
            train_rank_max=args.train_rank_max,
        )

        selected = False
        if ok and len(accepted_rows) < args.max_new_train_candidates:
            new_row = materialize_row(row)
            accepted_rows.append(new_row)
            existing_case_ids.add(str(new_row["case_id"]))
            existing_identities.add(row_identity(new_row, args.board_size))
            selected = True
        elif ok:
            decision = "accepted_but_over_max_new_train_candidate_cap"

        review_rows.append(
            {
                "case_id": row.get("case_id", ""),
                "candidate_bucket": row.get("candidate_bucket", ""),
                "game_number": row.get("game_number", ""),
                "move_count": row.get("move_count", ""),
                "side_to_move": row.get("side_to_move", ""),
                "target_rc": json.dumps(row.get("target_rc", []), sort_keys=True),
                "before_target_rank": row.get("before_target_rank", ""),
                "before_target_prob": row.get("before_target_prob", ""),
                "before_primary_gap": row.get("before_primary_gap", ""),
                "before_worst_suppress_gap": row.get("before_worst_suppress_gap", ""),
                "target_source_field": row.get("target_source_field", ""),
                "training_allowed": row.get("training_allowed", ""),
                "review_decision": decision,
                "selected_for_train_dryrun": int(selected),
            }
        )

    out_dataset = deepcopy(base)
    out_dataset["name"] = (
        "rapfi_teacher_policy_multisuppress_conservative_plus_generated_tail_guards_plus_generated_train_candidates_dryrun"
    )
    out_dataset["description"] = (
        "Dry-run dataset with generated tail guards held out and generated P1 train candidates added to samples. "
        "Not a checkpoint-producing route and not a promotion candidate."
    )
    out_dataset["source_dataset"] = str(args.base_dataset)
    out_dataset["generated_train_candidate_source"] = str(args.candidate_source)
    out_dataset["scope"] = "generated train candidate materialization dry-run only; no training/checkpoint/export/benchmark/promotion"
    out_dataset["materialization_policy"] = {
        "accepted_group": "samples",
        "max_new_train_candidates": args.max_new_train_candidates,
        "min_new_train_candidates": args.min_new_train_candidates,
        "rank_band": [args.train_rank_min, args.train_rank_max],
        "protected_eval_samples_modified": False,
        "tail_eval_samples_modified": False,
        "quarantine_samples_modified": False,
    }
    out_dataset["samples"] = list(base["samples"]) + accepted_rows
    out_dataset["generated_train_candidate_review_rows"] = review_rows

    before_counts = {
        "samples": len(base["samples"]),
        "protected_eval_samples": len(base["protected_eval_samples"]),
        "tail_eval_samples": len(base["tail_eval_samples"]),
        "quarantine_samples": len(base["quarantine_samples"]),
    }
    after_counts = {
        "samples": len(out_dataset["samples"]),
        "protected_eval_samples": len(out_dataset["protected_eval_samples"]),
        "tail_eval_samples": len(out_dataset["tail_eval_samples"]),
        "quarantine_samples": len(out_dataset["quarantine_samples"]),
    }

    decision_counts = {
        k: sum(1 for r in review_rows if r["review_decision"] == k)
        for k in sorted({r["review_decision"] for r in review_rows})
    }

    decision = (
        "GENERATED_TRAIN_CANDIDATE_MATERIALIZATION_DRYRUN_TARGET_MET"
        if len(accepted_rows) >= args.min_new_train_candidates
        else "GENERATED_TRAIN_CANDIDATE_MATERIALIZATION_DRYRUN_PARTIAL"
        if accepted_rows
        else "GENERATED_TRAIN_CANDIDATE_MATERIALIZATION_DRYRUN_NO_ACCEPTED_ROWS"
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(OUT_DATASET, out_dataset)

    fields = [
        "case_id",
        "candidate_bucket",
        "game_number",
        "move_count",
        "side_to_move",
        "target_rc",
        "before_target_rank",
        "before_target_prob",
        "before_primary_gap",
        "before_worst_suppress_gap",
        "target_source_field",
        "training_allowed",
        "review_decision",
        "selected_for_train_dryrun",
    ]
    with OUT_MANIFEST.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(review_rows)

    summary = {
        "decision": decision,
        "scope": "generated train candidate materialization dry-run only; no training/checkpoint/export/benchmark/promotion",
        "base_dataset": str(args.base_dataset),
        "candidate_source": str(args.candidate_source),
        "out_dataset": str(OUT_DATASET),
        "source_train_candidates": len(source_train_candidates),
        "accepted_new_train_candidates": len(accepted_rows),
        "max_new_train_candidates": args.max_new_train_candidates,
        "min_new_train_candidates": args.min_new_train_candidates,
        "before_counts": before_counts,
        "after_counts": after_counts,
        "review_decision_counts": decision_counts,
        "outputs": {
            "dataset": str(OUT_DATASET),
            "manifest": str(OUT_MANIFEST),
            "summary": str(OUT_SUMMARY),
            "report": str(OUT_REPORT),
        },
    }
    write_json(OUT_SUMMARY, summary)

    lines: list[str] = []
    lines += ["# Teacher-divergence generated train candidate materialization dry-run", ""]
    lines += ["## Scope", ""]
    lines += [
        "- Generated train candidate materialization dry-run only.",
        "- Accepted rows are added only to `samples`.",
        "- `protected_eval_samples`, `tail_eval_samples`, and `quarantine_samples` are unchanged.",
        "- No training.",
        "- No checkpoint save.",
        "- No C export, no public benchmark, no promotion.",
        "",
    ]

    lines += ["## Inputs", ""]
    lines += [
        f"- base dataset: `{args.base_dataset}`",
        f"- candidate source: `{args.candidate_source}`",
        f"- max new train candidates: `{args.max_new_train_candidates}`",
        f"- min new train candidates: `{args.min_new_train_candidates}`",
        f"- rank band: `{args.train_rank_min}` to `{args.train_rank_max}`",
        "",
    ]

    lines += ["## Counts", ""]
    lines += ["| group | before | after | delta |", "|---|---:|---:|---:|"]
    for group in ["samples", "protected_eval_samples", "tail_eval_samples", "quarantine_samples"]:
        b = before_counts[group]
        a = after_counts[group]
        lines.append(f"| {group} | {b} | {a} | {a - b} |")
    lines.append("")

    lines += ["## Review decisions", ""]
    lines += ["| decision | count |", "|---|---:|"]
    for k, v in decision_counts.items():
        lines.append(f"| {k} | {v} |")
    lines.append("")

    lines += ["## Accepted rows", ""]
    lines += [
        "| case_id | game | move | side | target_rc | rank | prob | source_field |",
        "|---|---:|---:|---|---|---:|---:|---|",
    ]
    for row in accepted_rows:
        lines.append(
            f"| `{row['case_id']}` | {row.get('game_number')} | {row.get('move_count')} | "
            f"{row.get('side_to_move')} | `{row.get('target_rc')}` | "
            f"{row.get('before_target_rank')} | {float(row.get('before_target_prob', 0.0)):.6g} | "
            f"`{row.get('target_source_field')}` |"
        )
    if not accepted_rows:
        lines.append("| _none_ |  |  |  |  |  |  |  |")
    lines.append("")

    lines += ["## Decision", ""]
    lines += [f"`{decision}`", ""]

    lines += ["## Final note", ""]
    lines += [
        "This dry-run does not authorize training, checkpoint save, C export, public benchmark, promotion, or current_best overwrite.",
        "",
    ]

    OUT_REPORT.write_text("\n".join(lines), encoding="utf-8")

    print("decision:", decision)
    print("source_train_candidates:", len(source_train_candidates))
    print("accepted_new_train_candidates:", len(accepted_rows))
    print("before_counts:", before_counts)
    print("after_counts:", after_counts)
    print("review_decision_counts:", decision_counts)
    print("out_dataset:", OUT_DATASET)
    print("out_manifest:", OUT_MANIFEST)
    print("out_summary:", OUT_SUMMARY)
    print("out_report:", OUT_REPORT)
    print("status: generated train candidate materialization dry-run only; no training/checkpoint/export/benchmark/promotion")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
