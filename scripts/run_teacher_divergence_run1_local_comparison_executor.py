#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CORE_INPUTS = {
    "core_trainable_guard_reuse": "analysis/integration_eval/teacher_divergence_gated_training_run1_e10_trainable_gap_guard.csv",
    "core_protected_tail_guard_reuse": "analysis/integration_eval/teacher_divergence_gated_training_run1_e10_manifest_bucket_guard.csv",
    "core_anchor_drift_guard_reuse": "analysis/integration_eval/teacher_divergence_gated_training_run1_e10_anchor_drift_guard.csv",
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Dry-run local comparison executor for run1 candidate vs current_best."
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
    p.add_argument("--execute", action="store_true", help="Intentionally disabled in this dry-run branch.")
    p.add_argument(
        "--out-combined-csv",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_local_comparison_executor_dryrun_combined_summary.csv"),
    )
    p.add_argument(
        "--out-decision-json",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_local_comparison_executor_dryrun_decision.json"),
    )
    p.add_argument(
        "--out-decision-csv",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_local_comparison_executor_dryrun_decision.csv"),
    )
    p.add_argument(
        "--out-commands",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_local_comparison_executor_dryrun_commands.txt"),
    )
    p.add_argument(
        "--out-report",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_local_comparison_executor_dryrun_report.md"),
    )
    return p.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def by_metric(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {r["metric"]: r for r in rows}


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


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def csv_row(metric: str, value: Any, status: str, notes: str = "") -> dict[str, str]:
    return {
        "metric": metric,
        "value": str(value),
        "status": status,
        "notes": notes,
    }


def combined_row(section: str, rows: int, metric: str, value: Any, status: str, notes: str = "") -> dict[str, str]:
    return {
        "section": section,
        "rows": str(rows),
        "metric": metric,
        "value": str(value),
        "status": status,
        "notes": notes,
    }


def summarize_trainable(path: Path) -> tuple[list[dict[str, str]], dict[str, Any]]:
    rows = read_csv(path)
    gap_improved = sum(int_field(r, "gap_improved") for r in rows)
    target_prob_improved = sum(int_field(r, "target_prob_improved") for r in rows)
    rank_regressed = sum(int_field(r, "target_rank_regressed") for r in rows)
    gap_delta = mean([float_field(r, "gap_delta") for r in rows])

    combined = [
        combined_row("trainable_guard_reuse", len(rows), "gap_improved_rows", gap_improved, "PASS" if gap_improved == 44 else "FAIL"),
        combined_row("trainable_guard_reuse", len(rows), "target_prob_improved_rows", target_prob_improved, "INFO"),
        combined_row("trainable_guard_reuse", len(rows), "target_rank_regressed_rows", rank_regressed, "PASS" if rank_regressed == 0 else "FAIL"),
        combined_row("trainable_guard_reuse", len(rows), "mean_gap_delta", f"{gap_delta:.10f}", "PASS" if gap_delta > 0 else "FAIL"),
    ]
    metrics = {
        "trainable_rows": len(rows),
        "trainable_gap_improved": gap_improved,
        "trainable_target_prob_improved": target_prob_improved,
        "trainable_rank_regressed": rank_regressed,
        "trainable_mean_gap_delta": gap_delta,
    }
    return combined, metrics


def summarize_bucket(path: Path) -> tuple[list[dict[str, str]], dict[str, Any]]:
    rows = read_csv(path)
    evaluated = [r for r in rows if r.get("status") == "evaluated"]
    protected = [r for r in evaluated if r.get("ready_bucket") == "protected_top10"]
    tail = [r for r in evaluated if r.get("ready_bucket") == "tail_rank_gt50"]

    protected_rank_regressed = sum(int_field(r, "target_rank_regressed") for r in protected)
    protected_prob_regressed = sum(int_field(r, "target_prob_regressed") for r in protected)
    tail_rank_regressed = sum(int_field(r, "target_rank_regressed") for r in tail)
    tail_prob_regressed = sum(int_field(r, "target_prob_regressed") for r in tail)

    combined = [
        combined_row("protected_tail_guard_reuse", len(rows), "evaluated_rows", len(evaluated), "PASS" if len(evaluated) == 89 else "WARN"),
        combined_row("protected_tail_guard_reuse", len(protected), "protected_top10_rank_regressed_rows", protected_rank_regressed, "PASS" if protected_rank_regressed == 0 else "FAIL"),
        combined_row("protected_tail_guard_reuse", len(protected), "protected_top10_prob_regressed_rows", protected_prob_regressed, "WARN" if protected_prob_regressed else "PASS"),
        combined_row("protected_tail_guard_reuse", len(tail), "tail_rank_gt50_rank_regressed_rows", tail_rank_regressed, "PASS" if tail_rank_regressed == 0 else "WARN"),
        combined_row("protected_tail_guard_reuse", len(tail), "tail_rank_gt50_prob_regressed_rows", tail_prob_regressed, "WARN" if tail_prob_regressed else "PASS"),
    ]
    metrics = {
        "bucket_rows": len(rows),
        "bucket_evaluated": len(evaluated),
        "protected_rows": len(protected),
        "protected_rank_regressed": protected_rank_regressed,
        "protected_prob_regressed": protected_prob_regressed,
        "tail_rows": len(tail),
        "tail_rank_regressed": tail_rank_regressed,
        "tail_prob_regressed": tail_prob_regressed,
    }
    return combined, metrics


def summarize_anchor(path: Path) -> tuple[list[dict[str, str]], dict[str, Any]]:
    rows = read_csv(path)
    top1_changed = sum(int_field(r, "top1_changed") for r in rows)
    kl_values = [float_field(r, "kl_ref_to_candidate") for r in rows]
    mean_kl = mean(kl_values)
    max_kl = max(kl_values) if kl_values else 0.0

    combined = [
        combined_row("anchor_drift_guard_reuse", len(rows), "anchor_top1_changed_rows", top1_changed, "PASS" if top1_changed == 0 else "FAIL"),
        combined_row("anchor_drift_guard_reuse", len(rows), "anchor_mean_kl", f"{mean_kl:.10f}", "INFO"),
        combined_row("anchor_drift_guard_reuse", len(rows), "anchor_max_kl", f"{max_kl:.10f}", "PASS" if max_kl <= 0.005 else "FAIL"),
    ]
    metrics = {
        "anchor_rows": len(rows),
        "anchor_top1_changed": top1_changed,
        "anchor_mean_kl": mean_kl,
        "anchor_max_kl": max_kl,
    }
    return combined, metrics


def main() -> None:
    args = parse_args()

    if args.execute:
        raise RuntimeError("Execute mode is intentionally disabled in this dry-run branch.")

    for p in [args.adapter_selection, args.adapter_design_summary, args.current_best_checkpoint]:
        if not p.exists():
            raise FileNotFoundError(p)

    selection = read_csv(args.adapter_selection)
    design_summary = by_metric(read_csv(args.adapter_design_summary))

    design_decision = design_summary.get("design_decision", {}).get("value", "")
    candidate_exists = args.candidate_checkpoint.exists()
    current_best_exists = args.current_best_checkpoint.exists()

    selected = [r for r in selection if r.get("selected_for_initial_executor") == "1"]
    adapter_counts = Counter(r.get("adapter_kind", "") for r in selected)

    blockers: list[str] = []
    warnings: list[str] = []

    if design_decision != "READY_TO_IMPLEMENT_LOCAL_COMPARISON_EXECUTOR":
        blockers.append(f"adapter design is not ready: {design_decision}")
    if not current_best_exists:
        blockers.append("current_best checkpoint missing")
    if not candidate_exists:
        blockers.append("candidate checkpoint missing locally")
    if adapter_counts.get("core_trainable_guard_reuse", 0) != 1:
        blockers.append("core trainable guard output not selected exactly once")
    if adapter_counts.get("core_protected_tail_guard_reuse", 0) != 1:
        blockers.append("core protected/tail guard output not selected exactly once")
    if adapter_counts.get("core_anchor_drift_guard_reuse", 0) != 1:
        blockers.append("core anchor drift guard output not selected exactly once")

    direct_selected = [r for r in selected if r.get("adapter_kind", "").startswith("direct_model_eval_")]
    if direct_selected:
        warnings.append(f"direct model-eval inputs selected but not executed in dry-run: {len(direct_selected)}")

    combined_rows: list[dict[str, str]] = []
    metrics: dict[str, Any] = {}

    for adapter_kind, path_str in CORE_INPUTS.items():
        path = Path(path_str)
        if not path.exists():
            blockers.append(f"missing core input: {path}")
            continue

        if adapter_kind == "core_trainable_guard_reuse":
            rows, m = summarize_trainable(path)
        elif adapter_kind == "core_protected_tail_guard_reuse":
            rows, m = summarize_bucket(path)
        elif adapter_kind == "core_anchor_drift_guard_reuse":
            rows, m = summarize_anchor(path)
        else:
            rows, m = [], {}

        combined_rows.extend(rows)
        metrics.update(m)

    fail_rows = [r for r in combined_rows if r["status"] == "FAIL"]
    warn_rows = [r for r in combined_rows if r["status"] == "WARN"]

    if fail_rows:
        blockers.append(f"combined reused guard output has FAIL rows: {len(fail_rows)}")
    if warn_rows:
        warnings.append(f"combined reused guard output has WARN rows: {len(warn_rows)}")

    executor_decision = "LOCAL_COMPARISON_DRYRUN_READY" if not blockers else "LOCAL_COMPARISON_DRYRUN_BLOCKED"

    args.out_combined_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.out_combined_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["section", "rows", "metric", "value", "status", "notes"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(combined_rows)

    decision = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "mode": "dry_run",
        "execute_requested": False,
        "would_train": False,
        "would_eval_model": False,
        "would_write_checkpoint": False,
        "would_c_export": False,
        "would_public_benchmark": False,
        "would_promote": False,
        "executor_decision": executor_decision,
        "blockers": blockers,
        "warnings": warnings,
        "design_decision": design_decision,
        "candidate_checkpoint_exists_locally": candidate_exists,
        "current_best_exists": current_best_exists,
        "selected_inputs": [
            {
                "adapter_kind": r.get("adapter_kind", ""),
                "comparison_action": r.get("comparison_action", ""),
                "path": r.get("path", ""),
                "stage_class": r.get("stage_class", ""),
                "sample_rows_or_count": r.get("sample_rows_or_count", ""),
            }
            for r in selected
        ],
        "metrics": metrics,
    }

    args.out_decision_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_decision_json.write_text(json.dumps(decision, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    decision_rows = [
        csv_row("executor_decision", executor_decision, "PASS" if not blockers else "FAIL", "; ".join(blockers)),
        csv_row("mode", "dry_run", "PASS"),
        csv_row("execute_requested", 0, "PASS"),
        csv_row("would_train", 0, "PASS"),
        csv_row("would_eval_model", 0, "PASS"),
        csv_row("would_write_checkpoint", 0, "PASS"),
        csv_row("would_c_export", 0, "PASS"),
        csv_row("would_public_benchmark", 0, "PASS"),
        csv_row("would_promote", 0, "PASS"),
        csv_row("blocker_count", len(blockers), "PASS" if not blockers else "FAIL", "; ".join(blockers)),
        csv_row("warning_count", len(warnings), "WARN" if warnings else "PASS", "; ".join(warnings)),
        csv_row("selected_inputs", len(selected), "INFO"),
        csv_row("direct_model_eval_inputs_selected", len(direct_selected), "INFO"),
        csv_row("candidate_checkpoint_exists_locally", int(candidate_exists), "PASS" if candidate_exists else "FAIL"),
        csv_row("current_best_exists", int(current_best_exists), "PASS" if current_best_exists else "FAIL"),
    ]

    for key, value in metrics.items():
        decision_rows.append(csv_row(key, value, "INFO"))

    with args.out_decision_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["metric", "value", "status", "notes"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(decision_rows)

    commands = [
        "# Teacher-divergence run1 local comparison executor dry-run commands",
        "# Dry-run only. No model eval, no C export, no public benchmark, no promotion.",
        "",
        "## Inputs reused in this dry-run",
    ]
    for r in selected:
        commands.append(f"- {r.get('adapter_kind', '')}: {r.get('path', '')}")
    commands.extend([
        "",
        "## Next implementation branch may add model eval for direct_model_eval inputs only.",
        "## This branch only reuses already-computed run1 guard outputs.",
        "",
    ])
    args.out_commands.write_text("\n".join(commands), encoding="utf-8")

    lines = [
        "# Teacher-divergence run1 local comparison executor dry-run",
        "",
        "## Branch",
        "",
        "`exp/15x15-teacher-divergence-run1-local-comparison-executor-dryrun`",
        "",
        "## Scope",
        "",
        "- Implements a dry-run local comparison executor.",
        "- Reuses already-computed run1 guard outputs.",
        "- Does not run model eval.",
        "- Does not train.",
        "- Does not read or write checkpoints.",
        "- Does not overwrite `checkpoints/15x15_current_best.pt`.",
        "- Does not C export.",
        "- Does not run public benchmark.",
        "- Does not promote.",
        "",
        "## Executor decision",
        "",
        f"`{executor_decision}`",
        "",
        "## Safety flags",
        "",
        "| flag | value |",
        "|---|---:|",
        "| mode | dry_run |",
        "| execute_requested | 0 |",
        "| would_train | 0 |",
        "| would_eval_model | 0 |",
        "| would_write_checkpoint | 0 |",
        "| would_c_export | 0 |",
        "| would_public_benchmark | 0 |",
        "| would_promote | 0 |",
        "",
        "## Combined reused guard summary",
        "",
        "| section | rows | metric | value | status | notes |",
        "|---|---:|---|---:|---|---|",
    ]

    for r in combined_rows:
        notes = r["notes"].replace("|", "\\|")
        lines.append(f"| {r['section']} | {r['rows']} | {r['metric']} | {r['value']} | {r['status']} | {notes} |")

    lines.extend([
        "",
        "## Selected inputs",
        "",
        "| adapter_kind | action | path | rows/count |",
        "|---|---|---|---:|",
    ])

    for r in selected:
        lines.append(
            f"| {r.get('adapter_kind', '')} | {r.get('comparison_action', '')} | `{r.get('path', '')}` | {r.get('sample_rows_or_count', '')} |"
        )

    lines.extend([
        "",
        "## Blockers",
        "",
    ])
    if blockers:
        for item in blockers:
            lines.append(f"- {item}")
    else:
        lines.append("- None.")

    lines.extend([
        "",
        "## Warnings",
        "",
    ])
    if warnings:
        for item in warnings:
            lines.append(f"- {item}")
    else:
        lines.append("- None.")

    lines.extend([
        "",
        "## Interpretation",
        "",
        "This dry-run executor confirms that the already-computed run1 trainable, protected/tail, and anchor guard outputs can be reused as a local comparison baseline.",
        "",
        "It does not yet perform additional fixed-probe model evaluation. A later branch may add controlled model-eval support only for selected direct-ready inputs.",
        "",
        "## Outputs",
        "",
        f"- combined summary CSV: `{args.out_combined_csv}`",
        f"- decision JSON: `{args.out_decision_json}`",
        f"- decision CSV: `{args.out_decision_csv}`",
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

    print("executor_decision:", executor_decision)
    print("blocker_count:", len(blockers))
    print("warning_count:", len(warnings))
    print("selected_inputs:", len(selected))
    print("direct_model_eval_inputs_selected:", len(direct_selected))
    print("trainable_rows:", metrics.get("trainable_rows", ""))
    print("trainable_gap_improved:", metrics.get("trainable_gap_improved", ""))
    print("protected_rank_regressed:", metrics.get("protected_rank_regressed", ""))
    print("tail_rank_regressed:", metrics.get("tail_rank_regressed", ""))
    print("anchor_top1_changed:", metrics.get("anchor_top1_changed", ""))
    print("out_combined_csv:", args.out_combined_csv)
    print("out_decision_json:", args.out_decision_json)
    print("out_decision_csv:", args.out_decision_csv)
    print("out_commands:", args.out_commands)
    print("out_report:", args.out_report)
    print("dry-run only; no model eval; no training; no checkpoint read/write; no C export; no benchmark; no promotion")


if __name__ == "__main__":
    main()
