#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


EXPECTED_TOTAL_TRAINABLE_READY = 44
EXPECTED_EXPORTABLE_TRAINABLE = 35
EXPECTED_LEGACY_NEEDS_NORMALIZATION = 9


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Dry-run export and schema validation for round2 teacher-divergence trainable rows."
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_expanded_candidate_manifest_with_suppress_round2.csv"),
    )
    parser.add_argument(
        "--out-json",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_round2_trainable_dryrun_dataset.json"),
    )
    parser.add_argument(
        "--out-report",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_round2_trainable_dryrun_report.md"),
    )
    parser.add_argument("--expected-total-trainable-ready", type=int, default=EXPECTED_TOTAL_TRAINABLE_READY)
    parser.add_argument("--expected-exportable-trainable", type=int, default=EXPECTED_EXPORTABLE_TRAINABLE)
    parser.add_argument("--expected-legacy-needs-normalization", type=int, default=EXPECTED_LEGACY_NEEDS_NORMALIZATION)
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


def parse_json_value(value: str, field: str, manifest_id: str) -> Any:
    if is_blank(value):
        raise ValueError(f"{manifest_id}: missing {field}")
    try:
        return json.loads(value)
    except Exception as exc:
        raise ValueError(f"{manifest_id}: could not parse {field}={value!r}") from exc


def parse_rc(value: str, field: str, manifest_id: str) -> list[int]:
    obj = parse_json_value(value, field, manifest_id)
    if not isinstance(obj, list) or len(obj) != 2:
        raise ValueError(f"{manifest_id}: {field} must be [row, col], got {obj!r}")
    rc = [int(obj[0]), int(obj[1])]
    if not (0 <= rc[0] < 15 and 0 <= rc[1] < 15):
        raise ValueError(f"{manifest_id}: {field} out of 15x15 range: {rc}")
    return rc


def parse_rc_list(value: str, field: str, manifest_id: str) -> list[list[int]]:
    obj = parse_json_value(value, field, manifest_id)
    if not isinstance(obj, list):
        raise ValueError(f"{manifest_id}: {field} must be list, got {obj!r}")

    out: list[list[int]] = []
    for item in obj:
        if not isinstance(item, list) or len(item) != 2:
            raise ValueError(f"{manifest_id}: malformed item in {field}: {item!r}")
        rc = [int(item[0]), int(item[1])]
        if not (0 <= rc[0] < 15 and 0 <= rc[1] < 15):
            raise ValueError(f"{manifest_id}: {field} item out of range: {rc}")
        out.append(rc)

    return out


def parse_float(value: str, field: str, manifest_id: str) -> float:
    if is_blank(value):
        raise ValueError(f"{manifest_id}: missing {field}")
    try:
        return float(value)
    except Exception as exc:
        raise ValueError(f"{manifest_id}: malformed {field}={value!r}") from exc


def parse_int(value: str, field: str, manifest_id: str) -> int:
    if is_blank(value):
        raise ValueError(f"{manifest_id}: missing {field}")
    try:
        return int(float(value))
    except Exception as exc:
        raise ValueError(f"{manifest_id}: malformed {field}={value!r}") from exc


def ready_bucket(row: dict[str, str]) -> str:
    return row.get("ready_bucket") or row.get("bucket") or ""


def is_non_duplicate(row: dict[str, str]) -> bool:
    return is_blank(row.get("duplicate_of"))


