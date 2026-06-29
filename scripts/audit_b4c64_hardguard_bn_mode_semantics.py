#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

import torch

from probe_policy_rank_topk_protected_nosave_b4c64_current_best import (
    load_model_b4c64_current_best,
)
from train_rapfi_teacher_policy_rank_topk_probe import (
    make_multisuppress_tensors,
    masked_log_softmax,
    set_policy_head_training_mode,
)


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Audit b4c64 hard-guard output differences under eval/train/policy-head training modes."
    )
    ap.add_argument(
        "--dataset",
        type=Path,
        default=Path("analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_guarded_split_v1.json"),
    )
    ap.add_argument("--checkpoint", type=Path, default=Path("checkpoints/15x15_current_best.pt"))
    ap.add_argument("--board-size", type=int, default=15)
    ap.add_argument("--win-length", type=int, default=5)
    ap.add_argument("--channels", type=int, default=64)
    ap.add_argument("--blocks", type=int, default=4)
    ap.add_argument("--out-dir", type=Path, required=True)
    return ap.parse_args()


def action_to_rc(action: int, board_size: int) -> str:
    return f"{action // board_size},{action % board_size}"


def module_mode_rows(model: torch.nn.Module) -> list[dict[str, Any]]:
    rows = []
    for name, mod in model.named_modules():
        if name == "":
            continue
        cls = mod.__class__.__name__
        if "BatchNorm" in cls or name.startswith("policy") or name.startswith("trunk") or name.startswith("res_blocks"):
            rows.append({
                "name": name,
                "class": cls,
                "training": bool(mod.training),
            })
    return rows


def eval_samples(
    model: torch.nn.Module,
    samples: list[dict[str, Any]],
    tensors: tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor],
    mode_name: str,
    args: argparse.Namespace,
) -> list[dict[str, Any]]:
    states, legal_masks, target_actions, suppress_actions, weights = tensors
    with torch.no_grad():
        logits, _ = model(states)
        log_probs = masked_log_softmax(logits, legal_masks)
        probs = log_probs.exp()

    rows = []
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
            "mode": mode_name,
            "case_id": sample.get("case_id"),
            "hard_guard_role": sample.get("guarded_split_v1_hard_guard_role"),
            "target_action": target,
            "target_rc": action_to_rc(target, args.board_size),
            "rank": rank,
            "rank_gt50": int(rank > 50),
            "target_prob": float(probs[i, target].item()),
            "target_logit": target_logit,
            "suppress_actions": json.dumps(suppress),
            "suppress_rcs": json.dumps([action_to_rc(a, args.board_size) for a in suppress]),
            "suppress_logits": json.dumps(suppress_logits),
            "gaps": json.dumps(gaps),
            "worst_gap": worst_gap,
        })
    return rows


