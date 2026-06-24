from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import torch

from gomoku_agent.checkpoint import load_compatible_checkpoint
from gomoku_agent.model import PolicyValueNet
from train_rapfi_teacher_policy_margin import masked_softmax, rank_of_action


DEFAULT_ANCHOR_SNAPSHOTS = Path("analysis/public_benchmark_eval/corpus8_selected_board_snapshots.json")


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description=(
            "No-promotion b4c96-safe policy rank/top-k gate wrapper for "
            "capacity-data pairing Stage C."
        )
    )
    ap.add_argument(
        "--dataset",
        type=Path,
        default=Path(
            "analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected.json"
        ),
    )
    ap.add_argument(
        "--model-a",
        type=Path,
        default=Path("checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt"),
    )
    ap.add_argument(
        "--model-b",
        type=Path,
        default=Path("checkpoints/probes/15x15_capacity_data_pairing_b4c96_probe_candidate.pt"),
    )
    ap.add_argument(
        "--out-csv",
        type=Path,
        default=Path("analysis/integration_eval/b4c96_safe_rank_topk_gate_metrics.csv"),
    )
    ap.add_argument(
        "--out-report",
        type=Path,
        default=Path("analysis/integration_eval/b4c96_safe_rank_topk_gate_report.md"),
    )
    ap.add_argument("--margin", type=float, default=1.0)
    ap.add_argument("--board-size", type=int, default=15)
    ap.add_argument("--win-length", type=int, default=5)
    ap.add_argument("--model-a-channels", type=int, default=64)
    ap.add_argument("--model-a-blocks", type=int, default=4)
    ap.add_argument("--model-b-channels", type=int, default=96)
    ap.add_argument("--model-b-blocks", type=int, default=4)
    return ap.parse_args()


def validate_arch_args(args: argparse.Namespace) -> None:
    if args.board_size <= 0:
        raise ValueError("--board-size must be positive")
    if args.win_length <= 0:
        raise ValueError("--win-length must be positive")
    if args.board_size < args.win_length:
        raise ValueError("--board-size must be >= --win-length")
    if args.model_a_channels <= 0:
        raise ValueError("--model-a-channels must be positive")
    if args.model_a_blocks <= 0:
        raise ValueError("--model-a-blocks must be positive")
    if args.model_b_channels <= 0:
        raise ValueError("--model-b-channels must be positive")
    if args.model_b_blocks <= 0:
        raise ValueError("--model-b-blocks must be positive")


