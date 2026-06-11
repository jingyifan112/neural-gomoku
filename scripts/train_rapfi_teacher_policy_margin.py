from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import torch
from torch.nn import functional as F

from gomoku_agent.checkpoint import load_compatible_checkpoint
from gomoku_agent.model import PolicyValueNet


BOARD_SIZE = 15
WIN_LENGTH = 5
CHANNELS = 64
BLOCKS = 4


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train Rapfi teacher policy pairwise margin repair checkpoint.")
    parser.add_argument(
        "--dataset",
        type=Path,
        default=Path("analysis/public_benchmark_eval/rapfi_teacher_policy_margin_dataset_corpus8_selected.json"),
    )
    parser.add_argument(
        "--anchor-snapshots",
        type=Path,
        default=Path("analysis/public_benchmark_eval/corpus8_selected_board_snapshots.json"),
    )
    parser.add_argument("--init-checkpoint", type=Path, required=True)
    parser.add_argument("--reference-checkpoint", type=Path, required=True)
    parser.add_argument("--out-checkpoint", type=Path, required=True)
    parser.add_argument("--margin", type=float, default=1.0)
    parser.add_argument("--lr", type=float, default=5e-6)
    parser.add_argument("--epochs", type=int, default=40)
    parser.add_argument("--anchor-kl-weight", type=float, default=0.05)
    parser.add_argument("--ce-weight", type=float, default=0.10)
    parser.add_argument("--weight-decay", type=float, default=1e-5)
    parser.add_argument("--seed", type=int, default=29)
    parser.add_argument("--print-every", type=int, default=5)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def parse_board_snapshot(snapshot: str) -> list[list[int]]:
    rows: list[list[int]] = []
    for raw_line in snapshot.splitlines():
        tokens = raw_line.strip().split()
        if len(tokens) != BOARD_SIZE:
            continue
        if not all(token in {".", "X", "O"} for token in tokens):
            continue
        rows.append([0 if token == "." else 1 if token == "X" else -1 for token in tokens])

    if len(rows) != BOARD_SIZE:
        raise ValueError(f"expected {BOARD_SIZE} board rows, got {len(rows)}")
    return rows


def parse_side_to_move(side: str) -> int:
    side_l = side.strip().lower()
    if side_l == "black":
        return 1
    if side_l == "white":
        return -1
    raise ValueError(f"unknown side_to_move {side!r}")


def validate_rc(rc: list[int] | tuple[int, int]) -> tuple[int, int]:
    if len(rc) != 2:
        raise ValueError(f"expected rc with length 2, got {rc!r}")
    row, col = int(rc[0]), int(rc[1])
    if not (0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE):
        raise ValueError(f"rc out of range: {rc!r}")
    return row, col


def rc_to_action(rc: list[int] | tuple[int, int]) -> int:
    row, col = validate_rc(rc)
    return row * BOARD_SIZE + col


def encode_state(board: list[list[int]], current_player: int) -> np.ndarray:
    grid = np.asarray(board, dtype=np.int8)
    if grid.shape != (BOARD_SIZE, BOARD_SIZE):
        raise ValueError(f"expected {BOARD_SIZE}x{BOARD_SIZE} board, got {grid.shape}")
    current = (grid == current_player).astype(np.float32)
    opponent = (grid == -current_player).astype(np.float32)
    last = np.zeros_like(current, dtype=np.float32)
    return np.stack([current, opponent, last], axis=0)


def legal_mask_from_board(board: list[list[int]]) -> np.ndarray:
    grid = np.asarray(board, dtype=np.int8)
    if grid.shape != (BOARD_SIZE, BOARD_SIZE):
        raise ValueError(f"expected {BOARD_SIZE}x{BOARD_SIZE} board, got {grid.shape}")
    return (grid.reshape(-1) == 0).astype(np.float32)


def load_margin_samples(path: Path) -> list[dict[str, Any]]:
    dataset = json.loads(path.read_text(encoding="utf-8"))
    samples = dataset["samples"]
    if not samples:
        raise ValueError("empty margin dataset")
    return samples


