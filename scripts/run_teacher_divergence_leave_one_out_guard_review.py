#!/usr/bin/env python3
from __future__ import annotations

import copy
import csv
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


SOURCE_DATASET = Path("analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_conservative_selection_next.json")
ANCHORS = Path("analysis/public_benchmark_eval/corpus8_selected_board_snapshots.json")
B4C96 = Path("checkpoints/probes/15x15_capacity_data_pairing_b4c96_probe_candidate.pt")
WRAPPER = Path("scripts/probe_policy_rank_topk_protected_nosave_b4c96.py")
BASELINE_SUMMARY = Path("analysis/integration_eval/teacher_divergence_next_nosave_probe/nosave_probe_summary.csv")

OUT_DIR = Path("analysis/integration_eval/teacher_divergence_row_level_guard_review")
DATASET_DIR = OUT_DIR / "leave_one_out_datasets"
LOG_DIR = Path("eval_logs/integration_eval/teacher_divergence_row_level_guard_review")

OUT_SUMMARY_CSV = OUT_DIR / "leave_one_out_summary.csv"
OUT_SUMMARY_JSON = OUT_DIR / "leave_one_out_summary.json"
OUT_REPORT = OUT_DIR / "leave_one_out_report.md"

TRAIN_CASE_IDS = [
    "legacy_g4_m13",
    "legacy_g4_m23",
    "legacy_g5_m28",
    "legacy_g6_m17",
]

COMMON_WEIGHTS = {
    "epochs": "3",
    "lr": "1e-6",
    "margin": "0.25",
    "ce_weight": "1.0",
    "pair_weight": "0.5",
    "worst_weight": "0.3",
    "anchor_kl_weight": "1.0",
    "seed": "37",
}


