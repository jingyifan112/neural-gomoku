#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Close out tiny teacher-divergence probe by combining training summary and posttrain guard audit."
    )
    p.add_argument(
        "--tiny-gap-csv",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_tiny_policy_margin_probe_e3_gap_summary.csv"),
    )
    p.add_argument(
        "--tiny-epoch-csv",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_tiny_policy_margin_probe_e3_epoch_metrics.csv"),
    )
    p.add_argument(
        "--posttrain-trainable-csv",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_tiny_posttrain_trainable_gap_guard.csv"),
    )
    p.add_argument(
        "--posttrain-bucket-csv",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_tiny_posttrain_manifest_bucket_guard.csv"),
    )
    p.add_argument(
        "--posttrain-anchor-csv",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_tiny_posttrain_anchor_drift_guard.csv"),
    )
    p.add_argument(
        "--out-summary-csv",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_tiny_probe_guard_decision_summary.csv"),
    )
    p.add_argument(
        "--out-report",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_tiny_probe_guard_decision_closeout.md"),
    )
    p.add_argument("--expected-trainable", type=int, default=44)
    p.add_argument("--expected-anchors", type=int, default=32)
    p.add_argument("--min-gap-improved", type=int, default=40)
    p.add_argument("--max-train-rank-regressions", type=int, default=4)
    p.add_argument("--max-anchor-top1-changes", type=int, default=0)
    p.add_argument("--max-protected-rank-regressions", type=int, default=0)
    p.add_argument("--hard-anchor-kl", type=float, default=0.05)
    p.add_argument("--warn-anchor-kl", type=float, default=0.005)
    return p.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def f(row: dict[str, str], key: str, default: float = 0.0) -> float:
    value = row.get(key, "")
    if value == "":
        return default
    return float(value)


def i(row: dict[str, str], key: str, default: int = 0) -> int:
    value = row.get(key, "")
    if value == "":
        return default
    return int(float(value))


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def metric_row(name: str, value: Any, status: str, notes: str = "") -> dict[str, str]:
    return {
        "metric": name,
        "value": str(value),
        "status": status,
        "notes": notes,
    }


