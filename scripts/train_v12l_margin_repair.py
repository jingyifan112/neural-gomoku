from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import torch
from torch.nn import functional as F

from gomoku_agent.model import PolicyValueNet


BOARD_SIZE = 15


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train v12l pairwise margin repair candidate.")
    parser.add_argument("--dataset", type=Path, default=Path("analysis/v12l_margin_repair_dataset.json"))
    parser.add_argument("--anchor-snapshots", type=Path, default=Path("analysis/v12i_failure_board_snapshots.json"))
    parser.add_argument("--init-checkpoint", type=Path, default=Path("checkpoints/15x15_v12i_candidate.pt"))
    parser.add_argument("--reference-checkpoint", type=Path, default=None)
    parser.add_argument("--out-checkpoint", type=Path, default=Path("checkpoints/15x15_v12l_margin_candidate.pt"))
    parser.add_argument("--margin", type=float, default=1.0)
    parser.add_argument("--lr", type=float, default=1e-5)
    parser.add_argument("--epochs", type=int, default=40)
    parser.add_argument("--anchor-kl-weight", type=float, default=0.05)
    parser.add_argument("--anchor-value-weight", type=float, default=0.0)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--seed", type=int, default=12)
    parser.add_argument("--print-every", type=int, default=5)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def load_checkpoint_payload(path: Path, device: torch.device) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    return torch.load(path, map_location=device)


def build_model_from_payload(payload: dict[str, Any], device: torch.device) -> PolicyValueNet:
    board_size = int(payload.get("board_size", 15))
    channels = int(payload.get("channels", 64))
    blocks = int(payload.get("blocks", 4))
    model = PolicyValueNet(board_size=board_size, channels=channels, blocks=blocks).to(device)
    model.load_state_dict(payload["model"])
    return model


def parse_board_snapshot(snapshot: str) -> list[list[int]]:
    rows: list[list[int]] = []
    for raw_line in snapshot.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if set(line) <= {"-"}:
            continue

        tokens = line.split()
        if len(tokens) != BOARD_SIZE:
            continue
        if not all(tok in {".", "X", "O"} for tok in tokens):
            continue

        row = []
        for tok in tokens:
            if tok == ".":
                row.append(0)
            elif tok == "X":
                row.append(1)
            elif tok == "O":
                row.append(-1)
            else:
                raise ValueError(f"unexpected token {tok!r}")
        rows.append(row)

    if len(rows) != BOARD_SIZE:
        raise ValueError(f"expected {BOARD_SIZE} rows, got {len(rows)}")
    return rows


def parse_side_to_move(side: str) -> int:
    side_l = side.strip().lower()
    if side_l == "black":
        return 1
    if side_l == "white":
        return -1
    raise ValueError(f"unknown side_to_move {side!r}")


def encode_state(board: list[list[int]], current_player: int) -> np.ndarray:
    grid = np.asarray(board, dtype=np.int8)
    current = (grid == current_player).astype(np.float32)
    opponent = (grid == -current_player).astype(np.float32)
    last = np.zeros_like(current, dtype=np.float32)
    return np.stack([current, opponent, last], axis=0)


def legal_mask_from_board(board: list[list[int]]) -> np.ndarray:
    grid = np.asarray(board, dtype=np.int8)
    return (grid.reshape(-1) == 0).astype(np.float32)


def rc_to_action(rc: list[int], board_size: int = BOARD_SIZE) -> int:
    r, c = rc
    return int(r) * board_size + int(c)


def load_margin_cases(dataset_path: Path) -> list[dict[str, Any]]:
    dataset = json.loads(dataset_path.read_text())
    samples = dataset["samples"]
    if len(samples) == 0:
        raise ValueError("empty margin dataset")
    return samples


def load_anchor_samples(snapshot_path: Path) -> list[dict[str, Any]]:
    if not snapshot_path.exists():
        print(f"warning: no anchor snapshots at {snapshot_path}; KL anti-drift disabled")
        return []

    raw = json.loads(snapshot_path.read_text())
    anchors = []
    for item in raw:
        board = parse_board_snapshot(item["board_snapshot_before_decision"])
        current_player = parse_side_to_move(item["side_to_move"])
        anchors.append(
            {
                "case_id": f"anchor_g{item.get('game_number')}_m{item.get('move_count')}",
                "board": board,
                "current_player": current_player,
                "state": encode_state(board, current_player),
                "legal_mask": legal_mask_from_board(board),
            }
        )
    return anchors