def max_abs_delta(rows_a: list[dict[str, Any]], rows_b: list[dict[str, Any]], key: str) -> float:
    vals = []
    for a, b in zip(rows_a, rows_b):
        vals.append(abs(float(a[key]) - float(b[key])))
    return max(vals) if vals else 0.0


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    device = torch.device("cpu")
    data = json.loads(args.dataset.read_text())
    hard_samples = data.get("hard_guard_samples", []) or []
    if not hard_samples:
        raise ValueError("dataset has no hard_guard_samples")

    tensors = make_multisuppress_tensors(hard_samples, device)

    mode_outputs: dict[str, list[dict[str, Any]]] = {}
    mode_module_rows: dict[str, list[dict[str, Any]]] = {}

    # Fresh model each mode to avoid BN stat mutation carryover.
    model_eval = load_model_b4c64_current_best(
        args.checkpoint, device, args.board_size, args.win_length, args.channels, args.blocks
    )
    model_eval.eval()
    mode_module_rows["eval"] = module_mode_rows(model_eval)
    mode_outputs["eval"] = eval_samples(model_eval, hard_samples, tensors, "eval", args)

    model_train = load_model_b4c64_current_best(
        args.checkpoint, device, args.board_size, args.win_length, args.channels, args.blocks
    )
    model_train.train()
    mode_module_rows["train"] = module_mode_rows(model_train)
    mode_outputs["train"] = eval_samples(model_train, hard_samples, tensors, "train", args)

    model_policy = load_model_b4c64_current_best(
        args.checkpoint, device, args.board_size, args.win_length, args.channels, args.blocks
    )
    set_policy_head_training_mode(model_policy)
    mode_module_rows["policy_head_training_mode"] = module_mode_rows(model_policy)
    mode_outputs["policy_head_training_mode"] = eval_samples(
        model_policy, hard_samples, tensors, "policy_head_training_mode", args
    )

    all_rows = []
    for rows in mode_outputs.values():
        all_rows.extend(rows)

    with (args.out_dir / "bn_mode_outputs.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(all_rows)

    module_rows = []
    for mode, rows in mode_module_rows.items():
        for r in rows:
            rr = dict(r)
            rr["mode"] = mode
            module_rows.append(rr)
    with (args.out_dir / "bn_mode_modules.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["mode", "name", "class", "training"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(module_rows)

    compare_rows = []
    eval_rows = mode_outputs["eval"]
    for mode in ["train", "policy_head_training_mode"]:
        for e, r in zip(eval_rows, mode_outputs[mode]):
            compare_rows.append({
                "case_id": e["case_id"],
                "hard_guard_role": e["hard_guard_role"],
                "compare": f"{mode}_minus_eval",
                "rank_eval": e["rank"],
                "rank_mode": r["rank"],
                "rank_delta": r["rank"] - e["rank"],
                "rank_gt50_eval": e["rank_gt50"],
                "rank_gt50_mode": r["rank_gt50"],
                "target_prob_eval": e["target_prob"],
                "target_prob_mode": r["target_prob"],
                "target_prob_delta": r["target_prob"] - e["target_prob"],
                "target_logit_eval": e["target_logit"],
                "target_logit_mode": r["target_logit"],
                "target_logit_delta": r["target_logit"] - e["target_logit"],
                "worst_gap_eval": e["worst_gap"],
                "worst_gap_mode": r["worst_gap"],
                "worst_gap_delta": None if e["worst_gap"] is None or r["worst_gap"] is None else r["worst_gap"] - e["worst_gap"],
            })

    with (args.out_dir / "bn_mode_compare.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(compare_rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(compare_rows)

    summary = {
        "scope": "BN/train-eval mode audit only; no checkpoint save; no C export; no public benchmark; no promotion",
        "dataset": str(args.dataset),
        "checkpoint": str(args.checkpoint),
        "hard_guard_rows": len(hard_samples),
        "max_abs_train_minus_eval_target_prob_delta": max_abs_delta(
            mode_outputs["eval"], mode_outputs["train"], "target_prob"
        ),
        "max_abs_policy_head_training_minus_eval_target_prob_delta": max_abs_delta(
            mode_outputs["eval"], mode_outputs["policy_head_training_mode"], "target_prob"
        ),
        "any_train_rank_differs_from_eval": any(r["rank_delta"] != 0 for r in compare_rows if r["compare"] == "train_minus_eval"),
        "any_policy_head_training_rank_differs_from_eval": any(
            r["rank_delta"] != 0 for r in compare_rows if r["compare"] == "policy_head_training_mode_minus_eval"
        ),
        "eval_rows": mode_outputs["eval"],
        "train_rows": mode_outputs["train"],
        "policy_head_training_mode_rows": mode_outputs["policy_head_training_mode"],
        "compare_rows": compare_rows,
        "checkpoint_like_outputs": sorted(
            str(p) for p in args.out_dir.glob("*") if p.suffix in {".pt", ".pth", ".bin"}
        ),
    }

    (args.out_dir / "bn_mode_semantics_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n"
    )

    lines = []
    lines.append("# b4c64 hard guard BN / mode semantics audit")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append("- Audit only.")
    lines.append("- No checkpoint save, C export, public benchmark, promotion, or current-best overwrite was performed.")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    for k in [
        "max_abs_train_minus_eval_target_prob_delta",
        "max_abs_policy_head_training_minus_eval_target_prob_delta",
        "any_train_rank_differs_from_eval",
        "any_policy_head_training_rank_differs_from_eval",
    ]:
        lines.append(f"- `{k}`: `{summary[k]}`")
    lines.append("")
    lines.append("## Mode compare")
    lines.append("")
    lines.append("| case_id | compare | rank eval→mode | target prob eval→mode | target logit delta | worst gap delta |")
    lines.append("|---|---|---:|---:|---:|---:|")
    for r in compare_rows:
        lines.append(
            f"| `{r['case_id']}` | `{r['compare']}` | "
            f"{r['rank_eval']}→{r['rank_mode']} | "
            f"{r['target_prob_eval']}→{r['target_prob_mode']} | "
            f"{r['target_logit_delta']} | {r['worst_gap_delta']} |"
        )
    lines.append("")
    lines.append("## Module mode rows")
    lines.append("")
    lines.append("| mode | module | class | training |")
    lines.append("|---|---|---|---:|")
    for r in module_rows:
        if "BatchNorm" in r["class"] or r["name"].startswith("policy"):
            lines.append(f"| `{r['mode']}` | `{r['name']}` | `{r['class']}` | `{r['training']}` |")
    lines.append("")
    lines.append("## Decision")
    lines.append("")
    if summary["any_policy_head_training_rank_differs_from_eval"] or summary["any_train_rank_differs_from_eval"]:
        lines.append("- Output semantics differ across eval/train modes for hard guard rows.")
        lines.append("- Next patch should keep non-policy modules in eval mode during policy-head-only optimization and diagnostics.")
    else:
        lines.append("- Eval/train mode does not explain the hard guard regression; inspect optimizer application and row-group mismatch next.")
    lines.append("")
    lines.append("## Outputs")
    lines.append("")
    for p in sorted(args.out_dir.glob("*")):
        if p.is_file():
            lines.append(f"- `{p}`")
    lines.append("")
    (args.out_dir / "bn_mode_semantics_report.md").write_text("\n".join(lines))

    print(json.dumps({
        "any_train_rank_differs_from_eval": summary["any_train_rank_differs_from_eval"],
        "any_policy_head_training_rank_differs_from_eval": summary["any_policy_head_training_rank_differs_from_eval"],
        "max_abs_train_minus_eval_target_prob_delta": summary["max_abs_train_minus_eval_target_prob_delta"],
        "max_abs_policy_head_training_minus_eval_target_prob_delta": summary["max_abs_policy_head_training_minus_eval_target_prob_delta"],
    }, indent=2, sort_keys=True))
    print("wrote", args.out_dir)


if __name__ == "__main__":
    main()
