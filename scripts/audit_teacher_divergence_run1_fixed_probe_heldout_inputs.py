#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any


KEYWORDS = [
    "fixed", "probe", "heldout", "retention", "tactical", "anchor",
    "blocker", "failure", "benchmark", "teacher_divergence", "margin",
    "dataset", "eval", "guard",
]

DATA_SUFFIXES = {".csv", ".json", ".jsonl", ".md", ".txt"}

SKIP_PARTS = {
    ".git",
    "__pycache__",
    "checkpoints",
    "eval_logs",
    "c_inference",
    "adapter_probe_tmp",
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Inventory fixed-probe/heldout inputs for run1 candidate-vs-current_best comparison."
    )
    p.add_argument(
        "--plan-summary",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_fixed_probe_heldout_plan_summary.csv"),
    )
    p.add_argument(
        "--trainable-guard",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_gated_training_run1_e10_trainable_gap_guard.csv"),
    )
    p.add_argument(
        "--bucket-guard",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_gated_training_run1_e10_manifest_bucket_guard.csv"),
    )
    p.add_argument(
        "--anchor-guard",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_gated_training_run1_e10_anchor_drift_guard.csv"),
    )
    p.add_argument(
        "--search-roots",
        nargs="+",
        type=Path,
        default=[
            Path("analysis/integration_eval"),
            Path("analysis/public_benchmark_eval"),
            Path("scripts"),
        ],
    )
    p.add_argument(
        "--out-inventory-csv",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_fixed_probe_heldout_input_inventory.csv"),
    )
    p.add_argument(
        "--out-summary-csv",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_fixed_probe_heldout_input_audit_summary.csv"),
    )
    p.add_argument(
        "--out-report",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_run1_fixed_probe_heldout_input_audit.md"),
    )
    return p.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def safe_text(path: Path, limit: int = 240_000) -> str:
    try:
        data = path.read_bytes()[:limit]
    except Exception:
        return ""
    return data.decode("utf-8", errors="replace")


def skip_path(path: Path) -> bool:
    return any(part in SKIP_PARTS for part in path.parts)


def matched_terms(path: Path) -> list[str]:
    s = str(path).lower()
    return [k for k in KEYWORDS if k in s]


def classify_stage(path: Path) -> str:
    s = str(path).lower()
    if "run1" in s:
        return "run1_output"
    if "heldout" in s:
        return "heldout_candidate"
    if "fixed" in s or "probe" in s or "tactical" in s:
        return "fixed_probe_candidate"
    if "anchor" in s:
        return "anchor_candidate"
    if "benchmark" in s:
        return "benchmark_related"
    if "dataset" in s:
        return "dataset_related"
    if "guard" in s:
        return "guard_related"
    return "related"


def detect_from_csv(path: Path) -> dict[str, Any]:
    try:
        with path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fields = list(reader.fieldnames or [])
            sample_rows = []
            for i, row in enumerate(reader):
                sample_rows.append(row)
                if i >= 2:
                    break
    except Exception as e:
        return {"read_error": str(e), "fields": [], "sample_rows": 0}

    field_set = set(fields)
    return {
        "fields": fields,
        "sample_rows": len(sample_rows),
        "has_board": bool(field_set & {"board", "board_snapshot", "board_snapshot_before_decision"}),
        "has_side": bool(field_set & {"current_player", "side_to_move", "player", "to_move"}),
        "has_target": bool(field_set & {"target_rc", "target", "expected_rc", "teacher_move", "correct_move"}),
        "has_suppress": bool(field_set & {"suppress_rc", "primary_suppress_rc"}),
        "has_prob_delta": bool(field_set & {"target_prob_delta", "prob_delta"}),
        "has_rank_delta": bool(field_set & {"target_rank_delta", "rank_delta"}),
        "has_case_id": bool(field_set & {"case_id", "manifest_id", "id"}),
    }


def flatten_keys(obj: Any, prefix: str = "", limit: int = 400) -> set[str]:
    out: set[str] = set()
    if len(out) > limit:
        return out
    if isinstance(obj, dict):
        for k, v in obj.items():
            key = f"{prefix}.{k}" if prefix else str(k)
            out.add(key)
            out.add(str(k))
            out |= flatten_keys(v, key, limit)
            if len(out) > limit:
                break
    elif isinstance(obj, list):
        for item in obj[:3]:
            out |= flatten_keys(item, prefix, limit)
            if len(out) > limit:
                break
    return out


