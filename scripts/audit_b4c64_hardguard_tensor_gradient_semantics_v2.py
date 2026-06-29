#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

import numpy as np
import torch
import torch.nn.functional as F

from probe_policy_rank_topk_protected_nosave_b4c64_current_best import (
    load_model_b4c64_current_best,
    make_hard_guard_beats_mask,
)
from train_rapfi_teacher_policy_rank_topk_probe import (
    make_multisuppress_tensors,
    masked_log_softmax,
    masked_softmax,
    set_policy_head_training_mode,
)


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Corrected audit of hard-guard tensor/loss/gradient semantics under policy-head training mode."
    )
    ap.add_argument(
        "--dataset",
        type=Path,
        default=Path("analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_guarded_split_v1.json"),
    )
    ap.add_argument("--checkpoint", type=Path, default=Path("checkpoints/15x15_current_best.pt"))
    ap.add_argument("--reference-checkpoint", type=Path, default=Path("checkpoints/15x15_current_best.pt"))
    ap.add_argument("--board-size", type=int, default=15)
    ap.add_argument("--win-length", type=int, default=5)
    ap.add_argument("--channels", type=int, default=64)
    ap.add_argument("--blocks", type=int, default=4)
    ap.add_argument("--lr", type=float, default=5e-8)
    ap.add_argument("--hard-guard-reference-kl-weight", type=float, default=8.0)
    ap.add_argument("--hard-guard-target-ce-weight", type=float, default=1.0)
    ap.add_argument("--hard-guard-beats-weight", type=float, default=4.0)
    ap.add_argument("--hard-guard-beats-margin", type=float, default=0.0)
    ap.add_argument("--out-dir", type=Path, required=True)
    return ap.parse_args()


def action_to_rc(action: int, board_size: int) -> str:
    return f"{action // board_size},{action % board_size}"


def weighted_mean(values: torch.Tensor, weights: torch.Tensor) -> torch.Tensor:
    return (values * weights).sum() / weights.sum().clamp_min(1e-8)


def configure_policy_head_params(model: torch.nn.Module) -> list[torch.nn.Parameter]:
    for param in model.parameters():
        param.requires_grad = False
    params: list[torch.nn.Parameter] = []
    for name, param in model.named_parameters():
        if name.startswith("policy."):
            param.requires_grad = True
            params.append(param)
    if not params:
        raise RuntimeError("no policy head params found")
    return params


def build_terms(
    model: torch.nn.Module,
    reference_model: torch.nn.Module,
    tensors: tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor],
    beats_mask: torch.Tensor,
    args: argparse.Namespace,
) -> tuple[torch.Tensor, dict[str, torch.Tensor], dict[str, torch.Tensor]]:
    states, legal_masks, target_actions, suppress_actions, weights = tensors

    logits, _values = model(states)
    logits.retain_grad()
    log_probs = masked_log_softmax(logits, legal_masks)
    probs_from_log = log_probs.exp()

    with torch.no_grad():
        reference_model.eval()
        ref_logits, _ref_values = reference_model(states)
        ref_probs_masked_softmax = masked_softmax(ref_logits, legal_masks)
        ref_log_probs = masked_log_softmax(ref_logits, legal_masks)
        ref_probs_from_log = ref_log_probs.exp()

    target_logits = logits.gather(1, target_actions.unsqueeze(1)).squeeze(1)
    target_log_probs = log_probs.gather(1, target_actions.unsqueeze(1)).squeeze(1)
    target_probs = target_log_probs.exp()

    if suppress_actions.ndim == 1:
        suppress_actions = suppress_actions.unsqueeze(1)

    valid_suppress = suppress_actions >= 0
    safe_suppress_actions = suppress_actions.clamp_min(0)
    suppress_logits = logits.gather(1, safe_suppress_actions)
    suppress_log_probs = log_probs.gather(1, safe_suppress_actions)
    suppress_probs = suppress_log_probs.exp()
    gaps = target_logits.unsqueeze(1) - suppress_logits

    suppress_logits_for_worst = suppress_logits.masked_fill(~valid_suppress, -1.0e9)
    worst_idx = suppress_logits_for_worst.argmax(dim=1)
    worst_suppress_action = safe_suppress_actions.gather(1, worst_idx.unsqueeze(1)).squeeze(1)
    worst_suppress_logit = suppress_logits.gather(1, worst_idx.unsqueeze(1)).squeeze(1)
    worst_gap = target_logits - worst_suppress_logit

    ce_per_row = -target_log_probs
    kl_per_row_masked_softmax = (
        ref_probs_masked_softmax
        * (torch.log(ref_probs_masked_softmax.clamp_min(1e-12)) - log_probs)
    ).sum(dim=-1)
    kl_per_row_from_log = (
        ref_probs_from_log
        * (ref_log_probs - log_probs)
    ).sum(dim=-1)

    worst_hinge_per_row = F.relu(float(args.hard_guard_beats_margin) - worst_gap)

    reference_kl = weighted_mean(kl_per_row_masked_softmax, weights)
    reference_kl_from_log = weighted_mean(kl_per_row_from_log, weights)
    target_ce = weighted_mean(ce_per_row, weights)
    beats_weights = weights * beats_mask
    if float(beats_weights.sum().item()) > 0:
        beats_hinge = weighted_mean(worst_hinge_per_row, beats_weights)
    else:
        beats_hinge = torch.zeros((), dtype=target_ce.dtype, device=target_ce.device)

    loss = (
        args.hard_guard_reference_kl_weight * reference_kl
        + args.hard_guard_target_ce_weight * target_ce
        + args.hard_guard_beats_weight * beats_hinge
    )

    tensors_by_name = {
        "logits": logits,
        "log_probs": log_probs,
        "probs_from_log": probs_from_log,
        "ref_probs_masked_softmax": ref_probs_masked_softmax,
        "ref_probs_from_log": ref_probs_from_log,
        "target_actions": target_actions,
        "suppress_actions": suppress_actions,
        "valid_suppress": valid_suppress,
        "weights": weights,
        "beats_mask": beats_mask,
        "target_logits": target_logits,
        "target_probs": target_probs,
        "suppress_logits": suppress_logits,
        "suppress_probs": suppress_probs,
        "gaps": gaps,
        "worst_idx": worst_idx,
        "worst_suppress_action": worst_suppress_action,
        "worst_gap": worst_gap,
        "ce_per_row": ce_per_row,
        "kl_per_row_masked_softmax": kl_per_row_masked_softmax,
        "kl_per_row_from_log": kl_per_row_from_log,
        "worst_hinge_per_row": worst_hinge_per_row,
    }
    terms = {
        "loss": loss,
        "reference_kl_masked_softmax": reference_kl,
        "reference_kl_from_log": reference_kl_from_log,
        "target_ce": target_ce,
        "beats_hinge": beats_hinge,
    }
    return loss, terms, tensors_by_name


