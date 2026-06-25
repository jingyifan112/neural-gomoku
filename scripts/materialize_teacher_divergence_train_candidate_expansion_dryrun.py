#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any


OUT_DIR = Path("analysis/integration_eval/teacher_divergence_train_candidate_expansion_materialize")
OUT_DATASET = Path(
    "analysis/public_benchmark_eval/"
    "rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_conservative_plus_generated_tail_guards_plus_train_candidates_dryrun.json"
)
OUT_MANIFEST = OUT_DIR / "train_candidate_materialization_manifest.csv"
OUT_SUMMARY = OUT_DIR / "train_candidate_materialization_summary.json"
OUT_REPORT = OUT_DIR / "train_candidate_materialization_report.md"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=(
            "Materialize safe P1 train candidates into samples. "
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
        "--source-manifest",
        type=Path,
        default=Path(
            "analysis/integration_eval/"
            "teacher_divergence_expansion_source_audit_next/"
            "source_candidate_manifest.csv"
        ),
    )
    p.add_argument("--max-new-train-candidates", type=int, default=15)
    p.add_argument("--board-size", type=int, default=15)
    p.add_argument("--min-train-rank", type=int, default=11)
    p.add_argument("--max-train-rank", type=int, default=50)
    return p.parse_args()


def read_json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_bool(x: Any) -> bool:
    return str(x).strip().lower() in {"1", "true", "yes", "y"}


def parse_float(x: Any, default: float = float("nan")) -> float:
    try:
        return float(x)
    except Exception:
        return default


def board_hash(board: list[list[int]]) -> str:
    raw = json.dumps(board, separators=(",", ":"), sort_keys=False)
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]


def validate_board(board: Any, board_size: int) -> list[list[int]]:
    if not isinstance(board, list) or len(board) != board_size:
        raise ValueError("board must be board_size x board_size list")
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


def identity_from_row(row: dict[str, Any], board_size: int) -> str:
    board = validate_board(row["board"], board_size)
    target_rc = validate_rc(row["target_rc"], board_size)
    return f"{board_hash(board)}:{target_rc[0]}:{target_rc[1]}"


def resolve_json_path(obj: Any, path: str) -> Any:
    if not path.startswith("$."):
        raise ValueError(f"unsupported json path: {path}")

    cur = obj
    rest = path[2:]

    # Supports forms like samples[3].foo or $.samples[3]
    parts = rest.split(".")
    for part in parts:
        m = re.fullmatch(r"([A-Za-z0-9_]+)(?:\[(\d+)\])?", part)
        if not m:
            raise ValueError(f"unsupported json path part: {part}")
        key, idx = m.group(1), m.group(2)
        if not isinstance(cur, dict) or key not in cur:
            raise KeyError(f"path key missing: {key}")
        cur = cur[key]
        if idx is not None:
            if not isinstance(cur, list):
                raise TypeError(f"path target not list for index: {part}")
            cur = cur[int(idx)]
    return cur


def load_source_row(source_path: Path, source_json_path: str) -> dict[str, Any]:
    data = read_json(source_path)
    row = resolve_json_path(data, source_json_path)
    if not isinstance(row, dict):
        raise ValueError("resolved source row is not dict")
    return row


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
                identities.add(identity_from_row(row, board_size))
            except Exception:
                pass

    return case_ids, identities


def review_manifest_row(
    manifest_row: dict[str, str],
    *,
    existing_case_ids: set[str],
    existing_identities: set[str],
    board_size: int,
    min_train_rank: int,
    max_train_rank: int,
) -> tuple[bool, str, dict[str, Any] | None]:
    case_id = manifest_row.get("case_id", "")
    rank = parse_float(manifest_row.get("rank"))

    if not case_id:
        return False, "missing_case_id", None
    if case_id in existing_case_ids:
        return False, "case_id_already_exists", None

    if parse_bool(manifest_row.get("already_selected")):
        return False, "already_selected", None
    if not parse_bool(manifest_row.get("train_candidate")):
        return False, "not_train_candidate", None
    if parse_bool(manifest_row.get("tail_candidate")):
        return False, "tail_candidate_excluded_from_train", None
    if parse_bool(manifest_row.get("protected_candidate")):
        return False, "protected_candidate_excluded_from_train", None
    if parse_bool(manifest_row.get("has_quarantine_words")):
        return False, "quarantine_words_excluded", None

    role = manifest_row.get("role", "")
    risk = manifest_row.get("risk", "")
    flags = manifest_row.get("flags", "")

    forbidden_role_tokens = [
        "protected_guard_holdout",
        "tail_guard_holdout",
        "quarantine_regression_sensitive",
        "heldout_retention_anchor",
        "audit_only",
        "public_failure_snapshot_audit",
    ]
    if any(tok in role for tok in forbidden_role_tokens):
        return False, f"forbidden_role:{role}", None

    if any(tok in risk.lower() for tok in ["hard", "high", "quarantine"]):
        return False, f"forbidden_risk:{risk}", None
    if any(tok in flags.lower() for tok in ["quarantine", "protected", "tail_guard"]):
        return False, "forbidden_flags", None

    if not (min_train_rank <= rank <= max_train_rank):
        return False, "rank_outside_train_band", None

    source_path = Path(manifest_row.get("source_path", ""))
    source_json_path = manifest_row.get("source_json_path", "")

    try:
        source_row = load_source_row(source_path, source_json_path)
    except Exception as exc:
        return False, f"source_load_failed:{type(exc).__name__}", None

    try:
        board = validate_board(source_row.get("board"), board_size)
        target_rc = validate_rc(source_row.get("target_rc"), board_size)
        suppress_rcs = source_row.get("suppress_rcs")
        if not isinstance(suppress_rcs, list) or len(suppress_rcs) < 1:
            return False, "missing_suppress_rcs", None
        for rc in suppress_rcs:
            validate_rc(rc, board_size)
        primary_suppress_rc = source_row.get("primary_suppress_rc", suppress_rcs[0])
        validate_rc(primary_suppress_rc, board_size)
    except Exception as exc:
        return False, f"schema_invalid:{type(exc).__name__}", None

    if not legal_empty(board, target_rc):
        return False, "target_not_empty", None
    for rc in suppress_rcs:
        if not legal_empty(board, validate_rc(rc, board_size)):
            return False, "suppress_not_empty", None

    try:
        ident = identity_from_row(source_row, board_size)
    except Exception as exc:
        return False, f"identity_failed:{type(exc).__name__}", None

    if ident in existing_identities:
        return False, "board_target_identity_already_exists", None

    return True, "accepted_train_candidate_dryrun", source_row


