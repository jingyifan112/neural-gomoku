#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


REQUIRED_SAMPLE_FIELDS = [
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

LEGACY_IDS = {
    "td_exp_00008",
    "td_exp_00009",
    "td_exp_00013",
    "td_exp_00015",
    "td_exp_00019",
    "td_exp_00021",
    "td_exp_00024",
    "td_exp_00055",
    "td_exp_00058",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit trainer compatibility for legacy-normalized teacher-divergence dry-run dataset."
    )
    parser.add_argument(
        "--dataset-json",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_round2_trainable_dryrun_dataset_legacy_normalized.json"),
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_expanded_candidate_manifest_legacy_suppress_normalized.csv"),
    )
    parser.add_argument(
        "--trainer",
        type=Path,
        default=Path("scripts/train_rapfi_teacher_policy_margin.py"),
    )
    parser.add_argument(
        "--out-summary-csv",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_normalized_trainer_compat_summary.csv"),
    )
    parser.add_argument(
        "--out-report",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_normalized_trainer_compat_audit.md"),
    )
    parser.add_argument("--expected-samples", type=int, default=44)
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


def check_rc(value: Any, field: str, mid: str) -> list[int]:
    if not isinstance(value, list) or len(value) != 2:
        raise ValueError(f"{mid}: {field} must be [row, col], got {value!r}")
    rc = [int(value[0]), int(value[1])]
    if not (0 <= rc[0] < 15 and 0 <= rc[1] < 15):
        raise ValueError(f"{mid}: {field} out of 15x15 range: {rc}")
    return rc


def add_result(results: list[dict[str, str]], item: str, status: str, detail: str) -> None:
    results.append({
        "audit_item": item,
        "status": status,
        "detail": detail,
    })


def trainer_contains(text: str, needle: str) -> bool:
    return needle in text


def trainer_regex(text: str, pattern: str) -> bool:
    return re.search(pattern, text, flags=re.MULTILINE) is not None


def main() -> None:
    args = parse_args()
    results: list[dict[str, str]] = []

    if not args.dataset_json.exists():
        raise FileNotFoundError(args.dataset_json)
    if not args.manifest.exists():
        raise FileNotFoundError(args.manifest)
    if not args.trainer.exists():
        raise FileNotFoundError(args.trainer)

    dataset = json.loads(args.dataset_json.read_text(encoding="utf-8"))
    metadata = dataset.get("metadata", {})
    samples = dataset.get("samples", [])

    if len(samples) == args.expected_samples:
        add_result(results, "dataset_sample_count", "PASS", f"sample_count={len(samples)}")
    else:
        add_result(results, "dataset_sample_count", "FAIL", f"expected={args.expected_samples} actual={len(samples)}")

    if metadata.get("not_training") is True:
        add_result(results, "dataset_not_training_metadata", "PASS", "metadata.not_training is true")
    else:
        add_result(results, "dataset_not_training_metadata", "WARN", "metadata.not_training is not true or missing")

    missing_by_sample: list[tuple[str, list[str]]] = []
    ids: list[str] = []
    legacy_count = 0
    rank_counter: Counter[str] = Counter()
    source_counter: Counter[str] = Counter()
    suppress_candidate_count_counter: Counter[str] = Counter()

    for sample in samples:
        mid = str(sample.get("manifest_id", ""))
        ids.append(mid)
        if mid in LEGACY_IDS:
            legacy_count += 1

        missing = [field for field in REQUIRED_SAMPLE_FIELDS if field not in sample or is_blank(sample.get(field))]
        if missing:
            missing_by_sample.append((mid, missing))
            continue

        target_rc = check_rc(sample["target_rc"], "target_rc", mid)
        suppress_rc = check_rc(sample["suppress_rc"], "suppress_rc", mid)

        if target_rc == suppress_rc:
            raise RuntimeError(f"{mid}: target_rc equals suppress_rc")

        expected_action = target_rc[0] * 15 + target_rc[1]
        actual_action = int(sample["target_action"])
        if expected_action != actual_action:
            raise RuntimeError(f"{mid}: target_action mismatch expected={expected_action} actual={actual_action}")

        rank = int(sample["before_target_rank"])
        if not (11 <= rank <= 50):
            raise RuntimeError(f"{mid}: before_target_rank outside trainable range: {rank}")
        rank_counter[str(rank)] += 1

        current_player = int(sample["current_player"])
        if current_player not in {-1, 1}:
            raise RuntimeError(f"{mid}: current_player must be -1 or 1, got {current_player}")

        candidates_rcs = sample["suppress_candidates_rcs"]
        candidates_probs = sample["suppress_candidates_probs"]
        if not isinstance(candidates_rcs, list) or not candidates_rcs:
            raise RuntimeError(f"{mid}: empty suppress_candidates_rcs")
        if not isinstance(candidates_probs, list) or not candidates_probs:
            raise RuntimeError(f"{mid}: empty suppress_candidates_probs")
        if len(candidates_rcs) != len(candidates_probs):
            raise RuntimeError(f"{mid}: suppress candidate rcs/probs length mismatch")

        suppress_candidate_count_counter[str(len(candidates_rcs))] += 1
        source_counter[str(sample.get("source_class") or sample.get("primary_source_path") or "")] += 1

    if missing_by_sample:
        add_result(results, "dataset_required_sample_fields", "FAIL", json.dumps(missing_by_sample[:20], sort_keys=True))
    else:
        add_result(results, "dataset_required_sample_fields", "PASS", f"all {len(samples)} samples contain required single-suppress fields")

    if len(ids) == len(set(ids)):
        add_result(results, "dataset_manifest_id_unique", "PASS", f"unique_ids={len(set(ids))}")
    else:
        add_result(results, "dataset_manifest_id_unique", "FAIL", "duplicate manifest_id found in samples")

    if legacy_count == 9:
        add_result(results, "legacy_rows_in_dataset", "PASS", "all 9 legacy-normalized rows are present")
    else:
        add_result(results, "legacy_rows_in_dataset", "FAIL", f"expected 9 legacy rows, got {legacy_count}")

    fields, manifest_rows = read_csv(args.manifest)
    nondup = [r for r in manifest_rows if is_blank(r.get("duplicate_of"))]
    ready_trainable = [
        r for r in nondup
        if r.get("status") == "ready_full_schema"
        and ready_bucket(r) == "trainable_rank_11_50"
    ]

    manifest_ids = {r.get("manifest_id", "") for r in ready_trainable}
    sample_ids = set(ids)

    if len(ready_trainable) == args.expected_samples:
        add_result(results, "manifest_trainable_ready_count", "PASS", f"trainable_ready={len(ready_trainable)}")
    else:
        add_result(results, "manifest_trainable_ready_count", "FAIL", f"expected={args.expected_samples} actual={len(ready_trainable)}")

    if sample_ids == manifest_ids:
        add_result(results, "dataset_manifest_id_match", "PASS", "dataset sample IDs exactly match manifest trainable ready IDs")
    else:
        add_result(
            results,
            "dataset_manifest_id_match",
            "FAIL",
            f"missing_from_dataset={sorted(manifest_ids - sample_ids)} extra_in_dataset={sorted(sample_ids - manifest_ids)}",
        )

    trainer_text = args.trainer.read_text(encoding="utf-8")

    trainer_checks = [
        ("trainer_has_samples_loader", trainer_contains(trainer_text, "samples")),
        ("trainer_references_target_rc", trainer_contains(trainer_text, "target_rc")),
        ("trainer_references_suppress_rc", trainer_contains(trainer_text, "suppress_rc")),
        ("trainer_has_margin_tensor_builder", trainer_contains(trainer_text, "make_margin_tensors") or trainer_contains(trainer_text, "target_action")),
        ("trainer_looks_single_suppress", trainer_contains(trainer_text, "suppress_rc") and not trainer_contains(trainer_text, "suppress_candidates_rcs")),
        ("trainer_has_checkpoint_output_arg", trainer_regex(trainer_text, r"out[_-]checkpoint|checkpoint")),
        ("trainer_has_metrics_or_logging", trainer_regex(trainer_text, r"metrics|loss|csv|json")),
    ]

    for item, ok in trainer_checks:
        add_result(results, item, "PASS" if ok else "WARN", "found expected trainer marker" if ok else "expected marker not found; inspect trainer manually")

    if "suppress_candidates_rcs" not in trainer_text:
        add_result(
            results,
            "multi_suppress_not_consumed",
            "PASS",
            "trainer appears compatible with one suppress_rc per sample; suppress_candidates can remain audit metadata",
        )
    else:
        add_result(
            results,
            "multi_suppress_not_consumed",
            "WARN",
            "trainer references suppress_candidates_rcs; verify whether it expects multi-suppress schema",
        )

    proposed_checkpoint = "checkpoints/15x15_teacher_divergence_round2_policy_margin_probe.pt"
    proposed_metrics = "analysis/integration_eval/teacher_divergence_round2_policy_margin_probe_train_metrics.csv"

    if proposed_checkpoint != "checkpoints/15x15_current_best.pt":
        add_result(results, "safe_checkpoint_path", "PASS", proposed_checkpoint)
    else:
        add_result(results, "safe_checkpoint_path", "FAIL", "proposed checkpoint would overwrite current_best")

    add_result(results, "safe_metrics_path", "PASS", proposed_metrics)
    add_result(results, "protected_top10_excluded", "PASS", "dataset selects only trainable_rank_11_50")
    add_result(results, "tail_rank_gt50_excluded", "PASS", "dataset selects only trainable_rank_11_50")
    add_result(results, "no_training_executed", "PASS", "audit only; no trainer invocation")

    status_counter = Counter(r["status"] for r in results)
    if status_counter["FAIL"]:
        failed = [r for r in results if r["status"] == "FAIL"]
        raise RuntimeError(f"compat audit found FAIL rows: {failed}")

    args.out_summary_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.out_summary_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["audit_item", "status", "detail"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(results)

    lines = [
        "# Teacher-divergence normalized trainer compatibility audit",
        "",
        "## Branch",
        "",
        "`exp/15x15-teacher-divergence-normalized-trainer-compat-audit`",
        "",
        "## Scope",
        "",
        "- Audits compatibility between the 44-row legacy-normalized dry-run dataset and the existing policy-margin trainer.",
        "- Confirms the dataset uses single-suppress schema: one `target_rc` and one `suppress_rc` per sample.",
        "- Confirms protected top10 and tail rank > 50 rows are excluded from the trainable dry-run dataset.",
        "- Proposes isolated output paths for a later tiny training probe.",
        "- Does not train.",
        "- Does not save a checkpoint.",
        "- Does not C export.",
        "- Does not run public benchmark.",
        "- Does not promote.",
        "",
        "## Inputs",
        "",
        f"- dataset JSON: `{args.dataset_json}`",
        f"- normalized manifest: `{args.manifest}`",
        f"- trainer: `{args.trainer}`",
        "",
        "## Summary",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| dataset samples | {len(samples)} |",
        f"| legacy-normalized samples | {legacy_count} |",
        f"| manifest trainable ready rows | {len(ready_trainable)} |",
        f"| audit PASS | {status_counter.get('PASS', 0)} |",
        f"| audit WARN | {status_counter.get('WARN', 0)} |",
        f"| audit FAIL | {status_counter.get('FAIL', 0)} |",
        "",
        "## Audit results",
        "",
        "| audit_item | status | detail |",
        "|---|---|---|",
    ]

    for result in results:
        detail = result["detail"].replace("|", "\\|")
        lines.append(f"| {result['audit_item']} | {result['status']} | {detail} |")

    lines.extend([
        "",
        "## Source counts",
        "",
        "| source | rows |",
        "|---|---:|",
    ])

    for key, value in source_counter.most_common():
        lines.append(f"| {key} | {value} |")

    lines.extend([
        "",
        "## Suppress candidate count distribution",
        "",
        "| suppress candidate count | rows |",
        "|---|---:|",
    ])

    for key, value in sorted(suppress_candidate_count_counter.items(), key=lambda kv: int(kv[0])):
        lines.append(f"| {key} | {value} |")

    lines.extend([
        "",
        "## Target rank distribution",
        "",
        "| target rank | rows |",
        "|---|---:|",
    ])

    for key, value in sorted(rank_counter.items(), key=lambda kv: int(kv[0])):
        lines.append(f"| {key} | {value} |")

    lines.extend([
        "",
        "## Later training probe constraints",
        "",
        "Use isolated output paths only:",
        "",
        f"- checkpoint: `{proposed_checkpoint}`",
        f"- metrics: `{proposed_metrics}`",
        "",
        "Do not overwrite `checkpoints/15x15_current_best.pt`.",
        "",
        "Do not export C weights from this probe.",
        "",
        "Do not run public benchmark from this probe.",
        "",
        "Do not promote this probe unless a later validation branch explicitly supports it.",
        "",
        "## Recommended next step",
        "",
        "Run a tiny training dry-run/probe branch only after this compatibility audit is pushed. The first training probe should be intentionally small and isolated, with a new checkpoint path and metrics path.",
        "",
        "## Outputs",
        "",
        f"- `{args.out_summary_csv}`",
        f"- `{args.out_report}`",
        "",
        "## Decision",
        "",
        "Compatibility audit only.",
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

    print("dataset_samples:", len(samples))
    print("legacy_normalized_samples:", legacy_count)
    print("manifest_trainable_ready_rows:", len(ready_trainable))
    print("audit_status_counts:", json.dumps(dict(status_counter), sort_keys=True))
    print("source_counts:", json.dumps(dict(source_counter), sort_keys=True))
    print("suppress_candidate_count_distribution:", json.dumps(dict(suppress_candidate_count_counter), sort_keys=True))
    print("out_summary_csv:", args.out_summary_csv)
    print("out_report:", args.out_report)
    print("no training; no checkpoint saved")


if __name__ == "__main__":
    main()
