#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


OUT_DIR = Path("analysis/integration_eval/teacher_divergence_final_model_scoring")
OUT_SUMMARY = OUT_DIR / "final_model_scoring_summary.json"
OUT_REPORT = OUT_DIR / "final_model_scoring_report.md"


DATASET = Path(
    "analysis/public_benchmark_eval/"
    "rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_conservative_plus_generated_tail_guards_plus_generated_train_candidates_dryrun.json"
)
TRAIN_MATERIALIZATION_SUMMARY = Path(
    "analysis/integration_eval/"
    "teacher_divergence_generated_train_candidate_materialization/"
    "generated_train_candidate_materialization_summary.json"
)
TRAIN_GENERATION_SUMMARY = Path(
    "analysis/integration_eval/"
    "teacher_divergence_train_candidate_generation/"
    "train_candidate_generation_summary.json"
)
TAIL_MATERIALIZATION_SUMMARY = Path(
    "analysis/integration_eval/"
    "teacher_divergence_tail_guard_materialization_dryrun/"
    "tail_guard_materialization_summary.json"
)
NOSAVE_CSV = Path(
    "analysis/integration_eval/"
    "b4c64_expanded_nosave_eval/"
    "b4c64_expanded_nosave_group_metrics.csv"
)
NOSAVE_REPORT = Path(
    "analysis/integration_eval/"
    "b4c64_expanded_nosave_eval/"
    "b4c64_expanded_nosave_report.md"
)


def read_json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def f(row: dict[str, str], key: str) -> float:
    return float(row[key])


def score_train(row: dict[str, str]) -> tuple[int, list[str]]:
    score = 0
    notes: list[str] = []

    if f(row, "top10_delta") > 0:
        score += 10
        notes.append("top10 improved")
    if f(row, "rank_gt50_delta") < 0:
        score += 10
        notes.append("tail-count reduced inside train group")
    if f(row, "mean_rank_delta") < 0:
        score += 10
        notes.append("mean rank improved")
    if f(row, "mean_target_prob_delta") > 0:
        score += 10
        notes.append("target probability improved")

    return score, notes


def score_protected(row: dict[str, str]) -> tuple[int, list[str], list[str]]:
    score = 0
    pass_notes: list[str] = []
    fail_notes: list[str] = []

    checks = [
        ("top10_delta", f(row, "top10_delta") >= 0, 5, "top10 did not regress", "top10 regressed"),
        ("rank_gt50_delta", f(row, "rank_gt50_delta") <= 0, 5, "no new rank>50", "rank>50 increased"),
        ("mean_rank_delta", f(row, "mean_rank_delta") <= 0, 5, "mean rank did not worsen", "mean rank worsened"),
        ("mean_target_prob_delta", f(row, "mean_target_prob_delta") >= 0, 5, "target probability did not regress", "target probability regressed"),
        ("teacher_beats_worst_delta", f(row, "teacher_beats_worst_delta") >= 0, 5, "teacher-beats-worst did not regress", "teacher-beats-worst regressed"),
        ("teacher_beats_all_delta", f(row, "teacher_beats_all_delta") >= 0, 5, "teacher-beats-all did not regress", "teacher-beats-all regressed"),
    ]

    for _key, ok, pts, pass_note, fail_note in checks:
        if ok:
            score += pts
            pass_notes.append(pass_note)
        else:
            fail_notes.append(fail_note)

    return score, pass_notes, fail_notes


def score_tail(row: dict[str, str]) -> tuple[int, list[str], list[str]]:
    score = 0
    pass_notes: list[str] = []
    fail_notes: list[str] = []

    checks = [
        ("rank_gt50_delta", f(row, "rank_gt50_delta") <= 0, 10, "tail rank>50 count did not increase", "tail rank>50 count increased"),
        ("mean_rank_delta", f(row, "mean_rank_delta") <= 0, 10, "tail mean rank did not worsen", "tail mean rank worsened"),
        ("mean_target_prob_delta", f(row, "mean_target_prob_delta") >= 0, 5, "tail target probability did not regress", "tail target probability regressed"),
        (
            "mean_pair_hinge_margin_025_delta",
            f(row, "mean_pair_hinge_margin_025_delta") <= 0,
            5,
            "tail hinge did not worsen",
            "tail hinge worsened",
        ),
    ]

    for _key, ok, pts, pass_note, fail_note in checks:
        if ok:
            score += pts
            pass_notes.append(pass_note)
        else:
            fail_notes.append(fail_note)

    return score, pass_notes, fail_notes


