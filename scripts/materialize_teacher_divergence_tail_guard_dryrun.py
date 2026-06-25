#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any


OUT_DIR = Path("analysis/integration_eval/teacher_divergence_tail_guard_materialization_dryrun")
OUT_DATASET = Path(
    "analysis/public_benchmark_eval/"
    "rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_conservative_plus_generated_tail_guards_dryrun.json"
)
OUT_MANIFEST = OUT_DIR / "tail_guard_materialization_manifest.csv"
OUT_SUMMARY = OUT_DIR / "tail_guard_materialization_summary.json"
OUT_REPORT = OUT_DIR / "tail_guard_materialization_report.md"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=(
            "Materialize generated tail guard candidates into heldout tail_eval_samples only. "
            "Dry-run dataset build only; no training/checkpoint/export/benchmark/promotion."
        )
    )
    p.add_argument(
        "--base-dataset",
        type=Path,
        default=Path(
            "analysis/public_benchmark_eval/"
            "rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_conservative_selection_next.json"
        ),
    )
    p.add_argument(
        "--candidate-source",
        type=Path,
        default=Path(
            "analysis/integration_eval/"
            "teacher_divergence_tail_guard_candidate_generation/"
            "tail_guard_candidate_source.json"
        ),
    )
    p.add_argument("--max-new-tail-guards", type=int, default=12)
    p.add_argument("--board-size", type=int, default=15)
    p.add_argument("--tail-rank-threshold", type=int, default=50)
    return p.parse_args()


def read_json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def board_hash(board: list[list[int]]) -> str:
    raw = json.dumps(board, separators=(",", ":"), sort_keys=False)
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]


def validate_board(board: Any, board_size: int) -> list[list[int]]:
    if not isinstance(board, list) or len(board) != board_size:
        raise ValueError("board must be list[list[int]] with board_size rows")
    out: list[list[int]] = []
    for row in board:
        if not isinstance(row, list) or len(row) != board_size:
            raise ValueError("board row has wrong length")
        out.append([int(x) for x in row])
    return out


def validate_rc(rc: Any, board_size: int) -> tuple[int, int]:
    if not isinstance(rc, list) or len(rc) != 2:
        raise ValueError(f"bad rc: {rc!r}")
    r, c = int(rc[0]), int(rc[1])
    if not (0 <= r < board_size and 0 <= c < board_size):
        raise ValueError(f"rc out of range: {rc!r}")
    return r, c


def legal_empty(board: list[list[int]], rc: tuple[int, int]) -> bool:
    r, c = rc
    return int(board[r][c]) == 0


def identity(row: dict[str, Any], board_size: int) -> str:
    board = validate_board(row["board"], board_size)
    target_rc = validate_rc(row["target_rc"], board_size)
    return f"{board_hash(board)}:{target_rc[0]}:{target_rc[1]}"


def existing_identities(base: dict[str, Any], board_size: int) -> tuple[set[str], set[str]]:
    case_ids: set[str] = set()
    identities: set[str] = set()

    for group in ["samples", "protected_eval_samples", "tail_eval_samples", "quarantine_samples"]:
        for row in base.get(group, []) or []:
            if not isinstance(row, dict):
                continue
            if row.get("case_id"):
                case_ids.add(str(row["case_id"]))
            try:
                identities.add(identity(row, board_size))
            except Exception:
                pass

    return case_ids, identities


def review_candidate(
    row: dict[str, Any],
    *,
    board_size: int,
    tail_rank_threshold: int,
    seen_case_ids: set[str],
    seen_identities: set[str],
) -> tuple[bool, str]:
    if row.get("candidate_bucket") != "P0_tail_guard_candidate":
        return False, "not_p0_tail_guard_candidate"

    case_id = str(row.get("case_id", ""))
    if not case_id:
        return False, "missing_case_id"
    if case_id in seen_case_ids:
        return False, "case_id_already_exists"

    if row.get("training_allowed") is not False:
        return False, "training_allowed_not_false"

    try:
        board = validate_board(row.get("board"), board_size)
        target_rc = validate_rc(row.get("target_rc"), board_size)
        primary_suppress_rc = validate_rc(row.get("primary_suppress_rc"), board_size)
        suppress_rcs = row.get("suppress_rcs")
        if not isinstance(suppress_rcs, list) or len(suppress_rcs) < 5:
            return False, "too_few_suppress_rcs"
        for rc in suppress_rcs:
            validate_rc(rc, board_size)
    except Exception as exc:
        return False, f"schema_invalid:{type(exc).__name__}"

    if not legal_empty(board, target_rc):
        return False, "target_not_empty"
    if not legal_empty(board, primary_suppress_rc):
        return False, "primary_suppress_not_empty"

    try:
        rank = int(row.get("before_target_rank"))
    except Exception:
        return False, "missing_or_bad_rank"

    if rank <= tail_rank_threshold:
        return False, "rank_not_tail"

    row_identity = identity(row, board_size)
    if row_identity in seen_identities:
        return False, "board_target_identity_already_exists"

    return True, "accepted_tail_eval_heldout"