def make_margin_tensors(samples: list[dict[str, Any]], device: torch.device) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
    states = []
    masks = []
    target_actions = []
    suppress_actions = []

    for sample in samples:
        board = sample["board"]
        current_player = int(sample["current_player"])
        target = sample["target_rc"]
        suppress = sample["suppress_rc"]

        states.append(encode_state(board, current_player))
        masks.append(legal_mask_from_board(board))
        target_actions.append(rc_to_action(target))
        suppress_actions.append(rc_to_action(suppress))

    return (
        torch.tensor(np.stack(states), dtype=torch.float32, device=device),
        torch.tensor(np.stack(masks), dtype=torch.float32, device=device),
        torch.tensor(target_actions, dtype=torch.long, device=device),
        torch.tensor(suppress_actions, dtype=torch.long, device=device),
    )


def make_anchor_tensors(anchors: list[dict[str, Any]], device: torch.device) -> tuple[torch.Tensor, torch.Tensor] | None:
    if not anchors:
        return None
    states = torch.tensor(np.stack([a["state"] for a in anchors]), dtype=torch.float32, device=device)
    masks = torch.tensor(np.stack([a["legal_mask"] for a in anchors]), dtype=torch.float32, device=device)
    return states, masks


def masked_log_softmax(logits: torch.Tensor, legal_mask: torch.Tensor) -> torch.Tensor:
    masked = logits.masked_fill(legal_mask <= 0, -1e9)
    return F.log_softmax(masked, dim=-1)


def masked_softmax(logits: torch.Tensor, legal_mask: torch.Tensor) -> torch.Tensor:
    return torch.exp(masked_log_softmax(logits, legal_mask))


def rank_of_action(probs: torch.Tensor, action: int, legal_mask: torch.Tensor) -> int:
    legal_actions = torch.nonzero(legal_mask > 0, as_tuple=False).flatten()
    legal_probs = probs[legal_actions]
    order = torch.argsort(legal_probs, descending=True)
    ranked_actions = legal_actions[order].tolist()
    return ranked_actions.index(int(action)) + 1


@torch.no_grad()
def diagnose_cases(
    label: str,
    model: PolicyValueNet,
    samples: list[dict[str, Any]],
    device: torch.device,
) -> None:
    model.eval()
    print("=" * 100)
    print(label)
    for sample in samples:
        state = torch.tensor(encode_state(sample["board"], int(sample["current_player"])), dtype=torch.float32, device=device).unsqueeze(0)
        mask = torch.tensor(legal_mask_from_board(sample["board"]), dtype=torch.float32, device=device).unsqueeze(0)

        logits, value = model(state)
        probs = masked_softmax(logits, mask)[0]
        logits0 = logits[0]
        mask0 = mask[0]

        target_action = rc_to_action(sample["target_rc"])
        suppress_action = rc_to_action(sample["suppress_rc"])

        target_prob = float(probs[target_action].item())
        suppress_prob = float(probs[suppress_action].item())
        target_logit = float(logits0[target_action].item())
        suppress_logit = float(logits0[suppress_action].item())
        gap = target_logit - suppress_logit

        print("-" * 100)
        print("case_id:", sample["case_id"])
        print("target_xy:", sample["target_xy"], "target_rc:", sample["target_rc"])
        print("suppress_xy:", sample["suppress_xy"], "suppress_rc:", sample["suppress_rc"])
        print("old_final:", sample.get("old_final"))
        print(f"value={float(value.item()):.6f}")
        print(
            f"target_prob={target_prob:.8f} "
            f"suppress_prob={suppress_prob:.8f} "
            f"target_rank={rank_of_action(probs, target_action, mask0)} "
            f"suppress_rank={rank_of_action(probs, suppress_action, mask0)}"
        )
        print(
            f"target_logit={target_logit:.6f} "
            f"suppress_logit={suppress_logit:.6f} "
            f"logit_gap={gap:.6f}"
        )


