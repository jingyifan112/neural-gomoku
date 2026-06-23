#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


ROUTE_DERIVED_TOKENS = [
    "route",
    "dispatch",
    "followup",
    "closeout",
    "dryrun",
    "executor",
    "decision",
    "summary",
]

DEBUG_OR_LEGACY_TOKENS = [
    "debug",
    "tmp",
    "legacy",
    "candidate_c",
    "candidate_d",
    "candidate_e",
    "mcts16_debug",
    "mcts32_debug",
    "nearend",
    "failure_snapshots",
]

TRAIN_DERIVED_TOKENS = [
    "trainable",
    "trainer_ready",
    "train_candidate",
    "train_teacher",
    "policy_margin",
    "retention_expanded_dataset",
    "expanded_candidate_manifest",
]

CLEAN_SOURCE_TOKENS = [
    "heldout",
    "fixed_probe",
    "direct_probe",
    "probe_heldout",
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Inspect direct adapter blockers row-by-row without model eval/checkpoint reads."
    )
    p.add_argument(
        "--repair-plan-summary",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_next_direct_probe_input_repair_plan_summary.csv"),
    )
    p.add_argument(
        "--repair-plan-decision-json",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_next_direct_probe_input_repair_plan_decision.json"),
    )
    p.add_argument(
        "--repair-actions",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_next_direct_probe_input_repair_actions.csv"),
    )
    p.add_argument(
        "--direct-adapter-summary",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_direct_probe_eval_adapter_summary.csv"),
    )
    p.add_argument(
        "--direct-manifest",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_direct_probe_eval_adapter_manifest.csv"),
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
        "--out-rows-csv",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_next_direct_adapter_blocker_inspection_rows.csv"),
    )
    p.add_argument(
        "--out-summary-csv",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_next_direct_adapter_blocker_inspection_summary.csv"),
    )
    p.add_argument(
        "--out-decision-json",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_next_direct_adapter_blocker_inspection_decision.json"),
    )
    p.add_argument(
        "--out-report",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_next_direct_adapter_blocker_inspection.md"),
    )
    return p.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def by_metric(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {r["metric"]: r for r in rows}


def get(m: dict[str, dict[str, str]], key: str, default: str = "") -> str:
    return m.get(key, {}).get("value", default)


def notes(m: dict[str, dict[str, str]], key: str, default: str = "") -> str:
    return m.get(key, {}).get("notes", default)


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


def summary_row(metric: str, value: Any, status: str, notes_text: str = "") -> dict[str, str]:
    return {
        "metric": metric,
        "value": str(value),
        "status": status,
        "notes": notes_text,
    }


def contains_any(text: str, tokens: list[str]) -> bool:
    lower = text.lower()
    return any(t in lower for t in tokens)


def split_tokens(text: str, tokens: list[str]) -> list[str]:
    lower = text.lower()
    return [t for t in tokens if t in lower]


def infer_schema_from_path(path: Path) -> tuple[str, str, str, int, str]:
    """Return path_exists, path_type, format, row_count_or_keys, schema_keys."""
    if not path.exists():
        return "0", "missing", path.suffix.lower().lstrip(".") or "unknown", 0, ""

    if path.is_dir():
        try:
            count = len(list(path.iterdir()))
        except OSError:
            count = 0
        return "1", "directory", "directory", count, ""

    suffix = path.suffix.lower()
    fmt = suffix.lstrip(".") or "unknown"

    if suffix == ".csv":
        try:
            rows = read_csv(path)
            keys = []
            if rows:
                keys = sorted(rows[0].keys())
            else:
                with path.open(newline="", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    keys = sorted(reader.fieldnames or [])
            return "1", "file", "csv", len(rows), ",".join(keys)
        except Exception as e:
            return "1", "file", "csv", -1, f"CSV_READ_ERROR:{type(e).__name__}"

    if suffix == ".json":
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                keys = sorted(data.keys())
                if "samples" in data and isinstance(data["samples"], list):
                    count = len(data["samples"])
                elif "rows" in data and isinstance(data["rows"], list):
                    count = len(data["rows"])
                else:
                    count = len(keys)
                return "1", "file", "json", count, ",".join(map(str, keys))
            if isinstance(data, list):
                keys = sorted(data[0].keys()) if data and isinstance(data[0], dict) else []
                return "1", "file", "json", len(data), ",".join(map(str, keys))
            return "1", "file", "json", 1, type(data).__name__
        except Exception as e:
            return "1", "file", "json", -1, f"JSON_READ_ERROR:{type(e).__name__}"

    if suffix in {".md", ".txt"}:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
            line_count = len(text.splitlines())
            heading_count = sum(1 for line in text.splitlines() if line.lstrip().startswith("#"))
            keys = f"lines={line_count};headings={heading_count}"
            return "1", "file", fmt, line_count, keys
        except Exception as e:
            return "1", "file", fmt, -1, f"TEXT_READ_ERROR:{type(e).__name__}"

    try:
        size = path.stat().st_size
    except OSError:
        size = 0
    return "1", "file", fmt, size, ""


def choose_path(row: dict[str, str]) -> str:
    for k in ["path", "source_path", "manifest_path", "input_path", "file", "filepath"]:
        v = row.get(k, "").strip()
        if v:
            return v
    return ""


def inspect_row(idx: int, row: dict[str, str]) -> dict[str, str]:
    row_text = " ".join(str(v) for v in row.values())
    path_text = choose_path(row)
    path = Path(path_text) if path_text else Path("__missing_path__")
    path_exists, path_type, inferred_format, inspected_count, schema_keys = infer_schema_from_path(path)

    adapter_kind = row.get("adapter_kind", "")
    eval_manifest_id = row.get("eval_manifest_id", row.get("id", f"row_{idx}"))
    sample_count = row.get("sample_rows_or_count", row.get("rows", row.get("count", "")))

    route_tokens = split_tokens(path_text + " " + row_text, ROUTE_DERIVED_TOKENS)
    debug_tokens = split_tokens(path_text + " " + row_text, DEBUG_OR_LEGACY_TOKENS)
    train_tokens = split_tokens(path_text + " " + row_text, TRAIN_DERIVED_TOKENS)
    clean_tokens = split_tokens(path_text + " " + row_text, CLEAN_SOURCE_TOKENS)

    problems: list[str] = []

    if not path_text:
        problems.append("missing_path_field")
    if path_exists != "1":
        problems.append("path_missing")
    if not adapter_kind:
        problems.append("missing_adapter_kind")
    if not sample_count:
        problems.append("missing_sample_count")
    if inspected_count == -1:
        problems.append("source_parse_error")
    if route_tokens:
        problems.append("route_derived_artifact")
    if debug_tokens:
        problems.append("debug_or_legacy_artifact")
    if train_tokens:
        problems.append("train_derived_artifact")
    if not clean_tokens:
        problems.append("no_clean_heldout_or_direct_token")

    if not problems:
        schema_status = "OK"
    elif any(p in problems for p in ["missing_path_field", "missing_adapter_kind", "missing_sample_count", "source_parse_error"]):
        schema_status = "INCOMPLETE"
    else:
        schema_status = "HAS_CONTEXT_BUT_NEEDS_REVIEW"

    if clean_tokens and not train_tokens and not debug_tokens:
        provenance_status = "CLEAN_HELDOUT_OR_DIRECT_SOURCE"
    elif route_tokens:
        provenance_status = "ROUTE_DERIVED_ONLY"
    elif debug_tokens:
        provenance_status = "DEBUG_OR_LEGACY_SOURCE"
    elif train_tokens:
        provenance_status = "TRAIN_DERIVED_SOURCE"
    else:
        provenance_status = "UNKNOWN"

    if train_tokens:
        leakage_risk = "HIGH"
    elif route_tokens or debug_tokens:
        leakage_risk = "MEDIUM"
    elif clean_tokens:
        leakage_risk = "LOW"
    else:
        leakage_risk = "MEDIUM"

    if schema_status == "OK" and provenance_status == "CLEAN_HELDOUT_OR_DIRECT_SOURCE" and leakage_risk == "LOW":
        direct_eval_readiness = "READY_FOR_FUTURE_GUARDED_EVAL_REVIEW"
        risk_level = "LOW"
        recommended_action = "KEEP_AS_CANDIDATE_FOR_NORMALIZATION"
    elif schema_status == "INCOMPLETE":
        direct_eval_readiness = "NEEDS_REPAIR"
        risk_level = "HIGH"
        recommended_action = "REPAIR_SCHEMA_THEN_REVIEW"
    elif provenance_status in {"ROUTE_DERIVED_ONLY", "UNKNOWN"}:
        direct_eval_readiness = "NEEDS_REPAIR"
        risk_level = "MEDIUM"
        recommended_action = "REPAIR_PROVENANCE_THEN_REVIEW"
    elif provenance_status in {"DEBUG_OR_LEGACY_SOURCE", "TRAIN_DERIVED_SOURCE"}:
        direct_eval_readiness = "NOT_READY"
        risk_level = "HIGH"
        recommended_action = "QUARANTINE_FOR_NOW"
    else:
        direct_eval_readiness = "NEEDS_REPAIR"
        risk_level = "MEDIUM"
        recommended_action = "MANUAL_REVIEW"

    return {
        "manifest_row_id": str(idx),
        "eval_manifest_id": eval_manifest_id,
        "adapter_kind": adapter_kind,
        "path": path_text,
        "sample_rows_or_count": sample_count,
        "path_exists": path_exists,
        "path_type": path_type,
        "inferred_format": inferred_format,
        "inspected_count": str(inspected_count),
        "schema_keys": schema_keys,
        "schema_status": schema_status,
        "provenance_status": provenance_status,
        "leakage_risk": leakage_risk,
        "direct_eval_readiness": direct_eval_readiness,
        "risk_level": risk_level,
        "recommended_action": recommended_action,
        "route_tokens": ",".join(route_tokens),
        "debug_or_legacy_tokens": ",".join(debug_tokens),
        "train_derived_tokens": ",".join(train_tokens),
        "clean_source_tokens": ",".join(clean_tokens),
        "problems": ";".join(problems),
        "notes": "row-level input inspection only; no model eval or checkpoint read",
    }


def esc(value: Any) -> str:
    return str(value).replace("|", "\\|")


def main() -> None:
    args = parse_args()

    for p in [
        args.repair_plan_summary,
        args.repair_plan_decision_json,
        args.repair_actions,
        args.direct_adapter_summary,
        args.direct_manifest,
        args.combined_summary,
        args.current_best_checkpoint,
    ]:
        if not p.exists():
            raise FileNotFoundError(p)

    repair_plan = by_metric(read_csv(args.repair_plan_summary))
    repair_decision = json.loads(args.repair_plan_decision_json.read_text(encoding="utf-8"))
    repair_actions = read_csv(args.repair_actions)
    direct_summary = by_metric(read_csv(args.direct_adapter_summary))
    manifest = read_csv(args.direct_manifest)
    combined = read_csv(args.combined_summary)

    plan_decision = get(repair_plan, "plan_decision")
    direct_adapter_decision = get(direct_summary, "adapter_decision")
    direct_adapter_blocker_count = as_int(get(direct_summary, "blocker_count"))
    direct_adapter_blocker_notes = notes(direct_summary, "blocker_count")
    direct_adapter_warning_count = as_int(get(direct_summary, "warning_count"))
    direct_adapter_warning_notes = notes(direct_summary, "warning_count")

    candidate_exists = args.candidate_checkpoint.exists()
    current_best_exists = args.current_best_checkpoint.exists()

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

    inspected_rows = [inspect_row(i, row) for i, row in enumerate(manifest, start=1)]

    counts: dict[str, int] = {}
    for r in inspected_rows:
        for key in [
            "schema_status",
            "provenance_status",
            "leakage_risk",
            "direct_eval_readiness",
            "risk_level",
            "recommended_action",
        ]:
            k = f"{key}:{r[key]}"
            counts[k] = counts.get(k, 0) + 1

    ready_rows = sum(1 for r in inspected_rows if r["direct_eval_readiness"] == "READY_FOR_FUTURE_GUARDED_EVAL_REVIEW")
    needs_repair_rows = sum(1 for r in inspected_rows if r["direct_eval_readiness"] == "NEEDS_REPAIR")
    not_ready_rows = sum(1 for r in inspected_rows if r["direct_eval_readiness"] == "NOT_READY")
    quarantine_rows = sum(1 for r in inspected_rows if r["recommended_action"] == "QUARANTINE_FOR_NOW")
    schema_repair_rows = sum(1 for r in inspected_rows if r["recommended_action"] == "REPAIR_SCHEMA_THEN_REVIEW")
    provenance_repair_rows = sum(1 for r in inspected_rows if r["recommended_action"] == "REPAIR_PROVENANCE_THEN_REVIEW")

    blockers: list[str] = []
    warnings: list[str] = []

    if plan_decision != "DIRECT_PROBE_INPUT_REPAIR_PLAN_READY":
        blockers.append(f"repair plan not ready: {plan_decision}")
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
    if not inspected_rows:
        blockers.append("direct manifest is empty")

    if not candidate_exists:
        warnings.append("candidate checkpoint path missing locally; still no checkpoint read needed for inspection")
    if combined_warn_rows:
        warnings.append(f"combined WARN rows carried forward: {len(combined_warn_rows)}")
    if protected_prob_regressed:
        warnings.append(f"protected probability regressions carried forward: {protected_prob_regressed}")
    if tail_prob_regressed:
        warnings.append(f"tail probability regressions carried forward: {tail_prob_regressed}")
    if direct_adapter_blocker_count:
        warnings.append(f"direct adapter blocker notes carried forward: {direct_adapter_blocker_notes}")
    if direct_adapter_warning_count:
        warnings.append(f"direct adapter warning notes carried forward: {direct_adapter_warning_notes}")
    if quarantine_rows:
        warnings.append(f"rows recommended for quarantine: {quarantine_rows}")
    if schema_repair_rows:
        warnings.append(f"rows needing schema repair: {schema_repair_rows}")
    if provenance_repair_rows:
        warnings.append(f"rows needing provenance repair: {provenance_repair_rows}")

    if blockers:
        inspection_decision = "DIRECT_ADAPTER_BLOCKER_INSPECTION_BLOCKED"
        recommended_next = "Fix hard blocker before manifest repair."
    elif ready_rows > 0:
        inspection_decision = "DIRECT_ADAPTER_BLOCKER_INSPECTION_READY_FOR_NORMALIZATION_REVIEW"
        recommended_next = "Normalize ready/repairable rows into a stricter manifest; keep eval disabled."
    elif needs_repair_rows > 0:
        inspection_decision = "DIRECT_ADAPTER_BLOCKER_INSPECTION_REPAIR_NEEDED"
        recommended_next = "Repair schema/provenance first; do not build eval executor yet."
    else:
        inspection_decision = "DIRECT_ADAPTER_BLOCKER_INSPECTION_QUARANTINE_DIRECT_ROUTE"
        recommended_next = "Quarantine direct route and materialize cleaner heldout/fixed-probe sources."

    args.out_rows_csv.parent.mkdir(parents=True, exist_ok=True)
    if inspected_rows:
        fieldnames = list(inspected_rows[0].keys())
    else:
        fieldnames = [
            "manifest_row_id",
            "eval_manifest_id",
            "adapter_kind",
            "path",
            "sample_rows_or_count",
            "path_exists",
            "path_type",
            "inferred_format",
            "inspected_count",
            "schema_keys",
            "schema_status",
            "provenance_status",
            "leakage_risk",
            "direct_eval_readiness",
            "risk_level",
            "recommended_action",
            "route_tokens",
            "debug_or_legacy_tokens",
            "train_derived_tokens",
            "clean_source_tokens",
            "problems",
            "notes",
        ]
    with args.out_rows_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(inspected_rows)

    summary_rows = [
        summary_row("inspection_decision", inspection_decision, "INFO", "Inspection only; no model eval."),
        summary_row("recommended_next", recommended_next, "INFO"),
        summary_row("plan_decision", plan_decision, "INFO"),
        summary_row("direct_adapter_decision", direct_adapter_decision, "INFO"),
        summary_row("direct_adapter_blocker_count", direct_adapter_blocker_count, "WARN" if direct_adapter_blocker_count else "PASS", direct_adapter_blocker_notes),
        summary_row("direct_adapter_warning_count", direct_adapter_warning_count, "WARN" if direct_adapter_warning_count else "PASS", direct_adapter_warning_notes),
        summary_row("repair_action_count", len(repair_actions), "INFO"),
        summary_row("manifest_rows", len(inspected_rows), "INFO"),
        summary_row("ready_rows", ready_rows, "INFO"),
        summary_row("needs_repair_rows", needs_repair_rows, "INFO"),
        summary_row("not_ready_rows", not_ready_rows, "INFO"),
        summary_row("quarantine_rows", quarantine_rows, "WARN" if quarantine_rows else "PASS"),
        summary_row("schema_repair_rows", schema_repair_rows, "WARN" if schema_repair_rows else "PASS"),
        summary_row("provenance_repair_rows", provenance_repair_rows, "WARN" if provenance_repair_rows else "PASS"),
        summary_row("blocker_count", len(blockers), "PASS" if not blockers else "FAIL", "; ".join(blockers)),
        summary_row("warning_count", len(warnings), "WARN" if warnings else "PASS", "; ".join(warnings)),
        summary_row("candidate_checkpoint_exists_locally", int(candidate_exists), "INFO", "Existence only; no checkpoint read."),
        summary_row("current_best_exists", int(current_best_exists), "PASS" if current_best_exists else "FAIL"),
        summary_row("combined_fail_rows", len(combined_fail_rows), "PASS" if not combined_fail_rows else "FAIL"),
        summary_row("combined_warn_rows", len(combined_warn_rows), "WARN" if combined_warn_rows else "PASS"),
        summary_row("trainable_gap_improved", trainable_gap_improved, "PASS" if trainable_gap_improved == 44 else "FAIL"),
        summary_row("trainable_rank_regressed", trainable_rank_regressed, "PASS" if trainable_rank_regressed == 0 else "FAIL"),
        summary_row("protected_rank_regressed", protected_rank_regressed, "PASS" if protected_rank_regressed == 0 else "FAIL"),
        summary_row("tail_rank_regressed", tail_rank_regressed, "PASS" if tail_rank_regressed == 0 else "WARN"),
        summary_row("protected_prob_regressed", protected_prob_regressed, "WARN" if protected_prob_regressed else "PASS"),
        summary_row("tail_prob_regressed", tail_prob_regressed, "WARN" if tail_prob_regressed else "PASS"),
        summary_row("anchor_top1_changed", anchor_top1_changed, "PASS" if anchor_top1_changed == 0 else "FAIL"),
        summary_row("anchor_max_kl", f"{anchor_max_kl:.10f}", "PASS" if anchor_max_kl <= 0.005 else "FAIL"),
        summary_row("would_train", 0, "PASS"),
        summary_row("would_eval_model_now", 0, "PASS"),
        summary_row("would_read_checkpoint_contents_now", 0, "PASS"),
        summary_row("would_write_checkpoint", 0, "PASS"),
        summary_row("would_c_export", 0, "PASS"),
        summary_row("would_public_benchmark", 0, "PASS"),
        summary_row("would_promote", 0, "PASS"),
    ]

    for key, count in sorted(counts.items()):
        summary_rows.append(summary_row(f"count_{key}", count, "INFO"))

    args.out_summary_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.out_summary_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["metric", "value", "status", "notes"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(summary_rows)

    decision = {
        "inspection_decision": inspection_decision,
        "recommended_next": recommended_next,
        "plan_decision": plan_decision,
        "direct_adapter_decision": direct_adapter_decision,
        "would_train_now": False,
        "would_eval_model_now": False,
        "would_read_checkpoint_contents_now": False,
        "would_write_checkpoint": False,
        "would_c_export": False,
        "would_public_benchmark": False,
        "would_promote": False,
        "candidate_checkpoint_path": str(args.candidate_checkpoint),
        "current_best_checkpoint_path": str(args.current_best_checkpoint),
        "row_counts": {
            "manifest_rows": len(inspected_rows),
            "ready_rows": ready_rows,
            "needs_repair_rows": needs_repair_rows,
            "not_ready_rows": not_ready_rows,
            "quarantine_rows": quarantine_rows,
            "schema_repair_rows": schema_repair_rows,
            "provenance_repair_rows": provenance_repair_rows,
        },
        "blockers": blockers,
        "warnings": warnings,
    }

    args.out_decision_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_decision_json.write_text(json.dumps(decision, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    report = [
        "# Teacher-divergence next direct adapter blocker inspection",
        "",
        "## Branch",
        "",
        "`exp/15x15-teacher-divergence-next-direct-adapter-blocker-inspection`",
        "",
        "## Scope",
        "",
        "- Inspects direct manifest rows one by one.",
        "- Does not train.",
        "- Does not run model eval.",
        "- Does not read checkpoint contents.",
        "- Does not write checkpoints.",
        "- Does not overwrite `checkpoints/15x15_current_best.pt`.",
        "- Does not C export.",
        "- Does not run public benchmark.",
        "- Does not promote.",
        "",
        "## Inspection decision",
        "",
        f"`{inspection_decision}`",
        "",
        "## Recommended next",
        "",
        recommended_next,
        "",
        "## Row-level summary",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| manifest_rows | {len(inspected_rows)} |",
        f"| ready_rows | {ready_rows} |",
        f"| needs_repair_rows | {needs_repair_rows} |",
        f"| not_ready_rows | {not_ready_rows} |",
        f"| quarantine_rows | {quarantine_rows} |",
        f"| schema_repair_rows | {schema_repair_rows} |",
        f"| provenance_repair_rows | {provenance_repair_rows} |",
        "",
        "## Row inspection table",
        "",
        "| row | eval_manifest_id | path_exists | schema | provenance | leakage | readiness | action | problems |",
        "|---:|---|---:|---|---|---|---|---|---|",
    ]

    for r in inspected_rows:
        report.append(
            "| {row} | {eval_id} | {exists} | {schema} | {prov} | {leak} | {ready} | {action} | {problems} |".format(
                row=esc(r["manifest_row_id"]),
                eval_id=esc(r["eval_manifest_id"]),
                exists=esc(r["path_exists"]),
                schema=esc(r["schema_status"]),
                prov=esc(r["provenance_status"]),
                leak=esc(r["leakage_risk"]),
                ready=esc(r["direct_eval_readiness"]),
                action=esc(r["recommended_action"]),
                problems=esc(r["problems"]),
            )
        )

    report.extend([
        "",
        "## Summary metrics",
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
    if inspection_decision == "DIRECT_ADAPTER_BLOCKER_INSPECTION_READY_FOR_NORMALIZATION_REVIEW":
        report.append("At least one direct row looks repairable/normalizable enough for a future guarded-input manifest review. This is still not an eval executor.")
    elif inspection_decision == "DIRECT_ADAPTER_BLOCKER_INSPECTION_REPAIR_NEEDED":
        report.append("Rows exist, but they need schema/provenance repair before any future guarded eval route.")
    elif inspection_decision == "DIRECT_ADAPTER_BLOCKER_INSPECTION_QUARANTINE_DIRECT_ROUTE":
        report.append("The current direct route should be quarantined; materialize cleaner heldout/fixed-probe inputs first.")
    else:
        report.append("A hard blocker remains; do not continue to manifest repair.")

    report.extend([
        "",
        "## Final guardrails",
        "",
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

    print("inspection_decision:", inspection_decision)
    print("recommended_next:", recommended_next)
    print("manifest_rows:", len(inspected_rows))
    print("ready_rows:", ready_rows)
    print("needs_repair_rows:", needs_repair_rows)
    print("not_ready_rows:", not_ready_rows)
    print("quarantine_rows:", quarantine_rows)
    print("schema_repair_rows:", schema_repair_rows)
    print("provenance_repair_rows:", provenance_repair_rows)
    print("blocker_count:", len(blockers))
    print("warning_count:", len(warnings))
    print("out_rows_csv:", args.out_rows_csv)
    print("out_summary_csv:", args.out_summary_csv)
    print("out_decision_json:", args.out_decision_json)
    print("out_report:", args.out_report)
    print("inspection only; no model eval; no training; no checkpoint read/write; no C export; no benchmark; no promotion")


if __name__ == "__main__":
    main()
