#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

DEFAULT_VARIANTS = [
    (
        "w010",
        "0.10",
        Path("analysis/integration_eval/teacher_divergence_policy_mixed_ce_anchor_probe_gated_eval.csv"),
    ),
    (
        "w005",
        "0.05",
        Path("analysis/integration_eval/teacher_divergence_policy_mixed_ce_anchor_probe_w005_gated_eval.csv"),
    ),
    (
        "w0025",
        "0.025",
        Path("analysis/integration_eval/teacher_divergence_policy_mixed_ce_anchor_probe_w0025_gated_eval.csv"),
    ),
]


def as_int(x: str) -> int:
    return int(float(x))


def as_float(x: str) -> float:
    return float(x)


def as_bool(x: str) -> bool:
    return str(x).strip().lower() == "true"


def load_eval_csv(path: Path, split: str) -> dict[str, dict[str, dict[str, str]]]:
    if not path.exists():
        raise FileNotFoundError(path)

    grouped: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)

    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        required = {
            "phase",
            "id",
            "split",
            "label_type",
            "source_id",
            "side_to_move",
            "policy_target",
            "target_rank",
            "target_prob",
            "target_ce",
            "top_move",
            "top_prob",
            "top_matches_target",
            "value",
        }
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"{path} missing columns: {sorted(missing)}")

        for row in reader:
            if row["split"] != split:
                continue
            phase = row["phase"]
            if phase not in {"before", "after"}:
                continue
            grouped[row["id"]][phase] = row

    bad = [k for k, v in grouped.items() if set(v) != {"before", "after"}]
    if bad:
        raise ValueError(f"{path} has rows without before/after pairs: {bad[:10]}")

    return dict(grouped)


