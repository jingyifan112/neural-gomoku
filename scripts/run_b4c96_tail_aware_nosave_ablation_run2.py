#!/usr/bin/env python3
from __future__ import annotations

import csv
import os
import re
import subprocess
import sys
from pathlib import Path


OUT_DIR = Path("analysis/integration_eval/b4c96_tail_aware_nosave_ablation_run2")
LOG_DIR = Path("eval_logs/integration_eval/b4c96_tail_aware_nosave_ablation_run2")

WRAPPER = Path("scripts/probe_policy_rank_topk_protected_nosave_b4c96.py")
ANCHORS = Path("analysis/public_benchmark_eval/corpus8_selected_board_snapshots.json")
B4C96 = Path("checkpoints/probes/15x15_capacity_data_pairing_b4c96_probe_candidate.pt")

VARIANTS = [
    {
        "variant": "A4_tail_guard",
        "dataset": Path("analysis/public_benchmark_eval/b4c96_tail_aware_ablation_A4_tail_guard_dataset.json"),
        "ce_weight": 1.0,
        "pair_weight": 0.5,
        "worst_weight": 0.3,
        "anchor_kl_weight": 1.0,
    },
    {
        "variant": "A5_tail_guard_downweight",
        "dataset": Path("analysis/public_benchmark_eval/b4c96_tail_aware_ablation_A5_tail_guard_downweight_dataset.json"),
        "ce_weight": 1.0,
        "pair_weight": 0.5,
        "worst_weight": 0.3,
        "anchor_kl_weight": 1.0,
    },
]


def require(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(path)


def run_variant(v: dict[str, object]) -> None:
    variant = str(v["variant"])
    dataset = Path(str(v["dataset"]))
    out_csv = OUT_DIR / f"{variant}_group_metrics.csv"
    out_report = OUT_DIR / f"{variant}_report.md"
    log_path = LOG_DIR / f"{variant}.log"

    cmd = [
        sys.executable,
        str(WRAPPER),
        "--dataset",
        str(dataset),
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
    print("dataset:", dataset)
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
    rows: list[dict[str, object]] = []

    for v in VARIANTS:
        variant = str(v["variant"])
        csv_path = OUT_DIR / f"{variant}_group_metrics.csv"
        report_path = OUT_DIR / f"{variant}_report.md"
        require(csv_path)
        require(report_path)

        verdict = extract_verdict(report_path)

        with csv_path.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                rows.append(
                    {
                        "variant": variant,
                        "dataset": str(v["dataset"]),
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
        "dataset",
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

    summary_csv = OUT_DIR / "run2_summary.csv"
    with summary_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    md: list[str] = []
    md += ["# b4c96 tail-aware no-save ablation run2 summary", ""]
    md += ["## Scope", ""]
    md += [
        "- Tail-aware no-save ablation only.",
        "- No checkpoint save, no C export, no public benchmark, no promotion.",
        "",
    ]

    md += ["## Variants", ""]
    md += ["| variant | dataset | ce | pair | worst | anchor_kl | verdict |"]
    md += ["|---|---|---:|---:|---:|---:|---|"]
    seen: set[str] = set()
    for r in rows:
        variant = str(r["variant"])
        if variant in seen:
            continue
        seen.add(variant)
        md.append(
            f"| {variant} | `{r['dataset']}` | {r['ce_weight']} | {r['pair_weight']} | "
            f"{r['worst_weight']} | {r['anchor_kl_weight']} | {r['verdict']} |"
        )

    md += ["", "## Group metrics", ""]
    md += [
        "| variant | group | top5 Δ | top10 Δ | rank>50 Δ | mean_rank Δ | target_prob Δ | worst_gap Δ | hinge Δ |"
    ]
    md += ["|---|---|---:|---:|---:|---:|---:|---:|---:|"]
    for r in rows:
        md.append(
            f"| {r['variant']} | {r['group']} | {float(r['top5_delta']):.6f} | "
            f"{float(r['top10_delta']):.6f} | {float(r['rank_gt50_delta']):.6f} | "
            f"{float(r['mean_rank_delta']):.6f} | {float(r['mean_target_prob_delta']):.8f} | "
            f"{float(r['mean_worst_gap_delta']):.6f} | {float(r['hinge_delta']):.6f} |"
        )

    md += ["", "## Directional decision rule", ""]
    md.append(
        "A variant is directionally useful only if it improves train while avoiding protected top5/top10 loss and avoiding tail rank>50 regression."
    )
    md += ["", "## Final note", ""]
    md.append("This summary records no-save ablation metrics only. It does not authorize checkpoint save or promotion.")
    md.append("")

    summary_md = OUT_DIR / "run2_summary.md"
    summary_md.write_text("\n".join(md), encoding="utf-8")

    print()
    print("wrote", summary_csv)
    print("wrote", summary_md)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    for path in [WRAPPER, ANCHORS, B4C96]:
        require(path)
    for v in VARIANTS:
        require(Path(str(v["dataset"])))

    for v in VARIANTS:
        run_variant(v)

    summarize()

    print()
    print("run2 complete: no checkpoint save, no C export, no public benchmark, no promotion")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
