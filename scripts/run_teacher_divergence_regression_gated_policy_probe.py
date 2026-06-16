from __future__ import annotations

import argparse
import csv
import os
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run a teacher-divergence anchored policy probe with regression gates. "
            "The checkpoint is saved only if gates pass."
        )
    )

    parser.add_argument(
        "--anchor-script",
        type=Path,
        default=Path("scripts/train_teacher_divergence_policy_anchor_probe.py"),
    )
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--epochs", type=int, default=80)
    parser.add_argument("--lr", type=float, default=3e-5)
    parser.add_argument("--kl-weight", type=float, default=0.35)
    parser.add_argument(
        "--anchor-kl-splits",
        default="train_candidate,train_teacher_divergence",
    )
    parser.add_argument("--train-scope", default="policy_head")

    parser.add_argument(
        "--eval-csv",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_policy_regression_gated_probe_eval.csv"),
    )
    parser.add_argument(
        "--train-report",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_policy_regression_gated_probe_train_report.md"),
    )
    parser.add_argument(
        "--gate-report",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_policy_regression_gated_probe_gate_report.md"),
    )
    parser.add_argument(
        "--out-checkpoint",
        type=Path,
        default=Path("checkpoints/15x15_teacher_divergence_policy_regression_gated_probe.pt"),
    )

    parser.add_argument("--min-candidate-rank-improved", type=int, default=8)
    parser.add_argument("--min-candidate-prob-improved", type=int, default=8)
    parser.add_argument("--max-candidate-prob-regressed", type=int, default=0)
    parser.add_argument("--max-teacher-divergence-prob-regressed", type=int, default=10)
    parser.add_argument("--max-teacher-divergence-rank-regressed", type=int, default=5)
    parser.add_argument("--max-heldout-prob-regressed", type=int, default=4)
    parser.add_argument("--max-heldout-rank-regressed", type=int, default=3)
    parser.add_argument("--allow-heldout-top1-loss", action="store_true")

    parser.add_argument(
        "--save-on-pass",
        action="store_true",
        help=(
            "If gates pass, rerun the deterministic training command without --no-save "
            "and save the checkpoint. Without this flag, the runner only reports whether "
            "the probe would pass."
        ),
    )
    parser.add_argument(
        "--fail-exit-code",
        type=int,
        default=0,
        help="Exit code to use when gates fail. Default 0 keeps exploratory scripts non-fatal.",
    )

    return parser.parse_args()


def run_anchor_probe(args: argparse.Namespace, *, no_save: bool) -> None:
    cmd = [
        sys.executable,
        str(args.anchor_script),
        "--device",
        args.device,
        "--epochs",
        str(args.epochs),
        "--lr",
        str(args.lr),
        "--kl-weight",
        str(args.kl_weight),
        "--anchor-kl-splits",
        args.anchor_kl_splits,
        "--train-scope",
        args.train_scope,
        "--eval-csv",
        str(args.eval_csv),
        "--report",
        str(args.train_report),
        "--out-checkpoint",
        str(args.out_checkpoint),
    ]
    if no_save:
        cmd.append("--no-save")

    print()
    print("=== running anchor probe ===")
    print("mode:", "no-save" if no_save else "save")
    print(" ".join(cmd))
    subprocess.run(cmd, check=True)


