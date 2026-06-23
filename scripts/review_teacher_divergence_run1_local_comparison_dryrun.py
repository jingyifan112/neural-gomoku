#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


EXPECTED_READY = "LOCAL_COMPARISON_DRYRUN_READY"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Controlled review of run1 local comparison executor dry-run outputs."
    )
    p.add_argument(
        "--dryrun-decision-json",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_local_comparison_executor_dryrun_decision.json"),
    )
    p.add_argument(
        "--dryrun-decision-csv",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_local_comparison_executor_dryrun_decision.csv"),
    )
    p.add_argument(
        "--dryrun-combined-csv",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_local_comparison_executor_dryrun_combined_summary.csv"),
    )
    p.add_argument(
        "--adapter-selection",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_local_comparison_adapter_selection.csv"),
    )
    p.add_argument(
        "--adapter-design-summary",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_local_comparison_adapter_design_summary.csv"),
    )
    p.add_argument(
        "--out-summary-csv",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_local_comparison_controlled_review_summary.csv"),
    )
    p.add_argument(
        "--out-next-plan",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_local_comparison_controlled_review_next_plan.txt"),
    )
    p.add_argument(
        "--out-report",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_local_comparison_controlled_review.md"),
    )
    return p.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def by_metric(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {r["metric"]: r for r in rows}


def get_metric(rows_by_metric: dict[str, dict[str, str]], key: str, default: str = "") -> str:
    return rows_by_metric.get(key, {}).get("value", default)


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


def main() -> None:
    args = parse_args()

    for p in [
        args.dryrun_decision_json,
        args.dryrun_decision_csv,
        args.dryrun_combined_csv,
        args.adapter_selection,
        args.adapter_design_summary,
    ]:
        if not p.exists():
            raise FileNotFoundError(p)

    decision = json.loads(args.dryrun_decision_json.read_text(encoding="utf-8"))
    decision_csv = by_metric(read_csv(args.dryrun_decision_csv))
    combined = read_csv(args.dryrun_combined_csv)
    selection = read_csv(args.adapter_selection)
    adapter_design = by_metric(read_csv(args.adapter_design_summary))

    executor_decision = str(decision.get("executor_decision", ""))
    blockers = list(decision.get("blockers", []))
    warnings = list(decision.get("warnings", []))
    metrics = dict(decision.get("metrics", {}))

    selected = [r for r in selection if r.get("selected_for_initial_executor") == "1"]
    direct_selected = [
        r for r in selected
        if r.get("adapter_kind", "").startswith("direct_model_eval_")
    ]
    core_selected = [
        r for r in selected
        if r.get("adapter_kind", "").startswith("core_")
    ]

    combined_fail = [r for r in combined if r.get("status") == "FAIL"]
    combined_warn = [r for r in combined if r.get("status") == "WARN"]

    would_flags = {
        "would_train": bool(decision.get("would_train")),
        "would_eval_model": bool(decision.get("would_eval_model")),
        "would_write_checkpoint": bool(decision.get("would_write_checkpoint")),
        "would_c_export": bool(decision.get("would_c_export")),
        "would_public_benchmark": bool(decision.get("would_public_benchmark")),
        "would_promote": bool(decision.get("would_promote")),
    }

    trainable_gap_improved = as_int(metrics.get("trainable_gap_improved"))
    trainable_rank_regressed = as_int(metrics.get("trainable_rank_regressed"))
    protected_rank_regressed = as_int(metrics.get("protected_rank_regressed"))
    tail_rank_regressed = as_int(metrics.get("tail_rank_regressed"))
    anchor_top1_changed = as_int(metrics.get("anchor_top1_changed"))
    anchor_max_kl = as_float(metrics.get("anchor_max_kl"))
    protected_prob_regressed = as_int(metrics.get("protected_prob_regressed"))
    tail_prob_regressed = as_int(metrics.get("tail_prob_regressed"))

    review_blockers: list[str] = []
    review_warnings: list[str] = []

    if executor_decision != EXPECTED_READY:
        review_blockers.append(f"executor dry-run decision is not ready: {executor_decision}")
    if blockers:
        review_blockers.append(f"dry-run blockers present: {len(blockers)}")
    if combined_fail:
        review_blockers.append(f"combined dry-run FAIL rows present: {len(combined_fail)}")
    if len(core_selected) != 3:
        review_blockers.append(f"core selected inputs count is not 3: {len(core_selected)}")
    if trainable_gap_improved != 44:
        review_blockers.append(f"trainable gap improved rows not 44: {trainable_gap_improved}")
    if trainable_rank_regressed > 0:
        review_blockers.append(f"trainable rank regressions present: {trainable_rank_regressed}")
    if protected_rank_regressed > 0:
        review_blockers.append(f"protected rank regressions present: {protected_rank_regressed}")
    if tail_rank_regressed > 0:
        review_blockers.append(f"tail rank regressions present: {tail_rank_regressed}")
    if anchor_top1_changed > 0:
        review_blockers.append(f"anchor top1 changed rows present: {anchor_top1_changed}")
    if anchor_max_kl > 0.005:
        review_blockers.append(f"anchor max KL too high: {anchor_max_kl:.10f}")

    for flag, value in would_flags.items():
        if value:
            review_blockers.append(f"dry-run safety flag unexpectedly true: {flag}")

    if warnings:
        review_warnings.append(f"dry-run warnings carried forward: {len(warnings)}")
    if combined_warn:
        review_warnings.append(f"combined dry-run WARN rows carried forward: {len(combined_warn)}")
    if protected_prob_regressed > 0:
        review_warnings.append(f"protected raw probability regressions carried forward: {protected_prob_regressed}")
    if tail_prob_regressed > 0:
        review_warnings.append(f"tail raw probability regressions carried forward: {tail_prob_regressed}")
    if not direct_selected:
        review_warnings.append("no direct model-eval inputs selected; next adapter may need to start from core guard reuse only")
    else:
        review_warnings.append(f"direct model-eval inputs available for next adapter: {len(direct_selected)}")

    if review_blockers:
        review_decision = "LOCAL_COMPARISON_CONTROLLED_REVIEW_BLOCKED"
    elif direct_selected:
        review_decision = "READY_FOR_DIRECT_PROBE_EVAL_ADAPTER_WITH_WARNINGS"
    else:
        review_decision = "READY_FOR_CORE_REUSE_LOCAL_DECISION_WITH_WARNINGS"

    adapter_design_decision = get_metric(adapter_design, "design_decision")
    design_direct_count = get_metric(adapter_design, "direct_model_eval_inputs_selected", "0")
    design_deferred_count = get_metric(adapter_design, "deferred_adapter_inputs", "0")

    summary_rows = [
        row("review_decision", review_decision, "INFO", "Controlled review only; no model eval."),
        row("review_blocker_count", len(review_blockers), "PASS" if not review_blockers else "FAIL", "; ".join(review_blockers)),
        row("review_warning_count", len(review_warnings), "WARN" if review_warnings else "PASS", "; ".join(review_warnings)),
        row("executor_decision", executor_decision, "PASS" if executor_decision == EXPECTED_READY else "FAIL"),
        row("dryrun_blocker_count", len(blockers), "PASS" if not blockers else "FAIL", "; ".join(blockers)),
        row("dryrun_warning_count", len(warnings), "WARN" if warnings else "PASS", "; ".join(warnings)),
        row("combined_rows", len(combined), "INFO"),
        row("combined_fail_rows", len(combined_fail), "PASS" if not combined_fail else "FAIL"),
        row("combined_warn_rows", len(combined_warn), "WARN" if combined_warn else "PASS"),
        row("selected_inputs", len(selected), "INFO"),
        row("core_selected_inputs", len(core_selected), "PASS" if len(core_selected) == 3 else "FAIL"),
        row("direct_model_eval_inputs_selected", len(direct_selected), "INFO"),
        row("adapter_design_decision", adapter_design_decision, "INFO"),
        row("adapter_design_direct_model_eval_inputs_selected", design_direct_count, "INFO"),
        row("adapter_design_deferred_adapter_inputs", design_deferred_count, "INFO"),
        row("would_train", int(would_flags["would_train"]), "PASS" if not would_flags["would_train"] else "FAIL"),
        row("would_eval_model", int(would_flags["would_eval_model"]), "PASS" if not would_flags["would_eval_model"] else "FAIL"),
        row("would_write_checkpoint", int(would_flags["would_write_checkpoint"]), "PASS" if not would_flags["would_write_checkpoint"] else "FAIL"),
        row("would_c_export", int(would_flags["would_c_export"]), "PASS" if not would_flags["would_c_export"] else "FAIL"),
        row("would_public_benchmark", int(would_flags["would_public_benchmark"]), "PASS" if not would_flags["would_public_benchmark"] else "FAIL"),
        row("would_promote", int(would_flags["would_promote"]), "PASS" if not would_flags["would_promote"] else "FAIL"),
        row("trainable_gap_improved", trainable_gap_improved, "PASS" if trainable_gap_improved == 44 else "FAIL"),
        row("trainable_rank_regressed", trainable_rank_regressed, "PASS" if trainable_rank_regressed == 0 else "FAIL"),
        row("protected_rank_regressed", protected_rank_regressed, "PASS" if protected_rank_regressed == 0 else "FAIL"),
        row("tail_rank_regressed", tail_rank_regressed, "PASS" if tail_rank_regressed == 0 else "WARN"),
        row("protected_prob_regressed", protected_prob_regressed, "WARN" if protected_prob_regressed else "PASS"),
        row("tail_prob_regressed", tail_prob_regressed, "WARN" if tail_prob_regressed else "PASS"),
        row("anchor_top1_changed", anchor_top1_changed, "PASS" if anchor_top1_changed == 0 else "FAIL"),
        row("anchor_max_kl", f"{anchor_max_kl:.10f}", "PASS" if anchor_max_kl <= 0.005 else "FAIL"),
    ]

    args.out_summary_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.out_summary_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["metric", "value", "status", "notes"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(summary_rows)

    next_plan_lines = [
        "# Teacher-divergence run1 local comparison controlled review next plan",
        "",
        f"review_decision={review_decision}",
        "",
        "## If proceeding",
        "",
        "Next branch:",
        "exp/15x15-teacher-divergence-run1-direct-probe-eval-adapter",
        "",
        "Purpose:",
        "- Add controlled model-eval adapter only for selected direct-ready fixed-probe/heldout inputs, if any.",
        "- Keep default mode dry-run.",
        "- Require explicit confirmation before any model eval.",
        "- Produce local comparison outputs only.",
        "",
        "Must remain forbidden:",
        "- training",
        "- checkpoint write",
        "- current_best overwrite",
        "- C export",
        "- public benchmark",
        "- promotion",
        "",
        "## Carried-forward warnings",
    ]
    if review_warnings:
        next_plan_lines.extend([f"- {w}" for w in review_warnings])
    else:
        next_plan_lines.append("- none")

    next_plan_lines.extend([
        "",
        "## Blockers",
    ])
    if review_blockers:
        next_plan_lines.extend([f"- {b}" for b in review_blockers])
    else:
        next_plan_lines.append("- none")

    args.out_next_plan.parent.mkdir(parents=True, exist_ok=True)
    args.out_next_plan.write_text("\n".join(next_plan_lines) + "\n", encoding="utf-8")

    report = [
        "# Teacher-divergence run1 local comparison controlled review",
        "",
        "## Branch",
        "",
        "`exp/15x15-teacher-divergence-run1-local-comparison-controlled-review`",
        "",
        "## Scope",
        "",
        "- Reviews local comparison executor dry-run outputs.",
        "- Confirms whether the dry-run is safe enough to proceed to a controlled direct-probe eval adapter.",
        "- Does not train.",
        "- Does not run model eval.",
        "- Does not read or write checkpoint contents.",
        "- Does not overwrite `checkpoints/15x15_current_best.pt`.",
        "- Does not C export.",
        "- Does not run public benchmark.",
        "- Does not promote.",
        "",
        "## Review decision",
        "",
        f"`{review_decision}`",
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
        "## Review blockers",
        "",
    ])
    if review_blockers:
        for item in review_blockers:
            report.append(f"- {item}")
    else:
        report.append("- None.")

    report.extend([
        "",
        "## Review warnings",
        "",
    ])
    if review_warnings:
        for item in review_warnings:
            report.append(f"- {item}")
    else:
        report.append("- None.")

    report.extend([
        "",
        "## Selected direct model-eval inputs",
        "",
        "| adapter_kind | stage | path | rows/count |",
        "|---|---|---|---:|",
    ])

    if direct_selected:
        for r in direct_selected:
            report.append(
                f"| {r.get('adapter_kind', '')} | {r.get('stage_class', '')} | `{r.get('path', '')}` | {r.get('sample_rows_or_count', '')} |"
            )
    else:
        report.append("| none |  |  |  |")

    report.extend([
        "",
        "## Interpretation",
        "",
    ])

    if review_blockers:
        report.append("Do not proceed to direct-probe eval adapter until the blockers above are fixed.")
    elif direct_selected:
        report.append("Proceed to a controlled direct-probe eval adapter branch. Keep default mode dry-run and require explicit confirmation before model eval.")
    else:
        report.append("No direct-ready eval inputs are selected. The next step should either implement a core-reuse local decision report or add a narrow adapter for one reviewed input source.")

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

    print("review_decision:", review_decision)
    print("review_blocker_count:", len(review_blockers))
    print("review_warning_count:", len(review_warnings))
    print("executor_decision:", executor_decision)
    print("combined_fail_rows:", len(combined_fail))
    print("combined_warn_rows:", len(combined_warn))
    print("core_selected_inputs:", len(core_selected))
    print("direct_model_eval_inputs_selected:", len(direct_selected))
    print("trainable_gap_improved:", trainable_gap_improved)
    print("protected_rank_regressed:", protected_rank_regressed)
    print("tail_rank_regressed:", tail_rank_regressed)
    print("anchor_top1_changed:", anchor_top1_changed)
    print("out_summary_csv:", args.out_summary_csv)
    print("out_next_plan:", args.out_next_plan)
    print("out_report:", args.out_report)
    print("controlled review only; no model eval; no training; no checkpoint read/write; no C export; no benchmark; no promotion")


if __name__ == "__main__":
    main()
