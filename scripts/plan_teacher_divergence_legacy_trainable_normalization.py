#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


REQUIRED_EXPORT_FIELDS = [
    "manifest_id",
    "board_hash",
    "current_player",
    "target_rc",
    "target_action",
    "before_target_rank",
    "before_target_prob",
    "suppress_rc",
    "suppress_prob",
    "suppress_candidates_rcs",
    "suppress_candidates_probs",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Plan normalization for legacy trainable teacher-divergence rows excluded from round2 dry-run export."
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_expanded_candidate_manifest_with_suppress_round2.csv"),
    )
    parser.add_argument(
        "--dryrun-json",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_round2_trainable_dryrun_dataset.json"),
    )
    parser.add_argument(
        "--out-csv",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_legacy_trainable_normalization_plan.csv"),
    )
    parser.add_argument(
        "--out-report",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_legacy_trainable_normalization_plan.md"),
    )
    parser.add_argument("--expected-legacy-rows", type=int, default=9)
    return parser.parse_args()


def is_blank(value: Any) -> bool:
    if value is None:
        return True
    s = str(value).strip()
    return s == "" or s.lower() in {"none", "nan", "na", "null"}


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def ready_bucket(row: dict[str, str]) -> str:
    return row.get("ready_bucket") or row.get("bucket") or ""


def nondup(row: dict[str, str]) -> bool:
    return is_blank(row.get("duplicate_of"))


def missing_required_fields(row: dict[str, str]) -> list[str]:
    return [f for f in REQUIRED_EXPORT_FIELDS if is_blank(row.get(f))]


def parse_json_list(value: str) -> list[Any]:
    if is_blank(value):
        return []
    try:
        obj = json.loads(value)
    except Exception:
        return []
    return obj if isinstance(obj, list) else []


def norm_rc(value: Any) -> tuple[int, int] | None:
    if value is None:
        return None
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except Exception:
            return None
    if isinstance(value, list) and len(value) == 2:
        try:
            rc = (int(value[0]), int(value[1]))
        except Exception:
            return None
        if 0 <= rc[0] < 15 and 0 <= rc[1] < 15:
            return rc
    return None


def can_reconstruct_suppress_from_top_policy(row: dict[str, str]) -> tuple[bool, str]:
    target = norm_rc(row.get("target_rc", ""))
    top_rcs = parse_json_list(row.get("current_best_top_policy_rcs", ""))
    top_probs = parse_json_list(row.get("current_best_top_policy_probs", ""))

    if target is None:
        return False, "missing_or_malformed_target_rc"
    if not top_rcs or not top_probs:
        return False, "missing_top_policy_lists"
    if len(top_rcs) != len(top_probs):
        return False, "top_policy_rc_prob_length_mismatch"

    for rc_raw, prob_raw in zip(top_rcs, top_probs):
        rc = norm_rc(rc_raw)
        if rc is None:
            continue
        if rc == target:
            continue
        try:
            float(prob_raw)
        except Exception:
            continue
        return True, "can_reconstruct_from_top_policy_excluding_target"

    return False, "no_non_target_top_policy_candidate"


def proposed_action(row: dict[str, str]) -> str:
    missing = set(missing_required_fields(row))
    can_reconstruct, reason = can_reconstruct_suppress_from_top_policy(row)

    if not missing:
        return "already_export_schema_complete"
    if missing.issubset({"suppress_rc", "suppress_prob", "suppress_candidates_rcs", "suppress_candidates_probs"}) and can_reconstruct:
        return "reconstruct_suppress_from_existing_top_policy"
    if can_reconstruct:
        return "partial_schema_repair_plus_suppress_reconstruct"
    if {"before_target_rank", "before_target_prob", "current_best_top_policy_rcs", "current_best_top_policy_probs"} & missing:
        return "rerun_current_best_probe_then_suppress_build"
    return f"manual_schema_review:{reason}"


