#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


PASS_DECISIONS = {
    "EPSILON_REVIEW_PASS__READY_FOR_FIXED_PROBE_HELDOUT",
    "EPSILON_REVIEW_PASS_WITH_WARNINGS__NEEDS_FIXED_PROBE_HELDOUT",
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Plan local fixed-probe/heldout comparison after run1 epsilon review."
    )
    p.add_argument(
        "--epsilon-summary",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_epsilon_prob_regression_summary.csv"),
    )
    p.add_argument(
        "--promotion-readiness-summary",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_promotion_readiness_summary.csv"),
    )
    p.add_argument(
        "--wrapper-decision-json",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_gated_training_run1_e10_wrapper_decision.json"),
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
        default=Path("analysis/integration_eval/teacher_divergence_run1_fixed_probe_heldout_plan_summary.csv"),
    )
    p.add_argument(
        "--out-commands",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_fixed_probe_heldout_plan_commands.txt"),
    )
    p.add_argument(
        "--out-report",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_fixed_probe_heldout_plan.md"),
    )
    return p.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def by_metric(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {r["metric"]: r for r in rows}


def get_value(m: dict[str, dict[str, str]], key: str, default: str = "") -> str:
    return m.get(key, {}).get("value", default)


def as_int(value: str) -> int:
    if value == "":
        return 0
    return int(float(value))


def as_float(value: str) -> float:
    if value == "":
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
        args.epsilon_summary,
        args.promotion_readiness_summary,
        args.wrapper_decision_json,
        args.current_best_checkpoint,
    ]:
        if not p.exists():
            raise FileNotFoundError(p)

    eps_rows = read_csv(args.epsilon_summary)
    promo_rows = read_csv(args.promotion_readiness_summary)
    eps = by_metric(eps_rows)
    promo = by_metric(promo_rows)
    wrapper = json.loads(args.wrapper_decision_json.read_text(encoding="utf-8"))

    epsilon_decision = get_value(eps, "epsilon_decision")
    readiness_decision = get_value(promo, "readiness_decision")
    wrapper_decision = wrapper.get("executor_decision", "")

    hard_concern_rows = as_int(get_value(eps, "hard_concern_rows"))
    warning_rows = as_int(get_value(eps, "warning_rows"))
    total_rank_regressions = as_int(get_value(eps, "total_rank_regressions"))
    total_prob_regressions = as_int(get_value(eps, "total_prob_regressions"))
    max_probability_loss = as_float(get_value(eps, "max_probability_loss"))
    protected_prob_regressions = as_int(get_value(eps, "protected_top10_prob_regressions"))
    tail_prob_regressions = as_int(get_value(eps, "tail_rank_gt50_prob_regressions"))

    train_gap_improved = as_int(get_value(promo, "trainable_gap_improved_rows"))
    train_mean_gap_delta = as_float(get_value(promo, "trainable_mean_gap_delta"))
    train_rank_regressed = as_int(get_value(promo, "trainable_rank_regressed_rows"))
    protected_rank_regressed = as_int(get_value(promo, "protected_top10_rank_regressed_rows"))
    anchor_top1_changed = as_int(get_value(promo, "anchor_top1_changed_rows"))
    anchor_max_kl = as_float(get_value(promo, "anchor_max_kl"))

    candidate_exists = args.candidate_checkpoint.exists()
    current_best_exists = args.current_best_checkpoint.exists()

    blockers: list[str] = []
    warnings: list[str] = []

    if wrapper_decision != "EXECUTION_PASS_KEEP_ISOLATED_CANDIDATE":
        blockers.append(f"wrapper decision is not pass: {wrapper_decision}")
    if readiness_decision != "NOT_PROMOTION_READY__READY_FOR_EPSILON_GATED_LOCAL_REVIEW":
        blockers.append(f"unexpected promotion-readiness decision: {readiness_decision}")
    if epsilon_decision not in PASS_DECISIONS:
        blockers.append(f"epsilon review does not allow fixed-probe/heldout: {epsilon_decision}")
    if hard_concern_rows > 0:
        blockers.append(f"epsilon hard concerns present: {hard_concern_rows}")
    if total_rank_regressions > 0:
        blockers.append(f"rank regressions present in epsilon review: {total_rank_regressions}")
    if train_gap_improved != 44:
        blockers.append(f"trainable gap improved rows not 44: {train_gap_improved}")
    if train_mean_gap_delta <= 0:
        blockers.append(f"trainable mean gap delta not positive: {train_mean_gap_delta:.10f}")
    if train_rank_regressed > 0:
        blockers.append(f"trainable rank regressions present: {train_rank_regressed}")
    if protected_rank_regressed > 0:
        blockers.append(f"protected rank regressions present: {protected_rank_regressed}")
    if anchor_top1_changed > 0:
        blockers.append(f"anchor top1 changes present: {anchor_top1_changed}")
    if anchor_max_kl > 0.005:
        blockers.append(f"anchor max KL above threshold: {anchor_max_kl:.10f}")
    if not candidate_exists:
        blockers.append("local isolated candidate checkpoint missing")
    if not current_best_exists:
        blockers.append("current_best checkpoint missing")

    if warning_rows > 0:
        warnings.append(f"epsilon warning rows present: {warning_rows}")
    if total_prob_regressions > 0:
        warnings.append(f"raw probability regressions remain: {total_prob_regressions}")
    if protected_prob_regressions > 0:
        warnings.append(f"protected_top10 raw probability regressions: {protected_prob_regressions}")
    if tail_prob_regressions > 0:
        warnings.append(f"tail_rank_gt50 raw probability regressions: {tail_prob_regressions}")

    if blockers:
        plan_decision = "FIXED_PROBE_HELDOUT_PLAN_BLOCKED"
    elif epsilon_decision == "EPSILON_REVIEW_PASS_WITH_WARNINGS__NEEDS_FIXED_PROBE_HELDOUT":
        plan_decision = "READY_TO_DESIGN_FIXED_PROBE_HELDOUT_WITH_WARNINGS"
    else:
        plan_decision = "READY_TO_DESIGN_FIXED_PROBE_HELDOUT"

    fixed_probe_outputs = {
        "fixed_probe_csv": "analysis/integration_eval/teacher_divergence_run1_fixed_probe_candidate_vs_current_best.csv",
        "fixed_probe_report": "analysis/integration_eval/teacher_divergence_run1_fixed_probe_candidate_vs_current_best.md",
        "heldout_csv": "analysis/integration_eval/teacher_divergence_run1_heldout_candidate_vs_current_best.csv",
        "heldout_report": "analysis/integration_eval/teacher_divergence_run1_heldout_candidate_vs_current_best.md",
        "decision_csv": "analysis/integration_eval/teacher_divergence_run1_fixed_probe_heldout_decision.csv",
        "decision_report": "analysis/integration_eval/teacher_divergence_run1_fixed_probe_heldout_decision.md",
    }

    summary_rows = [
        row("plan_decision", plan_decision, "INFO", "Plan only; not execution."),
        row("blocker_count", len(blockers), "PASS" if not blockers else "FAIL", "; ".join(blockers)),
        row("warning_count", len(warnings), "WARN" if warnings else "PASS", "; ".join(warnings)),
        row("epsilon_decision", epsilon_decision, "PASS" if epsilon_decision in PASS_DECISIONS else "FAIL"),
        row("promotion_readiness_decision", readiness_decision, "INFO"),
        row("wrapper_decision", wrapper_decision, "PASS" if wrapper_decision == "EXECUTION_PASS_KEEP_ISOLATED_CANDIDATE" else "FAIL"),
        row("candidate_checkpoint_exists_locally", int(candidate_exists), "PASS" if candidate_exists else "FAIL", "Local artifact only; do not add to git."),
        row("current_best_exists", int(current_best_exists), "PASS" if current_best_exists else "FAIL"),
        row("hard_concern_rows", hard_concern_rows, "PASS" if hard_concern_rows == 0 else "FAIL"),
        row("epsilon_warning_rows", warning_rows, "WARN" if warning_rows else "PASS"),
        row("total_prob_regressions", total_prob_regressions, "WARN" if total_prob_regressions else "PASS"),
        row("protected_top10_prob_regressions", protected_prob_regressions, "WARN" if protected_prob_regressions else "PASS"),
        row("tail_rank_gt50_prob_regressions", tail_prob_regressions, "WARN" if tail_prob_regressions else "PASS"),
        row("total_rank_regressions", total_rank_regressions, "PASS" if total_rank_regressions == 0 else "FAIL"),
        row("max_probability_loss", f"{max_probability_loss:.12f}", "INFO"),
        row("trainable_gap_improved_rows", train_gap_improved, "PASS" if train_gap_improved == 44 else "FAIL"),
        row("trainable_mean_gap_delta", f"{train_mean_gap_delta:.10f}", "PASS" if train_mean_gap_delta > 0 else "FAIL"),
        row("trainable_rank_regressed_rows", train_rank_regressed, "PASS" if train_rank_regressed == 0 else "FAIL"),
        row("protected_rank_regressed_rows", protected_rank_regressed, "PASS" if protected_rank_regressed == 0 else "FAIL"),
        row("anchor_top1_changed_rows", anchor_top1_changed, "PASS" if anchor_top1_changed == 0 else "FAIL"),
        row("anchor_max_kl", f"{anchor_max_kl:.10f}", "PASS" if anchor_max_kl <= 0.005 else "FAIL"),
    ]

    args.out_summary_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.out_summary_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["metric", "value", "status", "notes"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(summary_rows)

    commands = [
        "# Teacher-divergence run1 fixed-probe/heldout local comparison command plan",
        "# Plan only. Do not execute in this branch.",
        "",
        "## Intended next branch",
        "exp/15x15-teacher-divergence-run1-fixed-probe-heldout-comparison",
        "",
        "## Candidate/baseline checkpoints",
        f"baseline={args.current_best_checkpoint}",
        f"candidate={args.candidate_checkpoint}",
        "",
        "## Planned comparison responsibilities",
        "- Compare candidate vs current_best on existing local fixed probes.",
        "- Compare candidate vs current_best on heldout/retention/protected anchors available in repo.",
        "- Preserve explicit protected_top10 rank gate.",
        "- Preserve epsilon-aware probability warning policy.",
        "- Generate decision report before any C export or public benchmark.",
        "",
        "## Planned output files",
    ]
    for key, value in fixed_probe_outputs.items():
        commands.append(f"- {key}: {value}")
    commands.extend([
        "",
        "## Hard gates for next comparison",
        "- fixed-probe tactical regressions: 0 allowed unless explicitly reviewed",
        "- protected_top10 target rank regressions: 0",
        "- anchor top1 changes: 0 or explicitly reviewed as non-critical",
        "- heldout rank/prob regression: bounded by epsilon policy",
        "- no current_best overwrite",
        "- no C export",
        "- no public benchmark",
        "- no promotion",
        "",
    ])
    args.out_commands.write_text("\n".join(commands), encoding="utf-8")

    lines = [
        "# Teacher-divergence run1 fixed-probe / heldout local comparison plan",
        "",
        "## Branch",
        "",
        "`exp/15x15-teacher-divergence-run1-fixed-probe-heldout-plan`",
        "",
        "## Scope",
        "",
        "- Plans the next local comparison stage after run1 epsilon review.",
        "- Does not train.",
        "- Does not read or write checkpoints.",
        "- Does not overwrite `checkpoints/15x15_current_best.pt`.",
        "- Does not C export.",
        "- Does not run public benchmark.",
        "- Does not promote.",
        "",
        "## Plan decision",
        "",
        f"`{plan_decision}`",
        "",
        "## Upstream decisions",
        "",
        "| source | decision |",
        "|---|---|",
        f"| wrapper run1 | `{wrapper_decision}` |",
        f"| promotion readiness | `{readiness_decision}` |",
        f"| epsilon review | `{epsilon_decision}` |",
        "",
        "## Key carried-forward evidence",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| trainable gap improved rows | {train_gap_improved}/44 |",
        f"| trainable mean gap delta | {train_mean_gap_delta:.10f} |",
        f"| trainable rank regressions | {train_rank_regressed} |",
        f"| protected rank regressions | {protected_rank_regressed} |",
        f"| anchor top1 changes | {anchor_top1_changed} |",
        f"| anchor max KL | {anchor_max_kl:.10f} |",
        f"| epsilon warning rows | {warning_rows} |",
        f"| epsilon hard concern rows | {hard_concern_rows} |",
        f"| total raw probability regressions | {total_prob_regressions} |",
        f"| max probability loss | {max_probability_loss:.12f} |",
        "",
        "## Blockers",
        "",
    ]

    if blockers:
        for item in blockers:
            lines.append(f"- {item}")
    else:
        lines.append("- None.")

    lines.extend([
        "",
        "## Warnings to carry into next stage",
        "",
    ])
    if warnings:
        for item in warnings:
            lines.append(f"- {item}")
    else:
        lines.append("- None.")

    lines.extend([
        "",
        "## Required next comparison design",
        "",
        "The next branch should implement local candidate-vs-current_best evaluation only. It should not export C and should not run a public benchmark.",
        "",
        "Required comparisons:",
        "",
        "1. Existing fixed probes / tactical probes available in the repository.",
        "2. Heldout retention/protected rows available from the normalized manifest and prior guard outputs.",
        "3. Anchor drift rows already used by the wrapper.",
        "4. Epsilon-aware probability regression classification carried forward from run1.",
        "",
        "## Proposed next-stage hard gates",
        "",
        "| gate | threshold |",
        "|---|---|",
        "| fixed-probe tactical regression | 0 unreviewed regressions |",
        "| protected_top10 rank regression | 0 |",
        "| anchor top1 changed rows | 0, unless explicitly reviewed |",
        "| heldout severe probability loss | 0 hard_concern rows |",
        "| current_best overwrite | forbidden |",
        "| C export | forbidden in this stage |",
        "| public benchmark | forbidden in this stage |",
        "| promotion | forbidden in this stage |",
        "",
        "## Planned outputs for next branch",
        "",
    ])

    for key, value in fixed_probe_outputs.items():
        lines.append(f"- {key}: `{value}`")

    lines.extend([
        "",
        "## Summary table",
        "",
        "| metric | value | status | notes |",
        "|---|---:|---|---|",
    ])

    for r in summary_rows:
        notes = r["notes"].replace("|", "\\|")
        lines.append(f"| {r['metric']} | {r['value']} | {r['status']} | {notes} |")

    lines.extend([
        "",
        "## Recommendation",
        "",
    ])

    if blockers:
        lines.append("Do not proceed to fixed-probe/heldout comparison until blockers are resolved.")
    elif epsilon_decision == "EPSILON_REVIEW_PASS_WITH_WARNINGS__NEEDS_FIXED_PROBE_HELDOUT":
        lines.append("Proceed to a local fixed-probe/heldout comparison branch with warnings carried forward. Do not export C or benchmark.")
    else:
        lines.append("Proceed to a local fixed-probe/heldout comparison branch. Do not export C or benchmark.")

    lines.extend([
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
    args.out_report.write_text("\n".join(lines), encoding="utf-8")

    print("plan_decision:", plan_decision)
    print("epsilon_decision:", epsilon_decision)
    print("blocker_count:", len(blockers))
    print("warning_count:", len(warnings))
    print("candidate_checkpoint_exists_locally:", int(candidate_exists))
    print("trainable_gap_improved:", train_gap_improved)
    print("trainable_mean_gap_delta:", f"{train_mean_gap_delta:.10f}")
    print("hard_concern_rows:", hard_concern_rows)
    print("epsilon_warning_rows:", warning_rows)
    print("out_summary_csv:", args.out_summary_csv)
    print("out_commands:", args.out_commands)
    print("out_report:", args.out_report)
    print("plan only; no training; no checkpoint read/write; no C export; no benchmark; no promotion")


if __name__ == "__main__":
    main()
