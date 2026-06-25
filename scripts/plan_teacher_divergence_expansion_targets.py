#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


ROW_LEVEL_SUMMARY = Path("analysis/integration_eval/teacher_divergence_row_level_guard_review/leave_one_out_summary.json")
ROW_LEVEL_REPORT = Path("analysis/integration_eval/teacher_divergence_row_level_guard_review/leave_one_out_report.md")
NOSAVE_SUMMARY = Path("analysis/integration_eval/teacher_divergence_next_nosave_probe/nosave_probe_summary.csv")
SELECTION_SUMMARY = Path("analysis/integration_eval/teacher_divergence_data_selection_next/selection_summary.json")
MATERIALIZED_SUMMARY = Path("analysis/integration_eval/teacher_divergence_next_materialize_conservative/materialized_summary.json")
STOP_REVIEW = Path("analysis/integration_eval/b4c96_capacity_route_stop_review.md")

OUT_DIR = Path("analysis/integration_eval/teacher_divergence_expansion_targets")
OUT_CSV = OUT_DIR / "expansion_targets.csv"
OUT_JSON = OUT_DIR / "expansion_targets_summary.json"
OUT_MD = OUT_DIR / "expansion_targets_report.md"


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main() -> int:
    row_level = read_json(ROW_LEVEL_SUMMARY)
    selection = read_json(SELECTION_SUMMARY)
    materialized = read_json(MATERIALIZED_SUMMARY)
    nosave_rows = read_csv(NOSAVE_SUMMARY)

    tail_rows = [r for r in nosave_rows if r["group"] == "tail_eval_rank_gt50"]
    protected_rows = [r for r in nosave_rows if r["group"] == "protected_eval_top10"]
    train_rows = [r for r in nosave_rows if r["group"] == "train_main_rank_11_50"]

    tail_failure = tail_rows and float(tail_rows[0]["rank_gt50_delta"]) > 0
    protected_failure = protected_rows and float(protected_rows[0]["top5_delta"]) < 0
    train_improved = train_rows and float(train_rows[0]["mean_rank_delta"]) < 0

    expansion_targets = [
        {
            "priority": "P0",
            "target_area": "tail_guard_expansion",
            "current_evidence": "tail_eval_rank_gt50 failed in full conservative probe and every leave-one-out variant",
            "minimum_new_rows": 12,
            "selection_rule": "Collect rank>50 or near-tail teacher-divergence rows, especially cases where training tends to lose top10 or create rank>50 regressions.",
            "acceptance_rule": "Rows must remain held out as tail_guard until a no-save probe shows rank_gt50_delta <= 0 and mean_rank_delta <= 0.",
            "do_not_use_as": "ordinary_train_rows",
        },
        {
            "priority": "P0",
            "target_area": "protected_guard_expansion",
            "current_evidence": "protected_eval_top10 lost top5 coverage or target probability across probes",
            "minimum_new_rows": 12,
            "selection_rule": "Collect top3/top5/top10 teacher rows where target is already relatively good and must not regress.",
            "acceptance_rule": "Rows must remain held out as protected_guard until top5_delta >= 0, top10_delta >= 0, and no teacher-beats regression appears.",
            "do_not_use_as": "ordinary_train_rows",
        },
        {
            "priority": "P1",
            "target_area": "train_candidate_expansion",
            "current_evidence": "Only 4 strict train candidates survived selection audit, and no leave-one-out subset became guard-safe.",
            "minimum_new_rows": 20,
            "selection_rule": "Collect rank 11-50 directionally useful teacher-divergence rows with no severe/core regression tags and no overlap with protected/tail instability.",
            "acceptance_rule": "Candidate rows may be trainable only after no-save checks show train improvement without protected/tail guard failure.",
            "do_not_use_as": "checkpoint_producing_train_until_guard_safe",
        },
        {
            "priority": "P1",
            "target_area": "quarantine_review",
            "current_evidence": "3 prior train rows became quarantine: legacy_g2_m11, legacy_g2_m21, legacy_g5_m14",
            "minimum_new_rows": 0,
            "selection_rule": "Do not expand from severe/core-regression families unless explicitly reviewed as negative examples.",
            "acceptance_rule": "Quarantine rows remain excluded from ordinary training.",
            "do_not_use_as": "ordinary_train_rows",
        },
        {
            "priority": "P2",
            "target_area": "family_diversity",
            "current_evidence": "Current corpus is small and concentrated; no 25-row subset was guard-safe for b4c96.",
            "minimum_new_rows": 20,
            "selection_rule": "Prefer more games/families rather than multiple near-duplicates from the same local pattern.",
            "acceptance_rule": "Expansion manifest should include game/family balancing and duplicate-family flags.",
            "do_not_use_as": "unbalanced_single_family_expansion",
        },
    ]

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    fields = [
        "priority",
        "target_area",
        "current_evidence",
        "minimum_new_rows",
        "selection_rule",
        "acceptance_rule",
        "do_not_use_as",
    ]
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        for row in expansion_targets:
            w.writerow(row)

    summary = {
        "decision": "TEACHER_DIVERGENCE_EXPANSION_TARGETS_READY",
        "scope": "planning only; no training/checkpoint/export/benchmark/promotion",
        "inputs": {
            "row_level_summary": str(ROW_LEVEL_SUMMARY),
            "row_level_report": str(ROW_LEVEL_REPORT),
            "nosave_summary": str(NOSAVE_SUMMARY),
            "selection_summary": str(SELECTION_SUMMARY),
            "materialized_summary": str(MATERIALIZED_SUMMARY),
            "stop_review": str(STOP_REVIEW),
        },
        "current_findings": {
            "selection_base_rows": selection.get("base_rows"),
            "strict_train_candidate_rows": selection.get("strict_train_candidate_rows"),
            "materialized_train_rows": materialized.get("train_rows"),
            "materialized_protected_eval_rows": materialized.get("protected_eval_rows"),
            "materialized_tail_eval_rows": materialized.get("tail_eval_rows"),
            "materialized_quarantine_rows": materialized.get("quarantine_rows"),
            "row_level_decision": row_level.get("decision"),
            "tail_failure": bool(tail_failure),
            "protected_failure": bool(protected_failure),
            "train_improved": bool(train_improved),
        },
        "expansion_targets": expansion_targets,
        "recommended_next_branch": "exp/15x15-teacher-divergence-expansion-source-audit-next",
        "recommended_next_step": "Audit available source artifacts for rows matching P0/P1 expansion targets before building any new training dataset.",
    }

    OUT_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines: list[str] = []
    lines += ["# Teacher-divergence expansion targets", ""]
    lines += ["## Scope", ""]
    lines += [
        "- Expansion target planning only.",
        "- No training.",
        "- No checkpoint read or write.",
        "- No C export, no public benchmark, no promotion.",
        "",
    ]

    lines += ["## Why expansion is required", ""]
    lines += [
        "The conservative 4-train-row no-save probe improved the train group but still failed protected/tail guards.",
        "",
        "Leave-one-train-candidate-out review showed that removing any single train candidate did not produce a guard-safe subset.",
        "",
        "Therefore the current 25-row corpus is insufficient for stable b4c96 capacity work. The next safe step is targeted data expansion, not more training.",
        "",
    ]

    lines += ["## Current findings", ""]
    cf = summary["current_findings"]
    for k, v in cf.items():
        lines.append(f"- {k}: `{v}`")
    lines.append("")

    lines += ["## Expansion targets", ""]
    lines += [
        "| priority | target_area | minimum_new_rows | do_not_use_as |",
        "|---|---|---:|---|",
    ]
    for row in expansion_targets:
        lines.append(
            f"| {row['priority']} | {row['target_area']} | {row['minimum_new_rows']} | {row['do_not_use_as']} |"
        )
    lines.append("")

    lines += ["## Detailed rules", ""]
    for row in expansion_targets:
        lines += [
            f"### {row['priority']} {row['target_area']}",
            "",
            f"- current evidence: {row['current_evidence']}",
            f"- minimum new rows: {row['minimum_new_rows']}",
            f"- selection rule: {row['selection_rule']}",
            f"- acceptance rule: {row['acceptance_rule']}",
            f"- do not use as: `{row['do_not_use_as']}`",
            "",
        ]

    lines += ["## Decision", ""]
    lines += [
        "`TEACHER_DIVERGENCE_EXPANSION_TARGETS_READY`",
        "",
        "Recommended next branch:",
        "",
        "`exp/15x15-teacher-divergence-expansion-source-audit-next`",
        "",
        "The next branch should audit available source artifacts for rows matching these targets. It should not train.",
        "",
    ]

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("decision:", summary["decision"])
    print("row_level_decision:", row_level.get("decision"))
    print("tail_failure:", tail_failure)
    print("protected_failure:", protected_failure)
    print("train_improved:", train_improved)
    print("out_csv:", OUT_CSV)
    print("out_json:", OUT_JSON)
    print("out_report:", OUT_MD)
    print("status: planning only; no training/checkpoint/export/benchmark/promotion")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
