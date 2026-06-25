#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


EXPANSION_TARGETS = Path("analysis/integration_eval/teacher_divergence_expansion_targets/expansion_targets_summary.json")
MATERIALIZED_SUMMARY = Path("analysis/integration_eval/teacher_divergence_next_materialize_conservative/materialized_summary.json")
ROW_LEVEL_SUMMARY = Path("analysis/integration_eval/teacher_divergence_row_level_guard_review/leave_one_out_summary.json")

OUT_DIR = Path("analysis/integration_eval/teacher_divergence_expansion_source_audit_next")
OUT_MANIFEST = OUT_DIR / "source_candidate_manifest.csv"
OUT_SUMMARY = OUT_DIR / "source_audit_summary.json"
OUT_REPORT = OUT_DIR / "source_audit_report.md"

SOURCE_PATHS = [
    Path("analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected.json"),
    Path("analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_protected_train_11_50_weightcap3.json"),
    Path("analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_conservative_selection_next.json"),
    Path("analysis/integration_eval/teacher_divergence_data_inventory_manifest.csv"),
    Path("analysis/integration_eval/teacher_divergence_data_inventory.json"),
    Path("analysis/integration_eval/teacher_divergence_expansion_candidate_manifest.csv"),
    Path("analysis/integration_eval/teacher_divergence_expansion_source_audit.csv"),
    Path("analysis/integration_eval/teacher_divergence_expansion_source_audit.json"),
    Path("analysis/integration_eval/teacher_divergence_retention_expanded_manifest.csv"),
    Path("analysis/integration_eval/teacher_divergence_retention_expanded_dataset.json"),
    Path("analysis/integration_eval/teacher_divergence_retention_expanded_source_audit.json"),
    Path("analysis/integration_eval/teacher_divergence_source_schema_audit.json"),
]


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, Any]]:
    with path.open(newline="", encoding="utf-8") as f:
        return [dict(r) for r in csv.DictReader(f)]


def as_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        if value == "":
            return None
        x = float(value)
        if math.isnan(x):
            return None
        return x
    except Exception:
        return None


def lower_blob(row: dict[str, Any]) -> str:
    return json.dumps(row, ensure_ascii=False, sort_keys=True).lower()


def first_present(row: dict[str, Any], keys: list[str]) -> Any:
    for k in keys:
        if k in row and row[k] not in [None, ""]:
            return row[k]
    return None


def case_id_of(row: dict[str, Any], fallback: str) -> str:
    val = first_present(
        row,
        [
            "case_id",
            "id",
            "sample_id",
            "position_id",
            "source_case_id",
            "legacy_case_id",
            "name",
        ],
    )
    return str(val) if val not in [None, ""] else fallback


def rank_of(row: dict[str, Any]) -> float | None:
    for k in [
        "before_target_rank",
        "target_rank",
        "teacher_rank",
        "rank",
        "model_target_rank",
        "policy_rank",
    ]:
        v = as_float(row.get(k))
        if v is not None:
            return v
    return None


def score_prob(row: dict[str, Any]) -> float | None:
    for k in [
        "before_target_prob",
        "target_prob",
        "teacher_prob",
        "prob",
        "model_target_prob",
    ]:
        v = as_float(row.get(k))
        if v is not None:
            return v
    return None


def walk_json_objects(obj: Any, path: str = "$") -> list[tuple[str, dict[str, Any]]]:
    out: list[tuple[str, dict[str, Any]]] = []

    if isinstance(obj, dict):
        sample_like = False
        keys = set(obj.keys())
        if {"target_rc", "suppress_rcs"} & keys:
            sample_like = True
        if {"case_id", "id", "sample_id", "position_id"} & keys and (
            {"before_target_rank", "teacher_rank", "target_rank", "rank"} & keys
            or {"recommended_selection_role", "selection_risk", "role", "split"} & keys
        ):
            sample_like = True

        if sample_like:
            out.append((path, dict(obj)))

        for k, v in obj.items():
            out.extend(walk_json_objects(v, f"{path}.{k}"))

    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out.extend(walk_json_objects(v, f"{path}[{i}]"))

    return out


def load_source_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []

    rows: list[dict[str, Any]] = []
    if path.suffix.lower() == ".csv":
        for i, r in enumerate(read_csv(path)):
            r = dict(r)
            r["_source_json_path"] = f"$[{i}]"
            rows.append(r)
    elif path.suffix.lower() == ".json":
        obj = read_json(path)
        for json_path, r in walk_json_objects(obj):
            r = dict(r)
            r["_source_json_path"] = json_path
            rows.append(r)
    else:
        return []

    return rows


