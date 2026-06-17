#!/usr/bin/env python3
"""
Review run2 eval probability regressions.

Read-only review:
- no training
- no checkpoint
- no C export
- no benchmark
- no promotion
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple


DEFAULT_EVAL_ADAPTER_JSON = Path("analysis/integration_eval/retention_family_training_consumer_adapter_eval_dataset.json")
DEFAULT_EVAL_BEFORE_CSV = Path("analysis/integration_eval/retention_family_wrapper_run2_weighted/eval_before.csv")
DEFAULT_EVAL_AFTER_CSV = Path("analysis/integration_eval/retention_family_wrapper_run2_weighted/eval_after.csv")
DEFAULT_GATE_JSON = Path("analysis/integration_eval/retention_family_wrapper_run2_weighted/gate_eval.json")

DEFAULT_OUT_CSV = Path("analysis/integration_eval/retention_family_run2_eval_prob_regression_review.csv")
DEFAULT_OUT_JSON = Path("analysis/integration_eval/retention_family_run2_eval_prob_regression_review.json")
DEFAULT_OUT_MD = Path("analysis/integration_eval/retention_family_run2_eval_prob_regression_review.md")


def clean(v: Any) -> str:
    if v is None:
        return ""
    return str(v).strip()


def norm(s: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in clean(s)).strip("_")


def get_any(row: Dict[str, Any], names: Sequence[str], default: str = "") -> str:
    by_norm = {norm(k): k for k in row.keys()}
    for name in names:
        k = by_norm.get(norm(name))
        if k is not None and clean(row.get(k)):
            return clean(row.get(k))
    return default


def parse_float(v: Any) -> Tuple[float | None, str]:
    s = clean(v)
    if s.lower() in {"", "none", "nan", "null"}:
        return None, "missing"
    try:
        x = float(s)
    except Exception as e:
        return None, f"unparseable:{e}"
    if not math.isfinite(x):
        return x, "nonfinite"
    return x, "finite"


def parse_int(v: Any) -> Tuple[int | None, str]:
    x, status = parse_float(v)
    if x is None:
        return None, status
    return int(x), status


def parse_boolish(v: Any) -> str:
    s = clean(v).lower()
    if s in {"true", "1", "yes", "y"}:
        return "True"
    if s in {"false", "0", "no", "n"}:
        return "False"
    return clean(v)


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return [dict(r) for r in csv.DictReader(f)]


def read_adapter_rows(path: Path) -> List[Dict[str, Any]]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict) or not isinstance(obj.get("rows"), list):
        raise SystemExit(f"ERROR: expected JSON object with rows: {path}")
    return obj["rows"]


def adapter_meta(row: Dict[str, Any]) -> Dict[str, Any]:
    meta = row.get("retention_family_consumer_adapter")
    return meta if isinstance(meta, dict) else {}


def key_from_adapter(row: Dict[str, Any]) -> str:
    meta = adapter_meta(row)
    family = clean(meta.get("family_id"))
    source = clean(meta.get("source"))
    target = clean(meta.get("policy_target") or row.get("policy_target") or row.get("teacher_move"))
    if family or source or target:
        return "|".join([family, source, target])
    return clean(row.get("id"))


def key_from_probe(row: Dict[str, Any]) -> str:
    family = get_any(row, ["family_id"])
    source = get_any(row, ["source"])
    target = get_any(row, ["policy_target", "teacher_move", "target_move"])
    if family or source or target:
        return "|".join([family, source, target])
    return get_any(row, ["id", "row_id"])


def index_probe(rows: List[Dict[str, str]]) -> Dict[str, Dict[str, str]]:
    out: Dict[str, Dict[str, str]] = {}
    for row in rows:
        out[key_from_probe(row)] = row
    return out


def row_summary(row: Dict[str, Any]) -> Dict[str, str]:
    return {
        "target_rank": get_any(row, ["target_rank"]),
        "target_prob": get_any(row, ["target_prob"]),
        "target_ce": get_any(row, ["target_ce"]),
        "top_matches_target": parse_boolish(get_any(row, ["top_matches_target", "top1", "top_matches_reference"])),
        "top_move": get_any(row, ["top_move", "top_legal_move", "top_policy_move"]),
    }


def md_table(headers: Sequence[str], rows: Sequence[Sequence[Any]]) -> str:
    lines = []
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for row in rows:
        cells = [str(x).replace("\n", " ").replace("|", "\\|") for x in row]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--eval-adapter-json", type=Path, default=DEFAULT_EVAL_ADAPTER_JSON)
    ap.add_argument("--eval-before-csv", type=Path, default=DEFAULT_EVAL_BEFORE_CSV)
    ap.add_argument("--eval-after-csv", type=Path, default=DEFAULT_EVAL_AFTER_CSV)
    ap.add_argument("--gate-json", type=Path, default=DEFAULT_GATE_JSON)
    ap.add_argument("--out-csv", type=Path, default=DEFAULT_OUT_CSV)
    ap.add_argument("--out-json", type=Path, default=DEFAULT_OUT_JSON)
    ap.add_argument("--out-md", type=Path, default=DEFAULT_OUT_MD)
    ap.add_argument("--prob-epsilon", type=float, default=0.0)
    args = ap.parse_args()

    adapter_rows = read_adapter_rows(args.eval_adapter_json)
    before_idx = index_probe(read_csv(args.eval_before_csv))
    after_idx = index_probe(read_csv(args.eval_after_csv))
    gate = json.loads(args.gate_json.read_text(encoding="utf-8"))

    review_rows: List[Dict[str, Any]] = []
    missing_before = 0
    missing_after = 0

    for idx, row in enumerate(adapter_rows, 1):
        meta = adapter_meta(row)
        key = key_from_adapter(row)

        before = before_idx.get(key, {})
        after = after_idx.get(key, {})

        if not before:
            missing_before += 1
        if not after:
            missing_after += 1

        b = row_summary(before)
        a = row_summary(after)

        b_prob, b_prob_status = parse_float(b["target_prob"])
        a_prob, a_prob_status = parse_float(a["target_prob"])
        b_rank, b_rank_status = parse_int(b["target_rank"])
        a_rank, a_rank_status = parse_int(a["target_rank"])

        prob_delta = None
        if b_prob is not None and a_prob is not None:
            prob_delta = a_prob - b_prob

        rank_delta = None
        if b_rank is not None and a_rank is not None:
            rank_delta = a_rank - b_rank

        prob_regressed = (
            prob_delta is not None
            and b_prob_status == "finite"
            and a_prob_status == "finite"
            and prob_delta < -args.prob_epsilon
        )
        rank_regressed = (
            rank_delta is not None
            and b_rank_status == "finite"
            and a_rank_status == "finite"
            and rank_delta > 0
        )
        top1_lost = b["top_matches_target"] == "True" and a["top_matches_target"] != "True"

        family_id = clean(meta.get("family_id"))
        target = clean(meta.get("policy_target") or row.get("policy_target") or row.get("teacher_move"))

        is_critical_family = family_id == "bd:ea22cc14729b88fd"
        is_critical_7_9 = is_critical_family and target == "7,9"

        severity = "ok"
        if is_critical_7_9 and (prob_regressed or rank_regressed or top1_lost):
            severity = "critical_gate_regression"
        elif rank_regressed or top1_lost:
            severity = "hard_regression"
        elif prob_regressed:
            severity = "prob_only_regression"

        review_rows.append({
            "eval_row_index": idx,
            "key": key,
            "id": clean(row.get("id")),
            "family_id": family_id,
            "source": clean(meta.get("source")),
            "policy_target": target,
            "gate_scope": clean(meta.get("gate_scope")),
            "allowed_as_only_sibling_family_gate": clean(meta.get("allowed_as_only_sibling_family_gate")),
            "risk_flags": clean(meta.get("risk_flags")),
            "before_rank": "" if b_rank is None else b_rank,
            "after_rank": "" if a_rank is None else a_rank,
            "rank_delta_after_minus_before": "" if rank_delta is None else rank_delta,
            "before_prob": "" if b_prob is None else f"{b_prob:.10g}",
            "after_prob": "" if a_prob is None else f"{a_prob:.10g}",
            "prob_delta_after_minus_before": "" if prob_delta is None else f"{prob_delta:.10g}",
            "prob_regressed": prob_regressed,
            "rank_regressed": rank_regressed,
            "before_top_matches_target": b["top_matches_target"],
            "after_top_matches_target": a["top_matches_target"],
            "top1_lost": top1_lost,
            "before_top_move": b["top_move"],
            "after_top_move": a["top_move"],
            "is_critical_family": is_critical_family,
            "is_critical_7_9": is_critical_7_9,
            "severity": severity,
            "missing_before": not bool(before),
            "missing_after": not bool(after),
        })

    prob_regressions = [r for r in review_rows if r["prob_regressed"]]
    rank_regressions = [r for r in review_rows if r["rank_regressed"]]
    top1_losses = [r for r in review_rows if r["top1_lost"]]
    critical_7_9_rows = [r for r in review_rows if r["is_critical_7_9"]]

    severity_counts = Counter(r["severity"] for r in review_rows)
    family_counts = Counter(r["family_id"] for r in prob_regressions)

    interpretation = []
    if not rank_regressions and not top1_losses and prob_regressions:
        interpretation.append("probability-only regressions: rank/top1 gates stayed stable, but strict probability threshold failed")
    if any(r["is_critical_7_9"] and r["prob_regressed"] for r in review_rows):
        interpretation.append("critical 7,9 probability regressed")
    else:
        interpretation.append("critical 7,9 did not have a probability regression")
    if not prob_regressions:
        interpretation.append("no probability regressions found by review despite gate failure")
    if missing_before or missing_after:
        interpretation.append("one or more rows were missing before/after probe matches")

    payload = {
        "scope": "run2 eval probability regression review only; no training/checkpoint/C export/benchmark/promotion",
        "inputs": {
            "eval_adapter_json": str(args.eval_adapter_json),
            "eval_before_csv": str(args.eval_before_csv),
            "eval_after_csv": str(args.eval_after_csv),
            "gate_json": str(args.gate_json),
            "prob_epsilon": args.prob_epsilon,
        },
        "gate": {
            "decision": gate.get("decision"),
            "failures": gate.get("failures"),
            "counts": gate.get("counts"),
        },
        "counts": {
            "eval_rows": len(review_rows),
            "prob_regressions": len(prob_regressions),
            "rank_regressions": len(rank_regressions),
            "top1_losses": len(top1_losses),
            "critical_7_9_rows": len(critical_7_9_rows),
            "missing_before": missing_before,
            "missing_after": missing_after,
            "severity_counts": dict(sorted(severity_counts.items())),
            "prob_regression_family_counts": dict(sorted(family_counts.items())),
        },
        "interpretation": interpretation,
        "prob_regression_rows": prob_regressions,
        "critical_7_9_rows": critical_7_9_rows,
        "rows": review_rows,
    }

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    csv_fields = [
        "eval_row_index",
        "family_id",
        "source",
        "policy_target",
        "gate_scope",
        "risk_flags",
        "before_rank",
        "after_rank",
        "rank_delta_after_minus_before",
        "before_prob",
        "after_prob",
        "prob_delta_after_minus_before",
        "prob_regressed",
        "rank_regressed",
        "before_top_matches_target",
        "after_top_matches_target",
        "top1_lost",
        "before_top_move",
        "after_top_move",
        "is_critical_7_9",
        "severity",
    ]
    with args.out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=csv_fields, lineterminator="\n")
        w.writeheader()
        for r in review_rows:
            w.writerow({k: r.get(k, "") for k in csv_fields})

    md: List[str] = []
    md.append("# Retention family run2 eval probability regression review")
    md.append("")
    md.append("Scope: run2 eval regression review only. No training, checkpoint, C export, benchmark, or promotion was run.")
    md.append("")
    md.append("## Gate context")
    md.append("")
    md.append(f"- gate decision: `{gate.get('decision')}`")
    md.append(f"- gate failures: `{gate.get('failures')}`")
    md.append(f"- gate counts: `{gate.get('counts')}`")
    md.append("")
    md.append("## Summary")
    md.append("")
    for k, v in payload["counts"].items():
        md.append(f"- {k}: `{v}`")
    md.append("")
    md.append("## Interpretation")
    md.append("")
    for item in interpretation:
        md.append(f"- {item}")
    md.append("")
    md.append("## Probability regression rows")
    md.append("")
    if prob_regressions:
        md.append(md_table(
            [
                "idx", "family", "target", "gate_scope", "before_rank", "after_rank",
                "before_prob", "after_prob", "prob_delta", "critical_7_9", "severity",
            ],
            [
                [
                    r["eval_row_index"],
                    r["family_id"],
                    r["policy_target"],
                    r["gate_scope"],
                    r["before_rank"],
                    r["after_rank"],
                    r["before_prob"],
                    r["after_prob"],
                    r["prob_delta_after_minus_before"],
                    r["is_critical_7_9"],
                    r["severity"],
                ]
                for r in prob_regressions
            ],
        ))
    else:
        md.append("No probability regression rows found.")
    md.append("")
    md.append("## Critical 7,9 rows")
    md.append("")
    if critical_7_9_rows:
        md.append(md_table(
            [
                "idx", "family", "target", "gate_scope", "before_rank", "after_rank",
                "before_prob", "after_prob", "prob_delta", "prob_regressed", "rank_regressed",
            ],
            [
                [
                    r["eval_row_index"],
                    r["family_id"],
                    r["policy_target"],
                    r["gate_scope"],
                    r["before_rank"],
                    r["after_rank"],
                    r["before_prob"],
                    r["after_prob"],
                    r["prob_delta_after_minus_before"],
                    r["prob_regressed"],
                    r["rank_regressed"],
                ]
                for r in critical_7_9_rows
            ],
        ))
    else:
        md.append("No critical 7,9 row found.")
    md.append("")
    md.append("## Full eval review")
    md.append("")
    md.append(md_table(
        [
            "idx", "family", "target", "before_rank", "after_rank",
            "before_prob", "after_prob", "prob_delta", "prob_regressed", "severity",
        ],
        [
            [
                r["eval_row_index"],
                r["family_id"],
                r["policy_target"],
                r["before_rank"],
                r["after_rank"],
                r["before_prob"],
                r["after_prob"],
                r["prob_delta_after_minus_before"],
                r["prob_regressed"],
                r["severity"],
            ]
            for r in review_rows
        ],
    ))
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

    print("wrote", args.out_csv)
    print("wrote", args.out_json)
    print("wrote", args.out_md)
    print("counts", payload["counts"])
    print("interpretation", interpretation)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