def materialize_train_row(
    source_row: dict[str, Any],
    manifest_row: dict[str, str],
    *,
    board_size: int,
) -> dict[str, Any]:
    out = deepcopy(source_row)
    target_rc = validate_rc(out["target_rc"], board_size)

    out["case_id"] = manifest_row["case_id"]
    out["source"] = "train_candidate_expansion_materialization_dryrun"
    out["source_path"] = manifest_row.get("source_path", "")
    out["source_json_path"] = manifest_row.get("source_json_path", "")
    out["source_role"] = manifest_row.get("role", "")
    out["source_rank"] = parse_float(manifest_row.get("rank"))
    out["source_prob"] = parse_float(manifest_row.get("prob"))
    out["target_xy"] = [target_rc[1], target_rc[0]]

    out["label_type"] = "generated_train_candidate_review"
    out["suggested_bucket"] = "trainable_rank_11_50"
    out["split"] = "train"
    out["training_allowed"] = True
    out["materialization_status"] = "dryrun_materialized_train_candidate"
    out["materialization_notes"] = (
        "P1 train candidate expansion row. Dry-run materialization only; "
        "requires no-save gate before any checkpoint-producing route."
    )

    # Keep existing weights when available, but make missing weights explicit.
    out["sample_weight"] = float(out.get("sample_weight", 1.0))
    out["effective_sample_weight"] = float(out.get("effective_sample_weight", out["sample_weight"]))

    out.setdefault("validation_notes", [])
    return out


