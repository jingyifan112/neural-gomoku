#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import os
import shlex
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CONFIRM_TOKEN = "TEACHER_DIVERGENCE_GATED_TRAINING"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Controlled wrapper for gated teacher-divergence training. Defaults to dry-run."
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
    p.add_argument("--execute", action="store_true")
    p.add_argument("--confirm-execute", type=str, default="")
    p.add_argument("--allow-existing-candidate", action="store_true")
    p.add_argument(
        "--train-log",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_gated_training_dryrun_e10_train.log"),
    )
    p.add_argument(
        "--trainable-guard-csv",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_gated_training_dryrun_e10_trainable_gap_guard.csv"),
    )
    p.add_argument(
        "--bucket-guard-csv",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_gated_training_dryrun_e10_manifest_bucket_guard.csv"),
    )
    p.add_argument(
        "--anchor-guard-csv",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_gated_training_dryrun_e10_anchor_drift_guard.csv"),
    )
    p.add_argument(
        "--guard-report",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_gated_training_dryrun_e10_guard_audit.md"),
    )
    p.add_argument(
        "--out-decision-json",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_gated_training_wrapper_controlled_exec_review_decision.json"),
    )
    p.add_argument(
        "--out-decision-csv",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_gated_training_wrapper_controlled_exec_review_decision.csv"),
    )
    p.add_argument(
        "--out-commands",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_gated_training_wrapper_controlled_exec_review_commands.txt"),
    )
    p.add_argument(
        "--out-report",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_gated_training_wrapper_controlled_exec_review_report.md"),
    )
    p.add_argument("--min-gap-improved", type=int, default=40)
    p.add_argument("--max-anchor-kl", type=float, default=0.005)
    return p.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def by_item(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {r["item"]: r for r in rows}


def shell_cmd(parts: list[str | Path | int | float]) -> str:
    return shlex.join([str(p) for p in parts])


def csv_row(item: str, value: Any, status: str, notes: str = "") -> dict[str, str]:
    return {
        "item": item,
        "value": str(value),
        "status": status,
        "notes": notes,
    }


def run_logged(cmd: list[str], log_path: Path, env: dict[str, str]) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8") as log:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env)
        log.write(proc.stdout)
        print(proc.stdout, end="")
    if proc.returncode != 0:
        raise RuntimeError(f"command failed with code {proc.returncode}: {shell_cmd(cmd)}")


def run_plain(cmd: list[str], env: dict[str, str]) -> None:
    proc = subprocess.run(cmd, env=env)
    if proc.returncode != 0:
        raise RuntimeError(f"command failed with code {proc.returncode}: {shell_cmd(cmd)}")


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


def evaluate_guards(
    trainable_csv: Path,
    bucket_csv: Path,
    anchor_csv: Path,
    min_gap_improved: int,
    max_anchor_kl: float,
) -> tuple[dict[str, Any], list[str], list[str]]:
    trainable = read_csv(trainable_csv)
    bucket = read_csv(bucket_csv)
    anchors = read_csv(anchor_csv)

    hard_failures: list[str] = []
    warnings: list[str] = []

    trainable_rows = len(trainable)
    trainable_gap_improved = sum(int_field(r, "gap_improved") for r in trainable)
    trainable_rank_regressed = sum(int_field(r, "target_rank_regressed") for r in trainable)
    trainable_mean_gap_delta = (
        sum(float_field(r, "gap_delta") for r in trainable) / trainable_rows
        if trainable_rows
        else 0.0
    )

    evaluated_bucket = [r for r in bucket if r.get("status") == "evaluated"]
    protected = [r for r in evaluated_bucket if r.get("ready_bucket") == "protected_top10"]
    tail = [r for r in evaluated_bucket if r.get("ready_bucket") == "tail_rank_gt50"]

    protected_rank_regressed = sum(int_field(r, "target_rank_regressed") for r in protected)
    protected_prob_regressed = sum(int_field(r, "target_prob_regressed") for r in protected)
    tail_rank_regressed = sum(int_field(r, "target_rank_regressed") for r in tail)
    tail_prob_regressed = sum(int_field(r, "target_prob_regressed") for r in tail)

    anchor_top1_changed = sum(int_field(r, "top1_changed") for r in anchors)
    anchor_kl_values = [float_field(r, "kl_ref_to_candidate") for r in anchors]
    anchor_max_kl = max(anchor_kl_values) if anchor_kl_values else 0.0
    anchor_mean_kl = sum(anchor_kl_values) / len(anchor_kl_values) if anchor_kl_values else 0.0

    if trainable_rows != 44:
        hard_failures.append(f"trainable rows {trainable_rows} != 44")
    if trainable_gap_improved < min_gap_improved:
        hard_failures.append(f"trainable gap improved {trainable_gap_improved} < {min_gap_improved}")
    if trainable_mean_gap_delta <= 0:
        hard_failures.append(f"trainable mean gap delta {trainable_mean_gap_delta:.10f} <= 0")
    if trainable_rank_regressed != 0:
        hard_failures.append(f"trainable target rank regressions {trainable_rank_regressed} != 0")
    if protected_rank_regressed != 0:
        hard_failures.append(f"protected_top10 rank regressions {protected_rank_regressed} != 0")
    if anchor_top1_changed != 0:
        hard_failures.append(f"anchor top1 changed rows {anchor_top1_changed} != 0")
    if anchor_max_kl > max_anchor_kl:
        hard_failures.append(f"anchor max KL {anchor_max_kl:.10f} > {max_anchor_kl}")

    if protected_prob_regressed > 0:
        warnings.append(f"protected_top10 raw probability regressions {protected_prob_regressed}")
    if tail_prob_regressed > 0:
        warnings.append(f"tail_rank_gt50 raw probability regressions {tail_prob_regressed}")
    if tail_rank_regressed > 0:
        warnings.append(f"tail_rank_gt50 rank regressions {tail_rank_regressed}")

    metrics = {
        "trainable_rows": trainable_rows,
        "trainable_gap_improved": trainable_gap_improved,
        "trainable_mean_gap_delta": trainable_mean_gap_delta,
        "trainable_rank_regressed": trainable_rank_regressed,
        "protected_rows": len(protected),
        "protected_rank_regressed": protected_rank_regressed,
        "protected_prob_regressed": protected_prob_regressed,
        "tail_rows": len(tail),
        "tail_rank_regressed": tail_rank_regressed,
        "tail_prob_regressed": tail_prob_regressed,
        "anchor_rows": len(anchors),
        "anchor_top1_changed": anchor_top1_changed,
        "anchor_mean_kl": anchor_mean_kl,
        "anchor_max_kl": anchor_max_kl,
    }
    return metrics, hard_failures, warnings


def main() -> None:
    args = parse_args()

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

    wrapper_rows = read_csv(args.wrapper_summary) if args.wrapper_summary.exists() else []
    wrapper = by_item(wrapper_rows)

    source_decision = wrapper.get("source_closeout_decision", {}).get("value", "")
    plan_decision = wrapper.get("plan_decision", {}).get("value", "")
    expected_wrapper_ready = wrapper.get("allowed_to_design_wrapper", {}).get("value") == "1"
    expected_missing_paths_zero = wrapper.get("missing_required_paths", {}).get("value") == "0"

    train_cmd_list = [
        "python",
        "scripts/train_rapfi_teacher_policy_margin.py",
        "--dataset", str(args.dataset),
        "--anchor-snapshots", str(args.anchor_snapshots),
        "--init-checkpoint", str(args.baseline_checkpoint),
        "--reference-checkpoint", str(args.baseline_checkpoint),
        "--out-checkpoint", str(args.candidate_checkpoint),
        "--epochs", str(args.epochs),
        "--margin", str(args.margin),
        "--lr", str(args.lr),
        "--anchor-kl-weight", str(args.anchor_kl_weight),
        "--ce-weight", str(args.ce_weight),
        "--weight-decay", str(args.weight_decay),
        "--seed", str(args.seed),
        "--print-every", "1",
    ]

    guard_cmd_list = [
        "python",
        "scripts/audit_teacher_divergence_tiny_posttrain_guards.py",
        "--baseline-checkpoint", str(args.baseline_checkpoint),
        "--candidate-checkpoint", str(args.candidate_checkpoint),
        "--trainer-ready-dataset", str(args.dataset),
        "--manifest", str(args.manifest),
        "--anchor-snapshots", str(args.anchor_snapshots),
        "--out-trainable-csv", str(args.trainable_guard_csv),
        "--out-bucket-csv", str(args.bucket_guard_csv),
        "--out-anchor-csv", str(args.anchor_guard_csv),
        "--out-report", str(args.guard_report),
        "--expected-trainable", "44",
    ]

    train_shell = "env PYTHONPATH=src " + shell_cmd(train_cmd_list) + f" | tee {shlex.quote(str(args.train_log))}"
    guard_shell = "env PYTHONPATH=src " + shell_cmd(guard_cmd_list)

    hard_gates = {
        "trainable_rows": "== 44",
        "trainable_gap_improved": f">= {args.min_gap_improved}",
        "trainable_mean_gap_delta": "> 0",
        "trainable_rank_regressed": "== 0",
        "protected_top10_rank_regressed": "== 0",
        "anchor_top1_changed": "== 0",
        "anchor_max_kl": f"<= {args.max_anchor_kl}",
    }

    warning_gates = {
        "protected_top10_raw_probability_regressions": "warn if > 0",
        "tail_rank_gt50_raw_probability_regressions": "warn if > 0",
        "tail_rank_gt50_rank_regressions": "warn/block uncontrolled scaling if > 0",
    }

    preflight_blockers: list[str] = []
    preflight_warnings: list[str] = []

    if missing:
        preflight_blockers.append("missing required paths")
    if not expected_wrapper_ready:
        preflight_blockers.append("wrapper summary does not report allowed_to_design_wrapper=1")
    if not expected_missing_paths_zero:
        preflight_blockers.append("wrapper summary does not report missing_required_paths=0")
    if source_decision != "PASS_TO_GATED_TRAINING_REVIEW_WITH_WARNINGS":
        preflight_blockers.append(f"unexpected source decision: {source_decision}")
    if plan_decision != "READY_TO_DESIGN_GATED_TRAINING_DRYRUN":
        preflight_blockers.append(f"unexpected plan decision: {plan_decision}")
    if args.baseline_checkpoint == args.candidate_checkpoint:
        preflight_blockers.append("candidate checkpoint path equals baseline checkpoint path")
    if args.candidate_checkpoint.name == "15x15_current_best.pt":
        preflight_blockers.append("candidate checkpoint would overwrite current_best")
    if args.execute and args.confirm_execute != CONFIRM_TOKEN:
        preflight_blockers.append(f"--execute requires --confirm-execute {CONFIRM_TOKEN}")
    if args.execute and args.candidate_checkpoint.exists() and not args.allow_existing_candidate:
        preflight_blockers.append("candidate checkpoint already exists; refuse overwrite without --allow-existing-candidate")

    if args.candidate_checkpoint.exists():
        preflight_warnings.append(f"candidate checkpoint already exists: {args.candidate_checkpoint}")
    if args.quarantine_checkpoint.exists():
        preflight_warnings.append(f"quarantine checkpoint already exists: {args.quarantine_checkpoint}")

    mode = "execute" if args.execute else "dry_run"
    executed_training = False
    executed_guard = False
    moved_to_quarantine = False
    final_hard_failures: list[str] = list(preflight_blockers)
    final_warnings: list[str] = list(preflight_warnings)
    guard_metrics: dict[str, Any] = {}

    if args.execute and not preflight_blockers:
        env = os.environ.copy()
        old_pythonpath = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = "src" if not old_pythonpath else f"src:{old_pythonpath}"

        args.candidate_checkpoint.parent.mkdir(parents=True, exist_ok=True)
        args.train_log.parent.mkdir(parents=True, exist_ok=True)

        run_logged(train_cmd_list, args.train_log, env)
        executed_training = True

        run_plain(guard_cmd_list, env)
        executed_guard = True

        guard_metrics, guard_failures, guard_warnings = evaluate_guards(
            args.trainable_guard_csv,
            args.bucket_guard_csv,
            args.anchor_guard_csv,
            args.min_gap_improved,
            args.max_anchor_kl,
        )
        final_hard_failures.extend(guard_failures)
        final_warnings.extend(guard_warnings)

        if guard_failures and args.candidate_checkpoint.exists():
            args.quarantine_checkpoint.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(args.candidate_checkpoint), str(args.quarantine_checkpoint))
            moved_to_quarantine = True
    else:
        guard_metrics = {
            "trainable_rows": "",
            "trainable_gap_improved": "",
            "trainable_mean_gap_delta": "",
            "trainable_rank_regressed": "",
            "protected_rank_regressed": "",
            "anchor_top1_changed": "",
            "anchor_max_kl": "",
        }

    if args.execute:
        executor_decision = "EXECUTION_PASS_KEEP_ISOLATED_CANDIDATE" if not final_hard_failures else "EXECUTION_FAIL_CANDIDATE_QUARANTINED_OR_BLOCKED"
    else:
        executor_decision = "DRY_RUN_READY_FOR_CONTROLLED_EXECUTION" if not preflight_blockers else "DRY_RUN_BLOCKED"

    decision = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "mode": mode,
        "execute_requested": bool(args.execute),
        "confirm_execute_valid": args.confirm_execute == CONFIRM_TOKEN,
        "executed_training": executed_training,
        "executed_guard": executed_guard,
        "moved_to_quarantine": moved_to_quarantine,
        "executor_decision": executor_decision,
        "preflight_blockers": preflight_blockers,
        "preflight_warnings": preflight_warnings,
        "final_hard_failures": final_hard_failures,
        "final_warnings": final_warnings,
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
            "train_log": str(args.train_log),
            "trainable_guard_csv": str(args.trainable_guard_csv),
            "bucket_guard_csv": str(args.bucket_guard_csv),
            "anchor_guard_csv": str(args.anchor_guard_csv),
            "guard_report": str(args.guard_report),
        },
        "commands": {
            "train": train_shell,
            "guard": guard_shell,
        },
        "hard_gates": hard_gates,
        "warning_gates": warning_gates,
        "guard_metrics": guard_metrics,
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
        csv_row("executor_decision", executor_decision, "PASS" if not final_hard_failures else "FAIL", "; ".join(final_hard_failures)),
        csv_row("mode", mode, "INFO"),
        csv_row("execute_requested", int(args.execute), "INFO"),
        csv_row("confirm_execute_valid", int(args.confirm_execute == CONFIRM_TOKEN), "INFO"),
        csv_row("executed_training", int(executed_training), "PASS" if not args.execute else "INFO"),
        csv_row("executed_guard", int(executed_guard), "PASS" if not args.execute else "INFO"),
        csv_row("moved_to_quarantine", int(moved_to_quarantine), "PASS" if not moved_to_quarantine else "INFO"),
        csv_row("preflight_blocker_count", len(preflight_blockers), "PASS" if not preflight_blockers else "FAIL", "; ".join(preflight_blockers)),
        csv_row("preflight_warning_count", len(preflight_warnings), "WARN" if preflight_warnings else "PASS", "; ".join(preflight_warnings)),
        csv_row("final_hard_failure_count", len(final_hard_failures), "PASS" if not final_hard_failures else "FAIL", "; ".join(final_hard_failures)),
        csv_row("final_warning_count", len(final_warnings), "WARN" if final_warnings else "PASS", "; ".join(final_warnings)),
        csv_row("baseline_checkpoint", args.baseline_checkpoint, "INFO", "must never be overwritten"),
        csv_row("candidate_checkpoint", args.candidate_checkpoint, "INFO", "isolated candidate only"),
        csv_row("quarantine_checkpoint", args.quarantine_checkpoint, "INFO", "failure path only"),
        csv_row("epochs", args.epochs, "INFO"),
        csv_row("lr", args.lr, "INFO"),
        csv_row("margin", args.margin, "INFO"),
        csv_row("anchor_kl_weight", args.anchor_kl_weight, "INFO"),
        csv_row("ce_weight", args.ce_weight, "INFO"),
        csv_row("weight_decay", args.weight_decay, "INFO"),
        csv_row("seed", args.seed, "INFO"),
        csv_row("trainable_rows", guard_metrics.get("trainable_rows", ""), "INFO"),
        csv_row("trainable_gap_improved", guard_metrics.get("trainable_gap_improved", ""), "INFO"),
        csv_row("trainable_mean_gap_delta", guard_metrics.get("trainable_mean_gap_delta", ""), "INFO"),
        csv_row("trainable_rank_regressed", guard_metrics.get("trainable_rank_regressed", ""), "INFO"),
        csv_row("protected_rank_regressed", guard_metrics.get("protected_rank_regressed", ""), "INFO"),
        csv_row("anchor_top1_changed", guard_metrics.get("anchor_top1_changed", ""), "INFO"),
        csv_row("anchor_max_kl", guard_metrics.get("anchor_max_kl", ""), "INFO"),
    ]

    args.out_decision_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.out_decision_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["item", "value", "status", "notes"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    command_lines = [
        "# Teacher-divergence gated training wrapper controlled execution command plan",
        "# Default invocation below is dry-run only.",
        "",
        "## Dry-run invocation used in this branch",
        shell_cmd([
            "python",
            "scripts/run_teacher_divergence_gated_training_wrapper.py",
            "--wrapper-summary", args.wrapper_summary,
            "--dataset", args.dataset,
            "--manifest", args.manifest,
            "--anchor-snapshots", args.anchor_snapshots,
            "--baseline-checkpoint", args.baseline_checkpoint,
            "--candidate-checkpoint", args.candidate_checkpoint,
            "--quarantine-checkpoint", args.quarantine_checkpoint,
            "--epochs", args.epochs,
            "--lr", args.lr,
            "--margin", args.margin,
            "--anchor-kl-weight", args.anchor_kl_weight,
            "--ce-weight", args.ce_weight,
            "--weight-decay", args.weight_decay,
            "--seed", args.seed,
        ]),
        "",
        "## Controlled execution invocation for later branch only",
        shell_cmd([
            "python",
            "scripts/run_teacher_divergence_gated_training_wrapper.py",
            "--execute",
            "--confirm-execute", CONFIRM_TOKEN,
            "--wrapper-summary", args.wrapper_summary,
            "--dataset", args.dataset,
            "--manifest", args.manifest,
            "--anchor-snapshots", args.anchor_snapshots,
            "--baseline-checkpoint", args.baseline_checkpoint,
            "--candidate-checkpoint", args.candidate_checkpoint,
            "--quarantine-checkpoint", args.quarantine_checkpoint,
            "--epochs", args.epochs,
            "--lr", args.lr,
            "--margin", args.margin,
            "--anchor-kl-weight", args.anchor_kl_weight,
            "--ce-weight", args.ce_weight,
            "--weight-decay", args.weight_decay,
            "--seed", args.seed,
        ]),
        "",
        "## Planned training command inside executor",
        train_shell,
        "",
        "## Planned guard command inside executor",
        guard_shell,
        "",
    ]
    args.out_commands.parent.mkdir(parents=True, exist_ok=True)
    args.out_commands.write_text("\n".join(command_lines), encoding="utf-8")

    lines = [
        "# Teacher-divergence gated wrapper controlled execution review",
        "",
        "## Branch",
        "",
        "`exp/15x15-teacher-divergence-gated-wrapper-controlled-exec-review`",
        "",
        "## Scope",
        "",
        "- Upgrades the wrapper to support controlled execution mode.",
        "- Default mode remains dry-run.",
        "- Controlled execution requires both `--execute` and the exact confirm token.",
        "- This branch only runs dry-run validation.",
        "- Does not train in this run.",
        "- Does not write checkpoints in this run.",
        "- Does not move or delete checkpoints in this run.",
        "- Does not overwrite `checkpoints/15x15_current_best.pt`.",
        "- Does not C export.",
        "- Does not run public benchmark.",
        "- Does not promote.",
        "",
        "## Executor decision",
        "",
        f"`{executor_decision}`",
        "",
        "## Safety flags for this run",
        "",
        "| flag | value |",
        "|---|---:|",
        f"| mode | {mode} |",
        f"| execute_requested | {int(args.execute)} |",
        f"| confirm_execute_valid | {int(args.confirm_execute == CONFIRM_TOKEN)} |",
        f"| executed_training | {int(executed_training)} |",
        f"| executed_guard | {int(executed_guard)} |",
        f"| moved_to_quarantine | {int(moved_to_quarantine)} |",
        "",
        "## Preconditions",
        "",
        "| item | value |",
        "|---|---:|",
        f"| source closeout decision | {source_decision} |",
        f"| plan decision | {plan_decision} |",
        f"| preflight blockers | {len(preflight_blockers)} |",
        f"| preflight warnings | {len(preflight_warnings)} |",
        f"| final hard failures | {len(final_hard_failures)} |",
        f"| final warnings | {len(final_warnings)} |",
        "",
        "## Hard gates for execution mode",
        "",
        "| gate | threshold |",
        "|---|---|",
    ]
    for key, value in hard_gates.items():
        lines.append(f"| {key} | {value} |")

    lines.extend([
        "",
        "## Warning gates",
        "",
        "| gate | action |",
        "|---|---|",
    ])
    for key, value in warning_gates.items():
        lines.append(f"| {key} | {value} |")

    lines.extend([
        "",
        "## Planned training command",
        "",
        "```bash",
        train_shell,
        "```",
        "",
        "## Planned guard command",
        "",
        "```bash",
        guard_shell,
        "```",
        "",
        "## Checkpoint policy",
        "",
        f"- Baseline checkpoint: `{args.baseline_checkpoint}`",
        f"- Candidate checkpoint: `{args.candidate_checkpoint}`",
        f"- Quarantine checkpoint: `{args.quarantine_checkpoint}`",
        "- Pass action: keep isolated candidate checkpoint only.",
        "- Fail action: quarantine candidate checkpoint if it exists.",
        "- Never overwrite `checkpoints/15x15_current_best.pt`.",
        "- Never add checkpoint artifacts to git.",
        "",
        "## Preflight blockers",
        "",
    ])
    if preflight_blockers:
        for item in preflight_blockers:
            lines.append(f"- {item}")
    else:
        lines.append("- None.")

    lines.extend([
        "",
        "## Warnings",
        "",
    ])
    if final_warnings:
        for item in final_warnings:
            lines.append(f"- {item}")
    else:
        lines.append("- None.")

    lines.extend([
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
        "A later branch may run controlled execution by passing `--execute --confirm-execute TEACHER_DIVERGENCE_GATED_TRAINING`.",
        "",
        "This branch remains a review/dry-run branch only.",
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
    print("mode:", mode)
    print("execute_requested:", int(args.execute))
    print("executed_training:", int(executed_training))
    print("executed_guard:", int(executed_guard))
    print("moved_to_quarantine:", int(moved_to_quarantine))
    print("preflight_blockers:", len(preflight_blockers))
    print("final_hard_failures:", len(final_hard_failures))
    print("final_warnings:", len(final_warnings))
    print("out_decision_json:", args.out_decision_json)
    print("out_decision_csv:", args.out_decision_csv)
    print("out_commands:", args.out_commands)
    print("out_report:", args.out_report)
    print("default dry-run; no training unless explicit execute+confirm token")


if __name__ == "__main__":
    main()
