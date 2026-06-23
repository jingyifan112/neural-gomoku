#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Epsilon-aware review of run1 protected/tail probability regressions."
    )
    p.add_argument(
        "--bucket-guard",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_gated_training_run1_e10_manifest_bucket_guard.csv"),
    )
    p.add_argument(
        "--promotion-readiness-summary",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_promotion_readiness_summary.csv"),
    )
    p.add_argument(
        "--out-detail-csv",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_epsilon_prob_regression_review.csv"),
    )
    p.add_argument(
        "--out-summary-csv",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_epsilon_prob_regression_summary.csv"),
    )
    p.add_argument(
        "--out-report",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_epsilon_prob_regression_review.md"),
    )
    p.add_argument("--noise-eps", type=float, default=1e-6)
    p.add_argument("--tiny-eps", type=float, default=1e-5)
    p.add_argument("--warn-eps", type=float, default=1e-4)
    return p.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def as_int(value: str) -> int:
    if value == "":
        return 0
    return int(float(value))


def as_float(value: str) -> float:
    if value == "":
        return 0.0
    return float(value)


def severity_for_delta(delta: float, noise_eps: float, tiny_eps: float, warn_eps: float) -> str:
    if delta >= 0:
        return "no_regression"
    loss = abs(delta)
    if loss <= noise_eps:
        return "numerical_noise"
    if loss <= tiny_eps:
        return "tiny_acceptable_drift"
    if loss <= warn_eps:
        return "warning"
    return "hard_concern"


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def min_or_zero(values: list[float]) -> float:
    return min(values) if values else 0.0


def max_or_zero(values: list[float]) -> float:
    return max(values) if values else 0.0


def row(metric: str, value: Any, status: str, notes: str = "") -> dict[str, str]:
    return {
        "metric": metric,
        "value": str(value),
        "status": status,
        "notes": notes,
    }


