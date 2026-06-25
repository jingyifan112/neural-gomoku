#!/usr/bin/env python3
from __future__ import annotations

import csv
import os
import re
import subprocess
import sys
from pathlib import Path


OUT_DIR = Path("analysis/integration_eval/teacher_divergence_next_nosave_probe")
LOG_DIR = Path("eval_logs/integration_eval/teacher_divergence_next_nosave_probe")

WRAPPER = Path("scripts/probe_policy_rank_topk_protected_nosave_b4c96.py")
DATASET = Path("analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_conservative_selection_next.json")
ANCHORS = Path("analysis/public_benchmark_eval/corpus8_selected_board_snapshots.json")
B4C96 = Path("checkpoints/probes/15x15_capacity_data_pairing_b4c96_probe_candidate.pt")
CONSUMER_AUDIT = Path("analysis/integration_eval/teacher_divergence_next_consumer_audit/consumer_schema_audit_summary.json")

VARIANT = {
    "variant": "conservative_selection_next",
    "ce_weight": 1.0,
    "pair_weight": 0.5,
    "worst_weight": 0.3,
    "anchor_kl_weight": 1.0,
    "epochs": 3,
    "lr": "1e-6",
    "margin": "0.25",
    "seed": "37",
}


def require(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(path)


def extract_verdict(report_path: Path) -> str:
    text = report_path.read_text(encoding="utf-8")
    match = re.search(r"## Verdict\s*\n\s*([A-Z0-9_]+)", text)
    return match.group(1) if match else "UNKNOWN"


def run_probe() -> None:
    variant = VARIANT["variant"]
    out_csv = OUT_DIR / f"{variant}_group_metrics.csv"
    out_report = OUT_DIR / f"{variant}_report.md"
    log_path = LOG_DIR / f"{variant}.log"

    cmd = [
        sys.executable,
        str(WRAPPER),
        "--dataset",
        str(DATASET),
        "--anchor-snapshots",
        str(ANCHORS),
        "--init-checkpoint",
        str(B4C96),
        "--reference-checkpoint",
        str(B4C96),
        "--board-size",
        "15",
        "--win-length",
        "5",
        "--channels",
        "96",
        "--blocks",
        "4",
        "--epochs",
        str(VARIANT["epochs"]),
        "--lr",
        str(VARIANT["lr"]),
        "--margin",
        str(VARIANT["margin"]),
        "--ce-weight",
        str(VARIANT["ce_weight"]),
        "--pair-weight",
        str(VARIANT["pair_weight"]),
        "--worst-weight",
        str(VARIANT["worst_weight"]),
        "--anchor-kl-weight",
        str(VARIANT["anchor_kl_weight"]),
        "--weight-decay",
        "1e-5",
        "--seed",
        str(VARIANT["seed"]),
        "--print-every",
        "1",
        "--out-csv",
        str(out_csv),
        "--out-report",
        str(out_report),
    ]

    env = os.environ.copy()
    old_pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = "src" if not old_pythonpath else f"src:{old_pythonpath}"

    print("=== run conservative no-save probe ===")
    print("dataset:", DATASET)
    print(" ".join(cmd), flush=True)

    proc = subprocess.run(cmd, text=True, capture_output=True, env=env)
    log_path.write_text(proc.stdout + proc.stderr, encoding="utf-8")

    print(proc.stdout, end="")
    if proc.stderr:
        print(proc.stderr, end="", file=sys.stderr)

    if proc.returncode != 0:
        raise RuntimeError(f"probe failed with exit code {proc.returncode}; see {log_path}")

    require(out_csv)
    require(out_report)


def summarize() -> None:
    variant = VARIANT["variant"]
    csv_path = OUT_DIR / f"{variant}_group_metrics.csv"
    report_path = OUT_DIR / f"{variant}_report.md"

    verdict = extract_verdict(report_path)

    rows = []
    with csv_path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows.append(
                {
                    "variant": variant,
                    "dataset": str(DATASET),
                    "verdict": verdict,
                    "group": row["group"],
                    "top5_delta": row["top5_delta"],
                    "top10_delta": row["top10_delta"],
                    "rank_gt50_delta": row["rank_gt50_delta"],
                    "mean_rank_delta": row["mean_rank_delta"],
                    "mean_target_prob_delta": row["mean_target_prob_delta"],
                    "mean_worst_gap_delta": row["mean_worst_gap_delta"],
                    "hinge_delta": row["mean_pair_hinge_margin_025_delta"],
                    "teacher_beats_worst_delta": row["teacher_beats_worst_delta"],
                    "teacher_beats_all_delta": row["teacher_beats_all_delta"],
                }
            )

    fields = [
        "variant",
        "dataset",
        "verdict",
        "group",
        "top5_delta",
        "top10_delta",
        "rank_gt50_delta",
        "mean_rank_delta",
        "mean_target_prob_delta",
        "mean_worst_gap_delta",
        "hinge_delta",
        "teacher_beats_worst_delta",
        "teacher_beats_all_delta",
    ]

    summary_csv = OUT_DIR / "nosave_probe_summary.csv"
    with summary_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

    protected = [r for r in rows if r["group"] == "protected_eval_top10"]
    tail = [r for r in rows if r["group"] == "tail_eval_rank_gt50"]
    train = [r for r in rows if r["group"] == "train_main_rank_11_50"]

    def fval(row_list: list[dict[str, str]], key: str) -> float:
        if not row_list:
            return 0.0
        return float(row_list[0][key])

    protected_safe = bool(
        protected
        and fval(protected, "top5_delta") >= 0
        and fval(protected, "top10_delta") >= 0
        and fval(protected, "rank_gt50_delta") <= 0
    )
    tail_safe = bool(
        tail
        and fval(tail, "top10_delta") >= 0
        and fval(tail, "rank_gt50_delta") <= 0
        and fval(tail, "mean_rank_delta") <= 0
    )
    train_not_worse_tail = bool(
        train
        and fval(train, "rank_gt50_delta") <= 0
    )

    directional_decision = (
        "CONSERVATIVE_NOSAVE_PROBE_DIRECTIONALLY_SAFE"
        if protected_safe and tail_safe and train_not_worse_tail
        else "CONSERVATIVE_NOSAVE_PROBE_FAILED_GUARDS"
    )

    md: list[str] = []
    md += ["# Teacher-divergence next conservative no-save probe summary", ""]
    md += ["## Scope", ""]
    md += [
        "- No-save probe only.",
        "- No checkpoint save.",
        "- No C export, no public benchmark, no promotion.",
        "",
    ]

    md += ["## Inputs", ""]
    md += [
        f"- dataset: `{DATASET}`",
        f"- wrapper: `{WRAPPER}`",
        f"- consumer audit: `{CONSUMER_AUDIT}`",
        f"- init/reference checkpoint: `{B4C96}`",
        "",
    ]

    md += ["## Variant", ""]
    md += [
        "| variant | epochs | lr | ce | pair | worst | anchor_kl | wrapper verdict | directional decision |",
        "|---|---:|---:|---:|---:|---:|---:|---|---|",
        f"| {variant} | {VARIANT['epochs']} | {VARIANT['lr']} | {VARIANT['ce_weight']} | "
        f"{VARIANT['pair_weight']} | {VARIANT['worst_weight']} | {VARIANT['anchor_kl_weight']} | "
        f"{verdict} | {directional_decision} |",
        "",
    ]

    md += ["## Group metrics", ""]
    md += [
        "| group | top5 Δ | top10 Δ | rank>50 Δ | mean_rank Δ | target_prob Δ | worst_gap Δ | hinge Δ |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in rows:
        md.append(
            f"| {r['group']} | {float(r['top5_delta']):.6f} | "
            f"{float(r['top10_delta']):.6f} | {float(r['rank_gt50_delta']):.6f} | "
            f"{float(r['mean_rank_delta']):.6f} | {float(r['mean_target_prob_delta']):.8f} | "
            f"{float(r['mean_worst_gap_delta']):.6f} | {float(r['hinge_delta']):.6f} |"
        )

    md += ["", "## Guard interpretation", ""]
    md += [
        f"- protected_safe: `{protected_safe}`",
        f"- tail_safe: `{tail_safe}`",
        f"- train_not_worse_tail: `{train_not_worse_tail}`",
        "",
    ]

    if directional_decision == "CONSERVATIVE_NOSAVE_PROBE_DIRECTIONALLY_SAFE":
        md += [
            "The conservative dataset avoided the key protected/tail guard failures in this no-save probe.",
            "",
            "This does not authorize checkpoint save. It only justifies a separate gate-design or repeated-seed no-save check.",
            "",
        ]
    else:
        md += [
            "The conservative dataset did not avoid the key protected/tail guard failures.",
            "",
            "Do not proceed to checkpoint-producing training. Return to data expansion or row-level review.",
            "",
        ]

    md += ["## Final note", ""]
    md += [
        "This summary records no-save behavior only and does not authorize checkpoint save, C export, public benchmark, promotion, or current_best overwrite.",
        "",
    ]

    summary_md = OUT_DIR / "nosave_probe_summary.md"
    summary_md.write_text("\n".join(md), encoding="utf-8")

    print()
    print("wrote", summary_csv)
    print("wrote", summary_md)
    print("directional_decision:", directional_decision)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    for p in [WRAPPER, DATASET, ANCHORS, B4C96, CONSUMER_AUDIT]:
        require(p)

    run_probe()
    summarize()

    print()
    print("probe complete: no checkpoint save, no C export, no public benchmark, no promotion")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
