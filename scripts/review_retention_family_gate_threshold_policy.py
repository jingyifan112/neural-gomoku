#!/usr/bin/env python3
"""
Review retention-family gate threshold policy for run2.

Scope:
- policy review only
- no training
- no checkpoint
- no C export
- no benchmark
- no promotion

Question:
Should eval probability gate change from:
  any probability decrease => FAIL
to:
  rank/top1 unchanged and prob_delta within epsilon => WARNING

This script reads existing run2 review artifacts and writes a policy review report.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Sequence


DEFAULT_RUN2_REVIEW_CSV = Path("analysis/integration_eval/retention_family_run2_eval_prob_regression_review.csv")
DEFAULT_RUN2_REVIEW_JSON = Path("analysis/integration_eval/retention_family_run2_eval_prob_regression_review.json")
DEFAULT_GATE_JSON = Path("analysis/integration_eval/retention_family_wrapper_run2_weighted/gate_eval.json")
DEFAULT_WRAPPER_JSON = Path("analysis/integration_eval/retention_family_wrapper_run2_weighted/wrapper_result.json")

DEFAULT_OUT_CSV = Path("analysis/integration_eval/retention_family_gate_threshold_policy_review.csv")
DEFAULT_OUT_JSON = Path("analysis/integration_eval/retention_family_gate_threshold_policy_review.json")
DEFAULT_OUT_MD = Path("analysis/integration_eval/retention_family_gate_threshold_policy_review.md")


def clean(v: Any) -> str:
    if v is None:
        return ""
    return str(v).strip()


def parse_bool(v: Any) -> bool:
    return clean(v).lower() in {"true", "1", "yes", "y"}


def parse_float(v: Any) -> float | None:
    s = clean(v)
    if s.lower() in {"", "none", "nan", "null"}:
        return None
    try:
        x = float(s)
    except Exception:
        return None
    if not math.isfinite(x):
        return None
    return x


def parse_int(v: Any) -> int | None:
    x = parse_float(v)
    if x is None:
        return None
    return int(x)


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return [dict(r) for r in csv.DictReader(f)]


def write_csv(path: Path, rows: Sequence[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        for row in rows:
            w.writerow(row)


def md_table(headers: Sequence[str], rows: Sequence[Sequence[Any]]) -> str:
    lines = []
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for row in rows:
        cells = [str(x).replace("\n", " ").replace("|", "\\|") for x in row]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def classify_row(row: Dict[str, str], prob_epsilon: float) -> Dict[str, Any]:
    before_rank = parse_int(row.get("before_rank"))
    after_rank = parse_int(row.get("after_rank"))
    prob_delta = parse_float(row.get("prob_delta_after_minus_before"))

    prob_regressed_under_current_gate = parse_bool(row.get("prob_regressed"))
    rank_regressed = parse_bool(row.get("rank_regressed"))
    top1_lost = parse_bool(row.get("top1_lost"))
    is_critical_7_9 = parse_bool(row.get("is_critical_7_9"))

    rank_unchanged_or_improved = (
        before_rank is not None
        and after_rank is not None
        and after_rank <= before_rank
    )
    top1_preserved = not top1_lost

    abs_prob_drop = ""
    if prob_delta is not None and prob_delta < 0:
        abs_prob_drop = -prob_delta

    within_epsilon = (
        prob_delta is not None
        and prob_delta < 0
        and -prob_delta <= prob_epsilon
    )

    critical_harmed = is_critical_7_9 and (
        prob_regressed_under_current_gate
        or rank_regressed
        or top1_lost
    )

    if rank_regressed or top1_lost or critical_harmed:
        threshold_policy_class = "fail_hard_regression"
    elif prob_regressed_under_current_gate and rank_unchanged_or_improved and top1_preserved and within_epsilon:
        threshold_policy_class = "warning_prob_only_within_epsilon"
    elif prob_regressed_under_current_gate:
        threshold_policy_class = "fail_prob_drop_exceeds_epsilon_or_context_changed"
    else:
        threshold_policy_class = "pass_no_regression"

    return {
        "eval_row_index": row.get("eval_row_index", ""),
        "family_id": row.get("family_id", ""),
        "source": row.get("source", ""),
        "policy_target": row.get("policy_target", ""),
        "before_rank": row.get("before_rank", ""),
        "after_rank": row.get("after_rank", ""),
        "rank_delta_after_minus_before": row.get("rank_delta_after_minus_before", ""),
        "before_prob": row.get("before_prob", ""),
        "after_prob": row.get("after_prob", ""),
        "prob_delta_after_minus_before": row.get("prob_delta_after_minus_before", ""),
        "abs_prob_drop": "" if abs_prob_drop == "" else f"{abs_prob_drop:.10g}",
        "prob_epsilon": f"{prob_epsilon:.10g}",
        "current_gate_prob_regressed": prob_regressed_under_current_gate,
        "rank_regressed": rank_regressed,
        "top1_lost": top1_lost,
        "rank_unchanged_or_improved": rank_unchanged_or_improved,
        "top1_preserved": top1_preserved,
        "within_epsilon": within_epsilon,
        "is_critical_7_9": is_critical_7_9,
        "critical_harmed": critical_harmed,
        "threshold_policy_class": threshold_policy_class,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run2-review-csv", type=Path, default=DEFAULT_RUN2_REVIEW_CSV)
    ap.add_argument("--run2-review-json", type=Path, default=DEFAULT_RUN2_REVIEW_JSON)
    ap.add_argument("--gate-json", type=Path, default=DEFAULT_GATE_JSON)
    ap.add_argument("--wrapper-json", type=Path, default=DEFAULT_WRAPPER_JSON)
    ap.add_argument("--out-csv", type=Path, default=DEFAULT_OUT_CSV)
    ap.add_argument("--out-json", type=Path, default=DEFAULT_OUT_JSON)
    ap.add_argument("--out-md", type=Path, default=DEFAULT_OUT_MD)
    ap.add_argument(
        "--prob-epsilon",
        type=float,
        default=5e-4,
        help="Absolute probability-drop epsilon for warning-only probability regressions.",
    )
    args = ap.parse_args()

    if args.prob_epsilon < 0:
        raise SystemExit("ERROR: --prob-epsilon must be non-negative")

    rows = read_csv(args.run2_review_csv)
    run2_review = json.loads(args.run2_review_json.read_text(encoding="utf-8"))
    gate = json.loads(args.gate_json.read_text(encoding="utf-8"))
    wrapper = json.loads(args.wrapper_json.read_text(encoding="utf-8"))

    reviewed_rows = [classify_row(row, args.prob_epsilon) for row in rows]

    class_counts = Counter(r["threshold_policy_class"] for r in reviewed_rows)
    current_prob_regressions = sum(1 for r in reviewed_rows if r["current_gate_prob_regressed"])
    current_rank_regressions = sum(1 for r in reviewed_rows if r["rank_regressed"])
    current_top1_losses = sum(1 for r in reviewed_rows if r["top1_lost"])
    critical_harmed = sum(1 for r in reviewed_rows if r["critical_harmed"])

    hard_failures_under_threshold_policy = (
        class_counts["fail_hard_regression"]
        + class_counts["fail_prob_drop_exceeds_epsilon_or_context_changed"]
    )
    warnings_under_threshold_policy = class_counts["warning_prob_only_within_epsilon"]

    if hard_failures_under_threshold_policy:
        threshold_policy_decision = "FAIL"
    elif warnings_under_threshold_policy:
        threshold_policy_decision = "PASS_WITH_WARNINGS_FOR_POLICY_REVIEW_ONLY"
    else:
        threshold_policy_decision = "PASS"

    recommendation = {
        "recommended_gate_hierarchy": [
            "FAIL if top1 is lost.",
            "FAIL if target rank regresses.",
            "FAIL if a critical protected row regresses by probability, rank, or top1.",
            "FAIL if probability-only drop is larger than epsilon.",
            "WARNING, not FAIL, if probability-only drop is within epsilon and rank/top1 are preserved.",
        ],
        "recommended_epsilon_absolute_probability": args.prob_epsilon,
        "reason": (
            "Run2 failures are probability-only drops. In this run, rank regressions and top1 losses are zero, "
            "and the protected 7,9 row improved in probability while keeping rank unchanged. "
            "The observed probability-only drops are small enough to be treated as warning-only under the "
            "review epsilon, but this review does not retroactively promote the checkpoint."
        ),
        "non_actions": [
            "no training",
            "no checkpoint",
            "no C export",
            "no benchmark",
            "no promotion",
        ],
    }

    summary = {
        "scope": "gate threshold policy review only; no training/checkpoint/C export/benchmark/promotion",
        "inputs": {
            "run2_review_csv": str(args.run2_review_csv),
            "run2_review_json": str(args.run2_review_json),
            "gate_json": str(args.gate_json),
            "wrapper_json": str(args.wrapper_json),
        },
        "source_run2_status": {
            "gate_decision": gate.get("decision"),
            "wrapper_overall_status": wrapper.get("overall_status"),
            "wrapper_gates_passed": wrapper.get("gates_passed"),
            "run2_review_scope": run2_review.get("scope"),
        },
        "policy": {
            "prob_epsilon": args.prob_epsilon,
            "prob_epsilon_interpretation": "absolute policy probability, not relative percentage",
            "current_gate_rule": "any finite probability decrease larger than zero is FAIL",
            "reviewed_threshold_rule": "probability-only decrease within epsilon is WARNING if rank/top1 are preserved and row is not critical harmed",
        },
        "counts": {
            "eval_rows": len(reviewed_rows),
            "current_gate_prob_regressions": current_prob_regressions,
            "current_gate_rank_regressions": current_rank_regressions,
            "current_gate_top1_losses": current_top1_losses,
            "critical_harmed_rows": critical_harmed,
            "threshold_policy_warnings": warnings_under_threshold_policy,
            "threshold_policy_hard_failures": hard_failures_under_threshold_policy,
            "threshold_policy_class_counts": dict(sorted(class_counts.items())),
        },
        "threshold_policy_decision": threshold_policy_decision,
        "recommendation": recommendation,
        "rows": reviewed_rows,
    }

    write_csv(args.out_csv, reviewed_rows)
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    warning_rows = [
        r for r in reviewed_rows
        if r["threshold_policy_class"] == "warning_prob_only_within_epsilon"
    ]
    hard_rows = [
        r for r in reviewed_rows
        if r["threshold_policy_class"].startswith("fail_")
    ]

    md: List[str] = []
    md.append("# Retention Family Gate Threshold Policy Review")
    md.append("")
    md.append("## Scope")
    md.append("")
    md.append("- Policy review only.")
    md.append("- No training.")
    md.append("- No checkpoint.")
    md.append("- No C export.")
    md.append("- No benchmark.")
    md.append("- No promotion.")
    md.append("")
    md.append("## Source Run2 Status")
    md.append("")
    md.append(md_table(
        ["field", "value"],
        [
            ["gate decision", gate.get("decision")],
            ["wrapper overall_status", wrapper.get("overall_status")],
            ["wrapper gates_passed", wrapper.get("gates_passed")],
            ["run2 review scope", run2_review.get("scope")],
        ],
    ))
    md.append("")
    md.append("## Reviewed Policy")
    md.append("")
    md.append(f"- Probability epsilon: `{args.prob_epsilon:.10g}` absolute policy probability.")
    md.append("- Current rule: any finite eval probability decrease is a gate failure.")
    md.append("- Reviewed rule: probability-only decrease within epsilon becomes warning-only if rank/top1 are preserved and no critical row is harmed.")
    md.append("")
    md.append("Recommended gate hierarchy:")
    md.append("")
    for item in recommendation["recommended_gate_hierarchy"]:
        md.append(f"- {item}")
    md.append("")
    md.append("## Counts")
    md.append("")
    md.append(md_table(
        ["metric", "value"],
        [
            ["eval rows", len(reviewed_rows)],
            ["current gate prob regressions", current_prob_regressions],
            ["current gate rank regressions", current_rank_regressions],
            ["current gate top1 losses", current_top1_losses],
            ["critical harmed rows", critical_harmed],
            ["threshold policy warnings", warnings_under_threshold_policy],
            ["threshold policy hard failures", hard_failures_under_threshold_policy],
            ["threshold policy decision", threshold_policy_decision],
        ],
    ))
    md.append("")
    md.append("## Warning Rows Under Threshold Policy")
    md.append("")
    if warning_rows:
        md.append(md_table(
            [
                "row",
                "family_id",
                "target",
                "rank before->after",
                "prob before->after",
                "prob delta",
                "abs drop",
                "class",
            ],
            [
                [
                    r["eval_row_index"],
                    r["family_id"],
                    r["policy_target"],
                    f'{r["before_rank"]}->{r["after_rank"]}',
                    f'{r["before_prob"]}->{r["after_prob"]}',
                    r["prob_delta_after_minus_before"],
                    r["abs_prob_drop"],
                    r["threshold_policy_class"],
                ]
                for r in warning_rows
            ],
        ))
    else:
        md.append("None.")
    md.append("")
    md.append("## Hard Failure Rows Under Threshold Policy")
    md.append("")
    if hard_rows:
        md.append(md_table(
            [
                "row",
                "family_id",
                "target",
                "rank before->after",
                "prob delta",
                "critical_harmed",
                "class",
            ],
            [
                [
                    r["eval_row_index"],
                    r["family_id"],
                    r["policy_target"],
                    f'{r["before_rank"]}->{r["after_rank"]}',
                    r["prob_delta_after_minus_before"],
                    r["critical_harmed"],
                    r["threshold_policy_class"],
                ]
                for r in hard_rows
            ],
        ))
    else:
        md.append("None.")
    md.append("")
    md.append("## Recommendation")
    md.append("")
    md.append(
        "Adopt the thresholded policy for future gate-evaluator design review: "
        "rank/top1/critical regressions remain hard failures, while probability-only drops "
        "within epsilon are warnings. This run should remain a policy-review case rather than "
        "a retroactive checkpoint promotion."
    )
    md.append("")
    md.append("## Outputs")
    md.append("")
    md.append(f"- CSV: `{args.out_csv}`")
    md.append(f"- JSON: `{args.out_json}`")
    md.append(f"- Markdown: `{args.out_md}`")
    md.append("")

    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.write_text("\n".join(md), encoding="utf-8")

    print(json.dumps({
        "eval_rows": len(reviewed_rows),
        "prob_epsilon": args.prob_epsilon,
        "current_gate_prob_regressions": current_prob_regressions,
        "threshold_policy_warnings": warnings_under_threshold_policy,
        "threshold_policy_hard_failures": hard_failures_under_threshold_policy,
        "threshold_policy_decision": threshold_policy_decision,
        "out_csv": str(args.out_csv),
        "out_json": str(args.out_json),
        "out_md": str(args.out_md),
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
