#!/usr/bin/env python3
"""
Apply positive train weights to retention-family adapter train rows.

This is a data-contract adapter step:
- no training
- no checkpoint
- no C export
- no benchmark
- no promotion

Why:
The wrapper run1 adapter train rows were correctly moved to train_candidate,
but retained suggested_weight=0.0 from their historical heldout/eval role.
The legacy trainer reads suggested_weight as row.weight, so zero total train
weight produces NaN loss. This script materializes a weighted train dataset
for future guarded probes.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Tuple


DEFAULT_IN = Path("analysis/integration_eval/retention_family_training_consumer_adapter_train_dataset.json")
DEFAULT_OUT_JSON = Path("analysis/integration_eval/retention_family_training_consumer_adapter_train_weighted_dataset.json")
DEFAULT_OUT_CSV = Path("analysis/integration_eval/retention_family_training_consumer_adapter_train_weighted_manifest.csv")
DEFAULT_OUT_MD = Path("analysis/integration_eval/retention_family_training_consumer_adapter_train_weighted_report.md")


def clean(v: Any) -> str:
    if v is None:
        return ""
    return str(v).strip()


def parse_float(v: Any) -> Tuple[float | None, str]:
    if v is None or clean(v).lower() in {"", "none", "nan", "null"}:
        return None, "missing"
    try:
        x = float(v)
    except Exception as e:
        return None, f"unparseable:{e}"
    if not math.isfinite(x):
        return x, "nonfinite"
    return x, "finite"


def load_rows(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict) or not isinstance(obj.get("rows"), list):
        raise SystemExit(f"ERROR: expected JSON object with rows: {path}")
    metadata = obj.get("metadata", {})
    if not isinstance(metadata, dict):
        metadata = {}
    return metadata, obj["rows"]


def row_adapter(row: dict[str, Any]) -> dict[str, Any]:
    meta = row.get("retention_family_consumer_adapter")
    if isinstance(meta, dict):
        return meta
    meta = {}
    row["retention_family_consumer_adapter"] = meta
    return meta


def should_apply_weight(row: dict[str, Any]) -> bool:
    split = clean(row.get("split"))
    role = clean(row.get("role"))
    label_type = clean(row.get("label_type"))
    meta = row_adapter(row)
    train_use_policy = clean(meta.get("train_use_policy"))

    if split != "train_candidate":
        return False

    # This branch intentionally targets adapter train rows, especially
    # nonheldout retention anchors reclassified from heldout/eval material.
    if "include_as_nonheldout_retention_anchor_candidate" in train_use_policy:
        return True

    if role == "nonheldout_retention_anchor" or label_type == "nonheldout_retention_anchor":
        return True

    return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-json", type=Path, default=DEFAULT_IN)
    ap.add_argument("--out-json", type=Path, default=DEFAULT_OUT_JSON)
    ap.add_argument("--out-csv", type=Path, default=DEFAULT_OUT_CSV)
    ap.add_argument("--out-md", type=Path, default=DEFAULT_OUT_MD)
    ap.add_argument("--default-train-weight", type=float, default=1.0)
    args = ap.parse_args()

    if not math.isfinite(args.default_train_weight) or args.default_train_weight <= 0:
        raise SystemExit("--default-train-weight must be positive and finite")

    input_metadata, input_rows = load_rows(args.input_json)
    rows = deepcopy(input_rows)

    manifest_rows: list[dict[str, Any]] = []
    changed = 0
    unchanged_positive = 0
    skipped = 0

    for idx, row in enumerate(rows, 1):
        meta = row_adapter(row)

        before_raw = row.get("suggested_weight")
        before_value, before_status = parse_float(before_raw)

        applies = should_apply_weight(row)
        after_value = before_value
        action = "skipped"

        if applies:
            if before_value is None or before_status != "finite" or before_value <= 0:
                row["suggested_weight"] = args.default_train_weight
                after_value = args.default_train_weight
                changed += 1
                action = "set_default_positive_weight"
            else:
                unchanged_positive += 1
                action = "kept_existing_positive_weight"

            meta["adapter_weight_policy"] = "positive_train_weight_required"
            meta["adapter_weight_policy_reason"] = (
                "adapter train rows are consumed by the legacy trainer as CE/KL rows; "
                "zero or non-finite weights would make the loss denominator invalid"
            )
            meta["adapter_original_suggested_weight"] = clean(before_raw)
            meta["adapter_materialized_suggested_weight"] = row["suggested_weight"]
        else:
            skipped += 1

        manifest_rows.append({
            "row_index": idx,
            "id": clean(row.get("id")),
            "family_id": clean(meta.get("family_id")),
            "split": clean(row.get("split")),
            "role": clean(row.get("role")),
            "label_type": clean(row.get("label_type")),
            "policy_target": clean(row.get("policy_target") or meta.get("policy_target")),
            "train_use_policy": clean(meta.get("train_use_policy")),
            "gate_scope": clean(meta.get("gate_scope")),
            "risk_flags": clean(meta.get("risk_flags")),
            "before_suggested_weight": clean(before_raw),
            "before_weight_status": before_status,
            "after_suggested_weight": "" if after_value is None else after_value,
            "action": action,
            "applies": applies,
        })

    split_counts = Counter(clean(r.get("split")) for r in rows)
    label_type_counts = Counter(clean(r.get("label_type")) for r in rows)
    action_counts = Counter(r["action"] for r in manifest_rows)

    output_metadata = dict(input_metadata)
    output_metadata["source"] = str(args.input_json)
    output_metadata["adapter_train_weight_policy"] = {
        "default_train_weight": args.default_train_weight,
        "changed_rows": changed,
        "unchanged_positive_rows": unchanged_positive,
        "skipped_rows": skipped,
        "purpose": "ensure adapter train rows have positive finite suggested_weight before guarded training",
        "non_actions": [
            "no training",
            "no checkpoint",
            "no C export",
            "no benchmark",
            "no promotion",
        ],
    }

    out_payload = {
        "metadata": output_metadata,
        "rows": rows,
    }

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(out_payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    with args.out_csv.open("w", encoding="utf-8", newline="") as f:
        fieldnames = [
            "row_index",
            "id",
            "family_id",
            "split",
            "role",
            "label_type",
            "policy_target",
            "train_use_policy",
            "gate_scope",
            "risk_flags",
            "before_suggested_weight",
            "before_weight_status",
            "after_suggested_weight",
            "action",
            "applies",
        ]
        w = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        w.writeheader()
        for r in manifest_rows:
            w.writerow({k: r.get(k, "") for k in fieldnames})

    def table(headers: list[str], body: list[list[Any]]) -> str:
        out = []
        out.append("| " + " | ".join(headers) + " |")
        out.append("| " + " | ".join(["---"] * len(headers)) + " |")
        for row in body:
            out.append("| " + " | ".join(str(x).replace("|", "\\|") for x in row) + " |")
        return "\n".join(out)

    md: list[str] = []
    md.append("# Retention family adapter train weight policy")
    md.append("")
    md.append("Scope: adapter train-weight materialization only. No training, checkpoint, C export, benchmark, or promotion was run.")
    md.append("")
    md.append("## Summary")
    md.append("")
    md.append(f"- input_json: `{args.input_json}`")
    md.append(f"- out_json: `{args.out_json}`")
    md.append(f"- default_train_weight: `{args.default_train_weight}`")
    md.append(f"- rows: `{len(rows)}`")
    md.append(f"- changed_rows: `{changed}`")
    md.append(f"- unchanged_positive_rows: `{unchanged_positive}`")
    md.append(f"- skipped_rows: `{skipped}`")
    md.append(f"- split_counts: `{dict(sorted(split_counts.items()))}`")
    md.append(f"- label_type_counts: `{dict(sorted(label_type_counts.items()))}`")
    md.append(f"- action_counts: `{dict(sorted(action_counts.items()))}`")
    md.append("")
    md.append("## Row manifest")
    md.append("")
    md.append(table(
        [
            "idx", "family", "target", "split", "label_type",
            "before_weight", "before_status", "after_weight", "action", "risk_flags",
        ],
        [
            [
                r["row_index"],
                r["family_id"],
                r["policy_target"],
                r["split"],
                r["label_type"],
                r["before_suggested_weight"],
                r["before_weight_status"],
                r["after_suggested_weight"],
                r["action"],
                r["risk_flags"],
            ]
            for r in manifest_rows
        ],
    ))
    md.append("")
    md.append("## Interpretation")
    md.append("")
    md.append("The wrapper run1 failure showed that adapter train rows with zero suggested_weight make the legacy trainer's weighted CE/KL denominator invalid. This materialized dataset gives those train rows positive finite weights so future guarded dry-runs or probes can proceed without entering the zero-weight NaN path.")
    md.append("")
    md.append("## Explicit non-actions")
    md.append("")
    md.append("- No model training was run.")
    md.append("- No checkpoint was saved.")
    md.append("- No C weights were exported.")
    md.append("- No benchmark was run.")
    md.append("- No promotion decision was made.")
    md.append("")

    args.out_md.write_text("\n".join(md).rstrip() + "\n", encoding="utf-8")

    print("wrote", args.out_json)
    print("wrote", args.out_csv)
    print("wrote", args.out_md)
    print("changed_rows", changed)
    print("unchanged_positive_rows", unchanged_positive)
    print("skipped_rows", skipped)
    print("action_counts", dict(sorted(action_counts.items())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
