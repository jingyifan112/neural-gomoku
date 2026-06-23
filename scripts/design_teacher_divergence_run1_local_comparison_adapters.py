#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path
from typing import Any


CORE_GUARD_OUTPUTS = {
    "analysis/integration_eval/teacher_divergence_gated_training_run1_e10_trainable_gap_guard.csv": "core_trainable_guard_reuse",
    "analysis/integration_eval/teacher_divergence_gated_training_run1_e10_manifest_bucket_guard.csv": "core_protected_tail_guard_reuse",
    "analysis/integration_eval/teacher_divergence_gated_training_run1_e10_anchor_drift_guard.csv": "core_anchor_drift_guard_reuse",
}

DIRECT_STAGE_PRIORITY = {
    "fixed_probe_candidate": 1,
    "heldout_candidate": 2,
    "anchor_candidate": 3,
    "dataset_related": 4,
    "benchmark_related": 5,
    "guard_related": 6,
    "run1_output": 7,
    "related": 8,
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Design local comparison adapters from fixed-probe/heldout input inventory."
    )
    p.add_argument(
        "--inventory-csv",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_fixed_probe_heldout_input_inventory.csv"),
    )
    p.add_argument(
        "--input-audit-summary",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_fixed_probe_heldout_input_audit_summary.csv"),
    )
    p.add_argument(
        "--plan-summary",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_fixed_probe_heldout_plan_summary.csv"),
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
        "--out-selection-csv",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_local_comparison_adapter_selection.csv"),
    )
    p.add_argument(
        "--out-summary-csv",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_local_comparison_adapter_design_summary.csv"),
    )
    p.add_argument(
        "--out-commands",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_local_comparison_adapter_design_commands.txt"),
    )
    p.add_argument(
        "--out-report",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_local_comparison_adapter_design.md"),
    )
    return p.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def by_metric(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {r["metric"]: r for r in rows}


def get_value(rows_by_metric: dict[str, dict[str, str]], key: str, default: str = "") -> str:
    return rows_by_metric.get(key, {}).get("value", default)


def int_value(value: str) -> int:
    if value == "":
        return 0
    return int(float(value))


def row(metric: str, value: Any, status: str, notes: str = "") -> dict[str, str]:
    return {
        "metric": metric,
        "value": str(value),
        "status": status,
        "notes": notes,
    }


def adapter_kind_for_inventory_row(r: dict[str, str]) -> tuple[str, str, str]:
    path = r["path"]
    ready = r["schema_ready_kind"]
    stage = r["stage_class"]

    if path in CORE_GUARD_OUTPUTS:
        return CORE_GUARD_OUTPUTS[path], "reuse_already_computed", "Run1 wrapper already compared candidate vs current_best."

    if ready == "direct_model_eval_ready":
        if stage in {"fixed_probe_candidate", "heldout_candidate", "anchor_candidate"}:
            return f"direct_model_eval_{stage}", "candidate_vs_current_best_eval", "Has board/side/target; can be evaluated directly."
        return "direct_model_eval_lower_priority", "candidate_vs_current_best_eval_optional", "Direct-ready but lower-priority stage."

    if ready == "already_compared_guard_output":
        return "guard_output_reuse_optional", "reuse_already_computed", "Already contains probability/rank deltas."

    if ready == "needs_board_join_adapter":
        return "board_join_adapter_needed", "defer_adapter", "Has target but needs board/source join before model eval."

    if ready == "needs_target_adapter":
        return "target_adapter_needed", "defer_adapter", "Has board/side but needs target extraction policy."

    return "not_selected", "not_directly_evaluable", "Not enough schema information for local comparison."


def selection_priority(r: dict[str, str]) -> tuple[int, int, str]:
    path = r["path"]
    adapter_kind = r["adapter_kind"]
    stage = r["stage_class"]

    if path in CORE_GUARD_OUTPUTS:
        return (0, 0, path)
    if adapter_kind.startswith("direct_model_eval_"):
        return (1, DIRECT_STAGE_PRIORITY.get(stage, 99), path)
    if adapter_kind == "guard_output_reuse_optional":
        return (2, DIRECT_STAGE_PRIORITY.get(stage, 99), path)
    if adapter_kind in {"board_join_adapter_needed", "target_adapter_needed"}:
        return (3, DIRECT_STAGE_PRIORITY.get(stage, 99), path)
    return (9, DIRECT_STAGE_PRIORITY.get(stage, 99), path)


def main() -> None:
    args = parse_args()

    for p in [args.inventory_csv, args.input_audit_summary, args.plan_summary, args.current_best_checkpoint]:
        if not p.exists():
            raise FileNotFoundError(p)

    inventory = read_csv(args.inventory_csv)
    input_summary = by_metric(read_csv(args.input_audit_summary))
    plan_summary = by_metric(read_csv(args.plan_summary))

    input_plan_decision = get_value(input_summary, "plan_decision")
    upstream_plan_decision = get_value(plan_summary, "plan_decision")
    candidate_exists = args.candidate_checkpoint.exists()
    current_best_exists = args.current_best_checkpoint.exists()

    selections: list[dict[str, str]] = []
    for inv in inventory:
        adapter_kind, action, rationale = adapter_kind_for_inventory_row(inv)
        selected = adapter_kind in {
            "core_trainable_guard_reuse",
            "core_protected_tail_guard_reuse",
            "core_anchor_drift_guard_reuse",
        } or adapter_kind.startswith("direct_model_eval_")

        if adapter_kind == "direct_model_eval_lower_priority":
            # Include in design inventory, but mark optional.
            selected = False

        selection = dict(inv)
        selection.update({
            "adapter_kind": adapter_kind,
            "comparison_action": action,
            "selected_for_initial_executor": "1" if selected else "0",
            "selection_rationale": rationale,
        })
        selections.append(selection)

    selections.sort(key=selection_priority)

    args.out_selection_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.out_selection_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(selections[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(selections)

    selected = [r for r in selections if r["selected_for_initial_executor"] == "1"]
    core_selected = [r for r in selected if r["adapter_kind"].startswith("core_")]
    direct_selected = [r for r in selected if r["adapter_kind"].startswith("direct_model_eval_")]
    deferred = [r for r in selections if r["comparison_action"] == "defer_adapter"]
    optional_reuse = [r for r in selections if r["adapter_kind"] == "guard_output_reuse_optional"]

    adapter_counts = Counter(r["adapter_kind"] for r in selections)
    action_counts = Counter(r["comparison_action"] for r in selections)
    selected_stage_counts = Counter(r["stage_class"] for r in selected)

    blockers: list[str] = []
    warnings: list[str] = []

    if input_plan_decision != "READY_TO_IMPLEMENT_LOCAL_COMPARISON_ADAPTERS":
        blockers.append(f"input audit decision is not ready: {input_plan_decision}")
    if upstream_plan_decision not in {
        "READY_TO_DESIGN_FIXED_PROBE_HELDOUT_WITH_WARNINGS",
        "READY_TO_DESIGN_FIXED_PROBE_HELDOUT",
    }:
        blockers.append(f"fixed-probe/heldout plan decision is not ready: {upstream_plan_decision}")
    if not current_best_exists:
        blockers.append("current_best checkpoint missing")
    if not candidate_exists:
        blockers.append("run1 candidate checkpoint missing locally")
    if len(core_selected) < 3:
        blockers.append(f"core guard outputs selected {len(core_selected)} < 3")
    if not direct_selected:
        warnings.append("no direct model-eval fixed-probe/heldout inputs selected for initial executor")
    if deferred:
        warnings.append(f"deferred adapter inputs present: {len(deferred)}")
    if optional_reuse:
        warnings.append(f"optional already-compared guard outputs present: {len(optional_reuse)}")

    design_decision = "READY_TO_IMPLEMENT_LOCAL_COMPARISON_EXECUTOR" if not blockers else "LOCAL_COMPARISON_ADAPTER_DESIGN_BLOCKED"

    summary_rows = [
        row("design_decision", design_decision, "INFO", "Adapter design only; no model eval."),
        row("blocker_count", len(blockers), "PASS" if not blockers else "FAIL", "; ".join(blockers)),
        row("warning_count", len(warnings), "WARN" if warnings else "PASS", "; ".join(warnings)),
        row("input_audit_plan_decision", input_plan_decision, "PASS" if input_plan_decision == "READY_TO_IMPLEMENT_LOCAL_COMPARISON_ADAPTERS" else "FAIL"),
        row("fixed_probe_heldout_plan_decision", upstream_plan_decision, "PASS" if upstream_plan_decision in {"READY_TO_DESIGN_FIXED_PROBE_HELDOUT_WITH_WARNINGS", "READY_TO_DESIGN_FIXED_PROBE_HELDOUT"} else "FAIL"),
        row("candidate_checkpoint_exists_locally", int(candidate_exists), "PASS" if candidate_exists else "FAIL", "Local artifact only; do not add to git."),
        row("current_best_exists", int(current_best_exists), "PASS" if current_best_exists else "FAIL"),
        row("inventory_rows", len(inventory), "INFO"),
        row("selection_rows", len(selections), "INFO"),
        row("selected_for_initial_executor", len(selected), "INFO"),
        row("core_guard_outputs_selected", len(core_selected), "PASS" if len(core_selected) == 3 else "FAIL"),
        row("direct_model_eval_inputs_selected", len(direct_selected), "INFO"),
        row("deferred_adapter_inputs", len(deferred), "WARN" if deferred else "PASS"),
        row("optional_guard_reuse_inputs", len(optional_reuse), "INFO"),
    ]

    for adapter_kind, count in adapter_counts.most_common():
        summary_rows.append(row(f"adapter_kind:{adapter_kind}", count, "INFO"))

    args.out_summary_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.out_summary_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["metric", "value", "status", "notes"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(summary_rows)

    commands = [
        "# Teacher-divergence run1 local comparison adapter design command plan",
        "# Design only. Do not execute model comparison in this branch.",
        "",
        "## Intended next branch",
        "exp/15x15-teacher-divergence-run1-local-comparison-executor",
        "",
        "## Baseline/candidate checkpoints",
        f"baseline={args.current_best_checkpoint}",
        f"candidate={args.candidate_checkpoint}",
        "",
        "## Initial executor selected inputs",
    ]
    for r in selected:
        commands.append(f"- {r['adapter_kind']}: {r['path']}")

    commands.extend([
        "",
        "## Deferred adapter inputs",
    ])
    if deferred:
        for r in deferred[:50]:
            commands.append(f"- {r['adapter_kind']}: {r['path']}")
    else:
        commands.append("- none")

    commands.extend([
        "",
        "## Initial executor responsibilities",
        "- Reuse core run1 guard outputs as already-computed comparison rows.",
        "- Evaluate selected direct_model_eval inputs candidate vs current_best if any are present.",
        "- Produce combined local-comparison decision before any export/benchmark.",
        "- Preserve no current_best overwrite / no C export / no public benchmark / no promotion.",
        "",
    ])
    args.out_commands.write_text("\n".join(commands), encoding="utf-8")

    lines = [
        "# Teacher-divergence run1 local comparison adapter design",
        "",
        "## Branch",
        "",
        "`exp/15x15-teacher-divergence-run1-local-comparison-adapter-design`",
        "",
        "## Scope",
        "",
        "- Designs adapters for local candidate-vs-current_best comparison.",
        "- Uses input inventory from fixed-probe/heldout input audit.",
        "- Selects stable initial executor inputs.",
        "- Does not train.",
        "- Does not read or write checkpoints.",
        "- Does not overwrite `checkpoints/15x15_current_best.pt`.",
        "- Does not C export.",
        "- Does not run public benchmark.",
        "- Does not promote.",
        "",
        "## Decision",
        "",
        f"`{design_decision}`",
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
        "## Selected initial executor inputs",
        "",
        "| adapter_kind | action | stage | path | rows/count |",
        "|---|---|---|---|---:|",
    ])

    if selected:
        for r in selected:
            lines.append(
                f"| {r['adapter_kind']} | {r['comparison_action']} | {r['stage_class']} | `{r['path']}` | {r['sample_rows_or_count']} |"
            )
    else:
        lines.append("| none |  |  |  |  |")

    lines.extend([
        "",
        "## Adapter kind counts",
        "",
        "| adapter_kind | files |",
        "|---|---:|",
    ])
    for kind, count in adapter_counts.most_common():
        lines.append(f"| {kind} | {count} |")

    lines.extend([
        "",
        "## Action counts",
        "",
        "| action | files |",
        "|---|---:|",
    ])
    for action, count in action_counts.most_common():
        lines.append(f"| {action} | {count} |")

    lines.extend([
        "",
        "## Selected stage counts",
        "",
        "| stage | files |",
        "|---|---:|",
    ])
    for stage, count in selected_stage_counts.most_common():
        lines.append(f"| {stage} | {count} |")

    lines.extend([
        "",
        "## Deferred adapter inputs",
        "",
        "| adapter_kind | stage | path | reason |",
        "|---|---|---|---|",
    ])
    if deferred:
        for r in deferred[:50]:
            lines.append(
                f"| {r['adapter_kind']} | {r['stage_class']} | `{r['path']}` | {r['selection_rationale']} |"
            )
    else:
        lines.append("| none |  |  |  |")

    lines.extend([
        "",
        "## Recommended executor design",
        "",
        "The next branch should implement a local-comparison executor with two input classes:",
        "",
        "1. `reuse_already_computed`: load run1 guard CSVs and summarize candidate-vs-current_best results already computed by the wrapper.",
        "2. `candidate_vs_current_best_eval`: evaluate selected direct model-eval-ready files if any are stable enough for immediate use.",
        "",
        "The executor should produce:",
        "",
        "- combined comparison CSV",
        "- fixed-probe/heldout summary CSV",
        "- decision report",
        "",
        "Hard gates should remain local-only and should not trigger C export, public benchmark, or promotion.",
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
        "## Outputs",
        "",
        f"- selection CSV: `{args.out_selection_csv}`",
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

    print("design_decision:", design_decision)
    print("blocker_count:", len(blockers))
    print("warning_count:", len(warnings))
    print("inventory_rows:", len(inventory))
    print("selected_for_initial_executor:", len(selected))
    print("core_guard_outputs_selected:", len(core_selected))
    print("direct_model_eval_inputs_selected:", len(direct_selected))
    print("deferred_adapter_inputs:", len(deferred))
    print("out_selection_csv:", args.out_selection_csv)
    print("out_summary_csv:", args.out_summary_csv)
    print("out_commands:", args.out_commands)
    print("out_report:", args.out_report)
    print("adapter design only; no training; no checkpoint read/write; no C export; no benchmark; no promotion")


if __name__ == "__main__":
    main()
