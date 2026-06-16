#!/usr/bin/env python3
"""
Audit the legacy mixed-CE trainer loss path for retention-family wrapper run1.

Read-only audit:
- no training
- no optimizer step
- no checkpoint save
- no C export
- no benchmark
- no promotion
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from pathlib import Path
from typing import Any, Dict, List


DEFAULT_DATASET = Path("analysis/integration_eval/retention_family_wrapper_run1/train_plain_dataset.json")
DEFAULT_TRAIN_SCRIPT = Path("scripts/train_teacher_divergence_policy_mixed_ce_anchor_probe.py")
DEFAULT_TRAIN_STDOUT = Path("eval_logs/integration_eval/retention_family_wrapper_run1/train.stdout.log")
DEFAULT_OUT_JSON = Path("analysis/integration_eval/retention_family_run1_loss_path_audit.json")
DEFAULT_OUT_MD = Path("analysis/integration_eval/retention_family_run1_loss_path_audit.md")
DEFAULT_OUT_CSV = Path("analysis/integration_eval/retention_family_run1_loss_path_audit_rows.csv")


def clean(v: Any) -> str:
    if v is None:
        return ""
    return str(v).strip()


def finite_float(v: Any) -> tuple[str, str]:
    if v is None:
        return "", "missing"
    try:
        x = float(v)
    except Exception as e:
        return "", f"unparseable:{e}"
    if not math.isfinite(x):
        return repr(x), "nonfinite"
    return repr(x), "finite"


def read_rows(path: Path) -> list[dict[str, Any]]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(obj, dict) and isinstance(obj.get("rows"), list):
        return obj["rows"]
    raise SystemExit(f"ERROR: expected object with rows in {path}")


def extract_log_facts(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"exists": False}

    text = path.read_text(encoding="utf-8", errors="replace")
    facts: dict[str, Any] = {"exists": True}

    patterns = {
        "ce_training_rows": r"ce_training_rows=([^\n]+)",
        "anchor_kl_rows": r"anchor_kl_rows=([^\n]+)",
        "mixed_ce_rows": r"mixed_ce_rows=([^\n]+)",
        "epoch_line": r"epoch\s+001/1\s+([^\n]+)",
        "train_scope": r"train_scope=([^\n]+)",
        "trainable_parameters": r"trainable_parameters=([^\n]+)",
    }

    for k, pat in patterns.items():
        m = re.search(pat, text)
        facts[k] = m.group(1).strip() if m else ""

    facts["contains_loss_nan"] = "loss=nan" in text.lower()
    facts["contains_main_ce_nan"] = "main_ce=nan" in text.lower()
    facts["contains_anchor_kl_nan"] = "anchor_kl=nan" in text.lower()
    facts["contains_checkpoint_written"] = "wrote checkpoint:" in text.lower()
    return facts


def extract_script_hits(path: Path) -> list[dict[str, Any]]:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()

    terms = [
        "ce_indices",
        "anchor_indices",
        "mixed_ce",
        "anchor_kl",
        "main_ce",
        "loss",
        "backward",
        "step",
        "nan",
        "no_strict_splits",
        "anchor_kl_splits",
        "mixed_ce_splits",
    ]

    hits = []
    for i, line in enumerate(lines, 1):
        low = line.lower()
        if any(t.lower() in low for t in terms):
            hits.append({"line": i, "text": line.rstrip()})

    return hits


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    ap.add_argument("--train-script", type=Path, default=DEFAULT_TRAIN_SCRIPT)
    ap.add_argument("--train-stdout", type=Path, default=DEFAULT_TRAIN_STDOUT)
    ap.add_argument("--out-json", type=Path, default=DEFAULT_OUT_JSON)
    ap.add_argument("--out-md", type=Path, default=DEFAULT_OUT_MD)
    ap.add_argument("--out-csv", type=Path, default=DEFAULT_OUT_CSV)
    args = ap.parse_args()

    rows = read_rows(args.dataset)
    row_reports: list[dict[str, Any]] = []

    for i, r in enumerate(rows, 1):
        meta = r.get("retention_family_consumer_adapter", {})
        if not isinstance(meta, dict):
            meta = {}

        sw_value, sw_status = finite_float(r.get("suggested_weight"))
        w_value, w_status = finite_float(r.get("weight"))
        target_prob_value, target_prob_status = finite_float(meta.get("target_prob"))

        row_reports.append({
            "row_index": i,
            "id": clean(r.get("id")),
            "split": clean(r.get("split")),
            "role": clean(r.get("role")),
            "label_type": clean(r.get("label_type")),
            "policy_target": clean(r.get("policy_target") or meta.get("policy_target")),
            "suggested_weight_raw": clean(r.get("suggested_weight")),
            "suggested_weight_float": sw_value,
            "suggested_weight_status": sw_status,
            "weight_raw": clean(r.get("weight")),
            "weight_float": w_value,
            "weight_status": w_status,
            "adapter_target_prob_raw": clean(meta.get("target_prob")),
            "adapter_target_prob_float": target_prob_value,
            "adapter_target_prob_status": target_prob_status,
            "train_use_policy": clean(meta.get("train_use_policy")),
            "gate_scope": clean(meta.get("gate_scope")),
            "risk_flags": clean(meta.get("risk_flags")),
        })

    log_facts = extract_log_facts(args.train_stdout)
    script_hits = extract_script_hits(args.train_script)

    finding_list: list[str] = []

    if log_facts.get("mixed_ce_rows") == "0":
        finding_list.append("mixed_ce_rows_zero")
    if log_facts.get("contains_loss_nan"):
        finding_list.append("training_log_loss_nan")
    if log_facts.get("contains_main_ce_nan"):
        finding_list.append("training_log_main_ce_nan")
    if log_facts.get("contains_anchor_kl_nan"):
        finding_list.append("training_log_anchor_kl_nan")
    if log_facts.get("contains_checkpoint_written"):
        finding_list.append("checkpoint_written_despite_nan_loss")
    if any(r["suggested_weight_status"] == "nonfinite" for r in row_reports):
        finding_list.append("nonfinite_suggested_weight")
    if any(r["weight_status"] == "nonfinite" for r in row_reports):
        finding_list.append("nonfinite_weight")

    likely_causes: list[str] = []
    if "nonfinite_suggested_weight" in finding_list or "nonfinite_weight" in finding_list:
        likely_causes.append("row_weight_nonfinite")
    if "mixed_ce_rows_zero" in finding_list and "training_log_main_ce_nan" in finding_list:
        likely_causes.append("legacy_trainer_allows_empty_main_ce_path")
    if "training_log_loss_nan" in finding_list and "checkpoint_written_despite_nan_loss" in finding_list:
        likely_causes.append("legacy_trainer_does_not_block_nonfinite_loss_before_optimizer_or_checkpoint")
    if not likely_causes:
        likely_causes.append("requires_manual_loss_loop_inspection")

    payload = {
        "scope": "loss path audit only; no training/checkpoint/C export/benchmark/promotion",
        "inputs": {
            "dataset": str(args.dataset),
            "train_script": str(args.train_script),
            "train_stdout": str(args.train_stdout),
        },
        "row_count": len(rows),
        "row_reports": row_reports,
        "train_log_facts": log_facts,
        "script_hits": script_hits,
        "findings": finding_list,
        "likely_causes": likely_causes,
    }

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    with args.out_csv.open("w", encoding="utf-8", newline="") as f:
        fieldnames = [
            "row_index",
            "id",
            "split",
            "role",
            "label_type",
            "policy_target",
            "suggested_weight_raw",
            "suggested_weight_float",
            "suggested_weight_status",
            "weight_raw",
            "weight_float",
            "weight_status",
            "adapter_target_prob_raw",
            "adapter_target_prob_float",
            "adapter_target_prob_status",
            "train_use_policy",
            "gate_scope",
            "risk_flags",
        ]
        w = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        w.writeheader()
        for r in row_reports:
            w.writerow({k: r.get(k, "") for k in fieldnames})

    def table(headers: list[str], body: list[list[Any]]) -> str:
        out = []
        out.append("| " + " | ".join(headers) + " |")
        out.append("| " + " | ".join(["---"] * len(headers)) + " |")
        for row in body:
            out.append("| " + " | ".join(str(x).replace("|", "\\|") for x in row) + " |")
        return "\n".join(out)

    md: list[str] = []
    md.append("# Retention family run1 loss path audit")
    md.append("")
    md.append("Scope: read-only loss-path audit. No training, optimizer step, checkpoint save, C export, benchmark, or promotion was run.")
    md.append("")
    md.append("## Train log facts")
    md.append("")
    for k, v in log_facts.items():
        md.append(f"- {k}: `{v}`")
    md.append("")
    md.append("## Row weight/probability audit")
    md.append("")
    md.append(table(
        [
            "idx", "split", "label_type", "target",
            "suggested_weight", "suggested_weight_status",
            "weight", "weight_status",
            "adapter_target_prob", "adapter_target_prob_status",
        ],
        [
            [
                r["row_index"],
                r["split"],
                r["label_type"],
                r["policy_target"],
                r["suggested_weight_raw"],
                r["suggested_weight_status"],
                r["weight_raw"],
                r["weight_status"],
                r["adapter_target_prob_raw"],
                r["adapter_target_prob_status"],
            ]
            for r in row_reports
        ],
    ))
    md.append("")
    md.append("## Findings")
    md.append("")
    for item in finding_list:
        md.append(f"- `{item}`")
    md.append("")
    md.append("## Likely causes")
    md.append("")
    for item in likely_causes:
        md.append(f"- `{item}`")
    md.append("")
    md.append("## Relevant script lines")
    md.append("")
    md.append(table(
        ["line", "text"],
        [[h["line"], h["text"]] for h in script_hits[:120]],
    ))
    md.append("")
    md.append("## Interpretation")
    md.append("")
    md.append("The run1 trainer should not write a checkpoint when the training loss is non-finite. If the main CE path is empty and yields NaN, the next code fix should add explicit finite-loss guards and prevent optimizer/checkpoint side effects.")
    md.append("")
    md.append("## Explicit non-actions")
    md.append("")
    md.append("- No training was run.")
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
    print("findings", finding_list)
    print("likely_causes", likely_causes)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
