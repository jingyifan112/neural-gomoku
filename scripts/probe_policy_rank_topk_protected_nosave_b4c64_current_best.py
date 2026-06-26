#!/usr/bin/env python3
# SAFETY NOTE:
# This wrapper is for b4c64/current-best no-save rank/top-k probing only.
# It must not save checkpoints, export C weights, run public benchmarks, promote,
# or overwrite current-best. Optimizer updates are in-memory only.
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

import numpy as np
import torch

from gomoku_agent.checkpoint import load_compatible_checkpoint
from gomoku_agent.model import PolicyValueNet
from train_rapfi_teacher_policy_rank_topk_probe import (
    load_anchor_samples,
    make_anchor_tensors,
    make_multisuppress_tensors,
    diagnose_summary,
    train,
)


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description=(
            "b4c64/current-best-safe no-save protected rank/top-k objective ablation wrapper. "
            "Optimizer runs in memory only; no checkpoint is saved."
        )
    )
    ap.add_argument(
        "--dataset",
        type=Path,
        default=Path(
            "analysis/public_benchmark_eval/"
            "rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_protected_train_11_50_weightcap3.json"
        ),
    )
    ap.add_argument(
        "--anchor-snapshots",
        type=Path,
        default=Path("analysis/public_benchmark_eval/corpus8_selected_board_snapshots.json"),
    )
    ap.add_argument(
        "--init-checkpoint",
        type=Path,
        default=Path("checkpoints/15x15_current_best.pt"),
    )
    ap.add_argument(
        "--reference-checkpoint",
        type=Path,
        default=Path("checkpoints/15x15_current_best.pt"),
    )
    ap.add_argument("--board-size", type=int, default=15)
    ap.add_argument("--win-length", type=int, default=5)
    ap.add_argument("--channels", type=int, default=64)
    ap.add_argument("--blocks", type=int, default=4)
    ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument("--lr", type=float, default=1e-6)
    ap.add_argument("--margin", type=float, default=0.25)
    ap.add_argument("--ce-weight", type=float, default=1.0)
    ap.add_argument("--pair-weight", type=float, default=0.0)
    ap.add_argument("--worst-weight", type=float, default=0.0)
    ap.add_argument("--anchor-kl-weight", type=float, default=0.05)
    ap.add_argument("--weight-decay", type=float, default=1e-5)
    ap.add_argument("--seed", type=int, default=37)
    ap.add_argument("--print-every", type=int, default=1)
    ap.add_argument(
        "--out-csv",
        type=Path,
        default=Path(
            "analysis/integration_eval/b4c64_current_best_safe_nosave_ablation_wrapper/"
            "protected_nosave_group_metrics.csv"
        ),
    )
    ap.add_argument(
        "--out-report",
        type=Path,
        default=Path(
            "analysis/integration_eval/b4c64_current_best_safe_nosave_ablation_wrapper/"
            "protected_nosave_report.md"
        ),
    )
    return ap.parse_args()


def validate_args(args: argparse.Namespace) -> None:
    if args.board_size != 15:
        raise ValueError("this wrapper is currently scoped to board-size 15 only")
    if args.win_length != 5:
        raise ValueError("this wrapper is currently scoped to win-length 5 only")
    if args.channels <= 0:
        raise ValueError("--channels must be positive")
    if args.blocks <= 0:
        raise ValueError("--blocks must be positive")
    if args.epochs <= 0:
        raise ValueError("--epochs must be positive")
    # current_best is the intended safe init/reference default for this b4c64 no-save wrapper.


def load_model_b4c64_current_best(
    checkpoint: Path,
    device: torch.device,
    board_size: int,
    win_length: int,
    channels: int,
    blocks: int,
) -> PolicyValueNet:
    model = PolicyValueNet(board_size=board_size, channels=channels, blocks=blocks).to(device)
    model.win_length = win_length
    loaded = load_compatible_checkpoint(
        model,
        checkpoint,
        device,
        board_size=board_size,
        channels=channels,
        blocks=blocks,
    )
    if not loaded:
        raise RuntimeError(
            f"could not load compatible checkpoint: {checkpoint} "
            f"for board_size={board_size} channels={channels} blocks={blocks}"
        )
    return model


