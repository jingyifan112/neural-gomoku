from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

import train_v12l_margin_repair as base


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train v12l margin repair with frozen BatchNorm stats.")
    parser.add_argument("--dataset", type=Path, default=Path("analysis/v12l_margin_repair_dataset.json"))
    parser.add_argument("--anchor-snapshots", type=Path, default=Path("analysis/v12i_failure_board_snapshots.json"))
    parser.add_argument("--init-checkpoint", type=Path, required=True)
    parser.add_argument("--reference-checkpoint", type=Path, required=True)
    parser.add_argument("--out-checkpoint", type=Path, required=True)
    parser.add_argument("--margin", type=float, default=1.0)
    parser.add_argument("--lr", type=float, default=5e-6)
    parser.add_argument("--epochs", type=int, default=40)
    parser.add_argument("--anchor-kl-weight", type=float, default=0.05)
    parser.add_argument("--case-weights", type=str, default="2.0,1.0")
    parser.add_argument("--seed", type=int, default=21)
    parser.add_argument("--print-every", type=int, default=5)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def freeze_batchnorm_stats(model: nn.Module) -> None:
    for module in model.modules():
        if isinstance(module, (nn.BatchNorm1d, nn.BatchNorm2d, nn.BatchNorm3d)):
            module.eval()


def train_frozen_bn(
    model: base.PolicyValueNet,
    reference_model: base.PolicyValueNet,
    margin_tensors,
    anchor_tensors,
    args: argparse.Namespace,
) -> None:
    states, legal_masks, target_actions, suppress_actions = margin_tensors

    case_weights = [float(x) for x in args.case_weights.split(",")]
    if len(case_weights) != len(target_actions):
        raise ValueError(f"--case-weights must have {len(target_actions)} values")
    weights = torch.tensor(case_weights, dtype=torch.float32, device=states.device)

    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-5)

    reference_model.eval()

    for epoch in range(1, args.epochs + 1):
        model.train()
        freeze_batchnorm_stats(model)

        logits, _values = model(states)
        target_logits = logits.gather(1, target_actions.unsqueeze(1)).squeeze(1)
        suppress_logits = logits.gather(1, suppress_actions.unsqueeze(1)).squeeze(1)
        gaps = target_logits - suppress_logits

        per_case_margin = F.relu(args.margin - gaps)
        margin_loss = (weights * per_case_margin).sum() / weights.sum()

        anchor_kl = torch.tensor(0.0, device=states.device)
        if anchor_tensors is not None and args.anchor_kl_weight > 0:
            anchor_states, anchor_masks = anchor_tensors
            current_logits, _current_values = model(anchor_states)
            with torch.no_grad():
                ref_logits, _ref_values = reference_model(anchor_states)
                ref_probs = base.masked_softmax(ref_logits, anchor_masks)

            current_log_probs = base.masked_log_softmax(current_logits, anchor_masks)
            anchor_kl = (
                ref_probs * (torch.log(ref_probs.clamp_min(1e-12)) - current_log_probs)
            ).sum(dim=-1).mean()

        loss = margin_loss + args.anchor_kl_weight * anchor_kl

        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=0.5)
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

    init_payload = base.load_checkpoint_payload(args.init_checkpoint, device)
    ref_payload = base.load_checkpoint_payload(args.reference_checkpoint, device)

    model = base.build_model_from_payload(init_payload, device)
    reference_model = base.build_model_from_payload(ref_payload, device)
    for p in reference_model.parameters():
        p.requires_grad = False

    samples = base.load_margin_cases(args.dataset)
    anchors = base.load_anchor_samples(args.anchor_snapshots)

    print(f"device: {device}")
    print(f"loaded init checkpoint: {args.init_checkpoint}")
    print(f"loaded reference checkpoint: {args.reference_checkpoint}")
    print(f"margin samples: {len(samples)}")
    print(f"anchor samples: {len(anchors)}")
    print(f"case_weights: {args.case_weights}")
    print(f"out checkpoint: {args.out_checkpoint}")
    print("NOTE: frozen BatchNorm stats; never writes checkpoints/15x15_current_best.pt")

    margin_tensors = base.make_margin_tensors(samples, device)
    anchor_tensors = base.make_anchor_tensors(anchors, device)

    base.diagnose_cases("BEFORE", model, samples, device)

    if args.dry_run:
        print("dry-run only; not training or saving")
        return

    train_frozen_bn(model, reference_model, margin_tensors, anchor_tensors, args)

    freeze_batchnorm_stats(model)
    base.diagnose_cases("AFTER", model, samples, device)

    args.out_checkpoint.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "model": model.state_dict(),
            "board_size": int(init_payload.get("board_size", 15)),
            "win_length": int(init_payload.get("win_length", 5)),
            "channels": int(init_payload.get("channels", 64)),
            "blocks": int(init_payload.get("blocks", 4)),
            "v12l_margin_repair_frozen_bn": {
                "init_checkpoint": str(args.init_checkpoint),
                "reference_checkpoint": str(args.reference_checkpoint),
                "dataset": str(args.dataset),
                "margin": args.margin,
                "lr": args.lr,
                "epochs": args.epochs,
                "anchor_kl_weight": args.anchor_kl_weight,
                "case_weights": args.case_weights,
                "frozen_batchnorm_stats": True,
            },
        },
        args.out_checkpoint,
    )
    print(f"saved {args.out_checkpoint}")


if __name__ == "__main__":
    main()
