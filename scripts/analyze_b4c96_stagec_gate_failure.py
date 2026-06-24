#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean


DEFAULT_GATE_CSV = "analysis/integration_eval/capacity_data_pairing_probe/gate_eval.csv"
DEFAULT_OUT_CSV = "analysis/integration_eval/b4c96_stagec_failure_forensics.csv"
DEFAULT_OUT_JSON = "analysis/integration_eval/b4c96_stagec_failure_forensics_summary.json"
DEFAULT_OUT_MD = "analysis/integration_eval/b4c96_stagec_failure_forensics.md"


NUMERIC_FIELDS = {
    "suppress_count",
    "target_rank_a",
    "target_rank_b",
    "target_rank_delta",
    "target_prob_a",
    "target_prob_b",
    "target_prob_delta",
    "primary_gap_a",
    "primary_gap_b",
    "primary_gap_delta",
    "worst_suppress_gap_a",
    "worst_suppress_gap_b",
    "worst_suppress_gap_delta",
    "multi_pair_hinge_a",
    "multi_pair_hinge_b",
    "multi_pair_hinge_delta",
    "teacher_beats_primary_a",
    "teacher_beats_primary_b",
    "teacher_beats_worst_a",
    "teacher_beats_worst_b",
    "teacher_beats_all_suppressors_a",
    "teacher_beats_all_suppressors_b",
    "protected_top10_regression",
    "rank_gt50_a",
    "rank_gt50_b",
}


def as_float(value: object) -> float:
    if value is None:
        return float("nan")
    text = str(value).strip()
    if text == "":
        return float("nan")
    return float(text)


def as_int(value: object) -> int:
    x = as_float(value)
    if math.isnan(x):
        return 0
    return int(round(x))


def direction(delta: float, improve_when_positive: bool, eps: float = 1e-12) -> str:
    if abs(delta) <= eps:
        return "same"
    improved = delta > 0 if improve_when_positive else delta < 0
    return "improved" if improved else "regressed"


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


def game_id(case_id: str) -> str:
    m = re.search(r"legacy_g(\d+)_", case_id)
    if m:
        return f"g{m.group(1)}"
    return "unknown"


def load_rows(path: Path) -> tuple[list[dict], list[str]]:
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        original_fields = list(reader.fieldnames or [])
        rows = []
        for raw in reader:
            row = dict(raw)
            for field in NUMERIC_FIELDS:
                if field in row:
                    row[field] = as_float(row[field])
            rows.append(row)
    return rows, original_fields


def enrich_row(row: dict) -> dict:
    case = str(row.get("case_id", ""))
    rank_a = as_int(row.get("target_rank_a"))
    rank_b = as_int(row.get("target_rank_b"))
    rank_delta = as_float(row.get("target_rank_delta"))
    prob_delta = as_float(row.get("target_prob_delta"))
    primary_gap_delta = as_float(row.get("primary_gap_delta"))
    worst_gap_delta = as_float(row.get("worst_suppress_gap_delta"))
    hinge_delta = as_float(row.get("multi_pair_hinge_delta"))

    protected_regression = as_int(row.get("protected_top10_regression")) == 1
    rank_gt50_a = as_int(row.get("rank_gt50_a")) == 1
    rank_gt50_b = as_int(row.get("rank_gt50_b")) == 1

    tags = []

    if protected_regression:
        tags.append("protected_top10_regression")
    if rank_a <= 5 and rank_b > 5:
        tags.append("top5_lost")
    if rank_a <= 10 and rank_b > 10:
        tags.append("top10_lost")
    if (not rank_gt50_a) and rank_gt50_b:
        tags.append("new_tail_rank_gt50")
    if rank_gt50_b:
        tags.append("tail_rank_gt50_after_b")

    rank_dir = direction(rank_delta, improve_when_positive=False)
    prob_dir = direction(prob_delta, improve_when_positive=True)
    primary_gap_dir = direction(primary_gap_delta, improve_when_positive=True)
    worst_gap_dir = direction(worst_gap_delta, improve_when_positive=True)
    hinge_dir = direction(hinge_delta, improve_when_positive=False)

    if rank_dir == "regressed":
        tags.append("rank_regression")
    if prob_dir == "regressed":
        tags.append("prob_regression")
    if primary_gap_dir == "regressed":
        tags.append("primary_gap_regression")
    if worst_gap_dir == "regressed":
        tags.append("worst_gap_regression")
    if hinge_dir == "regressed":
        tags.append("multi_pair_hinge_regression")

    core_improved = (
        rank_dir in {"improved", "same"}
        and prob_dir == "improved"
        and worst_gap_dir == "improved"
        and hinge_dir == "improved"
    )
    core_regressed = (
        rank_dir == "regressed"
        and prob_dir == "regressed"
        and worst_gap_dir == "regressed"
        and hinge_dir == "regressed"
    )

    if core_improved and not rank_gt50_b:
        outcome = "directionally_useful"
    elif core_improved and rank_gt50_b:
        outcome = "partial_tail_repair_unresolved"
    elif core_regressed:
        outcome = "severe_core_regression"
    elif protected_regression:
        outcome = "protected_regression"
    elif tags:
        outcome = "mixed_or_regressed"
    else:
        outcome = "mostly_neutral"

    if core_improved:
        tags.append("core_improved")
    if core_regressed:
        tags.append("core_regressed")

    enriched = dict(row)
    enriched.update(
        {
            "game_id": game_id(case),
            "rank_bucket_a": rank_bucket(rank_a),
            "rank_bucket_b": rank_bucket(rank_b),
            "rank_direction": rank_dir,
            "prob_direction": prob_dir,
            "primary_gap_direction": primary_gap_dir,
            "worst_gap_direction": worst_gap_dir,
            "multi_pair_hinge_direction": hinge_dir,
            "forensics_outcome": outcome,
            "failure_tags": ";".join(tags) if tags else "none",
        }
    )
    return enriched