def load_anchor_samples(path: Path) -> list[dict[str, Any]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    anchors = []
    for item in raw:
        board = parse_board_snapshot(item["board_snapshot_before_decision"])
        current_player = parse_side_to_move(item["side_to_move"])
        anchors.append(
            {
                "case_id": f"anchor_g{item.get('game_number')}_m{item.get('move_count')}",
                "state": encode_state(board, current_player),
                "legal_mask": legal_mask_from_board(board),
            }
        )
    return anchors


def load_model(path: Path, device: torch.device) -> PolicyValueNet:
    model = PolicyValueNet(board_size=BOARD_SIZE, channels=CHANNELS, blocks=BLOCKS).to(device)
    loaded = load_compatible_checkpoint(
        model,
        path,
        device,
        board_size=BOARD_SIZE,
        channels=CHANNELS,
        blocks=BLOCKS,
    )
    if not loaded:
        raise RuntimeError(f"could not load compatible checkpoint: {path}")
    return model


def configure_policy_head_trainable(model: PolicyValueNet) -> list[torch.nn.Parameter]:
    for name, parameter in model.named_parameters():
        parameter.requires_grad = name.startswith("policy.")

    trainable = [(name, parameter) for name, parameter in model.named_parameters() if parameter.requires_grad]
    if not trainable:
        raise ValueError("policy_head selected no trainable parameters")

    print(f"train_scope=policy_head")
    print(f"trainable_parameters={sum(parameter.numel() for _, parameter in trainable)}")
    for name, _ in trainable:
        print(f"  trainable: {name}")
    return [parameter for _, parameter in trainable]


def set_policy_head_training_mode(model: PolicyValueNet) -> None:
    model.eval()
    model.policy.train()


def masked_log_softmax(logits: torch.Tensor, legal_mask: torch.Tensor) -> torch.Tensor:
    return F.log_softmax(logits.masked_fill(legal_mask <= 0, -1e9), dim=-1)


def masked_softmax(logits: torch.Tensor, legal_mask: torch.Tensor) -> torch.Tensor:
    return torch.exp(masked_log_softmax(logits, legal_mask))


def rank_of_action(probs: torch.Tensor, action: int, legal_mask: torch.Tensor) -> int:
    legal_actions = torch.nonzero(legal_mask > 0, as_tuple=False).flatten()
    ranked_actions = legal_actions[torch.argsort(probs[legal_actions], descending=True)].tolist()
    return ranked_actions.index(int(action)) + 1


def make_margin_tensors(
    samples: list[dict[str, Any]], device: torch.device
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
    states = []
    masks = []
    target_actions = []
    suppress_actions = []
    weights = []

    for sample in samples:
        board = sample["board"]
        current_player = int(sample["current_player"])
        legal_mask = legal_mask_from_board(board)
        target_action = rc_to_action(sample["target_rc"])
        suppress_action = rc_to_action(sample["suppress_rc"])
        if legal_mask[target_action] <= 0:
            raise ValueError(f"{sample['case_id']}: target_rc is not legal")
        if legal_mask[suppress_action] <= 0:
            raise ValueError(f"{sample['case_id']}: suppress_rc is not legal")

        states.append(encode_state(board, current_player))
        masks.append(legal_mask)
        target_actions.append(target_action)
        suppress_actions.append(suppress_action)
        weights.append(float(sample.get("sample_weight", 1.0)))

    return (
        torch.tensor(np.stack(states), dtype=torch.float32, device=device),
        torch.tensor(np.stack(masks), dtype=torch.float32, device=device),
        torch.tensor(target_actions, dtype=torch.long, device=device),
        torch.tensor(suppress_actions, dtype=torch.long, device=device),
        torch.tensor(weights, dtype=torch.float32, device=device),
    )


def make_anchor_tensors(anchors: list[dict[str, Any]], device: torch.device) -> tuple[torch.Tensor, torch.Tensor]:
    states = torch.tensor(np.stack([anchor["state"] for anchor in anchors]), dtype=torch.float32, device=device)
    masks = torch.tensor(np.stack([anchor["legal_mask"] for anchor in anchors]), dtype=torch.float32, device=device)
    return states, masks


@torch.no_grad()
def diagnose_cases(label: str, model: PolicyValueNet, samples: list[dict[str, Any]], device: torch.device) -> None:
    model.eval()
    print("=" * 100)
    print(label)
    for sample in samples:
        state = torch.tensor(
            encode_state(sample["board"], int(sample["current_player"])),
            dtype=torch.float32,
            device=device,
        ).unsqueeze(0)
        mask = torch.tensor(legal_mask_from_board(sample["board"]), dtype=torch.float32, device=device).unsqueeze(0)

        logits, _values = model(state)
        probs = masked_softmax(logits, mask)[0]
        logits0 = logits[0]
        mask0 = mask[0]
        target_action = rc_to_action(sample["target_rc"])
        suppress_action = rc_to_action(sample["suppress_rc"])
        target_logit = float(logits0[target_action].item())
        suppress_logit = float(logits0[suppress_action].item())

        print("-" * 100)
        print(f"case_id: {sample['case_id']}")
        print(f"target_rc: {sample['target_rc']} suppress_rc: {sample['suppress_rc']} sample_weight: {sample.get('sample_weight', 1.0)}")
        print(
            f"target_prob={float(probs[target_action].item()):.8f} "
            f"suppress_prob={float(probs[suppress_action].item()):.8f} "
            f"target_rank={rank_of_action(probs, target_action, mask0)} "
            f"suppress_rank={rank_of_action(probs, suppress_action, mask0)} "
            f"target_logit={target_logit:.6f} "
            f"suppress_logit={suppress_logit:.6f} "
            f"gap={target_logit - suppress_logit:.6f}"
        )


def train(
    model: PolicyValueNet,
    reference_model: PolicyValueNet,
    margin_tensors: tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor],
    anchor_tensors: tuple[torch.Tensor, torch.Tensor],
    args: argparse.Namespace,
) -> None:
    states, legal_masks, target_actions, suppress_actions, weights = margin_tensors
    anchor_states, anchor_masks = anchor_tensors
    optimizer = torch.optim.AdamW(
        configure_policy_head_trainable(model),
        lr=args.lr,
        weight_decay=args.weight_decay,
    )

    reference_model.eval()
    with torch.no_grad():
        ref_anchor_logits, _ref_values = reference_model(anchor_states)
        ref_anchor_probs = masked_softmax(ref_anchor_logits, anchor_masks)

    for epoch in range(1, args.epochs + 1):
        set_policy_head_training_mode(model)
        logits, _values = model(states)

        target_logits = logits.gather(1, target_actions.unsqueeze(1)).squeeze(1)
        suppress_logits = logits.gather(1, suppress_actions.unsqueeze(1)).squeeze(1)
        gaps = target_logits - suppress_logits
        per_row_margin = F.relu(args.margin - gaps)
        margin_loss = (per_row_margin * weights).sum() / weights.sum()

        log_probs = masked_log_softmax(logits, legal_masks)
        ce_per_row = -log_probs.gather(1, target_actions.unsqueeze(1)).squeeze(1)
        ce_loss = (ce_per_row * weights).sum() / weights.sum()

        anchor_logits, _anchor_values = model(anchor_states)
        anchor_log_probs = masked_log_softmax(anchor_logits, anchor_masks)
        anchor_kl = (
            ref_anchor_probs * (torch.log(ref_anchor_probs.clamp_min(1e-12)) - anchor_log_probs)
        ).sum(dim=-1).mean()

        loss = margin_loss + args.anchor_kl_weight * anchor_kl + args.ce_weight * ce_loss

        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=0.5)
        optimizer.step()

        if epoch == 1 or epoch == args.epochs or epoch % args.print_every == 0:
            gap_str = ", ".join(f"{float(gap):.4f}" for gap in gaps.detach().cpu())
            print(
                f"epoch {epoch:03d}/{args.epochs} "
                f"loss={float(loss.item()):.6f} "
                f"margin_loss={float(margin_loss.item()):.6f} "
                f"anchor_kl={float(anchor_kl.item()):.6f} "
                f"ce={float(ce_loss.item()):.6f} "
                f"gaps=[{gap_str}]",
                flush=True,
            )


