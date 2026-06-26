#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
import torch

from train_rapfi_teacher_policy_rank_topk_b4c96_probe import (
    action_to_rc,
    encode_state,
    legal_mask_from_board,
    load_model,
    rc_to_action,
)
from train_rapfi_teacher_policy_margin import (
    configure_policy_head_trainable,
    masked_log_softmax,
    masked_softmax,
    rank_of_action,
    set_policy_head_training_mode,
)


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="No-save benchmark-preserving adapter for expanded b6c64 teacher-divergence repair."
    )
    ap.add_argument(
        "--input",
        type=Path,
        default=Path(
            "analysis/integration_eval/expanded_data_b6c64_benchmark_preserving_training_input_dryrun/"
            "benchmark_preserving_training_input_dryrun.json"
        ),
    )
    ap.add_argument(
        "--init-checkpoint",
        type=Path,
        default=Path("checkpoints/15x15_capacity_a_b6c64_train_v2.pt"),
    )
    ap.add_argument(
        "--reference-checkpoint",
        type=Path,
        default=Path("checkpoints/15x15_capacity_a_b6c64_train_v2.pt"),
    )
    ap.add_argument(
        "--out-checkpoint",
        type=Path,
        default=Path("checkpoints/probes/15x15_expanded_b6c64_benchmark_preserving_adapter_candidate.pt"),
    )
    ap.add_argument(
        "--out-csv",
        type=Path,
        default=Path(
            "analysis/integration_eval/expanded_data_b6c64_benchmark_preserving_adapter_nosave/"
            "adapter_train_history.csv"
        ),
    )
    ap.add_argument(
        "--out-report",
        type=Path,
        default=Path(
            "analysis/integration_eval/expanded_data_b6c64_benchmark_preserving_adapter_nosave/"
            "adapter_train_report.md"
        ),
    )
    ap.add_argument("--board-size", type=int, default=15)
    ap.add_argument("--channels", type=int, default=64)
    ap.add_argument("--blocks", type=int, default=6)
    ap.add_argument("--win-length", type=int, default=5)
    ap.add_argument("--epochs", type=int, default=1)
    ap.add_argument("--lr", type=float, default=5e-7)
    ap.add_argument("--weight-decay", type=float, default=1e-4)
    ap.add_argument("--ce-weight", type=float, default=1.0)
    ap.add_argument("--public-kl-weight", type=float, default=0.20)
    ap.add_argument("--protected-kl-weight", type=float, default=0.35)
    ap.add_argument("--tail-kl-weight", type=float, default=0.35)
    ap.add_argument("--seed", type=int, default=43)
    ap.add_argument("--print-every", type=int, default=1)
    ap.add_argument("--no-save", action="store_true")
    return ap.parse_args()


def assert_safe_out_checkpoint(path: Path, *, will_save: bool) -> None:
    if "current_best" in path.name or any("current_best" in part for part in path.parts):
        raise ValueError(f"refusing out-checkpoint containing current_best: {path}")
    if will_save and path.exists():
        raise FileExistsError(f"refusing to overwrite existing checkpoint: {path}")


def parse_side(side: Any) -> int:
    if isinstance(side, int):
        if side in (1, -1):
            return side
    s = str(side).strip().lower()
    if s in {"black", "b", "x", "1"}:
        return 1
    if s in {"white", "w", "o", "-1"}:
        return -1
    raise ValueError(f"cannot parse side/current_player: {side!r}")


def parse_board_rows(rows: list[str], board_size: int) -> list[list[int]]:
    board: list[list[int]] = []
    for raw in rows:
        line = str(raw).strip()
        if " " in line:
            tokens = line.split()
        else:
            tokens = list(line)
        if len(tokens) != board_size:
            raise ValueError(f"board_rows expected width {board_size}, got {len(tokens)} in {raw!r}")
        parsed = []
        for token in tokens:
            if token == ".":
                parsed.append(0)
            elif token == "X":
                parsed.append(1)
            elif token == "O":
                parsed.append(-1)
            else:
                raise ValueError(f"unexpected board token {token!r}")
        board.append(parsed)
    if len(board) != board_size:
        raise ValueError(f"board_rows expected height {board_size}, got {len(board)}")
    return board