def train(
    model: PolicyValueNet,
    reference_model: PolicyValueNet,
    margin_tensors: tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor],
    anchor_tensors: tuple[torch.Tensor, torch.Tensor] | None,
    args: argparse.Namespace,
) -> None:
    states, legal_masks, target_actions, suppress_actions = margin_tensors
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-5)

    reference_model.eval()

    for epoch in range(1, args.epochs + 1):
        model.train()
        logits, _values = model(states)

        target_logits = logits.gather(1, target_actions.unsqueeze(1)).squeeze(1)
        suppress_logits = logits.gather(1, suppress_actions.unsqueeze(1)).squeeze(1)
        gaps = target_logits - suppress_logits
        margin_loss = F.relu(args.margin - gaps).mean()

        anchor_kl = torch.tensor(0.0, device=states.device)
        anchor_value_loss = torch.tensor(0.0, device=states.device)

        if anchor_tensors is not None and args.anchor_kl_weight > 0:
            anchor_states, anchor_masks = anchor_tensors
            current_logits, current_values = model(anchor_states)
            with torch.no_grad():
                ref_logits, ref_values = reference_model(anchor_states)
                ref_probs = masked_softmax(ref_logits, anchor_masks)

            current_log_probs = masked_log_softmax(current_logits, anchor_masks)
            anchor_kl = (ref_probs * (torch.log(ref_probs.clamp_min(1e-12)) - current_log_probs)).sum(dim=-1).mean()

            if args.anchor_value_weight > 0:
                anchor_value_loss = F.mse_loss(current_values, ref_values)

        loss = margin_loss + args.anchor_kl_weight * anchor_kl + args.anchor_value_weight * anchor_value_loss

        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()

        if epoch == 1 or epoch == args.epochs or epoch % args.print_every == 0:
            gap_str = ", ".join(f"{float(g):.4f}" for g in gaps.detach().cpu())
            print(
                f"epoch {epoch:03d}/{args.epochs} "
                f"loss={float(loss.item()):.6f} "
                f"margin_loss={float(margin_loss.item()):.6f} "
                f"anchor_kl={float(anchor_kl.item()):.6f} "
                f"gaps=[{gap_str}]",
                flush=True,
            )


def main() -> None:
    args = parse_args()
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    init_payload = load_checkpoint_payload(args.init_checkpoint, device)
    reference_path = args.reference_checkpoint or args.init_checkpoint
    reference_payload = load_checkpoint_payload(reference_path, device)

    model = build_model_from_payload(init_payload, device)
    reference_model = build_model_from_payload(reference_payload, device)
    for p in reference_model.parameters():
        p.requires_grad = False

    samples = load_margin_cases(args.dataset)
    anchors = load_anchor_samples(args.anchor_snapshots)

    print(f"device: {device}")
    print(f"loaded init checkpoint: {args.init_checkpoint}")
    print(f"loaded reference checkpoint: {reference_path}")
    print(f"margin samples: {len(samples)}")
    print(f"anchor samples: {len(anchors)}")
    print(f"out checkpoint: {args.out_checkpoint}")
    print("NOTE: this script never writes checkpoints/15x15_current_best.pt")

    margin_tensors = make_margin_tensors(samples, device)
    anchor_tensors = make_anchor_tensors(anchors, device)

    diagnose_cases("BEFORE", model, samples, device)

    if args.dry_run:
        print("dry-run only; not training or saving")
        return

    train(model, reference_model, margin_tensors, anchor_tensors, args)

    diagnose_cases("AFTER", model, samples, device)

    args.out_checkpoint.parent.mkdir(parents=True, exist_ok=True)
    save_payload = {
        "model": model.state_dict(),
        "board_size": int(init_payload.get("board_size", 15)),
        "win_length": int(init_payload.get("win_length", 5)),
        "channels": int(init_payload.get("channels", 64)),
        "blocks": int(init_payload.get("blocks", 4)),
        "v12l_margin_repair": {
            "init_checkpoint": str(args.init_checkpoint),
            "reference_checkpoint": str(reference_path),
            "dataset": str(args.dataset),
            "margin": args.margin,
            "lr": args.lr,
            "epochs": args.epochs,
            "anchor_kl_weight": args.anchor_kl_weight,
            "anchor_value_weight": args.anchor_value_weight,
        },
    }
    torch.save(save_payload, args.out_checkpoint)
    print(f"saved {args.out_checkpoint}")


if __name__ == "__main__":
    main()
