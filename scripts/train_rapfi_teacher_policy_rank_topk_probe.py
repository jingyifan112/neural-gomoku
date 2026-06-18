from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import torch
from torch.nn import functional as F

from train_rapfi_teacher_policy_margin import (
    BOARD_SIZE,
    WIN_LENGTH,
    CHANNELS,
    BLOCKS,
    encode_state,
    legal_mask_from_board,
    load_anchor_samples,
    load_model,
    configure_policy_head_trainable,
    set_policy_head_training_mode,
    masked_log_softmax,
    masked_softmax,
    rank_of_action,
    rc_to_action,
    make_anchor_tensors,
)


def action_to_rc(action: int) -> list[int]:
    return [int(action) // BOARD_SIZE, int(action) % BOARD_SIZE]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Policy-only rank/top-k multi-suppress training probe."
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        default=Path(
            "analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected.json"
        ),
    )
    parser.add_argument(
        "--anchor-snapshots",
        type=Path,
        default=Path("analysis/public_benchmark_eval/corpus8_selected_board_snapshots.json"),
    )
    parser.add_argument("--init-checkpoint", type=Path, default=Path("checkpoints/15x15_current_best.pt"))
    parser.add_argument("--reference-checkpoint", type=Path, default=Path("checkpoints/15x15_current_best.pt"))
    parser.add_argument(
        "--out-checkpoint",
        type=Path,
        default=Path("checkpoints/15x15_policy_rank_topk_probe.pt"),
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("analysis/integration_eval/policy_only_rank_topk_training_probe_dryrun_report.md"),
    )
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


def assert_not_current_best(path: Path) -> None:
    if path.name == "15x15_current_best.pt":
        raise ValueError("refusing to write checkpoints/15x15_current_best.pt")


def load_multisuppress_samples(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    dataset = json.loads(path.read_text(encoding="utf-8"))
    samples = dataset.get("samples", [])
    if not samples:
        raise ValueError(f"empty or missing samples in dataset: {path}")
    return dataset, samples


def make_multisuppress_tensors(
    samples: list[dict[str, Any]],
    device: torch.device,
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
        legal_mask = legal_mask_from_board(board)

        target_action = rc_to_action(sample["target_rc"])
        suppress = [rc_to_action(rc) for rc in sample["suppress_rcs"]]

        if expected_suppress_count is None:
            expected_suppress_count = len(suppress)
        if len(suppress) != expected_suppress_count:
            raise ValueError(
                f"{sample['case_id']}: variable suppress count not supported in this first probe"
            )

        if legal_mask[target_action] <= 0:
            raise ValueError(f"{sample['case_id']}: illegal target_rc {sample['target_rc']}")

        seen: set[int] = set()
        for action in suppress:
            if legal_mask[action] <= 0:
                raise ValueError(f"{sample['case_id']}: illegal suppress_rc {action_to_rc(action)}")
            if action == target_action:
                raise ValueError(f"{sample['case_id']}: suppress equals target {action_to_rc(action)}")
            if action in seen:
                raise ValueError(f"{sample['case_id']}: duplicate suppress {action_to_rc(action)}")
            seen.add(action)

        states.append(encode_state(board, current_player))
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
        legal_np = legal_mask_from_board(board)

        target_action = rc_to_action(sample["target_rc"])
        suppress_actions = [rc_to_action(rc) for rc in sample["suppress_rcs"]]

        state = torch.tensor(
            encode_state(board, current_player),
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
    lines += ["# Policy-only rank/top-k training probe report", ""]
    lines += ["## Scope", ""]
    lines += ["- Policy-head-only rank/top-k multi-suppress probe."]
    lines += ["- No C export, no public benchmark, no promotion."]
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
    lines += [f"- anchor_snapshots: {args.anchor_snapshots}"]
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
        lines.append("Checkpoint saved. It must pass evaluate_policy_rank_topk_gate.py before any further action.")
    else:
        lines.append("No checkpoint was saved.")

    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    args = parse_args()
    if not args.no_save:
        assert_not_current_best(args.out_checkpoint)

    torch.manual_seed(args.seed)
    np.random.seed(args.seed)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    dataset_meta, samples = load_multisuppress_samples(args.dataset)
    anchors = load_anchor_samples(args.anchor_snapshots)
    tensors = make_multisuppress_tensors(samples, device)
    anchor_tensors = make_anchor_tensors(anchors, device)

    model = load_model(args.init_checkpoint, device)
    reference_model = load_model(args.reference_checkpoint, device)
    reference_model.eval()
    for parameter in reference_model.parameters():
        parameter.requires_grad = False

    anchor_states, anchor_masks = anchor_tensors
    with torch.no_grad():
        ref_anchor_logits, _ref_values = reference_model(anchor_states)
        ref_anchor_probs = masked_softmax(ref_anchor_logits, anchor_masks)

    before = diagnose_summary(model, samples, device)
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
        after = diagnose_summary(model, samples, device)

        if args.no_save:
            print("no checkpoint saved due to --no-save")
        else:
            args.out_checkpoint.parent.mkdir(parents=True, exist_ok=True)
            torch.save(
                {
                    "model": model.state_dict(),
                    "board_size": BOARD_SIZE,
                    "win_length": WIN_LENGTH,
                    "channels": CHANNELS,
                    "blocks": BLOCKS,
                    "rapfi_teacher_policy_rank_topk_probe": {
                        "init_checkpoint": str(args.init_checkpoint),
                        "reference_checkpoint": str(args.reference_checkpoint),
                        "dataset": str(args.dataset),
                        "anchor_snapshots": str(args.anchor_snapshots),
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
                    },
                },
                args.out_checkpoint,
            )
            saved_checkpoint = True
            print("saved_checkpoint:", args.out_checkpoint)

    write_report(
        args.report,
        args,
        dataset_meta,
        before,
        after,
        initial_terms,
        history,
        saved_checkpoint,
    )
    print("report:", args.report)
    print("status: no export, no public benchmark, no promotion")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
