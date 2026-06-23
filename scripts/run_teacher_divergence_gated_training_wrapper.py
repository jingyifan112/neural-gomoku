#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import shlex
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Dry-run executor wrapper for gated teacher-divergence training."
    )
    p.add_argument(
        "--wrapper-summary",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_gated_training_dryrun_wrapper_summary.csv"),
    )
    p.add_argument(
        "--dataset",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_round2_trainable_trainer_ready_dataset.json"),
    )
    p.add_argument(
        "--manifest",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_expanded_candidate_manifest_legacy_suppress_normalized.csv"),
    )
    p.add_argument(
        "--anchor-snapshots",
        type=Path,
        default=Path("analysis/public_benchmark_eval/corpus8_selected_board_snapshots.json"),
    )
    p.add_argument("--baseline-checkpoint", type=Path, default=Path("checkpoints/15x15_current_best.pt"))
    p.add_argument(
        "--candidate-checkpoint",
        type=Path,
        default=Path("checkpoints/15x15_teacher_divergence_round2_policy_margin_gated_review_e10.pt"),
    )
    p.add_argument(
        "--quarantine-checkpoint",
        type=Path,
        default=Path("checkpoints/quarantine/15x15_teacher_divergence_round2_policy_margin_gated_review_e10_FAILED.pt"),
    )
    p.add_argument("--epochs", type=int, default=10)
    p.add_argument("--lr", type=str, default="1e-6")
    p.add_argument("--margin", type=str, default="1.0")
    p.add_argument("--anchor-kl-weight", type=str, default="0.05")
    p.add_argument("--ce-weight", type=str, default="0.05")
    p.add_argument("--weight-decay", type=str, default="1e-5")
    p.add_argument("--seed", type=int, default=31)
    p.add_argument("--execute", action="store_true", help="Intentionally disabled in this dry-run branch.")
    p.add_argument(
        "--out-decision-json",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_gated_training_wrapper_dryrun_decision.json"),
    )
    p.add_argument(
        "--out-decision-csv",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_gated_training_wrapper_dryrun_decision.csv"),
    )
    p.add_argument(
        "--out-commands",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_gated_training_wrapper_dryrun_commands.txt"),
    )
    p.add_argument(
        "--out-report",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_gated_training_wrapper_dryrun_report.md"),
    )
    return p.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def by_item(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {r["item"]: r for r in rows}


def command(parts: list[str | Path | int | float]) -> str:
    return shlex.join([str(p) for p in parts])


def csv_row(item: str, value: Any, status: str, notes: str = "") -> dict[str, str]:
    return {
        "item": item,
        "value": str(value),
        "status": status,
        "notes": notes,
    }


def main() -> None:
    args = parse_args()

    if args.execute:
        raise RuntimeError(
            "Execute mode is intentionally disabled in this dry-run implementation branch. "
            "This branch validates wrapper logic only and must not start training."
        )

    required_paths = [
        args.wrapper_summary,
        args.dataset,
        args.manifest,
        args.anchor_snapshots,
        args.baseline_checkpoint,
        Path("scripts/train_rapfi_teacher_policy_margin.py"),
        Path("scripts/audit_teacher_divergence_tiny_posttrain_guards.py"),
    ]
    missing = [str(p) for p in required_paths if not p.exists()]

    wrapper_rows = read_csv(args.wrapper_summary)
    wrapper = by_item(wrapper_rows)

    expected_wrapper_ready = wrapper.get("allowed_to_design_wrapper", {}).get("value") == "1"
    expected_missing_paths_zero = wrapper.get("missing_required_paths", {}).get("value") == "0"
    source_decision = wrapper.get("source_closeout_decision", {}).get("value", "")
    plan_decision = wrapper.get("plan_decision", {}).get("value", "")

    train_log = Path("analysis/integration_eval/teacher_divergence_gated_training_dryrun_e10_train.log")
    trainable_guard = Path("analysis/integration_eval/teacher_divergence_gated_training_dryrun_e10_trainable_gap_guard.csv")
    bucket_guard = Path("analysis/integration_eval/teacher_divergence_gated_training_dryrun_e10_manifest_bucket_guard.csv")
    anchor_guard = Path("analysis/integration_eval/teacher_divergence_gated_training_dryrun_e10_anchor_drift_guard.csv")
    guard_report = Path("analysis/integration_eval/teacher_divergence_gated_training_dryrun_e10_guard_audit.md")
    wrapper_decision_json = Path("analysis/integration_eval/teacher_divergence_gated_training_dryrun_e10_wrapper_decision.json")
    wrapper_decision_csv = Path("analysis/integration_eval/teacher_divergence_gated_training_dryrun_e10_wrapper_decision.csv")
    wrapper_closeout = Path("analysis/integration_eval/teacher_divergence_gated_training_dryrun_e10_wrapper_closeout.md")

    train_cmd = command([
        "env",
        "PYTHONPATH=src",
        "python",
        "scripts/train_rapfi_teacher_policy_margin.py",
        "--dataset", args.dataset,
        "--anchor-snapshots", args.anchor_snapshots,
        "--init-checkpoint", args.baseline_checkpoint,
        "--reference-checkpoint", args.baseline_checkpoint,
        "--out-checkpoint", args.candidate_checkpoint,
        "--epochs", args.epochs,
        "--margin", args.margin,
        "--lr", args.lr,
        "--anchor-kl-weight", args.anchor_kl_weight,
        "--ce-weight", args.ce_weight,
        "--weight-decay", args.weight_decay,
        "--seed", args.seed,
        "--print-every", 1,
    ]) + f" | tee {shlex.quote(str(train_log))}"

    guard_cmd = command([
        "env",
        "PYTHONPATH=src",
        "python",
        "scripts/audit_teacher_divergence_tiny_posttrain_guards.py",
        "--baseline-checkpoint", args.baseline_checkpoint,
        "--candidate-checkpoint", args.candidate_checkpoint,
        "--trainer-ready-dataset", args.dataset,
        "--manifest", args.manifest,
        "--anchor-snapshots", args.anchor_snapshots,
        "--out-trainable-csv", trainable_guard,
        "--out-bucket-csv", bucket_guard,
        "--out-anchor-csv", anchor_guard,
        "--out-report", guard_report,
        "--expected-trainable", 44,
    ])

    hard_gates = {
        "trainable_rows_evaluated": "== 44",
        "trainable_gap_improved_rows": ">= 40",
        "trainable_mean_gap_delta": "> 0",
        "trainable_target_rank_regressions": "== 0",
        "protected_top10_target_rank_regressions": "== 0",
        "anchor_top1_changed_rows": "== 0",
        "anchor_max_kl_ref_to_candidate": "<= 0.005",
    }

    warning_gates = {
        "protected_top10_raw_probability_regressions": "warn if > 0; require epsilon-aware review",
        "tail_rank_gt50_raw_probability_regressions": "warn if > 0; require epsilon-aware review",
        "tail_rank_gt50_rank_regressions": "block uncontrolled scaling and inspect if > 0",
        "anchor_max_kl_ref_to_candidate": "warn if > 0.001 and <= 0.005",
    }

    candidate_preexisting = args.candidate_checkpoint.exists()
    quarantine_preexisting = args.quarantine_checkpoint.exists()

    blockers: list[str] = []
    warnings: list[str] = []

    if missing:
        blockers.append("missing required paths")
    if not expected_wrapper_ready:
        blockers.append("wrapper design summary does not allow design")
    if not expected_missing_paths_zero:
        blockers.append("wrapper design summary reported missing paths")
    if source_decision != "PASS_TO_GATED_TRAINING_REVIEW_WITH_WARNINGS":
        blockers.append(f"unexpected source decision: {source_decision}")
    if plan_decision != "READY_TO_DESIGN_GATED_TRAINING_DRYRUN":
        blockers.append(f"unexpected plan decision: {plan_decision}")
    if args.baseline_checkpoint == args.candidate_checkpoint:
        blockers.append("candidate checkpoint path equals baseline checkpoint path")
    if args.baseline_checkpoint.name == "15x15_current_best.pt" and args.candidate_checkpoint.name == "15x15_current_best.pt":
        blockers.append("candidate would overwrite current_best")
    if candidate_preexisting:
        warnings.append(f"candidate checkpoint already exists: {args.candidate_checkpoint}")
    if quarantine_preexisting:
        warnings.append(f"quarantine checkpoint already exists: {args.quarantine_checkpoint}")

    executor_decision = "DRY_RUN_READY_FOR_CONTROLLED_EXECUTION" if not blockers else "DRY_RUN_BLOCKED"

    decision = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "mode": "dry_run",
        "execute_requested": bool(args.execute),
        "would_train": False,
        "would_write_checkpoint": False,
        "would_move_checkpoint": False,
        "would_delete_checkpoint": False,
        "executor_decision": executor_decision,
        "blockers": blockers,
        "warnings": warnings,
        "source_closeout_decision": source_decision,
        "plan_decision": plan_decision,
        "paths": {
            "baseline_checkpoint": str(args.baseline_checkpoint),
            "candidate_checkpoint": str(args.candidate_checkpoint),
            "quarantine_checkpoint": str(args.quarantine_checkpoint),
            "dataset": str(args.dataset),
            "manifest": str(args.manifest),
            "anchor_snapshots": str(args.anchor_snapshots),
        },
        "planned_outputs": {
            "train_log": str(train_log),
            "trainable_guard": str(trainable_guard),
            "bucket_guard": str(bucket_guard),
            "anchor_guard": str(anchor_guard),
            "guard_report": str(guard_report),
            "wrapper_decision_json": str(wrapper_decision_json),
            "wrapper_decision_csv": str(wrapper_decision_csv),
            "wrapper_closeout": str(wrapper_closeout),
        },
        "commands": {
            "train": train_cmd,
            "guard": guard_cmd,
        },
        "hard_gates": hard_gates,
        "warning_gates": warning_gates,
        "checkpoint_policy": {
            "on_pass": "keep isolated candidate checkpoint only; do not promote",
            "on_fail": f"quarantine candidate to {args.quarantine_checkpoint} if it exists",
            "never": [
                "overwrite checkpoints/15x15_current_best.pt",
                "C export",
                "public benchmark",
                "promotion",
                "git add checkpoint artifacts",
            ],
        },
    }

    args.out_decision_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_decision_json.write_text(json.dumps(decision, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    rows = [
        csv_row("executor_decision", executor_decision, "PASS" if not blockers else "FAIL", "; ".join(blockers)),
        csv_row("mode", "dry_run", "PASS"),
        csv_row("execute_requested", int(args.execute), "PASS" if not args.execute else "FAIL"),
        csv_row("would_train", 0, "PASS"),
        csv_row("would_write_checkpoint", 0, "PASS"),
        csv_row("would_move_checkpoint", 0, "PASS"),
        csv_row("would_delete_checkpoint", 0, "PASS"),
        csv_row("source_closeout_decision", source_decision, "INFO"),
        csv_row("plan_decision", plan_decision, "INFO"),
        csv_row("missing_required_paths", len(missing), "PASS" if not missing else "FAIL", "; ".join(missing)),
        csv_row("blocker_count", len(blockers), "PASS" if not blockers else "FAIL", "; ".join(blockers)),
        csv_row("warning_count", len(warnings), "WARN" if warnings else "PASS", "; ".join(warnings)),
        csv_row("baseline_checkpoint", args.baseline_checkpoint, "INFO", "must never be overwritten"),
        csv_row("candidate_checkpoint", args.candidate_checkpoint, "INFO", "isolated candidate only"),
        csv_row("quarantine_checkpoint", args.quarantine_checkpoint, "INFO", "failure path only"),
        csv_row("candidate_checkpoint_preexisting", int(candidate_preexisting), "WARN" if candidate_preexisting else "PASS"),
        csv_row("quarantine_checkpoint_preexisting", int(quarantine_preexisting), "WARN" if quarantine_preexisting else "PASS"),
        csv_row("epochs", args.epochs, "INFO"),
        csv_row("lr", args.lr, "INFO"),
        csv_row("margin", args.margin, "INFO"),
        csv_row("anchor_kl_weight", args.anchor_kl_weight, "INFO"),
        csv_row("ce_weight", args.ce_weight, "INFO"),
        csv_row("weight_decay", args.weight_decay, "INFO"),
        csv_row("seed", args.seed, "INFO"),
    ]

    with args.out_decision_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["item", "value", "status", "notes"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    command_lines = [
        "# Teacher-divergence gated training wrapper dry-run commands",
        "# Generated by scripts/run_teacher_divergence_gated_training_wrapper.py",
        "# Do not execute automatically in this branch.",
        "",
        "## Planned training command",
        train_cmd,
        "",
        "## Planned guard command",
        guard_cmd,
        "",
        "## Hard gates",
    ]
    for k, v in hard_gates.items():
        command_lines.append(f"- {k}: {v}")
    command_lines += [
        "",
        "## Warning gates",
    ]
    for k, v in warning_gates.items():
        command_lines.append(f"- {k}: {v}")
    command_lines += [
        "",
        "## Checkpoint policy",
        f"- pass: keep `{args.candidate_checkpoint}` as isolated candidate artifact only",
        f"- fail: quarantine to `{args.quarantine_checkpoint}` if candidate exists",
        "- never overwrite `checkpoints/15x15_current_best.pt`",
        "- never add checkpoint artifacts to git",
        "",
    ]
    args.out_commands.write_text("\n".join(command_lines), encoding="utf-8")

    lines = [
        "# Teacher-divergence gated training wrapper dry-run report",
        "",
        "## Branch",
        "",
        "`exp/15x15-teacher-divergence-gated-training-wrapper-dryrun`",
        "",
        "## Scope",
        "",
        "- Implements a dry-run executor frame for later gated training.",
        "- Validates wrapper preconditions, commands, hard gates, warning gates, and checkpoint policy.",
        "- Does not train.",
        "- Does not write checkpoints.",
        "- Does not move or delete checkpoints.",
        "- Does not overwrite `checkpoints/15x15_current_best.pt`.",
        "- Does not C export.",
        "- Does not run public benchmark.",
        "- Does not promote.",
        "",
        "## Executor decision",
        "",
        f"`{executor_decision}`",
        "",
        "## Dry-run safety flags",
        "",
        "| flag | value |",
        "|---|---:|",
        "| execute_requested | 0 |",
        "| would_train | 0 |",
        "| would_write_checkpoint | 0 |",
        "| would_move_checkpoint | 0 |",
        "| would_delete_checkpoint | 0 |",
        "",
        "## Preconditions",
        "",
        "| item | value |",
        "|---|---:|",
        f"| source closeout decision | {source_decision} |",
        f"| plan decision | {plan_decision} |",
        f"| missing required paths | {len(missing)} |",
        f"| blockers | {len(blockers)} |",
        f"| warnings | {len(warnings)} |",
        f"| candidate checkpoint preexisting | {int(candidate_preexisting)} |",
        f"| quarantine checkpoint preexisting | {int(quarantine_preexisting)} |",
        "",
        "## Planned training command",
        "",
        "```bash",
        train_cmd,
        "```",
        "",
        "## Planned guard command",
        "",
        "```bash",
        guard_cmd,
        "```",
        "",
        "## Hard gates",
        "",
        "| gate | threshold |",
        "|---|---|",
    ]
    for k, v in hard_gates.items():
        lines.append(f"| {k} | {v} |")

    lines += [
        "",
        "## Warning gates",
        "",
        "| gate | action |",
        "|---|---|",
    ]
    for k, v in warning_gates.items():
        lines.append(f"| {k} | {v} |")

    lines += [
        "",
        "## Checkpoint policy",
        "",
        f"- Baseline checkpoint: `{args.baseline_checkpoint}`",
        f"- Candidate checkpoint: `{args.candidate_checkpoint}`",
        f"- Quarantine checkpoint: `{args.quarantine_checkpoint}`",
        "- Pass action: keep candidate checkpoint isolated only.",
        "- Fail action: quarantine candidate checkpoint if it exists.",
        "- Never overwrite `checkpoints/15x15_current_best.pt`.",
        "- Never add checkpoint artifacts to git.",
        "",
        "## Blockers",
        "",
    ]
    if blockers:
        for b in blockers:
            lines.append(f"- {b}")
    else:
        lines.append("- None.")

    lines += [
        "",
        "## Warnings",
        "",
    ]
    if warnings:
        for w in warnings:
            lines.append(f"- {w}")
    else:
        lines.append("- None.")

    lines += [
        "",
        "## Outputs",
        "",
        f"- decision JSON: `{args.out_decision_json}`",
        f"- decision CSV: `{args.out_decision_csv}`",
        f"- command plan: `{args.out_commands}`",
        f"- report: `{args.out_report}`",
        "",
        "## Next step",
        "",
        "A later branch may add controlled execution mode. This branch remains dry-run only.",
        "",
        "## Final guardrails",
        "",
        "- No current_best overwrite.",
        "- No C export.",
        "- No public benchmark.",
        "- No promotion.",
        "- Do not add local checkpoint artifacts to git.",
        "",
    ]
    args.out_report.write_text("\n".join(lines), encoding="utf-8")

    print("executor_decision:", executor_decision)
    print("execute_requested:", int(args.execute))
    print("would_train:", 0)
    print("would_write_checkpoint:", 0)
    print("missing_required_paths:", len(missing))
    print("blocker_count:", len(blockers))
    print("warning_count:", len(warnings))
    print("out_decision_json:", args.out_decision_json)
    print("out_decision_csv:", args.out_decision_csv)
    print("out_commands:", args.out_commands)
    print("out_report:", args.out_report)
    print("dry-run only; no training; no checkpoint write; no C export; no benchmark; no promotion")


if __name__ == "__main__":
    main()
