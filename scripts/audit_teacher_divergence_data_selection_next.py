#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
from statistics import mean
from typing import Any


BASE_DATASET = Path("analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected.json")
SPLIT_DATASET = Path("analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_protected_train_11_50_weightcap3.json")
FORENSICS_CSV = Path("analysis/integration_eval/b4c96_stagec_failure_forensics.csv")
RUN1_SUMMARY = Path("analysis/integration_eval/b4c96_nosave_objective_ablation_run1/run1_summary.csv")
RUN2_SUMMARY = Path("analysis/integration_eval/b4c96_tail_aware_nosave_ablation_run2/run2_summary.csv")
STOP_REVIEW = Path("analysis/integration_eval/b4c96_capacity_route_stop_review.md")

OUT_DIR = Path("analysis/integration_eval/teacher_divergence_data_selection_next")
OUT_MANIFEST = OUT_DIR / "selection_manifest.csv"
OUT_SUMMARY = OUT_DIR / "selection_summary.json"
OUT_REPORT = OUT_DIR / "selection_report.md"


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def case_id_of(sample: dict[str, Any]) -> str:
    cid = sample.get("case_id") or sample.get("id")
    if not cid:
        raise ValueError(f"sample missing case_id/id: {sample.keys()}")
    return str(cid)


def rank_bucket(rank: int) -> str:
    if rank <= 3:
        return "protected_top3"
    if rank <= 5:
        return "protected_top5"
    if rank <= 10:
        return "protected_top10"
    if rank <= 50:
        return "trainable_rank_11_50"
    return "tail_rank_gt50"


def blob(row: dict[str, str]) -> str:
    return " ".join(str(v) for v in row.values()).lower()


def bool_flag(row: dict[str, str] | None, *needles: str) -> bool:
    if row is None:
        return False
    b = blob(row)
    return any(n.lower() in b for n in needles)


def load_split_roles(split: dict[str, Any]) -> dict[str, str]:
    roles: dict[str, str] = {}
    for key, role in [
        ("samples", "previous_train_rank_11_50"),
        ("protected_eval_samples", "previous_protected_eval_top10"),
        ("tail_eval_samples", "previous_tail_eval_rank_gt50"),
    ]:
        for s in split.get(key, []):
            cid = case_id_of(s)
            if cid in roles:
                raise ValueError(f"duplicate split case_id: {cid}")
            roles[cid] = role
    return roles


