from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import torch
from torch.nn import functional as F

from gomoku_agent.checkpoint import load_compatible_checkpoint
from gomoku_agent.model import PolicyValueNet
from train_rapfi_teacher_policy_margin import (
    configure_policy_head_trainable,
    masked_log_softmax,
    masked_softmax,
    parse_side_to_move,
    rank_of_action,
    set_policy_head_training_mode,
)


DEFAULT_ANCHOR_SNAPSHOTS = Path("analysis/public_benchmark_eval/corpus8_selected_board_snapshots.json")
FORBIDDEN_OUT_CHECKPOINTS = {
    Path("checkpoints/15x15_current_best.pt"),
    Path("checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt"),
}
REFERENCE_FALLBACK_CHANNELS = 64
REFERENCE_FALLBACK_BLOCKS = 4


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "No-promotion b4c96-safe policy rank/top-k multi-suppress training wrapper "
            "for capacity-data pairing Stage B."
        )
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        default=Path(
            "analysis/public_benchmark_eval/"
            "rapfi_teacher_policy_multisuppress_dataset_corpus8_selected.json"
        ),
    )
    parser.add_argument(
        "--init-checkpoint",
        type=Path,
        default=Path("checkpoints/probes/15x15_capacity_data_pairing_b4c96_warmstart.pt"),
    )
    parser.add_argument(
        "--reference-checkpoint",
        type=Path,
        default=Path("checkpoints/15x15_current_best.pt"),
    )
    parser.add_argument(
        "--out-checkpoint",
        type=Path,
        default=Path("checkpoints/probes/15x15_capacity_data_pairing_b4c96_probe_candidate.pt"),
    )
    parser.add_argument(
        "--out-csv",
        type=Path,
        default=Path("analysis/integration_eval/b4c96_safe_rank_topk_training_history.csv"),
    )
    parser.add_argument(
        "--out-report",
        type=Path,
        default=Path("analysis/integration_eval/b4c96_safe_rank_topk_training_report.md"),
    )
    parser.add_argument("--board-size", type=int, default=15)
    parser.add_argument("--channels", type=int, default=96)
    parser.add_argument("--blocks", type=int, default=4)
    parser.add_argument("--win-length", type=int, default=5)
    parser.add_argument("--margin", type=float, default=0.25)
    parser.add_argument("--ce-weight", type=float, default=1.0)
    parser.add_argument("--pair-weight", type=float, default=0.25)
    parser.add_argument("--worst-weight", type=float, default=0.50)
    parser.add_argument("--anchor-kl-weight", type=float, default=0.05)
    parser.add_argument("--lr", type=float, default=3e-6)
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--weight-decay", type=float, default=1e-5)
    parser.add_argument("--seed", type=int, default=31)
    parser.add_argument("--print-every", type=int, default=5)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-save", action="store_true")
    return parser.parse_args()


def normalized_checkpoint_path(path: Path) -> Path:
    return Path(path).expanduser()


def assert_safe_out_checkpoint(path: Path, *, will_save: bool) -> None:
    candidate = normalized_checkpoint_path(path)
    candidate_parts = set(candidate.parts)
    if "current_best" in candidate.name or any("current_best" in part for part in candidate.parts):
        raise ValueError(f"refusing out-checkpoint path containing current_best: {path}")

    for forbidden in FORBIDDEN_OUT_CHECKPOINTS:
        if candidate == forbidden or candidate.match(str(forbidden)):
            raise ValueError(f"refusing protected out-checkpoint path: {path}")

    if "checkpoints" in candidate_parts:
        suffix = Path(*candidate.parts[list(candidate.parts).index("checkpoints") :])
        if suffix in FORBIDDEN_OUT_CHECKPOINTS:
            raise ValueError(f"refusing protected out-checkpoint path: {path}")

    if will_save and candidate.exists():
        raise FileExistsError(f"refusing to overwrite existing out-checkpoint: {path}")


def validate_arch_args(args: argparse.Namespace) -> None:
    if args.board_size <= 0:
        raise ValueError("--board-size must be positive")
    if args.channels <= 0:
        raise ValueError("--channels must be positive")
    if args.blocks <= 0:
        raise ValueError("--blocks must be positive")
    if args.win_length <= 0:
        raise ValueError("--win-length must be positive")
    if args.board_size < args.win_length:
        raise ValueError("--board-size must be >= --win-length")