def audit_variant(variant: str, scale: str, path: Path, split: str) -> list[dict[str, Any]]:
    grouped = load_eval_csv(path, split=split)
    out: list[dict[str, Any]] = []

    for row_id in sorted(grouped):
        before = grouped[row_id]["before"]
        after = grouped[row_id]["after"]

        before_rank = as_int(before["target_rank"])
        after_rank = as_int(after["target_rank"])
        before_prob = as_float(before["target_prob"])
        after_prob = as_float(after["target_prob"])
        before_ce = as_float(before["target_ce"])
        after_ce = as_float(after["target_ce"])
        before_top_match = as_bool(before["top_matches_target"])
        after_top_match = as_bool(after["top_matches_target"])

        out.append(
            {
                "variant": variant,
                "scale": scale,
                "id": row_id,
                "source_id": before["source_id"],
                "label_type": before["label_type"],
                "side_to_move": before["side_to_move"],
                "policy_target": before["policy_target"],
                "before_rank": before_rank,
                "after_rank": after_rank,
                "rank_delta": after_rank - before_rank,
                "rank_improved": after_rank < before_rank,
                "rank_same": after_rank == before_rank,
                "rank_regressed": after_rank > before_rank,
                "before_prob": before_prob,
                "after_prob": after_prob,
                "prob_delta": after_prob - before_prob,
                "prob_improved": after_prob > before_prob,
                "prob_same": after_prob == before_prob,
                "prob_regressed": after_prob < before_prob,
                "before_ce": before_ce,
                "after_ce": after_ce,
                "ce_delta": after_ce - before_ce,
                "before_top_matches_target": before_top_match,
                "after_top_matches_target": after_top_match,
                "top_match_gained": (not before_top_match) and after_top_match,
                "top_match_lost": before_top_match and (not after_top_match),
                "before_top_move": before["top_move"],
                "after_top_move": after["top_move"],
                "before_top_prob": as_float(before["top_prob"]),
                "after_top_prob": as_float(after["top_prob"]),
                "before_value": as_float(before["value"]),
                "after_value": as_float(after["value"]),
            }
        )

    return out


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"no rows for {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0].keys())
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def summarize(detail_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_id: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in detail_rows:
        by_id[row["id"]].append(row)

    summary_rows: list[dict[str, Any]] = []

    for row_id in sorted(by_id):
        rows = sorted(by_id[row_id], key=lambda r: r["scale"], reverse=True)
        first = rows[0]

        rank_regression_count = sum(bool(r["rank_regressed"]) for r in rows)
        prob_regression_count = sum(bool(r["prob_regressed"]) for r in rows)
        rank_improvement_count = sum(bool(r["rank_improved"]) for r in rows)
        prob_improvement_count = sum(bool(r["prob_improved"]) for r in rows)
        top_match_gained_count = sum(bool(r["top_match_gained"]) for r in rows)
        top_match_lost_count = sum(bool(r["top_match_lost"]) for r in rows)

        summary_rows.append(
            {
                "id": row_id,
                "source_id": first["source_id"],
                "label_type": first["label_type"],
                "side_to_move": first["side_to_move"],
                "policy_target": first["policy_target"],
                "variant_count": len(rows),
                "rank_regression_count": rank_regression_count,
                "prob_regression_count": prob_regression_count,
                "rank_improvement_count": rank_improvement_count,
                "prob_improvement_count": prob_improvement_count,
                "top_match_gained_count": top_match_gained_count,
                "top_match_lost_count": top_match_lost_count,
                "regressed_rank_all_variants": rank_regression_count == len(rows),
                "regressed_prob_all_variants": prob_regression_count == len(rows),
                "regressed_rank_or_prob_all_variants": all(
                    bool(r["rank_regressed"]) or bool(r["prob_regressed"]) for r in rows
                ),
                "rank_delta_by_scale": ";".join(
                    f'{r["scale"]}:{r["rank_delta"]}' for r in rows
                ),
                "prob_delta_by_scale": ";".join(
                    f'{r["scale"]}:{r["prob_delta"]:.8f}' for r in rows
                ),
                "top_match_by_scale": ";".join(
                    f'{r["scale"]}:{int(r["before_top_matches_target"])}->{int(r["after_top_matches_target"])}'
                    for r in rows
                ),
            }
        )

    summary_rows.sort(
        key=lambda r: (
            -int(r["regressed_rank_or_prob_all_variants"]),
            -int(r["regressed_prob_all_variants"]),
            -int(r["regressed_rank_all_variants"]),
            -int(r["prob_regression_count"]),
            -int(r["rank_regression_count"]),
            r["id"],
        )
    )
    return summary_rows


def write_markdown(
    path: Path,
    detail_rows: list[dict[str, Any]],
    summary_rows: list[dict[str, Any]],
    split: str,
) -> None:
    by_variant = defaultdict(list)
    for row in detail_rows:
        by_variant[row["variant"]].append(row)

    lines: list[str] = []
    lines.append("# Mixed-CE heldout regression audit")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append(f"- audited split: `{split}`")
    lines.append("- source runs: corrected mixed-CE scale sweep")
    lines.append("- no training")
    lines.append("- no checkpoint")
    lines.append("- no C export")
    lines.append("- no benchmark")
    lines.append("- no promotion")
    lines.append("")
    lines.append("## Per-scale summary")
    lines.append("")
    lines.append(
        "| variant | scale | rows | rank improved/same/regressed | prob improved/same/regressed | top match gained/lost |"
    )
    lines.append("|---|---:|---:|---:|---:|---:|")

    for variant in ["w010", "w005", "w0025"]:
        rows = by_variant[variant]
        if not rows:
            continue
        scale = rows[0]["scale"]
        rank_counts = Counter(
            "improved"
            if r["rank_improved"]
            else "regressed"
            if r["rank_regressed"]
            else "same"
            for r in rows
        )
        prob_counts = Counter(
            "improved"
            if r["prob_improved"]
            else "regressed"
            if r["prob_regressed"]
            else "same"
            for r in rows
        )
        top_gained = sum(bool(r["top_match_gained"]) for r in rows)
        top_lost = sum(bool(r["top_match_lost"]) for r in rows)
        lines.append(
            f"| {variant} | {scale} | {len(rows)} | "
            f"{rank_counts['improved']}/{rank_counts['same']}/{rank_counts['regressed']} | "
            f"{prob_counts['improved']}/{prob_counts['same']}/{prob_counts['regressed']} | "
            f"{top_gained}/{top_lost} |"
        )

    lines.append("")
    lines.append("## Repeated regression rows")
    lines.append("")
    repeated = [
        r
        for r in summary_rows
        if r["regressed_rank_or_prob_all_variants"]
    ]
    lines.append(
        "| id | target | rank regression count | prob regression count | rank delta by scale | prob delta by scale | top match by scale |"
    )
    lines.append("|---|---|---:|---:|---|---|---|")
    for r in repeated:
        lines.append(
            f"| `{r['id']}` | `{r['policy_target']}` | "
            f"{r['rank_regression_count']} | {r['prob_regression_count']} | "
            f"`{r['rank_delta_by_scale']}` | `{r['prob_delta_by_scale']}` | "
            f"`{r['top_match_by_scale']}` |"
        )

    lines.append("")
    lines.append("## Top-match gains")
    lines.append("")
    gain_rows = [r for r in summary_rows if int(r["top_match_gained_count"]) > 0]
    if gain_rows:
        lines.append("| id | target | gained count | top match by scale |")
        lines.append("|---|---|---:|---|")
        for r in gain_rows:
            lines.append(
                f"| `{r['id']}` | `{r['policy_target']}` | "
                f"{r['top_match_gained_count']} | `{r['top_match_by_scale']}` |"
            )
    else:
        lines.append("No heldout rows gained target top-1 under these variants.")

    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append(
        "Rows that regress under all scales are the most important blockers for any future mixed-CE selection strategy."
    )
    lines.append(
        "The next step should inspect these repeated regression rows before adding more training signal."
    )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", default="heldout_retention")
    parser.add_argument(
        "--detail-csv",
        type=Path,
        default=Path(
            "analysis/integration_eval/teacher_divergence_policy_mixed_ce_heldout_regression_audit.csv"
        ),
    )
    parser.add_argument(
        "--summary-csv",
        type=Path,
        default=Path(
            "analysis/integration_eval/teacher_divergence_policy_mixed_ce_heldout_regression_audit_summary.csv"
        ),
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=Path(
            "analysis/integration_eval/teacher_divergence_policy_mixed_ce_heldout_regression_audit.md"
        ),
    )
    args = parser.parse_args()

    detail_rows: list[dict[str, Any]] = []
    for variant, scale, path in DEFAULT_VARIANTS:
        detail_rows.extend(audit_variant(variant, scale, path, split=args.split))

    summary_rows = summarize(detail_rows)

    write_csv(args.detail_csv, detail_rows)
    write_csv(args.summary_csv, summary_rows)
    write_markdown(args.report, detail_rows, summary_rows, split=args.split)

    print(f"wrote detail csv: {args.detail_csv}")
    print(f"wrote summary csv: {args.summary_csv}")
    print(f"wrote report: {args.report}")

    print("")
    print("Repeated blockers:")
    for row in summary_rows:
        if row["regressed_rank_or_prob_all_variants"]:
            print(
                row["id"],
                "rank_regressions=",
                row["rank_regression_count"],
                "prob_regressions=",
                row["prob_regression_count"],
                "target=",
                row["policy_target"],
            )


if __name__ == "__main__":
    main()
