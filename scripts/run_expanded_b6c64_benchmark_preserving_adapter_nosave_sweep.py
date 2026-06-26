#!/usr/bin/env python3
from __future__ import annotations

import ast
import csv
import json
import os
import subprocess
import sys
from pathlib import Path


SCRIPT = Path("scripts/train_expanded_b6c64_benchmark_preserving_adapter.py")
INPUT = Path(
    "analysis/integration_eval/expanded_data_b6c64_benchmark_preserving_training_input_dryrun/"
    "benchmark_preserving_training_input_dryrun.json"
)
OUT_DIR = Path("analysis/integration_eval/expanded_data_b6c64_benchmark_preserving_adapter_nosave_sweep")
OUT_CSV = OUT_DIR / "adapter_nosave_sweep_summary.csv"
OUT_JSON = OUT_DIR / "adapter_nosave_sweep_summary.json"
OUT_MD = OUT_DIR / "adapter_nosave_sweep_report.md"
CKPT = Path("checkpoints/probes/15x15_expanded_b6c64_benchmark_preserving_adapter_candidate.pt")


CONFIGS = [
    {
        "name": "ce_only_lr5e7_wd0",
        "lr": 5e-7,
        "weight_decay": 0.0,
        "public_kl_weight": 0.0,
        "protected_kl_weight": 0.0,
        "tail_kl_weight": 0.0,
    },
    {
        "name": "ce_only_lr1e7_wd0",
        "lr": 1e-7,
        "weight_decay": 0.0,
        "public_kl_weight": 0.0,
        "protected_kl_weight": 0.0,
        "tail_kl_weight": 0.0,
    },
    {
        "name": "balanced_lr1e7_wd0",
        "lr": 1e-7,
        "weight_decay": 0.0,
        "public_kl_weight": 0.20,
        "protected_kl_weight": 0.35,
        "tail_kl_weight": 0.35,
    },
    {
        "name": "balanced_lr5e8_wd0",
        "lr": 5e-8,
        "weight_decay": 0.0,
        "public_kl_weight": 0.20,
        "protected_kl_weight": 0.35,
        "tail_kl_weight": 0.35,
    },
    {
        "name": "strong_kl_lr5e7_wd0",
        "lr": 5e-7,
        "weight_decay": 0.0,
        "public_kl_weight": 0.50,
        "protected_kl_weight": 0.75,
        "tail_kl_weight": 0.75,
    },
]


def parse_dict_line(stdout: str, prefix: str) -> dict:
    for line in stdout.splitlines():
        if line.startswith(prefix):
            return ast.literal_eval(line[len(prefix):].strip())
    raise RuntimeError(f"missing stdout line prefix {prefix!r}")