def classify(row: dict[str, Any], selected_case_ids: set[str]) -> dict[str, Any]:
    blob = lower_blob(row)
    rank = rank_of(row)
    prob = score_prob(row)

    case_id = str(row["_case_id"])
    already_selected = case_id in selected_case_ids

    has_tail_words = any(s in blob for s in ["tail", "rank_gt50", "rank>50", "gt50"])
    has_protected_words = any(s in blob for s in ["protected", "top10", "top5", "top3"])
    has_train_words = any(s in blob for s in ["train_candidate", "trainable", "rank_11_50", "11_50"])
    has_quarantine_words = any(
        s in blob
        for s in [
            "quarantine",
            "severe_core_regression",
            "core_regressed",
            "severe",
            "hard_fail",
            "regression_sensitive",
        ]
    )

    tail_candidate = bool((rank is not None and rank > 50) or has_tail_words)
    protected_candidate = bool((rank is not None and rank <= 10) or has_protected_words)
    train_candidate = bool(
        rank is not None
        and 11 <= rank <= 50
        and not tail_candidate
        and not protected_candidate
        and not has_quarantine_words
    ) or bool(has_train_words and not has_quarantine_words and not already_selected)

    if already_selected:
        recommended_bucket = "already_selected_or_guarded"
    elif has_quarantine_words:
        recommended_bucket = "quarantine_or_negative_example"
    elif tail_candidate:
        recommended_bucket = "P0_tail_guard_candidate"
    elif protected_candidate:
        recommended_bucket = "P0_protected_guard_candidate"
    elif train_candidate:
        recommended_bucket = "P1_train_candidate"
    else:
        recommended_bucket = "unclassified_review"

    return {
        "rank": rank,
        "prob": prob,
        "already_selected": already_selected,
        "tail_candidate": tail_candidate,
        "protected_candidate": protected_candidate,
        "train_candidate": train_candidate,
        "has_quarantine_words": has_quarantine_words,
        "recommended_bucket": recommended_bucket,
    }