def read_eval_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def summarize_eval(rows: list[dict[str, str]]) -> dict[str, dict[str, Any]]:
    before = {r["id"]: r for r in rows if r["phase"] == "before"}
    after = {r["id"]: r for r in rows if r["phase"] == "after"}

    if set(before) != set(after):
        missing_before = sorted(set(after) - set(before))
        missing_after = sorted(set(before) - set(after))
        raise ValueError(
            f"before/after mismatch: missing_before={missing_before[:10]} "
            f"missing_after={missing_after[:10]}"
        )

    grouped: dict[str, list[tuple[dict[str, str], dict[str, str]]]] = defaultdict(list)
    for row_id, b in before.items():
        grouped[b["split"]].append((b, after[row_id]))

    out: dict[str, dict[str, Any]] = {}
    for split, pairs in grouped.items():
        c = Counter()
        before_ranks: list[int] = []
        after_ranks: list[int] = []
        before_probs: list[float] = []
        after_probs: list[float] = []

        for b, a in pairs:
            br = int(b["target_rank"])
            ar = int(a["target_rank"])
            bp = float(b["target_prob"])
            ap = float(a["target_prob"])

            before_ranks.append(br)
            after_ranks.append(ar)
            before_probs.append(bp)
            after_probs.append(ap)

            if ar < br:
                c["rank_improved"] += 1
            elif ar > br:
                c["rank_regressed"] += 1
            else:
                c["rank_same"] += 1

            if ap > bp:
                c["prob_improved"] += 1
            elif ap < bp:
                c["prob_regressed"] += 1
            else:
                c["prob_same"] += 1

            if b["top_matches_target"] == "True":
                c["before_top1"] += 1
            if a["top_matches_target"] == "True":
                c["after_top1"] += 1

        out[split] = {
            "rows": len(pairs),
            "rank_improved": c["rank_improved"],
            "rank_same": c["rank_same"],
            "rank_regressed": c["rank_regressed"],
            "prob_improved": c["prob_improved"],
            "prob_same": c["prob_same"],
            "prob_regressed": c["prob_regressed"],
            "before_top1": c["before_top1"],
            "after_top1": c["after_top1"],
            "mean_rank_before": sum(before_ranks) / len(before_ranks),
            "mean_rank_after": sum(after_ranks) / len(after_ranks),
            "mean_prob_before": sum(before_probs) / len(before_probs),
            "mean_prob_after": sum(after_probs) / len(after_probs),
        }

    required = {"train_candidate", "train_teacher_divergence", "heldout_retention"}
    missing = sorted(required - set(out))
    if missing:
        raise ValueError(f"missing required splits in eval CSV: {missing}")

    return out


def evaluate_gates(
    stats: dict[str, dict[str, Any]],
    args: argparse.Namespace,
) -> tuple[str, list[str]]:
    failures: list[str] = []

    cand = stats["train_candidate"]
    teacher = stats["train_teacher_divergence"]
    heldout = stats["heldout_retention"]

    if cand["rank_improved"] < args.min_candidate_rank_improved:
        failures.append(
            f"train_candidate rank_improved {cand['rank_improved']} < {args.min_candidate_rank_improved}"
        )
    if cand["prob_improved"] < args.min_candidate_prob_improved:
        failures.append(
            f"train_candidate prob_improved {cand['prob_improved']} < {args.min_candidate_prob_improved}"
        )
    if cand["prob_regressed"] > args.max_candidate_prob_regressed:
        failures.append(
            f"train_candidate prob_regressed {cand['prob_regressed']} > {args.max_candidate_prob_regressed}"
        )

    if teacher["prob_regressed"] > args.max_teacher_divergence_prob_regressed:
        failures.append(
            f"train_teacher_divergence prob_regressed {teacher['prob_regressed']} > {args.max_teacher_divergence_prob_regressed}"
        )
    if teacher["rank_regressed"] > args.max_teacher_divergence_rank_regressed:
        failures.append(
            f"train_teacher_divergence rank_regressed {teacher['rank_regressed']} > {args.max_teacher_divergence_rank_regressed}"
        )

    if heldout["prob_regressed"] > args.max_heldout_prob_regressed:
        failures.append(
            f"heldout_retention prob_regressed {heldout['prob_regressed']} > {args.max_heldout_prob_regressed}"
        )
    if heldout["rank_regressed"] > args.max_heldout_rank_regressed:
        failures.append(
            f"heldout_retention rank_regressed {heldout['rank_regressed']} > {args.max_heldout_rank_regressed}"
        )
    if not args.allow_heldout_top1_loss and heldout["after_top1"] < heldout["before_top1"]:
        failures.append(
            f"heldout_retention top1 decreased {heldout['before_top1']} -> {heldout['after_top1']}"
        )

    return ("PASS" if not failures else "FAIL"), failures