def read_history(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    if CKPT.exists():
        raise RuntimeError(f"checkpoint already exists; refusing sweep to preserve no-save invariant: {CKPT}")

    env = dict(os.environ)
    root = str(Path.cwd())
    env["PYTHONPATH"] = f"{root}:{root}/src" + (f":{env['PYTHONPATH']}" if env.get("PYTHONPATH") else "")

    rows = []
    details = []

    for cfg in CONFIGS:
        name = cfg["name"]
        run_dir = OUT_DIR / name
        run_dir.mkdir(parents=True, exist_ok=True)
        out_csv = run_dir / "adapter_train_history.csv"
        out_report = run_dir / "adapter_train_report.md"
        stdout_path = run_dir / "stdout.txt"
        stderr_path = run_dir / "stderr.txt"

        cmd = [
            sys.executable,
            str(SCRIPT),
            "--input",
            str(INPUT),
            "--init-checkpoint",
            "checkpoints/15x15_capacity_a_b6c64_train_v2.pt",
            "--reference-checkpoint",
            "checkpoints/15x15_capacity_a_b6c64_train_v2.pt",
            "--out-checkpoint",
            str(CKPT),
            "--out-csv",
            str(out_csv),
            "--out-report",
            str(out_report),
            "--board-size",
            "15",
            "--channels",
            "64",
            "--blocks",
            "6",
            "--win-length",
            "5",
            "--epochs",
            "1",
            "--lr",
            str(cfg["lr"]),
            "--weight-decay",
            str(cfg["weight_decay"]),
            "--ce-weight",
            "1.0",
            "--public-kl-weight",
            str(cfg["public_kl_weight"]),
            "--protected-kl-weight",
            str(cfg["protected_kl_weight"]),
            "--tail-kl-weight",
            str(cfg["tail_kl_weight"]),
            "--seed",
            "43",
            "--print-every",
            "1",
            "--no-save",
        ]

        print(f"=== run {name} ===", flush=True)
        proc = subprocess.run(cmd, text=True, capture_output=True, env=env)
        stdout_path.write_text(proc.stdout, encoding="utf-8")
        stderr_path.write_text(proc.stderr, encoding="utf-8")

        if CKPT.exists():
            raise RuntimeError(f"no-save invariant violated; checkpoint exists after {name}: {CKPT}")

        base_row = {
            "name": name,
            "returncode": proc.returncode,
            "lr": cfg["lr"],
            "weight_decay": cfg["weight_decay"],
            "public_kl_weight": cfg["public_kl_weight"],
            "protected_kl_weight": cfg["protected_kl_weight"],
            "tail_kl_weight": cfg["tail_kl_weight"],
            "stdout": str(stdout_path),
            "stderr": str(stderr_path),
            "history_csv": str(out_csv),
            "report": str(out_report),
            "checkpoint_exists": int(CKPT.exists()),
        }

        if proc.returncode != 0:
            row = {
                **base_row,
                "status": "ERROR",
                "reason": f"returncode={proc.returncode}",
            }
            rows.append(row)
            details.append({"config": cfg, "row": row, "stdout": proc.stdout, "stderr": proc.stderr})
            print(f"{name}: ERROR returncode={proc.returncode}", flush=True)
            continue

        before = parse_dict_line(proc.stdout, "before_ce:")
        after = parse_dict_line(proc.stdout, "after_ce:")
        hist = read_history(out_csv)
        initial = next(r for r in hist if r["phase"] == "initial")
        train = next(r for r in hist if r["phase"] == "train")

        top3_delta = int(after["top3"]) - int(before["top3"])
        top5_delta = int(after["top5"]) - int(before["top5"])
        top10_delta = int(after["top10"]) - int(before["top10"])
        rank_gt50_delta = int(after["rank_gt50"]) - int(before["rank_gt50"])
        mean_rank_delta = float(after["mean_rank"]) - float(before["mean_rank"])
        mean_prob_delta = float(after["mean_target_prob"]) - float(before["mean_target_prob"])
        ce_loss_delta = float(train["ce_loss"]) - float(initial["ce_loss"])

        hard_pass = (
            top3_delta >= 0
            and top5_delta >= 0
            and top10_delta >= 0
            and rank_gt50_delta <= 0
            and mean_rank_delta <= 0.0
            and mean_prob_delta >= 0.0
        )

        soft_pass = (
            top5_delta >= 0
            and top10_delta >= 0
            and rank_gt50_delta <= 0
            and mean_rank_delta <= 0.0
            and mean_prob_delta >= 0.0
        )

        if hard_pass:
            status = "PASS_HARD_NO_SAVE"
        elif soft_pass:
            status = "PASS_SOFT_TOP3_WARNING_NO_SAVE"
        else:
            status = "FAIL_NO_SAVE"

        row = {
            **base_row,
            "status": status,
            "before_top3": before["top3"],
            "after_top3": after["top3"],
            "top3_delta": top3_delta,
            "before_top5": before["top5"],
            "after_top5": after["top5"],
            "top5_delta": top5_delta,
            "before_top10": before["top10"],
            "after_top10": after["top10"],
            "top10_delta": top10_delta,
            "before_rank_gt50": before["rank_gt50"],
            "after_rank_gt50": after["rank_gt50"],
            "rank_gt50_delta": rank_gt50_delta,
            "before_mean_rank": before["mean_rank"],
            "after_mean_rank": after["mean_rank"],
            "mean_rank_delta": mean_rank_delta,
            "before_mean_target_prob": before["mean_target_prob"],
            "after_mean_target_prob": after["mean_target_prob"],
            "mean_target_prob_delta": mean_prob_delta,
            "initial_loss": initial["loss"],
            "train_loss": train["loss"],
            "initial_ce_loss": initial["ce_loss"],
            "train_ce_loss": train["ce_loss"],
            "ce_loss_delta": ce_loss_delta,
            "train_public_kl": train["public_kl"],
            "train_protected_kl": train["protected_kl"],
            "train_tail_kl": train["tail_kl"],
            "diagnostic_mode_before": before.get("diagnostic_mode"),
            "diagnostic_mode_after": after.get("diagnostic_mode"),
        }
        rows.append(row)
        details.append({"config": cfg, "row": row, "before": before, "after": after})

        print(
            f"{name}: {status} "
            f"top3_delta={top3_delta} rank_gt50_delta={rank_gt50_delta} "
            f"mean_rank_delta={mean_rank_delta:.3f} prob_delta={mean_prob_delta:.8f}",
            flush=True,
        )

    fields = [
        "name",
        "status",
        "returncode",
        "lr",
        "weight_decay",
        "public_kl_weight",
        "protected_kl_weight",
        "tail_kl_weight",
        "before_top3",
        "after_top3",
        "top3_delta",
        "before_top5",
        "after_top5",
        "top5_delta",
        "before_top10",
        "after_top10",
        "top10_delta",
        "before_rank_gt50",
        "after_rank_gt50",
        "rank_gt50_delta",
        "before_mean_rank",
        "after_mean_rank",
        "mean_rank_delta",
        "before_mean_target_prob",
        "after_mean_target_prob",
        "mean_target_prob_delta",
        "initial_loss",
        "train_loss",
        "initial_ce_loss",
        "train_ce_loss",
        "ce_loss_delta",
        "train_public_kl",
        "train_protected_kl",
        "train_tail_kl",
        "diagnostic_mode_before",
        "diagnostic_mode_after",
        "checkpoint_exists",
        "history_csv",
        "report",
        "stdout",
        "stderr",
        "reason",
    ]

    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fields})

    summary = {
        "decision": "NO_SAVE_SWEEP_COMPLETE",
        "not_checkpoint": True,
        "not_export": True,
        "not_public_benchmark": True,
        "not_promotion": True,
        "candidate_checkpoint_exists": CKPT.exists(),
        "rows": rows,
        "recommended_configs": [
            r for r in rows if r.get("status") in {"PASS_HARD_NO_SAVE", "PASS_SOFT_TOP3_WARNING_NO_SAVE"}
        ],
    }
    OUT_JSON.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    lines = []
    lines.append("# Expanded b6c64 benchmark-preserving adapter no-save sweep")
    lines.append("")
    lines.append("- decision: `NO_SAVE_SWEEP_COMPLETE`")
    lines.append("- no checkpoint")
    lines.append("- no export")
    lines.append("- no public benchmark")
    lines.append("- no promotion/current_best overwrite")
    lines.append("")
    lines.append("## Results")
    lines.append("")
    lines.append("| config | status | top3 Δ | top5 Δ | top10 Δ | rank>50 Δ | mean_rank Δ | target_prob Δ | train public KL |")
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|---:|")
    for r in rows:
        lines.append(
            f"| `{r.get('name')}` | `{r.get('status')}` | {r.get('top3_delta', '')} | "
            f"{r.get('top5_delta', '')} | {r.get('top10_delta', '')} | {r.get('rank_gt50_delta', '')} | "
            f"{float(r.get('mean_rank_delta', 0.0)):.3f} | {float(r.get('mean_target_prob_delta', 0.0)):.8f} | "
            f"{float(r.get('train_public_kl', 0.0)):.6f} |"
        )
    lines.append("")
    lines.append("## Selection rule")
    lines.append("")
    lines.append("- Hard pass requires no top3/top5/top10 regression, no rank>50 increase, mean rank not worse, and target probability not worse.")
    lines.append("- Soft pass allows only top3 warning if all broader metrics improve.")
    lines.append("- No saved candidate should be created unless at least one no-save sweep config passes.")
    lines.append("")
    lines.append("## Artifacts")
    lines.append("")
    lines.append(f"- summary CSV: `{OUT_CSV}`")
    lines.append(f"- summary JSON: `{OUT_JSON}`")
    lines.append("")
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print()
    print("decision: NO_SAVE_SWEEP_COMPLETE")
    print("candidate_checkpoint_exists:", CKPT.exists())
    print("recommended_configs:", [r["name"] for r in summary["recommended_configs"]])
    print("wrote:", OUT_CSV)
    print("wrote:", OUT_JSON)
    print("wrote:", OUT_MD)


if __name__ == "__main__":
    main()