def assert_not_current_best(path: Path) -> None:
    if path.name == "15x15_current_best.pt":
        raise ValueError("refusing to write checkpoints/15x15_current_best.pt")


def main() -> int:
    args = parse_args()
    assert_not_current_best(args.out_checkpoint)
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = load_model(args.init_checkpoint, device)
    reference_model = load_model(args.reference_checkpoint, device)
    reference_model.eval()
    for parameter in reference_model.parameters():
        parameter.requires_grad = False

    samples = load_margin_samples(args.dataset)
    anchors = load_anchor_samples(args.anchor_snapshots)
    margin_tensors = make_margin_tensors(samples, device)
    anchor_tensors = make_anchor_tensors(anchors, device)

    print(f"device: {device}")
    print(f"dataset: {args.dataset}")
    print(f"anchor_snapshots: {args.anchor_snapshots}")
    print(f"loaded init checkpoint: {args.init_checkpoint}")
    print(f"loaded reference checkpoint: {args.reference_checkpoint}")
    print(f"margin samples: {len(samples)}")
    print(f"anchor samples: {len(anchors)}")
    print(f"out checkpoint: {args.out_checkpoint}")
    print("NOTE: policy-head-only training; never writes checkpoints/15x15_current_best.pt")

    diagnose_cases("BEFORE", model, samples, device)
    if args.dry_run:
        print("dry-run only; not training or saving")
        return 0

    train(model, reference_model, margin_tensors, anchor_tensors, args)
    diagnose_cases("AFTER", model, samples, device)

    args.out_checkpoint.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "model": model.state_dict(),
            "board_size": BOARD_SIZE,
            "win_length": WIN_LENGTH,
            "channels": CHANNELS,
            "blocks": BLOCKS,
            "rapfi_teacher_policy_margin": {
                "init_checkpoint": str(args.init_checkpoint),
                "reference_checkpoint": str(args.reference_checkpoint),
                "dataset": str(args.dataset),
                "anchor_snapshots": str(args.anchor_snapshots),
                "margin": args.margin,
                "lr": args.lr,
                "epochs": args.epochs,
                "anchor_kl_weight": args.anchor_kl_weight,
                "ce_weight": args.ce_weight,
                "weight_decay": args.weight_decay,
                "train_scope": "policy_head",
            },
        },
        args.out_checkpoint,
    )
    print(f"saved {args.out_checkpoint}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
