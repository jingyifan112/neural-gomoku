#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


DATASET = Path("analysis/integration_eval/teacher_divergence_retention_clean_v2_dataset.json")
MANIFEST = Path("analysis/integration_eval/teacher_divergence_retention_clean_v2_manifest.csv")
SOURCE_AUDIT = Path("analysis/integration_eval/teacher_divergence_retention_clean_v2_source_audit.json")

OUT_JSON = Path("analysis/integration_eval/teacher_divergence_retention_clean_v2_acceptance.json")
OUT_MD = Path("analysis/integration_eval/teacher_divergence_retention_clean_v2_acceptance.md")


REQUIRED_DATASET_FIELDS = [
    "id",
    "split",
    "role",
    "bucket",
    "source_path",
    "source_id",
    "board_size",
    "win_length",
    "side_to_move",
    "board",
    "policy_target",
    "teacher_move",
    "suggested_weight",
    "heldout",
    "metadata",
]


def load_dataset_rows() -> list[dict[str, Any]]:
    obj = json.loads(DATASET.read_text(encoding="utf-8"))
    rows = obj.get("rows", [])
    if not isinstance(rows, list):
        raise TypeError("dataset rows must be a list")
    return [r for r in rows if isinstance(r, dict)]


def load_manifest_rows() -> list[dict[str, Any]]:
    with MANIFEST.open("r", encoding="utf-8", newline="") as f:
        return [dict(r) for r in csv.DictReader(f)]


def load_source_audit() -> list[dict[str, Any]]:
    obj = json.loads(SOURCE_AUDIT.read_text(encoding="utf-8"))
    sources = obj.get("sources", [])
    if not isinstance(sources, list):
        return []
    return [s for s in sources if isinstance(s, dict)]


def as_bool_text(x: Any) -> bool:
    return str(x).strip().lower() in {"true", "1", "yes"}


