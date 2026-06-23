#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any


DIRECT_READY = "DIRECT_PROBE_EVAL_ADAPTER_DRYRUN_READY"
CORE_READY = "NO_DIRECT_PROBE_INPUTS__READY_FOR_CORE_REUSE_LOCAL_DECISION"
BLOCKED = "DIRECT_PROBE_EVAL_ADAPTER_BLOCKED"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Route next step after run1 direct-probe eval adapter dry-run/plan."
    )
    p.add_argument(
        "--adapter-summary",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_direct_probe_eval_adapter_summary.csv"),
    )
    p.add_argument(
        "--adapter-manifest",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_direct_probe_eval_adapter_manifest.csv"),
    )
    p.add_argument(
        "--controlled-review-summary",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_local_comparison_controlled_review_summary.csv"),
    )
    p.add_argument(
        "--out-summary-csv",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_post_adapter_route_decision_summary.csv"),
    )
    p.add_argument(
        "--out-next-plan",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_post_adapter_route_decision_next_plan.txt"),
    )
    p.add_argument(
        "--out-report",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_post_adapter_route_decision.md"),
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


def row(metric: str, value: Any, status: str, notes: str = "") -> dict[str, str]:
    return {
        "metric": metric,
        "value": str(value),
        "status": status,
        "notes": notes,
    }


def main() -> None:
    args = parse_args()

    for p in [args.adapter_summary, args.adapter_manifest, args.controlled_review_summary]:
        if not p.exists():
            raise FileNotFoundError(p)

    adapter_summary = by_metric(read_csv(args.adapter_summary))
    controlled_summary = by_metric(read_csv(args.controlled_review_summary))
    manifest = read_csv(args.adapter_manifest)

    adapter_decision = get_value(adapter_summary, "adapter_decision")
    adapter_blocker_count = as_int(get_value(adapter_summary, "blocker_count"))
    adapter_warning_count = as_int(get_value(adapter_summary, "warning_count"))
    core_reuse_inputs = as_int(get_value(adapter_summary, "core_reuse_inputs"))
    direct_ready_inputs = as_int(get_value(adapter_summary, "direct_ready_inputs_from_selection"))
    manifest_rows_reported = as_int(get_value(adapter_summary, "manifest_rows"))
    controlled_review_decision = get_value(controlled_summary, "review_decision")

    blockers: list[str] = []
    warnings: list[str] = []

    if adapter_blocker_count > 0:
        blockers.append(f"adapter blockers present: {adapter_blocker_count}")
    if core_reuse_inputs != 3:
        blockers.append(f"core reuse inputs not 3: {core_reuse_inputs}")
    if manifest_rows_reported != len(manifest):
        blockers.append(f"manifest row mismatch: summary={manifest_rows_reported}, csv={len(manifest)}")

    if adapter_warning_count > 0:
        warnings.append(f"adapter warnings carried forward: {adapter_warning_count}")

    if adapter_decision == DIRECT_READY:
        if direct_ready_inputs <= 0 or len(manifest) <= 0:
            blockers.append("adapter decision says direct ready, but manifest/direct-ready count is empty")
        route_decision = "ROUTE_TO_CONTROLLED_DIRECT_PROBE_EVAL_EXECUTOR_DRYRUN"
        next_branch = "exp/15x15-teacher-divergence-run1-direct-probe-eval-executor-dryrun"
        next_action = "Implement controlled direct-probe local eval executor in dry-run mode first."
    elif adapter_decision == CORE_READY:
        route_decision = "ROUTE_TO_CORE_REUSE_LOCAL_DECISION_REPORT"
        next_branch = "exp/15x15-teacher-divergence-run1-core-reuse-local-decision"
        next_action = "Build a core-reuse local decision report from already-computed guard outputs; do not run model eval."
    elif adapter_decision == BLOCKED:
        route_decision = "ROUTE_BLOCKED_FIX_ADAPTER_BLOCKERS"
        next_branch = "none"
        next_action = "Fix adapter blockers before continuing."
        blockers.append("adapter decision is blocked")
    else:
        route_decision = "ROUTE_BLOCKED_UNKNOWN_ADAPTER_DECISION"
        next_branch = "none"
        next_action = "Inspect adapter summary; unknown adapter_decision."
        blockers.append(f"unknown adapter_decision: {adapter_decision}")

    if blockers:
        final_route_decision = "POST_ADAPTER_ROUTE_BLOCKED"
    else:
        final_route_decision = route_decision

    summary_rows = [
        row("final_route_decision", final_route_decision, "INFO", "Route only; no model eval."),
        row("route_decision", route_decision, "INFO"),
        row("next_branch", next_branch, "INFO"),
        row("next_action", next_action, "INFO"),
        row("blocker_count", len(blockers), "PASS" if not blockers else "FAIL", "; ".join(blockers)),
        row("warning_count", len(warnings), "WARN" if warnings else "PASS", "; ".join(warnings)),
        row("adapter_decision", adapter_decision, "INFO"),
        row("adapter_blocker_count", adapter_blocker_count, "PASS" if adapter_blocker_count == 0 else "FAIL"),
        row("adapter_warning_count", adapter_warning_count, "WARN" if adapter_warning_count else "PASS"),
        row("controlled_review_decision", controlled_review_decision, "INFO"),
        row("core_reuse_inputs", core_reuse_inputs, "PASS" if core_reuse_inputs == 3 else "FAIL"),
        row("direct_ready_inputs_from_selection", direct_ready_inputs, "INFO"),
        row("manifest_rows", len(manifest), "INFO"),
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

    next_plan = [
        "# Teacher-divergence run1 post-adapter route decision next plan",
        "",
        f"final_route_decision={final_route_decision}",
        f"adapter_decision={adapter_decision}",
        f"next_branch={next_branch}",
        "",
        "## Next action",
        "",
        next_action,
        "",
        "## Required guardrails",
        "",
        "- No training.",
        "- No checkpoint write.",
        "- No current_best overwrite.",
        "- No C export.",
        "- No public benchmark.",
        "- No promotion.",
        "- Do not add local checkpoint artifacts to git.",
        "",
        "## If direct-probe executor is next",
        "",
        "The executor must default to dry-run and require both explicit flags before any local model eval:",
        "",
        "```text",
        "--execute-model-eval",
        "--confirm-model-eval TEACHER_DIVERGENCE_DIRECT_PROBE_LOCAL_EVAL",
        "```",
        "",
        "## Blockers",
        "",
    ]

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

    args.out_next_plan.parent.mkdir(parents=True, exist_ok=True)
    args.out_next_plan.write_text("\n".join(next_plan) + "\n", encoding="utf-8")

    report = [
        "# Teacher-divergence run1 post-adapter route decision",
        "",
        "## Branch",
        "",
        "`exp/15x15-teacher-divergence-run1-post-adapter-route-decision`",
        "",
        "## Scope",
        "",
        "- Routes the next step after direct-probe eval adapter dry-run/plan.",
        "- Reads adapter decision and manifest.",
        "- Does not train.",
        "- Does not run model eval.",
        "- Does not read checkpoint contents.",
        "- Does not write checkpoints.",
        "- Does not overwrite `checkpoints/15x15_current_best.pt`.",
        "- Does not C export.",
        "- Does not run public benchmark.",
        "- Does not promote.",
        "",
        "## Final route decision",
        "",
        f"`{final_route_decision}`",
        "",
        "## Next branch",
        "",
        f"`{next_branch}`",
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
        "## Direct-probe manifest rows",
        "",
        "| eval_manifest_id | adapter_kind | stage | path | rows/count |",
        "|---|---|---|---|---:|",
    ])

    if manifest:
        for r in manifest:
            report.append(
                f"| {r.get('eval_manifest_id', '')} | {r.get('adapter_kind', '')} | {r.get('stage_class', '')} | `{r.get('path', '')}` | {r.get('sample_rows_or_count', '')} |"
            )
    else:
        report.append("| none |  |  |  |  |")

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
        "## Recommendation",
        "",
        next_action,
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

    print("final_route_decision:", final_route_decision)
    print("route_decision:", route_decision)
    print("next_branch:", next_branch)
    print("adapter_decision:", adapter_decision)
    print("blocker_count:", len(blockers))
    print("warning_count:", len(warnings))
    print("core_reuse_inputs:", core_reuse_inputs)
    print("direct_ready_inputs_from_selection:", direct_ready_inputs)
    print("manifest_rows:", len(manifest))
    print("out_summary_csv:", args.out_summary_csv)
    print("out_next_plan:", args.out_next_plan)
    print("out_report:", args.out_report)
    print("route only; no model eval; no training; no checkpoint read/write; no C export; no benchmark; no promotion")


if __name__ == "__main__":
    main()
