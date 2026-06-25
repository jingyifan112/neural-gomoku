#!/usr/bin/env python3
from __future__ import annotations

import copy
import csv
import json
from collections import Counter
from pathlib import Path
from statistics import mean
from typing import Any


BASE_DATASET = Path("analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected.json")
SELECTION_MANIFEST = Path("analysis/integration_eval/teacher_divergence_data_selection_next/selection_manifest.csv")
SELECTION_SUMMARY = Path("analysis/integration_eval/teacher_divergence_data_selection_next/selection_summary.json")

OUT_DATASET = Path("analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_conservative_selection_next.json")
OUT_DIR = Path("analysis/integration_eval/teacher_divergence_next_materialize_conservative")
OUT_MANIFEST = OUT_DIR / "materialized_manifest.csv"
OUT_SUMMARY = OUT_DIR / "materialized_summary.json"
OUT_REPORT = OUT_DIR / "materialized_report.md"


TRAIN_ROLE = "train_candidate_review"
PROTECTED_ROLE = "protected_guard_holdout"
TAIL_ROLE = "tail_guard_holdout"
QUARANTINE_ROLE = "quarantine_regression_sensitive"


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def read_manifest(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def case_id_of(sample: dict[str, Any]) -> str:
    cid = sample.get("case_id") or sample.get("id")
    if not cid:
        raise ValueError("sample missing case_id/id")
    return str(cid)


def sample_weight(sample: dict[str, Any]) -> float:
    return float(sample.get("effective_sample_weight", sample.get("sample_weight", 1.0)))


def cap_weight(sample: dict[str, Any], cap: float) -> tuple[float, float]:
    old = sample_weight(sample)
    new = min(old, cap)
    sample["original_effective_sample_weight"] = old
    sample["effective_sample_weight"] = new
    if "sample_weight" in sample:
        sample["sample_weight"] = new
    sample["conservative_weight_cap"] = cap
    return old, new


def clone_with_selection(sample: dict[str, Any], manifest_row: dict[str, str], output_group: str) -> dict[str, Any]:
    out = copy.deepcopy(sample)
    out["selection_source"] = "teacher_divergence_data_selection_next"
    out["recommended_selection_role"] = manifest_row["recommended_selection_role"]
    out["selection_risk"] = manifest_row["selection_risk"]
    out["selection_flags"] = manifest_row["selection_flags"]
    out["previous_split_role"] = manifest_row["previous_split_role"]
    out["materialized_output_group"] = output_group
    return out


def suppress_count_stats(samples: list[dict[str, Any]]) -> dict[str, Any]:
    counts = Counter(len(s.get("suppress_rcs", [])) for s in samples)
    return dict(sorted(counts.items()))


def weight_stats(samples: list[dict[str, Any]]) -> dict[str, float]:
    weights = [sample_weight(s) for s in samples]
    if not weights:
        return {"min": 0.0, "mean": 0.0, "max": 0.0, "sum": 0.0}
    return {
        "min": float(min(weights)),
        "mean": float(mean(weights)),
        "max": float(max(weights)),
        "sum": float(sum(weights)),
    }


def main() -> int:
    base = read_json(BASE_DATASET)
    manifest = read_manifest(SELECTION_MANIFEST)
    selection_summary = read_json(SELECTION_SUMMARY)

    base_samples = base.get("samples", [])
    by_case = {case_id_of(s): s for s in base_samples}
    if len(by_case) != len(base_samples):
        raise ValueError("duplicate case_id in base dataset")

    manifest_by_case = {r["case_id"]: r for r in manifest}
    if len(manifest_by_case) != len(manifest):
        raise ValueError("duplicate case_id in selection manifest")

    if set(by_case) != set(manifest_by_case):
        missing_manifest = sorted(set(by_case) - set(manifest_by_case))
        missing_base = sorted(set(manifest_by_case) - set(by_case))
        raise ValueError(f"case_id mismatch missing_manifest={missing_manifest} missing_base={missing_base}")

    train_samples: list[dict[str, Any]] = []
    protected_eval_samples: list[dict[str, Any]] = []
    tail_eval_samples: list[dict[str, Any]] = []
    quarantine_samples: list[dict[str, Any]] = []
    materialized_rows: list[dict[str, Any]] = []

    for cid in sorted(by_case):
        sample = by_case[cid]
        row = manifest_by_case[cid]
        role = row["recommended_selection_role"]

        if role == TRAIN_ROLE:
            group = "samples"
            out = clone_with_selection(sample, row, group)
            old_w, new_w = cap_weight(out, 3.0)
            train_samples.append(out)
        elif role == PROTECTED_ROLE:
            group = "protected_eval_samples"
            out = clone_with_selection(sample, row, group)
            old_w, new_w = cap_weight(out, 3.0)
            protected_eval_samples.append(out)
        elif role == TAIL_ROLE:
            group = "tail_eval_samples"
            out = clone_with_selection(sample, row, group)
            old_w, new_w = cap_weight(out, 3.0)
            tail_eval_samples.append(out)
        elif role == QUARANTINE_ROLE:
            group = "quarantine_samples"
            out = clone_with_selection(sample, row, group)
            old_w, new_w = cap_weight(out, 3.0)
            quarantine_samples.append(out)
        else:
            raise ValueError(f"unknown role for {cid}: {role}")

        materialized_rows.append(
            {
                "case_id": cid,
                "output_group": group,
                "recommended_selection_role": role,
                "selection_risk": row["selection_risk"],
                "selection_flags": row["selection_flags"],
                "previous_split_role": row["previous_split_role"],
                "before_target_rank": row["before_target_rank"],
                "rank_bucket": row["rank_bucket"],
                "old_weight": old_w,
                "new_weight": new_w,
                "suppress_count": len(out.get("suppress_rcs", [])),
            }
        )

    output = {
        "name": "rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_conservative_selection_next",
        "description": (
            "Conservative materialization after b4c96 capacity route stop: "
            "only selection-audit train candidates are train samples; protected/tail guards remain held out; "
            "quarantine rows are kept separately and not used for ordinary training."
        ),
        "source_dataset": str(BASE_DATASET),
        "selection_manifest": str(SELECTION_MANIFEST),
        "selection_summary": str(SELECTION_SUMMARY),
        "samples": train_samples,
        "protected_eval_samples": protected_eval_samples,
        "tail_eval_samples": tail_eval_samples,
        "quarantine_samples": quarantine_samples,
        "materialization_metadata": {
            "scope": "dataset materialization only; no training/checkpoint/export/benchmark/promotion",
            "train_role": TRAIN_ROLE,
            "protected_role": PROTECTED_ROLE,
            "tail_role": TAIL_ROLE,
            "quarantine_role": QUARANTINE_ROLE,
            "weight_cap": 3.0,
            "source_rows": len(base_samples),
            "train_rows": len(train_samples),
            "protected_eval_rows": len(protected_eval_samples),
            "tail_eval_rows": len(tail_eval_samples),
            "quarantine_rows": len(quarantine_samples),
            "selection_audit_decision": selection_summary.get("decision"),
        },
    }

    OUT_DATASET.parent.mkdir(parents=True, exist_ok=True)
    OUT_DATASET.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    fields = [
        "case_id",
        "output_group",
        "recommended_selection_role",
        "selection_risk",
        "selection_flags",
        "previous_split_role",
        "before_target_rank",
        "rank_bucket",
        "old_weight",
        "new_weight",
        "suppress_count",
    ]
    with OUT_MANIFEST.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        for r in materialized_rows:
            w.writerow({k: r.get(k, "") for k in fields})

    group_counts = Counter(r["output_group"] for r in materialized_rows)
    role_counts = Counter(r["recommended_selection_role"] for r in materialized_rows)
    risk_counts = Counter(r["selection_risk"] for r in materialized_rows)

    summary = {
        "decision": "TEACHER_DIVERGENCE_NEXT_CONSERVATIVE_DATASET_MATERIALIZED",
        "scope": "materialization only; no training/checkpoint/export/benchmark/promotion",
        "out_dataset": str(OUT_DATASET),
        "source_dataset": str(BASE_DATASET),
        "selection_manifest": str(SELECTION_MANIFEST),
        "source_rows": len(base_samples),
        "train_rows": len(train_samples),
        "protected_eval_rows": len(protected_eval_samples),
        "tail_eval_rows": len(tail_eval_samples),
        "quarantine_rows": len(quarantine_samples),
        "group_counts": dict(group_counts),
        "role_counts": dict(role_counts),
        "risk_counts": dict(risk_counts),
        "train_case_ids": [case_id_of(s) for s in train_samples],
        "protected_case_ids": [case_id_of(s) for s in protected_eval_samples],
        "tail_case_ids": [case_id_of(s) for s in tail_eval_samples],
        "quarantine_case_ids": [case_id_of(s) for s in quarantine_samples],
        "suppress_count_stats": {
            "train": suppress_count_stats(train_samples),
            "protected": suppress_count_stats(protected_eval_samples),
            "tail": suppress_count_stats(tail_eval_samples),
            "quarantine": suppress_count_stats(quarantine_samples),
        },
        "weight_stats": {
            "train": weight_stats(train_samples),
            "protected": weight_stats(protected_eval_samples),
            "tail": weight_stats(tail_eval_samples),
            "quarantine": weight_stats(quarantine_samples),
        },
        "recommended_next": "manual schema/consumer audit before any no-save probe",
    }

    OUT_SUMMARY.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines: list[str] = []
    lines += ["# Teacher-divergence next conservative dataset materialization", ""]
    lines += ["## Scope", ""]
    lines += [
        "- Dataset materialization only.",
        "- No training.",
        "- No checkpoint read or write.",
        "- No C export, no public benchmark, no promotion.",
        "",
    ]

    lines += ["## Output dataset", ""]
    lines += [f"`{OUT_DATASET}`", ""]

    lines += ["## Counts", ""]
    lines += [
        f"- source rows: {len(base_samples)}",
        f"- train rows: {len(train_samples)}",
        f"- protected eval rows: {len(protected_eval_samples)}",
        f"- tail eval rows: {len(tail_eval_samples)}",
        f"- quarantine rows: {len(quarantine_samples)}",
        "",
    ]

    lines += ["## Train candidates", ""]
    for cid in summary["train_case_ids"]:
        lines.append(f"- `{cid}`")
    lines.append("")

    lines += ["## Quarantine rows", ""]
    for cid in summary["quarantine_case_ids"]:
        lines.append(f"- `{cid}`")
    lines.append("")

    lines += ["## Group counts", ""]
    lines += ["| group | rows |", "|---|---:|"]
    for group, count in sorted(group_counts.items()):
        lines.append(f"| {group} | {count} |")
    lines.append("")

    lines += ["## Interpretation", ""]
    lines += [
        "This dataset is intentionally conservative.",
        "",
        "Only the four directionally useful train-candidate rows become ordinary train samples. Protected and tail rows remain held out as guards. Quarantine rows are preserved separately but should not be used for checkpoint-producing training without manual review.",
        "",
    ]

    lines += ["## Decision", ""]
    lines += [
        "`TEACHER_DIVERGENCE_NEXT_CONSERVATIVE_DATASET_MATERIALIZED`",
        "",
        "Recommended next step: run a schema/consumer audit before any no-save probe.",
        "",
    ]

    OUT_REPORT.write_text("\n".join(lines), encoding="utf-8")

    print("out_dataset:", OUT_DATASET)
    print("train_rows:", len(train_samples), [case_id_of(s) for s in train_samples])
    print("protected_eval_rows:", len(protected_eval_samples))
    print("tail_eval_rows:", len(tail_eval_samples))
    print("quarantine_rows:", len(quarantine_samples), [case_id_of(s) for s in quarantine_samples])
    print("manifest:", OUT_MANIFEST)
    print("summary:", OUT_SUMMARY)
    print("report:", OUT_REPORT)
    print("status: materialization only; no training/checkpoint/export/benchmark/promotion")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
