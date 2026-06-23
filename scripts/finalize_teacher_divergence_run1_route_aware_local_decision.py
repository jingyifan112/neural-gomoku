#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


ROUTE_DIRECT = "ROUTE_TO_CONTROLLED_DIRECT_PROBE_EVAL_EXECUTOR_DRYRUN"
ROUTE_CORE = "ROUTE_TO_CORE_REUSE_LOCAL_DECISION_REPORT"
ROUTE_BLOCKED = "POST_ADAPTER_ROUTE_BLOCKED"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Route-aware local decision after run1 post-adapter route decision."
    )
    p.add_argument(
        "--route-summary",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_post_adapter_route_decision_summary.csv"),
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
        default=Path("analysis/integration_eval/teacher_divergence_run1_route_aware_local_decision_summary.csv"),
    )
    p.add_argument(
        "--out-next-plan",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_route_aware_local_decision_next_plan.txt"),
    )
    p.add_argument(
        "--out-report",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_route_aware_local_decision.md"),
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
        args.route_summary,
        args.direct_manifest,
        args.direct_summary,
        args.combined_summary,
        args.dryrun_decision_json,
        args.current_best_checkpoint,
    ]:
        if not p.exists():
            raise FileNotFoundError(p)

    route = by_metric(read_csv(args.route_summary))
    direct = by_metric(read_csv(args.direct_summary))
    manifest = read_csv(args.direct_manifest)
    combined = read_csv(args.combined_summary)
    dryrun_decision = json.loads(args.dryrun_decision_json.read_text(encoding="utf-8"))

    final_route_decision = get_value(route, "final_route_decision")
    route_decision = get_value(route, "route_decision")
    route_blockers = as_int(get_value(route, "blocker_count"))
    route_warnings = as_int(get_value(route, "warning_count"))
    adapter_decision = get_value(route, "adapter_decision")
    direct_ready_inputs = as_int(get_value(route, "direct_ready_inputs_from_selection"))
    core_reuse_inputs = as_int(get_value(route, "core_reuse_inputs"))

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

    blockers: list[str] = []
    warnings: list[str] = []

    if route_blockers > 0:
        blockers.append(f"route blockers present: {route_blockers}")
    if adapter_blockers > 0:
        blockers.append(f"adapter blockers present: {adapter_blockers}")
    if core_reuse_inputs != 3:
        blockers.append(f"core reuse inputs not 3: {core_reuse_inputs}")
    if not current_best_exists:
        blockers.append("current_best checkpoint path missing")
    if not candidate_exists:
        blockers.append("run1 candidate checkpoint path missing locally")
    if combined_fail_rows:
        blockers.append(f"combined dry-run FAIL rows present: {len(combined_fail_rows)}")
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

    if route_warnings > 0:
        warnings.append(f"route warnings carried forward: {route_warnings}")
    if adapter_warnings > 0:
        warnings.append(f"adapter warnings carried forward: {adapter_warnings}")
    if combined_warn_rows:
        warnings.append(f"combined dry-run WARN rows carried forward: {len(combined_warn_rows)}")
    if protected_prob_regressed > 0:
        warnings.append(f"protected raw probability regressions carried forward: {protected_prob_regressed}")
    if tail_prob_regressed > 0:
        warnings.append(f"tail raw probability regressions carried forward: {tail_prob_regressed}")

    if final_route_decision == ROUTE_DIRECT:
        if direct_ready_inputs <= 0 or len(manifest) <= 0:
            blockers.append("direct route selected but direct manifest is empty")
        local_decision = "READY_TO_BUILD_CONTROLLED_DIRECT_PROBE_EVAL_EXECUTOR_DRYRUN"
        recommended_branch = "exp/15x15-teacher-divergence-run1-direct-probe-eval-executor-dryrun"
        recommended_action = "Build a controlled direct-probe local eval executor in dry-run mode. Require explicit confirmation before any model eval."
    elif final_route_decision == ROUTE_CORE:
        local_decision = "READY_TO_FINALIZE_CORE_REUSE_LOCAL_DECISION_REPORT"
        recommended_branch = "exp/15x15-teacher-divergence-run1-core-reuse-local-decision"
        recommended_action = "Finalize a core-reuse local decision report from already-computed guard outputs. Do not run model eval."
    elif final_route_decision == ROUTE_BLOCKED:
        blockers.append("post-adapter route is blocked")
        local_decision = "ROUTE_AWARE_LOCAL_DECISION_BLOCKED"
        recommended_branch = "none"
        recommended_action = "Fix blockers before continuing."
    else:
        blockers.append(f"unknown final_route_decision: {final_route_decision}")
        local_decision = "ROUTE_AWARE_LOCAL_DECISION_BLOCKED"
        recommended_branch = "none"
        recommended_action = "Inspect route summary before continuing."

    if blockers:
        local_decision = "ROUTE_AWARE_LOCAL_DECISION_BLOCKED"

    summary_rows = [
        row("local_decision", local_decision, "INFO", "Route-aware local decision only; no model eval."),
        row("recommended_branch", recommended_branch, "INFO"),
        row("recommended_action", recommended_action, "INFO"),
        row("blocker_count", len(blockers), "PASS" if not blockers else "FAIL", "; ".join(blockers)),
        row("warning_count", len(warnings), "WARN" if warnings else "PASS", "; ".join(warnings)),
        row("final_route_decision", final_route_decision, "INFO"),
        row("route_decision", route_decision, "INFO"),
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

    plan_lines = [
        "# Teacher-divergence run1 route-aware local decision next plan",
        "",
        f"local_decision={local_decision}",
        f"recommended_branch={recommended_branch}",
        "",
        "## Recommended action",
        "",
        recommended_action,
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
        "## Blockers",
        "",
    ]

    if blockers:
        plan_lines.extend([f"- {b}" for b in blockers])
    else:
        plan_lines.append("- None.")

    plan_lines.extend([
        "",
        "## Warnings",
        "",
    ])

    if warnings:
        plan_lines.extend([f"- {w}" for w in warnings])
    else:
        plan_lines.append("- None.")

    if final_route_decision == ROUTE_DIRECT:
        plan_lines.extend([
            "",
            "## Future direct-probe executor confirmation guard",
            "",
            "Any future executor must require both flags before model eval:",
            "",
            "```text",
            "--execute-model-eval",
            "--confirm-model-eval TEACHER_DIVERGENCE_DIRECT_PROBE_LOCAL_EVAL",
            "```",
            "",
        ])

    args.out_next_plan.parent.mkdir(parents=True, exist_ok=True)
    args.out_next_plan.write_text("\n".join(plan_lines), encoding="utf-8")

    report = [
        "# Teacher-divergence run1 route-aware local decision",
        "",
        "## Branch",
        "",
        "`exp/15x15-teacher-divergence-run1-route-aware-local-decision`",
        "",
        "## Scope",
        "",
        "- Reads post-adapter route decision.",
        "- Produces the next safe local path.",
        "- Does not train.",
        "- Does not run model eval.",
        "- Does not read checkpoint contents.",
        "- Does not write checkpoints.",
        "- Does not overwrite `checkpoints/15x15_current_best.pt`.",
        "- Does not C export.",
        "- Does not run public benchmark.",
        "- Does not promote.",
        "",
        "## Local decision",
        "",
        f"`{local_decision}`",
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
        "## Reused core comparison summary",
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

    report.extend([
        "",
        "## Outputs",
        "",
        f"- summary CSV: `{args.out_summary_csv}`",
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

    print("local_decision:", local_decision)
    print("recommended_branch:", recommended_branch)
    print("final_route_decision:", final_route_decision)
    print("adapter_decision:", adapter_decision)
    print("blocker_count:", len(blockers))
    print("warning_count:", len(warnings))
    print("core_reuse_inputs:", core_reuse_inputs)
    print("direct_ready_inputs:", direct_ready_inputs)
    print("direct_manifest_rows:", len(manifest))
    print("trainable_gap_improved:", trainable_gap_improved)
    print("protected_rank_regressed:", protected_rank_regressed)
    print("tail_rank_regressed:", tail_rank_regressed)
    print("anchor_top1_changed:", anchor_top1_changed)
    print("out_summary_csv:", args.out_summary_csv)
    print("out_next_plan:", args.out_next_plan)
    print("out_report:", args.out_report)
    print("route-aware local decision only; no model eval; no training; no checkpoint read/write; no C export; no benchmark; no promotion")


if __name__ == "__main__":
    main()