def parse_board_snapshot(snapshot: str, board_size: int) -> list[list[int]]:
    rows: list[list[int]] = []
    for raw_line in snapshot.splitlines():
        tokens = raw_line.strip().split()
        if len(tokens) != board_size:
            continue
        if not all(token in {".", "X", "O"} for token in tokens):
            continue
        rows.append([0 if token == "." else 1 if token == "X" else -1 for token in tokens])

    if len(rows) != board_size:
        raise ValueError(f"expected {board_size} board rows, got {len(rows)}")
    return rows


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
    path: Path,
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
        path,
        device,
        board_size=board_size,
        channels=channels,
        blocks=blocks,
    )
    if not loaded:
        raise RuntimeError(
            f"could not load compatible checkpoint: {path} "
            f"for board_size={board_size} channels={channels} blocks={blocks}"
        )
    return model


def load_reference_model(args: argparse.Namespace, device: torch.device) -> PolicyValueNet:
    try:
        return load_model(
            args.reference_checkpoint,
            device,
            args.board_size,
            args.channels,
            args.blocks,
            args.win_length,
        )
    except RuntimeError as first_error:
        if args.channels == REFERENCE_FALLBACK_CHANNELS and args.blocks == REFERENCE_FALLBACK_BLOCKS:
            raise
        print(
            "reference checkpoint did not match train architecture; "
            f"trying b{REFERENCE_FALLBACK_BLOCKS}c{REFERENCE_FALLBACK_CHANNELS} reference fallback",
            flush=True,
        )
        try:
            return load_model(
                args.reference_checkpoint,
                device,
                args.board_size,
                REFERENCE_FALLBACK_CHANNELS,
                REFERENCE_FALLBACK_BLOCKS,
                args.win_length,
            )
        except RuntimeError as fallback_error:
            raise RuntimeError(
                "could not load reference checkpoint with train architecture or "
                f"b{REFERENCE_FALLBACK_BLOCKS}c{REFERENCE_FALLBACK_CHANNELS} fallback"
            ) from fallback_error or first_error