def load_protected_dataset(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    required = ["samples", "protected_eval_samples", "tail_eval_samples"]
    for key in required:
        if key not in data:
            raise ValueError(f"missing {key} in protected dataset: {path}")
    if not data["samples"]:
        raise ValueError("empty train samples")
    return data


def summarize_delta(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    keys = [
        "rows",
        "top3",
        "top5",
        "top10",
        "rank_gt50",
        "mean_rank",
        "mean_target_prob",
        "mean_worst_gap",
        "mean_pair_hinge_margin_025",
        "teacher_beats_worst",
        "teacher_beats_all",
    ]
    out: dict[str, Any] = {}
    for key in keys:
        out[f"{key}_before"] = before[key]
        out[f"{key}_after"] = after[key]
        if key != "rows":
            out[f"{key}_delta"] = float(after[key]) - float(before[key])
    return out


def verdict(group_rows: list[dict[str, Any]]) -> str:
    by_group = {r["group"]: r for r in group_rows}
    train_group = by_group["train_main_rank_11_50"]
    protected_group = by_group["protected_eval_top10"]
    tail_group = by_group["tail_eval_rank_gt50"]

    train_ok = (
        float(train_group["top10_delta"]) >= 0
        and float(train_group["mean_rank_delta"]) <= 0
        and float(train_group["mean_target_prob_delta"]) >= -1e-6
    )
    protected_ok = (
        float(protected_group["top10_delta"]) >= 0
        and float(protected_group["rank_gt50_delta"]) <= 0
        and float(protected_group["mean_target_prob_delta"]) >= -0.002
    )
    tail_ok = (
        float(tail_group["rank_gt50_delta"]) <= 0
        and float(tail_group["mean_rank_delta"]) <= 5
    )

    if train_ok and protected_ok and tail_ok:
        return "PASS_B4C64_CURRENT_BEST_SAFE_NO_SAVE_PROBE"
    return "FAIL_B4C64_CURRENT_BEST_SAFE_NO_SAVE_PROBE"


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["group"]
    fields += [
        "rows_before",
        "rows_after",
        "top3_before",
        "top3_after",
        "top3_delta",
        "top5_before",
        "top5_after",
        "top5_delta",
        "top10_before",
        "top10_after",
        "top10_delta",
        "rank_gt50_before",
        "rank_gt50_after",
        "rank_gt50_delta",
        "mean_rank_before",
        "mean_rank_after",
        "mean_rank_delta",
        "mean_target_prob_before",
        "mean_target_prob_after",
        "mean_target_prob_delta",
        "mean_worst_gap_before",
        "mean_worst_gap_after",
        "mean_worst_gap_delta",
        "mean_pair_hinge_margin_025_before",
        "mean_pair_hinge_margin_025_after",
        "mean_pair_hinge_margin_025_delta",
        "teacher_beats_worst_before",
        "teacher_beats_worst_after",
        "teacher_beats_worst_delta",
        "teacher_beats_all_before",
        "teacher_beats_all_after",
        "teacher_beats_all_delta",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fields})


def write_report(
    path: Path,
    args: argparse.Namespace,
    data: dict[str, Any],
    rows: list[dict[str, Any]],
    history: list[dict[str, float]],
    final_verdict: str,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    lines += ["# b4c64/current-best-safe protected no-save objective ablation wrapper report", ""]
    lines += ["## Scope", ""]
    lines += [
        "- b4c64/current-best-safe no-save probe only.",
        "- Optimizer runs in memory.",
        "- No checkpoint is saved.",
        "- No C export, no public benchmark, no promotion.",
        "",
    ]

    lines += ["## Architecture", ""]
    lines += [
        f"- board_size: {args.board_size}",
        f"- win_length: {args.win_length}",
        f"- channels: {args.channels}",
        f"- blocks: {args.blocks}",
        "",
    ]

    lines += ["## Inputs", ""]
    lines += [
        f"- dataset: `{args.dataset}`",
        f"- dataset_name: `{data.get('name', 'unknown')}`",
        f"- init_checkpoint: `{args.init_checkpoint}`",
        f"- reference_checkpoint: `{args.reference_checkpoint}`",
        f"- epochs: {args.epochs}",
        f"- lr: {args.lr}",
        f"- margin: {args.margin}",
        f"- ce_weight: {args.ce_weight}",
        f"- pair_weight: {args.pair_weight}",
        f"- worst_weight: {args.worst_weight}",
        f"- anchor_kl_weight: {args.anchor_kl_weight}",
        "",
    ]

    lines += ["## Group metrics", ""]
    lines += [
        "| group | rows | top3 delta | top5 delta | top10 delta | rank_gt50 delta | mean_rank delta | target_prob delta | mean_worst_gap delta | hinge delta | beats_worst delta | beats_all delta |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in rows:
        lines.append(
            f"| {r['group']} | {r['rows_before']} | "
            f"{float(r['top3_delta']):.6f} | {float(r['top5_delta']):.6f} | "
            f"{float(r['top10_delta']):.6f} | {float(r['rank_gt50_delta']):.6f} | "
            f"{float(r['mean_rank_delta']):.6f} | {float(r['mean_target_prob_delta']):.8f} | "
            f"{float(r['mean_worst_gap_delta']):.6f} | "
            f"{float(r['mean_pair_hinge_margin_025_delta']):.6f} | "
            f"{float(r['teacher_beats_worst_delta']):.6f} | "
            f"{float(r['teacher_beats_all_delta']):.6f} |"
        )

    if history:
        final = history[-1]
        lines += ["", "## Final training terms", ""]
        lines += ["| term | value |", "|---|---:|"]
        for key in [
            "loss",
            "ce_loss",
            "pair_hinge_loss",
            "worst_hinge_loss",
            "anchor_kl",
            "mean_gap",
            "mean_worst_gap",
        ]:
            lines.append(f"| {key} | {final[key]:.8f} |")

    lines += ["", "## Verdict", "", final_verdict, ""]
    lines += ["## Decision", ""]
    lines += [
        "No checkpoint was saved.",
        "If the no-save probe fails, the next step should be another objective/data design change, not a saved run.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    args = parse_args()
    validate_args(args)

    torch.manual_seed(args.seed)
    np.random.seed(args.seed)

    data = load_protected_dataset(args.dataset)
    groups = [
        ("train_main_rank_11_50", data["samples"]),
        ("protected_eval_top10", data["protected_eval_samples"]),
        ("tail_eval_rank_gt50", data["tail_eval_samples"]),
    ]

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model = load_model_b4c64_current_best(
        args.init_checkpoint,
        device,
        args.board_size,
        args.win_length,
        args.channels,
        args.blocks,
    )
    reference_model = load_model_b4c64_current_best(
        args.reference_checkpoint,
        device,
        args.board_size,
        args.win_length,
        args.channels,
        args.blocks,
    )
    reference_model.eval()
    for p in reference_model.parameters():
        p.requires_grad = False

    anchors = load_anchor_samples(args.anchor_snapshots)
    anchor_tensors = make_anchor_tensors(anchors, device)
    train_tensors = make_multisuppress_tensors(data["samples"], device)

    before = {
        name: diagnose_summary(model, samples, device)
        for name, samples in groups
    }

    history = train(
        model,
        reference_model,
        train_tensors,
        anchor_tensors,
        args,
    )

    after = {
        name: diagnose_summary(model, samples, device)
        for name, samples in groups
    }

    rows: list[dict[str, Any]] = []
    for name, _samples in groups:
        row = {"group": name}
        row.update(summarize_delta(before[name], after[name]))
        rows.append(row)

    final_verdict = verdict(rows)

    write_csv(args.out_csv, rows)
    write_report(args.out_report, args, data, rows, history, final_verdict)

    print("device:", device)
    print("dataset:", args.dataset)
    print("init_checkpoint:", args.init_checkpoint)
    print("reference_checkpoint:", args.reference_checkpoint)
    print("board_size:", args.board_size)
    print("win_length:", args.win_length)
    print("channels:", args.channels)
    print("blocks:", args.blocks)
    print("train_rows:", len(data["samples"]))
    print("protected_rows:", len(data["protected_eval_samples"]))
    print("tail_rows:", len(data["tail_eval_samples"]))
    for row in rows:
        print(
            row["group"],
            "top10_delta=", row["top10_delta"],
            "rank_gt50_delta=", row["rank_gt50_delta"],
            "mean_rank_delta=", row["mean_rank_delta"],
            "target_prob_delta=", row["mean_target_prob_delta"],
        )
    print("verdict:", final_verdict)
    print("out_csv:", args.out_csv)
    print("out_report:", args.out_report)
    print("b4c64/current-best-safe no-save probe complete; no checkpoint saved")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