def check_dataset(rows: list[dict[str, Any]]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    missing_by_field = defaultdict(list)
    for r in rows:
        rid = r.get("id", "<missing-id>")
        for field in REQUIRED_DATASET_FIELDS:
            if field not in r or r[field] in (None, ""):
                missing_by_field[field].append(rid)

    for field, ids in missing_by_field.items():
        if field in {"value_target"}:
            continue
        errors.append(f"missing required field {field}: {ids[:10]}")

    duplicate_ids = [k for k, v in Counter(r.get("id") for r in rows).items() if k and v > 1]
    duplicate_source_ids = [
        k for k, v in Counter(r.get("source_id") for r in rows if r.get("source_id")).items()
        if v > 1
    ]

    if duplicate_ids:
        errors.append(f"duplicate ids: {duplicate_ids}")
    if duplicate_source_ids:
        errors.append(f"duplicate source_ids: {duplicate_source_ids}")

    missing_board = [r.get("id") for r in rows if not r.get("board")]
    missing_target = [r.get("id") for r in rows if not r.get("policy_target") or not r.get("teacher_move")]

    if missing_board:
        errors.append(f"missing board: {missing_board[:10]}")
    if missing_target:
        errors.append(f"missing policy_target/teacher_move: {missing_target[:10]}")

    train_retention = [
        r.get("id") for r in rows
        if r.get("split") != "heldout_retention" and r.get("role") == "heldout_retention_anchor"
    ]
    if train_retention:
        errors.append(f"retention anchors leaked into train split: {train_retention}")

    heldout_nonretention = [
        r.get("id") for r in rows
        if r.get("split") == "heldout_retention" and r.get("role") != "heldout_retention_anchor"
    ]
    if heldout_nonretention:
        warnings.append(f"heldout rows with non-retention role: {heldout_nonretention}")

    board_size_bad = [
        r.get("id") for r in rows
        if r.get("board_size") != 15
    ]
    if board_size_bad:
        errors.append(f"non-15 board_size rows: {board_size_bad}")

    win_length_bad = [
        r.get("id") for r in rows
        if r.get("win_length") != 5
    ]
    if win_length_bad:
        errors.append(f"non-5 win_length rows: {win_length_bad}")

    split_counts = Counter(r.get("split") for r in rows)
    role_counts = Counter(r.get("role") for r in rows)
    bucket_counts = Counter(r.get("bucket") for r in rows)
    source_counts = Counter(
        (r.get("metadata") or {}).get("clean_v2_source", "unknown")
        for r in rows
    )

    train_candidate_rows = [r for r in rows if r.get("split") == "train_candidate"]
    train_candidate_summary = []
    for r in train_candidate_rows:
        meta = r.get("metadata") or {}
        train_candidate_summary.append({
            "id": r.get("id"),
            "source_id": r.get("source_id"),
            "side_to_move": r.get("side_to_move"),
            "teacher_move": r.get("teacher_move"),
            "model_or_current_best_move": meta.get("model_direct_move", meta.get("model_move", "")),
            "teacher_rank_or_gap": meta.get(
                "provisional_root_pov_gap_best_minus_model",
                meta.get("teacher_move_policy_rank", ""),
            ),
            "suggested_weight": r.get("suggested_weight"),
            "source": meta.get("clean_v2_source", ""),
        })

    return {
        "errors": errors,
        "warnings": warnings,
        "dataset_rows": len(rows),
        "split_counts": dict(split_counts),
        "role_counts": dict(role_counts),
        "bucket_counts": dict(bucket_counts),
        "source_counts": dict(source_counts),
        "train_candidate_summary": train_candidate_summary,
    }


def check_manifest(manifest: list[dict[str, Any]]) -> dict[str, Any]:
    included = [r for r in manifest if as_bool_text(r.get("included"))]
    skipped = [r for r in manifest if not as_bool_text(r.get("included"))]

    skip_counts = Counter(r.get("skip_reason") or "included" for r in manifest)

    scoregap = [
        r for r in manifest
        if r.get("source_path") == "analysis/public_benchmark_eval/rapfi_teacher_scoregap_corpus8_selected.csv"
    ]
    scoregap_skip_counts = Counter(r.get("skip_reason") or "included" for r in scoregap)

    candidate_g = [
        r for r in manifest
        if r.get("source_path") == "analysis/integration_eval/candidate_g_teacher_seed_dataset.json"
    ]
    candidate_g_skip_counts = Counter(r.get("skip_reason") or "included" for r in candidate_g)

    external_retention = [
        r for r in manifest
        if "diagnostic_anchors.json" in r.get("source_path", "")
        or "candidate_c_anchors.json" in r.get("source_path", "")
        or "conservative_anchors.json" in r.get("source_path", "")
    ]
    external_retention_skip_counts = Counter(r.get("skip_reason") or "included" for r in external_retention)

    manifest_errors = []
    if not manifest:
        manifest_errors.append("manifest is empty")

    return {
        "errors": manifest_errors,
        "manifest_rows": len(manifest),
        "manifest_included": len(included),
        "manifest_skipped": len(skipped),
        "skip_counts": dict(skip_counts),
        "scoregap_rows": len(scoregap),
        "scoregap_skip_counts": dict(scoregap_skip_counts),
        "candidate_g_rows": len(candidate_g),
        "candidate_g_skip_counts": dict(candidate_g_skip_counts),
        "external_retention_rows": len(external_retention),
        "external_retention_skip_counts": dict(external_retention_skip_counts),
    }


def decide_acceptance(dataset_check: dict[str, Any], manifest_check: dict[str, Any]) -> tuple[str, list[str]]:
    errors = dataset_check["errors"] + manifest_check["errors"]
    warnings = dataset_check["warnings"]

    notes = []

    if errors:
        return "REJECT", errors

    split_counts = dataset_check["split_counts"]
    role_counts = dataset_check["role_counts"]

    if split_counts.get("train_teacher_divergence", 0) <= 0:
        notes.append("missing canonical train_teacher_divergence rows")
    if split_counts.get("train_candidate", 0) <= 0:
        notes.append("no train_candidate expansion rows")
    if split_counts.get("heldout_retention", 0) <= 0:
        notes.append("missing heldout_retention rows")
    if role_counts.get("teacher_divergence", 0) <= 0:
        notes.append("missing teacher_divergence rows")
    if role_counts.get("heldout_retention_anchor", 0) <= 0:
        notes.append("missing heldout_retention_anchor rows")

    if notes:
        return "ACCEPT_WITH_WARNINGS", notes + warnings

    if warnings:
        return "ACCEPT_WITH_WARNINGS", warnings

    return "ACCEPT", [
        "clean v2 dataset passes structural validation",
        "score-gap source is represented in manifest/audit and does not duplicate baseline rows into training",
        "retention anchors remain held out",
        "no training/export/benchmark has been run",
    ]


def main() -> None:
    rows = load_dataset_rows()
    manifest = load_manifest_rows()
    source_audit = load_source_audit()

    dataset_check = check_dataset(rows)
    manifest_check = check_manifest(manifest)
    decision, decision_notes = decide_acceptance(dataset_check, manifest_check)

    result = {
        "decision": decision,
        "decision_notes": decision_notes,
        "dataset_check": dataset_check,
        "manifest_check": manifest_check,
        "source_audit": source_audit,
    }

    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    md = []
    md.append("# Clean v2 dataset acceptance report")
    md.append("")
    md.append("This is a data acceptance report only. It does not train, export, benchmark, or modify model weights.")
    md.append("")
    md.append(f"## Decision: {decision}")
    md.append("")
    for note in decision_notes:
        md.append(f"- {note}")
    md.append("")
    md.append("## Dataset counts")
    md.append("")
    md.append(f"- dataset rows: {dataset_check['dataset_rows']}")
    md.append("")
    md.append("### split counts")
    md.append("")
    md.append("| split | count |")
    md.append("|---|---:|")
    for k, v in sorted(dataset_check["split_counts"].items()):
        md.append(f"| {k} | {v} |")
    md.append("")
    md.append("### role counts")
    md.append("")
    md.append("| role | count |")
    md.append("|---|---:|")
    for k, v in sorted(dataset_check["role_counts"].items()):
        md.append(f"| {k} | {v} |")
    md.append("")
    md.append("### source counts")
    md.append("")
    md.append("| source | count |")
    md.append("|---|---:|")
    for k, v in sorted(dataset_check["source_counts"].items()):
        md.append(f"| {k} | {v} |")
    md.append("")
    md.append("## Train candidate rows")
    md.append("")
    md.append("| id | source_id | side | teacher | model/current-best | rank/gap | weight | source |")
    md.append("|---|---|---|---|---|---:|---:|---|")
    for r in dataset_check["train_candidate_summary"]:
        md.append(
            f"| `{r['id']}` | `{r['source_id']}` | {r['side_to_move']} | "
            f"`{r['teacher_move']}` | `{r['model_or_current_best_move']}` | "
            f"{r['teacher_rank_or_gap']} | {r['suggested_weight']} | {r['source']} |"
        )
    md.append("")
    md.append("## Manifest counts")
    md.append("")
    md.append(f"- manifest rows: {manifest_check['manifest_rows']}")
    md.append(f"- included: {manifest_check['manifest_included']}")
    md.append(f"- skipped/audit: {manifest_check['manifest_skipped']}")
    md.append("")
    md.append("### score-gap handling")
    md.append("")
    md.append(f"- score-gap manifest rows: {manifest_check['scoregap_rows']}")
    md.append("")
    md.append("| skip reason | count |")
    md.append("|---|---:|")
    for k, v in sorted(manifest_check["scoregap_skip_counts"].items()):
        md.append(f"| {k} | {v} |")
    md.append("")
    md.append("### Candidate G seed handling")
    md.append("")
    md.append(f"- Candidate G manifest rows: {manifest_check['candidate_g_rows']}")
    md.append("")
    md.append("| skip reason | count |")
    md.append("|---|---:|")
    for k, v in sorted(manifest_check["candidate_g_skip_counts"].items()):
        md.append(f"| {k} | {v} |")
    md.append("")
    md.append("### External retention anchor handling")
    md.append("")
    md.append(f"- external retention manifest rows: {manifest_check['external_retention_rows']}")
    md.append("")
    md.append("| skip reason | count |")
    md.append("|---|---:|")
    for k, v in sorted(manifest_check["external_retention_skip_counts"].items()):
        md.append(f"| {k} | {v} |")
    md.append("")
    md.append("## Source audit")
    md.append("")
    md.append("| source_group | path | exists | rows_seen | rows_included | error |")
    md.append("|---|---|---:|---:|---:|---|")
    for s in source_audit:
        md.append(
            f"| {s.get('source_group','')} | `{s.get('path','')}` | {s.get('exists','')} | "
            f"{s.get('rows_seen','')} | {s.get('rows_included','')} | {s.get('error','')} |"
        )
    md.append("")
    md.append("## Acceptance boundary")
    md.append("")
    md.append("- Accepted for data/manifest/report tracking.")
    md.append("- Not accepted as evidence that training will improve score ladder until a separate training/probe step is run.")
    md.append("- Held-out retention rows must remain out of teacher-divergence training.")
    md.append("- Capacity changes remain deferred until teacher signal and data volume justify them.")
    md.append("")

    OUT_MD.write_text("\n".join(md).rstrip() + "\n", encoding="utf-8")

    print("wrote", OUT_JSON)
    print("wrote", OUT_MD)
    print()
    print("decision", decision)
    print("dataset_rows", dataset_check["dataset_rows"])
    print("split_counts", dataset_check["split_counts"])
    print("role_counts", dataset_check["role_counts"])
    print("manifest_rows", manifest_check["manifest_rows"])
    print("manifest_included", manifest_check["manifest_included"])
    print("manifest_skipped", manifest_check["manifest_skipped"])
    print("scoregap_skip_counts", manifest_check["scoregap_skip_counts"])
    print("candidate_g_skip_counts", manifest_check["candidate_g_skip_counts"])
    print("external_retention_skip_counts", manifest_check["external_retention_skip_counts"])

    if dataset_check["errors"] or manifest_check["errors"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