def main() -> None:
    args = parse_args()

    for path in [
        args.tiny_gap_csv,
        args.tiny_epoch_csv,
        args.posttrain_trainable_csv,
        args.posttrain_bucket_csv,
        args.posttrain_anchor_csv,
    ]:
        if not path.exists():
            raise FileNotFoundError(path)

    tiny_gap = read_csv(args.tiny_gap_csv)
    epochs = read_csv(args.tiny_epoch_csv)
    trainable = read_csv(args.posttrain_trainable_csv)
    bucket = read_csv(args.posttrain_bucket_csv)
    anchors = read_csv(args.posttrain_anchor_csv)

    hard_failures: list[str] = []
    warnings: list[str] = []

    if len(tiny_gap) != args.expected_trainable:
        hard_failures.append(f"tiny_gap_rows expected {args.expected_trainable}, got {len(tiny_gap)}")
    if len(trainable) != args.expected_trainable:
        hard_failures.append(f"posttrain_trainable_rows expected {args.expected_trainable}, got {len(trainable)}")
    if len(anchors) != args.expected_anchors:
        hard_failures.append(f"anchor_rows expected {args.expected_anchors}, got {len(anchors)}")
    if len(epochs) != 3:
        warnings.append(f"expected 3 epoch metric rows, got {len(epochs)}")

    tiny_gap_improved = sum(i(r, "gap_improved") for r in tiny_gap)
    tiny_target_prob_improved = sum(i(r, "target_prob_improved") for r in tiny_gap)
    tiny_mean_gap_delta = mean([f(r, "gap_delta") for r in tiny_gap])
    tiny_mean_target_prob_delta = mean([f(r, "target_prob_delta") for r in tiny_gap])
    tiny_mean_suppress_prob_delta = mean([f(r, "suppress_prob_delta") for r in tiny_gap])

    post_gap_improved = sum(i(r, "gap_improved") for r in trainable)
    post_target_prob_improved = sum(i(r, "target_prob_improved") for r in trainable)
    post_target_rank_improved = sum(i(r, "target_rank_improved") for r in trainable)
    post_target_rank_regressed = sum(i(r, "target_rank_regressed") for r in trainable)
    post_mean_gap_delta = mean([f(r, "gap_delta") for r in trainable])
    post_min_gap_delta = min([f(r, "gap_delta") for r in trainable]) if trainable else 0.0
    post_mean_target_prob_delta = mean([f(r, "target_prob_delta") for r in trainable])
    post_mean_suppress_prob_delta = mean([f(r, "suppress_prob_delta") for r in trainable])

    evaluated_bucket = [r for r in bucket if r.get("status") == "evaluated"]
    bucket_counts = Counter(r.get("ready_bucket", "") for r in bucket)
    bucket_status_counts = Counter(r.get("status", "") for r in bucket)

    protected = [r for r in evaluated_bucket if r.get("ready_bucket") == "protected_top10"]
    tail = [r for r in evaluated_bucket if r.get("ready_bucket") == "tail_rank_gt50"]

    protected_rank_regressed = sum(i(r, "target_rank_regressed") for r in protected)
    protected_prob_regressed = sum(i(r, "target_prob_regressed") for r in protected)
    tail_rank_regressed = sum(i(r, "target_rank_regressed") for r in tail)
    tail_prob_regressed = sum(i(r, "target_prob_regressed") for r in tail)

    anchor_top1_changed = sum(i(r, "top1_changed") for r in anchors)
    anchor_kl_values = [f(r, "kl_ref_to_candidate") for r in anchors]
    anchor_mean_kl = mean(anchor_kl_values)
    anchor_max_kl = max(anchor_kl_values) if anchor_kl_values else 0.0

    first_loss = f(epochs[0], "loss") if epochs else 0.0
    final_loss = f(epochs[-1], "loss") if epochs else 0.0
    first_margin_loss = f(epochs[0], "margin_loss") if epochs else 0.0
    final_margin_loss = f(epochs[-1], "margin_loss") if epochs else 0.0
    loss_delta = final_loss - first_loss
    margin_loss_delta = final_margin_loss - first_margin_loss

    if post_gap_improved < args.min_gap_improved:
        hard_failures.append(f"posttrain gap improved rows {post_gap_improved} < threshold {args.min_gap_improved}")
    if post_mean_gap_delta <= 0:
        hard_failures.append(f"posttrain mean gap delta {post_mean_gap_delta:.10f} <= 0")
    if post_target_rank_regressed > args.max_train_rank_regressions:
        hard_failures.append(
            f"trainable target rank regressions {post_target_rank_regressed} > threshold {args.max_train_rank_regressions}"
        )
    elif post_target_rank_regressed > 0:
        warnings.append(f"trainable target rank regressions observed: {post_target_rank_regressed}")

    if protected_rank_regressed > args.max_protected_rank_regressions:
        hard_failures.append(
            f"protected_top10 rank regressions {protected_rank_regressed} > threshold {args.max_protected_rank_regressions}"
        )
    if protected_prob_regressed > 0:
        warnings.append(f"protected_top10 probability regressions observed: {protected_prob_regressed}")
    if tail_rank_regressed > 0:
        warnings.append(f"tail_rank_gt50 rank regressions observed: {tail_rank_regressed}")
    if tail_prob_regressed > 0:
        warnings.append(f"tail_rank_gt50 probability regressions observed: {tail_prob_regressed}")

    if anchor_top1_changed > args.max_anchor_top1_changes:
        hard_failures.append(f"anchor top1 changes {anchor_top1_changed} > threshold {args.max_anchor_top1_changes}")
    if anchor_max_kl > args.hard_anchor_kl:
        hard_failures.append(f"anchor max KL {anchor_max_kl:.10f} > hard threshold {args.hard_anchor_kl}")
    elif anchor_max_kl > args.warn_anchor_kl:
        warnings.append(f"anchor max KL {anchor_max_kl:.10f} > warning threshold {args.warn_anchor_kl}")

    if hard_failures:
        decision = "STOP_OR_REPAIR_BEFORE_LARGER_TRAINING"
    elif warnings:
        decision = "PASS_TO_GATED_TRAINING_REVIEW_WITH_WARNINGS"
    else:
        decision = "PASS_TO_GATED_TRAINING_REVIEW"

    summary_rows = [
        metric_row("decision", decision, "INFO", "closeout decision"),
        metric_row("hard_failure_count", len(hard_failures), "PASS" if not hard_failures else "FAIL", "; ".join(hard_failures)),
        metric_row("warning_count", len(warnings), "PASS" if not warnings else "WARN", "; ".join(warnings)),
        metric_row("tiny_gap_rows", len(tiny_gap), "PASS" if len(tiny_gap) == args.expected_trainable else "FAIL"),
        metric_row("posttrain_trainable_rows", len(trainable), "PASS" if len(trainable) == args.expected_trainable else "FAIL"),
        metric_row("anchor_rows", len(anchors), "PASS" if len(anchors) == args.expected_anchors else "FAIL"),
        metric_row("epoch_rows", len(epochs), "PASS" if len(epochs) == 3 else "WARN"),
        metric_row("tiny_gap_improved_rows", tiny_gap_improved, "INFO"),
        metric_row("tiny_target_prob_improved_rows", tiny_target_prob_improved, "INFO"),
        metric_row("tiny_mean_gap_delta", f"{tiny_mean_gap_delta:.10f}", "INFO"),
        metric_row("tiny_mean_target_prob_delta", f"{tiny_mean_target_prob_delta:.10f}", "INFO"),
        metric_row("tiny_mean_suppress_prob_delta", f"{tiny_mean_suppress_prob_delta:.10f}", "INFO"),
        metric_row("posttrain_gap_improved_rows", post_gap_improved, "PASS" if post_gap_improved >= args.min_gap_improved else "FAIL"),
        metric_row("posttrain_target_prob_improved_rows", post_target_prob_improved, "INFO"),
        metric_row("posttrain_target_rank_improved_rows", post_target_rank_improved, "INFO"),
        metric_row(
            "posttrain_target_rank_regressed_rows",
            post_target_rank_regressed,
            "PASS" if post_target_rank_regressed <= args.max_train_rank_regressions else "FAIL",
        ),
        metric_row("posttrain_mean_gap_delta", f"{post_mean_gap_delta:.10f}", "PASS" if post_mean_gap_delta > 0 else "FAIL"),
        metric_row("posttrain_min_gap_delta", f"{post_min_gap_delta:.10f}", "INFO"),
        metric_row("posttrain_mean_target_prob_delta", f"{post_mean_target_prob_delta:.10f}", "INFO"),
        metric_row("posttrain_mean_suppress_prob_delta", f"{post_mean_suppress_prob_delta:.10f}", "INFO"),
        metric_row("protected_top10_rows", len(protected), "INFO"),
        metric_row("protected_top10_rank_regressed_rows", protected_rank_regressed, "PASS" if protected_rank_regressed == 0 else "FAIL"),
        metric_row("protected_top10_prob_regressed_rows", protected_prob_regressed, "PASS" if protected_prob_regressed == 0 else "WARN"),
        metric_row("tail_rank_gt50_rows", len(tail), "INFO"),
        metric_row("tail_rank_gt50_rank_regressed_rows", tail_rank_regressed, "PASS" if tail_rank_regressed == 0 else "WARN"),
        metric_row("tail_rank_gt50_prob_regressed_rows", tail_prob_regressed, "PASS" if tail_prob_regressed == 0 else "WARN"),
        metric_row("anchor_top1_changed_rows", anchor_top1_changed, "PASS" if anchor_top1_changed == 0 else "FAIL"),
        metric_row("anchor_mean_kl", f"{anchor_mean_kl:.10f}", "INFO"),
        metric_row(
            "anchor_max_kl",
            f"{anchor_max_kl:.10f}",
            "PASS" if anchor_max_kl <= args.warn_anchor_kl else "WARN" if anchor_max_kl <= args.hard_anchor_kl else "FAIL",
        ),
        metric_row("loss_delta", f"{loss_delta:.10f}", "INFO"),
        metric_row("margin_loss_delta", f"{margin_loss_delta:.10f}", "INFO"),
    ]

    args.out_summary_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.out_summary_csv.open("w", newline="", encoding="utf-8") as fcsv:
        writer = csv.DictWriter(fcsv, fieldnames=["metric", "value", "status", "notes"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(summary_rows)

    lines = [
        "# Teacher-divergence tiny probe guard decision closeout",
        "",
        "## Branch",
        "",
        "`exp/15x15-teacher-divergence-tiny-guard-decision-closeout`",
        "",
        "## Scope",
        "",
        "- Combines the tiny policy-margin training summary and post-training guard audit.",
        "- Produces a decision for whether to continue to a later gated training review.",
        "- Does not train.",
        "- Does not read or write checkpoints.",
        "- Does not overwrite `checkpoints/15x15_current_best.pt`.",
        "- Does not C export.",
        "- Does not run public benchmark.",
        "- Does not promote.",
        "",
        "## Inputs",
        "",
        f"- tiny gap summary: `{args.tiny_gap_csv}`",
        f"- tiny epoch metrics: `{args.tiny_epoch_csv}`",
        f"- posttrain trainable guard: `{args.posttrain_trainable_csv}`",
        f"- posttrain bucket guard: `{args.posttrain_bucket_csv}`",
        f"- posttrain anchor drift guard: `{args.posttrain_anchor_csv}`",
        "",
        "## Decision",
        "",
        f"`{decision}`",
        "",
        "## Summary",
        "",
        "| metric | value | status | notes |",
        "|---|---:|---|---|",
    ]

    for row in summary_rows:
        notes = row["notes"].replace("|", "\\|")
        lines.append(f"| {row['metric']} | {row['value']} | {row['status']} | {notes} |")

    lines.extend([
        "",
        "## Bucket guard context",
        "",
        "| item | count |",
        "|---|---:|",
    ])

    for key, value in bucket_counts.most_common():
        lines.append(f"| bucket:{key} | {value} |")
    for key, value in bucket_status_counts.most_common():
        lines.append(f"| status:{key} | {value} |")

    lines.extend([
        "",
        "## Hard failures",
        "",
    ])

    if hard_failures:
        for failure in hard_failures:
            lines.append(f"- {failure}")
    else:
        lines.append("- None.")

    lines.extend([
        "",
        "## Warnings",
        "",
    ])

    if warnings:
        for warning in warnings:
            lines.append(f"- {warning}")
    else:
        lines.append("- None.")

    lines.extend([
        "",
        "## Interpretation",
        "",
    ])

    if decision == "STOP_OR_REPAIR_BEFORE_LARGER_TRAINING":
        lines.extend([
            "The tiny probe should not be scaled yet. Resolve hard failures first, then rerun guard audit.",
            "",
            "Do not run larger training from this checkpoint.",
        ])
    elif decision == "PASS_TO_GATED_TRAINING_REVIEW_WITH_WARNINGS":
        lines.extend([
            "The tiny probe has positive trainable signal but includes guard warnings.",
            "",
            "The next step may be a gated training review branch, not promotion. Any larger run should include explicit protected/heldout gates and save-on-pass behavior.",
        ])
    else:
        lines.extend([
            "The tiny probe passes the configured closeout checks.",
            "",
            "The next step may be a gated training review branch, not promotion. Any larger run should preserve protected/heldout gates and isolated output paths.",
        ])

    lines.extend([
        "",
        "## Output",
        "",
        f"- summary CSV: `{args.out_summary_csv}`",
        f"- closeout report: `{args.out_report}`",
        "",
        "## Final guardrails",
        "",
        "- No current_best overwrite.",
        "- No C export.",
        "- No public benchmark.",
        "- No promotion.",
        "",
    ])

    args.out_report.parent.mkdir(parents=True, exist_ok=True)
    args.out_report.write_text("\n".join(lines), encoding="utf-8")

    print("decision:", decision)
    print("hard_failure_count:", len(hard_failures))
    print("warning_count:", len(warnings))
    print("posttrain_gap_improved_rows:", post_gap_improved)
    print("posttrain_mean_gap_delta:", f"{post_mean_gap_delta:.10f}")
    print("protected_rank_regressed:", protected_rank_regressed)
    print("anchor_top1_changed:", anchor_top1_changed)
    print("anchor_max_kl:", f"{anchor_max_kl:.10f}")
    print("out_summary_csv:", args.out_summary_csv)
    print("out_report:", args.out_report)
    print("no training; no checkpoint write; no C export; no benchmark; no promotion")


if __name__ == "__main__":
    main()
