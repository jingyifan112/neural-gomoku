#!/usr/bin/env python3
from __future__ import annotations

import csv
import os
import re
import subprocess
import sys
from pathlib import Path


OUT_DIR = Path("analysis/integration_eval/b4c96_nosave_objective_ablation_run1")
LOG_DIR = Path("eval_logs/integration_eval/b4c96_nosave_objective_ablation_run1")

WRAPPER = Path("scripts/probe_policy_rank_topk_protected_nosave_b4c96.py")

DATASET = Path(
    "analysis/public_benchmark_eval/"
    "rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_protected_train_11_50_weightcap3.json"
)
ANCHORS = Path("analysis/public_benchmark_eval/corpus8_selected_board_snapshots.json")
B4C96 = Path("checkpoints/probes/15x15_capacity_data_pairing_b4c96_probe_candidate.pt")

VARIANTS = [
    {
        "variant": "A1_stronger_anchor_balanced_hinge",
        "ce_weight": 1.0,
        "pair_weight": 0.6,
        "worst_weight": 0.6,
        "anchor_kl_weight": 1.0,
    },
    {
        "variant": "A2_light_worst_suppress",
        "ce_weight": 1.0,
        "pair_weight": 0.6,
        "worst_weight": 0.2,
        "anchor_kl_weight": 0.8,
    },
    {
        "variant": "A3_ce_dominant_rank_repair",
        "ce_weight": 1.5,
        "pair_weight": 0.3,
        "worst_weight": 0.1,
        "anchor_kl_weight": 0.8,
    },
]


def require(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(path)


def run_variant(v: dict[str, float | str]) -> None:
    variant = str(v["variant"])
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
        "3",
        "--lr",
        "1e-6",
        "--margin",
        "0.25",
        "--ce-weight",
        str(v["ce_weight"]),
        "--pair-weight",
        str(v["pair_weight"]),
        "--worst-weight",
        str(v["worst_weight"]),
        "--anchor-kl-weight",
        str(v["anchor_kl_weight"]),
        "--weight-decay",
        "1e-5",
        "--seed",
        "37",
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

    print()
    print(f"=== run {variant} ===")
    print(" ".join(cmd), flush=True)

    proc = subprocess.run(cmd, text=True, capture_output=True, env=env)
    log_path.write_text(proc.stdout + proc.stderr, encoding="utf-8")

    print(proc.stdout, end="")
    if proc.stderr:
        print(proc.stderr, end="", file=sys.stderr)

    if proc.returncode != 0:
        raise RuntimeError(f"{variant} failed with exit code {proc.returncode}; see {log_path}")

    require(out_csv)
    require(out_report)


def extract_verdict(report_path: Path) -> str:
    text = report_path.read_text(encoding="utf-8")
    match = re.search(r"## Verdict\s*\n\s*([A-Z0-9_]+)", text)
    return match.group(1) if match else "UNKNOWN"


def summarize() -> None:
    summary_rows: list[dict[str, str | float]] = []

    for v in VARIANTS:
        variant = str(v["variant"])
        csv_path = OUT_DIR / f"{variant}_group_metrics.csv"
        report_path = OUT_DIR / f"{variant}_report.md"
        require(csv_path)
        require(report_path)

        verdict = extract_verdict(report_path)

        with csv_path.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                summary_rows.append(
                    {
                        "variant": variant,
                        "ce_weight": v["ce_weight"],
                        "pair_weight": v["pair_weight"],
                        "worst_weight": v["worst_weight"],
                        "anchor_kl_weight": v["anchor_kl_weight"],
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
        "ce_weight",
        "pair_weight",
        "worst_weight",
        "anchor_kl_weight",
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

    summary_csv = OUT_DIR / "run1_summary.csv"
    with summary_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(summary_rows)

    md: list[str] = []
    md += ["# b4c96 no-save objective ablation run1 summary", ""]
    md += ["## Scope", ""]
    md += [
        "- No-save objective ablation only.",
        "- No checkpoint save, no C export, no public benchmark, no promotion.",
        "",
    ]

    md += ["## Variants", ""]
    md += ["| variant | ce | pair | worst | anchor_kl | verdict |"]
    md += ["|---|---:|---:|---:|---:|---|"]
    seen: set[str] = set()
    for r in summary_rows:
        variant = str(r["variant"])
        if variant in seen:
            continue
        seen.add(variant)
        md.append(
            f"| {variant} | {r['ce_weight']} | {r['pair_weight']} | "
            f"{r['worst_weight']} | {r['anchor_kl_weight']} | {r['verdict']} |"
        )

    md += ["", "## Group metrics", ""]
    md += [
        "| variant | group | top5 Δ | top10 Δ | rank>50 Δ | mean_rank Δ | target_prob Δ | worst_gap Δ | hinge Δ |"
    ]
    md += ["|---|---|---:|---:|---:|---:|---:|---:|---:|"]
    for r in summary_rows:
        md.append(
            f"| {r['variant']} | {r['group']} | {float(r['top5_delta']):.6f} | "
            f"{float(r['top10_delta']):.6f} | {float(r['rank_gt50_delta']):.6f} | "
            f"{float(r['mean_rank_delta']):.6f} | {float(r['mean_target_prob_delta']):.8f} | "
            f"{float(r['mean_worst_gap_delta']):.6f} | {float(r['hinge_delta']):.6f} |"
        )

    md += ["", "## Preliminary decision rule", ""]
    md.append(
        "A variant is only directionally useful if train improves without protected top5/top10 loss and without tail rank>50 regression."
    )
    md += ["", "## Final note", ""]
    md.append("This summary records no-save ablation metrics only. It does not authorize checkpoint save or promotion.")
    md.append("")

    summary_md = OUT_DIR / "run1_summary.md"
    summary_md.write_text("\n".join(md), encoding="utf-8")

    print()
    print("wrote", summary_csv)
    print("wrote", summary_md)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    for path in [WRAPPER, DATASET, ANCHORS, B4C96]:
        require(path)

    for v in VARIANTS:
        run_variant(v)

    summarize()

    print()
    print("run1 complete: no checkpoint save, no C export, no public benchmark, no promotion")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
