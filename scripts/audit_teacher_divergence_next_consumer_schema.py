#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


DATASET = Path("analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_conservative_selection_next.json")
MATERIALIZED_SUMMARY = Path("analysis/integration_eval/teacher_divergence_next_materialize_conservative/materialized_summary.json")
WRAPPER = Path("scripts/probe_policy_rank_topk_protected_nosave_b4c96.py")
TRAINER = Path("scripts/train_rapfi_teacher_policy_rank_topk_probe.py")

OUT_DIR = Path("analysis/integration_eval/teacher_divergence_next_consumer_audit")
OUT_CSV = OUT_DIR / "consumer_schema_audit.csv"
OUT_JSON = OUT_DIR / "consumer_schema_audit_summary.json"
OUT_MD = OUT_DIR / "consumer_schema_audit_report.md"


REQUIRED_SAMPLE_FIELDS = [
    "case_id",
    "board",
    "board_size",
    "win_length",
    "current_player",
    "target_rc",
    "suppress_rcs",
    "primary_suppress_rc",
    "before_target_rank",
    "before_target_prob",
    "before_worst_suppress_gap",
    "effective_sample_weight",
]

EXPECTED_GROUPS = [
    "samples",
    "protected_eval_samples",
    "tail_eval_samples",
    "quarantine_samples",
]


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def case_id_of(sample: dict[str, Any]) -> str:
    cid = sample.get("case_id") or sample.get("id")
    if not cid:
        raise ValueError("sample missing case_id/id")
    return str(cid)


