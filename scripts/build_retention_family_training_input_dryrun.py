#!/usr/bin/env python3
"""
Build candidate training/eval input manifests from retention family applied split dry-run.

This is manifest construction only:
- no training
- no checkpoint save
- no C export
- no benchmark
- no promotion
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


DEFAULT_APPLIED_CSV = Path("analysis/integration_eval/retention_family_applied_split_dryrun_manifest.csv")

DEFAULT_OUT_TRAIN_CSV = Path("analysis/integration_eval/retention_family_training_input_dryrun_train_manifest.csv")
DEFAULT_OUT_EVAL_CSV = Path("analysis/integration_eval/retention_family_training_input_dryrun_eval_manifest.csv")
DEFAULT_OUT_JSON = Path("analysis/integration_eval/retention_family_training_input_dryrun_summary.json")
DEFAULT_OUT_MD = Path("analysis/integration_eval/retention_family_training_input_dryrun_report.md")

CRITICAL_FAMILY = "bd:ea22cc14729b88fd"


def clean(v: Any) -> str:
    if v is None:
        return ""
    return str(v).strip()


def yes(v: Any) -> bool:
    return clean(v).lower() in {"yes", "true", "1", "y"}


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return [dict(r) for r in csv.DictReader(f)]


def write_csv(path: Path, rows: List[Dict[str, Any]], fields: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})


def bucket_row(row: Dict[str, str]) -> str:
    proposed_split = clean(row.get("proposed_split"))
    proposed_role = clean(row.get("proposed_role"))
    materialized_role = clean(row.get("materialized_role"))

    if proposed_split == "train_retention_anchor" or proposed_role == "nonheldout_retention_anchor":
        return "train_candidate"

    if proposed_split == "heldout_retention_gate" or proposed_role == "heldout_retention_gate":
        return "eval_gate_candidate"

    if proposed_split == "heldout_retention_gate_review" or "review" in proposed_role:
        return "eval_gate_review"

    if materialized_role:
        return "materialized_review"

    return "unmatched_or_unchanged_review"


def train_use_policy(row: Dict[str, str]) -> str:
    bucket = bucket_row(row)
    if bucket == "train_candidate":
        return "include_as_nonheldout_retention_anchor_candidate"
    return "exclude_from_train_manifest"


def eval_use_policy(row: Dict[str, str]) -> str:
    bucket = bucket_row(row)
    gate_scope = clean(row.get("gate_scope"))

    if bucket == "eval_gate_candidate":
        if gate_scope == "normal_heldout_gate":
            return "normal_heldout_gate_candidate"
        if gate_scope == "external_or_family_level_only_not_sibling_only":
            return "restricted_family_level_gate_candidate"
        return "heldout_gate_candidate_review_scope"

    if bucket == "eval_gate_review":
        return "review_before_eval_gate_use"

    return "exclude_from_eval_manifest"


def risk_flags(row: Dict[str, str]) -> str:
    flags = []
    if clean(row.get("family_id")) == CRITICAL_FAMILY:
        flags.append("critical_sibling_conflict_family")
    if clean(row.get("gate_scope")) == "external_or_family_level_only_not_sibling_only":
        flags.append("not_only_sibling_family_gate")
    if clean(row.get("matched_materialized_row")) != "yes":
        flags.append("unmatched_materialized_row")
    if "review" in bucket_row(row):
        flags.append("review_required")
    return ";".join(flags)


def base_output_row(row: Dict[str, str]) -> Dict[str, str]:
    return {
        "dataset_index": clean(row.get("dataset_index")),
        "family_id": clean(row.get("family_id")),
        "source": clean(row.get("source")),
        "source_path": clean(row.get("source_path")),
        "policy_target": clean(row.get("policy_target")),
        "teacher_move": clean(row.get("teacher_move")),
        "side_to_move": clean(row.get("side_to_move")),
        "last_move": clean(row.get("last_move")),
        "original_split": clean(row.get("original_split")),
        "original_role": clean(row.get("original_role")),
        "materialized_role": clean(row.get("materialized_role")),
        "proposed_split": clean(row.get("proposed_split")),
        "proposed_role": clean(row.get("proposed_role")),
        "gate_scope": clean(row.get("gate_scope")),
        "allowed_as_only_sibling_family_gate": clean(row.get("allowed_as_only_sibling_family_gate")),
        "match_method": clean(row.get("match_method")),
        "match_key": clean(row.get("match_key")),
        "materialized_reason": clean(row.get("materialized_reason")),
        "bucket": bucket_row(row),
        "train_use_policy": train_use_policy(row),
        "eval_use_policy": eval_use_policy(row),
        "risk_flags": risk_flags(row),
    }


def make_table(headers: List[str], rows: List[List[Any]], max_rows: int = 200) -> str:
    lines = []
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for r in rows[:max_rows]:
        cells = [str(x).replace("\n", " ").replace("|", "\\|") for x in r]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def validate_critical_family(rows: List[Dict[str, str]]) -> List[str]:
    errors = []
    critical = [
        r for r in rows
        if clean(r.get("family_id")) == CRITICAL_FAMILY
    ]
    by_target = defaultdict(list)
    for r in critical:
        by_target[clean(r.get("policy_target"))].append(r)

    for target in ["7,10", "10,7"]:
        rs = by_target.get(target, [])
        if not rs:
            errors.append(f"missing critical target {target}")
            continue
        if not any(bucket_row(r) == "train_candidate" for r in rs):
            errors.append(f"critical target {target} is not train_candidate")

    rs_79 = by_target.get("7,9", [])
    if not rs_79:
        errors.append("missing critical target 7,9")
    else:
        if not any(bucket_row(r) == "eval_gate_candidate" for r in rs_79):
            errors.append("critical target 7,9 is not eval_gate_candidate")
        if not any(clean(r.get("gate_scope")) == "external_or_family_level_only_not_sibling_only" for r in rs_79):
            errors.append("critical target 7,9 does not have restricted sibling-family gate scope")
        if any(clean(r.get("allowed_as_only_sibling_family_gate")) == "yes" for r in rs_79):
            errors.append("critical target 7,9 incorrectly allowed as only sibling-family gate")

    return errors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--applied-csv", type=Path, default=DEFAULT_APPLIED_CSV)
    ap.add_argument("--out-train-csv", type=Path, default=DEFAULT_OUT_TRAIN_CSV)
    ap.add_argument("--out-eval-csv", type=Path, default=DEFAULT_OUT_EVAL_CSV)
    ap.add_argument("--out-json", type=Path, default=DEFAULT_OUT_JSON)
    ap.add_argument("--out-md", type=Path, default=DEFAULT_OUT_MD)
    ap.add_argument("--strict-critical-family", action="store_true")
    args = ap.parse_args()

    applied_rows = read_csv(args.applied_csv)
    if not applied_rows:
        raise SystemExit(f"ERROR: no rows found in {args.applied_csv}")

    output_rows = [base_output_row(r) for r in applied_rows]

    train_rows = [
        r for r in output_rows
        if r["bucket"] == "train_candidate"
    ]
    eval_rows = [
        r for r in output_rows
        if r["bucket"] in {"eval_gate_candidate", "eval_gate_review"}
    ]
    review_rows = [
        r for r in output_rows
        if r["bucket"] not in {"train_candidate", "eval_gate_candidate", "eval_gate_review"}
    ]

    fields = [
        "dataset_index",
        "family_id",
        "source",
        "source_path",
        "policy_target",
        "teacher_move",
        "side_to_move",
        "last_move",
        "original_split",
        "original_role",
        "materialized_role",
        "proposed_split",
        "proposed_role",
        "gate_scope",
        "allowed_as_only_sibling_family_gate",
        "match_method",
        "match_key",
        "materialized_reason",
        "bucket",
        "train_use_policy",
        "eval_use_policy",
        "risk_flags",
    ]

    write_csv(args.out_train_csv, train_rows, fields)
    write_csv(args.out_eval_csv, eval_rows, fields)

    critical_errors = validate_critical_family(output_rows)
    if args.strict_critical_family and critical_errors:
        raise SystemExit("ERROR: critical family validation failed: " + "; ".join(critical_errors))

    bucket_counts = Counter(r["bucket"] for r in output_rows)
    train_policy_counts = Counter(r["train_use_policy"] for r in output_rows)
    eval_policy_counts = Counter(r["eval_use_policy"] for r in output_rows)
    family_counts = Counter(r["family_id"] for r in output_rows if r["family_id"])

    summary = {
        "metadata": {
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "scope": "training input dry-run only; no training/checkpoint/C export/benchmark/promotion",
            "input_applied_csv": str(args.applied_csv),
            "output_train_manifest_csv": str(args.out_train_csv),
            "output_eval_manifest_csv": str(args.out_eval_csv),
        },
        "counts": {
            "applied_rows": len(output_rows),
            "train_manifest_rows": len(train_rows),
            "eval_manifest_rows": len(eval_rows),
            "review_or_unmatched_rows": len(review_rows),
            "bucket_counts": dict(sorted(bucket_counts.items())),
            "train_policy_counts": dict(sorted(train_policy_counts.items())),
            "eval_policy_counts": dict(sorted(eval_policy_counts.items())),
            "family_counts": dict(sorted(family_counts.items())),
        },
        "critical_family_validation_errors": critical_errors,
        "train_rows": train_rows,
        "eval_rows": eval_rows,
        "review_rows": review_rows,
        "consumer_contract": {
            "train_candidate": "Can be used as nonheldout_retention_anchor candidate in a future training manifest.",
            "eval_gate_candidate": "Can be used as heldout/eval candidate only according to gate_scope.",
            "restricted_gate_scope": "external_or_family_level_only_not_sibling_only must not be the sole heldout evidence for sibling targets from the same family.",
            "review_rows": "Must be manually reviewed before use in training or evaluation.",
        },
    }

    args.out_json.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    critical_rows = [
        r for r in output_rows
        if r["family_id"] == CRITICAL_FAMILY
    ]

    md = []
    md.append("# Retention family training input dry-run")
    md.append("")
    md.append("Scope: training-input manifest construction only. No training, checkpoint save, C export, benchmark, or promotion was run.")
    md.append("")
    md.append("## Inputs and outputs")
    md.append("")
    md.append(f"- input applied split dry-run CSV: `{args.applied_csv}`")
    md.append(f"- output train manifest CSV: `{args.out_train_csv}`")
    md.append(f"- output eval manifest CSV: `{args.out_eval_csv}`")
    md.append(f"- output summary JSON: `{args.out_json}`")
    md.append("")
    md.append("## Summary")
    md.append("")
    md.append(f"- applied rows: {len(output_rows)}")
    md.append(f"- train manifest rows: {len(train_rows)}")
    md.append(f"- eval manifest rows: {len(eval_rows)}")
    md.append(f"- review/unmatched rows: {len(review_rows)}")
    md.append(f"- bucket counts: `{dict(sorted(bucket_counts.items()))}`")
    md.append(f"- train policy counts: `{dict(sorted(train_policy_counts.items()))}`")
    md.append(f"- eval policy counts: `{dict(sorted(eval_policy_counts.items()))}`")
    md.append("")
    md.append("## Critical sibling-conflict family validation")
    md.append("")
    md.append(f"- family_id: `{CRITICAL_FAMILY}`")
    if critical_errors:
        md.append(f"- validation: FAIL — `{critical_errors}`")
    else:
        md.append("- validation: PASS")
    md.append("")
    md.append(make_table(
        [
            "target",
            "bucket",
            "train_policy",
            "eval_policy",
            "gate_scope",
            "only_sibling_gate_ok",
            "risk_flags",
        ],
        [
            [
                r["policy_target"],
                r["bucket"],
                r["train_use_policy"],
                r["eval_use_policy"],
                r["gate_scope"],
                r["allowed_as_only_sibling_family_gate"],
                r["risk_flags"],
            ]
            for r in critical_rows
        ],
    ))
    md.append("")
    md.append("Interpretation:")
    md.append("")
    md.append("- `7,10` and `10,7` from the critical family are training-side retention anchor candidates.")
    md.append("- `7,9` remains eval-side only with restricted gate scope.")
    md.append("- The restricted `7,9` gate must not be the only sibling-family heldout check for `7,10` or `10,7`.")
    md.append("")
    md.append("## Train manifest")
    md.append("")
    md.append(make_table(
        [
            "idx",
            "family_id",
            "source",
            "target",
            "train_policy",
            "risk_flags",
            "reason",
        ],
        [
            [
                r["dataset_index"],
                r["family_id"],
                r["source"],
                r["policy_target"],
                r["train_use_policy"],
                r["risk_flags"],
                r["materialized_reason"],
            ]
            for r in train_rows
        ],
    ))
    md.append("")
    md.append("## Eval manifest")
    md.append("")
    md.append(make_table(
        [
            "idx",
            "family_id",
            "source",
            "target",
            "eval_policy",
            "gate_scope",
            "only_sibling_gate_ok",
            "risk_flags",
        ],
        [
            [
                r["dataset_index"],
                r["family_id"],
                r["source"],
                r["policy_target"],
                r["eval_use_policy"],
                r["gate_scope"],
                r["allowed_as_only_sibling_family_gate"],
                r["risk_flags"],
            ]
            for r in eval_rows
        ],
    ))
    md.append("")
    if review_rows:
        md.append("## Review / unmatched rows")
        md.append("")
        md.append(make_table(
            [
                "idx",
                "family_id",
                "source",
                "target",
                "bucket",
                "risk_flags",
                "reason",
            ],
            [
                [
                    r["dataset_index"],
                    r["family_id"],
                    r["source"],
                    r["policy_target"],
                    r["bucket"],
                    r["risk_flags"],
                    r["materialized_reason"],
                ]
                for r in review_rows
            ],
        ))
        md.append("")
    md.append("## Consumer contract for future training script")
    md.append("")
    md.append("- Only rows in `retention_family_training_input_dryrun_train_manifest.csv` may be considered training-side retention anchor candidates.")
    md.append("- Rows in `retention_family_training_input_dryrun_eval_manifest.csv` are eval/heldout candidates only according to `eval_use_policy` and `gate_scope`.")
    md.append("- `external_or_family_level_only_not_sibling_only` is a hard restriction: it must not be used as the sole heldout evidence for a sibling target in the same family.")
    md.append("- This artifact is not a training dataset approval; it is a dry-run contract for the next implementation step.")
    md.append("")
    md.append("## Explicit non-actions")
    md.append("")
    md.append("- No model training was run.")
    md.append("- No checkpoint was saved.")
    md.append("- No C weights were exported.")
    md.append("- No benchmark was run.")
    md.append("- No promotion decision was made.")
    md.append("")

    args.out_md.write_text("\n".join(md).rstrip() + "\n", encoding="utf-8")

    print("wrote", args.out_train_csv)
    print("wrote", args.out_eval_csv)
    print("wrote", args.out_json)
    print("wrote", args.out_md)
    print("applied rows:", len(output_rows))
    print("train rows:", len(train_rows))
    print("eval rows:", len(eval_rows))
    print("review rows:", len(review_rows))
    print("bucket_counts:", dict(sorted(bucket_counts.items())))
    print("critical_family_validation_errors:", critical_errors)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