def detect_from_json(path: Path) -> dict[str, Any]:
    text = safe_text(path)
    try:
        obj = json.loads(text)
    except Exception as e:
        return {"read_error": str(e), "keys": [], "sample_rows": 0}

    keys = sorted(flatten_keys(obj))
    key_set = set(keys)

    sample_count = 0
    if isinstance(obj, dict):
        for container_key in ["samples", "rows", "data", "positions", "snapshots"]:
            value = obj.get(container_key)
            if isinstance(value, list):
                sample_count = len(value)
                break
    elif isinstance(obj, list):
        sample_count = len(obj)

    return {
        "keys": keys[:120],
        "sample_rows": sample_count,
        "has_board": bool(key_set & {"board", "board_snapshot", "board_snapshot_before_decision"}),
        "has_side": bool(key_set & {"current_player", "side_to_move", "player", "to_move"}),
        "has_target": bool(key_set & {"target_rc", "target", "expected_rc", "teacher_move", "correct_move"}),
        "has_suppress": bool(key_set & {"suppress_rc", "primary_suppress_rc"}),
        "has_prob_delta": bool(key_set & {"target_prob_delta", "prob_delta"}),
        "has_rank_delta": bool(key_set & {"target_rank_delta", "rank_delta"}),
        "has_case_id": bool(key_set & {"case_id", "manifest_id", "id"}),
    }


def detect_from_text(path: Path) -> dict[str, Any]:
    text = safe_text(path).lower()
    return {
        "sample_rows": 0,
        "has_board": "board" in text or "snapshot" in text,
        "has_side": "current_player" in text or "side_to_move" in text,
        "has_target": "target_rc" in text or "teacher_move" in text or "correct_move" in text,
        "has_suppress": "suppress_rc" in text,
        "has_prob_delta": "prob_delta" in text or "target_prob_delta" in text,
        "has_rank_delta": "rank_delta" in text or "target_rank_delta" in text,
        "has_case_id": "case_id" in text or "manifest_id" in text,
    }


def detect_schema(path: Path) -> dict[str, Any]:
    if path.suffix == ".csv":
        return detect_from_csv(path)
    if path.suffix == ".json":
        return detect_from_json(path)
    if path.suffix == ".jsonl":
        text = safe_text(path)
        first = text.splitlines()[0] if text.splitlines() else ""
        try:
            obj = json.loads(first) if first else {}
            keys = sorted(flatten_keys(obj))
        except Exception:
            keys = []
        key_set = set(keys)
        return {
            "keys": keys[:120],
            "sample_rows": len(text.splitlines()),
            "has_board": bool(key_set & {"board", "board_snapshot", "board_snapshot_before_decision"}),
            "has_side": bool(key_set & {"current_player", "side_to_move", "player", "to_move"}),
            "has_target": bool(key_set & {"target_rc", "target", "expected_rc", "teacher_move", "correct_move"}),
            "has_suppress": bool(key_set & {"suppress_rc", "primary_suppress_rc"}),
            "has_prob_delta": bool(key_set & {"target_prob_delta", "prob_delta"}),
            "has_rank_delta": bool(key_set & {"target_rank_delta", "rank_delta"}),
            "has_case_id": bool(key_set & {"case_id", "manifest_id", "id"}),
        }
    return detect_from_text(path)


def schema_ready_kind(det: dict[str, Any]) -> str:
    if det.get("has_board") and det.get("has_side") and det.get("has_target"):
        return "direct_model_eval_ready"
    if det.get("has_prob_delta") or det.get("has_rank_delta"):
        return "already_compared_guard_output"
    if det.get("has_board") and det.get("has_side"):
        return "needs_target_adapter"
    if det.get("has_target"):
        return "needs_board_join_adapter"
    return "not_directly_eval_ready"