def materialize_tail_row(row: dict[str, Any], board_size: int) -> dict[str, Any]:
    out = deepcopy(row)

    target_rc = validate_rc(out["target_rc"], board_size)
    out["target_xy"] = [target_rc[1], target_rc[0]]

    out["source"] = "generated_tail_guard_candidate_materialization_dryrun"
    out["source_candidate_case_id"] = row["case_id"]
    out["label_type"] = "generated_tail_guard_heldout"
    out["suggested_bucket"] = "tail_rank_gt50"
    out["suggested_split"] = "tail_eval_rank_gt50_heldout_only"
    out["split"] = "tail_eval"
    out["training_allowed"] = False
    out["sample_weight"] = 0.0
    out["effective_sample_weight"] = 0.0
    out["materialization_status"] = "dryrun_materialized_tail_eval_only"
    out["materialization_notes"] = (
        "Generated tail guard row. Heldout eval only. "
        "Do not use as train sample without a separate gate-policy change."
    )

    out.setdefault("teacher_move", None)
    out.setdefault("teacher_eval_before", None)
    out.setdefault("teacher_eval_kind", "generated_tail_candidate_no_teacher_numeric_eval")
    out.setdefault("numeric_gap_available", False)
    out.setdefault("numeric_gap_value", None)
    out.setdefault("validation_notes", [])

    return out


