#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


READY = "READY_FOR_FUTURE_GUARDED_EVAL_REVIEW"
NEEDS_REPAIR = "NEEDS_REPAIR"
NOT_READY = "NOT_READY"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Normalize reviewed direct manifest rows without eval/training/checkpoint reads."
    )
    p.add_argument(
        "--inspection-rows",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_next_direct_adapter_blocker_inspection_rows.csv"),
    )
    p.add_argument(
        "--inspection-summary",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_next_direct_adapter_blocker_inspection_summary.csv"),
    )
    p.add_argument(
        "--inspection-decision-json",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_next_direct_adapter_blocker_inspection_decision.json"),
    )
    p.add_argument(
        "--original-direct-manifest",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_direct_probe_eval_adapter_manifest.csv"),
    )
    p.add_argument(
        "--repair-plan-decision-json",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_next_direct_probe_input_repair_plan_decision.json"),
    )
    p.add_argument(
        "--combined-summary",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_local_comparison_executor_dryrun_combined_summary.csv"),
    )
    p.add_argument(
        "--candidate-checkpoint",
        type=Path,
        default=Path("checkpoints/15x15_teacher_divergence_round2_policy_margin_gated_run1_e10.pt"),
    )
    p.add_argument(
        "--current-best-checkpoint",
        type=Path,
        default=Path("checkpoints/15x15_current_best.pt"),
    )
    p.add_argument(
        "--out-normalized-manifest",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_next_direct_manifest_normalization_review_manifest.csv"),
    )
    p.add_argument(
        "--out-repair-queue",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_next_direct_manifest_normalization_review_repair_queue.csv"),
    )
    p.add_argument(
        "--out-quarantine",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_next_direct_manifest_normalization_review_quarantine.csv"),
    )
    p.add_argument(
        "--out-summary-csv",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_next_direct_manifest_normalization_review_summary.csv"),
    )
    p.add_argument(
        "--out-decision-json",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_next_direct_manifest_normalization_review_decision.json"),
    )
    p.add_argument(
        "--out-report",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_next_direct_manifest_normalization_review.md"),
    )
    return p.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def by_metric(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {r["metric"]: r for r in rows}


def get(m: dict[str, dict[str, str]], key: str, default: str = "") -> str:
    return m.get(key, {}).get("value", default)


def as_int(value: Any) -> int:
    if value in ("", None):
        return 0
    return int(float(value))


def as_float(value: Any) -> float:
    if value in ("", None):
        return 0.0
    return float(value)


def metric_from_combined(rows: list[dict[str, str]], metric: str, default: str = "") -> str:
    for r in rows:
        if r.get("metric") == metric:
            return r.get("value", default)
    return default


def row(metric: str, value: Any, status: str, notes: str = "") -> dict[str, str]:
    return {
        "metric": metric,
        "value": str(value),
        "status": status,
        "notes": notes,
    }


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def esc(value: Any) -> str:
    return str(value).replace("|", "\\|")


def normalize_ready_row(r: dict[str, str], normalized_id: int) -> dict[str, str]:
    return {
        "normalized_manifest_id": f"direct_norm_{normalized_id:03d}",
        "source_manifest_row_id": r.get("manifest_row_id", ""),
        "source_eval_manifest_id": r.get("eval_manifest_id", ""),
        "source_adapter_kind": r.get("adapter_kind", ""),
        "source_path": r.get("path", ""),
        "source_format": r.get("inferred_format", ""),
        "source_path_exists": r.get("path_exists", ""),
        "source_inspected_count": r.get("inspected_count", ""),
        "schema_status": r.get("schema_status", ""),
        "provenance_status": r.get("provenance_status", ""),
        "leakage_risk": r.get("leakage_risk", ""),
        "direct_eval_readiness": r.get("direct_eval_readiness", ""),
        "risk_level": r.get("risk_level", ""),
        "normalized_role": "future_guarded_direct_probe_candidate",
        "normalized_status": "NORMALIZED_REVIEW_READY",
        "eval_allowed_now": "0",
        "requires_future_explicit_flags": "1",
        "checkpoint_read_allowed_now": "0",
        "notes": "Candidate input row only; future eval executor still not built or enabled.",
    }


def repair_queue_row(r: dict[str, str], repair_id: int) -> dict[str, str]:
    return {
        "repair_queue_id": f"direct_repair_{repair_id:03d}",
        "source_manifest_row_id": r.get("manifest_row_id", ""),
        "source_eval_manifest_id": r.get("eval_manifest_id", ""),
        "source_adapter_kind": r.get("adapter_kind", ""),
        "source_path": r.get("path", ""),
        "schema_status": r.get("schema_status", ""),
        "provenance_status": r.get("provenance_status", ""),
        "leakage_risk": r.get("leakage_risk", ""),
        "direct_eval_readiness": r.get("direct_eval_readiness", ""),
        "recommended_action": r.get("recommended_action", ""),
        "problems": r.get("problems", ""),
        "repair_status": "REPAIR_REQUIRED_BEFORE_NORMALIZATION",
        "eval_allowed_now": "0",
        "notes": "Do not pass into eval executor until schema/provenance is repaired and re-reviewed.",
    }


def quarantine_row(r: dict[str, str], quarantine_id: int) -> dict[str, str]:
    return {
        "quarantine_id": f"direct_quarantine_{quarantine_id:03d}",
        "source_manifest_row_id": r.get("manifest_row_id", ""),
        "source_eval_manifest_id": r.get("eval_manifest_id", ""),
        "source_adapter_kind": r.get("adapter_kind", ""),
        "source_path": r.get("path", ""),
        "schema_status": r.get("schema_status", ""),
        "provenance_status": r.get("provenance_status", ""),
        "leakage_risk": r.get("leakage_risk", ""),
        "direct_eval_readiness": r.get("direct_eval_readiness", ""),
        "recommended_action": r.get("recommended_action", ""),
        "problems": r.get("problems", ""),
        "quarantine_reason": "not_ready_or_high_risk_from_blocker_inspection",
        "eval_allowed_now": "0",
        "notes": "Excluded from normalized direct manifest.",
    }


def main() -> None:
    args = parse_args()

    for p in [
        args.inspection_rows,
        args.inspection_summary,
        args.inspection_decision_json,
        args.original_direct_manifest,
        args.repair_plan_decision_json,
        args.combined_summary,
        args.current_best_checkpoint,
    ]:
        if not p.exists():
            raise FileNotFoundError(p)

    inspection_rows = read_csv(args.inspection_rows)
    inspection_summary = by_metric(read_csv(args.inspection_summary))
    inspection_decision = json.loads(args.inspection_decision_json.read_text(encoding="utf-8"))
    original_manifest = read_csv(args.original_direct_manifest)
    repair_plan_decision = json.loads(args.repair_plan_decision_json.read_text(encoding="utf-8"))
    combined = read_csv(args.combined_summary)

    inspection_decision_value = get(inspection_summary, "inspection_decision")
    plan_decision = inspection_decision.get("plan_decision", "")
    repair_plan = repair_plan_decision.get("plan_decision", "")

    candidate_exists = args.candidate_checkpoint.exists()
    current_best_exists = args.current_best_checkpoint.exists()

    ready = [r for r in inspection_rows if r.get("direct_eval_readiness") == READY]
    repair = [r for r in inspection_rows if r.get("direct_eval_readiness") == NEEDS_REPAIR]
    quarantine = [r for r in inspection_rows if r.get("direct_eval_readiness") == NOT_READY or r.get("recommended_action") == "QUARANTINE_FOR_NOW"]

    ready_ids = {r.get("manifest_row_id") for r in ready}
    repair_ids = {r.get("manifest_row_id") for r in repair}
    quarantine_ids = {r.get("manifest_row_id") for r in quarantine}
    classified_ids = ready_ids | repair_ids | quarantine_ids
    unclassified = [r for r in inspection_rows if r.get("manifest_row_id") not in classified_ids]

    normalized_rows = [normalize_ready_row(r, i) for i, r in enumerate(ready, start=1)]
    repair_rows = [repair_queue_row(r, i) for i, r in enumerate(repair + unclassified, start=1)]
    quarantine_rows = [quarantine_row(r, i) for i, r in enumerate(quarantine, start=1)]

    combined_fail_rows = [r for r in combined if r.get("status") == "FAIL"]
    combined_warn_rows = [r for r in combined if r.get("status") == "WARN"]

    trainable_gap_improved = as_int(metric_from_combined(combined, "gap_improved_rows"))
    trainable_rank_regressed = as_int(metric_from_combined(combined, "target_rank_regressed_rows"))
    protected_rank_regressed = as_int(metric_from_combined(combined, "protected_top10_rank_regressed_rows"))
    protected_prob_regressed = as_int(metric_from_combined(combined, "protected_top10_prob_regressed_rows"))
    tail_rank_regressed = as_int(metric_from_combined(combined, "tail_rank_gt50_rank_regressed_rows"))
    tail_prob_regressed = as_int(metric_from_combined(combined, "tail_rank_gt50_prob_regressed_rows"))
    anchor_top1_changed = as_int(metric_from_combined(combined, "anchor_top1_changed_rows"))
    anchor_max_kl = as_float(metric_from_combined(combined, "anchor_max_kl"))

    blockers: list[str] = []
    warnings: list[str] = []

    if inspection_decision_value != "DIRECT_ADAPTER_BLOCKER_INSPECTION_READY_FOR_NORMALIZATION_REVIEW":
        blockers.append(f"inspection decision not ready for normalization review: {inspection_decision_value}")
    if plan_decision != "DIRECT_PROBE_INPUT_REPAIR_PLAN_READY":
        blockers.append(f"inspection json plan decision not ready: {plan_decision}")
    if repair_plan != "DIRECT_PROBE_INPUT_REPAIR_PLAN_READY":
        blockers.append(f"repair plan decision not ready: {repair_plan}")
    if not current_best_exists:
        blockers.append("current_best checkpoint path missing")
    if not inspection_rows:
        blockers.append("inspection rows empty")
    if len(inspection_rows) != len(original_manifest):
        blockers.append(f"inspection/original manifest row mismatch: {len(inspection_rows)} vs {len(original_manifest)}")
    if not normalized_rows:
        blockers.append("no ready rows to normalize")
    if combined_fail_rows:
        blockers.append(f"combined FAIL rows present: {len(combined_fail_rows)}")
    if trainable_gap_improved != 44:
        blockers.append(f"trainable gap improved rows not 44: {trainable_gap_improved}")
    if trainable_rank_regressed > 0:
        blockers.append(f"trainable rank regressions present: {trainable_rank_regressed}")
    if protected_rank_regressed > 0:
        blockers.append(f"protected rank regressions present: {protected_rank_regressed}")
    if tail_rank_regressed > 0:
        blockers.append(f"tail rank regressions present: {tail_rank_regressed}")
    if anchor_top1_changed > 0:
        blockers.append(f"anchor top1 changes present: {anchor_top1_changed}")
    if anchor_max_kl > 0.005:
        blockers.append(f"anchor max KL too high: {anchor_max_kl:.10f}")

    if not candidate_exists:
        warnings.append("candidate checkpoint missing locally; no checkpoint read needed for normalization review")
    if combined_warn_rows:
        warnings.append(f"combined WARN rows carried forward: {len(combined_warn_rows)}")
    if protected_prob_regressed:
        warnings.append(f"protected probability regressions carried forward: {protected_prob_regressed}")
    if tail_prob_regressed:
        warnings.append(f"tail probability regressions carried forward: {tail_prob_regressed}")
    if repair_rows:
        warnings.append(f"repair queue rows: {len(repair_rows)}")
    if quarantine_rows:
        warnings.append(f"quarantine rows excluded: {len(quarantine_rows)}")
    if unclassified:
        warnings.append(f"unclassified rows sent to repair queue: {len(unclassified)}")

    if blockers:
        normalization_decision = "DIRECT_MANIFEST_NORMALIZATION_REVIEW_BLOCKED"
        recommended_next = "Fix hard blockers before manifest materialization."
    elif repair_rows:
        normalization_decision = "DIRECT_MANIFEST_NORMALIZATION_REVIEW_READY_WITH_REPAIR_QUEUE"
        recommended_next = (
            "Use the normalized ready manifest as a review-only candidate. "
            "Repair queued rows separately. Do not build eval executor yet."
        )
    else:
        normalization_decision = "DIRECT_MANIFEST_NORMALIZATION_REVIEW_READY"
        recommended_next = (
            "Use normalized ready manifest as review-only candidate input. "
            "Keep eval disabled until a later explicit executor dry-run branch."
        )

    normalized_fieldnames = [
        "normalized_manifest_id",
        "source_manifest_row_id",
        "source_eval_manifest_id",
        "source_adapter_kind",
        "source_path",
        "source_format",
        "source_path_exists",
        "source_inspected_count",
        "schema_status",
        "provenance_status",
        "leakage_risk",
        "direct_eval_readiness",
        "risk_level",
        "normalized_role",
        "normalized_status",
        "eval_allowed_now",
        "requires_future_explicit_flags",
        "checkpoint_read_allowed_now",
        "notes",
    ]
    repair_fieldnames = [
        "repair_queue_id",
        "source_manifest_row_id",
        "source_eval_manifest_id",
        "source_adapter_kind",
        "source_path",
        "schema_status",
        "provenance_status",
        "leakage_risk",
        "direct_eval_readiness",
        "recommended_action",
        "problems",
        "repair_status",
        "eval_allowed_now",
        "notes",
    ]
    quarantine_fieldnames = [
        "quarantine_id",
        "source_manifest_row_id",
        "source_eval_manifest_id",
        "source_adapter_kind",
        "source_path",
        "schema_status",
        "provenance_status",
        "leakage_risk",
        "direct_eval_readiness",
        "recommended_action",
        "problems",
        "quarantine_reason",
        "eval_allowed_now",
        "notes",
    ]

    write_csv(args.out_normalized_manifest, normalized_rows, normalized_fieldnames)
    write_csv(args.out_repair_queue, repair_rows, repair_fieldnames)
    write_csv(args.out_quarantine, quarantine_rows, quarantine_fieldnames)

    summary_rows = [
        row("normalization_decision", normalization_decision, "INFO", "Review only; no model eval."),
        row("recommended_next", recommended_next, "INFO"),
        row("inspection_decision", inspection_decision_value, "INFO"),
        row("plan_decision", plan_decision, "INFO"),
        row("repair_plan_decision", repair_plan, "INFO"),
        row("original_manifest_rows", len(original_manifest), "INFO"),
        row("inspection_rows", len(inspection_rows), "INFO"),
        row("normalized_ready_rows", len(normalized_rows), "INFO"),
        row("repair_queue_rows", len(repair_rows), "WARN" if repair_rows else "PASS"),
        row("quarantine_rows", len(quarantine_rows), "WARN" if quarantine_rows else "PASS"),
        row("unclassified_rows", len(unclassified), "WARN" if unclassified else "PASS"),
        row("blocker_count", len(blockers), "PASS" if not blockers else "FAIL", "; ".join(blockers)),
        row("warning_count", len(warnings), "WARN" if warnings else "PASS", "; ".join(warnings)),
        row("candidate_checkpoint_exists_locally", int(candidate_exists), "INFO", "Existence only; no checkpoint read."),
        row("current_best_exists", int(current_best_exists), "PASS" if current_best_exists else "FAIL"),
        row("combined_fail_rows", len(combined_fail_rows), "PASS" if not combined_fail_rows else "FAIL"),
        row("combined_warn_rows", len(combined_warn_rows), "WARN" if combined_warn_rows else "PASS"),
        row("trainable_gap_improved", trainable_gap_improved, "PASS" if trainable_gap_improved == 44 else "FAIL"),
        row("trainable_rank_regressed", trainable_rank_regressed, "PASS" if trainable_rank_regressed == 0 else "FAIL"),
        row("protected_rank_regressed", protected_rank_regressed, "PASS" if protected_rank_regressed == 0 else "FAIL"),
        row("tail_rank_regressed", tail_rank_regressed, "PASS" if tail_rank_regressed == 0 else "WARN"),
        row("protected_prob_regressed", protected_prob_regressed, "WARN" if protected_prob_regressed else "PASS"),
        row("tail_prob_regressed", tail_prob_regressed, "WARN" if tail_prob_regressed else "PASS"),
        row("anchor_top1_changed", anchor_top1_changed, "PASS" if anchor_top1_changed == 0 else "FAIL"),
        row("anchor_max_kl", f"{anchor_max_kl:.10f}", "PASS" if anchor_max_kl <= 0.005 else "FAIL"),
        row("would_train", 0, "PASS"),
        row("would_eval_model_now", 0, "PASS"),
        row("would_read_checkpoint_contents_now", 0, "PASS"),
        row("would_write_checkpoint", 0, "PASS"),
        row("would_c_export", 0, "PASS"),
        row("would_public_benchmark", 0, "PASS"),
        row("would_promote", 0, "PASS"),
    ]

    write_csv(args.out_summary_csv, summary_rows, ["metric", "value", "status", "notes"])

    decision = {
        "normalization_decision": normalization_decision,
        "recommended_next": recommended_next,
        "inspection_decision": inspection_decision_value,
        "plan_decision": plan_decision,
        "repair_plan_decision": repair_plan,
        "would_train_now": False,
        "would_eval_model_now": False,
        "would_read_checkpoint_contents_now": False,
        "would_write_checkpoint": False,
        "would_c_export": False,
        "would_public_benchmark": False,
        "would_promote": False,
        "candidate_checkpoint_path": str(args.candidate_checkpoint),
        "current_best_checkpoint_path": str(args.current_best_checkpoint),
        "row_counts": {
            "original_manifest_rows": len(original_manifest),
            "inspection_rows": len(inspection_rows),
            "normalized_ready_rows": len(normalized_rows),
            "repair_queue_rows": len(repair_rows),
            "quarantine_rows": len(quarantine_rows),
            "unclassified_rows": len(unclassified),
        },
        "outputs": {
            "normalized_manifest": str(args.out_normalized_manifest),
            "repair_queue": str(args.out_repair_queue),
            "quarantine": str(args.out_quarantine),
            "summary_csv": str(args.out_summary_csv),
            "report": str(args.out_report),
        },
        "blockers": blockers,
        "warnings": warnings,
    }

    args.out_decision_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_decision_json.write_text(json.dumps(decision, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    report = [
        "# Teacher-divergence next direct manifest normalization review",
        "",
        "## Branch",
        "",
        "`exp/15x15-teacher-divergence-next-direct-manifest-normalization-review`",
        "",
        "## Scope",
        "",
        "- Normalizes ready direct manifest rows into a stricter review-only manifest.",
        "- Places repairable rows into a repair queue.",
        "- Places unsafe/not-ready rows into quarantine.",
        "- Does not train.",
        "- Does not run model eval.",
        "- Does not read checkpoint contents.",
        "- Does not write checkpoints.",
        "- Does not overwrite `checkpoints/15x15_current_best.pt`.",
        "- Does not C export.",
        "- Does not run public benchmark.",
        "- Does not promote.",
        "",
        "## Normalization decision",
        "",
        f"`{normalization_decision}`",
        "",
        "## Recommended next",
        "",
        recommended_next,
        "",
        "## Row split",
        "",
        "| bucket | rows |",
        "|---|---:|",
        f"| normalized_ready_rows | {len(normalized_rows)} |",
        f"| repair_queue_rows | {len(repair_rows)} |",
        f"| quarantine_rows | {len(quarantine_rows)} |",
        f"| unclassified_rows | {len(unclassified)} |",
        "",
        "## Normalized manifest preview",
        "",
        "| normalized_manifest_id | source_manifest_row_id | source_eval_manifest_id | source_path | status | eval_allowed_now |",
        "|---|---:|---|---|---|---:|",
    ]

    for r in normalized_rows:
        report.append(
            f"| {esc(r['normalized_manifest_id'])} | {esc(r['source_manifest_row_id'])} | {esc(r['source_eval_manifest_id'])} | `{esc(r['source_path'])}` | {esc(r['normalized_status'])} | {esc(r['eval_allowed_now'])} |"
        )

    report.extend([
        "",
        "## Repair queue preview",
        "",
        "| repair_queue_id | source_manifest_row_id | source_eval_manifest_id | action | problems |",
        "|---|---:|---|---|---|",
    ])
    if repair_rows:
        for r in repair_rows:
            report.append(
                f"| {esc(r['repair_queue_id'])} | {esc(r['source_manifest_row_id'])} | {esc(r['source_eval_manifest_id'])} | {esc(r['recommended_action'])} | {esc(r['problems'])} |"
            )
    else:
        report.append("| none |  |  |  |  |")

    report.extend([
        "",
        "## Quarantine preview",
        "",
        "| quarantine_id | source_manifest_row_id | source_eval_manifest_id | provenance | action | problems |",
        "|---|---:|---|---|---|---|",
    ])
    if quarantine_rows:
        for r in quarantine_rows:
            report.append(
                f"| {esc(r['quarantine_id'])} | {esc(r['source_manifest_row_id'])} | {esc(r['source_eval_manifest_id'])} | {esc(r['provenance_status'])} | {esc(r['recommended_action'])} | {esc(r['problems'])} |"
            )
    else:
        report.append("| none |  |  |  |  |  |")

    report.extend([
        "",
        "## Summary",
        "",
        "| metric | value | status | notes |",
        "|---|---:|---|---|",
    ])
    for r in summary_rows:
        report.append(f"| {esc(r['metric'])} | {esc(r['value'])} | {esc(r['status'])} | {esc(r['notes'])} |")

    report.extend(["", "## Blockers", ""])
    if blockers:
        report.extend([f"- {b}" for b in blockers])
    else:
        report.append("- None.")

    report.extend(["", "## Warnings", ""])
    if warnings:
        report.extend([f"- {w}" for w in warnings])
    else:
        report.append("- None.")

    report.extend([
        "",
        "## Interpretation",
        "",
    ])
    if normalization_decision == "DIRECT_MANIFEST_NORMALIZATION_REVIEW_READY_WITH_REPAIR_QUEUE":
        report.append("Three ready rows can be preserved in a stricter manifest, while repair/quarantine rows remain excluded from any eval path.")
    elif normalization_decision == "DIRECT_MANIFEST_NORMALIZATION_REVIEW_READY":
        report.append("Ready rows are normalized. This is still a review-only artifact, not an eval executor.")
    else:
        report.append("Normalization is blocked; do not continue until blockers are fixed.")

    report.extend([
        "",
        "## Final guardrails",
        "",
        "- Normalized manifest is review-only.",
        "- `eval_allowed_now` is 0 for every row.",
        "- Keep the run1 candidate checkpoint isolated.",
        "- No current_best overwrite.",
        "- No C export.",
        "- No public benchmark.",
        "- No promotion.",
        "- Do not add local checkpoint artifacts to git.",
        "",
    ])

    args.out_report.parent.mkdir(parents=True, exist_ok=True)
    args.out_report.write_text("\n".join(report), encoding="utf-8")

    print("normalization_decision:", normalization_decision)
    print("recommended_next:", recommended_next)
    print("original_manifest_rows:", len(original_manifest))
    print("inspection_rows:", len(inspection_rows))
    print("normalized_ready_rows:", len(normalized_rows))
    print("repair_queue_rows:", len(repair_rows))
    print("quarantine_rows:", len(quarantine_rows))
    print("unclassified_rows:", len(unclassified))
    print("blocker_count:", len(blockers))
    print("warning_count:", len(warnings))
    print("out_normalized_manifest:", args.out_normalized_manifest)
    print("out_repair_queue:", args.out_repair_queue)
    print("out_quarantine:", args.out_quarantine)
    print("out_summary_csv:", args.out_summary_csv)
    print("out_decision_json:", args.out_decision_json)
    print("out_report:", args.out_report)
    print("normalization review only; no model eval; no training; no checkpoint read/write; no C export; no benchmark; no promotion")


if __name__ == "__main__":
    main()
