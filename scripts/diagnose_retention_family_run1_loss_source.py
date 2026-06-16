#!/usr/bin/env python3
"""
Forward-level loss source diagnosis for retention-family wrapper run1.

Read-only diagnostic:
- no training loop
- no optimizer.step
- no checkpoint save
- no C export
- no benchmark
- no promotion
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
import sys
from collections import Counter
from dataclasses import fields, is_dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import torch
import torch.nn.functional as F


DEFAULT_TRAIN_DATASET = Path("analysis/integration_eval/retention_family_wrapper_run1/train_plain_dataset.json")
DEFAULT_TRAIN_SCRIPT = Path("scripts/train_teacher_divergence_policy_mixed_ce_anchor_probe.py")
DEFAULT_BASE_CKPT = Path("checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt")
DEFAULT_CANDIDATE_CKPT = Path("checkpoints/failed_retention_family_probe/retention_family_wrapper_run1_candidate.pt")

DEFAULT_OUT_CSV = Path("analysis/integration_eval/retention_family_run1_loss_source_diagnosis.csv")
DEFAULT_OUT_JSON = Path("analysis/integration_eval/retention_family_run1_loss_source_diagnosis.json")
DEFAULT_OUT_MD = Path("analysis/integration_eval/retention_family_run1_loss_source_diagnosis.md")


def clean(v: Any) -> str:
    if v is None:
        return ""
    return str(v).strip()


def is_finite_float(x: Any) -> bool:
    try:
        return math.isfinite(float(x))
    except Exception:
        return False


def import_train_module(path: Path) -> Any:
    module_name = "retention_family_train_script_under_diagnosis"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def object_items(obj: Any) -> List[Tuple[str, Any]]:
    if is_dataclass(obj):
        return [(f.name, getattr(obj, f.name)) for f in fields(obj)]
    if hasattr(obj, "__dict__"):
        return list(vars(obj).items())
    return []


def shape_str(x: Any) -> str:
    if torch.is_tensor(x):
        return "x".join(str(i) for i in tuple(x.shape))
    return ""


def tensor_stats(x: torch.Tensor) -> Dict[str, Any]:
    x_detached = x.detach()
    finite = torch.isfinite(x_detached)
    total = x_detached.numel()
    finite_count = int(finite.sum().item())
    nonfinite_count = total - finite_count

    out: Dict[str, Any] = {
        "shape": shape_str(x_detached),
        "dtype": str(x_detached.dtype),
        "total": total,
        "finite_count": finite_count,
        "nonfinite_count": nonfinite_count,
        "all_finite": nonfinite_count == 0,
    }

    if finite_count:
        finite_vals = x_detached[finite].float()
        out["min"] = float(finite_vals.min().item())
        out["max"] = float(finite_vals.max().item())
        out["mean"] = float(finite_vals.mean().item())
    else:
        out["min"] = ""
        out["max"] = ""
        out["mean"] = ""

    return out


def model_parameter_stats(model: torch.nn.Module) -> Dict[str, Any]:
    total = 0
    nonfinite = 0
    bad_names: List[str] = []
    max_abs = 0.0

    for name, p in model.named_parameters():
        d = p.detach()
        total += d.numel()
        finite = torch.isfinite(d)
        bad = int((~finite).sum().item())
        if bad:
            nonfinite += bad
            bad_names.append(f"{name}:{bad}")
        if finite.any():
            max_abs = max(max_abs, float(d[finite].abs().max().item()))

    return {
        "parameter_count": total,
        "nonfinite_parameter_count": nonfinite,
        "all_parameters_finite": nonfinite == 0,
        "bad_parameter_names": bad_names,
        "max_abs_finite_parameter": max_abs,
    }


def find_feature_tensor(row: Any, board_size: int) -> Tuple[Optional[str], Optional[torch.Tensor], List[str]]:
    candidates: List[str] = []
    preferred = {
        "features", "feature", "input", "x", "planes", "state",
        "encoded", "tensor", "board_tensor", "input_tensor",
    }

    items = object_items(row)

    # First prefer name hits.
    for name, val in items:
        if not torch.is_tensor(val):
            continue
        candidates.append(f"{name}:{shape_str(val)}")
        low = name.lower()
        if low in preferred or any(tok in low for tok in ("feature", "plane", "input", "state")):
            if val.dim() == 3 and tuple(val.shape[-2:]) == (board_size, board_size):
                return name, val.float(), candidates

    # Fallback: any 3D board-shaped tensor.
    for name, val in items:
        if torch.is_tensor(val) and val.dim() == 3 and tuple(val.shape[-2:]) == (board_size, board_size):
            return name, val.float(), candidates

    return None, None, candidates


def find_mask_tensor(row: Any, board_size: int) -> Tuple[Optional[str], Optional[torch.Tensor], List[str]]:
    candidates: List[str] = []
    n = board_size * board_size

    items = object_items(row)

    # Prefer legal/mask names.
    for name, val in items:
        if not torch.is_tensor(val):
            continue
        candidates.append(f"{name}:{shape_str(val)}")
        low = name.lower()
        if ("mask" in low or "legal" in low) and val.numel() == n:
            return name, val.float().reshape(-1), candidates

    # Fallback: 1D board-action tensor with 0/1-ish values.
    for name, val in items:
        if torch.is_tensor(val) and val.numel() == n:
            flat = val.detach().float().reshape(-1)
            if torch.isfinite(flat).all() and flat.min() >= 0 and flat.max() <= 1:
                return name, flat, candidates

    return None, None, candidates


def extract_target_action(row: Any) -> Tuple[Optional[int], str]:
    for name, val in object_items(row):
        if name == "target_action":
            try:
                return int(val), "target_action"
            except Exception:
                return None, f"bad_target_action:{val}"
    return None, "missing_target_action"


def extract_weight(row: Any) -> Tuple[float, str]:
    for name, val in object_items(row):
        if name == "weight":
            try:
                x = float(val)
                return x, "weight"
            except Exception:
                return float("nan"), f"bad_weight:{val}"
    return 1.0, "default_1"


def extract_row_meta(row: Any) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for name, val in object_items(row):
        if name in {
            "row_id", "split", "label_type", "side_to_move",
            "target_xy", "target_action", "weight",
        }:
            out[name] = clean(val)
    return out


def get_policy_logits(model_out: Any) -> torch.Tensor:
    if isinstance(model_out, dict):
        for key in ("policy_logits", "logits", "policy", "policy_head"):
            if key in model_out:
                return model_out[key]
        raise RuntimeError(f"model output dict has no policy logits key: {list(model_out)}")

    if isinstance(model_out, (tuple, list)):
        return model_out[0]

    if torch.is_tensor(model_out):
        return model_out

    raise RuntimeError(f"unsupported model output type: {type(model_out)}")


def masked_log_softmax(logits: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
    return F.log_softmax(logits.masked_fill(mask <= 0, -1e9), dim=-1)


def load_prepared_rows(module: Any, dataset: Path, board_size: int) -> Tuple[Any, List[Any]]:
    if not hasattr(module, "prepare_rows"):
        raise RuntimeError("training module has no prepare_rows")
    return module.prepare_rows(dataset, board_size, strict_splits=False)


def make_load_args(board_size: int, win_length: int, channels: int, blocks: int) -> SimpleNamespace:
    return SimpleNamespace(
        board_size=board_size,
        win_length=win_length,
        channels=channels,
        blocks=blocks,
        device="cpu",
    )


def load_model(module: Any, checkpoint: Path, board_size: int, win_length: int, channels: int, blocks: int) -> torch.nn.Module:
    args = make_load_args(board_size, win_length, channels, blocks)

    if not hasattr(module, "load_model"):
        raise RuntimeError("training module has no load_model")

    model = module.load_model(args, checkpoint, torch.device("cpu"))
    model.eval()
    return model


@torch.no_grad()
def diagnose_checkpoint(
    label: str,
    model: torch.nn.Module,
    reference_model: Optional[torch.nn.Module],
    prepared_rows: List[Any],
    board_size: int,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    param_stats = model_parameter_stats(model)
    ref_param_stats = model_parameter_stats(reference_model) if reference_model is not None else {}

    row_reports: List[Dict[str, Any]] = []

    for i, row in enumerate(prepared_rows, 1):
        meta = extract_row_meta(row)

        feature_name, feature, feature_candidates = find_feature_tensor(row, board_size)
        mask_name, mask, mask_candidates = find_mask_tensor(row, board_size)
        target_action, target_source = extract_target_action(row)
        weight, weight_source = extract_weight(row)

        report: Dict[str, Any] = {
            "checkpoint_label": label,
            "row_index": i,
            **meta,
            "feature_name": feature_name or "",
            "feature_candidates": ";".join(feature_candidates),
            "mask_name": mask_name or "",
            "mask_candidates": ";".join(mask_candidates),
            "target_action_int": "" if target_action is None else target_action,
            "target_source": target_source,
            "weight_float": weight,
            "weight_source": weight_source,
            "can_forward": False,
            "diagnostic_errors": "",
        }

        errors: List[str] = []
        if feature is None:
            errors.append("missing_feature_tensor")
        if mask is None:
            errors.append("missing_mask_tensor")
        if target_action is None:
            errors.append("missing_target_action")
        if not math.isfinite(weight):
            errors.append("nonfinite_weight")

        if feature is not None:
            report.update({f"feature_{k}": v for k, v in tensor_stats(feature).items()})
        if mask is not None:
            legal_count = int((mask > 0).sum().item())
            report.update({f"mask_{k}": v for k, v in tensor_stats(mask).items()})
            report["legal_count"] = legal_count
            if target_action is not None and 0 <= target_action < mask.numel():
                report["target_legal"] = bool(mask[target_action].item() > 0)
            else:
                report["target_legal"] = False
                errors.append("target_action_out_of_mask_bounds")

        if errors:
            report["diagnostic_errors"] = ";".join(errors)
            row_reports.append(report)
            continue

        assert feature is not None
        assert mask is not None
        assert target_action is not None

        x = feature.unsqueeze(0)
        m = mask.reshape(1, -1)

        try:
            logits = get_policy_logits(model(x))
            if logits.dim() > 2:
                logits = logits.reshape(logits.shape[0], -1)
            log_probs = masked_log_softmax(logits, m)
            probs = log_probs.exp()

            target_log_prob = log_probs[0, target_action]
            target_prob = probs[0, target_action]
            ce = -target_log_prob * weight

            report["can_forward"] = True
            report.update({f"logits_{k}": v for k, v in tensor_stats(logits).items()})
            report.update({f"log_probs_{k}": v for k, v in tensor_stats(log_probs).items()})
            report["target_log_prob"] = float(target_log_prob.item())
            report["target_prob"] = float(target_prob.item())
            report["weighted_ce"] = float(ce.item())
            report["target_log_prob_finite"] = bool(torch.isfinite(target_log_prob).item())
            report["target_prob_finite"] = bool(torch.isfinite(target_prob).item())
            report["weighted_ce_finite"] = bool(torch.isfinite(ce).item())

            if reference_model is not None:
                ref_logits = get_policy_logits(reference_model(x))
                if ref_logits.dim() > 2:
                    ref_logits = ref_logits.reshape(ref_logits.shape[0], -1)
                ref_log_probs = masked_log_softmax(ref_logits, m)
                ref_probs = ref_log_probs.exp()
                kl = torch.sum(ref_probs * (ref_log_probs - log_probs), dim=-1)
                report["anchor_kl"] = float(kl.item())
                report["anchor_kl_finite"] = bool(torch.isfinite(kl).all().item())
                report.update({f"ref_logits_{k}": v for k, v in tensor_stats(ref_logits).items()})
            else:
                report["anchor_kl"] = ""
                report["anchor_kl_finite"] = ""

        except Exception as e:
            report["diagnostic_errors"] = "forward_error:" + repr(e)

        row_reports.append(report)

    summary = {
        "checkpoint_label": label,
        "parameter_stats": param_stats,
        "reference_parameter_stats": ref_param_stats,
        "row_count": len(prepared_rows),
        "forwardable_rows": sum(1 for r in row_reports if r.get("can_forward")),
        "row_error_counts": dict(Counter(
            err
            for r in row_reports
            for err in clean(r.get("diagnostic_errors")).split(";")
            if err
        )),
        "nonfinite_logit_rows": sum(1 for r in row_reports if r.get("logits_nonfinite_count", 0)),
        "nonfinite_logprob_rows": sum(1 for r in row_reports if r.get("log_probs_nonfinite_count", 0)),
        "nonfinite_ce_rows": sum(1 for r in row_reports if r.get("weighted_ce_finite") is False),
        "nonfinite_kl_rows": sum(1 for r in row_reports if r.get("anchor_kl_finite") is False),
    }

    return row_reports, summary


def write_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    preferred = [
        "checkpoint_label", "row_index", "row_id", "split", "label_type",
        "side_to_move", "target_xy", "target_action", "target_action_int",
        "feature_name", "feature_shape", "feature_nonfinite_count",
        "mask_name", "mask_shape", "mask_nonfinite_count", "legal_count",
        "target_legal", "weight_float", "can_forward", "logits_shape",
        "logits_nonfinite_count", "log_probs_nonfinite_count",
        "target_log_prob", "target_prob", "weighted_ce", "anchor_kl",
        "target_log_prob_finite", "target_prob_finite",
        "weighted_ce_finite", "anchor_kl_finite", "diagnostic_errors",
    ]

    all_fields: List[str] = []
    for key in preferred:
        if key not in all_fields:
            all_fields.append(key)
    for r in rows:
        for k in r:
            if k not in all_fields:
                all_fields.append(k)

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=all_fields, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in all_fields})


def md_table(headers: Sequence[str], rows: Sequence[Sequence[Any]]) -> str:
    out = []
    out.append("| " + " | ".join(headers) + " |")
    out.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for r in rows:
        cells = [str(x).replace("\n", " ").replace("|", "\\|") for x in r]
        out.append("| " + " | ".join(cells) + " |")
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--train-dataset", type=Path, default=DEFAULT_TRAIN_DATASET)
    ap.add_argument("--train-script", type=Path, default=DEFAULT_TRAIN_SCRIPT)
    ap.add_argument("--base-checkpoint", type=Path, default=DEFAULT_BASE_CKPT)
    ap.add_argument("--candidate-checkpoint", type=Path, default=DEFAULT_CANDIDATE_CKPT)
    ap.add_argument("--board-size", type=int, default=15)
    ap.add_argument("--win-length", type=int, default=5)
    ap.add_argument("--channels", type=int, default=64)
    ap.add_argument("--blocks", type=int, default=4)
    ap.add_argument("--out-csv", type=Path, default=DEFAULT_OUT_CSV)
    ap.add_argument("--out-json", type=Path, default=DEFAULT_OUT_JSON)
    ap.add_argument("--out-md", type=Path, default=DEFAULT_OUT_MD)
    args = ap.parse_args()

    module = import_train_module(args.train_script)

    dataset_meta, prepared_rows = load_prepared_rows(module, args.train_dataset, args.board_size)

    base_model = load_model(module, args.base_checkpoint, args.board_size, args.win_length, args.channels, args.blocks)

    all_rows: List[Dict[str, Any]] = []
    checkpoint_summaries: List[Dict[str, Any]] = []

    base_rows, base_summary = diagnose_checkpoint(
        "base",
        base_model,
        reference_model=None,
        prepared_rows=prepared_rows,
        board_size=args.board_size,
    )
    all_rows.extend(base_rows)
    checkpoint_summaries.append(base_summary)

    candidate_exists = args.candidate_checkpoint.exists()
    if candidate_exists:
        candidate_model = load_model(module, args.candidate_checkpoint, args.board_size, args.win_length, args.channels, args.blocks)
        candidate_rows, candidate_summary = diagnose_checkpoint(
            "candidate_quarantined",
            candidate_model,
            reference_model=base_model,
            prepared_rows=prepared_rows,
            board_size=args.board_size,
        )
        all_rows.extend(candidate_rows)
        checkpoint_summaries.append(candidate_summary)

    likely_causes: List[str] = []

    candidate_summary = next((s for s in checkpoint_summaries if s["checkpoint_label"] == "candidate_quarantined"), None)
    if candidate_summary and not candidate_summary["parameter_stats"]["all_parameters_finite"]:
        likely_causes.append("candidate_checkpoint_contains_nonfinite_parameters")
    if candidate_summary and candidate_summary["nonfinite_logit_rows"]:
        likely_causes.append("candidate_forward_produces_nonfinite_logits")
    if candidate_summary and candidate_summary["nonfinite_ce_rows"]:
        likely_causes.append("candidate_target_ce_is_nonfinite")
    if candidate_summary and candidate_summary["nonfinite_kl_rows"]:
        likely_causes.append("candidate_anchor_kl_is_nonfinite")
    if not likely_causes:
        likely_causes.append("forward_level_base_and_candidate_checks_did_not_find_nonfinite_values")

    payload = {
        "scope": "forward-level loss source diagnosis only; no training/optimizer/checkpoint/C export/benchmark/promotion",
        "inputs": {
            "train_dataset": str(args.train_dataset),
            "train_script": str(args.train_script),
            "base_checkpoint": str(args.base_checkpoint),
            "candidate_checkpoint": str(args.candidate_checkpoint),
            "candidate_checkpoint_exists": candidate_exists,
            "board_size": args.board_size,
            "win_length": args.win_length,
            "channels": args.channels,
            "blocks": args.blocks,
        },
        "dataset_meta": dataset_meta,
        "prepared_row_count": len(prepared_rows),
        "prepared_row_fields": [
            [name for name, _ in object_items(row)]
            for row in prepared_rows[:3]
        ],
        "checkpoint_summaries": checkpoint_summaries,
        "likely_causes": likely_causes,
        "rows": all_rows,
    }

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_csv(args.out_csv, all_rows)

    md: List[str] = []
    md.append("# Retention family run1 loss source diagnosis")
    md.append("")
    md.append("Scope: forward-level diagnosis only. No training loop, optimizer step, checkpoint save, C export, benchmark, or promotion was run.")
    md.append("")
    md.append("## Inputs")
    md.append("")
    md.append(f"- train_dataset: `{args.train_dataset}`")
    md.append(f"- train_script: `{args.train_script}`")
    md.append(f"- base_checkpoint: `{args.base_checkpoint}`")
    md.append(f"- candidate_checkpoint: `{args.candidate_checkpoint}`")
    md.append(f"- candidate_checkpoint_exists: `{candidate_exists}`")
    md.append(f"- model config: board_size={args.board_size}, channels={args.channels}, blocks={args.blocks}")
    md.append("")
    md.append("## Checkpoint summaries")
    md.append("")
    md.append(md_table(
        [
            "checkpoint",
            "params finite",
            "bad params",
            "forwardable rows",
            "nonfinite logits rows",
            "nonfinite CE rows",
            "nonfinite KL rows",
            "row errors",
        ],
        [
            [
                s["checkpoint_label"],
                s["parameter_stats"]["all_parameters_finite"],
                s["parameter_stats"]["nonfinite_parameter_count"],
                s["forwardable_rows"],
                s["nonfinite_logit_rows"],
                s["nonfinite_ce_rows"],
                s["nonfinite_kl_rows"],
                s["row_error_counts"],
            ]
            for s in checkpoint_summaries
        ],
    ))
    md.append("")
    md.append("## Row-level loss checks")
    md.append("")
    md.append(md_table(
        [
            "checkpoint",
            "row",
            "label_type",
            "target",
            "target legal",
            "logits bad",
            "logprob bad",
            "target_prob",
            "weighted_ce",
            "anchor_kl",
            "errors",
        ],
        [
            [
                r.get("checkpoint_label", ""),
                r.get("row_index", ""),
                r.get("label_type", ""),
                r.get("target_xy", ""),
                r.get("target_legal", ""),
                r.get("logits_nonfinite_count", ""),
                r.get("log_probs_nonfinite_count", ""),
                r.get("target_prob", ""),
                r.get("weighted_ce", ""),
                r.get("anchor_kl", ""),
                r.get("diagnostic_errors", ""),
            ]
            for r in all_rows
        ],
    ))
    md.append("")
    md.append("## Likely causes")
    md.append("")
    for c in likely_causes:
        md.append(f"- `{c}`")
    md.append("")
    md.append("## Interpretation")
    md.append("")
    md.append("If the base checkpoint has finite parameters and finite per-row CE, but the quarantined candidate has non-finite parameters/logits/CE/KL, then the NaN was introduced during the tiny training step rather than by invalid adapter rows.")
    md.append("")
    md.append("If both base and candidate forward checks are finite, then the NaN likely comes from the legacy trainer's aggregation/reporting path rather than the raw forward CE/KL calculations.")
    md.append("")
    md.append("## Explicit non-actions")
    md.append("")
    md.append("- No training loop was run.")
    md.append("- No optimizer step was run.")
    md.append("- No checkpoint was saved.")
    md.append("- No C weights were exported.")
    md.append("- No benchmark was run.")
    md.append("- No promotion decision was made.")
    md.append("")

    args.out_md.write_text("\n".join(md).rstrip() + "\n", encoding="utf-8")

    print("wrote", args.out_csv)
    print("wrote", args.out_json)
    print("wrote", args.out_md)
    print("prepared_row_count", len(prepared_rows))
    print("candidate_checkpoint_exists", candidate_exists)
    print("checkpoint_summaries")
    for s in checkpoint_summaries:
        print(s)
    print("likely_causes", likely_causes)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
