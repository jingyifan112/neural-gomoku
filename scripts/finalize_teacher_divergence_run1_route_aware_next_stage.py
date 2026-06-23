#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


LOCAL_DIRECT = "READY_TO_BUILD_CONTROLLED_DIRECT_PROBE_EVAL_EXECUTOR_DRYRUN"
LOCAL_CORE = "READY_TO_FINALIZE_CORE_REUSE_LOCAL_DECISION_REPORT"
LOCAL_BLOCKED = "ROUTE_AWARE_LOCAL_DECISION_BLOCKED"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Finalize route-aware next stage after run1 local decision."
    )
    p.add_argument(
        "--route-aware-summary",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_route_aware_local_decision_summary.csv"),
    )
    p.add_argument(
        "--direct-manifest",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_direct_probe_eval_adapter_manifest.csv"),
    )
    p.add_argument(
        "--direct-summary",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_direct_probe_eval_adapter_summary.csv"),
    )
    p.add_argument(
        "--combined-summary",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_local_comparison_executor_dryrun_combined_summary.csv"),
    )
    p.add_argument(
        "--dryrun-decision-json",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_local_comparison_executor_dryrun_decision.json"),
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
        default=Path("analysis/integration_eval/teacher_divergence_run1_route_aware_next_stage_summary.csv"),
    )
    p.add_argument(
        "--out-spec-json",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_route_aware_next_stage_spec.json"),
    )
    p.add_argument(
        "--out-next-plan",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_route_aware_next_stage_next_plan.txt"),
    )
    p.add_argument(
        "--out-report",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_route_aware_next_stage.md"),
    )
    return p.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def by_metric(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {r["metric"]: r for r in rows}


def get_value(m: dict[str, dict[str, str]], key: str, default: str = "") -> str:
    return m.get(key, {}).get("value", default)


def as_int(value: Any) -> int:
    if value in ("", None):
        return 0
    return int(float(value))


def as_float(value: Any) -> float:
    if value in ("", None):
        return 0.0
    return float(value)


def row(metric: str, value: Any, status: str, notes: str = "") -> dict[str, str]:
    return {
        "metric": metric,
        "value": str(value),
        "status": status,
        "notes": notes,
    }


def metric_from_combined(combined: list[dict[str, str]], name: str, default: str = "") -> str:
    for r in combined:
        if r.get("metric") == name:
            return r.get("value", default)
    return default


def main() -> None:
    args = parse_args()

    for p in [
        args.route_aware_summary,
        args.direct_manifest,
        args.direct_summary,
        args.combined_summary,
        args.dryrun_decision_json,
        args.current_best_checkpoint,
    ]:
        if not p.exists():
            raise FileNotFoundError(p)

    route = by_metric(read_csv(args.route_aware_summary))
    direct = by_metric(read_csv(args.direct_summary))
    manifest = read_csv(args.direct_manifest)
    combined = read_csv(args.combined_summary)
    dryrun_decision = json.loads(args.dryrun_decision_json.read_text(encoding="utf-8"))

    local_decision = get_value(route, "local_decision")
    recommended_branch_from_route = get_value(route, "recommended_branch")
    route_blockers = as_int(get_value(route, "blocker_count"))
    route_warnings = as_int(get_value(route, "warning_count"))
    direct_ready_inputs = as_int(get_value(route, "direct_ready_inputs"))
    direct_manifest_rows = as_int(get_value(route, "direct_manifest_rows"))
    core_reuse_inputs = as_int(get_value(route, "core_reuse_inputs"))

    adapter_decision = get_value(direct, "adapter_decision")
    adapter_blockers = as_int(get_value(direct, "blocker_count"))
    adapter_warnings = as_int(get_value(direct, "warning_count"))

    candidate_exists = args.candidate_checkpoint.exists()
    current_best_exists = args.current_best_checkpoint.exists()

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

    dryrun_flags = {
        "would_train": bool(dryrun_decision.get("would_train")),
        "would_eval_model": bool(dryrun_decision.get("would_eval_model")),
        "would_write_checkpoint": bool(dryrun_decision.get("would_write_checkpoint")),
        "would_c_export": bool(dryrun_decision.get("would_c_export")),
        "would_public_benchmark": bool(dryrun_decision.get("would_public_benchmark")),
        "would_promote": bool(dryrun_decision.get("would_promote")),
    }

    blockers: list[str] = []
    warnings: list[str] = []

    if route_blockers > 0:
        blockers.append(f"route-aware local decision blockers present: {route_blockers}")
    if adapter_blockers > 0:
        blockers.append(f"direct adapter blockers present: {adapter_blockers}")
    if core_reuse_inputs != 3:
        blockers.append(f"core reuse inputs not 3: {core_reuse_inputs}")
    if not current_best_exists:
        blockers.append("current_best checkpoint path missing")
    if not candidate_exists:
        blockers.append("run1 candidate checkpoint path missing locally")
    if direct_manifest_rows != len(manifest):
        blockers.append(f"direct manifest row mismatch: summary={direct_manifest_rows}, csv={len(manifest)}")
    if combined_fail_rows:
        blockers.append(f"combined local comparison has FAIL rows: {len(combined_fail_rows)}")
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

    for flag, value in dryrun_flags.items():
        if value:
            blockers.append(f"upstream dry-run safety flag unexpectedly true: {flag}")

    if route_warnings > 0:
        warnings.append(f"route-aware warnings carried forward: {route_warnings}")
    if adapter_warnings > 0:
        warnings.append(f"adapter warnings carried forward: {adapter_warnings}")
    if combined_warn_rows:
        warnings.append(f"combined local comparison WARN rows carried forward: {len(combined_warn_rows)}")
    if protected_prob_regressed > 0:
        warnings.append(f"protected raw probability regressions carried forward: {protected_prob_regressed}")
    if tail_prob_regressed > 0:
        warnings.append(f"tail raw probability regressions carried forward: {tail_prob_regressed}")

    if local_decision == LOCAL_DIRECT:
        if direct_ready_inputs <= 0 or len(manifest) <= 0:
            blockers.append("direct path selected but direct manifest is empty")
        next_stage_decision = "DIRECT_PROBE_EVAL_EXECUTOR_DRYRUN_SPEC_READY"
        recommended_branch = "exp/15x15-teacher-divergence-run1-direct-probe-eval-executor-dryrun"
        recommended_action = "Build controlled direct-probe local eval executor in dry-run mode. Require explicit confirmation before any model eval."
        future_requires = [
            "--execute-model-eval",
            "--confirm-model-eval TEACHER_DIVERGENCE_DIRECT_PROBE_LOCAL_EVAL",
        ]
    elif local_decision == LOCAL_CORE:
        next_stage_decision = "CORE_REUSE_LOCAL_DECISION_REPORT_READY_WITH_WARNINGS"
        recommended_branch = "exp/15x15-teacher-divergence-run1-core-reuse-local-decision"
        recommended_action = "Finalize core-reuse local decision from already-computed guard outputs. Do not run model eval."
        future_requires = []
    elif local_decision == LOCAL_BLOCKED:
        blockers.append("route-aware local decision is blocked")
        next_stage_decision = "NEXT_STAGE_BLOCKED"
        recommended_branch = "none"
        recommended_action = "Fix blockers before continuing."
        future_requires = []
    else:
        blockers.append(f"unknown local_decision: {local_decision}")
        next_stage_decision = "NEXT_STAGE_BLOCKED"
        recommended_branch = "none"
        recommended_action = "Inspect route-aware local decision summary before continuing."
        future_requires = []

    if blockers:
        next_stage_decision = "NEXT_STAGE_BLOCKED"
        recommended_branch = "none"
        recommended_action = "Fix blockers before continuing."

    summary_rows = [
        row("next_stage_decision", next_stage_decision, "INFO", "No model eval in this branch."),
        row("recommended_branch", recommended_branch, "INFO"),
        row("recommended_action", recommended_action, "INFO"),
        row("local_decision", local_decision, "INFO"),
        row("recommended_branch_from_route", recommended_branch_from_route, "INFO"),
        row("blocker_count", len(blockers), "PASS" if not blockers else "FAIL", "; ".join(blockers)),
        row("warning_count", len(warnings), "WARN" if warnings else "PASS", "; ".join(warnings)),
        row("adapter_decision", adapter_decision, "INFO"),
        row("route_blocker_count", route_blockers, "PASS" if route_blockers == 0 else "FAIL"),
        row("route_warning_count", route_warnings, "WARN" if route_warnings else "PASS"),
        row("adapter_blocker_count", adapter_blockers, "PASS" if adapter_blockers == 0 else "FAIL"),
        row("adapter_warning_count", adapter_warnings, "WARN" if adapter_warnings else "PASS"),
        row("candidate_checkpoint_exists_locally", int(candidate_exists), "PASS" if candidate_exists else "FAIL", "Existence only; do not add to git."),
        row("current_best_exists", int(current_best_exists), "PASS" if current_best_exists else "FAIL"),
        row("core_reuse_inputs", core_reuse_inputs, "PASS" if core_reuse_inputs == 3 else "FAIL"),
        row("direct_ready_inputs", direct_ready_inputs, "INFO"),
        row("direct_manifest_rows", len(manifest), "INFO"),
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

    spec = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "next_stage_decision": next_stage_decision,
        "recommended_branch": recommended_branch,
        "recommended_action": recommended_action,
        "local_decision": local_decision,
        "future_requires": future_requires,
        "would_train_now": False,
        "would_eval_model_now": False,
        "would_read_checkpoint_contents_now": False,
        "would_write_checkpoint": False,
        "would_c_export": False,
        "would_public_benchmark": False,
        "would_promote": False,
        "candidate_checkpoint_path": str(args.candidate_checkpoint),
        "current_best_checkpoint_path": str(args.current_best_checkpoint),
        "direct_manifest_rows": len(manifest),
        "direct_manifest": manifest,
        "core_reuse_metrics": {
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
    args.out_spec_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_spec_json.write_text(json.dumps(spec, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    next_plan = [
        "# Teacher-divergence run1 route-aware next-stage plan",
        "",
        f"next_stage_decision={next_stage_decision}",
        f"recommended_branch={recommended_branch}",
        "",
        "## Recommended action",
        "",
        recommended_action,
        "",
        "## Safety status",
        "",
        "- would_train_now: 0",
        "- would_eval_model_now: 0",
        "- would_read_checkpoint_contents_now: 0",
        "- would_write_checkpoint: 0",
        "- would_c_export: 0",
        "- would_public_benchmark: 0",
        "- would_promote: 0",
        "",
    ]

    if future_requires:
        next_plan.extend([
            "## Future explicit model-eval guard",
            "",
            "A later executor must require both:",
            "",
            "```text",
            *future_requires,
            "```",
            "",
        ])

    next_plan.extend([
        "## Blockers",
        "",
    ])
    if blockers:
        next_plan.extend([f"- {b}" for b in blockers])
    else:
        next_plan.append("- None.")

    next_plan.extend([
        "",
        "## Warnings",
        "",
    ])
    if warnings:
        next_plan.extend([f"- {w}" for w in warnings])
    else:
        next_plan.append("- None.")

    next_plan.extend([
        "",
        "## Still forbidden",
        "",
        "- training",
        "- checkpoint write",
        "- current_best overwrite",
        "- C export",
        "- public benchmark",
        "- promotion",
        "- adding local checkpoint artifacts to git",
        "",
    ])

    args.out_next_plan.parent.mkdir(parents=True, exist_ok=True)
    args.out_next_plan.write_text("\n".join(next_plan), encoding="utf-8")

    report = [
        "# Teacher-divergence run1 route-aware next-stage dry-run/report",
        "",
        "## Branch",
        "",
        "`exp/15x15-teacher-divergence-run1-route-aware-next-stage`",
        "",
        "## Scope",
        "",
        "- Reads route-aware local decision and prior local comparison outputs.",
        "- Produces the next-stage plan/spec.",
        "- Does not train.",
        "- Does not run model eval.",
        "- Does not read checkpoint contents.",
        "- Does not write checkpoints.",
        "- Does not overwrite `checkpoints/15x15_current_best.pt`.",
        "- Does not C export.",
        "- Does not run public benchmark.",
        "- Does not promote.",
        "",
        "## Next-stage decision",
        "",
        f"`{next_stage_decision}`",
        "",
        "## Recommended next branch",
        "",
        f"`{recommended_branch}`",
        "",
        "## Recommended action",
        "",
        recommended_action,
        "",
        "## Summary",
        "",
        "| metric | value | status | notes |",
        "|---|---:|---|---|",
    ]

    for r in summary_rows:
        notes = r["notes"].replace("|", "\\|")
        report.append(f"| {r['metric']} | {r['value']} | {r['status']} | {notes} |")

    report.extend([
        "",
        "## Direct manifest rows",
        "",
        "| eval_manifest_id | adapter_kind | path | rows/count |",
        "|---|---|---|---:|",
    ])
    if manifest:
        for r in manifest:
            report.append(
                f"| {r.get('eval_manifest_id', '')} | {r.get('adapter_kind', '')} | `{r.get('path', '')}` | {r.get('sample_rows_or_count', '')} |"
            )
    else:
        report.append("| none |  |  |  |")

    report.extend([
        "",
        "## Core reused comparison summary",
        "",
        "| section | metric | value | status |",
        "|---|---|---:|---|",
    ])
    for r in combined:
        report.append(
            f"| {r.get('section', '')} | {r.get('metric', '')} | {r.get('value', '')} | {r.get('status', '')} |"
        )

    report.extend([
        "",
        "## Blockers",
        "",
    ])
    if blockers:
        for b in blockers:
            report.append(f"- {b}")
    else:
        report.append("- None.")

    report.extend([
        "",
        "## Warnings",
        "",
    ])
    if warnings:
        for w in warnings:
            report.append(f"- {w}")
    else:
        report.append("- None.")

    if future_requires:
        report.extend([
            "",
            "## Future explicit model-eval guard",
            "",
            "A later executor must require both:",
            "",
            "```text",
            *future_requires,
            "```",
        ])

    report.extend([
        "",
        "## Outputs",
        "",
        f"- summary CSV: `{args.out_summary_csv}`",
        f"- spec JSON: `{args.out_spec_json}`",
        f"- next plan: `{args.out_next_plan}`",
        f"- report: `{args.out_report}`",
        "",
        "## Final guardrails",
        "",
        "- No current_best overwrite.",
        "- No C export.",
        "- No public benchmark.",
        "- No promotion.",
        "- Do not add local checkpoint artifacts to git.",
        "",
    ])

    args.out_report.parent.mkdir(parents=True, exist_ok=True)
    args.out_report.write_text("\n".join(report), encoding="utf-8")

    print("next_stage_decision:", next_stage_decision)
    print("recommended_branch:", recommended_branch)
    print("local_decision:", local_decision)
    print("blocker_count:", len(blockers))
    print("warning_count:", len(warnings))
    print("direct_manifest_rows:", len(manifest))
    print("trainable_gap_improved:", trainable_gap_improved)
    print("protected_rank_regressed:", protected_rank_regressed)
    print("tail_rank_regressed:", tail_rank_regressed)
    print("anchor_top1_changed:", anchor_top1_changed)
    print("out_summary_csv:", args.out_summary_csv)
    print("out_spec_json:", args.out_spec_json)
    print("out_next_plan:", args.out_next_plan)
    print("out_report:", args.out_report)
    print("next-stage dry-run/report only; no model eval; no training; no checkpoint read/write; no C export; no benchmark; no promotion")


if __name__ == "__main__":
    main()
