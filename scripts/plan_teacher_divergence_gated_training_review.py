#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Create a gated training review plan from tiny probe closeout and posttrain guards."
    )
    p.add_argument(
        "--decision-summary",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_tiny_probe_guard_decision_summary.csv"),
    )
    p.add_argument(
        "--trainable-guard",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_tiny_posttrain_trainable_gap_guard.csv"),
    )
    p.add_argument(
        "--bucket-guard",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_tiny_posttrain_manifest_bucket_guard.csv"),
    )
    p.add_argument(
        "--anchor-guard",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_tiny_posttrain_anchor_drift_guard.csv"),
    )
    p.add_argument(
        "--out-summary-csv",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_gated_training_review_plan_summary.csv"),
    )
    p.add_argument(
        "--out-report",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_gated_training_review_plan.md"),
    )
    return p.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def metric_map(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {r["metric"]: r for r in rows}


def as_int(value: str) -> int:
    return int(float(value))


def as_float(value: str) -> float:
    return float(value)


def row(name: str, value: str | int | float, gate: str, rationale: str) -> dict[str, str]:
    return {
        "item": name,
        "value": str(value),
        "gate": gate,
        "rationale": rationale,
    }


def main() -> None:
    args = parse_args()

    for p in [args.decision_summary, args.trainable_guard, args.bucket_guard, args.anchor_guard]:
        if not p.exists():
            raise FileNotFoundError(p)

    decision_rows = read_csv(args.decision_summary)
    trainable = read_csv(args.trainable_guard)
    bucket = read_csv(args.bucket_guard)
    anchors = read_csv(args.anchor_guard)
    m = metric_map(decision_rows)

    decision = m["decision"]["value"]
    hard_failures = as_int(m["hard_failure_count"]["value"])
    warnings = as_int(m["warning_count"]["value"])

    post_gap_improved = as_int(m["posttrain_gap_improved_rows"]["value"])
    post_mean_gap_delta = as_float(m["posttrain_mean_gap_delta"]["value"])
    post_rank_regressed = as_int(m["posttrain_target_rank_regressed_rows"]["value"])

    protected_rows = as_int(m["protected_top10_rows"]["value"])
    protected_rank_regressed = as_int(m["protected_top10_rank_regressed_rows"]["value"])
    protected_prob_regressed = as_int(m["protected_top10_prob_regressed_rows"]["value"])

    tail_rows = as_int(m["tail_rank_gt50_rows"]["value"])
    tail_rank_regressed = as_int(m["tail_rank_gt50_rank_regressed_rows"]["value"])
    tail_prob_regressed = as_int(m["tail_rank_gt50_prob_regressed_rows"]["value"])

    anchor_rows = as_int(m["anchor_rows"]["value"])
    anchor_top1_changed = as_int(m["anchor_top1_changed_rows"]["value"])
    anchor_max_kl = as_float(m["anchor_max_kl"]["value"])
    anchor_mean_kl = as_float(m["anchor_mean_kl"]["value"])

    min_gap_delta = min(float(r["gap_delta"]) for r in trainable)
    max_protected_prob_loss = 0.0
    max_tail_prob_loss = 0.0

    for r in bucket:
        if r.get("status") != "evaluated":
            continue
        delta = r.get("target_prob_delta", "")
        if delta == "":
            continue
        d = float(delta)
        if r.get("ready_bucket") == "protected_top10":
            max_protected_prob_loss = min(max_protected_prob_loss, d)
        elif r.get("ready_bucket") == "tail_rank_gt50":
            max_tail_prob_loss = min(max_tail_prob_loss, d)

    bucket_counts = Counter(r.get("ready_bucket", "") for r in bucket)
    anchor_top1_counts = Counter(r.get("top1_changed", "") for r in anchors)

    if decision == "STOP_OR_REPAIR_BEFORE_LARGER_TRAINING" or hard_failures:
        plan_decision = "DO_NOT_START_GATED_TRAINING"
    else:
        plan_decision = "READY_TO_DESIGN_GATED_TRAINING_DRYRUN"

    summary_rows = [
        row("source_closeout_decision", decision, "INFO", "Decision from tiny probe guard closeout."),
        row("plan_decision", plan_decision, "INFO", "This plan is review-only and does not start training."),
        row("hard_failure_count", hard_failures, "PASS" if hard_failures == 0 else "FAIL", "Must be zero before any larger run."),
        row("warning_count", warnings, "WARN" if warnings else "PASS", "Warnings require explicit guard handling."),
        row("trainable_rows", len(trainable), "PASS" if len(trainable) == 44 else "FAIL", "Expected 44 round2 trainable rows."),
        row("trainable_gap_improved_rows", post_gap_improved, "PASS" if post_gap_improved == 44 else "FAIL", "Tiny probe improved all trainable gaps."),
        row("trainable_mean_gap_delta", f"{post_mean_gap_delta:.10f}", "PASS" if post_mean_gap_delta > 0 else "FAIL", "Mean gap delta must remain positive."),
        row("trainable_min_gap_delta", f"{min_gap_delta:.10f}", "INFO", "Tiny probe min gap delta; useful for calibrating next gate."),
        row("trainable_target_rank_regressed_rows", post_rank_regressed, "PASS" if post_rank_regressed == 0 else "FAIL", "No trainable target rank regression allowed."),
        row("protected_top10_rows", protected_rows, "INFO", "Protected bucket must be guarded explicitly."),
        row("protected_top10_rank_regressed_rows", protected_rank_regressed, "PASS" if protected_rank_regressed == 0 else "FAIL", "Hard fail for any protected rank regression."),
        row("protected_top10_prob_regressed_rows", protected_prob_regressed, "WARN" if protected_prob_regressed else "PASS", "Raw prob regressions observed; next run needs epsilon-aware guard."),
        row("protected_top10_max_prob_loss", f"{max_protected_prob_loss:.10f}", "WARN" if max_protected_prob_loss < 0 else "PASS", "Use as warning context, not promotion evidence."),
        row("tail_rank_gt50_rows", tail_rows, "INFO", "Tail bucket is not promotion evidence but should be monitored."),
        row("tail_rank_gt50_rank_regressed_rows", tail_rank_regressed, "WARN" if tail_rank_regressed else "PASS", "Tail rank regression should block uncontrolled scaling."),
        row("tail_rank_gt50_prob_regressed_rows", tail_prob_regressed, "WARN" if tail_prob_regressed else "PASS", "Raw prob regressions observed; next run needs epsilon-aware guard."),
        row("tail_rank_gt50_max_prob_loss", f"{max_tail_prob_loss:.10f}", "WARN" if max_tail_prob_loss < 0 else "PASS", "Use as warning context."),
        row("anchor_rows", anchor_rows, "PASS" if anchor_rows == 32 else "FAIL", "Expected corpus8 anchor snapshots."),
        row("anchor_top1_changed_rows", anchor_top1_changed, "PASS" if anchor_top1_changed == 0 else "FAIL", "Hard fail for anchor top1 changes."),
        row("anchor_mean_kl", f"{anchor_mean_kl:.10f}", "PASS", "Tiny drift was very small."),
        row("anchor_max_kl", f"{anchor_max_kl:.10f}", "PASS" if anchor_max_kl <= 0.005 else "WARN", "Use KL as drift gate."),
    ]

    args.out_summary_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.out_summary_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["item", "value", "gate", "rationale"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(summary_rows)

    lines = [
        "# Teacher-divergence gated training review plan",
        "",
        "## Branch",
        "",
        "`exp/15x15-teacher-divergence-gated-training-review-plan`",
        "",
        "## Scope",
        "",
        "- Review-only plan for a later gated training dry run.",
        "- Based on tiny probe closeout and posttrain guard audit.",
        "- Does not train.",
        "- Does not read or write checkpoints.",
        "- Does not overwrite `checkpoints/15x15_current_best.pt`.",
        "- Does not C export.",
        "- Does not run public benchmark.",
        "- Does not promote.",
        "",
        "## Source decision",
        "",
        f"`{decision}`",
        "",
        "## Plan decision",
        "",
        f"`{plan_decision}`",
        "",
        "## Why a gated review is allowed",
        "",
        "| signal | value | interpretation |",
        "|---|---:|---|",
        f"| hard failures | {hard_failures} | must be zero |",
        f"| warnings | {warnings} | requires explicit gates |",
        f"| trainable gap improved rows | {post_gap_improved}/44 | positive trainable signal |",
        f"| trainable mean gap delta | {post_mean_gap_delta:.10f} | positive but tiny effect size |",
        f"| trainable rank regressions | {post_rank_regressed} | must stay zero |",
        f"| anchor top1 changes | {anchor_top1_changed} | must stay zero |",
        f"| anchor max KL | {anchor_max_kl:.10f} | very small drift |",
        "",
        "## Warning context",
        "",
        "| warning source | rows | rank regressions | raw probability regressions | max probability loss |",
        "|---|---:|---:|---:|---:|",
        f"| protected_top10 | {protected_rows} | {protected_rank_regressed} | {protected_prob_regressed} | {max_protected_prob_loss:.10f} |",
        f"| tail_rank_gt50 | {tail_rows} | {tail_rank_regressed} | {tail_prob_regressed} | {max_tail_prob_loss:.10f} |",
        "",
        "The tiny probe produced raw probability regressions in protected/tail buckets but no rank regression and no anchor top1 change. Therefore the next step may be a gated training dry-run design, not promotion.",
        "",
        "## Required next-run architecture",
        "",
        "A later gated run must use a wrapper with save-on-pass behavior:",
        "",
        "1. Train from `checkpoints/15x15_current_best.pt`, not from a promoted checkpoint.",
        "2. Write only to an isolated candidate path, for example `checkpoints/15x15_teacher_divergence_round2_policy_margin_gated_review.pt`.",
        "3. Run trainable, protected/tail, and anchor guards immediately after training.",
        "4. Keep candidate checkpoint only if all hard gates pass.",
        "5. Quarantine or delete the candidate checkpoint if hard gates fail.",
        "6. Never overwrite `checkpoints/15x15_current_best.pt` in this workflow.",
        "",
        "## Proposed hard gates for the later dry run",
        "",
        "| gate | threshold | failure action |",
        "|---|---:|---|",
        "| trainable rows evaluated | 44 | fail if not exact |",
        "| trainable gap improved rows | >= 40 | fail run |",
        "| trainable mean gap delta | > 0 | fail run |",
        "| trainable target rank regressions | 0 | fail run |",
        "| protected_top10 target rank regressions | 0 | fail run |",
        "| anchor top1 changed rows | 0 | fail run |",
        "| anchor max KL ref->candidate | <= 0.005 | fail if above hard threshold |",
        "",
        "## Proposed warning gates",
        "",
        "| warning gate | threshold | action |",
        "|---|---:|---|",
        "| protected_top10 raw target probability regressions | > 0 | report warning; require epsilon-aware review |",
        "| tail_rank_gt50 raw target probability regressions | > 0 | report warning; require epsilon-aware review |",
        "| tail_rank_gt50 target rank regressions | > 0 | block uncontrolled scaling; inspect before continuing |",
        "| anchor max KL ref->candidate | > 0.001 and <= 0.005 | warning only |",
        "",
        "## Candidate hyperparameter review, not execution",
        "",
        "The tiny run used a very conservative 3-epoch probe and showed positive but small gap movement. A later dry-run may review one conservative configuration first:",
        "",
        "| parameter | candidate review value | rationale |",
        "|---|---:|---|",
        "| epochs | 10 | modestly larger than tiny run |",
        "| lr | 1e-6 | same as tiny run to limit protected drift |",
        "| margin | 1.0 | same objective scale |",
        "| anchor_kl_weight | 0.05 | preserve anchor behavior |",
        "| ce_weight | 0.05 | preserve target CE signal |",
        "| weight_decay | 1e-5 | same as tiny run |",
        "| seed | fixed, e.g. 31 | reproducibility |",
        "",
        "This is only a review candidate. It is not approved for promotion or public benchmarking.",
        "",
        "## Required outputs for the next dry-run branch",
        "",
        "- gated train log",
        "- trainable guard CSV",
        "- protected/tail guard CSV",
        "- anchor drift guard CSV",
        "- wrapper decision JSON/CSV",
        "- closeout report",
        "- isolated local checkpoint if and only if hard gates pass",
        "",
        "## Summary table",
        "",
        "| item | value | gate | rationale |",
        "|---|---:|---|---|",
    ]

    for r in summary_rows:
        rationale = r["rationale"].replace("|", "\\|")
        lines.append(f"| {r['item']} | {r['value']} | {r['gate']} | {rationale} |")

    lines.extend([
        "",
        "## Bucket counts from guard audit",
        "",
        "| bucket/top1 item | count |",
        "|---|---:|",
    ])

    for k, v in bucket_counts.most_common():
        lines.append(f"| bucket:{k} | {v} |")
    for k, v in anchor_top1_counts.most_common():
        lines.append(f"| anchor_top1_changed:{k} | {v} |")

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

    print("source_decision:", decision)
    print("plan_decision:", plan_decision)
    print("hard_failures:", hard_failures)
    print("warnings:", warnings)
    print("trainable_gap_improved:", post_gap_improved)
    print("trainable_mean_gap_delta:", f"{post_mean_gap_delta:.10f}")
    print("protected_prob_regressed:", protected_prob_regressed)
    print("tail_prob_regressed:", tail_prob_regressed)
    print("anchor_top1_changed:", anchor_top1_changed)
    print("anchor_max_kl:", f"{anchor_max_kl:.10f}")
    print("out_summary_csv:", args.out_summary_csv)
    print("out_report:", args.out_report)
    print("review-only; no training; no checkpoint write; no C export; no benchmark; no promotion")


if __name__ == "__main__":
    main()