def board_and_player(payload: dict[str, Any], board_size: int) -> tuple[list[list[int]], int]:
    if "board" in payload:
        board = [[int(x) for x in row] for row in payload["board"]]
    elif "board_rows" in payload:
        board = parse_board_rows(payload["board_rows"], board_size)
    else:
        raise ValueError(f"payload missing board/board_rows keys: {sorted(payload.keys())}")

    if len(board) != board_size or any(len(row) != board_size for row in board):
        raise ValueError(f"bad board shape, expected {board_size}x{board_size}")

    if "current_player" in payload:
        current_player = parse_side(payload["current_player"])
    elif "side_to_move" in payload:
        current_player = parse_side(payload["side_to_move"])
    elif "side" in payload:
        current_player = parse_side(payload["side"])
    else:
        raise ValueError("payload missing current_player/side_to_move/side")

    return board, current_player


def split_records(doc: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for rec in doc["training_records"]:
        groups.setdefault(rec["group"], []).append(rec)
    return groups


def make_state_mask_tensors(
    records: list[dict[str, Any]],
    device: torch.device,
    board_size: int,
) -> tuple[torch.Tensor, torch.Tensor]:
    states = []
    masks = []
    for rec in records:
        board, current_player = board_and_player(rec["payload"], board_size)
        states.append(encode_state(board, current_player, board_size))
        masks.append(legal_mask_from_board(board, board_size))
    return (
        torch.tensor(np.stack(states), dtype=torch.float32, device=device),
        torch.tensor(np.stack(masks), dtype=torch.float32, device=device),
    )


def make_ce_tensors(
    records: list[dict[str, Any]],
    device: torch.device,
    board_size: int,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    states = []
    masks = []
    actions = []

    for rec in records:
        payload = rec["payload"]
        board, current_player = board_and_player(payload, board_size)
        action = rc_to_action(payload["target_rc"], board_size)
        mask = legal_mask_from_board(board, board_size)
        if mask[action] <= 0:
            raise ValueError(f"{rec['input_id']}: target_rc illegal: {payload['target_rc']}")
        states.append(encode_state(board, current_player, board_size))
        masks.append(mask)
        actions.append(action)

    return (
        torch.tensor(np.stack(states), dtype=torch.float32, device=device),
        torch.tensor(np.stack(masks), dtype=torch.float32, device=device),
        torch.tensor(actions, dtype=torch.long, device=device),
    )


@torch.no_grad()
def reference_probs(
    reference_model: torch.nn.Module,
    states: torch.Tensor,
    masks: torch.Tensor,
) -> torch.Tensor:
    logits, _ = reference_model(states)
    return masked_softmax(logits, masks)


def kl_to_reference(
    model: torch.nn.Module,
    states: torch.Tensor,
    masks: torch.Tensor,
    ref_probs: torch.Tensor,
) -> torch.Tensor:
    logits, _ = model(states)
    log_probs = masked_log_softmax(logits, masks)
    return (ref_probs * (torch.log(ref_probs.clamp_min(1e-12)) - log_probs)).sum(dim=-1).mean()


def compute_terms(
    model: torch.nn.Module,
    ce_tensors: tuple[torch.Tensor, torch.Tensor, torch.Tensor],
    public_tensors: tuple[torch.Tensor, torch.Tensor],
    protected_tensors: tuple[torch.Tensor, torch.Tensor],
    tail_tensors: tuple[torch.Tensor, torch.Tensor],
    ref_public_probs: torch.Tensor,
    ref_protected_probs: torch.Tensor,
    ref_tail_probs: torch.Tensor,
    args: argparse.Namespace,
) -> dict[str, torch.Tensor]:
    ce_states, ce_masks, ce_actions = ce_tensors
    logits, _ = model(ce_states)
    log_probs = masked_log_softmax(logits, ce_masks)
    ce_loss = -log_probs.gather(1, ce_actions.unsqueeze(1)).squeeze(1).mean()

    public_kl = kl_to_reference(model, public_tensors[0], public_tensors[1], ref_public_probs)
    protected_kl = kl_to_reference(model, protected_tensors[0], protected_tensors[1], ref_protected_probs)
    tail_kl = kl_to_reference(model, tail_tensors[0], tail_tensors[1], ref_tail_probs)

    loss = (
        args.ce_weight * ce_loss
        + args.public_kl_weight * public_kl
        + args.protected_kl_weight * protected_kl
        + args.tail_kl_weight * tail_kl
    )

    return {
        "loss": loss,
        "ce_loss": ce_loss,
        "public_kl": public_kl,
        "protected_kl": protected_kl,
        "tail_kl": tail_kl,
    }


def assert_finite(terms: dict[str, torch.Tensor], label: str) -> None:
    bad = []
    for k, v in terms.items():
        x = float(v.detach().item())
        if not math.isfinite(x):
            bad.append(f"{k}={x}")
    if bad:
        raise RuntimeError(f"non-finite {label}: {', '.join(bad)}")


@torch.no_grad()
def diagnose_ce_rows(
    model: torch.nn.Module,
    records: list[dict[str, Any]],
    device: torch.device,
    board_size: int,
) -> dict[str, Any]:
    # Public benchmark / C export uses inference behavior, so diagnostics must be eval-mode.
    was_training = model.training
    model.eval()
    try:
        ranks = []
        probs = []
        for rec in records:
            payload = rec["payload"]
            board, current_player = board_and_player(payload, board_size)
            mask_np = legal_mask_from_board(board, board_size)
            action = rc_to_action(payload["target_rc"], board_size)

            state = torch.tensor(
                encode_state(board, current_player, board_size),
                dtype=torch.float32,
                device=device,
            ).unsqueeze(0)
            mask = torch.tensor(mask_np, dtype=torch.float32, device=device).unsqueeze(0)

            logits, _ = model(state)
            prob = masked_softmax(logits, mask)[0]
            ranks.append(int(rank_of_action(prob, action, mask[0])))
            probs.append(float(prob[action].item()))

        return {
            "rows": len(records),
            "top3": int(sum(r <= 3 for r in ranks)),
            "top5": int(sum(r <= 5 for r in ranks)),
            "top10": int(sum(r <= 10 for r in ranks)),
            "rank_gt50": int(sum(r > 50 for r in ranks)),
            "mean_rank": float(np.mean(ranks)),
            "mean_target_prob": float(np.mean(probs)),
            "diagnostic_mode": "eval",
        }
    finally:
        if was_training:
            model.train()

def write_history_csv(path: Path, initial: dict[str, torch.Tensor], history: list[dict[str, float]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["phase", "epoch", "loss", "ce_loss", "public_kl", "protected_kl", "tail_kl"]
    rows = [
        {
            "phase": "initial",
            "epoch": 0,
            **{k: float(initial[k].detach().item()) for k in fields[2:]},
        }
    ]
    rows.extend({"phase": "train", **r} for r in history)

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fields})


def write_report(
    path: Path,
    args: argparse.Namespace,
    summary: dict[str, Any],
    counts: dict[str, int],
    before_ce: dict[str, Any],
    after_ce: dict[str, Any],
    initial: dict[str, torch.Tensor],
    history: list[dict[str, float]],
    saved_checkpoint: bool,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    lines = []
    lines.append("# Expanded b6c64 benchmark-preserving adapter no-save report")
    lines.append("")
    lines.append("- scope: benchmark-preserving adapter sanity run")
    lines.append(f"- no_save: `{args.no_save}`")
    lines.append(f"- saved_checkpoint: `{saved_checkpoint}`")
    lines.append("- no C export")
    lines.append("- no public benchmark")
    lines.append("- no promotion/current_best overwrite")
    lines.append("")
    lines.append("## Input counts")
    lines.append("")
    lines.append("| group | count |")
    lines.append("|---|---:|")
    for k, v in counts.items():
        lines.append(f"| `{k}` | {v} |")
    lines.append("")
    lines.append("## Loss weights")
    lines.append("")
    lines.append("| term | weight |")
    lines.append("|---|---:|")
    lines.append(f"| CE teacher-divergence | {args.ce_weight:.3g} |")
    lines.append(f"| public tactical_mid KL | {args.public_kl_weight:.3g} |")
    lines.append(f"| protected KL | {args.protected_kl_weight:.3g} |")
    lines.append(f"| tail KL | {args.tail_kl_weight:.3g} |")
    lines.append("")
    lines.append("## Initial loss")
    lines.append("")
    lines.append("| term | value |")
    lines.append("|---|---:|")
    for k in ["loss", "ce_loss", "public_kl", "protected_kl", "tail_kl"]:
        lines.append(f"| `{k}` | {float(initial[k].detach().item()):.6f} |")
    lines.append("")
    lines.append("## Final epoch")
    lines.append("")
    if history:
        last = history[-1]
        lines.append("| term | value |")
        lines.append("|---|---:|")
        for k in ["epoch", "loss", "ce_loss", "public_kl", "protected_kl", "tail_kl"]:
            lines.append(f"| `{k}` | {float(last[k]):.6f} |")
    else:
        lines.append("No training history.")
    lines.append("")
    lines.append("## Teacher-divergence CE diagnostics")
    lines.append("")
    lines.append("| phase | mode | rows | top3 | top5 | top10 | rank_gt50 | mean_rank | mean_target_prob |")
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|---:|")
    for name, d in [("before", before_ce), ("after", after_ce)]:
        lines.append(
            f"| {name} | {d.get('diagnostic_mode', 'unknown')} | {d['rows']} | {d['top3']} | "
            f"{d['top5']} | {d['top10']} | {d['rank_gt50']} | {d['mean_rank']:.3f} | "
            f"{d['mean_target_prob']:.6f} |"
        )
    lines.append("")
    lines.append("## Baseline policy")
    lines.append("")
    bp = summary.get("baseline_policy", {})
    lines.append(f"- current-local tactical_mid no-regression gate: `{bp.get('local_no_regression_gate')}`")
    lines.append(f"- aspirational recovery target: `{bp.get('aspirational_recovery_target')}`")
    lines.append("")
    lines.append("## Next step")
    lines.append("")
    lines.append(
        "If this no-save run is finite and teacher-divergence diagnostics improve without large KL movement, "
        "the next route can run a guarded saved candidate. Public benchmark must still be run separately after export."
    )
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)

    will_save = not args.no_save
    assert_safe_out_checkpoint(args.out_checkpoint, will_save=will_save)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    doc = json.loads(args.input.read_text(encoding="utf-8"))
    groups = split_records(doc)
    summary = doc.get("summary", {})

    required = [
        "teacher_divergence_ce_train",
        "public_tactical_mid_kl_anchor_train",
        "protected_top10_kl_guard",
        "tail_rank_kl_guard",
    ]
    missing = [g for g in required if not groups.get(g)]
    if missing:
        raise ValueError(f"missing training groups: {missing}")

    counts = {g: len(groups[g]) for g in required}

    print("device:", device)
    print("input:", args.input)
    print("init_checkpoint:", args.init_checkpoint)
    print("reference_checkpoint:", args.reference_checkpoint)
    print("out_checkpoint:", args.out_checkpoint)
    print("no_save:", args.no_save)
    print("counts:", counts)
    print("board_size:", args.board_size, "channels:", args.channels, "blocks:", args.blocks)

    model = load_model(args.init_checkpoint, device, args.board_size, args.channels, args.blocks, args.win_length)
    reference_model = load_model(args.reference_checkpoint, device, args.board_size, args.channels, args.blocks, args.win_length)
    reference_model.eval()

    ce_tensors = make_ce_tensors(groups["teacher_divergence_ce_train"], device, args.board_size)
    public_tensors = make_state_mask_tensors(groups["public_tactical_mid_kl_anchor_train"], device, args.board_size)
    protected_tensors = make_state_mask_tensors(groups["protected_top10_kl_guard"], device, args.board_size)
    tail_tensors = make_state_mask_tensors(groups["tail_rank_kl_guard"], device, args.board_size)

    with torch.no_grad():
        ref_public_probs = reference_probs(reference_model, public_tensors[0], public_tensors[1])
        ref_protected_probs = reference_probs(reference_model, protected_tensors[0], protected_tensors[1])
        ref_tail_probs = reference_probs(reference_model, tail_tensors[0], tail_tensors[1])

    before_ce = diagnose_ce_rows(model, groups["teacher_divergence_ce_train"], device, args.board_size)

    initial = compute_terms(
        model,
        ce_tensors,
        public_tensors,
        protected_tensors,
        tail_tensors,
        ref_public_probs,
        ref_protected_probs,
        ref_tail_probs,
        args,
    )
    assert_finite(initial, "initial")
    print(
        "initial "
        f"loss={float(initial['loss'].detach().item()):.6f} "
        f"ce={float(initial['ce_loss'].detach().item()):.6f} "
        f"public_kl={float(initial['public_kl'].detach().item()):.6f} "
        f"protected_kl={float(initial['protected_kl'].detach().item()):.6f} "
        f"tail_kl={float(initial['tail_kl'].detach().item()):.6f}",
        flush=True,
    )

    optimizer = torch.optim.AdamW(
        configure_policy_head_trainable(model),
        lr=args.lr,
        weight_decay=args.weight_decay,
    )

    history: list[dict[str, float]] = []
    for epoch in range(1, args.epochs + 1):
        set_policy_head_training_mode(model)
        terms = compute_terms(
            model,
            ce_tensors,
            public_tensors,
            protected_tensors,
            tail_tensors,
            ref_public_probs,
            ref_protected_probs,
            ref_tail_probs,
            args,
        )
        assert_finite(terms, f"epoch {epoch}")

        optimizer.zero_grad()
        terms["loss"].backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=0.5)
        optimizer.step()

        row = {k: float(v.detach().item()) for k, v in terms.items()}
        row["epoch"] = float(epoch)
        history.append(row)

        if epoch == 1 or epoch == args.epochs or epoch % args.print_every == 0:
            print(
                f"epoch {epoch:03d}/{args.epochs} "
                f"loss={row['loss']:.6f} "
                f"ce={row['ce_loss']:.6f} "
                f"public_kl={row['public_kl']:.6f} "
                f"protected_kl={row['protected_kl']:.6f} "
                f"tail_kl={row['tail_kl']:.6f}",
                flush=True,
            )

    after_ce = diagnose_ce_rows(model, groups["teacher_divergence_ce_train"], device, args.board_size)

    saved_checkpoint = False
    if not args.no_save:
        args.out_checkpoint.parent.mkdir(parents=True, exist_ok=True)
        torch.save(
            {
                "model": model.state_dict(),
                "board_size": args.board_size,
                "channels": args.channels,
                "blocks": args.blocks,
                "win_length": args.win_length,
                "source": "expanded_b6c64_benchmark_preserving_adapter",
                "input": str(args.input),
                "init_checkpoint": str(args.init_checkpoint),
                "reference_checkpoint": str(args.reference_checkpoint),
            },
            args.out_checkpoint,
        )
        saved_checkpoint = True

    write_history_csv(args.out_csv, initial, history)
    write_report(args.out_report, args, summary, counts, before_ce, after_ce, initial, history, saved_checkpoint)

    print("before_ce:", before_ce)
    print("after_ce:", after_ce)
    print("csv:", args.out_csv)
    print("report:", args.out_report)
    print("saved_checkpoint:", saved_checkpoint)
    print("status: no C export, no public benchmark, no promotion")


if __name__ == "__main__":
    main()
