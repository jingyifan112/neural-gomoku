#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Plan next direct-probe / heldout input repair after run1 conservative closeout."
    )
    p.add_argument(
        "--final-closeout-summary",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_core_reuse_final_closeout_summary.csv"),
    )
    p.add_argument(
        "--final-closeout-decision-json",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_core_reuse_final_closeout_decision.json"),
    )
    p.add_argument(
        "--direct-adapter-summary",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_direct_probe_eval_adapter_summary.csv"),
    )
    p.add_argument(
        "--direct-manifest",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_direct_probe_eval_adapter_manifest.csv"),
    )
    p.add_argument(
        "--combined-summary",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_local_comparison_executor_dryrun_combined_summary.csv"),
    )
    p.add_argument(
        "--blocker-review-summary",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_next_stage_blocker_review_summary.csv"),
    )
    p.add_argument(
        "--optional-fixed-input-audit-summary",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_fixed_probe_heldout_input_audit_summary.csv"),
    )
    p.add_argument(
        "--optional-fixed-input-audit-manifest",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_fixed_probe_heldout_input_audit_manifest.csv"),
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
        "--out-summary-csv",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_next_direct_probe_input_repair_plan_summary.csv"),
    )
    p.add_argument(
        "--out-actions-csv",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_next_direct_probe_input_repair_actions.csv"),
    )
    p.add_argument(
        "--out-decision-json",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_next_direct_probe_input_repair_plan_decision.json"),
    )
    p.add_argument(
        "--out-report",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_next_direct_probe_input_repair_plan.md"),
    )
    return p.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def maybe_read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    return read_csv(path)


