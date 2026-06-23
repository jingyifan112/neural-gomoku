#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Audit promotion readiness for controlled gated teacher-divergence run1."
    )
    p.add_argument(
        "--wrapper-decision-json",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_gated_training_run1_e10_wrapper_decision.json"),
    )
    p.add_argument(
        "--trainable-guard",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_gated_training_run1_e10_trainable_gap_guard.csv"),
    )
    p.add_argument(
        "--bucket-guard",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_gated_training_run1_e10_manifest_bucket_guard.csv"),
    )
    p.add_argument(
        "--anchor-guard",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_gated_training_run1_e10_anchor_drift_guard.csv"),
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
        default=Path("analysis/integration_eval/teacher_divergence_run1_promotion_readiness_summary.csv"),
    )
    p.add_argument(
        "--out-report",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_promotion_readiness_audit.md"),
    )
    return p.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def int_field(row: dict[str, str], key: str) -> int:
    value = row.get(key, "")
    if value == "":
        return 0
    return int(float(value))


def float_field(row: dict[str, str], key: str) -> float:
    value = row.get(key, "")
    if value == "":
        return 0.0
    return float(value)


def mean(xs: list[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def min_or_zero(xs: list[float]) -> float:
    return min(xs) if xs else 0.0


def max_or_zero(xs: list[float]) -> float:
    return max(xs) if xs else 0.0


def summary_row(metric: str, value: Any, status: str, notes: str = "") -> dict[str, str]:
    return {
        "metric": metric,
        "value": str(value),
        "status": status,
        "notes": notes,
    }


def main() -> None:
    args = parse_args()

    for p in [
        args.wrapper_decision_json,
        args.trainable_guard,
        args.bucket_guard,
        args.anchor_guard,
        args.current_best_checkpoint,
    ]:
        if not p.exists():
            raise FileNotFoundError(p)

    decision = json.loads(args.wrapper_decision_json.read_text(encoding="utf-8"))
    trainable = read_csv(args.trainable_guard)
    bucket = read_csv(args.bucket_guard)
    anchors = read_csv(args.anchor_guard)

    wrapper_decision = decision["executor_decision"]
    final_hard_failures = decision.get("final_hard_failures", [])
    final_warnings = decision.get("final_warnings", [])
    guard_metrics = decision.get("guard_metrics", {})

    trainable_rows = len(trainable)
    train_gap_improved = sum(int_field(r, "gap_improved") for r in trainable)
    train_rank_regressed = sum(int_field(r, "target_rank_regressed") for r in trainable)
    train_prob_improved = sum(int_field(r, "target_prob_improved") for r in trainable)
    train_gap_deltas = [float_field(r, "gap_delta") for r in trainable]
    train_mean_gap_delta = mean(train_gap_deltas)
    train_min_gap_delta = min_or_zero(train_gap_deltas)
    train_max_gap_delta = max_or_zero(train_gap_deltas)

    evaluated_bucket = [r for r in bucket if r.get("status") == "evaluated"]
    protected = [r for r in evaluated_bucket if r.get("ready_bucket") == "protected_top10"]
    tail = [r for r in evaluated_bucket if r.get("ready_bucket") == "tail_rank_gt50"]

    protected_prob_regressed = sum(int_field(r, "target_prob_regressed") for r in protected)
    protected_rank_regressed = sum(int_field(r, "target_rank_regressed") for r in protected)
    tail_prob_regressed = sum(int_field(r, "target_prob_regressed") for r in tail)
    tail_rank_regressed = sum(int_field(r, "target_rank_regressed") for r in tail)

    protected_prob_deltas = [float_field(r, "target_prob_delta") for r in protected if r.get("target_prob_delta", "") != ""]
    tail_prob_deltas = [float_field(r, "target_prob_delta") for r in tail if r.get("target_prob_delta", "") != ""]

    protected_max_loss = min_or_zero(protected_prob_deltas)
    tail_max_loss = min_or_zero(tail_prob_deltas)
    protected_mean_delta = mean(protected_prob_deltas)
    tail_mean_delta = mean(tail_prob_deltas)

    anchor_rows = len(anchors)
    anchor_top1_changed = sum(int_field(r, "top1_changed") for r in anchors)
    anchor_kl_values = [float_field(r, "kl_ref_to_candidate") for r in anchors]
    anchor_mean_kl = mean(anchor_kl_values)
    anchor_max_kl = max_or_zero(anchor_kl_values)

    candidate_exists = args.candidate_checkpoint.exists()
    current_best_exists = args.current_best_checkpoint.exists()
    candidate_same_as_current_best = args.candidate_checkpoint.resolve() == args.current_best_checkpoint.resolve()

    promotion_blockers: list[str] = []
    next_evidence: list[str] = []

    if wrapper_decision != "EXECUTION_PASS_KEEP_ISOLATED_CANDIDATE":
        promotion_blockers.append(f"wrapper decision is not pass: {wrapper_decision}")
    if final_hard_failures:
        promotion_blockers.append(f"wrapper hard failures present: {len(final_hard_failures)}")
    if not candidate_exists:
        promotion_blockers.append("isolated candidate checkpoint not present locally")
    if candidate_same_as_current_best:
        promotion_blockers.append("candidate checkpoint path equals current_best")
    if trainable_rows != 44:
        promotion_blockers.append(f"trainable rows not 44: {trainable_rows}")
    if train_gap_improved != 44:
        promotion_blockers.append(f"trainable gaps did not improve on all rows: {train_gap_improved}/44")
    if train_rank_regressed != 0:
        promotion_blockers.append(f"trainable target rank regressions present: {train_rank_regressed}")
    if protected_rank_regressed != 0:
        promotion_blockers.append(f"protected_top10 rank regressions present: {protected_rank_regressed}")
    if anchor_top1_changed != 0:
        promotion_blockers.append(f"anchor top1 changes present: {anchor_top1_changed}")
    if anchor_max_kl > 0.005:
        promotion_blockers.append(f"anchor max KL above hard drift threshold: {anchor_max_kl:.10f}")

    # Promotion-specific blockers even when run1 gates pass.
    promotion_blockers.extend([
        "no epsilon-aware protected/tail probability review has been run yet",
        "no heldout/fixed-probe comparison against current_best has been run yet",
        "no C export has been generated in this workflow",
        "no public benchmark has been run in this workflow",
        "candidate checkpoint is local isolated artifact and has not been approved for promotion",
    ])

    if protected_prob_regressed > 0:
        next_evidence.append(
            f"epsilon-aware protected_top10 probability review for {protected_prob_regressed} raw regressions"
        )
    if tail_prob_regressed > 0:
        next_evidence.append(
            f"epsilon-aware tail_rank_gt50 probability review for {tail_prob_regressed} raw regressions"
        )
    next_evidence.extend([
        "local fixed-probe/heldout comparison using candidate checkpoint vs current_best",
        "promotion gate design requiring no protected rank regression and bounded epsilon probability loss",
        "only after local gates pass: decide whether C export/public benchmark is justified",
    ])

    if wrapper_decision == "EXECUTION_PASS_KEEP_ISOLATED_CANDIDATE" and not final_hard_failures:
        readiness_decision = "NOT_PROMOTION_READY__READY_FOR_EPSILON_GATED_LOCAL_REVIEW"
    else:
        readiness_decision = "NOT_PROMOTION_READY__REPAIR_RUN1_FIRST"

    bucket_counts = Counter(r.get("ready_bucket", "") for r in bucket)
    bucket_status_counts = Counter(r.get("status", "") for r in bucket)

    rows = [
        summary_row("readiness_decision", readiness_decision, "INFO", "Promotion-readiness audit decision."),
        summary_row("wrapper_decision", wrapper_decision, "PASS" if wrapper_decision == "EXECUTION_PASS_KEEP_ISOLATED_CANDIDATE" else "FAIL"),
        summary_row("wrapper_hard_failure_count", len(final_hard_failures), "PASS" if not final_hard_failures else "FAIL", "; ".join(final_hard_failures)),
        summary_row("wrapper_warning_count", len(final_warnings), "WARN" if final_warnings else "PASS", "; ".join(final_warnings)),
        summary_row("candidate_checkpoint_exists_locally", int(candidate_exists), "PASS" if candidate_exists else "FAIL", "Local artifact only; do not add to git."),
        summary_row("current_best_exists", int(current_best_exists), "PASS" if current_best_exists else "FAIL"),
        summary_row("candidate_same_as_current_best", int(candidate_same_as_current_best), "FAIL" if candidate_same_as_current_best else "PASS"),
        summary_row("trainable_rows", trainable_rows, "PASS" if trainable_rows == 44 else "FAIL"),
        summary_row("trainable_gap_improved_rows", train_gap_improved, "PASS" if train_gap_improved == 44 else "FAIL"),
        summary_row("trainable_target_prob_improved_rows", train_prob_improved, "INFO"),
        summary_row("trainable_rank_regressed_rows", train_rank_regressed, "PASS" if train_rank_regressed == 0 else "FAIL"),
        summary_row("trainable_mean_gap_delta", f"{train_mean_gap_delta:.10f}", "PASS" if train_mean_gap_delta > 0 else "FAIL"),
        summary_row("trainable_min_gap_delta", f"{train_min_gap_delta:.10f}", "INFO"),
        summary_row("trainable_max_gap_delta", f"{train_max_gap_delta:.10f}", "INFO"),
        summary_row("protected_top10_rows", len(protected), "INFO"),
        summary_row("protected_top10_rank_regressed_rows", protected_rank_regressed, "PASS" if protected_rank_regressed == 0 else "FAIL"),
        summary_row("protected_top10_prob_regressed_rows", protected_prob_regressed, "WARN" if protected_prob_regressed else "PASS"),
        summary_row("protected_top10_mean_prob_delta", f"{protected_mean_delta:.10f}", "INFO"),
        summary_row("protected_top10_max_prob_loss", f"{protected_max_loss:.10f}", "WARN" if protected_max_loss < 0 else "PASS"),
        summary_row("tail_rank_gt50_rows", len(tail), "INFO"),
        summary_row("tail_rank_gt50_rank_regressed_rows", tail_rank_regressed, "PASS" if tail_rank_regressed == 0 else "WARN"),
        summary_row("tail_rank_gt50_prob_regressed_rows", tail_prob_regressed, "WARN" if tail_prob_regressed else "PASS"),
        summary_row("tail_rank_gt50_mean_prob_delta", f"{tail_mean_delta:.10f}", "INFO"),
        summary_row("tail_rank_gt50_max_prob_loss", f"{tail_max_loss:.10f}", "WARN" if tail_max_loss < 0 else "PASS"),
        summary_row("anchor_rows", anchor_rows, "PASS" if anchor_rows == 32 else "FAIL"),
        summary_row("anchor_top1_changed_rows", anchor_top1_changed, "PASS" if anchor_top1_changed == 0 else "FAIL"),
        summary_row("anchor_mean_kl", f"{anchor_mean_kl:.10f}", "INFO"),
        summary_row("anchor_max_kl", f"{anchor_max_kl:.10f}", "PASS" if anchor_max_kl <= 0.005 else "FAIL"),
        summary_row("promotion_blocker_count", len(promotion_blockers), "FAIL", "; ".join(promotion_blockers)),
        summary_row("next_evidence_count", len(next_evidence), "INFO", "; ".join(next_evidence)),
    ]

    args.out_summary_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.out_summary_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["metric", "value", "status", "notes"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    lines = [
        "# Teacher-divergence run1 promotion-readiness audit",
        "",
        "## Branch",
        "",
        "`exp/15x15-teacher-divergence-run1-promotion-readiness-audit`",
        "",
        "## Scope",
        "",
        "- Audits promotion readiness after controlled gated training run1.",
        "- Does not promote.",
        "- Does not overwrite `checkpoints/15x15_current_best.pt`.",
        "- Does not C export.",
        "- Does not run public benchmark.",
        "- Does not add checkpoint artifacts to git.",
        "",
        "## Decision",
        "",
        f"`{readiness_decision}`",
        "",
        "## Run1 pass evidence",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| wrapper decision | {wrapper_decision} |",
        f"| wrapper hard failures | {len(final_hard_failures)} |",
        f"| wrapper warnings | {len(final_warnings)} |",
        f"| trainable gap improved rows | {train_gap_improved}/44 |",
        f"| trainable mean gap delta | {train_mean_gap_delta:.10f} |",
        f"| trainable min gap delta | {train_min_gap_delta:.10f} |",
        f"| trainable rank regressions | {train_rank_regressed} |",
        f"| protected_top10 rank regressions | {protected_rank_regressed} |",
        f"| tail_rank_gt50 rank regressions | {tail_rank_regressed} |",
        f"| anchor top1 changed rows | {anchor_top1_changed} |",
        f"| anchor max KL | {anchor_max_kl:.10f} |",
        "",
        "## Remaining warnings",
        "",
        "| bucket | rows | raw prob regressions | rank regressions | mean prob delta | max prob loss |",
        "|---|---:|---:|---:|---:|---:|",
        f"| protected_top10 | {len(protected)} | {protected_prob_regressed} | {protected_rank_regressed} | {protected_mean_delta:.10f} | {protected_max_loss:.10f} |",
        f"| tail_rank_gt50 | {len(tail)} | {tail_prob_regressed} | {tail_rank_regressed} | {tail_mean_delta:.10f} | {tail_max_loss:.10f} |",
        "",
        "## Why this is not promotion-ready",
        "",
    ]

    for blocker in promotion_blockers:
        lines.append(f"- {blocker}")

    lines.extend([
        "",
        "## Required next evidence",
        "",
    ])

    for item in next_evidence:
        lines.append(f"- {item}")

    lines.extend([
        "",
        "## Bucket/status context",
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
        "## Summary table",
        "",
        "| metric | value | status | notes |",
        "|---|---:|---|---|",
    ])

    for r in rows:
        notes = r["notes"].replace("|", "\\|")
        lines.append(f"| {r['metric']} | {r['value']} | {r['status']} | {notes} |")

    lines.extend([
        "",
        "## Recommendation",
        "",
        "Do not promote run1.",
        "",
        "Proceed to an epsilon-aware protected/tail probability regression review branch. That branch should classify raw probability regressions by magnitude and decide whether warnings are acceptable noise or require objective/gate repair.",
        "",
        "Only after local epsilon-aware guards and fixed-probe/heldout checks pass should C export or public benchmark be considered.",
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

    print("readiness_decision:", readiness_decision)
    print("wrapper_decision:", wrapper_decision)
    print("trainable_gap_improved:", train_gap_improved)
    print("trainable_mean_gap_delta:", f"{train_mean_gap_delta:.10f}")
    print("protected_prob_regressed:", protected_prob_regressed)
    print("protected_max_prob_loss:", f"{protected_max_loss:.10f}")
    print("tail_prob_regressed:", tail_prob_regressed)
    print("tail_max_prob_loss:", f"{tail_max_loss:.10f}")
    print("anchor_top1_changed:", anchor_top1_changed)
    print("anchor_max_kl:", f"{anchor_max_kl:.10f}")
    print("promotion_blocker_count:", len(promotion_blockers))
    print("out_summary_csv:", args.out_summary_csv)
    print("out_report:", args.out_report)
    print("audit only; no C export; no benchmark; no promotion")


if __name__ == "__main__":
    main()