def count(rows: list[dict], key: str, value: str) -> int:
    return sum(1 for r in rows if r.get(key) == value)


def metric_counts(rows: list[dict], key: str) -> dict:
    c = Counter(str(r.get(key, "")) for r in rows)
    return dict(sorted(c.items()))


def avg(rows: list[dict], key: str) -> float:
    vals = [as_float(r.get(key)) for r in rows]
    vals = [v for v in vals if not math.isnan(v)]
    return mean(vals) if vals else float("nan")


def build_summary(rows: list[dict]) -> dict:
    n = len(rows)
    tag_counter = Counter()
    for r in rows:
        for tag in str(r.get("failure_tags", "")).split(";"):
            if tag and tag != "none":
                tag_counter[tag] += 1

    by_game = defaultdict(lambda: Counter())
    for r in rows:
        gid = str(r.get("game_id"))
        by_game[gid]["rows"] += 1
        if "core_regressed" in str(r.get("failure_tags", "")):
            by_game[gid]["core_regressed"] += 1
        if "protected_top10_regression" in str(r.get("failure_tags", "")):
            by_game[gid]["protected_top10_regression"] += 1
        if "tail_rank_gt50_after_b" in str(r.get("failure_tags", "")):
            by_game[gid]["tail_rank_gt50_after_b"] += 1
        if str(r.get("forensics_outcome")) == "directionally_useful":
            by_game[gid]["directionally_useful"] += 1

    top3_a = sum(1 for r in rows if as_int(r.get("target_rank_a")) <= 3)
    top3_b = sum(1 for r in rows if as_int(r.get("target_rank_b")) <= 3)
    top5_a = sum(1 for r in rows if as_int(r.get("target_rank_a")) <= 5)
    top5_b = sum(1 for r in rows if as_int(r.get("target_rank_b")) <= 5)
    top10_a = sum(1 for r in rows if as_int(r.get("target_rank_a")) <= 10)
    top10_b = sum(1 for r in rows if as_int(r.get("target_rank_b")) <= 10)
    gt50_a = sum(1 for r in rows if as_int(r.get("target_rank_a")) > 50)
    gt50_b = sum(1 for r in rows if as_int(r.get("target_rank_b")) > 50)

    hard_fail_reasons = []
    if tag_counter.get("protected_top10_regression", 0) > 0:
        hard_fail_reasons.append("protected_top10_regression_nonzero")
    if top5_b - top5_a < 0:
        hard_fail_reasons.append("target_top5_delta_negative")
    if gt50_b - gt50_a > 0:
        hard_fail_reasons.append("rank_gt50_delta_positive")
    if avg(rows, "worst_suppress_gap_delta") < 0:
        hard_fail_reasons.append("mean_worst_suppress_gap_delta_negative")
    if avg(rows, "multi_pair_hinge_delta") > 0:
        hard_fail_reasons.append("mean_multi_pair_hinge_delta_positive")

    if hard_fail_reasons:
        diagnosis = "B4C96_STAGEC_FAILED_DUE_TO_PROTECTED_OR_OBJECTIVE_REGRESSION"
    else:
        diagnosis = "B4C96_STAGEC_DIRECTIONALLY_POSITIVE_BUT_REQUIRES_REVIEW"

    return {
        "rows": n,
        "topk": {
            "top3_a": top3_a,
            "top3_b": top3_b,
            "top3_delta": top3_b - top3_a,
            "top5_a": top5_a,
            "top5_b": top5_b,
            "top5_delta": top5_b - top5_a,
            "top10_a": top10_a,
            "top10_b": top10_b,
            "top10_delta": top10_b - top10_a,
            "rank_gt50_a": gt50_a,
            "rank_gt50_b": gt50_b,
            "rank_gt50_delta": gt50_b - gt50_a,
        },
        "means": {
            "target_rank_a": avg(rows, "target_rank_a"),
            "target_rank_b": avg(rows, "target_rank_b"),
            "target_rank_delta": avg(rows, "target_rank_delta"),
            "target_prob_delta": avg(rows, "target_prob_delta"),
            "primary_gap_delta": avg(rows, "primary_gap_delta"),
            "worst_suppress_gap_delta": avg(rows, "worst_suppress_gap_delta"),
            "multi_pair_hinge_delta": avg(rows, "multi_pair_hinge_delta"),
        },
        "directions": {
            "rank": metric_counts(rows, "rank_direction"),
            "prob": metric_counts(rows, "prob_direction"),
            "primary_gap": metric_counts(rows, "primary_gap_direction"),
            "worst_gap": metric_counts(rows, "worst_gap_direction"),
            "multi_pair_hinge": metric_counts(rows, "multi_pair_hinge_direction"),
        },
        "bucket_a": metric_counts(rows, "rank_bucket_a"),
        "bucket_b": metric_counts(rows, "rank_bucket_b"),
        "outcomes": metric_counts(rows, "forensics_outcome"),
        "failure_tags": dict(tag_counter.most_common()),
        "by_game": {gid: dict(counter) for gid, counter in sorted(by_game.items())},
        "hard_fail_reasons": hard_fail_reasons,
        "diagnosis": diagnosis,
        "recommendation": (
            "Do not promote. Do not public benchmark. Next route should compare protected/anchor weighting, "
            "tail-row pruning, and objective weighting before any further b4c96 training."
        ),
    }