def load_anchor_samples(path: Path, board_size: int) -> list[dict[str, Any]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    anchors = []
    for item in raw:
        board = parse_board_snapshot(item["board_snapshot_before_decision"], board_size)
        current_player = parse_side_to_move(item["side_to_move"])
        anchors.append(
            {
                "case_id": f"anchor_g{item.get('game_number')}_m{item.get('move_count')}",
                "state": encode_state(board, current_player, board_size),
                "legal_mask": legal_mask_from_board(board, board_size),
            }
        )
    return anchors


def load_multisuppress_samples(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    dataset = json.loads(path.read_text(encoding="utf-8"))
    samples = dataset.get("samples", [])
    if not samples:
        raise ValueError(f"empty or missing samples in dataset: {path}")
    return dataset, samples


def make_multisuppress_tensors(
    samples: list[dict[str, Any]],
    device: torch.device,
    board_size: int,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
    states = []
    legal_masks = []
    target_actions = []
    suppress_actions = []
    weights = []

    expected_suppress_count = None
    for sample in samples:
        board = sample["board"]
        current_player = int(sample["current_player"])
        legal_mask = legal_mask_from_board(board, board_size)
        target_action = rc_to_action(sample["target_rc"], board_size)
        suppress = [rc_to_action(rc, board_size) for rc in sample["suppress_rcs"]]

        if expected_suppress_count is None:
            expected_suppress_count = len(suppress)
        if len(suppress) != expected_suppress_count:
            raise ValueError(
                f"{sample['case_id']}: variable suppress count not supported in this probe"
            )

        if legal_mask[target_action] <= 0:
            raise ValueError(f"{sample['case_id']}: illegal target_rc {sample['target_rc']}")

        seen: set[int] = set()
        for action in suppress:
            if legal_mask[action] <= 0:
                raise ValueError(
                    f"{sample['case_id']}: illegal suppress_rc {action_to_rc(action, board_size)}"
                )
            if action == target_action:
                raise ValueError(
                    f"{sample['case_id']}: suppress equals target {action_to_rc(action, board_size)}"
                )
            if action in seen:
                raise ValueError(
                    f"{sample['case_id']}: duplicate suppress {action_to_rc(action, board_size)}"
                )
            seen.add(action)

        states.append(encode_state(board, current_player, board_size))
        legal_masks.append(legal_mask)
        target_actions.append(target_action)
        suppress_actions.append(suppress)
        weights.append(float(sample.get("effective_sample_weight", sample.get("sample_weight", 1.0))))

    return (
        torch.tensor(np.stack(states), dtype=torch.float32, device=device),
        torch.tensor(np.stack(legal_masks), dtype=torch.float32, device=device),
        torch.tensor(target_actions, dtype=torch.long, device=device),
        torch.tensor(np.asarray(suppress_actions), dtype=torch.long, device=device),
        torch.tensor(weights, dtype=torch.float32, device=device),
    )


def make_anchor_tensors(anchors: list[dict[str, Any]], device: torch.device) -> tuple[torch.Tensor, torch.Tensor]:
    states = torch.tensor(np.stack([anchor["state"] for anchor in anchors]), dtype=torch.float32, device=device)
    masks = torch.tensor(np.stack([anchor["legal_mask"] for anchor in anchors]), dtype=torch.float32, device=device)
    return states, masks


def compute_loss_terms(
    model: torch.nn.Module,
    reference_model: torch.nn.Module,
    tensors: tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor],
    anchor_tensors: tuple[torch.Tensor, torch.Tensor],
    ref_anchor_probs: torch.Tensor,
    args: argparse.Namespace,
) -> dict[str, torch.Tensor]:
    states, legal_masks, target_actions, suppress_actions, weights = tensors
    anchor_states, anchor_masks = anchor_tensors
    weight_sum = weights.sum().clamp_min(1e-12)

    logits, _values = model(states)
    log_probs = masked_log_softmax(logits, legal_masks)

    target_logits = logits.gather(1, target_actions.unsqueeze(1)).squeeze(1)
    suppress_logits = logits.gather(1, suppress_actions)
    gaps = target_logits.unsqueeze(1) - suppress_logits

    ce_per_row = -log_probs.gather(1, target_actions.unsqueeze(1)).squeeze(1)
    ce_loss = (ce_per_row * weights).sum() / weight_sum

    pair_hinge_per_row = F.relu(args.margin - gaps).mean(dim=1)
    pair_hinge_loss = (pair_hinge_per_row * weights).sum() / weight_sum

    worst_gap = gaps.min(dim=1).values
    worst_hinge_per_row = F.relu(args.margin - worst_gap)
    worst_hinge_loss = (worst_hinge_per_row * weights).sum() / weight_sum

    anchor_logits, _anchor_values = model(anchor_states)
    anchor_log_probs = masked_log_softmax(anchor_logits, anchor_masks)
    anchor_kl = (
        ref_anchor_probs * (torch.log(ref_anchor_probs.clamp_min(1e-12)) - anchor_log_probs)
    ).sum(dim=-1).mean()

    loss = (
        args.ce_weight * ce_loss
        + args.pair_weight * pair_hinge_loss
        + args.worst_weight * worst_hinge_loss
        + args.anchor_kl_weight * anchor_kl
    )

    return {
        "loss": loss,
        "ce_loss": ce_loss,
        "pair_hinge_loss": pair_hinge_loss,
        "worst_hinge_loss": worst_hinge_loss,
        "anchor_kl": anchor_kl,
        "mean_gap": gaps.mean(),
        "mean_worst_gap": worst_gap.mean(),
    }


def assert_finite_terms(terms: dict[str, torch.Tensor], label: str) -> None:
    bad = []
    for name, value in terms.items():
        scalar = float(value.detach().item())
        if not math.isfinite(scalar):
            bad.append(f"{name}={scalar}")
    if bad:
        raise RuntimeError(f"non-finite {label} terms: {', '.join(bad)}")


@torch.no_grad()
def diagnose_summary(
    model: torch.nn.Module,
    samples: list[dict[str, Any]],
    device: torch.device,
    board_size: int,
) -> dict[str, Any]:
    ranks = []
    probs = []
    worst_gaps = []
    pair_hinges = []
    beats_worst = 0
    beats_all = 0

    for sample in samples:
        board = sample["board"]
        current_player = int(sample["current_player"])
        legal_np = legal_mask_from_board(board, board_size)
        target_action = rc_to_action(sample["target_rc"], board_size)
        suppress_actions = [rc_to_action(rc, board_size) for rc in sample["suppress_rcs"]]

        state = torch.tensor(
            encode_state(board, current_player, board_size),
            dtype=torch.float32,
            device=device,
        ).unsqueeze(0)
        mask = torch.tensor(legal_np, dtype=torch.float32, device=device).unsqueeze(0)

        logits, _values = model(state)
        prob = masked_softmax(logits, mask)[0]
        logits0 = logits[0]
        mask0 = mask[0]

        target_logit = float(logits0[target_action].item())
        gaps = [target_logit - float(logits0[action].item()) for action in suppress_actions]

        ranks.append(int(rank_of_action(prob, target_action, mask0)))
        probs.append(float(prob[target_action].item()))
        worst_gaps.append(float(min(gaps)))
        pair_hinges.append(float(np.mean([max(0.0, 0.25 - gap) for gap in gaps])))
        beats_worst += int(min(gaps) > 0.0)
        beats_all += int(all(gap > 0.0 for gap in gaps))

    return {
        "rows": len(samples),
        "top3": int(sum(rank <= 3 for rank in ranks)),
        "top5": int(sum(rank <= 5 for rank in ranks)),
        "top10": int(sum(rank <= 10 for rank in ranks)),
        "rank_gt50": int(sum(rank > 50 for rank in ranks)),
        "mean_rank": float(np.mean(ranks)),
        "mean_target_prob": float(np.mean(probs)),
        "mean_worst_gap": float(np.mean(worst_gaps)),
        "mean_pair_hinge_margin_025": float(np.mean(pair_hinges)),
        "teacher_beats_worst": int(beats_worst),
        "teacher_beats_all": int(beats_all),
    }


def train(
    model: torch.nn.Module,
    reference_model: torch.nn.Module,
    tensors: tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor],
    anchor_tensors: tuple[torch.Tensor, torch.Tensor],
    args: argparse.Namespace,
) -> list[dict[str, float]]:
    optimizer = torch.optim.AdamW(
        configure_policy_head_trainable(model),
        lr=args.lr,
        weight_decay=args.weight_decay,
    )

    reference_model.eval()
    anchor_states, anchor_masks = anchor_tensors
    with torch.no_grad():
        ref_anchor_logits, _ref_values = reference_model(anchor_states)
        ref_anchor_probs = masked_softmax(ref_anchor_logits, anchor_masks)

    history = []
    for epoch in range(1, args.epochs + 1):
        set_policy_head_training_mode(model)
        terms = compute_loss_terms(
            model,
            reference_model,
            tensors,
            anchor_tensors,
            ref_anchor_probs,
            args,
        )
        assert_finite_terms(terms, f"epoch {epoch}")

        optimizer.zero_grad()
        terms["loss"].backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=0.5)
        optimizer.step()

        row = {name: float(value.detach().item()) for name, value in terms.items()}
        row["epoch"] = float(epoch)
        history.append(row)

        if epoch == 1 or epoch == args.epochs or epoch % args.print_every == 0:
            print(
                f"epoch {epoch:03d}/{args.epochs} "
                f"loss={row['loss']:.6f} "
                f"ce={row['ce_loss']:.6f} "
                f"pair_hinge={row['pair_hinge_loss']:.6f} "
                f"worst_hinge={row['worst_hinge_loss']:.6f} "
                f"anchor_kl={row['anchor_kl']:.6f} "
                f"mean_gap={row['mean_gap']:.6f} "
                f"mean_worst_gap={row['mean_worst_gap']:.6f}",
                flush=True,
            )

    return history