def output_fields() -> list[str]:
    return [
        "manifest_id",
        "status",
        "ready_bucket",
        "source_class",
        "primary_source_path",
        "case_id",
        "game_number",
        "move_count",
        "board_hash",
        "current_player",
        "target_rc",
        "before_target_rank",
        "before_target_prob",
        "current_best_direct_rc",
        "current_best_direct_prob",
        "has_current_best_top_policy_rcs",
        "has_current_best_top_policy_probs",
        "has_suppress_rc",
        "has_suppress_prob",
        "has_suppress_candidates_rcs",
        "has_suppress_candidates_probs",
        "missing_required_fields",
        "can_reconstruct_suppress",
        "reconstruct_reason",
        "proposed_action",
        "round2_merge_action",
        "notes",
    ]


def main() -> None:
    args = parse_args()

    _fields, rows = read_csv(args.manifest)
    manifest_by_id = {r.get("manifest_id", ""): r for r in rows}

    dryrun = json.loads(args.dryrun_json.read_text(encoding="utf-8"))
    legacy_excluded = dryrun["excluded_from_dryrun_export"]["legacy_needs_schema_normalization"]
    legacy_ids = [r["manifest_id"] for r in legacy_excluded]

    if len(legacy_ids) != args.expected_legacy_rows:
        raise RuntimeError(f"expected {args.expected_legacy_rows} legacy rows from dryrun JSON, got {len(legacy_ids)}")
    if len(legacy_ids) != len(set(legacy_ids)):
        raise RuntimeError("duplicate legacy manifest_id in dryrun JSON")

    selected = []
    for mid in legacy_ids:
        if mid not in manifest_by_id:
            raise RuntimeError(f"legacy id missing from manifest: {mid}")
        row = manifest_by_id[mid]
        if not nondup(row):
            raise RuntimeError(f"legacy row unexpectedly duplicate: {mid}")
        if row.get("status") != "ready_full_schema":
            raise RuntimeError(f"legacy row not ready_full_schema: {mid} status={row.get('status')}")
        if ready_bucket(row) != "trainable_rank_11_50":
            raise RuntimeError(f"legacy row not trainable bucket: {mid} bucket={ready_bucket(row)}")
        selected.append(row)

    out_rows: list[dict[str, str]] = []
    for row in selected:
        missing = missing_required_fields(row)
        can_reconstruct, reason = can_reconstruct_suppress_from_top_policy(row)
        out_rows.append({
            "manifest_id": row.get("manifest_id", ""),
            "status": row.get("status", ""),
            "ready_bucket": ready_bucket(row),
            "source_class": row.get("source_class", ""),
            "primary_source_path": row.get("primary_source_path", ""),
            "case_id": row.get("case_id", ""),
            "game_number": row.get("game_number", ""),
            "move_count": row.get("move_count", ""),
            "board_hash": row.get("board_hash", ""),
            "current_player": row.get("current_player", ""),
            "target_rc": row.get("target_rc", ""),
            "before_target_rank": row.get("before_target_rank", ""),
            "before_target_prob": row.get("before_target_prob", ""),
            "current_best_direct_rc": row.get("current_best_direct_rc", ""),
            "current_best_direct_prob": row.get("current_best_direct_prob", ""),
            "has_current_best_top_policy_rcs": "1" if not is_blank(row.get("current_best_top_policy_rcs")) else "0",
            "has_current_best_top_policy_probs": "1" if not is_blank(row.get("current_best_top_policy_probs")) else "0",
            "has_suppress_rc": "1" if not is_blank(row.get("suppress_rc")) else "0",
            "has_suppress_prob": "1" if not is_blank(row.get("suppress_prob")) else "0",
            "has_suppress_candidates_rcs": "1" if not is_blank(row.get("suppress_candidates_rcs")) else "0",
            "has_suppress_candidates_probs": "1" if not is_blank(row.get("suppress_candidates_probs")) else "0",
            "missing_required_fields": json.dumps(missing),
            "can_reconstruct_suppress": "1" if can_reconstruct else "0",
            "reconstruct_reason": reason,
            "proposed_action": proposed_action(row),
            "round2_merge_action": row.get("round2_merge_action", "") or "pre_round2_or_unchanged",
            "notes": row.get("round2_merge_notes") or row.get("notes", ""),
        })

    action_counts = Counter(r["proposed_action"] for r in out_rows)
    reconstruct_counts = Counter(r["can_reconstruct_suppress"] for r in out_rows)
    source_counts = Counter(r["source_class"] or r["primary_source_path"] for r in out_rows)
    missing_field_counts: Counter[str] = Counter()
    for r in out_rows:
        for f in json.loads(r["missing_required_fields"]):
            missing_field_counts[f] += 1

    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=output_fields(), lineterminator="\n")
        writer.writeheader()
        writer.writerows(out_rows)

    lines = [
        "# Teacher-divergence legacy trainable normalization plan",
        "",
        "## Branch",
        "",
        "`exp/15x15-teacher-divergence-legacy-trainable-normalization-plan`",
        "",
        "## Scope",
        "",
        "- Audits the 9 legacy `trainable_rank_11_50` rows excluded from round2 dry-run export.",
        "- Determines which export-schema fields are missing.",
        "- Determines whether suppress fields can be reconstructed from existing top-policy fields.",
        "- Does not update the manifest.",
        "- Does not export a training dataset.",
        "- Does not train.",
        "- Does not save a checkpoint.",
        "- Does not C export.",
        "- Does not run public benchmark.",
        "- Does not promote.",
        "",
        "## Inputs",
        "",
        f"- manifest: `{args.manifest}`",
        f"- dry-run JSON: `{args.dryrun_json}`",
        "",
        "## Summary",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| legacy trainable rows needing normalization | {len(out_rows)} |",
        f"| rows with reconstructable suppress from top-policy | {reconstruct_counts.get('1', 0)} |",
        f"| rows not reconstructable from top-policy | {reconstruct_counts.get('0', 0)} |",
        "",
        "## Proposed actions",
        "",
        "| proposed_action | rows |",
        "|---|---:|",
    ]

    for key, value in action_counts.most_common():
        lines.append(f"| {key} | {value} |")

    lines.extend([
        "",
        "## Missing required fields",
        "",
        "| field | rows_missing |",
        "|---|---:|",
    ])

    for key, value in missing_field_counts.most_common():
        lines.append(f"| {key} | {value} |")

    lines.extend([
        "",
        "## Source counts",
        "",
        "| source | rows |",
        "|---|---:|",
    ])

    for key, value in source_counts.most_common():
        lines.append(f"| {key} | {value} |")

    lines.extend([
        "",
        "## Row-level plan",
        "",
        "| manifest_id | case_id | missing_required_fields | can_reconstruct_suppress | proposed_action |",
        "|---|---|---|---:|---|",
    ])

    for r in out_rows:
        lines.append(
            f"| {r['manifest_id']} | {r['case_id']} | `{r['missing_required_fields']}` | {r['can_reconstruct_suppress']} | {r['proposed_action']} |"
        )

    lines.extend([
        "",
        "## Recommended next step",
        "",
        "If all 9 rows are reconstructable from existing top-policy fields, run a dedicated normalization fill branch that writes suppress fields for only these 9 legacy rows, then rerun dry-run export expecting 44 exportable samples.",
        "",
        "If any row is not reconstructable, rerun current_best probe/suppress build only for those specific legacy rows before updating the manifest.",
        "",
        "## Outputs",
        "",
        f"- `{args.out_csv}`",
        f"- `{args.out_report}`",
        "",
        "## Decision",
        "",
        "No manifest update.",
        "",
        "No training.",
        "",
        "No checkpoint.",
        "",
        "No C export.",
        "",
        "No public benchmark.",
        "",
        "No promotion.",
        "",
    ])

    args.out_report.parent.mkdir(parents=True, exist_ok=True)
    args.out_report.write_text("\n".join(lines), encoding="utf-8")

    print("legacy_rows:", len(out_rows))
    print("action_counts:", json.dumps(dict(action_counts), sort_keys=True))
    print("reconstruct_counts:", json.dumps(dict(reconstruct_counts), sort_keys=True))
    print("missing_field_counts:", json.dumps(dict(missing_field_counts), sort_keys=True))
    print("out_csv:", args.out_csv)
    print("out_report:", args.out_report)
    print("no training; no checkpoint saved")


if __name__ == "__main__":
    main()