def write_csv(path: Path, rows: list[dict], original_fields: list[str]) -> None:
    derived_fields = [
        "game_id",
        "rank_bucket_a",
        "rank_bucket_b",
        "rank_direction",
        "prob_direction",
        "primary_gap_direction",
        "worst_gap_direction",
        "multi_pair_hinge_direction",
        "forensics_outcome",
        "failure_tags",
    ]
    fieldnames = original_fields + [f for f in derived_fields if f not in original_fields]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for r in rows:
            writer.writerow({k: r.get(k, "") for k in fieldnames})


def md_table_dict(d: dict) -> list[str]:
    lines = ["| key | value |", "|---|---:|"]
    for k, v in d.items():
        if isinstance(v, float):
            lines.append(f"| {k} | {v:.6f} |")
        else:
            lines.append(f"| {k} | {v} |")
    return lines


def write_md(path: Path, summary: dict, rows: list[dict], gate_csv: Path) -> None:
    worst_regressions = sorted(
        rows,
        key=lambda r: (
            as_float(r.get("worst_suppress_gap_delta")),
            as_float(r.get("multi_pair_hinge_delta")) * -1,
            as_float(r.get("target_rank_delta")) * -1,
        ),
    )[:12]

    worst_after_rank = sorted(rows, key=lambda r: as_float(r.get("target_rank_b")), reverse=True)[:12]

    lines = []
    lines.append("# b4c96 Stage C failure forensics")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append("- Analysis only: read existing Stage C gate CSV.")
    lines.append("- No training, no checkpoint write, no C export, no public benchmark, no promotion.")
    lines.append(f"- Input gate CSV: `{gate_csv}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.extend(md_table_dict({"rows": summary["rows"], "diagnosis": summary["diagnosis"]}))
    lines.append("")
    lines.append("## Top-k movement")
    lines.append("")
    lines.extend(md_table_dict(summary["topk"]))
    lines.append("")
    lines.append("## Mean deltas")
    lines.append("")
    lines.extend(md_table_dict(summary["means"]))
    lines.append("")
    lines.append("## Direction counts")
    lines.append("")
    for name, d in summary["directions"].items():
        lines.append(f"### {name}")
        lines.append("")
        lines.extend(md_table_dict(d))
        lines.append("")
    lines.append("## Rank buckets")
    lines.append("")
    lines.append("### Before Model B")
    lines.append("")
    lines.extend(md_table_dict(summary["bucket_a"]))
    lines.append("")
    lines.append("### After Model B")
    lines.append("")
    lines.extend(md_table_dict(summary["bucket_b"]))
    lines.append("")
    lines.append("## Forensics outcomes")
    lines.append("")
    lines.extend(md_table_dict(summary["outcomes"]))
    lines.append("")
    lines.append("## Failure tags")
    lines.append("")
    lines.extend(md_table_dict(summary["failure_tags"]))
    lines.append("")
    lines.append("## Hard fail reasons")
    lines.append("")
    if summary["hard_fail_reasons"]:
        for item in summary["hard_fail_reasons"]:
            lines.append(f"- {item}")
    else:
        lines.append("- none")
    lines.append("")
    lines.append("## Worst objective regressions")
    lines.append("")
    lines.append("| case_id | rank_a | rank_b | prob_delta | worst_gap_delta | hinge_delta | outcome | tags |")
    lines.append("|---|---:|---:|---:|---:|---:|---|---|")
    for r in worst_regressions:
        lines.append(
            "| {case_id} | {ra} | {rb} | {pd:.6f} | {wgd:.6f} | {hd:.6f} | {outcome} | {tags} |".format(
                case_id=r.get("case_id"),
                ra=as_int(r.get("target_rank_a")),
                rb=as_int(r.get("target_rank_b")),
                pd=as_float(r.get("target_prob_delta")),
                wgd=as_float(r.get("worst_suppress_gap_delta")),
                hd=as_float(r.get("multi_pair_hinge_delta")),
                outcome=r.get("forensics_outcome"),
                tags=r.get("failure_tags"),
            )
        )
    lines.append("")
    lines.append("## Worst target ranks after Model B")
    lines.append("")
    lines.append("| case_id | rank_a | rank_b | prob_a | prob_b | worst_gap_a | worst_gap_b | tags |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---|")
    for r in worst_after_rank:
        lines.append(
            "| {case_id} | {ra} | {rb} | {pa:.8f} | {pb:.8f} | {wga:.6f} | {wgb:.6f} | {tags} |".format(
                case_id=r.get("case_id"),
                ra=as_int(r.get("target_rank_a")),
                rb=as_int(r.get("target_rank_b")),
                pa=as_float(r.get("target_prob_a")),
                pb=as_float(r.get("target_prob_b")),
                wga=as_float(r.get("worst_suppress_gap_a")),
                wgb=as_float(r.get("worst_suppress_gap_b")),
                tags=r.get("failure_tags"),
            )
        )
    lines.append("")
    lines.append("## Recommendation")
    lines.append("")
    lines.append(summary["recommendation"])
    lines.append("")
    lines.append("## Final decision")
    lines.append("")
    lines.append("`B4C96_STAGEC_FAILURE_FORENSICS_COMPLETE_NO_PROMOTION`")
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gate-csv", default=DEFAULT_GATE_CSV)
    ap.add_argument("--out-csv", default=DEFAULT_OUT_CSV)
    ap.add_argument("--out-json", default=DEFAULT_OUT_JSON)
    ap.add_argument("--out-md", default=DEFAULT_OUT_MD)
    args = ap.parse_args()

    gate_csv = Path(args.gate_csv)
    out_csv = Path(args.out_csv)
    out_json = Path(args.out_json)
    out_md = Path(args.out_md)

    if not gate_csv.exists():
        raise SystemExit(f"missing gate csv: {gate_csv}")

    rows, original_fields = load_rows(gate_csv)
    enriched = [enrich_row(r) for r in rows]
    summary = build_summary(enriched)

    write_csv(out_csv, enriched, original_fields)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    write_md(out_md, summary, enriched, gate_csv)

    print("wrote:", out_csv)
    print("wrote:", out_json)
    print("wrote:", out_md)
    print("diagnosis:", summary["diagnosis"])
    print("hard_fail_reasons:", ", ".join(summary["hard_fail_reasons"]) or "none")


if __name__ == "__main__":
    main()