def main() -> int:
    args = parse_args()

    base = read_json(args.base_dataset)
    if not isinstance(base, dict):
        raise ValueError("base dataset must be dict")

    for key in ["samples", "protected_eval_samples", "tail_eval_samples", "quarantine_samples"]:
        if key not in base or not isinstance(base[key], list):
            raise ValueError(f"base dataset missing list group: {key}")

    with args.source_manifest.open(newline="", encoding="utf-8") as f:
        manifest_rows = list(csv.DictReader(f))

    existing_case_ids, existing_identities = collect_existing(base, args.board_size)

    review_rows: list[dict[str, Any]] = []
    accepted_rows: list[dict[str, Any]] = []

    # Highest-rank train-band rows first: harder rank 50 before rank 11.
    sorted_manifest = sorted(
        manifest_rows,
        key=lambda r: (
            not parse_bool(r.get("train_candidate")),
            -parse_float(r.get("rank"), -1.0),
            parse_float(r.get("prob"), 999.0),
            r.get("case_id", ""),
        ),
    )

    for mr in sorted_manifest:
        ok, reason, source_row = review_manifest_row(
            mr,
            existing_case_ids=existing_case_ids,
            existing_identities=existing_identities,
            board_size=args.board_size,
            min_train_rank=args.min_train_rank,
            max_train_rank=args.max_train_rank,
        )

        selected = False
        if ok and source_row is not None and len(accepted_rows) < args.max_new_train_candidates:
            new_row = materialize_train_row(source_row, mr, board_size=args.board_size)
            accepted_rows.append(new_row)
            existing_case_ids.add(new_row["case_id"])
            existing_identities.add(identity_from_row(new_row, args.board_size))
            selected = True
        elif ok:
            reason = "accepted_but_over_max_new_train_candidate_cap"

        # Keep all train_candidate-ish rows plus selected/rejected reasons; skip noise rows from manifest.
        if parse_bool(mr.get("train_candidate")) or selected or reason.startswith("accepted"):
            review_rows.append(
                {
                    "case_id": mr.get("case_id", ""),
                    "source_path": mr.get("source_path", ""),
                    "source_json_path": mr.get("source_json_path", ""),
                    "recommended_bucket": mr.get("recommended_bucket", ""),
                    "already_selected": mr.get("already_selected", ""),
                    "rank": mr.get("rank", ""),
                    "prob": mr.get("prob", ""),
                    "tail_candidate": mr.get("tail_candidate", ""),
                    "protected_candidate": mr.get("protected_candidate", ""),
                    "train_candidate": mr.get("train_candidate", ""),
                    "has_quarantine_words": mr.get("has_quarantine_words", ""),
                    "role": mr.get("role", ""),
                    "risk": mr.get("risk", ""),
                    "flags": mr.get("flags", ""),
                    "review_decision": reason,
                    "selected_for_train_dryrun": int(selected),
                }
            )

    out_dataset = deepcopy(base)
    out_dataset["name"] = "rapfi_teacher_policy_multisuppress_conservative_plus_generated_tail_guards_plus_train_candidates_dryrun"
    out_dataset["description"] = (
        "Dry-run dataset with generated tail guards held out and safe train candidates added to samples. "
        "Not a checkpoint-producing route and not a promotion candidate."
    )
    out_dataset["source_dataset"] = str(args.base_dataset)
    out_dataset["train_candidate_source_manifest"] = str(args.source_manifest)
    out_dataset["scope"] = "train candidate materialization dry-run only; no training/checkpoint/export/benchmark/promotion"
    out_dataset["materialization_policy"] = {
        "accepted_group": "samples",
        "max_new_train_candidates": args.max_new_train_candidates,
        "rank_band": [args.min_train_rank, args.max_train_rank],
        "tail_candidates_excluded_from_train": True,
        "protected_candidates_excluded_from_train": True,
        "quarantine_candidates_excluded_from_train": True,
        "protected_eval_samples_modified": False,
        "tail_eval_samples_modified": False,
        "quarantine_samples_modified": False,
    }
    out_dataset["samples"] = list(base["samples"]) + accepted_rows
    out_dataset["train_candidate_review_rows"] = review_rows

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

    decision = (
        "TRAIN_CANDIDATE_MATERIALIZATION_DRYRUN_TARGET_MET"
        if len(accepted_rows) >= args.max_new_train_candidates
        else "TRAIN_CANDIDATE_MATERIALIZATION_DRYRUN_PARTIAL"
        if accepted_rows
        else "TRAIN_CANDIDATE_MATERIALIZATION_DRYRUN_NO_ACCEPTED_ROWS"
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(OUT_DATASET, out_dataset)

    fields = [
        "case_id",
        "source_path",
        "source_json_path",
        "recommended_bucket",
        "already_selected",
        "rank",
        "prob",
        "tail_candidate",
        "protected_candidate",
        "train_candidate",
        "has_quarantine_words",
        "role",
        "risk",
        "flags",
        "review_decision",
        "selected_for_train_dryrun",
    ]
    with OUT_MANIFEST.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(review_rows)

    decision_counts = {
        k: sum(1 for r in review_rows if r["review_decision"] == k)
        for k in sorted({r["review_decision"] for r in review_rows})
    }

    summary = {
        "decision": decision,
        "scope": "train candidate materialization dry-run only; no training/checkpoint/export/benchmark/promotion",
        "base_dataset": str(args.base_dataset),
        "source_manifest": str(args.source_manifest),
        "out_dataset": str(OUT_DATASET),
        "source_manifest_rows": len(manifest_rows),
        "review_rows": len(review_rows),
        "accepted_new_train_candidates": len(accepted_rows),
        "max_new_train_candidates": args.max_new_train_candidates,
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
    lines += ["# Teacher-divergence train candidate expansion materialization dry-run", ""]
    lines += ["## Scope", ""]
    lines += [
        "- Train candidate materialization dry-run only.",
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
        f"- source manifest: `{args.source_manifest}`",
        f"- max new train candidates: `{args.max_new_train_candidates}`",
        f"- rank band: `{args.min_train_rank}` to `{args.max_train_rank}`",
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
    lines += ["| case_id | rank | prob | source_path | source_json_path |", "|---|---:|---:|---|---|"]
    for row in accepted_rows:
        lines.append(
            f"| `{row['case_id']}` | {row.get('source_rank')} | "
            f"{float(row.get('source_prob', 0.0)):.6g} | "
            f"`{row.get('source_path')}` | `{row.get('source_json_path')}` |"
        )
    if not accepted_rows:
        lines.append("| _none_ |  |  |  |  |")
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
    print("source_manifest_rows:", len(manifest_rows))
    print("review_rows:", len(review_rows))
    print("accepted_new_train_candidates:", len(accepted_rows))
    print("before_counts:", before_counts)
    print("after_counts:", after_counts)
    print("review_decision_counts:", decision_counts)
    print("out_dataset:", OUT_DATASET)
    print("out_manifest:", OUT_MANIFEST)
    print("out_summary:", OUT_SUMMARY)
    print("out_report:", OUT_REPORT)
    print("status: train candidate materialization dry-run only; no training/checkpoint/export/benchmark/promotion")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