def action_to_rc(action: int, board_size: int) -> list[int]:
    return [int(action) // board_size, int(action) % board_size]


def validate_rc(rc: list[int] | tuple[int, int], board_size: int) -> tuple[int, int]:
    if len(rc) != 2:
        raise ValueError(f"expected rc with length 2, got {rc!r}")
    row, col = int(rc[0]), int(rc[1])
    if not (0 <= row < board_size and 0 <= col < board_size):
        raise ValueError(f"rc out of range for {board_size}x{board_size}: {rc!r}")
    return row, col


def rc_to_action(rc: list[int] | tuple[int, int], board_size: int) -> int:
    row, col = validate_rc(rc, board_size)
    return row * board_size + col


def encode_state(board: list[list[int]], current_player: int, board_size: int) -> np.ndarray:
    grid = np.asarray(board, dtype=np.int8)
    if grid.shape != (board_size, board_size):
        raise ValueError(f"expected {board_size}x{board_size} board, got {grid.shape}")
    current = (grid == current_player).astype(np.float32)
    opponent = (grid == -current_player).astype(np.float32)
    last = np.zeros_like(current, dtype=np.float32)
    return np.stack([current, opponent, last], axis=0)


def legal_mask_from_board(board: list[list[int]], board_size: int) -> np.ndarray:
    grid = np.asarray(board, dtype=np.int8)
    if grid.shape != (board_size, board_size):
        raise ValueError(f"expected {board_size}x{board_size} board, got {grid.shape}")
    return (grid.reshape(-1) == 0).astype(np.float32)


def load_model(
    checkpoint: Path,
    device: torch.device,
    board_size: int,
    channels: int,
    blocks: int,
    win_length: int,
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


def load_multisuppress_dataset(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    dataset = json.loads(path.read_text(encoding="utf-8"))
    rows = dataset.get("samples", [])
    if not rows:
        raise ValueError(f"empty or missing samples in dataset: {path}")
    return dataset, rows


def same_model_path(a: Path, b: Path) -> bool:
    try:
        return a.resolve() == b.resolve()
    except FileNotFoundError:
        return str(a) == str(b)


def score_policy(
    model: torch.nn.Module,
    sample: dict[str, Any],
    device: torch.device,
    margin: float,
    board_size: int,
) -> dict[str, Any]:
    board = sample["board"]
    current_player = int(sample["current_player"])
    legal_np = legal_mask_from_board(board, board_size)

    target_action = rc_to_action(sample["target_rc"], board_size)
    suppress_actions = [rc_to_action(rc, board_size) for rc in sample["suppress_rcs"]]
    primary_action = rc_to_action(sample.get("primary_suppress_rc", sample["suppress_rcs"][0]), board_size)

    if legal_np[target_action] <= 0:
        raise ValueError(f"{sample['case_id']}: target illegal: {sample['target_rc']}")

    seen: set[int] = set()
    for action in suppress_actions:
        if legal_np[action] <= 0:
            raise ValueError(f"{sample['case_id']}: suppress illegal: {action_to_rc(action, board_size)}")
        if action == target_action:
            raise ValueError(f"{sample['case_id']}: suppress equals target: {action_to_rc(action, board_size)}")
        if action in seen:
            raise ValueError(f"{sample['case_id']}: duplicate suppress: {action_to_rc(action, board_size)}")
        seen.add(action)

    state = torch.tensor(
        encode_state(board, current_player, board_size),
        dtype=torch.float32,
        device=device,
    ).unsqueeze(0)
    mask = torch.tensor(legal_np, dtype=torch.float32, device=device).unsqueeze(0)

    with torch.no_grad():
        logits, _ = model(state)
        probs = masked_softmax(logits, mask)[0]

    logits0 = logits[0]
    mask0 = mask[0]
    target_logit = float(logits0[target_action].item())
    target_prob = float(probs[target_action].item())
    target_rank = int(rank_of_action(probs, target_action, mask0))

    suppress_records: list[dict[str, Any]] = []
    hinges: list[float] = []

    for action in suppress_actions:
        suppress_logit = float(logits0[action].item())
        gap = target_logit - suppress_logit
        hinge = max(0.0, margin - gap)
        hinges.append(hinge)
        suppress_records.append(
            {
                "rc": action_to_rc(action, board_size),
                "action": int(action),
                "prob": float(probs[action].item()),
                "rank": int(rank_of_action(probs, action, mask0)),
                "gap": float(gap),
                "hinge": float(hinge),
                "is_primary": int(action == primary_action),
            }
        )

    primary = next((r for r in suppress_records if r["is_primary"]), suppress_records[0])
    worst = min(suppress_records, key=lambda r: float(r["gap"]))

    return {
        "target_prob": target_prob,
        "target_rank": target_rank,
        "target_logit": target_logit,
        "primary_suppress_rc": primary["rc"],
        "primary_suppress_rank": int(primary["rank"]),
        "primary_gap": float(primary["gap"]),
        "worst_suppress_rc": worst["rc"],
        "worst_suppress_rank": int(worst["rank"]),
        "worst_suppress_gap": float(worst["gap"]),
        "multi_pair_hinge": float(np.mean(hinges)),
        "teacher_beats_primary": int(float(primary["gap"]) > 0.0),
        "teacher_beats_worst": int(float(worst["gap"]) > 0.0),
        "teacher_beats_all_suppressors": int(all(float(r["gap"]) > 0.0 for r in suppress_records)),
    }


def compare_sample(
    model_a: torch.nn.Module,
    model_b: torch.nn.Module,
    sample: dict[str, Any],
    device: torch.device,
    margin: float,
    board_size: int,
) -> dict[str, Any]:
    before = score_policy(model_a, sample, device, margin, board_size)
    after = score_policy(model_b, sample, device, margin, board_size)

    return {
        "case_id": sample["case_id"],
        "target_rc": sample["target_rc"],
        "suppress_count": len(sample["suppress_rcs"]),
        "target_rank_a": before["target_rank"],
        "target_rank_b": after["target_rank"],
        "target_rank_delta": int(after["target_rank"]) - int(before["target_rank"]),
        "target_prob_a": before["target_prob"],
        "target_prob_b": after["target_prob"],
        "target_prob_delta": float(after["target_prob"]) - float(before["target_prob"]),
        "primary_gap_a": before["primary_gap"],
        "primary_gap_b": after["primary_gap"],
        "primary_gap_delta": float(after["primary_gap"]) - float(before["primary_gap"]),
        "worst_suppress_rc_a": before["worst_suppress_rc"],
        "worst_suppress_rc_b": after["worst_suppress_rc"],
        "worst_suppress_gap_a": before["worst_suppress_gap"],
        "worst_suppress_gap_b": after["worst_suppress_gap"],
        "worst_suppress_gap_delta": float(after["worst_suppress_gap"]) - float(before["worst_suppress_gap"]),
        "multi_pair_hinge_a": before["multi_pair_hinge"],
        "multi_pair_hinge_b": after["multi_pair_hinge"],
        "multi_pair_hinge_delta": float(after["multi_pair_hinge"]) - float(before["multi_pair_hinge"]),
        "teacher_beats_primary_a": before["teacher_beats_primary"],
        "teacher_beats_primary_b": after["teacher_beats_primary"],
        "teacher_beats_worst_a": before["teacher_beats_worst"],
        "teacher_beats_worst_b": after["teacher_beats_worst"],
        "teacher_beats_all_suppressors_a": before["teacher_beats_all_suppressors"],
        "teacher_beats_all_suppressors_b": after["teacher_beats_all_suppressors"],
        "protected_top10_regression": int(int(before["target_rank"]) <= 10 and int(after["target_rank"]) > 10),
        "rank_gt50_a": int(int(before["target_rank"]) > 50),
        "rank_gt50_b": int(int(after["target_rank"]) > 50),
    }


def finite_check(rows: list[dict[str, Any]]) -> tuple[bool, list[str]]:
    problems: list[str] = []
    numeric_fields = [
        "target_prob_a",
        "target_prob_b",
        "target_prob_delta",
        "primary_gap_a",
        "primary_gap_b",
        "primary_gap_delta",
        "worst_suppress_gap_a",
        "worst_suppress_gap_b",
        "worst_suppress_gap_delta",
        "multi_pair_hinge_a",
        "multi_pair_hinge_b",
        "multi_pair_hinge_delta",
    ]
    for row in rows:
        for field in numeric_fields:
            value = float(row[field])
            if not math.isfinite(value):
                problems.append(f"{row['case_id']}: non-finite {field}={value}")
    return len(problems) == 0, problems


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    ranks_a = [int(r["target_rank_a"]) for r in rows]
    ranks_b = [int(r["target_rank_b"]) for r in rows]
    worst_a = [float(r["worst_suppress_gap_a"]) for r in rows]
    worst_b = [float(r["worst_suppress_gap_b"]) for r in rows]
    hinge_a = [float(r["multi_pair_hinge_a"]) for r in rows]
    hinge_b = [float(r["multi_pair_hinge_b"]) for r in rows]

    return {
        "rows": len(rows),
        "top3_a": int(sum(r <= 3 for r in ranks_a)),
        "top3_b": int(sum(r <= 3 for r in ranks_b)),
        "top5_a": int(sum(r <= 5 for r in ranks_a)),
        "top5_b": int(sum(r <= 5 for r in ranks_b)),
        "top10_a": int(sum(r <= 10 for r in ranks_a)),
        "top10_b": int(sum(r <= 10 for r in ranks_b)),
        "rank_gt50_a": int(sum(r > 50 for r in ranks_a)),
        "rank_gt50_b": int(sum(r > 50 for r in ranks_b)),
        "protected_top10_regressions": int(sum(int(r["protected_top10_regression"]) for r in rows)),
        "mean_target_rank_a": float(np.mean(ranks_a)),
        "mean_target_rank_b": float(np.mean(ranks_b)),
        "mean_worst_suppress_gap_a": float(np.mean(worst_a)),
        "mean_worst_suppress_gap_b": float(np.mean(worst_b)),
        "mean_multi_pair_hinge_a": float(np.mean(hinge_a)),
        "mean_multi_pair_hinge_b": float(np.mean(hinge_b)),
        "teacher_beats_worst_a": int(sum(int(r["teacher_beats_worst_a"]) for r in rows)),
        "teacher_beats_worst_b": int(sum(int(r["teacher_beats_worst_b"]) for r in rows)),
        "teacher_beats_all_suppressors_a": int(sum(int(r["teacher_beats_all_suppressors_a"]) for r in rows)),
        "teacher_beats_all_suppressors_b": int(sum(int(r["teacher_beats_all_suppressors_b"]) for r in rows)),
    }


def delta(summary: dict[str, Any], key: str) -> float:
    return float(summary[key + "_b"]) - float(summary[key + "_a"])


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "case_id",
        "target_rc",
        "suppress_count",
        "target_rank_a",
        "target_rank_b",
        "target_rank_delta",
        "target_prob_a",
        "target_prob_b",
        "target_prob_delta",
        "primary_gap_a",
        "primary_gap_b",
        "primary_gap_delta",
        "worst_suppress_rc_a",
        "worst_suppress_rc_b",
        "worst_suppress_gap_a",
        "worst_suppress_gap_b",
        "worst_suppress_gap_delta",
        "multi_pair_hinge_a",
        "multi_pair_hinge_b",
        "multi_pair_hinge_delta",
        "teacher_beats_primary_a",
        "teacher_beats_primary_b",
        "teacher_beats_worst_a",
        "teacher_beats_worst_b",
        "teacher_beats_all_suppressors_a",
        "teacher_beats_all_suppressors_b",
        "protected_top10_regression",
        "rank_gt50_a",
        "rank_gt50_b",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row[field] for field in fields})


def load_anchor_count(path: Path) -> tuple[int, str]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return len(raw), "loaded"
    except Exception as exc:
        return 0, f"not_loaded: {type(exc).__name__}: {exc}"


def gate_status(summary: dict[str, Any], finite_ok: bool, self_check: bool) -> tuple[str, list[str]]:
    checks: list[str] = []
    if self_check:
        checks.append("baseline-vs-baseline self-check; improvement thresholds are not applied")
        if finite_ok and all(
            abs(delta(summary, key)) < 1e-12
            for key in [
                "top3",
                "top5",
                "top10",
                "rank_gt50",
                "mean_worst_suppress_gap",
                "mean_multi_pair_hinge",
                "teacher_beats_worst",
                "teacher_beats_all_suppressors",
            ]
        ):
            return "PASS_SELF_CHECK", checks
        return "FAIL_SELF_CHECK", checks

    top3_delta = delta(summary, "top3")
    top5_delta = delta(summary, "top5")
    top10_delta = delta(summary, "top10")
    rank_gt50_delta = delta(summary, "rank_gt50")
    mean_worst_gap_delta = delta(summary, "mean_worst_suppress_gap")
    mean_hinge_delta = delta(summary, "mean_multi_pair_hinge")
    beats_worst_delta = delta(summary, "teacher_beats_worst")
    beats_all_delta = delta(summary, "teacher_beats_all_suppressors")

    checks.extend(
        [
            f"top3_delta >= +2: {top3_delta}",
            f"top5_delta >= +3: {top5_delta}",
            f"top10_delta >= +3: {top10_delta}",
            f"rank_gt50_delta <= 0: {rank_gt50_delta}",
            f"protected_top10_regressions == 0: {summary['protected_top10_regressions']}",
            f"mean_worst_suppress_gap_delta > 0: {mean_worst_gap_delta}",
            f"mean_multi_pair_hinge_delta < 0: {mean_hinge_delta}",
            f"teacher_beats_worst_delta >= +2: {beats_worst_delta}",
            f"teacher_beats_all_suppressors_delta >= +1: {beats_all_delta}",
        ]
    )

    passed = (
        finite_ok
        and top3_delta >= 2
        and top5_delta >= 3
        and top10_delta >= 3
        and rank_gt50_delta <= 0
        and int(summary["protected_top10_regressions"]) == 0
        and mean_worst_gap_delta > 0
        and mean_hinge_delta < 0
        and beats_worst_delta >= 2
        and beats_all_delta >= 1
    )
    return ("PASS_CANDIDATE_GATE" if passed else "FAIL_CANDIDATE_GATE"), checks


def write_report(
    path: Path,
    args: argparse.Namespace,
    dataset: dict[str, Any],
    rows: list[dict[str, Any]],
    summary: dict[str, Any],
    anchor_count: int,
    anchor_status: str,
    finite_ok: bool,
    finite_problems: list[str],
    verdict: str,
    checks: list[str],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    out: list[str] = []
    out += ["# b4c96-safe policy-only rank/top-k gate report", ""]
    out += ["## Scope", ""]
    out += ["- Evaluation only: no optimizer, no training, no checkpoint save."]
    out += ["- No C export, no public benchmark, no promotion, and manifest files are not modified."]
    out += [f"- Dataset: {args.dataset}"]
    out += [f"- Model A: {args.model_a}"]
    out += [f"- Model B: {args.model_b}"]
    out += [f"- Margin: {args.margin}"]
    out += [f"- Dataset name: {dataset.get('name', 'unknown')}"]
    out += [""]

    out += ["## Architecture", ""]
    out += [f"- board_size: {args.board_size}"]
    out += [f"- win_length: {args.win_length}"]
    out += [f"- model_a_channels: {args.model_a_channels}"]
    out += [f"- model_a_blocks: {args.model_a_blocks}"]
    out += [f"- model_b_channels: {args.model_b_channels}"]
    out += [f"- model_b_blocks: {args.model_b_blocks}"]
    out += [""]

    out += ["## Summary", ""]
    out += ["| metric | model_a | model_b | delta |"]
    out += ["|---|---:|---:|---:|"]
    for key, label in [
        ("top3", "target top-3 rows"),
        ("top5", "target top-5 rows"),
        ("top10", "target top-10 rows"),
        ("rank_gt50", "target rank > 50 rows"),
        ("mean_target_rank", "mean target rank"),
        ("mean_worst_suppress_gap", "mean worst suppress gap"),
        ("mean_multi_pair_hinge", "mean multi-pair hinge"),
        ("teacher_beats_worst", "teacher beats worst suppress rows"),
        ("teacher_beats_all_suppressors", "teacher beats all suppressors rows"),
    ]:
        a = summary[key + "_a"]
        b = summary[key + "_b"]
        d = float(b) - float(a)
        out.append(f"| {label} | {a} | {b} | {d} |")

    out += ["", "## Protected checks", ""]
    out += ["| check | value |", "|---|---:|"]
    out.append(f"| rows | {summary['rows']} |")
    out.append(f"| protected top-10 regressions | {summary['protected_top10_regressions']} |")
    out.append(f"| finite numeric checks passed | {finite_ok} |")
    out.append(f"| anchor rows loaded | {anchor_count} |")
    out.append(f"| anchor status | {anchor_status} |")

    out += ["", "## Gate checks", ""]
    out += ["| check | result |", "|---|---|"]
    for check in checks:
        out.append(f"| {check} | recorded |")

    out += ["", "## Worst target-rank rows after model B", ""]
    out += [
        "| case_id | target_rank_a | target_rank_b | target_prob_a | target_prob_b | worst_gap_a | worst_gap_b |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in sorted(rows, key=lambda r: int(r["target_rank_b"]), reverse=True)[:15]:
        out.append(
            "| {case_id} | {ra} | {rb} | {pa:.8f} | {pb:.8f} | {ga:.6f} | {gb:.6f} |".format(
                case_id=row["case_id"],
                ra=row["target_rank_a"],
                rb=row["target_rank_b"],
                pa=float(row["target_prob_a"]),
                pb=float(row["target_prob_b"]),
                ga=float(row["worst_suppress_gap_a"]),
                gb=float(row["worst_suppress_gap_b"]),
            )
        )

    if finite_problems:
        out += ["", "## Finite-check problems", ""]
        for problem in finite_problems[:50]:
            out.append(f"- {problem}")

    out += ["", "## Verdict", ""]
    out.append(verdict)
    out += ["", "## Decision", ""]
    out.append("Evaluation only. Do not train, export, public benchmark, promote, or modify manifest files from this wrapper.")
    out.append("")

    path.write_text("\n".join(out), encoding="utf-8")


def main() -> int:
    args = parse_args()
    validate_arch_args(args)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    dataset, samples = load_multisuppress_dataset(args.dataset)
    anchor_count, anchor_status = load_anchor_count(DEFAULT_ANCHOR_SNAPSHOTS)

    model_a = load_model(
        args.model_a,
        device,
        args.board_size,
        args.model_a_channels,
        args.model_a_blocks,
        args.win_length,
    )
    model_b = load_model(
        args.model_b,
        device,
        args.board_size,
        args.model_b_channels,
        args.model_b_blocks,
        args.win_length,
    )
    model_a.eval()
    model_b.eval()

    rows = [compare_sample(model_a, model_b, sample, device, args.margin, args.board_size) for sample in samples]
    finite_ok, finite_problems = finite_check(rows)
    summary = summarize(rows)

    self_check = same_model_path(args.model_a, args.model_b)
    verdict, checks = gate_status(summary, finite_ok, self_check)

    write_csv(args.out_csv, rows)
    write_report(
        args.out_report,
        args,
        dataset,
        rows,
        summary,
        anchor_count,
        anchor_status,
        finite_ok,
        finite_problems,
        verdict,
        checks,
    )

    print("device:", device)
    print("dataset:", args.dataset)
    print("model_a:", args.model_a)
    print("model_b:", args.model_b)
    print("board_size:", args.board_size)
    print("win_length:", args.win_length)
    print("model_a_channels:", args.model_a_channels)
    print("model_a_blocks:", args.model_a_blocks)
    print("model_b_channels:", args.model_b_channels)
    print("model_b_blocks:", args.model_b_blocks)
    print("rows:", len(rows))
    print("anchor_rows:", anchor_count)
    print("anchor_status:", anchor_status)
    print("top3_a:", summary["top3_a"], "top3_b:", summary["top3_b"], "delta:", delta(summary, "top3"))
    print("top5_a:", summary["top5_a"], "top5_b:", summary["top5_b"], "delta:", delta(summary, "top5"))
    print("top10_a:", summary["top10_a"], "top10_b:", summary["top10_b"], "delta:", delta(summary, "top10"))
    print(
        "rank_gt50_a:",
        summary["rank_gt50_a"],
        "rank_gt50_b:",
        summary["rank_gt50_b"],
        "delta:",
        delta(summary, "rank_gt50"),
    )
    print("mean_worst_suppress_gap_a:", "{:.6f}".format(summary["mean_worst_suppress_gap_a"]))
    print("mean_worst_suppress_gap_b:", "{:.6f}".format(summary["mean_worst_suppress_gap_b"]))
    print("mean_multi_pair_hinge_a:", "{:.6f}".format(summary["mean_multi_pair_hinge_a"]))
    print("mean_multi_pair_hinge_b:", "{:.6f}".format(summary["mean_multi_pair_hinge_b"]))
    print("finite_ok:", finite_ok)
    print("verdict:", verdict)
    print("out_csv:", args.out_csv)
    print("out_report:", args.out_report)
    print("evaluation only; no training/checkpoint/export/benchmark/promotion/manifest modification")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