def write_history_csv(
    path: Path,
    initial_terms: dict[str, torch.Tensor],
    history: list[dict[str, float]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "phase",
        "epoch",
        "loss",
        "ce_loss",
        "pair_hinge_loss",
        "worst_hinge_loss",
        "anchor_kl",
        "mean_gap",
        "mean_worst_gap",
    ]
    rows: list[dict[str, Any]] = [
        {
            "phase": "initial",
            "epoch": 0,
            **{key: float(initial_terms[key].detach().item()) for key in fields[2:]},
        }
    ]
    rows.extend({"phase": "train", **row} for row in history)

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def write_report(
    path: Path,
    args: argparse.Namespace,
    dataset_meta: dict[str, Any],
    before: dict[str, Any],
    after: dict[str, Any] | None,
    initial_terms: dict[str, torch.Tensor],
    history: list[dict[str, float]],
    saved_checkpoint: bool,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    lines = []
    lines += ["# b4c96-safe rank/top-k trainer wrapper report", ""]
    lines += ["## Scope", ""]
    lines += ["- No-promotion b4c96-safe rank/top-k multi-suppress trainer wrapper."]
    lines += ["- No C export, no public benchmark, no promotion, no current-best overwrite."]
    lines += [f"- dry_run: {args.dry_run}"]
    lines += [f"- no_save: {args.no_save}"]
    lines += [f"- saved_checkpoint: {saved_checkpoint}"]
    lines += [""]

    lines += ["## Inputs", ""]
    lines += [f"- dataset: {args.dataset}"]
    lines += [f"- dataset_name: {dataset_meta.get('name', 'unknown')}"]
    lines += [f"- init_checkpoint: {args.init_checkpoint}"]
    lines += [f"- reference_checkpoint: {args.reference_checkpoint}"]
    lines += [f"- out_checkpoint: {args.out_checkpoint}"]
    lines += [f"- out_csv: {args.out_csv}"]
    lines += [f"- anchor_snapshots: {DEFAULT_ANCHOR_SNAPSHOTS}"]
    lines += [""]

    lines += ["## Architecture", ""]
    lines += [f"- board_size: {args.board_size}"]
    lines += [f"- channels: {args.channels}"]
    lines += [f"- blocks: {args.blocks}"]
    lines += [f"- win_length: {args.win_length}"]
    lines += [""]

    lines += ["## Objective", ""]
    lines += [f"- margin: {args.margin}"]
    lines += [f"- ce_weight: {args.ce_weight}"]
    lines += [f"- pair_weight: {args.pair_weight}"]
    lines += [f"- worst_weight: {args.worst_weight}"]
    lines += [f"- anchor_kl_weight: {args.anchor_kl_weight}"]
    lines += [f"- lr: {args.lr}"]
    lines += [f"- epochs: {args.epochs}"]
    lines += [""]

    lines += ["## Safety Guards", ""]
    lines += ["- Refuses any out-checkpoint path containing `current_best`."]
    lines += ["- Refuses `checkpoints/15x15_current_best.pt`."]
    lines += ["- Refuses `checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt`."]
    lines += ["- Refuses to overwrite an existing out-checkpoint."]
    lines += [""]

    lines += ["## Initial loss terms", ""]
    lines += ["| term | value |", "|---|---:|"]
    for key in ["loss", "ce_loss", "pair_hinge_loss", "worst_hinge_loss", "anchor_kl", "mean_gap", "mean_worst_gap"]:
        lines.append(f"| {key} | {float(initial_terms[key].detach().item()):.8f} |")

    lines += ["", "## Rank/top-k summary", ""]
    lines += ["| metric | before | after | delta |", "|---|---:|---:|---:|"]
    keys = [
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
    for key in keys:
        b = before[key]
        a = after[key] if after is not None else before[key]
        try:
            d = float(a) - float(b)
            lines.append(f"| {key} | {b} | {a} | {d} |")
        except Exception:
            lines.append(f"| {key} | {b} | {a} | n/a |")

    if history:
        lines += ["", "## Final training terms", ""]
        lines += ["| term | value |", "|---|---:|"]
        final = history[-1]
        for key in ["loss", "ce_loss", "pair_hinge_loss", "worst_hinge_loss", "anchor_kl", "mean_gap", "mean_worst_gap"]:
            lines.append(f"| {key} | {final[key]:.8f} |")

    lines += ["", "## Decision", ""]
    if args.dry_run:
        lines.append("Dry-run only. No optimizer step and no checkpoint save.")
    elif args.no_save:
        lines.append("Training ran in-process, but no checkpoint was saved because --no-save was set.")
    elif saved_checkpoint:
        lines.append("Checkpoint saved as a no-promotion probe candidate only.")
    else:
        lines.append("No checkpoint was saved.")

    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    args = parse_args()
    validate_arch_args(args)
    assert_safe_out_checkpoint(args.out_checkpoint, will_save=not args.dry_run and not args.no_save)

    torch.manual_seed(args.seed)
    np.random.seed(args.seed)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    dataset_meta, samples = load_multisuppress_samples(args.dataset)
    anchors = load_anchor_samples(DEFAULT_ANCHOR_SNAPSHOTS, args.board_size)
    tensors = make_multisuppress_tensors(samples, device, args.board_size)
    anchor_tensors = make_anchor_tensors(anchors, device)

    model = load_model(
        args.init_checkpoint,
        device,
        args.board_size,
        args.channels,
        args.blocks,
        args.win_length,
    )
    reference_model = load_reference_model(args, device)
    reference_model.eval()
    for parameter in reference_model.parameters():
        parameter.requires_grad = False

    anchor_states, anchor_masks = anchor_tensors
    with torch.no_grad():
        ref_anchor_logits, _ref_values = reference_model(anchor_states)
        ref_anchor_probs = masked_softmax(ref_anchor_logits, anchor_masks)

    before = diagnose_summary(model, samples, device, args.board_size)
    initial_terms = compute_loss_terms(
        model,
        reference_model,
        tensors,
        anchor_tensors,
        ref_anchor_probs,
        args,
    )
    assert_finite_terms(initial_terms, "initial")

    print("device:", device)
    print("dataset:", args.dataset)
    print("samples:", len(samples))
    print("anchors:", len(anchors))
    print("init_checkpoint:", args.init_checkpoint)
    print("reference_checkpoint:", args.reference_checkpoint)
    print("out_checkpoint:", args.out_checkpoint)
    print("out_csv:", args.out_csv)
    print("out_report:", args.out_report)
    print("board_size:", args.board_size)
    print("channels:", args.channels)
    print("blocks:", args.blocks)
    print("win_length:", args.win_length)
    print("dry_run:", args.dry_run)
    print("no_save:", args.no_save)
    print("initial_loss:", "{:.6f}".format(float(initial_terms["loss"].detach().item())))
    print("initial_ce:", "{:.6f}".format(float(initial_terms["ce_loss"].detach().item())))
    print("initial_pair_hinge:", "{:.6f}".format(float(initial_terms["pair_hinge_loss"].detach().item())))
    print("initial_worst_hinge:", "{:.6f}".format(float(initial_terms["worst_hinge_loss"].detach().item())))
    print("initial_anchor_kl:", "{:.6f}".format(float(initial_terms["anchor_kl"].detach().item())))
    print("before_top3:", before["top3"])
    print("before_top5:", before["top5"])
    print("before_top10:", before["top10"])
    print("before_rank_gt50:", before["rank_gt50"])
    print("before_mean_worst_gap:", "{:.6f}".format(before["mean_worst_gap"]))

    history: list[dict[str, float]] = []
    after: dict[str, Any] | None = None
    saved_checkpoint = False

    if args.dry_run:
        print("dry-run only; no training and no checkpoint save")
    else:
        history = train(model, reference_model, tensors, anchor_tensors, args)
        after = diagnose_summary(model, samples, device, args.board_size)

        if args.no_save:
            print("no checkpoint saved due to --no-save")
        else:
            args.out_checkpoint.parent.mkdir(parents=True, exist_ok=True)
            torch.save(
                {
                    "model": model.state_dict(),
                    "board_size": args.board_size,
                    "win_length": args.win_length,
                    "channels": args.channels,
                    "blocks": args.blocks,
                    "rapfi_teacher_policy_rank_topk_b4c96_probe": {
                        "init_checkpoint": str(args.init_checkpoint),
                        "reference_checkpoint": str(args.reference_checkpoint),
                        "dataset": str(args.dataset),
                        "anchor_snapshots": str(DEFAULT_ANCHOR_SNAPSHOTS),
                        "margin": args.margin,
                        "ce_weight": args.ce_weight,
                        "pair_weight": args.pair_weight,
                        "worst_weight": args.worst_weight,
                        "anchor_kl_weight": args.anchor_kl_weight,
                        "lr": args.lr,
                        "epochs": args.epochs,
                        "weight_decay": args.weight_decay,
                        "seed": args.seed,
                        "train_scope": "policy_head",
                        "no_promotion": True,
                    },
                },
                args.out_checkpoint,
            )
            saved_checkpoint = True
            print("saved_checkpoint:", args.out_checkpoint)

    write_history_csv(args.out_csv, initial_terms, history)
    write_report(
        args.out_report,
        args,
        dataset_meta,
        before,
        after,
        initial_terms,
        history,
        saved_checkpoint,
    )
    print("csv:", args.out_csv)
    print("report:", args.out_report)
    print("status: no export, no public benchmark, no promotion")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