def main() -> int:
    if not EXPANSION_TARGETS.exists():
        raise FileNotFoundError(EXPANSION_TARGETS)
    if not MATERIALIZED_SUMMARY.exists():
        raise FileNotFoundError(MATERIALIZED_SUMMARY)
    if not ROW_LEVEL_SUMMARY.exists():
        raise FileNotFoundError(ROW_LEVEL_SUMMARY)

    targets = read_json(EXPANSION_TARGETS)
    materialized = read_json(MATERIALIZED_SUMMARY)
    row_level = read_json(ROW_LEVEL_SUMMARY)

    selected_case_ids = set()
    for k in ["train_case_ids", "protected_case_ids", "tail_case_ids", "quarantine_case_ids"]:
        for cid in materialized.get(k, []):
            selected_case_ids.add(str(cid))

    manifest_rows: list[dict[str, Any]] = []
    source_status: list[dict[str, Any]] = []

    for source_path in SOURCE_PATHS:
        exists = source_path.exists()
        rows = load_source_rows(source_path)
        source_status.append(
            {
                "source_path": str(source_path),
                "exists": exists,
                "loaded_rows": len(rows),
            }
        )

        for i, raw in enumerate(rows):
            row = dict(raw)
            fallback = f"{source_path.name}::{i}"
            cid = case_id_of(row, fallback=fallback)
            row["_case_id"] = cid

            cls = classify(row, selected_case_ids)

            manifest_rows.append(
                {
                    "source_path": str(source_path),
                    "source_json_path": row.get("_source_json_path", ""),
                    "case_id": cid,
                    "recommended_bucket": cls["recommended_bucket"],
                    "already_selected": cls["already_selected"],
                    "rank": "" if cls["rank"] is None else cls["rank"],
                    "prob": "" if cls["prob"] is None else cls["prob"],
                    "tail_candidate": cls["tail_candidate"],
                    "protected_candidate": cls["protected_candidate"],
                    "train_candidate": cls["train_candidate"],
                    "has_quarantine_words": cls["has_quarantine_words"],
                    "role": first_present(row, ["role", "split", "recommended_selection_role", "materialized_output_group"]) or "",
                    "risk": first_present(row, ["selection_risk", "risk", "risk_level"]) or "",
                    "flags": first_present(row, ["selection_flags", "tags", "failure_tags", "flags"]) or "",
                }
            )

    # Deduplicate candidate count by case_id within each bucket.
    bucket_case_ids: dict[str, set[str]] = defaultdict(set)
    for r in manifest_rows:
        bucket_case_ids[str(r["recommended_bucket"])].add(str(r["case_id"]))

    bucket_counts = {k: len(v) for k, v in sorted(bucket_case_ids.items())}

    candidate_new_counts = {
        "P0_tail_guard_candidate": bucket_counts.get("P0_tail_guard_candidate", 0),
        "P0_protected_guard_candidate": bucket_counts.get("P0_protected_guard_candidate", 0),
        "P1_train_candidate": bucket_counts.get("P1_train_candidate", 0),
    }

    minimum_targets = {
        "P0_tail_guard_candidate": 12,
        "P0_protected_guard_candidate": 12,
        "P1_train_candidate": 20,
    }

    target_gaps = {
        k: max(0, minimum_targets[k] - candidate_new_counts.get(k, 0))
        for k in minimum_targets
    }

    has_any_candidate_source = any(v > 0 for v in candidate_new_counts.values())
    meets_all_minimums = all(gap == 0 for gap in target_gaps.values())

    decision = (
        "EXPANSION_SOURCE_AUDIT_HAS_MINIMUM_CANDIDATES"
        if meets_all_minimums
        else "EXPANSION_SOURCE_AUDIT_HAS_PARTIAL_CANDIDATES"
        if has_any_candidate_source
        else "EXPANSION_SOURCE_AUDIT_NEEDS_NEW_SOURCE_GENERATION"
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    fields = [
        "source_path",
        "source_json_path",
        "case_id",
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
    ]
    with OUT_MANIFEST.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        for r in manifest_rows:
            w.writerow({k: r.get(k, "") for k in fields})

    summary = {
        "decision": decision,
        "scope": "source audit only; no dataset build/training/checkpoint/export/benchmark/promotion",
        "inputs": {
            "expansion_targets": str(EXPANSION_TARGETS),
            "materialized_summary": str(MATERIALIZED_SUMMARY),
            "row_level_summary": str(ROW_LEVEL_SUMMARY),
        },
        "upstream_decisions": {
            "expansion_targets_decision": targets.get("decision"),
            "row_level_decision": row_level.get("decision"),
        },
        "selected_case_ids_count": len(selected_case_ids),
        "source_status": source_status,
        "loaded_manifest_rows": len(manifest_rows),
        "bucket_counts": bucket_counts,
        "candidate_new_counts": candidate_new_counts,
        "minimum_targets": minimum_targets,
        "target_gaps": target_gaps,
        "recommended_next": (
            "Build an expansion candidate review manifest from available candidate sources."
            if has_any_candidate_source
            else "Generate or collect additional teacher-divergence source rows before materializing a dataset."
        ),
    }
    OUT_SUMMARY.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines: list[str] = []
    lines += ["# Teacher-divergence expansion source audit next", ""]
    lines += ["## Scope", ""]
    lines += [
        "- Source audit only.",
        "- No dataset build.",
        "- No training.",
        "- No checkpoint read or write.",
        "- No C export, no public benchmark, no promotion.",
        "",
    ]

    lines += ["## Upstream decisions", ""]
    lines += [
        f"- expansion targets: `{targets.get('decision')}`",
        f"- row-level guard review: `{row_level.get('decision')}`",
        "",
    ]

    lines += ["## Source status", ""]
    lines += ["| source | exists | loaded_rows |", "|---|---:|---:|"]
    for s in source_status:
        lines.append(f"| `{s['source_path']}` | {s['exists']} | {s['loaded_rows']} |")
    lines.append("")

    lines += ["## Candidate buckets", ""]
    lines += ["| bucket | unique case_ids | minimum target | gap |", "|---|---:|---:|---:|"]
    for bucket in [
        "P0_tail_guard_candidate",
        "P0_protected_guard_candidate",
        "P1_train_candidate",
    ]:
        lines.append(
            f"| {bucket} | {candidate_new_counts.get(bucket, 0)} | "
            f"{minimum_targets[bucket]} | {target_gaps[bucket]} |"
        )
    lines.append("")

    lines += ["## Other buckets", ""]
    lines += ["| bucket | unique case_ids |", "|---|---:|"]
    for bucket, count in sorted(bucket_counts.items()):
        if bucket not in minimum_targets:
            lines.append(f"| {bucket} | {count} |")
    lines.append("")

    lines += ["## Decision", ""]
    lines += [f"`{decision}`", ""]

    if decision == "EXPANSION_SOURCE_AUDIT_HAS_MINIMUM_CANDIDATES":
        lines += [
            "Available source artifacts appear to contain enough candidate rows for the requested minimum expansion targets.",
            "",
            "Next step should be a candidate-review/materialization branch, still no training.",
            "",
        ]
    elif decision == "EXPANSION_SOURCE_AUDIT_HAS_PARTIAL_CANDIDATES":
        lines += [
            "Available source artifacts contain some candidate rows but do not satisfy all minimum targets.",
            "",
            "Next step should either expand source generation further or build a review manifest for the partial candidates while clearly tracking remaining gaps.",
            "",
        ]
    else:
        lines += [
            "Available source artifacts do not contain usable new candidate rows for the target expansion.",
            "",
            "Next step should generate or collect more teacher-divergence source rows before any materialization.",
            "",
        ]

    lines += ["## Final note", ""]
    lines += [
        "This audit does not authorize training, checkpoint save, C export, public benchmark, promotion, or current_best overwrite.",
        "",
    ]

    OUT_REPORT.write_text("\n".join(lines), encoding="utf-8")

    print("decision:", decision)
    print("loaded_manifest_rows:", len(manifest_rows))
    print("bucket_counts:", bucket_counts)
    print("candidate_new_counts:", candidate_new_counts)
    print("target_gaps:", target_gaps)
    print("out_manifest:", OUT_MANIFEST)
    print("out_summary:", OUT_SUMMARY)
    print("out_report:", OUT_REPORT)
    print("status: source audit only; no dataset build/training/checkpoint/export/benchmark/promotion")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
