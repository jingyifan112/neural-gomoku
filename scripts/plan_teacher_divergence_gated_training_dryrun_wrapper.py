#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import shlex
from pathlib import Path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Create a dry-run wrapper design for gated teacher-divergence training."
    )
    p.add_argument(
        "--plan-summary",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_gated_training_review_plan_summary.csv"),
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
    p.add_argument(
        "--out-summary-csv",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_gated_training_dryrun_wrapper_summary.csv"),
    )
    p.add_argument(
        "--out-commands",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_gated_training_dryrun_wrapper_commands.txt"),
    )
    p.add_argument(
        "--out-report",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_gated_training_dryrun_wrapper_plan.md"),
    )
    return p.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def by_item(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {r["item"]: r for r in rows}


def cmd(parts: list[str | Path | int | float]) -> str:
    return shlex.join([str(p) for p in parts])


def summary_row(item: str, value: str | int | float, status: str, notes: str = "") -> dict[str, str]:
    return {
        "item": item,
        "value": str(value),
        "status": status,
        "notes": notes,
    }


def main() -> None:
    args = parse_args()

    required_paths = [
        args.plan_summary,
        args.dataset,
        args.manifest,
        args.anchor_snapshots,
        args.baseline_checkpoint,
        Path("scripts/train_rapfi_teacher_policy_margin.py"),
        Path("scripts/audit_teacher_divergence_tiny_posttrain_guards.py"),
    ]
    missing = [str(p) for p in required_paths if not p.exists()]

    plan_rows = read_csv(args.plan_summary)
    plan = by_item(plan_rows)

    source_decision = plan["source_closeout_decision"]["value"]
    plan_decision = plan["plan_decision"]["value"]
    hard_failure_count = int(float(plan["hard_failure_count"]["value"]))
    warning_count = int(float(plan["warning_count"]["value"]))

    allowed_to_design = (
        source_decision == "PASS_TO_GATED_TRAINING_REVIEW_WITH_WARNINGS"
        and plan_decision == "READY_TO_DESIGN_GATED_TRAINING_DRYRUN"
        and hard_failure_count == 0
    )

    train_log = Path("analysis/integration_eval/teacher_divergence_gated_training_dryrun_e10_train.log")
    trainable_guard = Path("analysis/integration_eval/teacher_divergence_gated_training_dryrun_e10_trainable_gap_guard.csv")
    bucket_guard = Path("analysis/integration_eval/teacher_divergence_gated_training_dryrun_e10_manifest_bucket_guard.csv")
    anchor_guard = Path("analysis/integration_eval/teacher_divergence_gated_training_dryrun_e10_anchor_drift_guard.csv")
    guard_report = Path("analysis/integration_eval/teacher_divergence_gated_training_dryrun_e10_guard_audit.md")
    wrapper_decision_json = Path("analysis/integration_eval/teacher_divergence_gated_training_dryrun_e10_wrapper_decision.json")
    wrapper_decision_csv = Path("analysis/integration_eval/teacher_divergence_gated_training_dryrun_e10_wrapper_decision.csv")
    wrapper_closeout = Path("analysis/integration_eval/teacher_divergence_gated_training_dryrun_e10_wrapper_closeout.md")

    train_cmd = cmd([
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

    guard_cmd = cmd([
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

    decision_policy = {
        "trainable_rows_evaluated": "must equal 44",
        "trainable_gap_improved_rows": "must be >= 40",
        "trainable_mean_gap_delta": "must be > 0",
        "trainable_target_rank_regressions": "must equal 0",
        "protected_top10_target_rank_regressions": "must equal 0",
        "anchor_top1_changed_rows": "must equal 0",
        "anchor_max_kl_ref_to_candidate": "must be <= 0.005",
        "candidate_checkpoint_action_on_pass": "keep isolated candidate checkpoint",
        "candidate_checkpoint_action_on_fail": f"move/quarantine to {args.quarantine_checkpoint}",
    }

    summary_rows = [
        summary_row("source_closeout_decision", source_decision, "INFO"),
        summary_row("plan_decision", plan_decision, "INFO"),
        summary_row("allowed_to_design_wrapper", int(allowed_to_design), "PASS" if allowed_to_design else "FAIL"),
        summary_row("hard_failure_count", hard_failure_count, "PASS" if hard_failure_count == 0 else "FAIL"),
        summary_row("warning_count", warning_count, "WARN" if warning_count else "PASS"),
        summary_row("missing_required_paths", len(missing), "PASS" if not missing else "FAIL", "; ".join(missing)),
        summary_row("baseline_checkpoint", args.baseline_checkpoint, "INFO", "must never be overwritten"),
        summary_row("candidate_checkpoint", args.candidate_checkpoint, "INFO", "isolated output path"),
        summary_row("quarantine_checkpoint", args.quarantine_checkpoint, "INFO", "failure path only"),
        summary_row("epochs", args.epochs, "INFO"),
        summary_row("lr", args.lr, "INFO"),
        summary_row("margin", args.margin, "INFO"),
        summary_row("anchor_kl_weight", args.anchor_kl_weight, "INFO"),
        summary_row("ce_weight", args.ce_weight, "INFO"),
        summary_row("weight_decay", args.weight_decay, "INFO"),
        summary_row("seed", args.seed, "INFO"),
        summary_row("train_log", train_log, "INFO"),
        summary_row("trainable_guard_csv", trainable_guard, "INFO"),
        summary_row("bucket_guard_csv", bucket_guard, "INFO"),
        summary_row("anchor_guard_csv", anchor_guard, "INFO"),
        summary_row("guard_report", guard_report, "INFO"),
        summary_row("wrapper_decision_json", wrapper_decision_json, "INFO"),
        summary_row("wrapper_decision_csv", wrapper_decision_csv, "INFO"),
        summary_row("wrapper_closeout", wrapper_closeout, "INFO"),
    ]

    args.out_summary_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.out_summary_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["item", "value", "status", "notes"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(summary_rows)

    command_lines = [
        "# Teacher-divergence gated training dry-run wrapper command plan",
        "# Review-only. Do not execute this file as a script yet.",
        "# The actual wrapper implementation should run these steps with save-on-pass logic.",
        "",
        "## Step 1: train isolated candidate",
        train_cmd,
        "",
        "## Step 2: run posttrain guards",
        guard_cmd,
        "",
        "## Step 3: apply wrapper decision policy",
    ]
    for key, value in decision_policy.items():
        command_lines.append(f"- {key}: {value}")
    command_lines.extend([
        "",
        "## Step 4: checkpoint action",
        f"- pass: keep `{args.candidate_checkpoint}` as isolated candidate artifact only",
        f"- fail: move `{args.candidate_checkpoint}` to `{args.quarantine_checkpoint}` if it exists",
        "- never overwrite `checkpoints/15x15_current_best.pt`",
        "- never add checkpoint artifacts to git",
        "",
    ])
    args.out_commands.write_text("\n".join(command_lines), encoding="utf-8")

    lines = [
        "# Teacher-divergence gated training dry-run wrapper design",
        "",
        "## Branch",
        "",
        "`exp/15x15-teacher-divergence-gated-training-dryrun-wrapper-design`",
        "",
        "## Scope",
        "",
        "- Designs the wrapper for a later gated training dry run.",
        "- Generates command plan and save-on-pass policy.",
        "- Does not train.",
        "- Does not read or write candidate checkpoints.",
        "- Does not overwrite `checkpoints/15x15_current_best.pt`.",
        "- Does not C export.",
        "- Does not run public benchmark.",
        "- Does not promote.",
        "",
        "## Source plan state",
        "",
        "| item | value |",
        "|---|---:|",
        f"| source closeout decision | {source_decision} |",
        f"| plan decision | {plan_decision} |",
        f"| hard failures | {hard_failure_count} |",
        f"| warnings | {warning_count} |",
        f"| allowed to design wrapper | {int(allowed_to_design)} |",
        f"| missing required paths | {len(missing)} |",
        "",
        "## Proposed training command",
        "",
        "```bash",
        train_cmd,
        "```",
        "",
        "## Proposed guard command",
        "",
        "```bash",
        guard_cmd,
        "```",
        "",
        "## Save-on-pass wrapper policy",
        "",
        "| gate | threshold | failure action |",
        "|---|---|---|",
        "| trainable rows evaluated | exactly 44 | fail + quarantine candidate |",
        "| trainable gap improved rows | >= 40 | fail + quarantine candidate |",
        "| trainable mean gap delta | > 0 | fail + quarantine candidate |",
        "| trainable target rank regressions | 0 | fail + quarantine candidate |",
        "| protected_top10 target rank regressions | 0 | fail + quarantine candidate |",
        "| anchor top1 changed rows | 0 | fail + quarantine candidate |",
        "| anchor max KL ref->candidate | <= 0.005 | fail + quarantine candidate |",
        "",
        "## Warning policy",
        "",
        "| warning | action |",
        "|---|---|",
        "| protected_top10 raw probability regressions | report, require epsilon-aware review |",
        "| tail_rank_gt50 raw probability regressions | report, require epsilon-aware review |",
        "| tail_rank_gt50 rank regression | block uncontrolled scaling and inspect |",
        "| anchor max KL > 0.001 and <= 0.005 | warning only |",
        "",
        "## Candidate paths",
        "",
        f"- baseline checkpoint: `{args.baseline_checkpoint}`",
        f"- isolated candidate checkpoint: `{args.candidate_checkpoint}`",
        f"- quarantine checkpoint path: `{args.quarantine_checkpoint}`",
        "",
        "## Planned outputs for later execution",
        "",
        f"- training log: `{train_log}`",
        f"- trainable guard CSV: `{trainable_guard}`",
        f"- manifest bucket guard CSV: `{bucket_guard}`",
        f"- anchor drift guard CSV: `{anchor_guard}`",
        f"- guard report: `{guard_report}`",
        f"- wrapper decision JSON: `{wrapper_decision_json}`",
        f"- wrapper decision CSV: `{wrapper_decision_csv}`",
        f"- wrapper closeout report: `{wrapper_closeout}`",
        "",
        "## Summary table",
        "",
        "| item | value | status | notes |",
        "|---|---:|---|---|",
    ]
    for r in summary_rows:
        notes = r["notes"].replace("|", "\\|")
        lines.append(f"| {r['item']} | {r['value']} | {r['status']} | {notes} |")

    lines.extend([
        "",
        "## Missing required paths",
        "",
    ])
    if missing:
        for item in missing:
            lines.append(f"- `{item}`")
    else:
        lines.append("- None.")

    lines.extend([
        "",
        "## Decision",
        "",
        "`WRAPPER_DESIGN_READY_FOR_IMPLEMENTATION`" if allowed_to_design and not missing else "`WRAPPER_DESIGN_BLOCKED`",
        "",
        "This branch is design-only. The next branch may implement the actual wrapper executor, still with dry-run defaults.",
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

    args.out_report.write_text("\n".join(lines), encoding="utf-8")

    print("source_decision:", source_decision)
    print("plan_decision:", plan_decision)
    print("allowed_to_design_wrapper:", int(allowed_to_design))
    print("missing_required_paths:", len(missing))
    print("candidate_checkpoint:", args.candidate_checkpoint)
    print("quarantine_checkpoint:", args.quarantine_checkpoint)
    print("out_summary_csv:", args.out_summary_csv)
    print("out_commands:", args.out_commands)
    print("out_report:", args.out_report)
    print("design-only; no training; no checkpoint write; no C export; no benchmark; no promotion")


if __name__ == "__main__":
    main()