def main() -> None:
    args = parse_args()

    for path in [args.plan_summary, args.trainable_guard, args.bucket_guard, args.anchor_guard]:
        if not path.exists():
            raise FileNotFoundError(path)

    plan_rows = read_csv(args.plan_summary)
    trainable_rows = read_csv(args.trainable_guard)
    bucket_rows = read_csv(args.bucket_guard)
    anchor_rows = read_csv(args.anchor_guard)

    found: list[Path] = []
    for root in args.search_roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if skip_path(path):
                continue
            if not path.is_file():
                continue
            if path.suffix not in DATA_SUFFIXES:
                continue
            terms = matched_terms(path)
            if terms:
                found.append(path)

    inventory: list[dict[str, str]] = []
    for path in sorted(set(found), key=lambda p: str(p)):
        det = detect_schema(path)
        ready_kind = schema_ready_kind(det)
        terms = matched_terms(path)
        inventory.append({
            "path": str(path),
            "suffix": path.suffix,
            "size_bytes": str(path.stat().st_size),
            "stage_class": classify_stage(path),
            "matched_terms": ";".join(terms),
            "sample_rows_or_count": str(det.get("sample_rows", "")),
            "has_board": str(int(bool(det.get("has_board")))),
            "has_side": str(int(bool(det.get("has_side")))),
            "has_target": str(int(bool(det.get("has_target")))),
            "has_suppress": str(int(bool(det.get("has_suppress")))),
            "has_prob_delta": str(int(bool(det.get("has_prob_delta")))),
            "has_rank_delta": str(int(bool(det.get("has_rank_delta")))),
            "has_case_id": str(int(bool(det.get("has_case_id")))),
            "schema_ready_kind": ready_kind,
            "read_error": str(det.get("read_error", "")),
        })

    args.out_inventory_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.out_inventory_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(inventory[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(inventory)

    kind_counts = Counter(r["schema_ready_kind"] for r in inventory)
    stage_counts = Counter(r["stage_class"] for r in inventory)
    suffix_counts = Counter(r["suffix"] for r in inventory)

    direct_ready = [r for r in inventory if r["schema_ready_kind"] == "direct_model_eval_ready"]
    guard_ready = [r for r in inventory if r["schema_ready_kind"] == "already_compared_guard_output"]
    needs_board_join = [r for r in inventory if r["schema_ready_kind"] == "needs_board_join_adapter"]
    needs_target_adapter = [r for r in inventory if r["schema_ready_kind"] == "needs_target_adapter"]

    plan_decision = "READY_TO_IMPLEMENT_LOCAL_COMPARISON_ADAPTERS"
    if not direct_ready and not guard_ready:
        plan_decision = "BLOCKED_NO_EVALUABLE_INPUTS_FOUND"

    summary_rows = [
        {"metric": "plan_decision", "value": plan_decision, "status": "INFO", "notes": "Input audit only."},
        {"metric": "inventory_rows", "value": str(len(inventory)), "status": "INFO", "notes": ""},
        {"metric": "direct_model_eval_ready_files", "value": str(len(direct_ready)), "status": "INFO", "notes": ""},
        {"metric": "already_compared_guard_output_files", "value": str(len(guard_ready)), "status": "INFO", "notes": ""},
        {"metric": "needs_board_join_adapter_files", "value": str(len(needs_board_join)), "status": "INFO", "notes": ""},
        {"metric": "needs_target_adapter_files", "value": str(len(needs_target_adapter)), "status": "INFO", "notes": ""},
        {"metric": "run1_trainable_guard_rows", "value": str(len(trainable_rows)), "status": "PASS" if len(trainable_rows) == 44 else "WARN", "notes": ""},
        {"metric": "run1_bucket_guard_rows", "value": str(len(bucket_rows)), "status": "PASS" if len(bucket_rows) == 89 else "WARN", "notes": ""},
        {"metric": "run1_anchor_guard_rows", "value": str(len(anchor_rows)), "status": "PASS" if len(anchor_rows) == 32 else "WARN", "notes": ""},
        {"metric": "plan_summary_rows", "value": str(len(plan_rows)), "status": "INFO", "notes": ""},
    ]

    args.out_summary_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.out_summary_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["metric", "value", "status", "notes"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(summary_rows)

    lines = [
        "# Teacher-divergence run1 fixed-probe / heldout input audit",
        "",
        "## Branch",
        "",
        "`exp/15x15-teacher-divergence-run1-fixed-probe-heldout-input-audit`",
        "",
        "## Scope",
        "",
        "- Inventories local fixed-probe, heldout, tactical, anchor, dataset, and guard artifacts.",
        "- Classifies which inputs are directly evaluable versus which need adapters.",
        "- Does not train.",
        "- Does not read or write checkpoints.",
        "- Does not overwrite `checkpoints/15x15_current_best.pt`.",
        "- Does not C export.",
        "- Does not run public benchmark.",
        "- Does not promote.",
        "",
        "## Decision",
        "",
        f"`{plan_decision}`",
        "",
        "## Summary",
        "",
        "| metric | value | status | notes |",
        "|---|---:|---|---|",
    ]

    for r in summary_rows:
        lines.append(f"| {r['metric']} | {r['value']} | {r['status']} | {r['notes']} |")

    lines.extend([
        "",
        "## Schema-ready counts",
        "",
        "| schema_ready_kind | files |",
        "|---|---:|",
    ])
    for k, v in kind_counts.most_common():
        lines.append(f"| {k} | {v} |")

    lines.extend([
        "",
        "## Stage counts",
        "",
        "| stage_class | files |",
        "|---|---:|",
    ])
    for k, v in stage_counts.most_common():
        lines.append(f"| {k} | {v} |")

    lines.extend([
        "",
        "## Suffix counts",
        "",
        "| suffix | files |",
        "|---|---:|",
    ])
    for k, v in suffix_counts.most_common():
        lines.append(f"| {k} | {v} |")

    def add_section(title: str, rows: list[dict[str, str]], limit: int = 30) -> None:
        lines.extend([
            "",
            f"## {title}",
            "",
            "| path | stage | rows/count | schema_ready_kind |",
            "|---|---|---:|---|",
        ])
        if not rows:
            lines.append("| none |  |  |  |")
            return
        for r in rows[:limit]:
            lines.append(
                f"| `{r['path']}` | {r['stage_class']} | {r['sample_rows_or_count']} | {r['schema_ready_kind']} |"
            )

    add_section("Direct model-eval ready candidates", direct_ready)
    add_section("Already compared guard outputs", guard_ready)
    add_section("Needs board-join adapter", needs_board_join)
    add_section("Needs target adapter", needs_target_adapter)

    lines.extend([
        "",
        "## Recommended next implementation",
        "",
        "Implement the local comparison executor in two layers:",
        "",
        "1. Reuse run1 guard outputs as already-computed candidate-vs-current_best comparisons for trainable, protected/tail, and anchor rows.",
        "2. Add adapters only for direct model-eval ready fixed-probe/heldout datasets discovered here.",
        "3. Keep fixed-probe/heldout comparison local only; do not export C and do not run public benchmark.",
        "",
        "## Outputs",
        "",
        f"- inventory CSV: `{args.out_inventory_csv}`",
        f"- summary CSV: `{args.out_summary_csv}`",
        f"- report: `{args.out_report}`",
        "",
        "## Final guardrails",
        "",
        "- No current_best overwrite.",
        "- No C export.",
        "- No public benchmark.",
        "- No promotion.",
        "- Do not add local checkpoint artifacts to git.",
        "",
    ])

    args.out_report.parent.mkdir(parents=True, exist_ok=True)
    args.out_report.write_text("\n".join(lines), encoding="utf-8")

    print("plan_decision:", plan_decision)
    print("inventory_rows:", len(inventory))
    print("direct_model_eval_ready_files:", len(direct_ready))
    print("already_compared_guard_output_files:", len(guard_ready))
    print("needs_board_join_adapter_files:", len(needs_board_join))
    print("needs_target_adapter_files:", len(needs_target_adapter))
    print("run1_trainable_guard_rows:", len(trainable_rows))
    print("run1_bucket_guard_rows:", len(bucket_rows))
    print("run1_anchor_guard_rows:", len(anchor_rows))
    print("out_inventory_csv:", args.out_inventory_csv)
    print("out_summary_csv:", args.out_summary_csv)
    print("out_report:", args.out_report)
    print("input audit only; no training; no checkpoint read/write; no C export; no benchmark; no promotion")


if __name__ == "__main__":
    main()