def main() -> int:
    dataset = read_json(DATASET)
    train_mat = read_json(TRAIN_MATERIALIZATION_SUMMARY)
    train_gen = read_json(TRAIN_GENERATION_SUMMARY)
    tail_mat = read_json(TAIL_MATERIALIZATION_SUMMARY)
    rows = read_csv_rows(NOSAVE_CSV)
    nosave_report = NOSAVE_REPORT.read_text(encoding="utf-8")

    row_by_group = {r["group"]: r for r in rows}
    required_groups = {
        "train_main_rank_11_50",
        "protected_eval_top10",
        "tail_eval_rank_gt50",
    }
    missing = required_groups - set(row_by_group)
    if missing:
        raise ValueError(f"missing no-save groups: {sorted(missing)}")

    train_row = row_by_group["train_main_rank_11_50"]
    protected_row = row_by_group["protected_eval_top10"]
    tail_row = row_by_group["tail_eval_rank_gt50"]

    train_score, train_notes = score_train(train_row)
    protected_score, protected_pass, protected_fail = score_protected(protected_row)
    tail_score, tail_pass, tail_fail = score_tail(tail_row)

    gate_score = train_score + protected_score + tail_score
    gate_pass = not protected_fail and not tail_fail and f(train_row, "mean_rank_delta") <= 0

    dataset_counts = {
        "samples": len(dataset.get("samples", [])),
        "protected_eval_samples": len(dataset.get("protected_eval_samples", [])),
        "tail_eval_samples": len(dataset.get("tail_eval_samples", [])),
        "quarantine_samples": len(dataset.get("quarantine_samples", [])),
    }

    generated_train_rows = [
        r for r in dataset.get("samples", [])
        if isinstance(r, dict)
        and r.get("materialization_status") == "dryrun_materialized_generated_train_candidate"
    ]
    generated_tail_rows = [
        r for r in dataset.get("tail_eval_samples", [])
        if isinstance(r, dict)
        and r.get("materialization_status") == "dryrun_materialized_tail_eval_only"
    ]

    data_expansion_pass = (
        dataset_counts["samples"] == 12
        and len(generated_train_rows) == 8
        and dataset_counts["tail_eval_samples"] == 15
        and len(generated_tail_rows) == 12
        and dataset_counts["protected_eval_samples"] == 15
        and dataset_counts["quarantine_samples"] == 3
    )

    final_decision = (
        "PROJECT_EVIDENCE_COMPLETE_MODEL_NOT_GATE_PASS"
        if data_expansion_pass and not gate_pass
        else "PROJECT_EVIDENCE_COMPLETE_MODEL_GATE_PASS"
        if data_expansion_pass and gate_pass
        else "PROJECT_EVIDENCE_INCOMPLETE"
    )

    promotion_readiness = "NOT_PROMOTION_READY" if not gate_pass else "GATE_PASS_REVIEW_REQUIRED"

    summary = {
        "decision": final_decision,
        "promotion_readiness": promotion_readiness,
        "scope": "final model scoring report only; no checkpoint save/export/benchmark/promotion",
        "capacity_model": {
            "label": "current increased-capacity b4c64 model",
            "checkpoint": "checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt",
            "board_size": 15,
            "channels": 64,
            "blocks": 4,
            "win_length": 5,
        },
        "data_expansion": {
            "pass": data_expansion_pass,
            "dataset": str(DATASET),
            "counts": dataset_counts,
            "generated_train_rows": len(generated_train_rows),
            "generated_tail_guard_rows": len(generated_tail_rows),
            "train_generation_decision": train_gen.get("decision"),
            "train_materialization_decision": train_mat.get("decision"),
            "tail_materialization_decision": tail_mat.get("decision"),
        },
        "no_save_gate": {
            "gate_pass": gate_pass,
            "gate_score_0_100": gate_score,
            "train_signal_score_0_40": train_score,
            "protected_guard_score_0_30": protected_score,
            "tail_guard_score_0_30": tail_score,
            "train_notes": train_notes,
            "protected_pass_notes": protected_pass,
            "protected_fail_notes": protected_fail,
            "tail_pass_notes": tail_pass,
            "tail_fail_notes": tail_fail,
            "csv": str(NOSAVE_CSV),
            "report": str(NOSAVE_REPORT),
        },
        "key_metrics": {
            "train": train_row,
            "protected": protected_row,
            "tail": tail_row,
        },
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_SUMMARY.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines: list[str] = []
    lines += ["# Teacher-divergence final model scoring report", ""]
    lines += ["## Scope", ""]
    lines += [
        "- Final scoring report only.",
        "- No training is run by this report.",
        "- No checkpoint is saved.",
        "- No C export, no public benchmark, no promotion.",
        "",
    ]

    lines += ["## Final decision", ""]
    lines += [
        f"- decision: `{final_decision}`",
        f"- promotion readiness: `{promotion_readiness}`",
        f"- gate score: `{gate_score}/100`",
        "",
    ]

    lines += ["## Capacity model", ""]
    lines += [
        "- model label: `current increased-capacity b4c64 model`",
        "- checkpoint: `checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt`",
        "- architecture: board-size 15, channels 64, blocks 4, win-length 5",
        "",
    ]

    lines += ["## Data expansion evidence", ""]
    lines += [
        f"- data expansion pass: `{data_expansion_pass}`",
        f"- dataset: `{DATASET}`",
        "",
        "| group | count | evidence |",
        "|---|---:|---|",
        f"| samples | {dataset_counts['samples']} | 4 original + {len(generated_train_rows)} generated train candidates |",
        f"| protected_eval_samples | {dataset_counts['protected_eval_samples']} | unchanged guard set |",
        f"| tail_eval_samples | {dataset_counts['tail_eval_samples']} | 3 original + {len(generated_tail_rows)} generated tail guards |",
        f"| quarantine_samples | {dataset_counts['quarantine_samples']} | unchanged quarantine set |",
        "",
        f"- train generation decision: `{train_gen.get('decision')}`",
        f"- train materialization decision: `{train_mat.get('decision')}`",
        f"- tail materialization decision: `{tail_mat.get('decision')}`",
        "",
    ]

    lines += ["## No-save gate score", ""]
    lines += [
        "| component | score | interpretation |",
        "|---|---:|---|",
        f"| train signal | {train_score}/40 | {'; '.join(train_notes) if train_notes else 'no train improvement'} |",
        f"| protected guard | {protected_score}/30 | fail notes: {'; '.join(protected_fail) if protected_fail else 'none'} |",
        f"| tail guard | {tail_score}/30 | fail notes: {'; '.join(tail_fail) if tail_fail else 'none'} |",
        f"| total | {gate_score}/100 | {'PASS' if gate_pass else 'FAIL'} |",
        "",
    ]

    lines += ["## Key no-save metrics", ""]
    lines += [
        "| group | rows | top10 delta | rank_gt50 delta | mean_rank delta | target_prob delta | hinge delta | beats_worst delta | beats_all delta |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for group_name in ["train_main_rank_11_50", "protected_eval_top10", "tail_eval_rank_gt50"]:
        r = row_by_group[group_name]
        lines.append(
            f"| {group_name} | {r['rows_before']} | {float(r['top10_delta']):.6g} | "
            f"{float(r['rank_gt50_delta']):.6g} | {float(r['mean_rank_delta']):.6g} | "
            f"{float(r['mean_target_prob_delta']):.6g} | "
            f"{float(r['mean_pair_hinge_margin_025_delta']):.6g} | "
            f"{float(r['teacher_beats_worst_delta']):.6g} | "
            f"{float(r['teacher_beats_all_delta']):.6g} |"
        )
    lines.append("")

    lines += ["## Interpretation", ""]
    lines += [
        "- The data expansion objective is complete at dry-run/materialization level: train rows increased and tail guards increased while protected and quarantine groups remained separated.",
        "- The no-save probe shows useful train-side signal: train top10 improves, train rank>50 count falls, mean rank improves, and target probability improves.",
        "- The model is not gate-pass because protected teacher-beats metrics regress and the tail guard group worsens substantially.",
        "- Therefore this route satisfies the capacity/data/scoring evidence requirement, but it does not authorize checkpoint-producing training, promotion, current_best overwrite, C export, or public benchmark.",
        "",
    ]

    lines += ["## Source reports", ""]
    lines += [
        f"- generated train materialization summary: `{TRAIN_MATERIALIZATION_SUMMARY}`",
        f"- generated train source summary: `{TRAIN_GENERATION_SUMMARY}`",
        f"- generated tail materialization summary: `{TAIL_MATERIALIZATION_SUMMARY}`",
        f"- b4c64 no-save csv: `{NOSAVE_CSV}`",
        f"- b4c64 no-save report: `{NOSAVE_REPORT}`",
        "",
    ]

    lines += ["## Final note", ""]
    lines += [
        "This report is the final scoring artifact for the current route. It does not save a model and does not promote any checkpoint.",
        "",
    ]

    OUT_REPORT.write_text("\n".join(lines), encoding="utf-8")

    print("decision:", final_decision)
    print("promotion_readiness:", promotion_readiness)
    print("gate_score_0_100:", gate_score)
    print("data_expansion_pass:", data_expansion_pass)
    print("dataset_counts:", dataset_counts)
    print("generated_train_rows:", len(generated_train_rows))
    print("generated_tail_guard_rows:", len(generated_tail_rows))
    print("train_signal_score_0_40:", train_score)
    print("protected_guard_score_0_30:", protected_score)
    print("tail_guard_score_0_30:", tail_score)
    print("out_summary:", OUT_SUMMARY)
    print("out_report:", OUT_REPORT)
    print("status: final scoring report only; no training/checkpoint/export/benchmark/promotion")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
