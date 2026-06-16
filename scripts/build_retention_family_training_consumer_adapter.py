#!/usr/bin/env python3
"""
Build consumer-compatible retention-family training/eval datasets.

This is a dataset adapter only:
- no training
- no checkpoint save
- no C export
- no benchmark
- no promotion

The adapter consumes:
- teacher_divergence_retention_safety_v3_dataset.json
- retention_family_training_input_dryrun_train_manifest.csv
- retention_family_training_input_dryrun_eval_manifest.csv

It emits:
- train-side adapter dataset JSON
- eval/gate adapter dataset JSON
- adapter manifest CSV
- adapter summary JSON
- adapter report MD
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple


CRITICAL_FAMILY = "bd:ea22cc14729b88fd"

DEFAULT_DATASET_JSON = Path("analysis/integration_eval/teacher_divergence_retention_safety_v3_dataset.json")
DEFAULT_TRAIN_MANIFEST = Path("analysis/integration_eval/retention_family_training_input_dryrun_train_manifest.csv")
DEFAULT_EVAL_MANIFEST = Path("analysis/integration_eval/retention_family_training_input_dryrun_eval_manifest.csv")

DEFAULT_OUT_TRAIN_JSON = Path("analysis/integration_eval/retention_family_training_consumer_adapter_train_dataset.json")
DEFAULT_OUT_EVAL_JSON = Path("analysis/integration_eval/retention_family_training_consumer_adapter_eval_dataset.json")
DEFAULT_OUT_MANIFEST_CSV = Path("analysis/integration_eval/retention_family_training_consumer_adapter_manifest.csv")
DEFAULT_OUT_SUMMARY_JSON = Path("analysis/integration_eval/retention_family_training_consumer_adapter_summary.json")
DEFAULT_OUT_MD = Path("analysis/integration_eval/retention_family_training_consumer_adapter_report.md")


def clean(v: Any) -> str:
    if v is None:
        return ""
    return str(v).strip()


def is_blank(v: Any) -> bool:
    return clean(v).lower() in {"", "none", "nan", "null"}


def yes(v: Any) -> bool:
    return clean(v).lower() in {"yes", "true", "1", "y"}


def norm_col_name(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", s.strip().lower()).strip("_")


def row_get(row: Dict[str, Any], names: Sequence[str], default: str = "") -> str:
    by_norm = {norm_col_name(k): k for k in row.keys()}
    for name in names:
        k = by_norm.get(norm_col_name(name))
        if k is not None and not is_blank(row.get(k)):
            return clean(row.get(k))
    return default


def norm_move(v: Any) -> str:
    if is_blank(v):
        return ""
    nums = re.findall(r"-?\d+", str(v))
    if len(nums) >= 2:
        return f"{int(nums[0])},{int(nums[1])}"
    return re.sub(r"\s+", "", str(v).strip())


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return [dict(r) for r in csv.DictReader(f)]


def load_json_rows(path: Path) -> Tuple[Any, List[Dict[str, Any]]]:
    obj = json.loads(path.read_text(encoding="utf-8"))

    rows: List[Dict[str, Any]] = []

    def walk(x: Any) -> None:
        if isinstance(x, list):
            for item in x:
                walk(item)
            return

        if isinstance(x, dict):
            for key in ("rows", "data", "examples", "items", "records", "positions"):
                if key in x and isinstance(x[key], list):
                    walk(x[key])
                    return

            rowish_keys = {
                "split",
                "role",
                "label_role",
                "label_type",
                "policy_target",
                "target",
                "target_move",
                "teacher_move",
                "source_path",
                "side_to_move",
                "last_move",
                "board",
                "moves",
                "position_id",
                "row_id",
                "id",
            }
            if any(k in x for k in rowish_keys):
                rows.append(x)

    walk(obj)
    return obj, rows


def natural_row_id(row: Dict[str, Any]) -> str:
    explicit = row_get(row, [
        "row_id",
        "id",
        "case_id",
        "position_id",
        "example_id",
        "name",
        "label_id",
        "uid",
    ])
    if explicit:
        return explicit

    parts = [
        row_get(row, ["source_path"]),
        row_get(row, ["source_id", "source_name"]),
        row_get(row, ["game_id", "game"]),
        row_get(row, ["ply", "move_index", "move_number"]),
        row_get(row, ["side_to_move", "side"]),
        norm_move(row_get(row, ["last_move"])),
        norm_move(row_get(row, ["policy_target", "target", "target_move", "label_move"])),
        norm_move(row_get(row, ["teacher_move", "teacher", "best_move"])),
    ]
    key = "|".join(p for p in parts if p)
    if key:
        return key

    raw = json.dumps(row, ensure_ascii=False, sort_keys=True, default=str)
    return "row:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def compact_source(row: Dict[str, Any]) -> str:
    for k in ["source_id", "case_id", "row_id", "id", "position_id", "name", "label_id"]:
        v = row_get(row, [k])
        if v:
            return v
    sp = row_get(row, ["source_path"])
    if sp:
        return Path(sp).name
    return natural_row_id(row)


def dataset_target(row: Dict[str, Any]) -> str:
    return norm_move(row_get(row, ["policy_target", "target", "target_move", "label_move", "teacher_move"]))


def dataset_source_path(row: Dict[str, Any]) -> str:
    return row_get(row, ["source_path"])


def build_dataset_indexes(rows: List[Dict[str, Any]]) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
    idx: Dict[str, Dict[str, List[Dict[str, Any]]]] = {
        "row_key": defaultdict(list),
        "source_target": defaultdict(list),
        "source_path_target": defaultdict(list),
    }

    for r in rows:
        row_key = natural_row_id(r)
        source = compact_source(r)
        target = dataset_target(r)
        source_path = dataset_source_path(r)

        if row_key:
            idx["row_key"][row_key].append(r)
        if source and target:
            idx["source_target"][f"{source}|{target}"].append(r)
        if source_path and target:
            idx["source_path_target"][f"{source_path}|{target}"].append(r)

    return idx


def find_dataset_row(
    manifest_row: Dict[str, str],
    indexes: Dict[str, Dict[str, List[Dict[str, Any]]]],
) -> Tuple[Optional[Dict[str, Any]], str, str]:
    row_key = clean(manifest_row.get("row_key"))
    source = clean(manifest_row.get("source"))
    target = clean(manifest_row.get("policy_target"))
    source_path = clean(manifest_row.get("source_path"))

    candidates = indexes["row_key"].get(row_key, [])
    if len(candidates) == 1:
        return candidates[0], "row_key", row_key

    candidates = indexes["source_target"].get(f"{source}|{target}", [])
    if len(candidates) == 1:
        return candidates[0], "source_target", f"{source}|{target}"

    candidates = indexes["source_path_target"].get(f"{source_path}|{target}", [])
    if len(candidates) == 1:
        return candidates[0], "source_path_target", f"{source_path}|{target}"

    if len(candidates) > 1:
        return None, "ambiguous", f"{source_path}|{target}"

    return None, "unmatched", f"{source}|{target}"


def adapt_row(
    dataset_row: Dict[str, Any],
    manifest_row: Dict[str, str],
    adapter_side: str,
    compat_split: str,
    compat_role: str,
) -> Dict[str, Any]:
    out = dict(dataset_row)

    original_split = row_get(dataset_row, ["split"])
    original_role = row_get(dataset_row, ["role", "label_role", "label_type"])

    out["split"] = compat_split
    out["role"] = compat_role
    out["label_type"] = compat_role

    out["retention_family_consumer_adapter"] = {
        "adapter_side": adapter_side,
        "family_id": clean(manifest_row.get("family_id")),
        "family_targets": clean(manifest_row.get("family_targets")),
        "policy_target": clean(manifest_row.get("policy_target")),
        "source": clean(manifest_row.get("source")),
        "source_path": clean(manifest_row.get("source_path")),
        "original_split": original_split,
        "original_role": original_role,
        "materialized_role": clean(manifest_row.get("materialized_role")),
        "proposed_split": clean(manifest_row.get("proposed_split")),
        "proposed_role": clean(manifest_row.get("proposed_role")),
        "gate_scope": clean(manifest_row.get("gate_scope")),
        "allowed_as_only_sibling_family_gate": clean(manifest_row.get("allowed_as_only_sibling_family_gate")),
        "train_use_policy": clean(manifest_row.get("train_use_policy")),
        "eval_use_policy": clean(manifest_row.get("eval_use_policy")),
        "risk_flags": clean(manifest_row.get("risk_flags")),
        "materialized_reason": clean(manifest_row.get("materialized_reason")),
        "compat_split": compat_split,
        "compat_role": compat_role,
    }

    return out


def validate_adapter_outputs(
    train_rows: List[Dict[str, Any]],
    eval_rows: List[Dict[str, Any]],
    train_manifest_rows: List[Dict[str, str]],
    eval_manifest_rows: List[Dict[str, str]],
) -> List[str]:
    errors: List[str] = []

    if len(train_rows) != len(train_manifest_rows):
        errors.append(f"train adapted row count {len(train_rows)} != train manifest row count {len(train_manifest_rows)}")
    if len(eval_rows) != len(eval_manifest_rows):
        errors.append(f"eval adapted row count {len(eval_rows)} != eval manifest row count {len(eval_manifest_rows)}")

    train_targets = {
        clean(r.get("retention_family_consumer_adapter", {}).get("policy_target"))
        for r in train_rows
        if clean(r.get("retention_family_consumer_adapter", {}).get("family_id")) == CRITICAL_FAMILY
    }
    eval_targets = {
        clean(r.get("retention_family_consumer_adapter", {}).get("policy_target"))
        for r in eval_rows
        if clean(r.get("retention_family_consumer_adapter", {}).get("family_id")) == CRITICAL_FAMILY
    }

    for target in ["7,10", "10,7"]:
        if target not in train_targets:
            errors.append(f"critical target {target} missing from adapted train dataset")

    if "7,9" not in eval_targets:
        errors.append("critical target 7,9 missing from adapted eval dataset")

    for r in eval_rows:
        meta = r.get("retention_family_consumer_adapter", {})
        if clean(meta.get("family_id")) == CRITICAL_FAMILY and clean(meta.get("policy_target")) == "7,9":
            if clean(meta.get("gate_scope")) != "external_or_family_level_only_not_sibling_only":
                errors.append("critical target 7,9 has wrong gate_scope")
            if clean(meta.get("allowed_as_only_sibling_family_gate")) == "yes":
                errors.append("critical target 7,9 incorrectly allowed as only sibling-family gate")

    train_keys = {
        f"{clean(r.get('retention_family_consumer_adapter', {}).get('family_id'))}|{clean(r.get('retention_family_consumer_adapter', {}).get('policy_target'))}|{natural_row_id(r)}"
        for r in train_rows
    }
    eval_keys = {
        f"{clean(r.get('retention_family_consumer_adapter', {}).get('family_id'))}|{clean(r.get('retention_family_consumer_adapter', {}).get('policy_target'))}|{natural_row_id(r)}"
        for r in eval_rows
    }
    overlap = sorted(train_keys & eval_keys)
    if overlap:
        errors.append(f"adapted train/eval overlap: {overlap[:5]}")

    return errors


def write_dataset(path: Path, rows: List[Dict[str, Any]], metadata: Dict[str, Any]) -> None:
    payload = {
        "metadata": metadata,
        "rows": rows,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def make_table(headers: List[str], rows: List[List[Any]], max_rows: int = 200) -> str:
    lines = []
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for r in rows[:max_rows]:
        cells = [str(x).replace("\n", " ").replace("|", "\\|") for x in r]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset-json", type=Path, default=DEFAULT_DATASET_JSON)
    ap.add_argument("--train-manifest", type=Path, default=DEFAULT_TRAIN_MANIFEST)
    ap.add_argument("--eval-manifest", type=Path, default=DEFAULT_EVAL_MANIFEST)
    ap.add_argument("--compat-train-split", default="train_candidate")
    ap.add_argument("--compat-train-role", default="nonheldout_retention_anchor")
    ap.add_argument("--compat-eval-split", default="heldout_retention")
    ap.add_argument("--compat-eval-role", default="heldout_retention_gate")
    ap.add_argument("--out-train-json", type=Path, default=DEFAULT_OUT_TRAIN_JSON)
    ap.add_argument("--out-eval-json", type=Path, default=DEFAULT_OUT_EVAL_JSON)
    ap.add_argument("--out-manifest-csv", type=Path, default=DEFAULT_OUT_MANIFEST_CSV)
    ap.add_argument("--out-summary-json", type=Path, default=DEFAULT_OUT_SUMMARY_JSON)
    ap.add_argument("--out-md", type=Path, default=DEFAULT_OUT_MD)
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()

    _, dataset_rows = load_json_rows(args.dataset_json)
    train_manifest_rows = read_csv(args.train_manifest)
    eval_manifest_rows = read_csv(args.eval_manifest)

    if not dataset_rows:
        raise SystemExit(f"ERROR: no rows found in dataset: {args.dataset_json}")
    if not train_manifest_rows:
        raise SystemExit(f"ERROR: empty train manifest: {args.train_manifest}")
    if not eval_manifest_rows:
        raise SystemExit(f"ERROR: empty eval manifest: {args.eval_manifest}")

    indexes = build_dataset_indexes(dataset_rows)

    adapter_manifest: List[Dict[str, Any]] = []
    adapted_train_rows: List[Dict[str, Any]] = []
    adapted_eval_rows: List[Dict[str, Any]] = []

    def process_manifest_rows(side: str, rows: List[Dict[str, str]]) -> None:
        for idx, m in enumerate(rows, 1):
            dataset_row, match_method, match_key = find_dataset_row(m, indexes)

            if side == "train":
                compat_split = args.compat_train_split
                compat_role = args.compat_train_role
            else:
                compat_split = args.compat_eval_split
                compat_role = args.compat_eval_role

            matched = dataset_row is not None
            if matched:
                adapted = adapt_row(dataset_row, m, side, compat_split, compat_role)
                if side == "train":
                    adapted_train_rows.append(adapted)
                else:
                    adapted_eval_rows.append(adapted)

            adapter_manifest.append({
                "adapter_side": side,
                "manifest_index": idx,
                "matched_dataset_row": "yes" if matched else "no",
                "match_method": match_method,
                "match_key": match_key,
                "family_id": clean(m.get("family_id")),
                "source": clean(m.get("source")),
                "source_path": clean(m.get("source_path")),
                "policy_target": clean(m.get("policy_target")),
                "teacher_move": clean(m.get("teacher_move")),
                "original_split": clean(m.get("original_split")),
                "original_role": clean(m.get("original_role")),
                "materialized_role": clean(m.get("materialized_role")),
                "proposed_split": clean(m.get("proposed_split")),
                "proposed_role": clean(m.get("proposed_role")),
                "gate_scope": clean(m.get("gate_scope")),
                "allowed_as_only_sibling_family_gate": clean(m.get("allowed_as_only_sibling_family_gate")),
                "train_use_policy": clean(m.get("train_use_policy")),
                "eval_use_policy": clean(m.get("eval_use_policy")),
                "risk_flags": clean(m.get("risk_flags")),
                "materialized_reason": clean(m.get("materialized_reason")),
                "compat_split": compat_split,
                "compat_role": compat_role,
            })

    process_manifest_rows("train", train_manifest_rows)
    process_manifest_rows("eval", eval_manifest_rows)

    validation_errors = validate_adapter_outputs(
        adapted_train_rows,
        adapted_eval_rows,
        train_manifest_rows,
        eval_manifest_rows,
    )

    if args.strict and validation_errors:
        raise SystemExit("ERROR: adapter validation failed: " + "; ".join(validation_errors))

    generated_at = datetime.now(timezone.utc).isoformat()

    common_metadata = {
        "generated_at_utc": generated_at,
        "scope": "consumer adapter dataset only; no training/checkpoint/C export/benchmark/promotion",
        "input_dataset_json": str(args.dataset_json),
        "input_train_manifest": str(args.train_manifest),
        "input_eval_manifest": str(args.eval_manifest),
        "critical_family": CRITICAL_FAMILY,
    }

    write_dataset(
        args.out_train_json,
        adapted_train_rows,
        {
            **common_metadata,
            "adapter_side": "train",
            "compat_split": args.compat_train_split,
            "compat_role": args.compat_train_role,
            "row_count": len(adapted_train_rows),
        },
    )
    write_dataset(
        args.out_eval_json,
        adapted_eval_rows,
        {
            **common_metadata,
            "adapter_side": "eval",
            "compat_split": args.compat_eval_split,
            "compat_role": args.compat_eval_role,
            "row_count": len(adapted_eval_rows),
        },
    )

    manifest_fields = [
        "adapter_side",
        "manifest_index",
        "matched_dataset_row",
        "match_method",
        "match_key",
        "family_id",
        "source",
        "source_path",
        "policy_target",
        "teacher_move",
        "original_split",
        "original_role",
        "materialized_role",
        "proposed_split",
        "proposed_role",
        "gate_scope",
        "allowed_as_only_sibling_family_gate",
        "train_use_policy",
        "eval_use_policy",
        "risk_flags",
        "materialized_reason",
        "compat_split",
        "compat_role",
    ]

    args.out_manifest_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.out_manifest_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=manifest_fields, lineterminator="\n")
        w.writeheader()
        for r in adapter_manifest:
            w.writerow({k: r.get(k, "") for k in manifest_fields})

    match_counts = Counter(r["matched_dataset_row"] for r in adapter_manifest)
    side_counts = Counter(r["adapter_side"] for r in adapter_manifest)
    compat_split_counts = Counter(r["compat_split"] for r in adapter_manifest)
    family_counts = Counter(r["family_id"] for r in adapter_manifest if r["family_id"])

    critical_manifest = [
        r for r in adapter_manifest
        if r["family_id"] == CRITICAL_FAMILY
    ]

    summary = {
        "metadata": {
            **common_metadata,
            "output_train_json": str(args.out_train_json),
            "output_eval_json": str(args.out_eval_json),
            "output_manifest_csv": str(args.out_manifest_csv),
        },
        "counts": {
            "source_dataset_rows": len(dataset_rows),
            "train_manifest_rows": len(train_manifest_rows),
            "eval_manifest_rows": len(eval_manifest_rows),
            "adapted_train_rows": len(adapted_train_rows),
            "adapted_eval_rows": len(adapted_eval_rows),
            "adapter_manifest_rows": len(adapter_manifest),
            "match_counts": dict(sorted(match_counts.items())),
            "side_counts": dict(sorted(side_counts.items())),
            "compat_split_counts": dict(sorted(compat_split_counts.items())),
            "family_counts": dict(sorted(family_counts.items())),
        },
        "validation_errors": validation_errors,
        "critical_family_rows": critical_manifest,
        "consumer_contract": {
            "train_json": "Rows are consumer-compatible train-side retention anchors. They use compat split/role but preserve original split/role in retention_family_consumer_adapter metadata.",
            "eval_json": "Rows are consumer-compatible eval/gate rows. Gate scope must still be enforced by the gated runner/reporting layer.",
            "critical_family_rule": "7,10 and 10,7 are train-side; 7,9 is eval-side with external_or_family_level_only_not_sibling_only scope.",
        },
    }

    args.out_summary_json.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    md: List[str] = []
    md.append("# Retention family training consumer adapter")
    md.append("")
    md.append("Scope: consumer adapter dataset generation only. No training, checkpoint save, C export, benchmark, or promotion was run.")
    md.append("")
    md.append("## Inputs and outputs")
    md.append("")
    md.append(f"- input dataset JSON: `{args.dataset_json}`")
    md.append(f"- input train manifest: `{args.train_manifest}`")
    md.append(f"- input eval manifest: `{args.eval_manifest}`")
    md.append(f"- output train dataset JSON: `{args.out_train_json}`")
    md.append(f"- output eval dataset JSON: `{args.out_eval_json}`")
    md.append(f"- output adapter manifest CSV: `{args.out_manifest_csv}`")
    md.append(f"- output summary JSON: `{args.out_summary_json}`")
    md.append("")
    md.append("## Summary")
    md.append("")
    md.append(f"- source dataset rows: {len(dataset_rows)}")
    md.append(f"- train manifest rows: {len(train_manifest_rows)}")
    md.append(f"- eval manifest rows: {len(eval_manifest_rows)}")
    md.append(f"- adapted train rows: {len(adapted_train_rows)}")
    md.append(f"- adapted eval rows: {len(adapted_eval_rows)}")
    md.append(f"- match counts: `{dict(sorted(match_counts.items()))}`")
    md.append(f"- compat split counts: `{dict(sorted(compat_split_counts.items()))}`")
    md.append(f"- validation errors: `{validation_errors}`")
    md.append("")
    md.append("## Critical family")
    md.append("")
    md.append(f"- family_id: `{CRITICAL_FAMILY}`")
    md.append("")
    md.append(make_table(
        [
            "side",
            "target",
            "matched",
            "compat_split",
            "compat_role",
            "gate_scope",
            "only_sibling_gate_ok",
            "risk_flags",
        ],
        [
            [
                r["adapter_side"],
                r["policy_target"],
                r["matched_dataset_row"],
                r["compat_split"],
                r["compat_role"],
                r["gate_scope"],
                r["allowed_as_only_sibling_family_gate"],
                r["risk_flags"],
            ]
            for r in critical_manifest
        ],
    ))
    md.append("")
    md.append("Interpretation:")
    md.append("")
    md.append("- `7,10` and `10,7` are emitted on the train side as non-heldout retention anchor candidates.")
    md.append("- `7,9` is emitted on the eval side with restricted gate scope.")
    md.append("- The adapter preserves family metadata so the gated runner can enforce sibling-family restrictions.")
    md.append("")
    md.append("## Adapter manifest")
    md.append("")
    md.append(make_table(
        [
            "side",
            "family_id",
            "source",
            "target",
            "matched",
            "match_method",
            "compat_split",
            "compat_role",
            "reason",
        ],
        [
            [
                r["adapter_side"],
                r["family_id"],
                r["source"],
                r["policy_target"],
                r["matched_dataset_row"],
                r["match_method"],
                r["compat_split"],
                r["compat_role"],
                r["materialized_reason"],
            ]
            for r in adapter_manifest
        ],
    ))
    md.append("")
    md.append("## Consumer contract")
    md.append("")
    md.append("- Future training commands may consume the train adapter JSON as train-side retention anchors.")
    md.append("- Future gate commands may consume the eval adapter JSON as eval/heldout gate rows.")
    md.append("- The eval adapter JSON alone does not make a promotion decision; gate results must still go through `scripts/run_retention_family_gated_training_probe.py`.")
    md.append("- `external_or_family_level_only_not_sibling_only` remains a hard restriction for critical-family gates.")
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

    print("wrote", args.out_train_json)
    print("wrote", args.out_eval_json)
    print("wrote", args.out_manifest_csv)
    print("wrote", args.out_summary_json)
    print("wrote", args.out_md)
    print("adapted train rows:", len(adapted_train_rows))
    print("adapted eval rows:", len(adapted_eval_rows))
    print("validation_errors:", validation_errors)
    print("match_counts:", dict(sorted(match_counts.items())))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
