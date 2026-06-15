from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ProbeSpec:
    name: str
    eval_csv: Path
    notes: str


DEFAULT_PROBES = [
    ProbeSpec(
        name="unanchored_e80_kl025",
        eval_csv=Path("analysis/integration_eval/teacher_divergence_policy_probe_eval.csv"),
        notes="CE on train_candidate only; KL on train_candidate only; 80 epochs; kl=0.25",
    ),
    ProbeSpec(
        name="anchored_e80_kl035",
        eval_csv=Path("analysis/integration_eval/teacher_divergence_policy_anchor_probe_eval.csv"),
        notes="CE on train_candidate; KL on train_candidate+train_teacher_divergence; 80 epochs; kl=0.35",
    ),
    ProbeSpec(
        name="anchored_e40_kl075",
        eval_csv=Path("analysis/integration_eval/teacher_divergence_policy_anchor_probe_e40_kl075_eval.csv"),
        notes="CE on train_candidate; KL on train_candidate+train_teacher_divergence; 40 epochs; kl=0.75; no-save",
    ),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate pass/fail gates for teacher-divergence policy probe CSVs."
    )
    parser.add_argument(
        "--summary-csv",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_policy_probe_gate_summary.csv"),
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_policy_probe_gate_report.md"),
    )
    parser.add_argument("--min-candidate-rank-improved", type=int, default=8)
    parser.add_argument("--min-candidate-prob-improved", type=int, default=8)
    parser.add_argument("--max-candidate-prob-regressed", type=int, default=0)
    parser.add_argument("--max-teacher-divergence-prob-regressed", type=int, default=10)
    parser.add_argument("--max-teacher-divergence-rank-regressed", type=int, default=5)
    parser.add_argument("--max-heldout-prob-regressed", type=int, default=4)
    parser.add_argument("--max-heldout-rank-regressed", type=int, default=3)
    parser.add_argument("--allow-heldout-top1-loss", action="store_true")
    return parser.parse_args()


def read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def split_stats(rows: list[dict[str, str]]) -> dict[str, dict[str, Any]]:
    before = {r["id"]: r for r in rows if r["phase"] == "before"}
    after = {r["id"]: r for r in rows if r["phase"] == "after"}

    missing = sorted(set(before) ^ set(after))
    if missing:
        raise ValueError(f"before/after id mismatch: {missing[:10]}")

    grouped: dict[str, list[tuple[dict[str, str], dict[str, str]]]] = defaultdict(list)
    for row_id, b in before.items():
        grouped[b["split"]].append((b, after[row_id]))

    out: dict[str, dict[str, Any]] = {}
    for split, pairs in grouped.items():
        c = Counter()
        before_ranks = []
        after_ranks = []
        before_probs = []
        after_probs = []

        for b, a in pairs:
            br, ar = int(b["target_rank"]), int(a["target_rank"])
            bp, ap = float(b["target_prob"]), float(a["target_prob"])

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

    return out


def gate_probe(name: str, stats: dict[str, dict[str, Any]], args: argparse.Namespace) -> tuple[str, list[str]]:
    failures: list[str] = []

    cand = stats["train_candidate"]
    td = stats["train_teacher_divergence"]
    held = stats["heldout_retention"]

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

    if td["prob_regressed"] > args.max_teacher_divergence_prob_regressed:
        failures.append(
            f"train_teacher_divergence prob_regressed {td['prob_regressed']} > {args.max_teacher_divergence_prob_regressed}"
        )
    if td["rank_regressed"] > args.max_teacher_divergence_rank_regressed:
        failures.append(
            f"train_teacher_divergence rank_regressed {td['rank_regressed']} > {args.max_teacher_divergence_rank_regressed}"
        )

    if held["prob_regressed"] > args.max_heldout_prob_regressed:
        failures.append(
            f"heldout_retention prob_regressed {held['prob_regressed']} > {args.max_heldout_prob_regressed}"
        )
    if held["rank_regressed"] > args.max_heldout_rank_regressed:
        failures.append(
            f"heldout_retention rank_regressed {held['rank_regressed']} > {args.max_heldout_rank_regressed}"
        )
    if not args.allow_heldout_top1_loss and held["after_top1"] < held["before_top1"]:
        failures.append(
            f"heldout_retention top1 decreased {held['before_top1']} -> {held['after_top1']}"
        )

    return ("PASS" if not failures else "FAIL"), failures


