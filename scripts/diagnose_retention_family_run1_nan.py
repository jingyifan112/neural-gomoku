#!/usr/bin/env python3
"""
Diagnose retention-family wrapper run1 NaN loss.

Read-only diagnostic:
- no training
- no checkpoint save
- no C export
- no benchmark
- no promotion
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


DEFAULT_RUN_DIR = Path("analysis/integration_eval/retention_family_wrapper_run1")
DEFAULT_TRAIN_DATASET = DEFAULT_RUN_DIR / "train_plain_dataset.json"
DEFAULT_TRAIN_BEFORE = DEFAULT_RUN_DIR / "train_before.csv"
DEFAULT_TRAIN_AFTER = DEFAULT_RUN_DIR / "train_after.csv"
DEFAULT_TRAIN_EVAL = DEFAULT_RUN_DIR / "train_script_eval.csv"
DEFAULT_TRAIN_REPORT = DEFAULT_RUN_DIR / "train_script_report.md"
DEFAULT_GATE_JSON = DEFAULT_RUN_DIR / "gate_eval.json"
DEFAULT_WRAPPER_JSON = DEFAULT_RUN_DIR / "wrapper_result.json"
DEFAULT_TRAIN_SCRIPT = Path("scripts/train_teacher_divergence_policy_mixed_ce_anchor_probe.py")

DEFAULT_OUT_CSV = Path("analysis/integration_eval/retention_family_run1_nan_diagnosis.csv")
DEFAULT_OUT_JSON = Path("analysis/integration_eval/retention_family_run1_nan_diagnosis.json")
DEFAULT_OUT_MD = Path("analysis/integration_eval/retention_family_run1_nan_diagnosis.md")


def clean(v: Any) -> str:
    if v is None:
        return ""
    return str(v).strip()


def is_blank(v: Any) -> bool:
    return clean(v).lower() in {"", "none", "nan", "null"}


def parse_move(v: Any) -> Tuple[Optional[int], Optional[int], str]:
    if is_blank(v):
        return None, None, "missing"
    nums = re.findall(r"-?\d+", str(v))
    if len(nums) < 2:
        return None, None, f"unparseable:{v}"
    return int(nums[0]), int(nums[1]), "ok"


def parse_float(v: Any) -> Tuple[Optional[float], str]:
    if is_blank(v):
        return None, "missing"
    try:
        x = float(str(v))
    except Exception:
        return None, f"unparseable:{v}"
    if not math.isfinite(x):
        return x, "nonfinite"
    return x, "ok"


def norm_col(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", s.strip().lower()).strip("_")


def get_any(row: Dict[str, Any], names: Sequence[str], default: str = "") -> str:
    by_norm = {norm_col(k): k for k in row.keys()}
    for n in names:
        k = by_norm.get(norm_col(n))
        if k is not None and not is_blank(row.get(k)):
            return clean(row.get(k))
    return default


def read_json_rows(path: Path) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(obj, dict) and isinstance(obj.get("rows"), list):
        return obj.get("metadata", {}), obj["rows"]
    if isinstance(obj, list):
        return {}, obj
    raise SystemExit(f"ERROR: no rows in {path}")


def read_csv(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as f:
        return [dict(r) for r in csv.DictReader(f)]


def adapter_meta(row: Dict[str, Any]) -> Dict[str, Any]:
    meta = row.get("retention_family_consumer_adapter")
    return meta if isinstance(meta, dict) else {}


def find_board(row: Dict[str, Any]) -> Any:
    for k in ("board", "board_grid", "grid", "position"):
        if k in row:
            return row[k]
    return None


def parse_board(board: Any) -> Tuple[Optional[List[List[str]]], str]:
    if board is None:
        return None, "missing"

    if isinstance(board, list):
        # matrix list
        if all(isinstance(r, list) for r in board):
            try:
                return [[str(c) for c in r] for r in board], "matrix_list"
            except Exception as e:
                return None, f"matrix_error:{e}"

        # list of text lines
        if all(isinstance(r, str) for r in board):
            return [list(r.strip()) for r in board if r.strip()], "line_list"

    if isinstance(board, str):
        lines = [ln.strip() for ln in board.splitlines() if ln.strip()]
        # Remove spaces for text grids.
        rows = [re.sub(r"\s+", "", ln) for ln in lines]
        if rows:
            return [list(r) for r in rows], "text_grid"

    return None, f"unsupported:{type(board).__name__}"


def cell_status(grid: Optional[List[List[str]]], x: Optional[int], y: Optional[int]) -> str:
    if grid is None:
        return "unknown_no_board"
    if x is None or y is None:
        return "unknown_no_target"
    if y < 0 or y >= len(grid):
        return "out_of_bounds_y"
    if x < 0 or x >= len(grid[y]):
        return "out_of_bounds_x"
    cell = grid[y][x]
    if cell in {".", "0", "_", "-", " "}:
        return "empty"
    return f"occupied:{cell}"


def row_key_from_adapter(row: Dict[str, Any]) -> str:
    meta = adapter_meta(row)
    family = clean(meta.get("family_id"))
    source = clean(meta.get("source"))
    target = clean(meta.get("policy_target"))
    return "|".join([family, source, target])


def row_key_from_probe(row: Dict[str, str]) -> str:
    return "|".join([
        get_any(row, ["family_id"]),
        get_any(row, ["source"]),
        get_any(row, ["policy_target"]),
    ])


def index_csv(rows: List[Dict[str, str]]) -> Dict[str, Dict[str, str]]:
    out = {}
    for r in rows:
        out[row_key_from_probe(r)] = r
    return out


def extract_training_log_observations(report: Path) -> Dict[str, Any]:
    if not report.exists():
        return {"report_exists": False}

    text = report.read_text(encoding="utf-8", errors="replace")
    return {
        "report_exists": True,
        "contains_nan": "nan" in text.lower(),
        "contains_loss_nan": "loss=nan" in text.lower(),
        "line_count": len(text.splitlines()),
    }


def script_excerpt(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    patterns = [
        "strict split check failed",
        "split_counts",
        "label_type",
        "policy_target",
        "target",
        "weight",
        "cross_entropy",
        "nll",
        "log_softmax",
        "nan",
        "main_ce",
        "anchor_kl",
    ]
    hits = []
    for i, line in enumerate(lines, 1):
        low = line.lower()
        if any(p.lower() in low for p in patterns):
            hits.append({"line": i, "text": line.rstrip()})
    return hits


def summarize_probe(before: Dict[str, str], after: Dict[str, str]) -> Dict[str, Any]:
    out = {}
    for prefix, row in [("before", before), ("after", after)]:
        for field in ["target_rank", "target_prob", "top1"]:
            out[f"{prefix}_{field}"] = get_any(row, [field])
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--train-dataset", type=Path, default=DEFAULT_TRAIN_DATASET)
    ap.add_argument("--train-before-csv", type=Path, default=DEFAULT_TRAIN_BEFORE)
    ap.add_argument("--train-after-csv", type=Path, default=DEFAULT_TRAIN_AFTER)
    ap.add_argument("--train-eval-csv", type=Path, default=DEFAULT_TRAIN_EVAL)
    ap.add_argument("--train-report", type=Path, default=DEFAULT_TRAIN_REPORT)
    ap.add_argument("--gate-json", type=Path, default=DEFAULT_GATE_JSON)
    ap.add_argument("--wrapper-json", type=Path, default=DEFAULT_WRAPPER_JSON)
    ap.add_argument("--train-script", type=Path, default=DEFAULT_TRAIN_SCRIPT)
    ap.add_argument("--out-csv", type=Path, default=DEFAULT_OUT_CSV)
    ap.add_argument("--out-json", type=Path, default=DEFAULT_OUT_JSON)
    ap.add_argument("--out-md", type=Path, default=DEFAULT_OUT_MD)
    args = ap.parse_args()

    dataset_meta, rows = read_json_rows(args.train_dataset)
    before_idx = index_csv(read_csv(args.train_before_csv))
    after_idx = index_csv(read_csv(args.train_after_csv))
    train_eval_rows = read_csv(args.train_eval_csv)

    row_reports: List[Dict[str, Any]] = []
    all_findings: List[str] = []

    for idx, row in enumerate(rows, 1):
        meta = adapter_meta(row)
        key = row_key_from_adapter(row)

        target_raw = (
            clean(meta.get("policy_target"))
            or get_any(row, ["policy_target", "target", "target_move", "teacher_move"])
        )
        tx, ty, target_parse_status = parse_move(target_raw)

        board, board_format = parse_board(find_board(row))
        board_shape = ""
        if board is not None:
            board_shape = f"{len(board)}x{len(board[0]) if board else 0}"

        cell = cell_status(board, tx, ty)

        weight_raw = get_any(row, ["weight", "sample_weight", "loss_weight"], default="1.0")
        weight, weight_status = parse_float(weight_raw)

        label_type = get_any(row, ["label_type"])
        role = get_any(row, ["role"])
        split = get_any(row, ["split"])

        before = before_idx.get(key, {})
        after = after_idx.get(key, {})
        probe_summary = summarize_probe(before, after)

        findings: List[str] = []
        if target_parse_status != "ok":
            findings.append(f"target_parse_{target_parse_status}")
        if cell != "empty":
            findings.append(f"target_cell_{cell}")
        if weight_status != "ok":
            findings.append(f"weight_{weight_status}")
        elif weight is not None and weight <= 0:
            findings.append("weight_nonpositive")
        if label_type not in {"teacher_divergence", "heldout_retention_anchor", "nonheldout_retention_anchor", "heldout_retention_gate"}:
            findings.append(f"unusual_label_type:{label_type}")
        if not before:
            findings.append("missing_train_before_probe")
        if not after:
            findings.append("missing_train_after_probe")
        if before and after:
            br, bs = parse_float(get_any(before, ["target_rank"]))
            ar, astatus = parse_float(get_any(after, ["target_rank"]))
            if bs == "ok" and astatus == "ok" and ar is not None and br is not None and ar > br:
                findings.append("train_rank_regressed")

        all_findings.extend(findings)

        row_reports.append({
            "adapter_row_index": idx,
            "key": key,
            "family_id": clean(meta.get("family_id")),
            "source": clean(meta.get("source")),
            "policy_target": target_raw,
            "target_parse_status": target_parse_status,
            "target_x": "" if tx is None else tx,
            "target_y": "" if ty is None else ty,
            "board_format": board_format,
            "board_shape": board_shape,
            "target_cell_status": cell,
            "split": split,
            "role": role,
            "label_type": label_type,
            "train_use_policy": clean(meta.get("train_use_policy")),
            "eval_use_policy": clean(meta.get("eval_use_policy")),
            "gate_scope": clean(meta.get("gate_scope")),
            "risk_flags": clean(meta.get("risk_flags")),
            "weight_raw": weight_raw,
            "weight_status": weight_status,
            "findings": ";".join(findings),
            **probe_summary,
        })

    wrapper = json.loads(args.wrapper_json.read_text(encoding="utf-8")) if args.wrapper_json.exists() else {}
    gate = json.loads(args.gate_json.read_text(encoding="utf-8")) if args.gate_json.exists() else {}

    train_log_obs = extract_training_log_observations(args.train_report)
    script_hits = script_excerpt(args.train_script)

    finding_counts = Counter(all_findings)
    split_counts = Counter(r["split"] for r in row_reports)
    label_type_counts = Counter(r["label_type"] for r in row_reports)
    cell_counts = Counter(r["target_cell_status"] for r in row_reports)
    board_format_counts = Counter(r["board_format"] for r in row_reports)

    likely_causes = []
    if train_log_obs.get("contains_nan") or wrapper.get("overall_status") == "gates_failed":
        likely_causes.append("run1_training_report_or_wrapper_records_failed_probe")
    if any(r["target_cell_status"] != "empty" for r in row_reports):
        likely_causes.append("one_or_more_train_targets_are_not_empty")
    if any(r["target_parse_status"] != "ok" for r in row_reports):
        likely_causes.append("one_or_more_train_targets_are_unparseable")
    if any("unusual_label_type" in r["findings"] for r in row_reports):
        likely_causes.append("adapter_role_label_type_may_not_be_supported_by_legacy_training_script")
    if not likely_causes:
        likely_causes.append("no_row_level_target_or_weight_issue_detected; inspect legacy CE/KL computation for two-row adapter dataset")

    summary = {
        "scope": "run1 NaN diagnosis only; no training/checkpoint/C export/benchmark/promotion",
        "inputs": {
            "train_dataset": str(args.train_dataset),
            "train_before_csv": str(args.train_before_csv),
            "train_after_csv": str(args.train_after_csv),
            "train_eval_csv": str(args.train_eval_csv),
            "train_report": str(args.train_report),
            "gate_json": str(args.gate_json),
            "wrapper_json": str(args.wrapper_json),
            "train_script": str(args.train_script),
        },
        "dataset_meta": dataset_meta,
        "row_count": len(rows),
        "split_counts": dict(sorted(split_counts.items())),
        "label_type_counts": dict(sorted(label_type_counts.items())),
        "target_cell_counts": dict(sorted(cell_counts.items())),
        "board_format_counts": dict(sorted(board_format_counts.items())),
        "finding_counts": dict(sorted(finding_counts.items())),
        "wrapper_status": {
            "overall_status": wrapper.get("overall_status"),
            "gates_passed": wrapper.get("gates_passed"),
            "checkpoint_action": wrapper.get("checkpoint_action", {}),
        },
        "gate_status": {
            "decision": gate.get("decision"),
            "failures": gate.get("failures"),
            "counts": gate.get("counts"),
        },
        "train_report_observations": train_log_obs,
        "likely_causes": likely_causes,
        "row_reports": row_reports,
        "training_script_relevant_lines": script_hits,
    }

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    fields = [
        "adapter_row_index", "family_id", "source", "policy_target", "target_parse_status",
        "target_x", "target_y", "board_format", "board_shape", "target_cell_status",
        "split", "role", "label_type", "train_use_policy", "eval_use_policy",
        "gate_scope", "risk_flags", "weight_raw", "weight_status",
        "before_target_rank", "after_target_rank", "before_target_prob", "after_target_prob",
        "before_top1", "after_top1", "findings",
    ]
    with args.out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        for r in row_reports:
            w.writerow({k: r.get(k, "") for k in fields})

    def md_table(headers: Sequence[str], values: Sequence[Sequence[Any]]) -> str:
        lines = []
        lines.append("| " + " | ".join(headers) + " |")
        lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
        for row in values:
            cells = [str(x).replace("\n", " ").replace("|", "\\|") for x in row]
            lines.append("| " + " | ".join(cells) + " |")
        return "\n".join(lines)

    md: List[str] = []
    md.append("# Retention family run1 NaN diagnosis")
    md.append("")
    md.append("Scope: run1 NaN diagnosis only. No training, checkpoint save, C export, benchmark, or promotion was run.")
    md.append("")
    md.append("## Run1 status")
    md.append("")
    md.append(f"- wrapper overall_status: `{summary['wrapper_status']['overall_status']}`")
    md.append(f"- gates_passed: `{summary['wrapper_status']['gates_passed']}`")
    md.append(f"- checkpoint_action: `{summary['wrapper_status']['checkpoint_action'].get('action', '')}`")
    md.append(f"- gate decision: `{summary['gate_status']['decision']}`")
    md.append(f"- gate failures: `{summary['gate_status']['failures']}`")
    md.append("")
    md.append("## Dataset summary")
    md.append("")
    md.append(f"- row_count: {len(rows)}")
    md.append(f"- split_counts: `{summary['split_counts']}`")
    md.append(f"- label_type_counts: `{summary['label_type_counts']}`")
    md.append(f"- target_cell_counts: `{summary['target_cell_counts']}`")
    md.append(f"- board_format_counts: `{summary['board_format_counts']}`")
    md.append(f"- finding_counts: `{summary['finding_counts']}`")
    md.append("")
    md.append("## Train rows")
    md.append("")
    md.append(md_table(
        ["idx", "family", "target", "cell", "label_type", "before_rank", "after_rank", "before_prob", "after_prob", "findings"],
        [
            [
                r["adapter_row_index"], r["family_id"], r["policy_target"],
                r["target_cell_status"], r["label_type"],
                r.get("before_target_rank", ""), r.get("after_target_rank", ""),
                r.get("before_target_prob", ""), r.get("after_target_prob", ""),
                r["findings"],
            ]
            for r in row_reports
        ],
    ))
    md.append("")
    md.append("## Likely causes")
    md.append("")
    for c in likely_causes:
        md.append(f"- `{c}`")
    md.append("")
    md.append("## Training-script relevant lines")
    md.append("")
    md.append(md_table(
        ["line", "text"],
        [[h["line"], h["text"]] for h in script_hits[:80]],
    ))
    md.append("")
    md.append("## Interpretation")
    md.append("")
    md.append("This diagnosis separates row-level adapter data validity from legacy training-script compatibility. If train targets are parseable, empty, and finite-weight, then the NaN is more likely caused by how the legacy mixed-CE training script handles the tiny two-row adapter dataset or the adapter role/label_type semantics.")
    md.append("")
    md.append("## Explicit non-actions")
    md.append("")
    md.append("- No model training was run by this diagnosis.")
    md.append("- No checkpoint was saved.")
    md.append("- No C weights were exported.")
    md.append("- No benchmark was run.")
    md.append("- No promotion decision was made.")
    md.append("")

    args.out_md.write_text("\n".join(md).rstrip() + "\n", encoding="utf-8")

    print("wrote", args.out_csv)
    print("wrote", args.out_json)
    print("wrote", args.out_md)
    print("row_count", len(rows))
    print("finding_counts", dict(sorted(finding_counts.items())))
    print("likely_causes", likely_causes)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