def main() -> None:
    args = parse_args()

    for p in [args.bucket_guard, args.promotion_readiness_summary]:
        if not p.exists():
            raise FileNotFoundError(p)

    bucket_rows = read_csv(args.bucket_guard)
    readiness_rows = read_csv(args.promotion_readiness_summary)
    readiness = {r["metric"]: r for r in readiness_rows}

    evaluated = [
        r for r in bucket_rows
        if r.get("status") == "evaluated"
        and r.get("ready_bucket") in {"protected_top10", "tail_rank_gt50"}
    ]

    details: list[dict[str, str]] = []
    for r in evaluated:
        bucket = r.get("ready_bucket", "")
        delta = as_float(r.get("target_prob_delta", "0"))
        rank_delta = as_int(r.get("target_rank_delta", "0"))
        prob_regressed = 1 if delta < 0 else 0
        loss = abs(delta) if delta < 0 else 0.0
        severity = severity_for_delta(delta, args.noise_eps, args.tiny_eps, args.warn_eps)

        details.append({
            "manifest_id": r.get("manifest_id", ""),
            "case_id": r.get("case_id", ""),
            "ready_bucket": bucket,
            "target_rc": r.get("target_rc", ""),
            "target_prob_before": r.get("target_prob_before", ""),
            "target_prob_after": r.get("target_prob_after", ""),
            "target_prob_delta": f"{delta:.12f}",
            "target_prob_loss": f"{loss:.12f}",
            "target_rank_before": r.get("target_rank_before", ""),
            "target_rank_after": r.get("target_rank_after", ""),
            "target_rank_delta": str(rank_delta),
            "target_prob_regressed": str(prob_regressed),
            "target_rank_regressed": str(1 if rank_delta > 0 else 0),
            "epsilon_severity": severity,
            "epsilon_pass": "1" if severity in {"no_regression", "numerical_noise", "tiny_acceptable_drift"} else "0",
        })

    args.out_detail_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.out_detail_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(details[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(details)

    by_bucket = defaultdict(list)
    for d in details:
        by_bucket[d["ready_bucket"]].append(d)

    severity_counts = Counter(d["epsilon_severity"] for d in details)
    bucket_severity_counts = Counter((d["ready_bucket"], d["epsilon_severity"]) for d in details)

    total_rows = len(details)
    total_regressions = sum(as_int(d["target_prob_regressed"]) for d in details)
    total_rank_regressions = sum(as_int(d["target_rank_regressed"]) for d in details)
    hard_concerns = severity_counts["hard_concern"]
    warning_rows = severity_counts["warning"]
    tiny_rows = severity_counts["tiny_acceptable_drift"]
    noise_rows = severity_counts["numerical_noise"]
    no_regression_rows = severity_counts["no_regression"]

    loss_values = [as_float(d["target_prob_loss"]) for d in details if as_int(d["target_prob_regressed"])]
    max_loss = max_or_zero(loss_values)
    mean_loss = mean(loss_values)

    protected = by_bucket["protected_top10"]
    tail = by_bucket["tail_rank_gt50"]

    protected_regressions = sum(as_int(d["target_prob_regressed"]) for d in protected)
    tail_regressions = sum(as_int(d["target_prob_regressed"]) for d in tail)

    protected_hard = sum(1 for d in protected if d["epsilon_severity"] == "hard_concern")
    tail_hard = sum(1 for d in tail if d["epsilon_severity"] == "hard_concern")
    protected_warning = sum(1 for d in protected if d["epsilon_severity"] == "warning")
    tail_warning = sum(1 for d in tail if d["epsilon_severity"] == "warning")

    # Promotion readiness stated run1 is not promotion-ready; this epsilon review can only decide next local gate.
    if total_rank_regressions > 0 or hard_concerns > 0:
        epsilon_decision = "EPSILON_REVIEW_FAILS__REPAIR_GATE_OR_OBJECTIVE"
    elif warning_rows > 0:
        epsilon_decision = "EPSILON_REVIEW_PASS_WITH_WARNINGS__NEEDS_FIXED_PROBE_HELDOUT"
    else:
        epsilon_decision = "EPSILON_REVIEW_PASS__READY_FOR_FIXED_PROBE_HELDOUT"

    summary_rows = [
        row("epsilon_decision", epsilon_decision, "INFO", "Local epsilon review decision; not promotion."),
        row("evaluated_rows", total_rows, "PASS" if total_rows == 89 else "WARN"),
        row("protected_top10_rows", len(protected), "PASS" if len(protected) == 23 else "WARN"),
        row("tail_rank_gt50_rows", len(tail), "PASS" if len(tail) == 66 else "WARN"),
        row("total_prob_regressions", total_regressions, "WARN" if total_regressions else "PASS"),
        row("protected_top10_prob_regressions", protected_regressions, "WARN" if protected_regressions else "PASS"),
        row("tail_rank_gt50_prob_regressions", tail_regressions, "WARN" if tail_regressions else "PASS"),
        row("total_rank_regressions", total_rank_regressions, "FAIL" if total_rank_regressions else "PASS"),
        row("no_regression_rows", no_regression_rows, "INFO"),
        row("numerical_noise_rows", noise_rows, "INFO"),
        row("tiny_acceptable_drift_rows", tiny_rows, "INFO"),
        row("warning_rows", warning_rows, "WARN" if warning_rows else "PASS"),
        row("hard_concern_rows", hard_concerns, "FAIL" if hard_concerns else "PASS"),
        row("protected_top10_warning_rows", protected_warning, "WARN" if protected_warning else "PASS"),
        row("tail_rank_gt50_warning_rows", tail_warning, "WARN" if tail_warning else "PASS"),
        row("protected_top10_hard_concern_rows", protected_hard, "FAIL" if protected_hard else "PASS"),
        row("tail_rank_gt50_hard_concern_rows", tail_hard, "FAIL" if tail_hard else "PASS"),
        row("max_probability_loss", f"{max_loss:.12f}", "FAIL" if max_loss > args.warn_eps else "WARN" if max_loss > args.tiny_eps else "PASS"),
        row("mean_probability_loss_among_regressions", f"{mean_loss:.12f}", "INFO"),
        row("noise_eps", args.noise_eps, "INFO"),
        row("tiny_eps", args.tiny_eps, "INFO"),
        row("warn_eps", args.warn_eps, "INFO"),
        row("promotion_readiness_decision", readiness.get("readiness_decision", {}).get("value", ""), "INFO"),
    ]

    args.out_summary_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.out_summary_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["metric", "value", "status", "notes"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(summary_rows)

    lines = [
        "# Teacher-divergence run1 epsilon-aware probability regression review",
        "",
        "## Branch",
        "",
        "`exp/15x15-teacher-divergence-run1-epsilon-prob-regression-review`",
        "",
        "## Scope",
        "",
        "- Reviews raw probability regressions from run1 protected/tail guard.",
        "- Classifies probability loss by epsilon bands.",
        "- Does not train.",
        "- Does not read or write checkpoints.",
        "- Does not overwrite `checkpoints/15x15_current_best.pt`.",
        "- Does not C export.",
        "- Does not run public benchmark.",
        "- Does not promote.",
        "",
        "## Epsilon bands",
        "",
        "| band | condition | interpretation |",
        "|---|---:|---|",
        f"| numerical_noise | loss <= {args.noise_eps:g} | likely numerical noise |",
        f"| tiny_acceptable_drift | loss <= {args.tiny_eps:g} | tiny drift, acceptable for local review |",
        f"| warning | loss <= {args.warn_eps:g} | warning; requires local fixed-probe/heldout before any export |",
        f"| hard_concern | loss > {args.warn_eps:g} | repair gate/objective before continuing |",
        "",
        "## Decision",
        "",
        f"`{epsilon_decision}`",
        "",
        "## Summary",
        "",
        "| metric | value | status | notes |",
        "|---|---:|---|---|",
    ]

    for r in summary_rows:
        notes = r["notes"].replace("|", "\\|")
        lines.append(f"| {r['metric']} | {r['value']} | {r['status']} | {notes} |")

    lines.extend([
        "",
        "## Severity counts",
        "",
        "| severity | rows |",
        "|---|---:|",
    ])
    for severity in ["no_regression", "numerical_noise", "tiny_acceptable_drift", "warning", "hard_concern"]:
        lines.append(f"| {severity} | {severity_counts[severity]} |")

    lines.extend([
        "",
        "## Bucket × severity counts",
        "",
        "| bucket | severity | rows |",
        "|---|---|---:|",
    ])
    for bucket in ["protected_top10", "tail_rank_gt50"]:
        for severity in ["no_regression", "numerical_noise", "tiny_acceptable_drift", "warning", "hard_concern"]:
            lines.append(f"| {bucket} | {severity} | {bucket_severity_counts[(bucket, severity)]} |")

    regressions = [d for d in details if as_int(d["target_prob_regressed"])]
    worst = sorted(regressions, key=lambda d: as_float(d["target_prob_loss"]), reverse=True)[:20]

    lines.extend([
        "",
        "## Worst raw probability regressions",
        "",
        "| bucket | manifest_id | case_id | prob_before | prob_after | prob_delta | loss | severity | rank_delta |",
        "|---|---|---|---:|---:|---:|---:|---|---:|",
    ])
    for d in worst:
        lines.append(
            f"| {d['ready_bucket']} | {d['manifest_id']} | {d['case_id']} | "
            f"{d['target_prob_before']} | {d['target_prob_after']} | {d['target_prob_delta']} | "
            f"{d['target_prob_loss']} | {d['epsilon_severity']} | {d['target_rank_delta']} |"
        )

    lines.extend([
        "",
        "## Interpretation",
        "",
    ])

    if epsilon_decision == "EPSILON_REVIEW_FAILS__REPAIR_GATE_OR_OBJECTIVE":
        lines.extend([
            "At least one hard concern or rank regression exists. Do not continue toward export or benchmark.",
            "",
            "Repair the gate/objective first, then rerun controlled training or guard audit.",
        ])
    elif epsilon_decision == "EPSILON_REVIEW_PASS_WITH_WARNINGS__NEEDS_FIXED_PROBE_HELDOUT":
        lines.extend([
            "No hard epsilon concern was found, but warning-level probability drift exists.",
            "",
            "The candidate remains not promotion-ready. The next step should be a local fixed-probe/heldout comparison against current_best, still without C export or public benchmark.",
        ])
    else:
        lines.extend([
            "All raw probability regressions are within tiny/noise bands.",
            "",
            "The candidate remains not promotion-ready, but can move to local fixed-probe/heldout comparison before any export or benchmark is considered.",
        ])

    lines.extend([
        "",
        "## Outputs",
        "",
        f"- detail CSV: `{args.out_detail_csv}`",
        f"- summary CSV: `{args.out_summary_csv}`",
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
    args.out_report.write_text("\n".join(lines), encoding="utf-8")

    print("epsilon_decision:", epsilon_decision)
    print("evaluated_rows:", total_rows)
    print("total_prob_regressions:", total_regressions)
    print("protected_prob_regressions:", protected_regressions)
    print("tail_prob_regressions:", tail_regressions)
    print("warning_rows:", warning_rows)
    print("hard_concern_rows:", hard_concerns)
    print("max_probability_loss:", f"{max_loss:.12f}")
    print("mean_probability_loss_among_regressions:", f"{mean_loss:.12f}")
    print("out_detail_csv:", args.out_detail_csv)
    print("out_summary_csv:", args.out_summary_csv)
    print("out_report:", args.out_report)
    print("review only; no training; no checkpoint write; no C export; no benchmark; no promotion")


if __name__ == "__main__":
    main()
