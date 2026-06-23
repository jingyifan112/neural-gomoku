#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any


REVIEW_READY_DIRECT = "READY_FOR_DIRECT_PROBE_EVAL_ADAPTER_WITH_WARNINGS"
REVIEW_READY_CORE = "READY_FOR_CORE_REUSE_LOCAL_DECISION_WITH_WARNINGS"
REVIEW_BLOCKED = "LOCAL_COMPARISON_CONTROLLED_REVIEW_BLOCKED"


MANIFEST_FIELDS = [
    "eval_manifest_id",
    "path",
    "adapter_kind",
    "comparison_action",
    "stage_class",
    "schema_ready_kind",
    "sample_rows_or_count",
    "has_board",
    "has_side",
    "has_target",
    "has_case_id",
    "dryrun_status",
    "future_executor_action",
    "future_execute_requires",
    "notes",
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Plan/dry-run direct-probe local eval adapter after run1 controlled review."
    )
    p.add_argument(
        "--controlled-review-summary",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_local_comparison_controlled_review_summary.csv"),
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
        "--out-manifest-csv",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_direct_probe_eval_adapter_manifest.csv"),
    )
    p.add_argument(
        "--out-summary-csv",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_direct_probe_eval_adapter_summary.csv"),
    )
    p.add_argument(
        "--out-commands",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_direct_probe_eval_adapter_commands.txt"),
    )
    p.add_argument(
        "--out-report",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_direct_probe_eval_adapter.md"),
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


def manifest_row(i: int, r: dict[str, str]) -> dict[str, str]:
    return {
        "eval_manifest_id": f"run1_direct_probe_eval_{i:03d}",
        "path": r.get("path", ""),
        "adapter_kind": r.get("adapter_kind", ""),
        "comparison_action": r.get("comparison_action", ""),
        "stage_class": r.get("stage_class", ""),
        "schema_ready_kind": r.get("schema_ready_kind", ""),
        "sample_rows_or_count": r.get("sample_rows_or_count", ""),
        "has_board": r.get("has_board", ""),
        "has_side": r.get("has_side", ""),
        "has_target": r.get("has_target", ""),
        "has_case_id": r.get("has_case_id", ""),
        "dryrun_status": "planned_only",
        "future_executor_action": "candidate_vs_current_best_local_model_eval",
        "future_execute_requires": "--execute-model-eval --confirm-model-eval TEACHER_DIVERGENCE_DIRECT_PROBE_LOCAL_EVAL",
        "notes": "Do not execute in this branch. No C export, no public benchmark, no promotion.",
    }


def main() -> None:
    args = parse_args()

    for p in [
        args.controlled_review_summary,
        args.adapter_selection,
        args.adapter_design_summary,
        args.current_best_checkpoint,
    ]:
        if not p.exists():
            raise FileNotFoundError(p)

    review = by_metric(read_csv(args.controlled_review_summary))
    design = by_metric(read_csv(args.adapter_design_summary))
    selection = read_csv(args.adapter_selection)

    review_decision = get_value(review, "review_decision")
    review_blocker_count = as_int(get_value(review, "review_blocker_count"))
    review_warning_count = as_int(get_value(review, "review_warning_count"))
    controlled_direct_count = as_int(get_value(review, "direct_model_eval_inputs_selected"))
    adapter_design_decision = get_value(design, "design_decision")
    adapter_design_direct_count = as_int(get_value(design, "direct_model_eval_inputs_selected"))
    adapter_design_deferred_count = as_int(get_value(design, "deferred_adapter_inputs"))

    candidate_exists = args.candidate_checkpoint.exists()
    current_best_exists = args.current_best_checkpoint.exists()

    selected = [r for r in selection if r.get("selected_for_initial_executor") == "1"]
    direct_ready = [
        r for r in selected
        if r.get("adapter_kind", "").startswith("direct_model_eval_")
    ]
    core_reuse = [
        r for r in selected
        if r.get("adapter_kind", "").startswith("core_")
    ]

    blockers: list[str] = []
    warnings: list[str] = []

    if review_decision == REVIEW_BLOCKED:
        blockers.append("controlled review is blocked")
    elif review_decision == REVIEW_READY_CORE:
        warnings.append("controlled review found no direct-ready model-eval inputs; core-reuse local decision is preferred")
    elif review_decision != REVIEW_READY_DIRECT:
        blockers.append(f"unexpected controlled review decision: {review_decision}")

    if review_blocker_count > 0:
        blockers.append(f"controlled review blockers present: {review_blocker_count}")
    if not current_best_exists:
        blockers.append("current_best checkpoint path missing")
    if not candidate_exists:
        blockers.append("run1 candidate checkpoint path missing locally")
    if len(core_reuse) != 3:
        blockers.append(f"core reuse inputs selected {len(core_reuse)} != 3")

    if review_decision == REVIEW_READY_DIRECT and not direct_ready:
        blockers.append("review says direct-probe adapter is ready, but no direct-ready selected rows were found")

    if review_warning_count > 0:
        warnings.append(f"controlled review warnings carried forward: {review_warning_count}")
    if adapter_design_deferred_count > 0:
        warnings.append(f"deferred adapter inputs remain: {adapter_design_deferred_count}")

    if blockers:
        adapter_decision = "DIRECT_PROBE_EVAL_ADAPTER_BLOCKED"
    elif direct_ready:
        adapter_decision = "DIRECT_PROBE_EVAL_ADAPTER_DRYRUN_READY"
    else:
        adapter_decision = "NO_DIRECT_PROBE_INPUTS__READY_FOR_CORE_REUSE_LOCAL_DECISION"

    manifest = [manifest_row(i + 1, r) for i, r in enumerate(direct_ready)]

    args.out_manifest_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.out_manifest_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=MANIFEST_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(manifest)

    summary_rows = [
        row("adapter_decision", adapter_decision, "INFO", "Dry-run/plan only; no model eval."),
        row("blocker_count", len(blockers), "PASS" if not blockers else "FAIL", "; ".join(blockers)),
        row("warning_count", len(warnings), "WARN" if warnings else "PASS", "; ".join(warnings)),
        row("controlled_review_decision", review_decision, "PASS" if review_decision in {REVIEW_READY_DIRECT, REVIEW_READY_CORE} else "FAIL"),
        row("controlled_review_blocker_count", review_blocker_count, "PASS" if review_blocker_count == 0 else "FAIL"),
        row("controlled_review_warning_count", review_warning_count, "WARN" if review_warning_count else "PASS"),
        row("adapter_design_decision", adapter_design_decision, "INFO"),
        row("adapter_design_direct_model_eval_inputs_selected", adapter_design_direct_count, "INFO"),
        row("adapter_design_deferred_adapter_inputs", adapter_design_deferred_count, "WARN" if adapter_design_deferred_count else "PASS"),
        row("candidate_checkpoint_exists_locally", int(candidate_exists), "PASS" if candidate_exists else "FAIL", "Existence only; do not add to git."),
        row("current_best_exists", int(current_best_exists), "PASS" if current_best_exists else "FAIL"),
        row("selected_inputs", len(selected), "INFO"),
        row("core_reuse_inputs", len(core_reuse), "PASS" if len(core_reuse) == 3 else "FAIL"),
        row("direct_ready_inputs_from_selection", len(direct_ready), "INFO"),
        row("controlled_review_direct_ready_inputs", controlled_direct_count, "INFO"),
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

    commands = [
        "# Teacher-divergence run1 direct-probe eval adapter command plan",
        "# Plan/dry-run only. Do not execute model eval in this branch.",
        "",
        f"adapter_decision={adapter_decision}",
        "",
        "## Candidate/baseline paths for a future executor",
        f"baseline={args.current_best_checkpoint}",
        f"candidate={args.candidate_checkpoint}",
        "",
        "## Future execution must require both flags",
        "--execute-model-eval",
        "--confirm-model-eval TEACHER_DIVERGENCE_DIRECT_PROBE_LOCAL_EVAL",
        "",
        "## Planned direct-ready inputs",
    ]
    if manifest:
        for r in manifest:
            commands.append(f"- {r['eval_manifest_id']}: {r['path']} ({r['adapter_kind']}, rows={r['sample_rows_or_count']})")
    else:
        commands.append("- none")

    commands.extend([
        "",
        "## Future executor must remain forbidden from",
        "- training",
        "- checkpoint write",
        "- current_best overwrite",
        "- C export",
        "- public benchmark",
        "- promotion",
        "",
    ])

    args.out_commands.write_text("\n".join(commands), encoding="utf-8")

    lines = [
        "# Teacher-divergence run1 direct-probe eval adapter dry-run",
        "",
        "## Branch",
        "",
        "`exp/15x15-teacher-divergence-run1-direct-probe-eval-adapter`",
        "",
        "## Scope",
        "",
        "- Plans a controlled direct-probe local model-eval adapter.",
        "- Reads controlled review and adapter selection outputs.",
        "- Does not train.",
        "- Does not run model eval.",
        "- Does not read checkpoint contents.",
        "- Does not write checkpoints.",
        "- Does not overwrite `checkpoints/15x15_current_best.pt`.",
        "- Does not C export.",
        "- Does not run public benchmark.",
        "- Does not promote.",
        "",
        "## Adapter decision",
        "",
        f"`{adapter_decision}`",
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
        "## Direct-ready eval manifest",
        "",
        "| eval_manifest_id | adapter_kind | stage | path | rows/count |",
        "|---|---|---|---|---:|",
    ])

    if manifest:
        for r in manifest:
            lines.append(
                f"| {r['eval_manifest_id']} | {r['adapter_kind']} | {r['stage_class']} | `{r['path']}` | {r['sample_rows_or_count']} |"
            )
    else:
        lines.append("| none |  |  |  |  |")

    lines.extend([
        "",
        "## Blockers",
        "",
    ])
    if blockers:
        for b in blockers:
            lines.append(f"- {b}")
    else:
        lines.append("- None.")

    lines.extend([
        "",
        "## Warnings",
        "",
    ])
    if warnings:
        for w in warnings:
            lines.append(f"- {w}")
    else:
        lines.append("- None.")

    lines.extend([
        "",
        "## Future executor requirements",
        "",
        "Any future model-eval executor must require both:",
        "",
        "```text",
        "--execute-model-eval",
        "--confirm-model-eval TEACHER_DIVERGENCE_DIRECT_PROBE_LOCAL_EVAL",
        "```",
        "",
        "It must output local comparison CSV/MD only and must not export C, run a public benchmark, or promote.",
        "",
        "## Recommendation",
        "",
    ])

    if adapter_decision == "DIRECT_PROBE_EVAL_ADAPTER_DRYRUN_READY":
        lines.append("Proceed to a separate controlled direct-probe local eval executor branch. Default must remain dry-run.")
    elif adapter_decision == "NO_DIRECT_PROBE_INPUTS__READY_FOR_CORE_REUSE_LOCAL_DECISION":
        lines.append("Do not build direct-probe eval yet. Proceed to a core-reuse local decision report.")
    else:
        lines.append("Do not proceed until blockers are resolved.")

    lines.extend([
        "",
        "## Outputs",
        "",
        f"- manifest CSV: `{args.out_manifest_csv}`",
        f"- summary CSV: `{args.out_summary_csv}`",
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
    args.out_report.write_text("\n".join(lines), encoding="utf-8")

    print("adapter_decision:", adapter_decision)
    print("blocker_count:", len(blockers))
    print("warning_count:", len(warnings))
    print("controlled_review_decision:", review_decision)
    print("core_reuse_inputs:", len(core_reuse))
    print("direct_ready_inputs_from_selection:", len(direct_ready))
    print("manifest_rows:", len(manifest))
    print("candidate_checkpoint_exists_locally:", int(candidate_exists))
    print("current_best_exists:", int(current_best_exists))
    print("out_manifest_csv:", args.out_manifest_csv)
    print("out_summary_csv:", args.out_summary_csv)
    print("out_commands:", args.out_commands)
    print("out_report:", args.out_report)
    print("dry-run/plan only; no model eval; no training; no checkpoint read/write; no C export; no benchmark; no promotion")


if __name__ == "__main__":
    main()
