#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


SOURCE_AUDIT_SUMMARY = Path("analysis/integration_eval/teacher_divergence_expansion_source_audit_next/source_audit_summary.json")
EXPANSION_TARGETS = Path("analysis/integration_eval/teacher_divergence_expansion_targets/expansion_targets_summary.json")
SOURCE_MANIFEST = Path("analysis/integration_eval/teacher_divergence_expansion_source_audit_next/source_candidate_manifest.csv")

OUT_DIR = Path("analysis/integration_eval/teacher_divergence_tail_source_generation_plan")
OUT_CSV = OUT_DIR / "tail_source_generation_steps.csv"
OUT_JSON = OUT_DIR / "tail_source_generation_summary.json"
OUT_MD = OUT_DIR / "tail_source_generation_report.md"


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
    source_audit = read_json(SOURCE_AUDIT_SUMMARY)
    expansion_targets = read_json(EXPANSION_TARGETS)
    manifest_rows = read_csv(SOURCE_MANIFEST)

    bucket_counts = source_audit["candidate_new_counts"]
    target_gaps = source_audit["target_gaps"]

    unclassified_rows = [
        r for r in manifest_rows
        if r["recommended_bucket"] == "unclassified_review"
    ]

    source_counts: dict[str, int] = {}
    for r in unclassified_rows:
        source_counts[r["source_path"]] = source_counts.get(r["source_path"], 0) + 1

    steps = [
        {
            "step": 1,
            "phase": "schema_recovery",
            "purpose": "Inspect the 599 unclassified_review rows and recover missing rank/prob/role fields from source-specific schemas.",
            "input": "source_candidate_manifest.csv plus original source artifacts",
            "output": "tail_source_schema_recovery_manifest.csv",
            "acceptance": "At least one source-specific extractor identifies candidate rows with usable board/side/target fields.",
            "training_allowed": "no",
        },
        {
            "step": 2,
            "phase": "tail_candidate_mining",
            "purpose": "Mine rank>50 or near-tail teacher-divergence cases from recovered source rows.",
            "input": "schema recovery manifest",
            "output": "tail_guard_candidate_manifest.csv",
            "acceptance": "At least 12 unique P0 tail_guard candidates, preferably from multiple games/families.",
            "training_allowed": "no",
        },
        {
            "step": 3,
            "phase": "protected_train_gap_review",
            "purpose": "Keep already found protected candidates and identify at least 5 more train candidates only if schemas are reliable.",
            "input": "source audit candidate buckets",
            "output": "protected_train_candidate_review.csv",
            "acceptance": "Protected remains >=12 and P1 train candidate pool reaches >=20 without using quarantine rows.",
            "training_allowed": "no",
        },
        {
            "step": 4,
            "phase": "candidate_materialization_dryrun",
            "purpose": "Materialize a candidate-only review dataset with tail/protected held out and train candidates separated.",
            "input": "tail/protected/train candidate manifests",
            "output": "candidate review dataset only",
            "acceptance": "Schema validates, suppress_rcs are complete, no overlap across train/protected/tail/quarantine.",
            "training_allowed": "no",
        },
        {
            "step": 5,
            "phase": "future_no_save_probe_gate",
            "purpose": "Only after candidate review passes, run no-save probes to check guard stability.",
            "input": "candidate review dataset",
            "output": "no-save metrics only",
            "acceptance": "tail rank_gt50_delta <= 0, tail mean_rank_delta <= 0, protected top5_delta >= 0, protected top10_delta >= 0.",
            "training_allowed": "no checkpoint-producing training",
        },
    ]

    decision = (
        "TAIL_SOURCE_GENERATION_PLAN_REQUIRED"
        if target_gaps.get("P0_tail_guard_candidate", 0) > 0
        else "TAIL_SOURCE_GENERATION_NOT_REQUIRED"
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    fields = [
        "step",
        "phase",
        "purpose",
        "input",
        "output",
        "acceptance",
        "training_allowed",
    ]
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        for row in steps:
            w.writerow(row)

    summary = {
        "decision": decision,
        "scope": "planning only; no dataset build/training/checkpoint/export/benchmark/promotion",
        "inputs": {
            "source_audit_summary": str(SOURCE_AUDIT_SUMMARY),
            "expansion_targets": str(EXPANSION_TARGETS),
            "source_manifest": str(SOURCE_MANIFEST),
        },
        "upstream": {
            "source_audit_decision": source_audit["decision"],
            "expansion_targets_decision": expansion_targets["decision"],
            "candidate_new_counts": bucket_counts,
            "target_gaps": target_gaps,
            "unclassified_review_rows": len(unclassified_rows),
            "unclassified_source_counts": source_counts,
        },
        "tail_gap": target_gaps.get("P0_tail_guard_candidate", 0),
        "protected_gap": target_gaps.get("P0_protected_guard_candidate", 0),
        "train_gap": target_gaps.get("P1_train_candidate", 0),
        "steps": steps,
        "recommended_next_branch": "exp/15x15-teacher-divergence-tail-schema-recovery",
        "recommended_next_step": "Recover source-specific schema fields from unclassified rows, then mine tail guard candidates.",
    }

    OUT_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines: list[str] = []
    lines += ["# Teacher-divergence tail source generation plan", ""]
    lines += ["## Scope", ""]
    lines += [
        "- Planning only.",
        "- No dataset build.",
        "- No training.",
        "- No checkpoint read or write.",
        "- No C export, no public benchmark, no promotion.",
        "",
    ]

    lines += ["## Why this plan is needed", ""]
    lines += [
        "The expansion source audit found partial candidates only.",
        "",
        f"- P0 tail guard candidates: `{bucket_counts.get('P0_tail_guard_candidate', 0)}` / `12`",
        f"- P0 protected guard candidates: `{bucket_counts.get('P0_protected_guard_candidate', 0)}` / `12`",
        f"- P1 train candidates: `{bucket_counts.get('P1_train_candidate', 0)}` / `20`",
        "",
        "The blocker is tail guard coverage. Source artifacts currently expose zero usable P0 tail guard candidates under the generic audit.",
        "",
    ]

    lines += ["## Unclassified source inventory", ""]
    lines += ["| source | unclassified rows |", "|---|---:|"]
    for source, count in sorted(source_counts.items()):
        lines.append(f"| `{source}` | {count} |")
    lines.append("")

    lines += ["## Plan steps", ""]
    lines += [
        "| step | phase | output | training_allowed |",
        "|---:|---|---|---|",
    ]
    for row in steps:
        lines.append(
            f"| {row['step']} | {row['phase']} | {row['output']} | {row['training_allowed']} |"
        )
    lines.append("")

    lines += ["## Detailed acceptance rules", ""]
    for row in steps:
        lines += [
            f"### Step {row['step']}: {row['phase']}",
            "",
            f"- purpose: {row['purpose']}",
            f"- input: {row['input']}",
            f"- output: {row['output']}",
            f"- acceptance: {row['acceptance']}",
            f"- training allowed: `{row['training_allowed']}`",
            "",
        ]

    lines += ["## Decision", ""]
    lines += [
        f"`{decision}`",
        "",
        "Recommended next branch:",
        "",
        "`exp/15x15-teacher-divergence-tail-schema-recovery`",
        "",
        "The next branch should recover source-specific schemas from unclassified rows and attempt to mine tail guard candidates. It should not train.",
        "",
    ]

    lines += ["## Final note", ""]
    lines += [
        "This plan does not authorize training, checkpoint save, C export, public benchmark, promotion, or current_best overwrite.",
        "",
    ]

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("decision:", decision)
    print("tail_gap:", summary["tail_gap"])
    print("protected_gap:", summary["protected_gap"])
    print("train_gap:", summary["train_gap"])
    print("unclassified_review_rows:", len(unclassified_rows))
    print("out_csv:", OUT_CSV)
    print("out_json:", OUT_JSON)
    print("out_report:", OUT_MD)
    print("status: planning only; no dataset build/training/checkpoint/export/benchmark/promotion")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
