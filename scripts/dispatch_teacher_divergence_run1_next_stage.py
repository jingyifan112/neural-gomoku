#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DIRECT_READY = "DIRECT_PROBE_EVAL_EXECUTOR_DRYRUN_SPEC_READY"
CORE_READY = "CORE_REUSE_LOCAL_DECISION_REPORT_READY_WITH_WARNINGS"
BLOCKED = "NEXT_STAGE_BLOCKED"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Dispatch run1 next stage based on route-aware next-stage decision."
    )
    p.add_argument(
        "--next-stage-summary",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_route_aware_next_stage_summary.csv"),
    )
    p.add_argument(
        "--next-stage-spec",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_route_aware_next_stage_spec.json"),
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
        default=Path("analysis/integration_eval/teacher_divergence_run1_next_stage_dispatch_summary.csv"),
    )
    p.add_argument(
        "--out-decision-json",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_next_stage_dispatch_decision.json"),
    )
    p.add_argument(
        "--out-commands",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_next_stage_dispatch_commands.txt"),
    )
    p.add_argument(
        "--out-report",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_next_stage_dispatch.md"),
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
        args.next_stage_summary,
        args.next_stage_spec,
        args.direct_manifest,
        args.combined_summary,
        args.dryrun_decision_json,
        args.current_best_checkpoint,
    ]:
        if not p.exists():
            raise FileNotFoundError(p)

    next_summary = by_metric(read_csv(args.next_stage_summary))
    spec = json.loads(args.next_stage_spec.read_text(encoding="utf-8"))
    manifest = read_csv(args.direct_manifest)
    combined = read_csv(args.combined_summary)
    upstream_dryrun = json.loads(args.dryrun_decision_json.read_text(encoding="utf-8"))

    next_stage_decision = get_value(next_summary, "next_stage_decision")
    recommended_branch = get_value(next_summary, "recommended_branch")
    local_decision = get_value(next_summary, "local_decision")
    upstream_blockers = as_int(get_value(next_summary, "blocker_count"))
    upstream_warnings = as_int(get_value(next_summary, "warning_count"))

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

    if upstream_blockers > 0:
        blockers.append(f"upstream next-stage blockers present: {upstream_blockers}")
    if not current_best_exists:
        blockers.append("current_best checkpoint path missing")
    if not candidate_exists:
        blockers.append("run1 candidate checkpoint path missing locally")
    if combined_fail_rows:
        blockers.append(f"combined local comparison FAIL rows present: {len(combined_fail_rows)}")
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

    safety_flags = {
        "would_train_now": False,
        "would_eval_model_now": False,
        "would_read_checkpoint_contents_now": False,
        "would_write_checkpoint": False,
        "would_c_export": False,
        "would_public_benchmark": False,
        "would_promote": False,
    }

    for key in [
        "would_train",
        "would_eval_model",
        "would_write_checkpoint",
        "would_c_export",
        "would_public_benchmark",
        "would_promote",
    ]:
        if bool(upstream_dryrun.get(key)):
            blockers.append(f"upstream dry-run safety flag unexpectedly true: {key}")

    if upstream_warnings > 0:
        warnings.append(f"upstream next-stage warnings carried forward: {upstream_warnings}")
    if combined_warn_rows:
        warnings.append(f"combined local comparison WARN rows carried forward: {len(combined_warn_rows)}")
    if protected_prob_regressed > 0:
        warnings.append(f"protected raw probability regressions carried forward: {protected_prob_regressed}")
    if tail_prob_regressed > 0:
        warnings.append(f"tail raw probability regressions carried forward: {tail_prob_regressed}")

    future_requires = []

    if next_stage_decision == DIRECT_READY:
        if not manifest:
            blockers.append("direct-probe path selected but manifest is empty")
        dispatch_decision = "DIRECT_PROBE_EVAL_EXECUTOR_DRYRUN_PLANNED"
        dispatch_type = "direct_probe_executor_dryrun"
        next_action = "Proceed to a separate branch that implements controlled local model-eval execution, still default dry-run."
        future_requires = [
            "--execute-model-eval",
            "--confirm-model-eval TEACHER_DIVERGENCE_DIRECT_PROBE_LOCAL_EVAL",
        ]
    elif next_stage_decision == CORE_READY:
        dispatch_decision = "CORE_REUSE_LOCAL_DECISION_REPORT_FINALIZED_WITH_WARNINGS"
        dispatch_type = "core_reuse_local_decision"
        next_action = "Use already-computed run1 guard outputs as the local decision. Keep candidate isolated; no promotion."
    elif next_stage_decision == BLOCKED:
        blockers.append("upstream next-stage decision is blocked")
        dispatch_decision = "NEXT_STAGE_DISPATCH_BLOCKED"
        dispatch_type = "blocked"
        next_action = "Fix blockers before continuing."
    else:
        blockers.append(f"unknown next_stage_decision: {next_stage_decision}")
        dispatch_decision = "NEXT_STAGE_DISPATCH_BLOCKED"
        dispatch_type = "unknown"
        next_action = "Inspect next-stage summary before continuing."

    if blockers:
        dispatch_decision = "NEXT_STAGE_DISPATCH_BLOCKED"
        dispatch_type = "blocked"
        next_action = "Fix blockers before continuing."

    promotion_decision = "NO_PROMOTION__KEEP_RUN1_CANDIDATE_ISOLATED"
    if dispatch_decision == "CORE_REUSE_LOCAL_DECISION_REPORT_FINALIZED_WITH_WARNINGS":
        promotion_decision = "NO_PROMOTION__CORE_REUSE_ONLY_WITH_WARNINGS"
    elif dispatch_decision == "DIRECT_PROBE_EVAL_EXECUTOR_DRYRUN_PLANNED":
        promotion_decision = "NO_PROMOTION__DIRECT_PROBE_EXECUTOR_STILL_DRYRUN_ONLY"
    elif dispatch_decision == "NEXT_STAGE_DISPATCH_BLOCKED":
        promotion_decision = "NO_PROMOTION__BLOCKED"

    summary_rows = [
        row("dispatch_decision", dispatch_decision, "INFO", "No model eval in this branch."),
        row("dispatch_type", dispatch_type, "INFO"),
        row("promotion_decision", promotion_decision, "INFO"),
        row("next_action", next_action, "INFO"),
        row("next_stage_decision", next_stage_decision, "INFO"),
        row("recommended_branch", recommended_branch, "INFO"),
        row("local_decision", local_decision, "INFO"),
        row("blocker_count", len(blockers), "PASS" if not blockers else "FAIL", "; ".join(blockers)),
        row("warning_count", len(warnings), "WARN" if warnings else "PASS", "; ".join(warnings)),
        row("candidate_checkpoint_exists_locally", int(candidate_exists), "PASS" if candidate_exists else "FAIL", "Existence only; do not add to git."),
        row("current_best_exists", int(current_best_exists), "PASS" if current_best_exists else "FAIL"),
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

    decision = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "dispatch_decision": dispatch_decision,
        "dispatch_type": dispatch_type,
        "promotion_decision": promotion_decision,
        "next_stage_decision": next_stage_decision,
        "recommended_branch": recommended_branch,
        "local_decision": local_decision,
        "next_action": next_action,
        "future_requires": future_requires,
        **safety_flags,
        "candidate_checkpoint_path": str(args.candidate_checkpoint),
        "current_best_checkpoint_path": str(args.current_best_checkpoint),
        "direct_manifest_rows": len(manifest),
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
        "direct_manifest": manifest,
        "blockers": blockers,
        "warnings": warnings,
    }

    args.out_decision_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_decision_json.write_text(json.dumps(decision, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    commands = [
        "# Teacher-divergence run1 next-stage dispatch commands",
        "",
        f"dispatch_decision={dispatch_decision}",
        f"dispatch_type={dispatch_type}",
        f"promotion_decision={promotion_decision}",
        "",
        "## Next action",
        next_action,
        "",
        "## Safety status",
        "- would_train: 0",
        "- would_eval_model_now: 0",
        "- would_read_checkpoint_contents_now: 0",
        "- would_write_checkpoint: 0",
        "- would_c_export: 0",
        "- would_public_benchmark: 0",
        "- would_promote: 0",
        "",
    ]

    if future_requires:
        commands.extend([
            "## Future model-eval executor must require both flags",
            "```text",
            *future_requires,
            "```",
            "",
        ])

    commands.extend([
        "## Still forbidden",
        "- current_best overwrite",
        "- C export",
        "- public benchmark",
        "- promotion",
        "- adding local checkpoint artifacts to git",
        "",
    ])

    args.out_commands.write_text("\n".join(commands), encoding="utf-8")

    report = [
        "# Teacher-divergence run1 next-stage dispatch",
        "",
        "## Branch",
        "",
        "`" + recommended_branch + "`",
        "",
        "## Scope",
        "",
        "- Dispatches the route-aware next stage.",
        "- Does not train.",
        "- Does not run model eval.",
        "- Does not read checkpoint contents.",
        "- Does not write checkpoints.",
        "- Does not overwrite `checkpoints/15x15_current_best.pt`.",
        "- Does not C export.",
        "- Does not run public benchmark.",
        "- Does not promote.",
        "",
        "## Dispatch decision",
        "",
        f"`{dispatch_decision}`",
        "",
        "## Promotion decision",
        "",
        f"`{promotion_decision}`",
        "",
        "## Next action",
        "",
        next_action,
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
        f"- decision JSON: `{args.out_decision_json}`",
        f"- command plan: `{args.out_commands}`",
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

    print("dispatch_decision:", dispatch_decision)
    print("dispatch_type:", dispatch_type)
    print("promotion_decision:", promotion_decision)
    print("next_stage_decision:", next_stage_decision)
    print("recommended_branch:", recommended_branch)
    print("blocker_count:", len(blockers))
    print("warning_count:", len(warnings))
    print("direct_manifest_rows:", len(manifest))
    print("trainable_gap_improved:", trainable_gap_improved)
    print("protected_rank_regressed:", protected_rank_regressed)
    print("tail_rank_regressed:", tail_rank_regressed)
    print("anchor_top1_changed:", anchor_top1_changed)
    print("out_summary_csv:", args.out_summary_csv)
    print("out_decision_json:", args.out_decision_json)
    print("out_commands:", args.out_commands)
    print("out_report:", args.out_report)
    print("dispatch only; no model eval; no training; no checkpoint read/write; no C export; no benchmark; no promotion")


if __name__ == "__main__":
    main()
