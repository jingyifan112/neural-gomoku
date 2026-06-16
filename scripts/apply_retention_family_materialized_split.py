#!/usr/bin/env python3
"""
Apply a materialized retention-family split to a dataset in dry-run mode.

This script does not mutate the input dataset. It emits proposed/applied artifacts:
- applied split manifest CSV
- applied candidate JSON
- dry-run report MD

Scope:
- no training
- no checkpoint save
- no C export
- no benchmark
- no promotion
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
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


DEFAULT_DATASET_JSON = Path("analysis/integration_eval/teacher_divergence_retention_safety_v3_dataset.json")
DEFAULT_SPLIT_MANIFEST = Path("analysis/integration_eval/retention_family_materialized_split_manifest.csv")

DEFAULT_OUT_CSV = Path("analysis/integration_eval/retention_family_applied_split_dryrun_manifest.csv")
DEFAULT_OUT_JSON = Path("analysis/integration_eval/retention_family_applied_split_dryrun.json")
DEFAULT_OUT_MD = Path("analysis/integration_eval/retention_family_applied_split_dryrun_report.md")


def clean(v: Any) -> str:
    if v is None:
        return ""
    return str(v).strip()


def is_blank(v: Any) -> bool:
    return clean(v).lower() in {"", "none", "nan", "null"}


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


def yes(v: Any) -> bool:
    return clean(v).lower() in {"yes", "true", "1", "y"}


def yn(v: bool) -> str:
    return "yes" if v else "no"


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


def load_csv(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return [dict(r) for r in csv.DictReader(f)]


def compact_source(row: Dict[str, Any]) -> str:
    for k in ["source_id", "case_id", "row_id", "id", "position_id", "name", "label_id"]:
        v = row_get(row, [k])
        if v:
            return v
    sp = row_get(row, ["source_path"])
    if sp:
        return Path(sp).name
    return natural_row_id(row)


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


def is_heldout_retention(row: Dict[str, Any]) -> bool:
    split = row_get(row, ["split"])
    role = row_get(row, ["role", "label_role", "label_type"])
    hay = f"{split} {role}".lower()
    return "heldout_retention" in hay or "heldout retention" in hay


def dataset_target(row: Dict[str, Any]) -> str:
    return norm_move(row_get(row, ["policy_target", "target", "target_move", "label_move", "teacher_move"]))


def dataset_source_path(row: Dict[str, Any]) -> str:
    return row_get(row, ["source_path"])


def dataset_side(row: Dict[str, Any]) -> str:
    return row_get(row, ["side_to_move", "side"])


def dataset_last_move(row: Dict[str, Any]) -> str:
    return norm_move(row_get(row, ["last_move"]))


def build_manifest_indexes(rows: List[Dict[str, str]]) -> Dict[str, Dict[str, List[Dict[str, str]]]]:
    idx: Dict[str, Dict[str, List[Dict[str, str]]]] = {
        "row_key": defaultdict(list),
        "source_target": defaultdict(list),
        "source_path_target": defaultdict(list),
        "source_only": defaultdict(list),
    }

    for r in rows:
        row_key = clean(r.get("row_key"))
        source = clean(r.get("source"))
        target = clean(r.get("policy_target"))
        source_path = clean(r.get("source_path"))

        if row_key:
            idx["row_key"][row_key].append(r)
        if source and target:
            idx["source_target"][f"{source}|{target}"].append(r)
        if source_path and target:
            idx["source_path_target"][f"{source_path}|{target}"].append(r)
        if source:
            idx["source_only"][source].append(r)

    return idx


def find_manifest_match(
    dataset_row: Dict[str, Any],
    manifest_indexes: Dict[str, Dict[str, List[Dict[str, str]]]],
) -> Tuple[Optional[Dict[str, str]], str, str]:
    row_key = natural_row_id(dataset_row)
    source = compact_source(dataset_row)
    target = dataset_target(dataset_row)
    source_path = dataset_source_path(dataset_row)

    candidates = manifest_indexes["row_key"].get(row_key, [])
    if len(candidates) == 1:
        return candidates[0], "row_key", row_key

    candidates = manifest_indexes["source_target"].get(f"{source}|{target}", [])
    if len(candidates) == 1:
        return candidates[0], "source_target", f"{source}|{target}"

    candidates = manifest_indexes["source_path_target"].get(f"{source_path}|{target}", [])
    if len(candidates) == 1:
        return candidates[0], "source_path_target", f"{source_path}|{target}"

    # Source-only is intentionally used only when there is exactly one source row
    # and target is blank in the dataset row.
    source_candidates = manifest_indexes["source_only"].get(source, [])
    if len(source_candidates) == 1 and not target:
        return source_candidates[0], "source_only_blank_target", source

    if len(candidates) > 1:
        return None, "ambiguous", f"{source}|{target}"

    return None, "unmatched", f"{source}|{target}"


def proposed_split_from_role(role: str) -> str:
    if role == "nonheldout_retention_anchor":
        return "train_retention_anchor"
    if role == "heldout_retention_gate":
        return "heldout_retention_gate"
    if role == "heldout_retention_gate_family_conflict_review":
        return "heldout_retention_gate_review"
    if role == "heldout_retention_gate_review":
        return "heldout_retention_gate_review"
    return "unchanged_review"


def proposed_role_from_role(role: str) -> str:
    if role == "nonheldout_retention_anchor":
        return "nonheldout_retention_anchor"
    if role == "heldout_retention_gate":
        return "heldout_retention_gate"
    if role.startswith("heldout_retention_gate"):
        return role
    return "unchanged_review"


def apply_to_row(
    dataset_index: int,
    row: Dict[str, Any],
    manifest: Optional[Dict[str, str]],
    match_method: str,
    match_key: str,
) -> Dict[str, Any]:
    original_split = row_get(row, ["split"])
    original_role = row_get(row, ["role", "label_role", "label_type"])

    if manifest is None:
        materialized_role = ""
        proposed_split = original_split or "unchanged"
        proposed_role = original_role or "unchanged"
        gate_scope = ""
        family_id = ""
        family_targets = ""
        materialized_reason = "no materialized split row matched this dataset row"
        only_sibling_gate_ok = ""
    else:
        materialized_role = clean(manifest.get("materialized_role"))
        proposed_split = proposed_split_from_role(materialized_role)
        proposed_role = proposed_role_from_role(materialized_role)
        gate_scope = clean(manifest.get("gate_scope"))
        family_id = clean(manifest.get("family_id"))
        family_targets = clean(manifest.get("family_targets"))
        materialized_reason = clean(manifest.get("materialized_reason"))
        only_sibling_gate_ok = clean(manifest.get("allowed_as_only_sibling_family_gate"))

    return {
        "dataset_index": dataset_index,
        "row_key": natural_row_id(row),
        "source": compact_source(row),
        "source_path": dataset_source_path(row),
        "policy_target": dataset_target(row),
        "teacher_move": norm_move(row_get(row, ["teacher_move", "teacher", "best_move"])),
        "side_to_move": dataset_side(row),
        "last_move": dataset_last_move(row),
        "original_split": original_split,
        "original_role": original_role,
        "is_heldout_retention": yn(is_heldout_retention(row)),
        "matched_materialized_row": yn(manifest is not None),
        "match_method": match_method,
        "match_key": match_key,
        "family_id": family_id,
        "family_targets": family_targets,
        "materialized_role": materialized_role,
        "proposed_split": proposed_split,
        "proposed_role": proposed_role,
        "gate_scope": gate_scope,
        "allowed_as_only_sibling_family_gate": only_sibling_gate_ok,
        "materialized_reason": materialized_reason,
    }


def make_candidate_json(
    original_obj: Any,
    dataset_rows: List[Dict[str, Any]],
    applied_rows: List[Dict[str, Any]],
) -> Dict[str, Any]:
    applied_by_key = {r["row_key"]: r for r in applied_rows}

    candidate_rows = []
    for row in dataset_rows:
        key = natural_row_id(row)
        app = applied_by_key.get(key)
        new_row = dict(row)
        if app:
            new_row["retention_family_split_dryrun"] = {
                "family_id": app["family_id"],
                "family_targets": app["family_targets"],
                "materialized_role": app["materialized_role"],
                "proposed_split": app["proposed_split"],
                "proposed_role": app["proposed_role"],
                "gate_scope": app["gate_scope"],
                "allowed_as_only_sibling_family_gate": app["allowed_as_only_sibling_family_gate"],
                "match_method": app["match_method"],
                "materialized_reason": app["materialized_reason"],
            }
        else:
            new_row["retention_family_split_dryrun"] = {
                "materialized_role": "",
                "proposed_split": "unchanged",
                "proposed_role": "unchanged",
                "match_method": "unmatched",
            }
        candidate_rows.append(new_row)

    return {
        "metadata": {
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "scope": "dry-run applied split only; input dataset not modified; no training/checkpoint/C export/benchmark/promotion",
            "row_count": len(candidate_rows),
        },
        "rows": candidate_rows,
    }


def make_md_table(headers: List[str], rows: List[List[Any]], max_rows: int = 200) -> str:
    out = []
    out.append("| " + " | ".join(headers) + " |")
    out.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for r in rows[:max_rows]:
        cells = [str(x).replace("\n", " ").replace("|", "\\|") for x in r]
        out.append("| " + " | ".join(cells) + " |")
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset-json", type=Path, default=DEFAULT_DATASET_JSON)
    ap.add_argument("--split-manifest-csv", type=Path, default=DEFAULT_SPLIT_MANIFEST)
    ap.add_argument("--out-csv", type=Path, default=DEFAULT_OUT_CSV)
    ap.add_argument("--out-json", type=Path, default=DEFAULT_OUT_JSON)
    ap.add_argument("--out-md", type=Path, default=DEFAULT_OUT_MD)
    args = ap.parse_args()

    original_obj, dataset_rows = load_json_rows(args.dataset_json)
    split_rows = load_csv(args.split_manifest_csv)

    if not dataset_rows:
        raise SystemExit(f"ERROR: no dataset rows found in {args.dataset_json}")
    if not split_rows:
        raise SystemExit(f"ERROR: no split rows found in {args.split_manifest_csv}")

    manifest_indexes = build_manifest_indexes(split_rows)

    applied_rows: List[Dict[str, Any]] = []
    matched_manifest_keys = set()

    for i, row in enumerate(dataset_rows, 1):
        manifest, match_method, match_key = find_manifest_match(row, manifest_indexes)
        applied = apply_to_row(i, row, manifest, match_method, match_key)
        applied_rows.append(applied)
        if manifest is not None:
            matched_manifest_keys.add(clean(manifest.get("materialized_index")))

    unmatched_manifest_rows = [
        r for r in split_rows
        if clean(r.get("materialized_index")) not in matched_manifest_keys
    ]

    out_fields = [
        "dataset_index",
        "row_key",
        "source",
        "source_path",
        "policy_target",
        "teacher_move",
        "side_to_move",
        "last_move",
        "original_split",
        "original_role",
        "is_heldout_retention",
        "matched_materialized_row",
        "match_method",
        "match_key",
        "family_id",
        "family_targets",
        "materialized_role",
        "proposed_split",
        "proposed_role",
        "gate_scope",
        "allowed_as_only_sibling_family_gate",
        "materialized_reason",
    ]

    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=out_fields, lineterminator="\n")
        w.writeheader()
        for r in applied_rows:
            w.writerow({k: r.get(k, "") for k in out_fields})

    candidate_payload = make_candidate_json(original_obj, dataset_rows, applied_rows)
    candidate_payload["metadata"].update({
        "input_dataset_json": str(args.dataset_json),
        "input_split_manifest_csv": str(args.split_manifest_csv),
        "matched_materialized_rows": len(matched_manifest_keys),
        "unmatched_materialized_rows": len(unmatched_manifest_rows),
    })
    candidate_payload["applied_manifest"] = applied_rows
    candidate_payload["unmatched_materialized_rows"] = unmatched_manifest_rows

    args.out_json.write_text(
        json.dumps(candidate_payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    proposed_split_counts = Counter(r["proposed_split"] for r in applied_rows)
    proposed_role_counts = Counter(r["proposed_role"] for r in applied_rows)
    match_counts = Counter(r["match_method"] for r in applied_rows)
    family_counts = Counter(r["family_id"] for r in applied_rows if r["family_id"])

    md = []
    md.append("# Retention family applied split dry-run")
    md.append("")
    md.append("Scope: dry-run split application only. The input dataset was not modified. No training, checkpoint save, C export, benchmark, or promotion was run.")
    md.append("")
    md.append("## Inputs and outputs")
    md.append("")
    md.append(f"- input dataset JSON: `{args.dataset_json}`")
    md.append(f"- input materialized split manifest: `{args.split_manifest_csv}`")
    md.append(f"- output dry-run manifest CSV: `{args.out_csv}`")
    md.append(f"- output dry-run candidate JSON: `{args.out_json}`")
    md.append("")
    md.append("## Summary")
    md.append("")
    md.append(f"- dataset rows: {len(dataset_rows)}")
    md.append(f"- materialized split rows: {len(split_rows)}")
    md.append(f"- matched materialized rows: {len(matched_manifest_keys)}")
    md.append(f"- unmatched materialized rows: {len(unmatched_manifest_rows)}")
    md.append(f"- proposed split counts: {dict(sorted(proposed_split_counts.items()))}")
    md.append(f"- proposed role counts: {dict(sorted(proposed_role_counts.items()))}")
    md.append(f"- match method counts: {dict(sorted(match_counts.items()))}")
    md.append("")

    critical = [r for r in applied_rows if r["family_id"] == "bd:ea22cc14729b88fd"]
    if critical:
        md.append("## Critical sibling-conflict family application")
        md.append("")
        md.append(make_md_table(
            [
                "source",
                "target",
                "materialized_role",
                "proposed_split",
                "gate_scope",
                "only_sibling_gate_ok",
                "reason",
            ],
            [
                [
                    r["source"],
                    r["policy_target"],
                    r["materialized_role"],
                    r["proposed_split"],
                    r["gate_scope"],
                    r["allowed_as_only_sibling_family_gate"],
                    r["materialized_reason"],
                ]
                for r in critical
            ],
        ))
        md.append("")

    md.append("## Family counts")
    md.append("")
    md.append(make_md_table(
        ["family_id", "rows"],
        [[fid, n] for fid, n in sorted(family_counts.items())],
    ))
    md.append("")

    md.append("## Applied row manifest")
    md.append("")
    md.append(make_md_table(
        [
            "idx",
            "source",
            "target",
            "original_split",
            "original_role",
            "matched",
            "family_id",
            "materialized_role",
            "proposed_split",
            "gate_scope",
        ],
        [
            [
                r["dataset_index"],
                r["source"],
                r["policy_target"],
                r["original_split"],
                r["original_role"],
                r["matched_materialized_row"],
                r["family_id"],
                r["materialized_role"],
                r["proposed_split"],
                r["gate_scope"],
            ]
            for r in applied_rows
        ],
    ))
    md.append("")

    if unmatched_manifest_rows:
        md.append("## Unmatched materialized split rows")
        md.append("")
        md.append("These materialized rows did not match the selected input dataset. This is acceptable if the selected input dataset is narrower than the proposal source, but must be reviewed before training.")
        md.append("")
        md.append(make_md_table(
            [
                "materialized_index",
                "family_id",
                "source",
                "target",
                "materialized_role",
                "reason",
            ],
            [
                [
                    r.get("materialized_index", ""),
                    r.get("family_id", ""),
                    r.get("source", ""),
                    r.get("policy_target", ""),
                    r.get("materialized_role", ""),
                    r.get("materialized_reason", ""),
                ]
                for r in unmatched_manifest_rows
            ],
        ))
        md.append("")

    md.append("## Usage notes")
    md.append("")
    md.append("- This dry-run file is a candidate split application artifact, not a training dataset approval.")
    md.append("- Rows with `proposed_split=train_retention_anchor` should be treated as non-heldout retention anchors in the next candidate split.")
    md.append("- Rows with `gate_scope=external_or_family_level_only_not_sibling_only` must not be used as the sole heldout evidence for a sibling target from the same family.")
    md.append("- Review unmatched materialized rows before using any generated split for training.")
    md.append("")

    args.out_md.write_text("\n".join(md).rstrip() + "\n", encoding="utf-8")

    print("wrote", args.out_csv)
    print("wrote", args.out_json)
    print("wrote", args.out_md)
    print("dataset rows:", len(dataset_rows))
    print("materialized rows:", len(split_rows))
    print("matched materialized rows:", len(matched_manifest_keys))
    print("unmatched materialized rows:", len(unmatched_manifest_rows))
    print("proposed_split_counts:", dict(sorted(proposed_split_counts.items())))
    print("proposed_role_counts:", dict(sorted(proposed_role_counts.items())))
    print("match_counts:", dict(sorted(match_counts.items())))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