def main() -> int:
    args = parse_args()

    base = read_json(args.base_dataset)
    candidate_source = read_json(args.candidate_source)

    if not isinstance(base, dict):
        raise ValueError("base dataset must be dict")
    if not isinstance(candidate_source, dict):
        raise ValueError("candidate source must be dict")

    for key in ["samples", "protected_eval_samples", "tail_eval_samples", "quarantine_samples"]:
        if key not in base:
            raise ValueError(f"base dataset missing {key}")

    source_candidates = candidate_source.get("tail_guard_candidates", [])
    if not isinstance(source_candidates, list):
        raise ValueError("candidate source tail_guard_candidates must be list")

    seen_case_ids, seen_identities = existing_identities(base, args.board_size)

    manifest_rows: list[dict[str, Any]] = []
    accepted_rows: list[dict[str, Any]] = []

    # Highest-rank tail candidates first.
    ranked_candidates = sorted(
        source_candidates,
        key=lambda r: (
            -int(r.get("before_target_rank", -1)),
            float(r.get("before_target_prob", 0.0)),
            str(r.get("case_id", "")),
        ),
    )

    for row in ranked_candidates:
        ok, reason = review_candidate(
            row,
            board_size=args.board_size,
            tail_rank_threshold=args.tail_rank_threshold,
            seen_case_ids=seen_case_ids,
            seen_identities=seen_identities,
        )

        selected = False
        materialized_case_id = ""

        if ok and len(accepted_rows) < args.max_new_tail_guards:
            new_row = materialize_tail_row(row, args.board_size)
            accepted_rows.append(new_row)
            seen_case_ids.add(str(new_row["case_id"]))
            seen_identities.add(identity(new_row, args.board_size))
            selected = True
            materialized_case_id = str(new_row["case_id"])
        elif ok:
            reason = "accepted_but_over_max_new_tail_guard_cap"

        manifest_rows.append(
            {
                "case_id": row.get("case_id", ""),
                "candidate_bucket": row.get("candidate_bucket", ""),
                "game_number": row.get("game_number", ""),
                "move_count": row.get("move_count", ""),
                "side_to_move": row.get("side_to_move", ""),
                "target_rc": json.dumps(row.get("target_rc", [])),
                "before_target_rank": row.get("before_target_rank", ""),
                "before_target_prob": row.get("before_target_prob", ""),
                "target_source_field": row.get("target_source_field", ""),
                "review_decision": reason,
                "selected_for_dryrun_tail_eval": int(selected),
                "materialized_case_id": materialized_case_id,
            }
        )

    out_dataset = deepcopy(base)
    out_dataset["name"] = "rapfi_teacher_policy_multisuppress_conservative_plus_generated_tail_guards_dryrun"
    out_dataset["description"] = (
        "Dry-run dataset with generated P0 tail guard candidates added to tail_eval_samples only. "
        "Not a training route and not a promotion candidate."
    )
    out_dataset["source_dataset"] = str(args.base_dataset)
    out_dataset["generated_tail_candidate_source"] = str(args.candidate_source)
    out_dataset["scope"] = "materialization dry-run only; no training/checkpoint/export/benchmark/promotion"
    out_dataset["materialization_policy"] = {
        "accepted_group": "tail_eval_samples",
        "max_new_tail_guards": args.max_new_tail_guards,
        "tail_rank_threshold": args.tail_rank_threshold,
        "training_allowed_for_generated_tail_rows": False,
        "samples_modified": False,
        "protected_eval_samples_modified": False,
        "quarantine_samples_modified": False,
    }
    out_dataset["tail_eval_samples"] = list(base.get("tail_eval_samples", [])) + accepted_rows
    out_dataset["generated_tail_guard_review_rows"] = manifest_rows

    before_counts = {
        "samples": len(base.get("samples", [])),
        "protected_eval_samples": len(base.get("protected_eval_samples", [])),
        "tail_eval_samples": len(base.get("tail_eval_samples", [])),
        "quarantine_samples": len(base.get("quarantine_samples", [])),
    }
    after_counts = {
        "samples": len(out_dataset.get("samples", [])),
        "protected_eval_samples": len(out_dataset.get("protected_eval_samples", [])),
        "tail_eval_samples": len(out_dataset.get("tail_eval_samples", [])),
        "quarantine_samples": len(out_dataset.get("quarantine_samples", [])),
    }

    decision = (
        "TAIL_GUARD_MATERIALIZATION_DRYRUN_TARGET_MET"
        if len(accepted_rows) >= args.max_new_tail_guards
        else "TAIL_GUARD_MATERIALIZATION_DRYRUN_PARTIAL"
        if accepted_rows
        else "TAIL_GUARD_MATERIALIZATION_DRYRUN_NO_ACCEPTED_ROWS"
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    write_json(OUT_DATASET, out_dataset)

    with OUT_MANIFEST.open("w", newline="", encoding="utf-8") as f:
        fields = [
            "case_id",
            "candidate_bucket",
            "game_number",
            "move_count",
            "side_to_move",
            "target_rc",
            "before_target_rank",
            "before_target_prob",
            "target_source_field",
            "review_decision",
            "selected_for_dryrun_tail_eval",
            "materialized_case_id",
        ]
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(manifest_rows)

    summary = {
        "decision": decision,
        "scope": "materialization dry-run only; no training/checkpoint/export/benchmark/promotion",
        "base_dataset": str(args.base_dataset),
        "candidate_source": str(args.candidate_source),
        "out_dataset": str(OUT_DATASET),
        "source_tail_candidates": len(source_candidates),
        "accepted_new_tail_guards": len(accepted_rows),
        "max_new_tail_guards": args.max_new_tail_guards,
        "before_counts": before_counts,
        "after_counts": after_counts,
        "review_decision_counts": {
            k: sum(1 for r in manifest_rows if r["review_decision"] == k)
            for k in sorted({r["review_decision"] for r in manifest_rows})
        },
        "outputs": {
            "dataset": str(OUT_DATASET),
            "manifest": str(OUT_MANIFEST),
            "summary": str(OUT_SUMMARY),
            "report": str(OUT_REPORT),
        },
    }
    write_json(OUT_SUMMARY, summary)

    lines: list[str] = []
    lines += ["# Teacher-divergence tail guard materialization dry-run", ""]
    lines += ["## Scope", ""]
    lines += [
        "- Materialization dry-run only.",
        "- Generated tail candidates are added only to `tail_eval_samples`.",
        "- `samples` train rows are unchanged.",
        "- No training.",
        "- No checkpoint save.",
        "- No C export, no public benchmark, no promotion.",
        "",
    ]

    lines += ["## Inputs", ""]
    lines += [
        f"- base dataset: `{args.base_dataset}`",
        f"- candidate source: `{args.candidate_source}`",
        f"- max new tail guards: `{args.max_new_tail_guards}`",
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
    for k, v in summary["review_decision_counts"].items():
        lines.append(f"| {k} | {v} |")
    lines.append("")

    lines += ["## Accepted rows", ""]
    lines += ["| case_id | game | move | side | target_rc | rank | prob | source_field |", "|---|---:|---:|---|---|---:|---:|---|"]
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
    print("source_tail_candidates:", len(source_candidates))
    print("accepted_new_tail_guards:", len(accepted_rows))
    print("before_counts:", before_counts)
    print("after_counts:", after_counts)
    print("review_decision_counts:", summary["review_decision_counts"])
    print("out_dataset:", OUT_DATASET)
    print("out_manifest:", OUT_MANIFEST)
    print("out_summary:", OUT_SUMMARY)
    print("out_report:", OUT_REPORT)
    print("status: materialization dry-run only; no training/checkpoint/export/benchmark/promotion")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