def load_forensics_by_case(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    by_case: dict[str, dict[str, str]] = {}
    for r in rows:
        cid = r.get("case_id") or r.get("id")
        if cid:
            by_case[str(cid)] = r
    return by_case


def summarize_run_summary(path: Path) -> dict[str, Any]:
    rows = read_csv_rows(path)
    if not rows:
        return {"path": str(path), "exists": path.exists(), "rows": 0}

    verdicts = sorted(set(r.get("verdict", "") for r in rows))
    group_rows = Counter(r.get("group", "") for r in rows)

    def group_float(group: str, field: str) -> list[float]:
        vals: list[float] = []
        for r in rows:
            if r.get("group") == group and r.get(field, "") not in ["", None]:
                vals.append(float(r[field]))
        return vals

    return {
        "path": str(path),
        "exists": True,
        "rows": len(rows),
        "verdicts": verdicts,
        "group_rows": dict(group_rows),
        "tail_rank_gt50_deltas": group_float("tail_eval_rank_gt50", "rank_gt50_delta"),
        "tail_mean_rank_deltas": group_float("tail_eval_rank_gt50", "mean_rank_delta"),
        "protected_top5_deltas": group_float("protected_eval_top10", "top5_delta"),
        "protected_prob_deltas": group_float("protected_eval_top10", "mean_target_prob_delta"),
        "train_rank_gt50_deltas": group_float("train_main_rank_11_50", "rank_gt50_delta"),
        "all_fail": all("FAIL" in v for v in verdicts if v),
    }


def choose_recommendation(
    *,
    rank: int,
    previous_role: str,
    forensics: dict[str, str] | None,
) -> tuple[str, str, list[str]]:
    flags: list[str] = []

    severe = bool_flag(forensics, "severe_core_regression")
    core_regressed = bool_flag(forensics, "core_regressed")
    protected_regressed = bool_flag(forensics, "protected_top10_regression", "top10_lost", "top5_lost")
    tail_regressed = bool_flag(forensics, "new_tail_rank_gt50", "tail_rank_gt50_after_b")
    rank_regressed = bool_flag(forensics, "rank_regression")
    prob_regressed = bool_flag(forensics, "prob_regression")
    directionally_useful = bool_flag(forensics, "directionally_useful", "core_improved")

    if severe:
        flags.append("severe_core_regression")
    if core_regressed:
        flags.append("core_regressed")
    if protected_regressed:
        flags.append("protected_regression")
    if tail_regressed:
        flags.append("tail_regression")
    if rank_regressed:
        flags.append("rank_regression")
    if prob_regressed:
        flags.append("prob_regression")
    if directionally_useful:
        flags.append("directionally_useful")

    if previous_role == "previous_tail_eval_rank_gt50" or rank > 50:
        return "tail_guard_holdout", "hard_guard", flags

    if previous_role == "previous_protected_eval_top10" or rank <= 10:
        return "protected_guard_holdout", "hard_guard", flags

    if severe or protected_regressed or tail_regressed:
        return "quarantine_regression_sensitive", "high", flags

    if rank_regressed and prob_regressed and not directionally_useful:
        return "quarantine_regression_sensitive", "high", flags

    if 11 <= rank <= 50 and directionally_useful:
        return "train_candidate_review", "medium", flags

    if 11 <= rank <= 50:
        return "train_candidate_review_low_confidence", "medium_high", flags

    return "manual_review", "unknown", flags


def main() -> int:
    base = read_json(BASE_DATASET)
    split = read_json(SPLIT_DATASET)

    samples = list(base.get("samples", []))
    if not samples:
        raise ValueError("base dataset has no samples")

    split_roles = load_split_roles(split)
    forensics_rows = read_csv_rows(FORENSICS_CSV)
    forensics_by_case = load_forensics_by_case(forensics_rows)

    run1 = summarize_run_summary(RUN1_SUMMARY)
    run2 = summarize_run_summary(RUN2_SUMMARY)

    manifest_rows: list[dict[str, Any]] = []
    missing_split = []
    missing_forensics = []

    for s in samples:
        cid = case_id_of(s)
        rank = int(s.get("before_target_rank"))
        previous_role = split_roles.get(cid, "not_in_previous_split")
        if previous_role == "not_in_previous_split":
            missing_split.append(cid)

        fx = forensics_by_case.get(cid)
        if fx is None:
            missing_forensics.append(cid)

        recommendation, risk, flags = choose_recommendation(
            rank=rank,
            previous_role=previous_role,
            forensics=fx,
        )

        manifest_rows.append(
            {
                "case_id": cid,
                "game_number": s.get("game_number", ""),
                "move_count": s.get("move_count", ""),
                "label_type": s.get("label_type", ""),
                "source": s.get("source", ""),
                "before_target_rank": rank,
                "rank_bucket": rank_bucket(rank),
                "before_target_prob": s.get("before_target_prob", ""),
                "before_worst_suppress_gap": s.get("before_worst_suppress_gap", ""),
                "effective_sample_weight": s.get("effective_sample_weight", s.get("sample_weight", "")),
                "target_rc": json.dumps(s.get("target_rc", [])),
                "primary_suppress_rc": json.dumps(s.get("primary_suppress_rc", [])),
                "suppress_count": len(s.get("suppress_rcs", [])),
                "previous_split_role": previous_role,
                "recommended_selection_role": recommendation,
                "selection_risk": risk,
                "selection_flags": ";".join(flags),
                "has_forensics": fx is not None,
            }
        )

    role_counts = Counter(r["recommended_selection_role"] for r in manifest_rows)
    risk_counts = Counter(r["selection_risk"] for r in manifest_rows)
    rank_counts = Counter(r["rank_bucket"] for r in manifest_rows)
    previous_role_counts = Counter(r["previous_split_role"] for r in manifest_rows)

    train_candidates = [
        r for r in manifest_rows
        if r["recommended_selection_role"] in [
            "train_candidate_review",
            "train_candidate_review_low_confidence",
        ]
    ]

    strict_train_candidates = [
        r for r in manifest_rows
        if r["recommended_selection_role"] == "train_candidate_review"
    ]

    summary = {
        "decision": "TEACHER_DIVERGENCE_DATA_SELECTION_AUDIT_READY",
        "scope": "selection audit only; no training/checkpoint/export/benchmark/promotion",
        "inputs": {
            "base_dataset": str(BASE_DATASET),
            "split_dataset": str(SPLIT_DATASET),
            "forensics_csv": str(FORENSICS_CSV),
            "run1_summary": str(RUN1_SUMMARY),
            "run2_summary": str(RUN2_SUMMARY),
            "stop_review": str(STOP_REVIEW),
        },
        "base_rows": len(samples),
        "manifest_rows": len(manifest_rows),
        "missing_split_case_ids": missing_split,
        "missing_forensics_case_ids": missing_forensics,
        "rank_bucket_counts": dict(rank_counts),
        "previous_split_role_counts": dict(previous_role_counts),
        "recommended_role_counts": dict(role_counts),
        "selection_risk_counts": dict(risk_counts),
        "train_candidate_review_rows": len(train_candidates),
        "strict_train_candidate_rows": len(strict_train_candidates),
        "train_candidate_case_ids": [r["case_id"] for r in train_candidates],
        "strict_train_candidate_case_ids": [r["case_id"] for r in strict_train_candidates],
        "hard_guard_case_ids": [
            r["case_id"] for r in manifest_rows
            if r["recommended_selection_role"] in ["protected_guard_holdout", "tail_guard_holdout"]
        ],
        "quarantine_case_ids": [
            r["case_id"] for r in manifest_rows
            if r["recommended_selection_role"] == "quarantine_regression_sensitive"
        ],
        "run1": run1,
        "run2": run2,
        "recommended_next": "manual review of train_candidate_review rows before materializing any new training dataset",
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    fields = [
        "case_id",
        "game_number",
        "move_count",
        "label_type",
        "source",
        "before_target_rank",
        "rank_bucket",
        "before_target_prob",
        "before_worst_suppress_gap",
        "effective_sample_weight",
        "target_rc",
        "primary_suppress_rc",
        "suppress_count",
        "previous_split_role",
        "recommended_selection_role",
        "selection_risk",
        "selection_flags",
        "has_forensics",
    ]

    with OUT_MANIFEST.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        for r in manifest_rows:
            w.writerow({k: r.get(k, "") for k in fields})

    OUT_SUMMARY.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines: list[str] = []
    lines += ["# Teacher-divergence data selection next audit", ""]
    lines += ["## Scope", ""]
    lines += [
        "- Data selection audit only.",
        "- No training.",
        "- No checkpoint read or write.",
        "- No C export, no public benchmark, no promotion.",
        "",
    ]

    lines += ["## Inputs", ""]
    for k, v in summary["inputs"].items():
        lines.append(f"- {k}: `{v}`")
    lines.append("")

    lines += ["## Why this audit exists", ""]
    lines += [
        "The b4c96 capacity route is stopped. Pairing capacity with increased multi-suppress data was completed, but Stage C, run1, and run2 all failed.",
        "",
        "The next safe step is not more b4c96 training. The next safe step is to classify teacher-divergence rows into train candidates, protected guards, tail guards, and quarantine rows.",
        "",
    ]

    lines += ["## Counts", ""]
    lines += [
        f"- base rows: {summary['base_rows']}",
        f"- manifest rows: {summary['manifest_rows']}",
        f"- train_candidate_review rows: {summary['train_candidate_review_rows']}",
        f"- strict_train_candidate rows: {summary['strict_train_candidate_rows']}",
        "",
    ]

    lines += ["## Recommended role counts", ""]
    lines += ["| role | rows |", "|---|---:|"]
    for role, count in sorted(role_counts.items()):
        lines.append(f"| {role} | {count} |")
    lines.append("")

    lines += ["## Risk counts", ""]
    lines += ["| risk | rows |", "|---|---:|"]
    for risk, count in sorted(risk_counts.items()):
        lines.append(f"| {risk} | {count} |")
    lines.append("")

    lines += ["## Rank bucket counts", ""]
    lines += ["| rank_bucket | rows |", "|---|---:|"]
    for bucket, count in sorted(rank_counts.items()):
        lines.append(f"| {bucket} | {count} |")
    lines.append("")

    lines += ["## Candidate lists", ""]
    lines.append("### Strict train candidates")
    if strict_train_candidates:
        for r in strict_train_candidates:
            lines.append(
                f"- `{r['case_id']}` rank={r['before_target_rank']} flags={r['selection_flags'] or 'none'}"
            )
    else:
        lines.append("- none")
    lines.append("")

    lines.append("### All train-candidate review rows")
    if train_candidates:
        for r in train_candidates:
            lines.append(
                f"- `{r['case_id']}` role={r['recommended_selection_role']} "
                f"rank={r['before_target_rank']} risk={r['selection_risk']} flags={r['selection_flags'] or 'none'}"
            )
    else:
        lines.append("- none")
    lines.append("")

    lines.append("### Quarantine rows")
    qrows = [r for r in manifest_rows if r["recommended_selection_role"] == "quarantine_regression_sensitive"]
    if qrows:
        for r in qrows:
            lines.append(
                f"- `{r['case_id']}` rank={r['before_target_rank']} flags={r['selection_flags'] or 'none'}"
            )
    else:
        lines.append("- none")
    lines.append("")

    lines += ["## Interpretation", ""]
    lines += [
        "This audit should not be treated as a final training dataset.",
        "",
        "Rows marked as protected or tail guards should remain held out from ordinary training and used as gate/guard evidence.",
        "",
        "Rows marked as quarantine should not be used for checkpoint-producing training without manual review because previous b4c96 forensics or ablations linked them to protected/tail instability.",
        "",
        "Rows marked as train-candidate review are only candidates for the next materialization step.",
        "",
    ]

    lines += ["## Decision", ""]
    lines += [
        "`TEACHER_DIVERGENCE_DATA_SELECTION_AUDIT_READY`",
        "",
        "Recommended next step: manually review the train-candidate review rows and then materialize a conservative next dataset in a separate branch.",
        "",
    ]

    OUT_REPORT.write_text("\n".join(lines), encoding="utf-8")

    print("base_rows:", len(samples))
    print("manifest:", OUT_MANIFEST)
    print("summary:", OUT_SUMMARY)
    print("report:", OUT_REPORT)
    print("recommended_role_counts:", dict(role_counts))
    print("selection_risk_counts:", dict(risk_counts))
    print("rank_bucket_counts:", dict(rank_counts))
    print("strict_train_candidate_case_ids:", summary["strict_train_candidate_case_ids"])
    print("train_candidate_case_ids:", summary["train_candidate_case_ids"])
    print("quarantine_case_ids:", summary["quarantine_case_ids"])
    print("status: selection audit only; no training/checkpoint/export/benchmark/promotion")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