def write_gate_report(
    path: Path,
    args: argparse.Namespace,
    decision: str,
    failures: list[str],
    stats: dict[str, dict[str, Any]],
    saved_checkpoint: bool,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    lines.append("# Teacher-divergence regression-gated policy probe report")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append("This runner trains/evaluates the anchored policy probe in no-save mode first, applies regression gates, and saves a checkpoint only if gates pass and `--save-on-pass` is set.")
    lines.append("")
    lines.append("It does not export C weights, run benchmarks, promote a model, overwrite current-best, or make a model-capacity conclusion.")
    lines.append("")
    lines.append("## Probe config")
    lines.append("")
    lines.append(f"- anchor_script: `{args.anchor_script}`")
    lines.append(f"- epochs: {args.epochs}")
    lines.append(f"- lr: {args.lr}")
    lines.append(f"- kl_weight: {args.kl_weight}")
    lines.append(f"- anchor_kl_splits: `{args.anchor_kl_splits}`")
    lines.append(f"- train_scope: `{args.train_scope}`")
    lines.append(f"- eval_csv: `{args.eval_csv}`")
    lines.append(f"- train_report: `{args.train_report}`")
    lines.append(f"- out_checkpoint: `{args.out_checkpoint}`")
    lines.append(f"- save_on_pass: {args.save_on_pass}")
    lines.append(f"- saved_checkpoint: {saved_checkpoint}")
    lines.append("")
    lines.append("## Gate thresholds")
    lines.append("")
    lines.append(f"- min train_candidate rank improved: {args.min_candidate_rank_improved}")
    lines.append(f"- min train_candidate probability improved: {args.min_candidate_prob_improved}")
    lines.append(f"- max train_candidate probability regressed: {args.max_candidate_prob_regressed}")
    lines.append(f"- max train_teacher_divergence probability regressed: {args.max_teacher_divergence_prob_regressed}")
    lines.append(f"- max train_teacher_divergence rank regressed: {args.max_teacher_divergence_rank_regressed}")
    lines.append(f"- max heldout_retention probability regressed: {args.max_heldout_prob_regressed}")
    lines.append(f"- max heldout_retention rank regressed: {args.max_heldout_rank_regressed}")
    lines.append(f"- allow heldout top-1 loss: {args.allow_heldout_top1_loss}")
    lines.append("")
    lines.append("## Decision")
    lines.append("")
    lines.append(f"- decision: **{decision}**")
    lines.append(f"- failure_count: {len(failures)}")
    if failures:
        lines.append("")
        lines.append("Failures:")
        lines.append("")
        for failure in failures:
            lines.append(f"- {failure}")
    lines.append("")
    lines.append("## Split summary")
    lines.append("")
    lines.append("| split | rows | rank improved/same/regressed | prob improved/same/regressed | top1 before->after | mean rank before->after | mean prob before->after |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|")
    for split in ("train_candidate", "train_teacher_divergence", "heldout_retention"):
        s = stats[split]
        lines.append(
            f"| {split} | {s['rows']} | "
            f"{s['rank_improved']}/{s['rank_same']}/{s['rank_regressed']} | "
            f"{s['prob_improved']}/{s['prob_same']}/{s['prob_regressed']} | "
            f"{s['before_top1']}->{s['after_top1']} | "
            f"{s['mean_rank_before']:.2f}->{s['mean_rank_after']:.2f} | "
            f"{s['mean_prob_before']:.6f}->{s['mean_prob_after']:.6f} |"
        )
    lines.append("")
    lines.append("## Boundary")
    lines.append("")
    if decision == "PASS":
        lines.append("Passing gates means this probe is eligible for further review. It still does not automatically justify C export, benchmark, promotion, or current-best replacement.")
    else:
        lines.append("Failing gates means no checkpoint should be saved for this configuration and no export/benchmark/promotion should be run.")
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()

    if args.out_checkpoint.exists():
        print(f"removing stale output checkpoint before gated run: {args.out_checkpoint}")
        args.out_checkpoint.unlink()

    run_anchor_probe(args, no_save=True)

    rows = read_eval_csv(args.eval_csv)
    stats = summarize_eval(rows)
    decision, failures = evaluate_gates(stats, args)

    saved_checkpoint = False
    if decision == "PASS" and args.save_on_pass:
        run_anchor_probe(args, no_save=False)
        saved_checkpoint = args.out_checkpoint.exists()

    write_gate_report(
        args.gate_report,
        args,
        decision,
        failures,
        stats,
        saved_checkpoint=saved_checkpoint,
    )

    print()
    print("=== regression gate decision ===")
    print(decision)
    for failure in failures:
        print(f"- {failure}")
    print(f"wrote gate report: {args.gate_report}")
    print(f"saved_checkpoint: {saved_checkpoint}")

    if decision == "FAIL":
        raise SystemExit(args.fail_exit_code)


if __name__ == "__main__":
    main()