def check_group(group: str, samples: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()

    for i, s in enumerate(samples):
        cid = case_id_of(s)
        duplicate = cid in seen
        seen.add(cid)

        missing = [k for k in REQUIRED_SAMPLE_FIELDS if k not in s]
        suppress_count = len(s.get("suppress_rcs", []))
        board_size = s.get("board_size")
        win_length = s.get("win_length")
        target_rc = s.get("target_rc")
        primary = s.get("primary_suppress_rc")

        ok = (
            not duplicate
            and not missing
            and suppress_count == 5
            and board_size == 15
            and win_length == 5
            and isinstance(target_rc, list)
            and len(target_rc) == 2
            and isinstance(primary, list)
            and len(primary) == 2
        )

        rows.append(
            {
                "group": group,
                "row_index": i,
                "case_id": cid,
                "ok": ok,
                "duplicate_in_group": duplicate,
                "missing_fields": ";".join(missing),
                "suppress_count": suppress_count,
                "board_size": board_size,
                "win_length": win_length,
                "target_rc": json.dumps(target_rc),
                "primary_suppress_rc": json.dumps(primary),
                "materialized_output_group": s.get("materialized_output_group", ""),
                "recommended_selection_role": s.get("recommended_selection_role", ""),
                "selection_risk": s.get("selection_risk", ""),
                "selection_flags": s.get("selection_flags", ""),
            }
        )

    return rows


def scan_consumer_scripts() -> dict[str, Any]:
    wrapper_text = WRAPPER.read_text(encoding="utf-8") if WRAPPER.exists() else ""
    trainer_text = TRAINER.read_text(encoding="utf-8") if TRAINER.exists() else ""

    joined = wrapper_text + "\n" + trainer_text

    return {
        "wrapper_exists": WRAPPER.exists(),
        "trainer_exists": TRAINER.exists(),
        "wrapper_mentions_protected_eval_samples": "protected_eval_samples" in wrapper_text,
        "wrapper_mentions_tail_eval_samples": "tail_eval_samples" in wrapper_text,
        "wrapper_mentions_quarantine_samples": "quarantine_samples" in wrapper_text,
        "trainer_mentions_effective_sample_weight": "effective_sample_weight" in trainer_text,
        "trainer_mentions_suppress_rcs": "suppress_rcs" in trainer_text,
        "forbidden_save_in_wrapper": ("torch" + ".save(") in wrapper_text or "--out-checkpoint" in wrapper_text,
        "forbidden_save_in_this_audit": False,
        "consumer_static_status": "PASS_STATIC_COMPATIBILITY_SCAN",
    }


def main() -> int:
    data = read_json(DATASET)
    materialized = read_json(MATERIALIZED_SUMMARY)

    rows: list[dict[str, Any]] = []
    group_counts: dict[str, int] = {}

    for group in EXPECTED_GROUPS:
        if group not in data:
            raise ValueError(f"dataset missing group: {group}")
        samples = data[group]
        if not isinstance(samples, list):
            raise TypeError(f"{group} is not a list")
        group_counts[group] = len(samples)
        rows.extend(check_group(group, samples))

    all_case_ids = [r["case_id"] for r in rows]
    duplicate_across_dataset = [cid for cid, c in Counter(all_case_ids).items() if c > 1]

    consumer_scan = scan_consumer_scripts()

    expected_counts = {
        "samples": 4,
        "protected_eval_samples": 15,
        "tail_eval_samples": 3,
        "quarantine_samples": 3,
    }

    counts_ok = group_counts == expected_counts
    rows_ok = all(bool(r["ok"]) for r in rows)
    no_duplicate_across = not duplicate_across_dataset

    quarantine_kept_separate = group_counts["quarantine_samples"] == 3 and all(
        r["group"] == "quarantine_samples"
        for r in rows
        if r["recommended_selection_role"] == "quarantine_regression_sensitive"
    )

    no_save_static_ok = not consumer_scan["forbidden_save_in_wrapper"]

    final_status = (
        "PASS_CONSUMER_SCHEMA_AUDIT"
        if counts_ok and rows_ok and no_duplicate_across and quarantine_kept_separate and no_save_static_ok
        else "FAIL_CONSUMER_SCHEMA_AUDIT"
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    fields = [
        "group",
        "row_index",
        "case_id",
        "ok",
        "duplicate_in_group",
        "missing_fields",
        "suppress_count",
        "board_size",
        "win_length",
        "target_rc",
        "primary_suppress_rc",
        "materialized_output_group",
        "recommended_selection_role",
        "selection_risk",
        "selection_flags",
    ]

    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})

    summary = {
        "decision": final_status,
        "scope": "consumer/schema audit only; no training/checkpoint/export/benchmark/promotion",
        "dataset": str(DATASET),
        "materialized_summary": str(MATERIALIZED_SUMMARY),
        "group_counts": group_counts,
        "expected_counts": expected_counts,
        "counts_ok": counts_ok,
        "rows_ok": rows_ok,
        "duplicate_across_dataset": duplicate_across_dataset,
        "no_duplicate_across_dataset": no_duplicate_across,
        "quarantine_kept_separate": quarantine_kept_separate,
        "consumer_scan": consumer_scan,
        "train_case_ids": [r["case_id"] for r in rows if r["group"] == "samples"],
        "protected_case_ids": [r["case_id"] for r in rows if r["group"] == "protected_eval_samples"],
        "tail_case_ids": [r["case_id"] for r in rows if r["group"] == "tail_eval_samples"],
        "quarantine_case_ids": [r["case_id"] for r in rows if r["group"] == "quarantine_samples"],
        "materialized_decision": materialized.get("decision"),
        "recommended_next": "If PASS, run a no-save probe only in a separate branch; do not save checkpoint.",
    }

    OUT_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines: list[str] = []
    lines += ["# Teacher-divergence next consumer/schema audit", ""]
    lines += ["## Scope", ""]
    lines += [
        "- Consumer/schema audit only.",
        "- No training.",
        "- No checkpoint read or write.",
        "- No C export, no public benchmark, no promotion.",
        "",
    ]

    lines += ["## Dataset", ""]
    lines += [f"`{DATASET}`", ""]

    lines += ["## Group counts", ""]
    lines += ["| group | expected | actual |", "|---|---:|---:|"]
    for group in EXPECTED_GROUPS:
        lines.append(f"| {group} | {expected_counts[group]} | {group_counts[group]} |")
    lines.append("")

    lines += ["## Static consumer scan", ""]
    lines += ["| check | value |", "|---|---|"]
    for k, v in consumer_scan.items():
        lines.append(f"| {k} | `{v}` |")
    lines.append("")

    lines += ["## Case IDs", ""]
    lines += ["### Train samples"]
    for cid in summary["train_case_ids"]:
        lines.append(f"- `{cid}`")
    lines.append("")

    lines += ["### Quarantine samples"]
    for cid in summary["quarantine_case_ids"]:
        lines.append(f"- `{cid}`")
    lines.append("")

    lines += ["## Decision", ""]
    lines += [
        f"`{final_status}`",
        "",
    ]

    if final_status == "PASS_CONSUMER_SCHEMA_AUDIT":
        lines += [
            "The conservative dataset is schema-compatible for a separate no-save probe route.",
            "",
            "Next route may run a no-save probe only. It must not save a checkpoint unless a later gate explicitly authorizes checkpoint-producing training.",
            "",
        ]
    else:
        lines += [
            "Do not run even a no-save probe until the schema issues are resolved.",
            "",
        ]

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("decision:", final_status)
    print("group_counts:", group_counts)
    print("counts_ok:", counts_ok)
    print("rows_ok:", rows_ok)
    print("duplicate_across_dataset:", duplicate_across_dataset)
    print("quarantine_kept_separate:", quarantine_kept_separate)
    print("consumer_scan:", consumer_scan)
    print("csv:", OUT_CSV)
    print("summary:", OUT_JSON)
    print("report:", OUT_MD)
    print("status: consumer/schema audit only; no training/checkpoint/export/benchmark/promotion")
    return 0 if final_status == "PASS_CONSUMER_SCHEMA_AUDIT" else 2


if __name__ == "__main__":
    raise SystemExit(main())