def require(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(path)


def case_id_of(sample: dict[str, Any]) -> str:
    cid = sample.get("case_id") or sample.get("id")
    if not cid:
        raise ValueError("sample missing case_id/id")
    return str(cid)


def read_json(path: Path) -> dict[str, Any]:
    require(path)
    return json.loads(path.read_text(encoding="utf-8"))


def extract_verdict(report_path: Path) -> str:
    text = report_path.read_text(encoding="utf-8")
    match = re.search(r"## Verdict\s*\n\s*([A-Z0-9_]+)", text)
    return match.group(1) if match else "UNKNOWN"


def materialize_variant(source: dict[str, Any], drop_case_id: str) -> Path:
    out = copy.deepcopy(source)

    original_train = list(out["samples"])
    kept_train = [s for s in original_train if case_id_of(s) != drop_case_id]
    dropped = [s for s in original_train if case_id_of(s) == drop_case_id]

    if len(dropped) != 1:
        raise ValueError(f"expected to drop exactly one row for {drop_case_id}, got {len(dropped)}")
    if len(kept_train) != len(original_train) - 1:
        raise ValueError("unexpected kept_train count")

    out["samples"] = kept_train
    out["name"] = f"teacher_divergence_leave_one_out_drop_{drop_case_id}"
    out["description"] = (
        "Leave-one-train-candidate-out no-save guard review dataset. "
        "Protected/tail/quarantine groups are unchanged."
    )
    out["leave_one_out_metadata"] = {
        "source_dataset": str(SOURCE_DATASET),
        "drop_case_id": drop_case_id,
        "kept_train_case_ids": [case_id_of(s) for s in kept_train],
        "dropped_train_case_ids": [drop_case_id],
        "scope": "no-save guard review only; no checkpoint/export/benchmark/promotion",
    }

    DATASET_DIR.mkdir(parents=True, exist_ok=True)
    out_path = DATASET_DIR / f"drop_{drop_case_id}.json"
    out_path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return out_path


def run_variant(drop_case_id: str, dataset_path: Path) -> tuple[Path, Path]:
    variant = f"drop_{drop_case_id}"
    out_csv = OUT_DIR / f"{variant}_group_metrics.csv"
    out_report = OUT_DIR / f"{variant}_report.md"
    log_path = LOG_DIR / f"{variant}.log"

    cmd = [
        sys.executable,
        str(WRAPPER),
        "--dataset",
        str(dataset_path),
        "--anchor-snapshots",
        str(ANCHORS),
        "--init-checkpoint",
        str(B4C96),
        "--reference-checkpoint",
        str(B4C96),
        "--board-size",
        "15",
        "--win-length",
        "5",
        "--channels",
        "96",
        "--blocks",
        "4",
        "--epochs",
        COMMON_WEIGHTS["epochs"],
        "--lr",
        COMMON_WEIGHTS["lr"],
        "--margin",
        COMMON_WEIGHTS["margin"],
        "--ce-weight",
        COMMON_WEIGHTS["ce_weight"],
        "--pair-weight",
        COMMON_WEIGHTS["pair_weight"],
        "--worst-weight",
        COMMON_WEIGHTS["worst_weight"],
        "--anchor-kl-weight",
        COMMON_WEIGHTS["anchor_kl_weight"],
        "--weight-decay",
        "1e-5",
        "--seed",
        COMMON_WEIGHTS["seed"],
        "--print-every",
        "1",
        "--out-csv",
        str(out_csv),
        "--out-report",
        str(out_report),
    ]

    env = os.environ.copy()
    old_pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = "src" if not old_pythonpath else f"src:{old_pythonpath}"

    print()
    print(f"=== run {variant} ===")
    print("dataset:", dataset_path)
    print(" ".join(cmd), flush=True)

    proc = subprocess.run(cmd, text=True, capture_output=True, env=env)
    log_path.write_text(proc.stdout + proc.stderr, encoding="utf-8")

    print(proc.stdout, end="")
    if proc.stderr:
        print(proc.stderr, end="", file=sys.stderr)

    if proc.returncode != 0:
        raise RuntimeError(f"{variant} failed with exit code {proc.returncode}; see {log_path}")

    require(out_csv)
    require(out_report)
    return out_csv, out_report


def load_group_metrics(csv_path: Path, report_path: Path, drop_case_id: str, dataset_path: Path) -> list[dict[str, Any]]:
    verdict = extract_verdict(report_path)
    rows: list[dict[str, Any]] = []
    with csv_path.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append(
                {
                    "variant": f"drop_{drop_case_id}",
                    "drop_case_id": drop_case_id,
                    "dataset": str(dataset_path),
                    "verdict": verdict,
                    "group": r["group"],
                    "rows_after": r["rows_after"],
                    "top5_delta": r["top5_delta"],
                    "top10_delta": r["top10_delta"],
                    "rank_gt50_delta": r["rank_gt50_delta"],
                    "mean_rank_delta": r["mean_rank_delta"],
                    "mean_target_prob_delta": r["mean_target_prob_delta"],
                    "mean_worst_gap_delta": r["mean_worst_gap_delta"],
                    "hinge_delta": r["mean_pair_hinge_margin_025_delta"],
                    "teacher_beats_worst_delta": r["teacher_beats_worst_delta"],
                    "teacher_beats_all_delta": r["teacher_beats_all_delta"],
                }
            )
    return rows


def group_row(rows: list[dict[str, Any]], group: str) -> dict[str, Any]:
    matches = [r for r in rows if r["group"] == group]
    if len(matches) != 1:
        raise ValueError(f"expected one {group}, got {len(matches)}")
    return matches[0]


def f(row: dict[str, Any], key: str) -> float:
    return float(row[key])


def classify_variant(rows: list[dict[str, Any]]) -> str:
    protected = group_row(rows, "protected_eval_top10")
    tail = group_row(rows, "tail_eval_rank_gt50")
    train = group_row(rows, "train_main_rank_11_50")

    protected_safe = (
        f(protected, "top5_delta") >= 0
        and f(protected, "top10_delta") >= 0
        and f(protected, "rank_gt50_delta") <= 0
    )
    tail_safe = (
        f(tail, "top10_delta") >= 0
        and f(tail, "rank_gt50_delta") <= 0
        and f(tail, "mean_rank_delta") <= 0
    )
    train_still_useful = (
        f(train, "top10_delta") >= 0
        and f(train, "rank_gt50_delta") <= 0
        and f(train, "mean_rank_delta") <= 0
    )

    if protected_safe and tail_safe and train_still_useful:
        return "PASS_LEAVE_ONE_OUT_GUARDS_AND_TRAIN"
    if protected_safe and tail_safe:
        return "PASS_LEAVE_ONE_OUT_GUARDS_ONLY"
    if f(tail, "rank_gt50_delta") <= 0 and f(protected, "top5_delta") >= 0:
        return "PARTIAL_GUARD_RECOVERY"
    return "FAIL_LEAVE_ONE_OUT_GUARDS"


def main() -> int:
    for p in [SOURCE_DATASET, ANCHORS, B4C96, WRAPPER, BASELINE_SUMMARY]:
        require(p)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DATASET_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    source = read_json(SOURCE_DATASET)
    actual_train_ids = [case_id_of(s) for s in source["samples"]]
    if actual_train_ids != TRAIN_CASE_IDS:
        raise ValueError(f"unexpected train ids: {actual_train_ids}")

    all_rows: list[dict[str, Any]] = []
    variant_decisions: list[dict[str, Any]] = []

    for drop_case_id in TRAIN_CASE_IDS:
        dataset_path = materialize_variant(source, drop_case_id)
        csv_path, report_path = run_variant(drop_case_id, dataset_path)
        rows = load_group_metrics(csv_path, report_path, drop_case_id, dataset_path)
        decision = classify_variant(rows)
        all_rows.extend(rows)

        protected = group_row(rows, "protected_eval_top10")
        tail = group_row(rows, "tail_eval_rank_gt50")
        train = group_row(rows, "train_main_rank_11_50")

        variant_decisions.append(
            {
                "variant": f"drop_{drop_case_id}",
                "drop_case_id": drop_case_id,
                "decision": decision,
                "train_top10_delta": f(train, "top10_delta"),
                "train_mean_rank_delta": f(train, "mean_rank_delta"),
                "protected_top5_delta": f(protected, "top5_delta"),
                "protected_top10_delta": f(protected, "top10_delta"),
                "protected_prob_delta": f(protected, "mean_target_prob_delta"),
                "tail_top10_delta": f(tail, "top10_delta"),
                "tail_rank_gt50_delta": f(tail, "rank_gt50_delta"),
                "tail_mean_rank_delta": f(tail, "mean_rank_delta"),
                "tail_prob_delta": f(tail, "mean_target_prob_delta"),
            }
        )

    fields = [
        "variant",
        "drop_case_id",
        "dataset",
        "verdict",
        "group",
        "rows_after",
        "top5_delta",
        "top10_delta",
        "rank_gt50_delta",
        "mean_rank_delta",
        "mean_target_prob_delta",
        "mean_worst_gap_delta",
        "hinge_delta",
        "teacher_beats_worst_delta",
        "teacher_beats_all_delta",
    ]
    with OUT_SUMMARY_CSV.open("w", newline="", encoding="utf-8") as fcsv:
        w = csv.DictWriter(fcsv, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        for r in all_rows:
            w.writerow({k: r.get(k, "") for k in fields})

    pass_guard = [v for v in variant_decisions if v["decision"].startswith("PASS")]
    partial = [v for v in variant_decisions if v["decision"] == "PARTIAL_GUARD_RECOVERY"]

    final_decision = (
        "LEAVE_ONE_OUT_FOUND_GUARD_SAFE_SUBSET"
        if pass_guard
        else "LEAVE_ONE_OUT_NO_GUARD_SAFE_SUBSET"
    )

    summary = {
        "decision": final_decision,
        "scope": "leave-one-train-candidate-out no-save guard review only; no checkpoint/export/benchmark/promotion",
        "source_dataset": str(SOURCE_DATASET),
        "baseline_summary": str(BASELINE_SUMMARY),
        "train_case_ids": TRAIN_CASE_IDS,
        "variant_decisions": variant_decisions,
        "pass_guard_variants": pass_guard,
        "partial_guard_recovery_variants": partial,
        "outputs": {
            "summary_csv": str(OUT_SUMMARY_CSV),
            "summary_json": str(OUT_SUMMARY_JSON),
            "report": str(OUT_REPORT),
        },
    }
    OUT_SUMMARY_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines: list[str] = []
    lines += ["# Teacher-divergence leave-one-out guard review", ""]
    lines += ["## Scope", ""]
    lines += [
        "- Leave-one-train-candidate-out no-save probes only.",
        "- No checkpoint save.",
        "- No C export, no public benchmark, no promotion.",
        "",
    ]

    lines += ["## Baseline failure", ""]
    lines += [
        "The full conservative dataset improved the train group but failed protected/tail guards.",
        "",
        "- protected top5 delta: -1",
        "- tail top10 delta: -1",
        "- tail rank>50 delta: +2",
        "- tail mean rank delta: +24.666667",
        "",
    ]

    lines += ["## Variant decisions", ""]
    lines += [
        "| drop_case_id | decision | train top10 Δ | train mean_rank Δ | protected top5 Δ | protected top10 Δ | tail top10 Δ | tail rank>50 Δ | tail mean_rank Δ |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for v in variant_decisions:
        lines.append(
            f"| {v['drop_case_id']} | {v['decision']} | {v['train_top10_delta']:.6f} | "
            f"{v['train_mean_rank_delta']:.6f} | {v['protected_top5_delta']:.6f} | "
            f"{v['protected_top10_delta']:.6f} | {v['tail_top10_delta']:.6f} | "
            f"{v['tail_rank_gt50_delta']:.6f} | {v['tail_mean_rank_delta']:.6f} |"
        )

    lines += ["", "## Decision", ""]
    lines += [f"`{final_decision}`", ""]

    if pass_guard:
        lines += [
            "At least one leave-one-out variant avoided the guard failures.",
            "",
            "Next step should still be no-save only: materialize the candidate subset and run repeated-seed no-save checks.",
            "",
        ]
    else:
        lines += [
            "No single train-candidate removal produced a guard-safe subset.",
            "",
            "Do not proceed to checkpoint-producing training. Return to data expansion or stronger row-level diagnostics.",
            "",
        ]

    if partial:
        lines += ["## Partial recovery variants", ""]
        for v in partial:
            lines.append(f"- `{v['drop_case_id']}`")
        lines.append("")

    lines += ["## Final note", ""]
    lines += [
        "This review does not authorize checkpoint save, C export, public benchmark, promotion, or current_best overwrite.",
        "",
    ]

    OUT_REPORT.write_text("\n".join(lines), encoding="utf-8")

    print("variant_decisions:")
    for v in variant_decisions:
        print(v)
    print("final_decision:", final_decision)
    print("summary_csv:", OUT_SUMMARY_CSV)
    print("summary_json:", OUT_SUMMARY_JSON)
    print("report:", OUT_REPORT)
    print("status: leave-one-out no-save guard review only; no checkpoint/export/benchmark/promotion")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
