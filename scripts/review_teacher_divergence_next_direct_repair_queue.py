#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Review direct manifest repair queue rows without eval/training/checkpoint reads."
    )
    p.add_argument(
        "--normalized-manifest",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_next_direct_manifest_normalization_review_manifest.csv"),
    )
    p.add_argument(
        "--repair-queue",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_next_direct_manifest_normalization_review_repair_queue.csv"),
    )
    p.add_argument(
        "--quarantine",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_next_direct_manifest_normalization_review_quarantine.csv"),
    )
    p.add_argument(
        "--normalization-summary",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_next_direct_manifest_normalization_review_summary.csv"),
    )
    p.add_argument(
        "--normalization-decision-json",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_next_direct_manifest_normalization_review_decision.json"),
    )
    p.add_argument(
        "--inspection-rows",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_next_direct_adapter_blocker_inspection_rows.csv"),
    )
    p.add_argument(
        "--combined-summary",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_local_comparison_executor_dryrun_combined_summary.csv"),
    )
    p.add_argument(
        "--candidate-checkpoint",
        type=Path,
        default=Path("checkpoints/15x15_teacher_divergence_round2_policy_margin_gated_run1_e10.pt"),
    )
    p.add_argument(
        "--current-best-checkpoint",
        type=Path,
        default=Path("checkpoints/15x15_current_best.pt"),
    )
    p.add_argument(
        "--out-review-rows",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_next_direct_repair_queue_review_rows.csv"),
    )
    p.add_argument(
        "--out-repair-candidates",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_next_direct_repair_queue_review_candidates.csv"),
    )
    p.add_argument(
        "--out-pending",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_next_direct_repair_queue_review_pending.csv"),
    )
    p.add_argument(
        "--out-quarantine-additions",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_next_direct_repair_queue_review_quarantine_additions.csv"),
    )
    p.add_argument(
        "--out-summary-csv",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_next_direct_repair_queue_review_summary.csv"),
    )
    p.add_argument(
        "--out-decision-json",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_next_direct_repair_queue_review_decision.json"),
    )
    p.add_argument(
        "--out-report",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_next_direct_repair_queue_review.md"),
    )
    return p.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def by_metric(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {r["metric"]: r for r in rows}


def get(m: dict[str, dict[str, str]], key: str, default: str = "") -> str:
    return m.get(key, {}).get("value", default)


def as_int(value: Any) -> int:
    if value in ("", None):
        return 0
    return int(float(value))


def as_float(value: Any) -> float:
    if value in ("", None):
        return 0.0
    return float(value)


def metric_from_combined(rows: list[dict[str, str]], metric: str, default: str = "") -> str:
    for r in rows:
        if r.get("metric") == metric:
            return r.get("value", default)
    return default


def row(metric: str, value: Any, status: str, notes: str = "") -> dict[str, str]:
    return {
        "metric": metric,
        "value": str(value),
        "status": status,
        "notes": notes,
    }


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def esc(value: Any) -> str:
    return str(value).replace("|", "\\|")


def find_inspection_row(inspection_rows: list[dict[str, str]], source_manifest_row_id: str) -> dict[str, str]:
    for r in inspection_rows:
        if r.get("manifest_row_id") == source_manifest_row_id:
            return r
    return {}


def review_repair_row(r: dict[str, str], inspection: dict[str, str]) -> dict[str, str]:
    source_path = r.get("source_path", "")
    p = Path(source_path) if source_path else Path("__missing_path__")
    path_exists = p.exists()

    schema_status = r.get("schema_status", "")
    provenance_status = r.get("provenance_status", "")
    leakage_risk = r.get("leakage_risk", "")
    direct_eval_readiness = r.get("direct_eval_readiness", "")
    recommended_action = r.get("recommended_action", "")
    problems = r.get("problems", "")

    problem_set = {x for x in problems.split(";") if x}

    hard_quarantine_reasons: list[str] = []
    pending_reasons: list[str] = []
    candidate_reasons: list[str] = []

    if not source_path:
        hard_quarantine_reasons.append("missing_source_path")
    if not path_exists:
        hard_quarantine_reasons.append("source_path_missing")
    if "source_parse_error" in problem_set:
        hard_quarantine_reasons.append("source_parse_error")
    if "train_derived_artifact" in problem_set:
        hard_quarantine_reasons.append("train_derived_artifact")
    if "debug_or_legacy_artifact" in problem_set:
        hard_quarantine_reasons.append("debug_or_legacy_artifact")
    if provenance_status in {"TRAIN_DERIVED_SOURCE", "DEBUG_OR_LEGACY_SOURCE"}:
        hard_quarantine_reasons.append(f"unsafe_provenance:{provenance_status}")
    if leakage_risk == "HIGH":
        hard_quarantine_reasons.append("high_leakage_risk")

    if schema_status in {"INCOMPLETE", ""}:
        pending_reasons.append(f"schema_needs_repair:{schema_status or 'missing'}")
    if provenance_status in {"UNKNOWN", "ROUTE_DERIVED_ONLY", ""}:
        pending_reasons.append(f"provenance_needs_repair:{provenance_status or 'missing'}")
    if direct_eval_readiness != "NEEDS_REPAIR":
        pending_reasons.append(f"unexpected_readiness:{direct_eval_readiness}")

    if (
        path_exists
        and schema_status in {"OK", "HAS_CONTEXT_BUT_NEEDS_REVIEW"}
        and provenance_status == "CLEAN_HELDOUT_OR_DIRECT_SOURCE"
        and leakage_risk == "LOW"
        and not hard_quarantine_reasons
    ):
        candidate_reasons.append("clean_low_risk_row_after_review")

    if hard_quarantine_reasons:
        repair_review_decision = "REPAIR_ROW_QUARANTINE"
        repair_review_bucket = "quarantine"
        next_action = "Move this row to quarantine; do not normalize."
    elif candidate_reasons:
        repair_review_decision = "REPAIR_ROW_CAN_NORMALIZE_AFTER_METADATA_PATCH"
        repair_review_bucket = "candidate"
        next_action = "Can be added as a review-only normalized candidate with eval disabled."
    elif pending_reasons:
        repair_review_decision = "REPAIR_ROW_STILL_PENDING"
        repair_review_bucket = "pending"
        next_action = "Keep pending until schema/provenance metadata is repaired."
    else:
        repair_review_decision = "REPAIR_ROW_MANUAL_REVIEW"
        repair_review_bucket = "pending"
        next_action = "Manual review required before any normalization."

    return {
        "repair_queue_id": r.get("repair_queue_id", ""),
        "source_manifest_row_id": r.get("source_manifest_row_id", ""),
        "source_eval_manifest_id": r.get("source_eval_manifest_id", ""),
        "source_adapter_kind": r.get("source_adapter_kind", ""),
        "source_path": source_path,
        "source_path_exists": "1" if path_exists else "0",
        "schema_status": schema_status,
        "provenance_status": provenance_status,
        "leakage_risk": leakage_risk,
        "direct_eval_readiness": direct_eval_readiness,
        "original_recommended_action": recommended_action,
        "problems": problems,
        "inspection_risk_level": inspection.get("risk_level", ""),
        "inspection_route_tokens": inspection.get("route_tokens", ""),
        "inspection_clean_source_tokens": inspection.get("clean_source_tokens", ""),
        "repair_review_decision": repair_review_decision,
        "repair_review_bucket": repair_review_bucket,
        "candidate_reasons": ";".join(candidate_reasons),
        "pending_reasons": ";".join(pending_reasons),
        "quarantine_reasons": ";".join(hard_quarantine_reasons),
        "next_action": next_action,
        "eval_allowed_now": "0",
        "checkpoint_read_allowed_now": "0",
        "notes": "repair queue review only; no model eval or checkpoint read",
    }


def candidate_from_review(r: dict[str, str], idx: int) -> dict[str, str]:
    return {
        "repair_candidate_id": f"direct_repair_candidate_{idx:03d}",
        "source_repair_queue_id": r["repair_queue_id"],
        "source_manifest_row_id": r["source_manifest_row_id"],
        "source_eval_manifest_id": r["source_eval_manifest_id"],
        "source_adapter_kind": r["source_adapter_kind"],
        "source_path": r["source_path"],
        "schema_status": r["schema_status"],
        "provenance_status": r["provenance_status"],
        "leakage_risk": r["leakage_risk"],
        "review_status": "CANDIDATE_AFTER_METADATA_PATCH",
        "eval_allowed_now": "0",
        "requires_future_explicit_flags": "1",
        "checkpoint_read_allowed_now": "0",
        "notes": "Not merged into normalized manifest in this branch.",
    }


def pending_from_review(r: dict[str, str], idx: int) -> dict[str, str]:
    return {
        "pending_id": f"direct_repair_pending_{idx:03d}",
        "source_repair_queue_id": r["repair_queue_id"],
        "source_manifest_row_id": r["source_manifest_row_id"],
        "source_eval_manifest_id": r["source_eval_manifest_id"],
        "source_path": r["source_path"],
        "schema_status": r["schema_status"],
        "provenance_status": r["provenance_status"],
        "leakage_risk": r["leakage_risk"],
        "pending_reasons": r["pending_reasons"],
        "next_action": r["next_action"],
        "eval_allowed_now": "0",
        "notes": "Needs metadata repair before any normalization.",
    }


def quarantine_from_review(r: dict[str, str], idx: int) -> dict[str, str]:
    return {
        "quarantine_addition_id": f"direct_repair_quarantine_{idx:03d}",
        "source_repair_queue_id": r["repair_queue_id"],
        "source_manifest_row_id": r["source_manifest_row_id"],
        "source_eval_manifest_id": r["source_eval_manifest_id"],
        "source_path": r["source_path"],
        "schema_status": r["schema_status"],
        "provenance_status": r["provenance_status"],
        "leakage_risk": r["leakage_risk"],
        "quarantine_reasons": r["quarantine_reasons"],
        "eval_allowed_now": "0",
        "notes": "Excluded from normalized direct manifest.",
    }


def main() -> None:
    args = parse_args()

    for p in [
        args.normalized_manifest,
        args.repair_queue,
        args.quarantine,
        args.normalization_summary,
        args.normalization_decision_json,
        args.inspection_rows,
        args.combined_summary,
        args.current_best_checkpoint,
    ]:
        if not p.exists():
            raise FileNotFoundError(p)

    normalized = read_csv(args.normalized_manifest)
    repair_queue = read_csv(args.repair_queue)
    quarantine_existing = read_csv(args.quarantine)
    normalization_summary = by_metric(read_csv(args.normalization_summary))
    normalization_decision = json.loads(args.normalization_decision_json.read_text(encoding="utf-8"))
    inspection_rows = read_csv(args.inspection_rows)
    combined = read_csv(args.combined_summary)

    normalization_decision_value = get(normalization_summary, "normalization_decision")
    expected_repair_rows = as_int(get(normalization_summary, "repair_queue_rows"))
    expected_normalized_rows = as_int(get(normalization_summary, "normalized_ready_rows"))
    expected_quarantine_rows = as_int(get(normalization_summary, "quarantine_rows"))

    candidate_exists = args.candidate_checkpoint.exists()
    current_best_exists = args.current_best_checkpoint.exists()

    review_rows = []
    for r in repair_queue:
        inspection = find_inspection_row(inspection_rows, r.get("source_manifest_row_id", ""))
        review_rows.append(review_repair_row(r, inspection))

    repair_candidates = [
        candidate_from_review(r, i)
        for i, r in enumerate([x for x in review_rows if x["repair_review_bucket"] == "candidate"], start=1)
    ]
    pending_rows = [
        pending_from_review(r, i)
        for i, r in enumerate([x for x in review_rows if x["repair_review_bucket"] == "pending"], start=1)
    ]
    quarantine_additions = [
        quarantine_from_review(r, i)
        for i, r in enumerate([x for x in review_rows if x["repair_review_bucket"] == "quarantine"], start=1)
    ]

    combined_fail_rows = [r for r in combined if r.get("status") == "FAIL"]
    combined_warn_rows = [r for r in combined if r.get("status") == "WARN"]

    trainable_gap_improved = as_int(metric_from_combined(combined, "gap_improved_rows"))
    trainable_rank_regressed = as_int(metric_from_combined(combined, "target_rank_regressed_rows"))
    protected_rank_regressed = as_int(metric_from_combined(combined, "protected_top10_rank_regressed_rows"))
    protected_prob_regressed = as_int(metric_from_combined(combined, "protected_top10_prob_regressed_rows"))
    tail_rank_regressed = as_int(metric_from_combined(combined, "tail_rank_gt50_rank_regressed_rows"))
    tail_prob_regressed = as_int(metric_from_combined(combined, "tail_rank_gt50_prob_regressed_rows"))
    anchor_top1_changed = as_int(metric_from_combined(combined, "anchor_top1_changed_rows"))
    anchor_max_kl = as_float(metric_from_combined(combined, "anchor_max_kl"))

    blockers: list[str] = []
    warnings: list[str] = []

    if normalization_decision_value not in {
        "DIRECT_MANIFEST_NORMALIZATION_REVIEW_READY_WITH_REPAIR_QUEUE",
        "DIRECT_MANIFEST_NORMALIZATION_REVIEW_READY",
    }:
        blockers.append(f"normalization decision not ready: {normalization_decision_value}")
    if len(repair_queue) != expected_repair_rows:
        blockers.append(f"repair queue row mismatch: csv={len(repair_queue)} summary={expected_repair_rows}")
    if len(normalized) != expected_normalized_rows:
        blockers.append(f"normalized row mismatch: csv={len(normalized)} summary={expected_normalized_rows}")
    if len(quarantine_existing) != expected_quarantine_rows:
        blockers.append(f"quarantine row mismatch: csv={len(quarantine_existing)} summary={expected_quarantine_rows}")
    if not current_best_exists:
        blockers.append("current_best checkpoint path missing")
    if combined_fail_rows:
        blockers.append(f"combined FAIL rows present: {len(combined_fail_rows)}")
    if trainable_gap_improved != 44:
        blockers.append(f"trainable gap improved rows not 44: {trainable_gap_improved}")
    if trainable_rank_regressed > 0:
        blockers.append(f"trainable rank regressions present: {trainable_rank_regressed}")
    if protected_rank_regressed > 0:
        blockers.append(f"protected rank regressions present: {protected_rank_regressed}")
    if tail_rank_regressed > 0:
        blockers.append(f"tail rank regressions present: {tail_rank_regressed}")
    if anchor_top1_changed > 0:
        blockers.append(f"anchor top1 changes present: {anchor_top1_changed}")
    if anchor_max_kl > 0.005:
        blockers.append(f"anchor max KL too high: {anchor_max_kl:.10f}")

    for key in [
        "would_train_now",
        "would_eval_model_now",
        "would_read_checkpoint_contents_now",
        "would_write_checkpoint",
        "would_c_export",
        "would_public_benchmark",
        "would_promote",
    ]:
        if bool(normalization_decision.get(key)):
            blockers.append(f"normalization safety flag unexpectedly true: {key}")

    if not candidate_exists:
        warnings.append("candidate checkpoint missing locally; no checkpoint read needed for repair review")
    if combined_warn_rows:
        warnings.append(f"combined WARN rows carried forward: {len(combined_warn_rows)}")
    if protected_prob_regressed:
        warnings.append(f"protected probability regressions carried forward: {protected_prob_regressed}")
    if tail_prob_regressed:
        warnings.append(f"tail probability regressions carried forward: {tail_prob_regressed}")
    if repair_candidates:
        warnings.append(f"repair candidates found but not merged in this branch: {len(repair_candidates)}")
    if pending_rows:
        warnings.append(f"repair rows still pending: {len(pending_rows)}")
    if quarantine_additions:
        warnings.append(f"repair rows moved to quarantine additions: {len(quarantine_additions)}")

    if blockers:
        review_decision = "DIRECT_REPAIR_QUEUE_REVIEW_BLOCKED"
        recommended_next = "Fix hard blockers before any repair queue action."
    elif repair_candidates:
        review_decision = "DIRECT_REPAIR_QUEUE_REVIEW_HAS_CANDIDATE_PATCHES"
        recommended_next = "Create a metadata patch branch for repair candidates; keep eval disabled."
    elif pending_rows:
        review_decision = "DIRECT_REPAIR_QUEUE_REVIEW_PENDING_METADATA"
        recommended_next = "Do not merge repair row yet; materialize missing schema/provenance metadata first."
    elif quarantine_additions:
        review_decision = "DIRECT_REPAIR_QUEUE_REVIEW_QUARANTINE_ADDITIONS"
        recommended_next = "Add quarantine additions and proceed with the existing 3-row normalized manifest only."
    else:
        review_decision = "DIRECT_REPAIR_QUEUE_REVIEW_EMPTY"
        recommended_next = "No repair rows to process; continue with existing normalized manifest."

    review_fieldnames = [
        "repair_queue_id",
        "source_manifest_row_id",
        "source_eval_manifest_id",
        "source_adapter_kind",
        "source_path",
        "source_path_exists",
        "schema_status",
        "provenance_status",
        "leakage_risk",
        "direct_eval_readiness",
        "original_recommended_action",
        "problems",
        "inspection_risk_level",
        "inspection_route_tokens",
        "inspection_clean_source_tokens",
        "repair_review_decision",
        "repair_review_bucket",
        "candidate_reasons",
        "pending_reasons",
        "quarantine_reasons",
        "next_action",
        "eval_allowed_now",
        "checkpoint_read_allowed_now",
        "notes",
    ]
    candidate_fieldnames = [
        "repair_candidate_id",
        "source_repair_queue_id",
        "source_manifest_row_id",
        "source_eval_manifest_id",
        "source_adapter_kind",
        "source_path",
        "schema_status",
        "provenance_status",
        "leakage_risk",
        "review_status",
        "eval_allowed_now",
        "requires_future_explicit_flags",
        "checkpoint_read_allowed_now",
        "notes",
    ]
    pending_fieldnames = [
        "pending_id",
        "source_repair_queue_id",
        "source_manifest_row_id",
        "source_eval_manifest_id",
        "source_path",
        "schema_status",
        "provenance_status",
        "leakage_risk",
        "pending_reasons",
        "next_action",
        "eval_allowed_now",
        "notes",
    ]
    quarantine_fieldnames = [
        "quarantine_addition_id",
        "source_repair_queue_id",
        "source_manifest_row_id",
        "source_eval_manifest_id",
        "source_path",
        "schema_status",
        "provenance_status",
        "leakage_risk",
        "quarantine_reasons",
        "eval_allowed_now",
        "notes",
    ]

    write_csv(args.out_review_rows, review_rows, review_fieldnames)
    write_csv(args.out_repair_candidates, repair_candidates, candidate_fieldnames)
    write_csv(args.out_pending, pending_rows, pending_fieldnames)
    write_csv(args.out_quarantine_additions, quarantine_additions, quarantine_fieldnames)

    summary_rows = [
        row("repair_queue_review_decision", review_decision, "INFO", "Review only; no eval."),
        row("recommended_next", recommended_next, "INFO"),
        row("normalization_decision", normalization_decision_value, "INFO"),
        row("normalized_manifest_rows", len(normalized), "INFO"),
        row("repair_queue_rows", len(repair_queue), "INFO"),
        row("existing_quarantine_rows", len(quarantine_existing), "INFO"),
        row("reviewed_repair_rows", len(review_rows), "INFO"),
        row("repair_candidate_rows", len(repair_candidates), "INFO"),
        row("pending_rows", len(pending_rows), "WARN" if pending_rows else "PASS"),
        row("quarantine_addition_rows", len(quarantine_additions), "WARN" if quarantine_additions else "PASS"),
        row("blocker_count", len(blockers), "PASS" if not blockers else "FAIL", "; ".join(blockers)),
        row("warning_count", len(warnings), "WARN" if warnings else "PASS", "; ".join(warnings)),
        row("candidate_checkpoint_exists_locally", int(candidate_exists), "INFO", "Existence only; no checkpoint read."),
        row("current_best_exists", int(current_best_exists), "PASS" if current_best_exists else "FAIL"),
        row("combined_fail_rows", len(combined_fail_rows), "PASS" if not combined_fail_rows else "FAIL"),
        row("combined_warn_rows", len(combined_warn_rows), "WARN" if combined_warn_rows else "PASS"),
        row("trainable_gap_improved", trainable_gap_improved, "PASS" if trainable_gap_improved == 44 else "FAIL"),
        row("trainable_rank_regressed", trainable_rank_regressed, "PASS" if trainable_rank_regressed == 0 else "FAIL"),
        row("protected_rank_regressed", protected_rank_regressed, "PASS" if protected_rank_regressed == 0 else "FAIL"),
        row("tail_rank_regressed", tail_rank_regressed, "PASS" if tail_rank_regressed == 0 else "WARN"),
        row("protected_prob_regressed", protected_prob_regressed, "WARN" if protected_prob_regressed else "PASS"),
        row("tail_prob_regressed", tail_prob_regressed, "WARN" if tail_prob_regressed else "PASS"),
        row("anchor_top1_changed", anchor_top1_changed, "PASS" if anchor_top1_changed == 0 else "FAIL"),
        row("anchor_max_kl", f"{anchor_max_kl:.10f}", "PASS" if anchor_max_kl <= 0.005 else "FAIL"),
        row("would_train", 0, "PASS"),
        row("would_eval_model_now", 0, "PASS"),
        row("would_read_checkpoint_contents_now", 0, "PASS"),
        row("would_write_checkpoint", 0, "PASS"),
        row("would_c_export", 0, "PASS"),
        row("would_public_benchmark", 0, "PASS"),
        row("would_promote", 0, "PASS"),
    ]
    write_csv(args.out_summary_csv, summary_rows, ["metric", "value", "status", "notes"])

    decision = {
        "repair_queue_review_decision": review_decision,
        "recommended_next": recommended_next,
        "normalization_decision": normalization_decision_value,
        "would_train_now": False,
        "would_eval_model_now": False,
        "would_read_checkpoint_contents_now": False,
        "would_write_checkpoint": False,
        "would_c_export": False,
        "would_public_benchmark": False,
        "would_promote": False,
        "row_counts": {
            "normalized_manifest_rows": len(normalized),
            "repair_queue_rows": len(repair_queue),
            "existing_quarantine_rows": len(quarantine_existing),
            "reviewed_repair_rows": len(review_rows),
            "repair_candidate_rows": len(repair_candidates),
            "pending_rows": len(pending_rows),
            "quarantine_addition_rows": len(quarantine_additions),
        },
        "outputs": {
            "review_rows": str(args.out_review_rows),
            "repair_candidates": str(args.out_repair_candidates),
            "pending": str(args.out_pending),
            "quarantine_additions": str(args.out_quarantine_additions),
            "summary_csv": str(args.out_summary_csv),
            "report": str(args.out_report),
        },
        "blockers": blockers,
        "warnings": warnings,
    }
    args.out_decision_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_decision_json.write_text(json.dumps(decision, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    report = [
        "# Teacher-divergence next direct repair queue review",
        "",
        "## Branch",
        "",
        "`exp/15x15-teacher-divergence-next-direct-repair-queue-review`",
        "",
        "## Scope",
        "",
        "- Reviews repair queue rows from direct manifest normalization.",
        "- Does not merge any repair row into the normalized manifest.",
        "- Does not train.",
        "- Does not run model eval.",
        "- Does not read checkpoint contents.",
        "- Does not write checkpoints.",
        "- Does not overwrite `checkpoints/15x15_current_best.pt`.",
        "- Does not C export.",
        "- Does not run public benchmark.",
        "- Does not promote.",
        "",
        "## Repair queue review decision",
        "",
        f"`{review_decision}`",
        "",
        "## Recommended next",
        "",
        recommended_next,
        "",
        "## Row split",
        "",
        "| bucket | rows |",
        "|---|---:|",
        f"| normalized_manifest_rows | {len(normalized)} |",
        f"| repair_queue_rows | {len(repair_queue)} |",
        f"| repair_candidate_rows | {len(repair_candidates)} |",
        f"| pending_rows | {len(pending_rows)} |",
        f"| quarantine_addition_rows | {len(quarantine_additions)} |",
        "",
        "## Review rows",
        "",
        "| repair_queue_id | source_manifest_row_id | source_eval_manifest_id | path_exists | schema | provenance | leakage | decision | bucket | next_action |",
        "|---|---:|---|---:|---|---|---|---|---|---|",
    ]

    for r in review_rows:
        report.append(
            f"| {esc(r['repair_queue_id'])} | {esc(r['source_manifest_row_id'])} | {esc(r['source_eval_manifest_id'])} | {esc(r['source_path_exists'])} | {esc(r['schema_status'])} | {esc(r['provenance_status'])} | {esc(r['leakage_risk'])} | {esc(r['repair_review_decision'])} | {esc(r['repair_review_bucket'])} | {esc(r['next_action'])} |"
        )

    report.extend([
        "",
        "## Summary",
        "",
        "| metric | value | status | notes |",
        "|---|---:|---|---|",
    ])
    for r in summary_rows:
        report.append(f"| {esc(r['metric'])} | {esc(r['value'])} | {esc(r['status'])} | {esc(r['notes'])} |")

    report.extend(["", "## Blockers", ""])
    if blockers:
        report.extend([f"- {b}" for b in blockers])
    else:
        report.append("- None.")

    report.extend(["", "## Warnings", ""])
    if warnings:
        report.extend([f"- {w}" for w in warnings])
    else:
        report.append("- None.")

    report.extend([
        "",
        "## Interpretation",
        "",
    ])
    if review_decision == "DIRECT_REPAIR_QUEUE_REVIEW_HAS_CANDIDATE_PATCHES":
        report.append("At least one repair row might be promotable after an explicit metadata patch. It is not merged here.")
    elif review_decision == "DIRECT_REPAIR_QUEUE_REVIEW_PENDING_METADATA":
        report.append("Repair row remains pending. The next safe step is metadata materialization, not eval.")
    elif review_decision == "DIRECT_REPAIR_QUEUE_REVIEW_QUARANTINE_ADDITIONS":
        report.append("Repair row should be moved to quarantine additions. Continue with the existing normalized manifest only.")
    else:
        report.append("Do not proceed until blockers or empty-state implications are reviewed.")

    report.extend([
        "",
        "## Final guardrails",
        "",
        "- No repair row is merged into the normalized manifest in this branch.",
        "- `eval_allowed_now` is 0 for all output rows.",
        "- Keep the run1 candidate checkpoint isolated.",
        "- No current_best overwrite.",
        "- No C export.",
        "- No public benchmark.",
        "- No promotion.",
        "- Do not add local checkpoint artifacts to git.",
        "",
    ])

    args.out_report.parent.mkdir(parents=True, exist_ok=True)
    args.out_report.write_text("\n".join(report), encoding="utf-8")

    print("repair_queue_review_decision:", review_decision)
    print("recommended_next:", recommended_next)
    print("normalized_manifest_rows:", len(normalized))
    print("repair_queue_rows:", len(repair_queue))
    print("existing_quarantine_rows:", len(quarantine_existing))
    print("reviewed_repair_rows:", len(review_rows))
    print("repair_candidate_rows:", len(repair_candidates))
    print("pending_rows:", len(pending_rows))
    print("quarantine_addition_rows:", len(quarantine_additions))
    print("blocker_count:", len(blockers))
    print("warning_count:", len(warnings))
    print("out_review_rows:", args.out_review_rows)
    print("out_repair_candidates:", args.out_repair_candidates)
    print("out_pending:", args.out_pending)
    print("out_quarantine_additions:", args.out_quarantine_additions)
    print("out_summary_csv:", args.out_summary_csv)
    print("out_decision_json:", args.out_decision_json)
    print("out_report:", args.out_report)
    print("repair queue review only; no model eval; no training; no checkpoint read/write; no C export; no benchmark; no promotion")


if __name__ == "__main__":
    main()
