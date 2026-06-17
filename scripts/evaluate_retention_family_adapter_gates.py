#!/usr/bin/env python3
"""
Evaluate retention-family adapter gates from before/after probe CSVs.

This script is gate evaluation only:
- no training
- no checkpoint save
- no C export
- no benchmark
- no promotion

It is intentionally adapter-aware:
- reads train/eval adapter datasets or manifests for metadata
- enforces the critical family rule
- enforces restricted gate_scope rows separately
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple


CRITICAL_FAMILY = "bd:ea22cc14729b88fd"

DEFAULT_OUT_JSON = Path("analysis/integration_eval/retention_family_adapter_gate_eval.json")
DEFAULT_OUT_MD = Path("analysis/integration_eval/retention_family_adapter_gate_eval.md")


def clean(v: Any) -> str:
    if v is None:
        return ""
    return str(v).strip()


def is_blank(v: Any) -> bool:
    return clean(v).lower() in {"", "none", "nan", "null"}


def norm_col(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", s.strip().lower()).strip("_")


def get(row: Dict[str, Any], names: Sequence[str], default: str = "") -> str:
    by_norm = {norm_col(k): k for k in row.keys()}
    for name in names:
        k = by_norm.get(norm_col(name))
        if k is not None and not is_blank(row.get(k)):
            return clean(row.get(k))
    return default


def parse_float(v: Any) -> Optional[float]:
    if is_blank(v):
        return None
    try:
        x = float(str(v).strip())
        return x
    except Exception:
        return None


def norm_move(v: Any) -> str:
    if is_blank(v):
        return ""
    nums = re.findall(r"-?\d+", str(v))
    if len(nums) >= 2:
        return f"{int(nums[0])},{int(nums[1])}"
    return re.sub(r"\s+", "", str(v).strip())


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return [dict(r) for r in csv.DictReader(f)]


def read_json_rows(path: Path) -> List[Dict[str, Any]]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(obj, dict) and isinstance(obj.get("rows"), list):
        return obj["rows"]
    if isinstance(obj, list):
        return obj
    raise SystemExit(f"ERROR: no rows found in {path}")


def adapter_meta(row: Dict[str, Any]) -> Dict[str, Any]:
    meta = row.get("retention_family_consumer_adapter")
    if isinstance(meta, dict):
        return meta
    return {}


def row_key_from_probe(row: Dict[str, str]) -> str:
    family = get(row, ["family_id", "retention_family_id"])
    source = get(row, ["source", "source_id", "case_id", "row_id", "id", "position_id"])
    target = norm_move(get(row, ["policy_target", "target", "target_move", "teacher_move"]))
    split = get(row, ["split"])
    role = get(row, ["role", "label_type"])

    if family or source or target:
        return "|".join([family, source, target])

    fallback = "|".join([
        split,
        role,
        get(row, ["source_path"]),
        norm_move(get(row, ["last_move"])),
        target,
    ])
    return fallback


def row_key_from_adapter_row(row: Dict[str, Any]) -> str:
    meta = adapter_meta(row)
    family = clean(meta.get("family_id"))
    source = clean(meta.get("source"))
    target = norm_move(meta.get("policy_target"))
    if family or source or target:
        return "|".join([family, source, target])

    return "|".join([
        clean(row.get("split")),
        clean(row.get("role")),
        clean(row.get("source_path")),
        norm_move(row.get("last_move")),
        norm_move(row.get("policy_target") or row.get("target") or row.get("teacher_move")),
    ])


def rank_value(row: Dict[str, str]) -> Optional[float]:
    return parse_float(get(row, [
        "target_rank",
        "policy_rank",
        "rank",
        "teacher_rank",
        "target_policy_rank",
        "policy_target_rank",
    ]))


def prob_value(row: Dict[str, str]) -> Optional[float]:
    return parse_float(get(row, [
        "target_prob",
        "policy_prob",
        "prob",
        "teacher_prob",
        "target_policy_prob",
        "policy_target_prob",
    ]))


def top1_value(row: Dict[str, str]) -> Optional[bool]:
    raw = get(row, ["top1", "is_top1", "target_top1", "policy_top1"])
    if raw:
        return raw.lower() in {"1", "true", "yes", "y"}
    r = rank_value(row)
    if r is None:
        return None
    return int(r) == 1


def build_probe_index(rows: List[Dict[str, str]]) -> Dict[str, Dict[str, str]]:
    idx: Dict[str, Dict[str, str]] = {}
    duplicates = Counter()
    for r in rows:
        k = row_key_from_probe(r)
        if k in idx:
            duplicates[k] += 1
        else:
            idx[k] = r
    if duplicates:
        print("warning: duplicate probe keys:", dict(duplicates))
    return idx


def compare_rows(
    side: str,
    adapter_rows: List[Dict[str, Any]],
    before_idx: Dict[str, Dict[str, str]],
    after_idx: Dict[str, Dict[str, str]],
) -> List[Dict[str, Any]]:
    out = []
    for ar in adapter_rows:
        meta = adapter_meta(ar)
        k = row_key_from_adapter_row(ar)
        b = before_idx.get(k)
        a = after_idx.get(k)

        before_rank = rank_value(b) if b else None
        after_rank = rank_value(a) if a else None
        before_prob = prob_value(b) if b else None
        after_prob = prob_value(a) if a else None
        before_top1 = top1_value(b) if b else None
        after_top1 = top1_value(a) if a else None

        prob_delta = None
        abs_prob_drop = None
        if before_prob is not None and after_prob is not None:
            prob_delta = after_prob - before_prob
            abs_prob_drop = max(0.0, before_prob - after_prob)

        rank_regressed = (
            before_rank is not None and after_rank is not None and after_rank > before_rank
        )
        prob_regressed = (
            before_prob is not None and after_prob is not None and after_prob + 1e-12 < before_prob
        )
        rank_improved = (
            before_rank is not None and after_rank is not None and after_rank < before_rank
        )
        prob_improved = (
            before_prob is not None and after_prob is not None and after_prob > before_prob + 1e-12
        )
        top1_lost = before_top1 is True and after_top1 is False

        out.append({
            "side": side,
            "key": k,
            "matched_before": b is not None,
            "matched_after": a is not None,
            "family_id": clean(meta.get("family_id")),
            "source": clean(meta.get("source")),
            "policy_target": norm_move(meta.get("policy_target")),
            "gate_scope": clean(meta.get("gate_scope")),
            "allowed_as_only_sibling_family_gate": clean(meta.get("allowed_as_only_sibling_family_gate")),
            "train_use_policy": clean(meta.get("train_use_policy")),
            "eval_use_policy": clean(meta.get("eval_use_policy")),
            "risk_flags": clean(meta.get("risk_flags")),
            "before_rank": before_rank,
            "after_rank": after_rank,
            "before_prob": before_prob,
            "after_prob": after_prob,
            "prob_delta": prob_delta,
            "abs_prob_drop": abs_prob_drop,
            "before_top1": before_top1,
            "after_top1": after_top1,
            "rank_regressed": rank_regressed,
            "prob_regressed": prob_regressed,
            "rank_improved": rank_improved,
            "prob_improved": prob_improved,
            "top1_lost": top1_lost,
        })
    return out


def classify_prob_regression_for_gate(row: Dict[str, Any], eval_prob_epsilon: float) -> str:
    if not row["prob_regressed"]:
        return "not_regressed"
    if row["side"] != "eval":
        return "non_eval_prob_regression_not_gate_failure"

    if row["rank_regressed"] or row["top1_lost"]:
        return "hard_regression_context"

    if row["family_id"] == CRITICAL_FAMILY and row["policy_target"] == "7,9":
        return "hard_critical_7_9_regression"

    abs_prob_drop = row.get("abs_prob_drop")
    if abs_prob_drop is None:
        return "hard_missing_probability_delta"

    if abs_prob_drop <= eval_prob_epsilon:
        return "warning_prob_only_within_epsilon"

    return "hard_prob_drop_exceeds_epsilon"


def gate_decision(
    comparisons: List[Dict[str, Any]],
    max_eval_rank_regressed: int,
    max_eval_prob_regressed: int,
    require_train_improvement: bool,
) -> Tuple[str, List[str]]:
    failures: List[str] = []

    missing = [r for r in comparisons if not r["matched_before"] or not r["matched_after"]]
    if missing:
        failures.append(f"missing before/after probe rows: {len(missing)}")

    eval_rows = [r for r in comparisons if r["side"] == "eval"]
    train_rows = [r for r in comparisons if r["side"] == "train"]

    eval_rank_regressed = [r for r in eval_rows if r["rank_regressed"]]
    eval_prob_regressed = [r for r in eval_rows if r["prob_regressed"]]
    eval_prob_hard_regressed = [
        r for r in eval_prob_regressed
        if str(r.get("prob_regression_gate_class", "")).startswith("hard_")
    ]
    eval_prob_warnings = [
        r for r in eval_prob_regressed
        if r.get("prob_regression_gate_class") == "warning_prob_only_within_epsilon"
    ]
    eval_top1_lost = [r for r in eval_rows if r["top1_lost"]]

    if len(eval_rank_regressed) > max_eval_rank_regressed:
        failures.append(f"eval rank regressions {len(eval_rank_regressed)} > {max_eval_rank_regressed}")
    if len(eval_prob_hard_regressed) > max_eval_prob_regressed:
        failures.append(
            f"eval hard prob regressions {len(eval_prob_hard_regressed)} > {max_eval_prob_regressed} "
            f"(warnings={len(eval_prob_warnings)})"
        )
    if eval_top1_lost:
        failures.append(f"eval top1 losses: {len(eval_top1_lost)}")

    critical_train_targets = {
        r["policy_target"] for r in train_rows
        if r["family_id"] == CRITICAL_FAMILY
    }
    critical_eval_targets = {
        r["policy_target"] for r in eval_rows
        if r["family_id"] == CRITICAL_FAMILY
    }

    for target in ["7,10", "10,7"]:
        if target not in critical_train_targets:
            failures.append(f"critical target {target} missing from train comparison")
    if "7,9" not in critical_eval_targets:
        failures.append("critical target 7,9 missing from eval comparison")

    for r in eval_rows:
        if r["family_id"] == CRITICAL_FAMILY and r["policy_target"] == "7,9":
            if r["gate_scope"] != "external_or_family_level_only_not_sibling_only":
                failures.append("critical 7,9 wrong gate_scope")
            if r["allowed_as_only_sibling_family_gate"] == "yes":
                failures.append("critical 7,9 incorrectly allowed as only sibling gate")
            if r["rank_regressed"] or r["prob_regressed"] or r["top1_lost"]:
                failures.append("critical 7,9 eval gate regressed")

    if require_train_improvement:
        improved = [r for r in train_rows if r["rank_improved"] or r["prob_improved"]]
        if not improved:
            failures.append("no train-side row improved")

    return ("PASS" if not failures else "FAIL"), failures


def table(headers: List[str], rows: List[List[Any]], max_rows: int = 200) -> str:
    lines = []
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for r in rows[:max_rows]:
        cells = [str(x).replace("\n", " ").replace("|", "\\|") for x in r]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--train-adapter-json", type=Path, required=True)
    ap.add_argument("--eval-adapter-json", type=Path, required=True)
    ap.add_argument("--train-before-csv", type=Path, required=True)
    ap.add_argument("--train-after-csv", type=Path, required=True)
    ap.add_argument("--eval-before-csv", type=Path, required=True)
    ap.add_argument("--eval-after-csv", type=Path, required=True)
    ap.add_argument("--max-eval-rank-regressed", type=int, default=0)
    ap.add_argument("--max-eval-prob-regressed", type=int, default=0)
    ap.add_argument(
        "--eval-prob-epsilon",
        type=float,
        default=0.0,
        help="Absolute eval probability-drop epsilon. Prob-only eval drops within epsilon become warnings.",
    )
    ap.add_argument("--require-train-improvement", action="store_true")
    ap.add_argument("--out-json", type=Path, default=DEFAULT_OUT_JSON)
    ap.add_argument("--out-md", type=Path, default=DEFAULT_OUT_MD)
    ap.add_argument("--fail-exit-code", type=int, default=1)
    args = ap.parse_args()

    if args.eval_prob_epsilon < 0:
        raise SystemExit("ERROR: --eval-prob-epsilon must be non-negative")

    train_adapter_rows = read_json_rows(args.train_adapter_json)
    eval_adapter_rows = read_json_rows(args.eval_adapter_json)

    train_before = read_csv(args.train_before_csv)
    train_after = read_csv(args.train_after_csv)
    eval_before = read_csv(args.eval_before_csv)
    eval_after = read_csv(args.eval_after_csv)

    comparisons = []
    comparisons.extend(compare_rows(
        "train",
        train_adapter_rows,
        build_probe_index(train_before),
        build_probe_index(train_after),
    ))
    comparisons.extend(compare_rows(
        "eval",
        eval_adapter_rows,
        build_probe_index(eval_before),
        build_probe_index(eval_after),
    ))

    for row in comparisons:
        row["prob_regression_gate_class"] = classify_prob_regression_for_gate(
            row,
            eval_prob_epsilon=args.eval_prob_epsilon,
        )

    decision, failures = gate_decision(
        comparisons,
        max_eval_rank_regressed=args.max_eval_rank_regressed,
        max_eval_prob_regressed=args.max_eval_prob_regressed,
        require_train_improvement=args.require_train_improvement,
    )

    side_counts = Counter(r["side"] for r in comparisons)
    eval_rank_regressed = sum(1 for r in comparisons if r["side"] == "eval" and r["rank_regressed"])
    eval_prob_regressed = sum(1 for r in comparisons if r["side"] == "eval" and r["prob_regressed"])
    eval_prob_hard_regressed = sum(
        1 for r in comparisons
        if r["side"] == "eval"
        and r["prob_regressed"]
        and str(r.get("prob_regression_gate_class", "")).startswith("hard_")
    )
    eval_prob_warnings = sum(
        1 for r in comparisons
        if r["side"] == "eval"
        and r.get("prob_regression_gate_class") == "warning_prob_only_within_epsilon"
    )
    train_improved = sum(1 for r in comparisons if r["side"] == "train" and (r["rank_improved"] or r["prob_improved"]))

    payload = {
        "metadata": {
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "scope": "adapter-aware gate evaluation only; no training/checkpoint/C export/benchmark/promotion",
            "train_adapter_json": str(args.train_adapter_json),
            "eval_adapter_json": str(args.eval_adapter_json),
            "train_before_csv": str(args.train_before_csv),
            "train_after_csv": str(args.train_after_csv),
            "eval_before_csv": str(args.eval_before_csv),
            "eval_after_csv": str(args.eval_after_csv),
            "eval_prob_epsilon": args.eval_prob_epsilon,
            "eval_prob_threshold_policy": (
                "prob-only eval drops within epsilon are warnings; rank/top1/critical regressions remain hard failures"
            ),
        },
        "decision": decision,
        "failures": failures,
        "counts": {
            "side_counts": dict(sorted(side_counts.items())),
            "eval_rank_regressed": eval_rank_regressed,
            "eval_prob_regressed": eval_prob_regressed,
            "eval_prob_hard_regressed": eval_prob_hard_regressed,
            "eval_prob_warnings": eval_prob_warnings,
            "eval_prob_epsilon": args.eval_prob_epsilon,
            "train_improved": train_improved,
        },
        "comparisons": comparisons,
    }

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    md = []
    md.append("# Retention family adapter gate evaluation")
    md.append("")
    md.append("Scope: adapter-aware gate evaluation only. No training, checkpoint save, C export, benchmark, or promotion was run.")
    md.append("")
    md.append("## Decision")
    md.append("")
    md.append(f"- decision: `{decision}`")
    md.append(f"- failures: `{failures}`")
    md.append(f"- side counts: `{dict(sorted(side_counts.items()))}`")
    md.append(f"- eval rank regressions: {eval_rank_regressed}")
    md.append(f"- eval prob regressions: {eval_prob_regressed}")
    md.append(f"- eval hard prob regressions: {eval_prob_hard_regressed}")
    md.append(f"- eval prob warnings: {eval_prob_warnings}")
    md.append(f"- eval prob epsilon: {args.eval_prob_epsilon}")
    md.append(f"- train improved rows: {train_improved}")
    md.append("")
    md.append("## Critical family rows")
    md.append("")
    critical = [r for r in comparisons if r["family_id"] == CRITICAL_FAMILY]
    md.append(table(
        [
            "side",
            "target",
            "before_rank",
            "after_rank",
            "before_prob",
            "after_prob",
            "prob_delta",
            "gate_scope",
            "rank_regressed",
            "prob_regressed",
            "prob_gate_class",
        ],
        [
            [
                r["side"],
                r["policy_target"],
                r["before_rank"],
                r["after_rank"],
                r["before_prob"],
                r["after_prob"],
                r["prob_delta"],
                r["gate_scope"],
                r["rank_regressed"],
                r["prob_regressed"],
                r["prob_regression_gate_class"],
            ]
            for r in critical
        ],
    ))
    md.append("")
    md.append("## All comparisons")
    md.append("")
    md.append(table(
        [
            "side",
            "family_id",
            "target",
            "before_rank",
            "after_rank",
            "before_prob",
            "after_prob",
            "prob_delta",
            "rank_regressed",
            "prob_regressed",
            "prob_gate_class",
            "risk_flags",
        ],
        [
            [
                r["side"],
                r["family_id"],
                r["policy_target"],
                r["before_rank"],
                r["after_rank"],
                r["before_prob"],
                r["after_prob"],
                r["prob_delta"],
                r["rank_regressed"],
                r["prob_regressed"],
                r["prob_regression_gate_class"],
                r["risk_flags"],
            ]
            for r in comparisons
        ],
    ))
    md.append("")
    md.append("## Explicit non-actions")
    md.append("")
    md.append("- No model training was run by this evaluator.")
    md.append("- No checkpoint was saved.")
    md.append("- No C weights were exported.")
    md.append("- No benchmark was run.")
    md.append("- No promotion decision was made.")
    md.append("")

    args.out_md.write_text("\n".join(md).rstrip() + "\n", encoding="utf-8")

    print("wrote", args.out_json)
    print("wrote", args.out_md)
    print("decision:", decision)
    print("failures:", failures)
    print("counts:", payload["counts"])

    return 0 if decision == "PASS" else args.fail_exit_code


if __name__ == "__main__":
    raise SystemExit(main())