def row_metrics(
    model: torch.nn.Module,
    samples: list[dict[str, Any]],
    tensors: tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor],
    args: argparse.Namespace,
) -> list[dict[str, Any]]:
    states, legal_masks, target_actions, suppress_actions, weights = tensors
    with torch.no_grad():
        logits, _ = model(states)
        log_probs = masked_log_softmax(logits, legal_masks)
        probs = log_probs.exp()

    rows: list[dict[str, Any]] = []
    for i, sample in enumerate(samples):
        target = int(target_actions[i].item())
        legal = legal_masks[i].bool()
        legal_probs = probs[i].clone()
        legal_probs[~legal] = -1.0
        sorted_actions = torch.argsort(legal_probs, descending=True)
        rank = int((sorted_actions == target).nonzero(as_tuple=False)[0].item()) + 1

        valid = suppress_actions[i] >= 0
        suppress = [int(x.item()) for x in suppress_actions[i][valid]]
        target_logit = float(logits[i, target].item())
        suppress_logits = [float(logits[i, a].item()) for a in suppress]
        gaps = [target_logit - s for s in suppress_logits]
        worst_gap = min(gaps) if gaps else None

        rows.append({
            "case_id": sample.get("case_id"),
            "hard_guard_role": sample.get("guarded_split_v1_hard_guard_role"),
            "target_action": target,
            "target_rc": action_to_rc(target, args.board_size),
            "target_prob": float(probs[i, target].item()),
            "target_logit": target_logit,
            "rank": rank,
            "rank_gt50": int(rank > 50),
            "suppress_actions": json.dumps(suppress),
            "suppress_rcs": json.dumps([action_to_rc(a, args.board_size) for a in suppress]),
            "suppress_logits": json.dumps(suppress_logits),
            "gaps": json.dumps(gaps),
            "worst_gap": worst_gap,
        })
    return rows


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    device = torch.device("cpu")
    torch.manual_seed(17)
    np.random.seed(17)

    data = json.loads(args.dataset.read_text())
    hard_samples = data.get("hard_guard_samples", []) or []
    if not hard_samples:
        raise ValueError("dataset has no hard_guard_samples")

    model = load_model_b4c64_current_best(
        args.checkpoint,
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

    policy_params = configure_policy_head_params(model)
    set_policy_head_training_mode(model)

    tensors = make_multisuppress_tensors(hard_samples, device)
    beats_mask = make_hard_guard_beats_mask(hard_samples, device)

    before_rows = row_metrics(model, hard_samples, tensors, args)

    loss, terms, tb = build_terms(model, reference_model, tensors, beats_mask, args)
    model.zero_grad(set_to_none=True)
    loss.backward()

    logits_grad = tb["logits"].grad.detach().clone()
    target_actions = tb["target_actions"]
    suppress_actions = tb["suppress_actions"]
    valid_suppress = tb["valid_suppress"]

    grad_rows: list[dict[str, Any]] = []
    for i, sample in enumerate(hard_samples):
        target = int(target_actions[i].item())
        valid = valid_suppress[i]
        suppress = [int(x.item()) for x in suppress_actions[i][valid]]
        target_grad = float(logits_grad[i, target].item())
        suppress_grads = [float(logits_grad[i, a].item()) for a in suppress]

        grad_rows.append({
            "case_id": sample.get("case_id"),
            "hard_guard_role": sample.get("guarded_split_v1_hard_guard_role"),
            "target_action": target,
            "target_rc": action_to_rc(target, args.board_size),
            "beats_mask": float(beats_mask[i].item()),
            "weight": float(tb["weights"][i].item()),
            "target_prob_before": float(tb["target_probs"][i].item()),
            "target_logit_before": float(tb["target_logits"][i].item()),
            "target_logit_grad": target_grad,
            "optimizer_would_change_target_logit_opposite_grad": -args.lr * target_grad,
            "suppress_actions": json.dumps(suppress),
            "suppress_rcs": json.dumps([action_to_rc(a, args.board_size) for a in suppress]),
            "suppress_logits_before": json.dumps([float(tb["suppress_logits"][i, j].item()) for j in range(len(suppress))]),
            "suppress_logit_grads": json.dumps(suppress_grads),
            "optimizer_would_change_suppress_logits_opposite_grad": json.dumps([-args.lr * g for g in suppress_grads]),
            "worst_suppress_action": int(tb["worst_suppress_action"][i].item()),
            "worst_suppress_rc": action_to_rc(int(tb["worst_suppress_action"][i].item()), args.board_size),
            "worst_gap_before": float(tb["worst_gap"][i].item()),
            "ce_per_row": float(tb["ce_per_row"][i].item()),
            "kl_per_row_masked_softmax": float(tb["kl_per_row_masked_softmax"][i].item()),
            "kl_per_row_from_log": float(tb["kl_per_row_from_log"][i].item()),
            "worst_hinge_per_row": float(tb["worst_hinge_per_row"][i].item()),
            "target_gradient_direction_expected_for_ce": "negative_grad_means_optimizer_increases_target_logit",
            "target_grad_sign_ok_for_increase": target_grad < 0.0,
        })

    optimizer = torch.optim.AdamW(policy_params, lr=args.lr, weight_decay=0.0)
    optimizer.zero_grad(set_to_none=True)
    set_policy_head_training_mode(model)
    loss2, _terms2, _tb2 = build_terms(model, reference_model, tensors, beats_mask, args)
    loss2.backward()
    torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=0.5)
    optimizer.step()
    set_policy_head_training_mode(model)

    after_rows = row_metrics(model, hard_samples, tensors, args)

    compare_rows: list[dict[str, Any]] = []
    for b, a in zip(before_rows, after_rows):
        compare_rows.append({
            "case_id": b["case_id"],
            "hard_guard_role": b["hard_guard_role"],
            "rank_before": b["rank"],
            "rank_after": a["rank"],
            "rank_delta": a["rank"] - b["rank"],
            "rank_gt50_before": b["rank_gt50"],
            "rank_gt50_after": a["rank_gt50"],
            "target_prob_before": b["target_prob"],
            "target_prob_after": a["target_prob"],
            "target_prob_delta": a["target_prob"] - b["target_prob"],
            "target_logit_before": b["target_logit"],
            "target_logit_after": a["target_logit"],
            "target_logit_delta": a["target_logit"] - b["target_logit"],
            "worst_gap_before": b["worst_gap"],
            "worst_gap_after": a["worst_gap"],
            "worst_gap_delta": None if b["worst_gap"] is None or a["worst_gap"] is None else a["worst_gap"] - b["worst_gap"],
        })

    with (args.out_dir / "hardguard_gradient_rows.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(grad_rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(grad_rows)

    with (args.out_dir / "hardguard_one_step_compare.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(compare_rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(compare_rows)

    terms_float = {k: float(v.detach().item()) for k, v in terms.items()}
    kl_inconsistency = abs(terms_float["reference_kl_masked_softmax"] - terms_float["reference_kl_from_log"])

    summary = {
        "scope": "corrected hard guard tensor/gradient semantics audit under policy-head training mode only; no checkpoint save; no C export; no public benchmark; no promotion",
        "dataset": str(args.dataset),
        "checkpoint": str(args.checkpoint),
        "reference_checkpoint": str(args.reference_checkpoint),
        "hard_guard_rows": len(hard_samples),
        "policy_head_trainable_params": sum(p.numel() for p in policy_params),
        "terms": terms_float,
        "kl_inconsistency_abs": kl_inconsistency,
        "gradient_rows": grad_rows,
        "one_step_compare": compare_rows,
        "checkpoint_like_outputs": sorted(str(p) for p in args.out_dir.glob("*") if p.suffix in {".pt", ".pth", ".bin"}),
        "audit_findings": {
            "masked_softmax_kl_nonzero_with_identical_models": terms_float["reference_kl_masked_softmax"] > 1e-6,
            "masked_log_softmax_kl_nonzero_with_identical_models": abs(terms_float["reference_kl_from_log"]) > 1e-6,
            "any_target_grad_wrong_sign_for_ce_increase": any(not r["target_grad_sign_ok_for_increase"] for r in grad_rows),
            "any_rank_regressed_after_one_step": any(r["rank_delta"] > 0 for r in compare_rows),
            "any_target_prob_decreased_after_one_step": any(r["target_prob_delta"] < 0 for r in compare_rows),
        },
    }
    (args.out_dir / "hardguard_gradient_semantics_v2_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")

    lines = []
    lines.append("# b4c64 hard guard tensor/gradient semantics audit v2")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append("- Corrected audit under `set_policy_head_training_mode(model)`.")
    lines.append("- Audit only.")
    lines.append("- No checkpoint save, C export, public benchmark, promotion, or current-best overwrite was performed.")
    lines.append("")
    lines.append("## Loss terms")
    lines.append("")
    for k, v in terms_float.items():
        lines.append(f"- `{k}`: `{v}`")
    lines.append(f"- `kl_inconsistency_abs`: `{kl_inconsistency}`")
    lines.append("")
    lines.append("## Key audit findings")
    lines.append("")
    for k, v in summary["audit_findings"].items():
        lines.append(f"- `{k}`: `{v}`")
    lines.append("")
    lines.append("## Gradient rows")
    lines.append("")
    lines.append("| case_id | role | target rc | target grad | expected target-logit step | grad sign ok | worst gap before | CE | KL masked_softmax | KL from log | worst hinge |")
    lines.append("|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for r in grad_rows:
        lines.append(
            f"| `{r['case_id']}` | `{r['hard_guard_role']}` | `{r['target_rc']}` | "
            f"{r['target_logit_grad']} | {r['optimizer_would_change_target_logit_opposite_grad']} | "
            f"{r['target_grad_sign_ok_for_increase']} | {r['worst_gap_before']} | "
            f"{r['ce_per_row']} | {r['kl_per_row_masked_softmax']} | "
            f"{r['kl_per_row_from_log']} | {r['worst_hinge_per_row']} |"
        )
    lines.append("")
    lines.append("## One-step compare")
    lines.append("")
    lines.append("| case_id | rank before→after | target prob delta | target logit delta | worst gap delta |")
    lines.append("|---|---:|---:|---:|---:|")
    for r in compare_rows:
        lines.append(
            f"| `{r['case_id']}` | {r['rank_before']}→{r['rank_after']} | "
            f"{r['target_prob_delta']} | {r['target_logit_delta']} | {r['worst_gap_delta']} |"
        )
    lines.append("")
    lines.append("## Decision")
    lines.append("")
    if summary["audit_findings"]["any_rank_regressed_after_one_step"] or summary["audit_findings"]["any_target_prob_decreased_after_one_step"]:
        lines.append("- Even under policy-head training mode, the hard guard one-step update damages guard rows.")
        lines.append("- Next step should inspect hard guard suppress set and whether worst-hinge/CE competition is selecting the intended suppressor.")
    elif summary["audit_findings"]["masked_log_softmax_kl_nonzero_with_identical_models"]:
        lines.append("- Gradient direction is safe under policy-head mode, but reference KL is still non-zero with identical checkpoints.")
        lines.append("- Next step should isolate whether reference/model logits are computed under different mode/order or whether checkpoint load is nondeterministic.")
    else:
        lines.append("- Gradient signs and one-step behavior are safe under policy-head mode.")
        lines.append("- The earlier hardguard-only failure likely comes from wrapper train/eval sequencing or post-update diagnostics mode; patch wrapper to force policy-head mode before after-diagnostics.")
    lines.append("")
    lines.append("## Outputs")
    lines.append("")
    for p in sorted(args.out_dir.glob("*")):
        if p.is_file():
            lines.append(f"- `{p}`")
    lines.append("")
    (args.out_dir / "hardguard_gradient_semantics_v2_report.md").write_text("\n".join(lines))

    print("terms:", json.dumps(terms_float, sort_keys=True))
    print("audit_findings:", json.dumps(summary["audit_findings"], sort_keys=True))
    print("wrote", args.out_dir)


if __name__ == "__main__":
    main()