def by_metric(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {r["metric"]: r for r in rows}


def get(m: dict[str, dict[str, str]], key: str, default: str = "") -> str:
    return m.get(key, {}).get("value", default)


def notes(m: dict[str, dict[str, str]], key: str, default: str = "") -> str:
    return m.get(key, {}).get("notes", default)


def as_int(value: Any) -> int:
    if value in ("", None):
        return 0
    return int(float(value))


def as_float(value: Any) -> float:
    if value in ("", None):
        return 0.0
    return float(value)


def combined_metric(rows: list[dict[str, str]], metric: str, default: str = "") -> str:
    for r in rows:
        if r.get("metric") == metric:
            return r.get("value", default)
    return default


def row(metric: str, value: Any, status: str, notes_text: str = "") -> dict[str, str]:
    return {
        "metric": metric,
        "value": str(value),
        "status": status,
        "notes": notes_text,
    }


def action(
    priority: int,
    action_id: str,
    action_type: str,
    rationale: str,
    proposed_output: str,
    guardrail: str,
) -> dict[str, str]:
    return {
        "priority": str(priority),
        "action_id": action_id,
        "action_type": action_type,
        "rationale": rationale,
        "proposed_output": proposed_output,
        "guardrail": guardrail,
    }


def esc(s: Any) -> str:
    return str(s).replace("|", "\\|")


def main() -> None:
    args = parse_args()

    for p in [
        args.final_closeout_summary,
        args.final_closeout_decision_json,
        args.direct_adapter_summary,
        args.direct_manifest,
        args.combined_summary,
        args.blocker_review_summary,
        args.current_best_checkpoint,
    ]:
        if not p.exists():
            raise FileNotFoundError(p)

    final_summary = by_metric(read_csv(args.final_closeout_summary))
    final_decision_json = json.loads(args.final_closeout_decision_json.read_text(encoding="utf-8"))
    direct = by_metric(read_csv(args.direct_adapter_summary))
    direct_manifest = read_csv(args.direct_manifest)
    combined = read_csv(args.combined_summary)
    blocker_review = by_metric(read_csv(args.blocker_review_summary))
    optional_fixed_summary = maybe_read_csv(args.optional_fixed_input_audit_summary)
    optional_fixed_manifest = maybe_read_csv(args.optional_fixed_input_audit_manifest)

    final_decision = get(final_summary, "final_decision")
    promotion_decision = get(final_summary, "promotion_decision")
    direct_adapter_decision = get(direct, "adapter_decision")
    direct_blocker_count = as_int(get(direct, "blocker_count"))
    direct_warning_count = as_int(get(direct, "warning_count"))
    direct_blocker_notes = notes(direct, "blocker_count")
    direct_warning_notes = notes(direct, "warning_count")

    candidate_exists = args.candidate_checkpoint.exists()
    current_best_exists = args.current_best_checkpoint.exists()

    combined_fail_rows = [r for r in combined if r.get("status") == "FAIL"]
    combined_warn_rows = [r for r in combined if r.get("status") == "WARN"]

    trainable_gap_improved = as_int(combined_metric(combined, "gap_improved_rows"))
    trainable_rank_regressed = as_int(combined_metric(combined, "target_rank_regressed_rows"))
    protected_rank_regressed = as_int(combined_metric(combined, "protected_top10_rank_regressed_rows"))
    protected_prob_regressed = as_int(combined_metric(combined, "protected_top10_prob_regressed_rows"))
    tail_rank_regressed = as_int(combined_metric(combined, "tail_rank_gt50_rank_regressed_rows"))
    tail_prob_regressed = as_int(combined_metric(combined, "tail_rank_gt50_prob_regressed_rows"))
    anchor_top1_changed = as_int(combined_metric(combined, "anchor_top1_changed_rows"))
    anchor_max_kl = as_float(combined_metric(combined, "anchor_max_kl"))

    root_causes: list[str] = []
    warnings: list[str] = []
    blockers: list[str] = []

    if final_decision != "RUN1_CORE_REUSE_FINAL_CLOSEOUT_COMPLETE_WITH_WARNINGS":
        blockers.append(f"run1 final closeout not complete-with-warnings: {final_decision}")
    if promotion_decision != "NO_PROMOTION__KEEP_RUN1_CANDIDATE_ISOLATED":
        blockers.append(f"unexpected promotion decision: {promotion_decision}")
    if not current_best_exists:
        blockers.append("current_best checkpoint path missing")
    if not candidate_exists:
        warnings.append("candidate checkpoint is not present locally; still no checkpoint read is needed for this planning branch")

    if "BLOCKED" in direct_adapter_decision or direct_blocker_count > 0:
        root_causes.append("direct_adapter_blocked")
    if protected_prob_regressed > 0 or tail_prob_regressed > 0:
        root_causes.append("probability_regression_warnings_remain")
    if direct_manifest:
        root_causes.append("direct_manifest_exists_but_route_not_safe")
    else:
        root_causes.append("direct_manifest_empty_or_missing")
    if optional_fixed_summary or optional_fixed_manifest:
        root_causes.append("prior_fixed_probe_heldout_audit_available")
    else:
        root_causes.append("prior_fixed_probe_heldout_audit_not_available_or_not_materialized")

    if combined_fail_rows:
        blockers.append(f"combined summary still has FAIL rows: {len(combined_fail_rows)}")
    if trainable_gap_improved != 44:
        blockers.append(f"trainable_gap_improved not 44: {trainable_gap_improved}")
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

    if combined_warn_rows:
        warnings.append(f"combined WARN rows carried forward: {len(combined_warn_rows)}")
    if protected_prob_regressed:
        warnings.append(f"protected raw probability regressions carried forward: {protected_prob_regressed}")
    if tail_prob_regressed:
        warnings.append(f"tail raw probability regressions carried forward: {tail_prob_regressed}")
    if direct_warning_count:
        warnings.append(f"direct adapter warnings carried forward: {direct_warning_count}; {direct_warning_notes}")
    if direct_blocker_count:
        warnings.append(f"direct adapter blocker notes need repair: {direct_blocker_notes}")

    actions: list[dict[str, str]] = [
        action(
            1,
            "inspect_direct_adapter_blockers",
            "diagnostic",
            "Direct adapter did not become a safe eval route; inspect blocker notes and manifest rows before building an executor.",
            "analysis/integration_eval/teacher_divergence_next_direct_probe_input_repair_blocker_notes.md",
            "No model eval; text/CSV inspection only.",
        ),
        action(
            2,
            "schema_normalize_direct_manifest",
            "input_repair",
            "Existing direct manifest rows should be normalized into a stricter candidate-eval-input schema before any local eval executor.",
            "analysis/integration_eval/teacher_divergence_next_direct_probe_input_repair_normalized_manifest.csv",
            "Do not read checkpoints; validate only paths, row counts, split names, and source provenance.",
        ),
        action(
            3,
            "build_clean_heldout_probe_source_plan",
            "input_repair",
            "Protected/tail probability warnings remain; a future eval path needs cleaner heldout/direct-probe inputs, not promotion reuse.",
            "analysis/integration_eval/teacher_divergence_next_direct_probe_input_repair_heldout_source_plan.csv",
            "No training, no eval, no C export, no promotion.",
        ),
        action(
            4,
            "dedupe_warning_propagation",
            "routing_quality",
            "Current route carried repeated warning strings across dispatch/follow-up layers; deduping will make future decisions easier to audit.",
            "analysis/integration_eval/teacher_divergence_next_direct_probe_input_repair_warning_dedupe_plan.md",
            "Report-only patch plan; do not change gate thresholds in this branch.",
        ),
        action(
            5,
            "keep_run1_candidate_isolated",
            "governance",
            "Run1 has positive gap signal but insufficient eval evidence and probability warnings remain.",
            "No checkpoint promotion; candidate stays local/isolated.",
            "No current_best overwrite; no checkpoint artifacts in git.",
        ),
    ]

    if optional_fixed_summary or optional_fixed_manifest:
        actions.append(
            action(
                6,
                "reuse_prior_fixed_probe_audit_as_candidate_source",
                "input_repair",
                "Prior fixed-probe/heldout input audit files are available and can seed a cleaner source review.",
                "analysis/integration_eval/teacher_divergence_next_direct_probe_input_repair_fixed_probe_source_review.csv",
                "Review-only; no model eval.",
            )
        )
    else:
        actions.append(
            action(
                6,
                "materialize_fixed_probe_audit_inputs",
                "input_repair",
                "No prior fixed-probe/heldout audit manifest was found at the expected paths; future branch should materialize one.",
                "analysis/integration_eval/teacher_divergence_next_direct_probe_input_repair_fixed_probe_materialize_plan.md",
                "Plan-only; no model eval.",
            )
        )

    if blockers:
        plan_decision = "DIRECT_PROBE_INPUT_REPAIR_PLAN_BLOCKED"
        recommended_next = "Fix hard blockers before input repair."
    else:
        plan_decision = "DIRECT_PROBE_INPUT_REPAIR_PLAN_READY"
        recommended_next = (
            "Create a follow-up branch to normalize/repair direct-probe and heldout input manifests. "
            "Keep all work report/input-only until a later explicitly guarded local-eval executor exists."
        )

    summary_rows = [
        row("plan_decision", plan_decision, "INFO", "Plan only; no model eval."),
        row("recommended_next", recommended_next, "INFO"),
        row("final_closeout_decision", final_decision, "INFO"),
        row("promotion_decision", promotion_decision, "INFO"),
        row("direct_adapter_decision", direct_adapter_decision, "INFO"),
        row("direct_adapter_blocker_count", direct_blocker_count, "WARN" if direct_blocker_count else "PASS", direct_blocker_notes),
        row("direct_adapter_warning_count", direct_warning_count, "WARN" if direct_warning_count else "PASS", direct_warning_notes),
        row("root_cause_count", len(root_causes), "INFO", "; ".join(root_causes)),
        row("planned_action_count", len(actions), "INFO"),
        row("blocker_count", len(blockers), "PASS" if not blockers else "FAIL", "; ".join(blockers)),
        row("warning_count", len(warnings), "WARN" if warnings else "PASS", "; ".join(warnings)),
        row("candidate_checkpoint_exists_locally", int(candidate_exists), "INFO", "Existence only; no checkpoint read."),
        row("current_best_exists", int(current_best_exists), "PASS" if current_best_exists else "FAIL"),
        row("direct_manifest_rows", len(direct_manifest), "INFO"),
        row("optional_fixed_audit_summary_rows", len(optional_fixed_summary), "INFO"),
        row("optional_fixed_audit_manifest_rows", len(optional_fixed_manifest), "INFO"),
        row("combined_summary_rows", len(combined), "INFO"),
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

    args.out_summary_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.out_summary_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["metric", "value", "status", "notes"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(summary_rows)

    args.out_actions_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.out_actions_csv.open("w", newline="", encoding="utf-8") as f:
        fieldnames = ["priority", "action_id", "action_type", "rationale", "proposed_output", "guardrail"]
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(actions)

    decision = {
        "plan_decision": plan_decision,
        "recommended_next": recommended_next,
        "final_closeout_decision": final_decision,
        "promotion_decision": promotion_decision,
        "direct_adapter_decision": direct_adapter_decision,
        "root_causes": root_causes,
        "planned_actions": actions,
        "would_train_now": False,
        "would_eval_model_now": False,
        "would_read_checkpoint_contents_now": False,
        "would_write_checkpoint": False,
        "would_c_export": False,
        "would_public_benchmark": False,
        "would_promote": False,
        "candidate_checkpoint_path": str(args.candidate_checkpoint),
        "current_best_checkpoint_path": str(args.current_best_checkpoint),
        "metrics": {
            "direct_manifest_rows": len(direct_manifest),
            "trainable_gap_improved": trainable_gap_improved,
            "trainable_rank_regressed": trainable_rank_regressed,
            "protected_rank_regressed": protected_rank_regressed,
            "protected_prob_regressed": protected_prob_regressed,
            "tail_rank_regressed": tail_rank_regressed,
            "tail_prob_regressed": tail_prob_regressed,
            "anchor_top1_changed": anchor_top1_changed,
            "anchor_max_kl": anchor_max_kl,
        },
        "blockers": blockers,
        "warnings": warnings,
    }
    args.out_decision_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_decision_json.write_text(json.dumps(decision, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    report = [
        "# Teacher-divergence next direct-probe input repair plan",
        "",
        "## Branch",
        "",
        "`exp/15x15-teacher-divergence-next-direct-probe-input-repair-plan`",
        "",
        "## Scope",
        "",
        "- Plans repair of direct-probe / heldout eval inputs after run1 conservative closeout.",
        "- Does not train.",
        "- Does not run model eval.",
        "- Does not read checkpoint contents.",
        "- Does not write checkpoints.",
        "- Does not overwrite `checkpoints/15x15_current_best.pt`.",
        "- Does not C export.",
        "- Does not run public benchmark.",
        "- Does not promote.",
        "",
        "## Plan decision",
        "",
        f"`{plan_decision}`",
        "",
        "## Recommended next",
        "",
        recommended_next,
        "",
        "## Root causes",
        "",
    ]

    for c in root_causes:
        report.append(f"- {c}")

    report.extend([
        "",
        "## Planned actions",
        "",
        "| priority | action_id | type | proposed_output | guardrail |",
        "|---:|---|---|---|---|",
    ])
    for a in actions:
        report.append(
            f"| {a['priority']} | {esc(a['action_id'])} | {esc(a['action_type'])} | {esc(a['proposed_output'])} | {esc(a['guardrail'])} |"
        )

    report.extend([
        "",
        "## Summary",
        "",
        "| metric | value | status | notes |",
        "|---|---:|---|---|",
    ])
    for r in summary_rows:
        report.append(f"| {esc(r['metric'])} | {esc(r['value'])} | {esc(r['status'])} | {esc(r['notes'])} |")

    report.extend([
        "",
        "## Direct manifest preview",
        "",
        "| row | keys |",
        "|---:|---|",
    ])
    for i, r in enumerate(direct_manifest[:20], start=1):
        report.append(f"| {i} | {esc(', '.join(sorted(r.keys())))} |")
    if len(direct_manifest) > 20:
        report.append(f"| ... | {len(direct_manifest) - 20} more rows omitted |")

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
        "## Final guardrails",
        "",
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

    print("plan_decision:", plan_decision)
    print("recommended_next:", recommended_next)
    print("final_closeout_decision:", final_decision)
    print("direct_adapter_decision:", direct_adapter_decision)
    print("root_causes:", ";".join(root_causes))
    print("planned_action_count:", len(actions))
    print("blocker_count:", len(blockers))
    print("warning_count:", len(warnings))
    print("direct_manifest_rows:", len(direct_manifest))
    print("optional_fixed_audit_summary_rows:", len(optional_fixed_summary))
    print("optional_fixed_audit_manifest_rows:", len(optional_fixed_manifest))
    print("trainable_gap_improved:", trainable_gap_improved)
    print("protected_prob_regressed:", protected_prob_regressed)
    print("tail_prob_regressed:", tail_prob_regressed)
    print("out_summary_csv:", args.out_summary_csv)
    print("out_actions_csv:", args.out_actions_csv)
    print("out_decision_json:", args.out_decision_json)
    print("out_report:", args.out_report)
    print("plan only; no model eval; no training; no checkpoint read/write; no C export; no benchmark; no promotion")


if __name__ == "__main__":
    main()