def has_export_schema(row: dict[str, str]) -> bool:
    required = [
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
    return all(not is_blank(row.get(k)) for k in required)


def build_sample(row: dict[str, str]) -> dict[str, Any]:
    mid = row.get("manifest_id", "")

    target_rc = parse_rc(row.get("target_rc", ""), "target_rc", mid)
    suppress_rc = parse_rc(row.get("suppress_rc", ""), "suppress_rc", mid)
    suppress_candidates_rcs = parse_rc_list(row.get("suppress_candidates_rcs", ""), "suppress_candidates_rcs", mid)

    target_rank = parse_int(row.get("before_target_rank", ""), "before_target_rank", mid)
    target_prob = parse_float(row.get("before_target_prob", ""), "before_target_prob", mid)
    suppress_prob = parse_float(row.get("suppress_prob", ""), "suppress_prob", mid)
    current_player = parse_int(row.get("current_player", ""), "current_player", mid)

    if target_rc == suppress_rc:
        raise ValueError(f"{mid}: target_rc equals suppress_rc: {target_rc}")
    if not (11 <= target_rank <= 50):
        raise ValueError(f"{mid}: target rank must be 11..50 for trainable dry-run export, got {target_rank}")
    if current_player not in {-1, 1}:
        raise ValueError(f"{mid}: current_player must be -1 or 1, got {current_player}")

    suppress_candidates_probs = parse_json_value(row.get("suppress_candidates_probs", ""), "suppress_candidates_probs", mid)
    if not isinstance(suppress_candidates_probs, list):
        raise ValueError(f"{mid}: suppress_candidates_probs must be list")
    suppress_candidates_probs = [float(x) for x in suppress_candidates_probs]

    if len(suppress_candidates_rcs) != len(suppress_candidates_probs):
        raise ValueError(
            f"{mid}: suppress candidates rcs/probs length mismatch: "
            f"{len(suppress_candidates_rcs)} vs {len(suppress_candidates_probs)}"
        )

    return {
        "manifest_id": mid,
        "split_role": "dryrun_trainable_candidate",
        "status": row.get("status", ""),
        "ready_bucket": ready_bucket(row),
        "source_class": row.get("source_class", ""),
        "primary_source_path": row.get("primary_source_path", ""),
        "case_id": row.get("case_id", ""),
        "game_number": row.get("game_number", ""),
        "move_count": row.get("move_count", ""),
        "board_hash": row.get("board_hash", ""),
        "current_player": current_player,
        "target_rc": target_rc,
        "target_action": parse_int(row.get("target_action", ""), "target_action", mid),
        "before_target_rank": target_rank,
        "before_target_prob": target_prob,
        "current_best_direct_rc": parse_rc(row.get("current_best_direct_rc", ""), "current_best_direct_rc", mid)
        if not is_blank(row.get("current_best_direct_rc"))
        else None,
        "current_best_direct_prob": parse_float(row.get("current_best_direct_prob", ""), "current_best_direct_prob", mid)
        if not is_blank(row.get("current_best_direct_prob"))
        else None,
        "suppress_rc": suppress_rc,
        "suppress_prob": suppress_prob,
        "suppress_rank_in_top_policy": parse_int(row.get("suppress_rank_in_top_policy", ""), "suppress_rank_in_top_policy", mid),
        "suppress_prob_gap": parse_float(row.get("suppress_prob_gap", ""), "suppress_prob_gap", mid)
        if not is_blank(row.get("suppress_prob_gap"))
        else None,
        "suppress_prob_ratio": parse_float(row.get("suppress_prob_ratio", ""), "suppress_prob_ratio", mid)
        if not is_blank(row.get("suppress_prob_ratio"))
        else None,
        "suppress_candidates_rcs": suppress_candidates_rcs,
        "suppress_candidates_probs": suppress_candidates_probs,
        "round2_merge_action": row.get("round2_merge_action", ""),
        "notes": row.get("round2_merge_notes") or row.get("notes", ""),
        "weight": 1.0,
    }


def main() -> None:
    args = parse_args()

    _fields, rows = read_csv(args.manifest)
    nondup = [r for r in rows if is_non_duplicate(r)]

    ready_trainable = [
        r for r in nondup
        if r.get("status") == "ready_full_schema"
        and ready_bucket(r) == "trainable_rank_11_50"
    ]

    exportable_rows = [r for r in ready_trainable if has_export_schema(r)]
    legacy_needs_normalization = [r for r in ready_trainable if not has_export_schema(r)]

    if len(ready_trainable) != args.expected_total_trainable_ready:
        raise RuntimeError(f"expected {args.expected_total_trainable_ready} total trainable ready rows, got {len(ready_trainable)}")
    if len(exportable_rows) != args.expected_exportable_trainable:
        raise RuntimeError(f"expected {args.expected_exportable_trainable} exportable rows, got {len(exportable_rows)}")
    if len(legacy_needs_normalization) != args.expected_legacy_needs_normalization:
        raise RuntimeError(
            f"expected {args.expected_legacy_needs_normalization} legacy rows needing normalization, "
            f"got {len(legacy_needs_normalization)}"
        )

    samples = [build_sample(r) for r in exportable_rows]

    manifest_ids = [s["manifest_id"] for s in samples]
    if len(manifest_ids) != len(set(manifest_ids)):
        raise RuntimeError("duplicate manifest_id in dry-run samples")

    source_counts = Counter(s["source_class"] or s["primary_source_path"] for s in samples)
    rank_counts = Counter(str(s["before_target_rank"]) for s in samples)
    suppress_count_distribution = Counter(str(len(s["suppress_candidates_rcs"])) for s in samples)
    round2_action_counts = Counter(s["round2_merge_action"] or "pre_round2_or_unchanged" for s in samples)

    payload = {
        "metadata": {
            "name": "teacher_divergence_round2_trainable_dryrun_dataset",
            "manifest": str(args.manifest),
            "board_size": 15,
            "sample_count": len(samples),
            "selection": {
                "status": "ready_full_schema",
                "ready_bucket": "trainable_rank_11_50",
                "requires_suppress_fields": True,
                "excluded_legacy_needs_normalization_count": len(legacy_needs_normalization),
            },
            "not_training": True,
            "not_checkpoint": True,
            "not_c_export": True,
            "not_public_benchmark": True,
            "not_promotion": True,
        },
        "samples": samples,
        "excluded_from_dryrun_export": {
            "legacy_needs_schema_normalization": [
                {
                    "manifest_id": r.get("manifest_id", ""),
                    "status": r.get("status", ""),
                    "ready_bucket": ready_bucket(r),
                    "source_class": r.get("source_class", ""),
                    "primary_source_path": r.get("primary_source_path", ""),
                    "case_id": r.get("case_id", ""),
                    "reason": "missing suppress fields in merged manifest",
                }
                for r in legacy_needs_normalization
            ]
        },
    }

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# Teacher-divergence round2 trainable dry-run dataset export",
        "",
        "## Branch",
        "",
        "`exp/15x15-teacher-divergence-dryrun-dataset-export-round2`",
        "",
        "## Scope",
        "",
        "- Dry-run export only.",
        "- Selects trainable `ready_full_schema` rows with `ready_bucket == trainable_rank_11_50`.",
        "- Requires target rank/prob and suppress fields.",
        "- Excludes protected top10 rows from training export.",
        "- Excludes tail rank > 50 rows from training export.",
        "- Excludes legacy trainable rows that need suppress schema normalization.",
        "- No training.",
        "- No checkpoint save.",
        "- No C export.",
        "- No public benchmark.",
        "- No promotion.",
        "",
        "## Input",
        "",
        f"- manifest: `{args.manifest}`",
        "",
        "## Summary",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| total trainable ready rows | {len(ready_trainable)} |",
        f"| exportable dry-run samples | {len(samples)} |",
        f"| legacy rows needing schema normalization | {len(legacy_needs_normalization)} |",
        "",
        "## Source counts in dry-run samples",
        "",
        "| source | rows |",
        "|---|---:|",
    ]

    for key, value in source_counts.most_common():
        lines.append(f"| {key} | {value} |")

    lines.extend([
        "",
        "## Round2 action counts in dry-run samples",
        "",
        "| action | rows |",
        "|---|---:|",
    ])

    for key, value in round2_action_counts.most_common():
        lines.append(f"| {key} | {value} |")

    lines.extend([
        "",
        "## Suppress candidate count distribution",
        "",
        "| suppress candidate count | rows |",
        "|---|---:|",
    ])

    for key, value in sorted(suppress_count_distribution.items(), key=lambda kv: int(kv[0])):
        lines.append(f"| {key} | {value} |")

    lines.extend([
        "",
        "## Target rank distribution",
        "",
        "| target rank | rows |",
        "|---|---:|",
    ])

    for key, value in sorted(rank_counts.items(), key=lambda kv: int(kv[0])):
        lines.append(f"| {key} | {value} |")

    lines.extend([
        "",
        "## Legacy trainable rows excluded from dry-run export",
        "",
        "| manifest_id | source_class | case_id | reason |",
        "|---|---|---|---|",
    ])

    for r in legacy_needs_normalization:
        lines.append(
            f"| {r.get('manifest_id','')} | {r.get('source_class','')} | {r.get('case_id','')} | missing suppress fields in merged manifest |"
        )

    lines.extend([
        "",
        "## Output",
        "",
        f"- `{args.out_json}`",
        f"- `{args.out_report}`",
        "",
        "## Decision",
        "",
        "This is a schema-validation dry run only.",
        "",
        "Do not train yet.",
        "",
        "Before training, either normalize the 9 legacy trainable rows or deliberately train only on the 35 round2 exportable samples.",
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

    print("manifest_rows:", len(rows))
    print("non_duplicate_rows:", len(nondup))
    print("total_trainable_ready_rows:", len(ready_trainable))
    print("exportable_dryrun_samples:", len(samples))
    print("legacy_needs_schema_normalization:", len(legacy_needs_normalization))
    print("source_counts:", json.dumps(dict(source_counts), sort_keys=True))
    print("round2_action_counts:", json.dumps(dict(round2_action_counts), sort_keys=True))
    print("out_json:", args.out_json)
    print("out_report:", args.out_report)
    print("no training; no checkpoint saved")


if __name__ == "__main__":
    main()