def flatten_summary(
    probe: ProbeSpec,
    stats: dict[str, dict[str, Any]],
    decision: str,
    failures: list[str],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for split in ("train_candidate", "train_teacher_divergence", "heldout_retention"):
        s = stats[split]
        rows.append(
            {
                "probe": probe.name,
                "split": split,
                "decision": decision,
                "failure_count": len(failures),
                "failures": " | ".join(failures),
                "rows": s["rows"],
                "rank_improved": s["rank_improved"],
                "rank_same": s["rank_same"],
                "rank_regressed": s["rank_regressed"],
                "prob_improved": s["prob_improved"],
                "prob_same": s["prob_same"],
                "prob_regressed": s["prob_regressed"],
                "before_top1": s["before_top1"],
                "after_top1": s["after_top1"],
                "mean_rank_before": f"{s['mean_rank_before']:.4f}",
                "mean_rank_after": f"{s['mean_rank_after']:.4f}",
                "mean_prob_before": f"{s['mean_prob_before']:.8f}",
                "mean_prob_after": f"{s['mean_prob_after']:.8f}",
                "notes": probe.notes,
                "eval_csv": str(probe.eval_csv),
            }
        )
    return rows


def write_summary_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "probe",
        "split",
        "decision",
        "failure_count",
        "failures",
        "rows",
        "rank_improved",
        "rank_same",
        "rank_regressed",
        "prob_improved",
        "prob_same",
        "prob_regressed",
        "before_top1",
        "after_top1",
        "mean_rank_before",
        "mean_rank_after",
        "mean_prob_before",
        "mean_prob_after",
        "notes",
        "eval_csv",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_report(
    path: Path,
    args: argparse.Namespace,
    probe_results: list[tuple[ProbeSpec, dict[str, dict[str, Any]], str, list[str]]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    lines.append("# Teacher-divergence policy probe gate report")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append("This report applies fixed regression gates to existing teacher-divergence policy probe CSVs.")
    lines.append("")
    lines.append("It does not train, save checkpoints, export C weights, run benchmarks, promote a model, or make a capacity conclusion.")
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
    lines.append("## Probe decisions")
    lines.append("")
    lines.append("| probe | decision | failure count | failures |")
    lines.append("|---|---|---:|---|")
    for probe, _stats, decision, failures in probe_results:
        lines.append(
            f"| `{probe.name}` | {decision} | {len(failures)} | "
            f"{'<br>'.join(failures) if failures else 'none'} |"
        )

    lines.append("")
    lines.append("## Split summary")
    lines.append("")
    lines.append("| probe | split | rows | rank improved/same/regressed | prob improved/same/regressed | top1 before->after | mean rank before->after | mean prob before->after |")
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|")
    for probe, stats, decision, failures in probe_results:
        for split in ("train_candidate", "train_teacher_divergence", "heldout_retention"):
            s = stats[split]
            lines.append(
                f"| `{probe.name}` | {split} | {s['rows']} | "
                f"{s['rank_improved']}/{s['rank_same']}/{s['rank_regressed']} | "
                f"{s['prob_improved']}/{s['prob_same']}/{s['prob_regressed']} | "
                f"{s['before_top1']}->{s['after_top1']} | "
                f"{s['mean_rank_before']:.2f}->{s['mean_rank_after']:.2f} | "
                f"{s['mean_prob_before']:.6f}->{s['mean_prob_after']:.6f} |"
            )

    lines.append("")
    lines.append("## Decision")
    lines.append("")
    lines.append("All evaluated probes fail the regression gates.")
    lines.append("")
    lines.append("The anchored e80/kl0.35 probe remains the best failed baseline because it keeps train_candidate rank/probability movement at 8/8 while reducing train_teacher_divergence regressions versus the unanchored probe.")
    lines.append("")
    lines.append("No existing probe should be exported, benchmarked, promoted, or used for a capacity conclusion.")
    lines.append("")
    lines.append("## Recommended next step")
    lines.append("")
    lines.append("Do not continue blindly sweeping KL weight and epoch count. The next probe should add explicit regression gates before checkpoint saving and should explore mixed low-weight CE anchors on selected train_teacher_divergence rows while keeping heldout_retention evaluation-only.")
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()

    probe_results: list[tuple[ProbeSpec, dict[str, dict[str, Any]], str, list[str]]] = []
    flat_rows: list[dict[str, Any]] = []

    for probe in DEFAULT_PROBES:
        rows = read_rows(probe.eval_csv)
        stats = split_stats(rows)
        decision, failures = gate_probe(probe.name, stats, args)
        probe_results.append((probe, stats, decision, failures))
        flat_rows.extend(flatten_summary(probe, stats, decision, failures))

    write_summary_csv(args.summary_csv, flat_rows)
    write_report(args.report, args, probe_results)

    print(f"wrote summary csv: {args.summary_csv}")
    print(f"wrote report: {args.report}")

    for probe, _stats, decision, failures in probe_results:
        print(f"{probe.name}: {decision}")
        for failure in failures:
            print(f"  - {failure}")


if __name__ == "__main__":
    main()
