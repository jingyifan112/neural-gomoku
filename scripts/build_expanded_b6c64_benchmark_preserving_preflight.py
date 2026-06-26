#!/usr/bin/env python3
import csv
import json
from collections import Counter
from pathlib import Path


OUT_DIR = Path("analysis/integration_eval/expanded_data_b6c64_benchmark_preserving_preflight")
OUT_JSON = OUT_DIR / "benchmark_preserving_preflight_summary.json"
OUT_MD = OUT_DIR / "benchmark_preserving_preflight_report.md"

SCORE_LADDER = Path("analysis/public_benchmark_eval/gomocup2026_score_ladder_summary.csv")
EXPANDED_DATASET = Path(
    "analysis/public_benchmark_eval/"
    "rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_conservative_plus_generated_tail_guards_plus_generated_train_candidates_dryrun.json"
)
AFTER_GAME_SUMMARY = Path(
    "analysis/integration_eval/expanded_data_b6c64_public_benchmark_candidate/tactical_mid_game_summary.csv"
)
AFTER_RUN_PREFIX_TXT = Path(
    "analysis/integration_eval/expanded_data_b6c64_public_benchmark_candidate/tactical_mid_run_prefix.txt"
)
TRAIN_REPORT = Path(
    "analysis/integration_eval/expanded_data_b6c64_public_benchmark_candidate/train_report.md"
)
TRAIN_GROUP_METRICS = Path(
    "analysis/integration_eval/expanded_data_b6c64_public_benchmark_candidate/train_group_metrics.csv"
)
CHECKPOINT = Path("checkpoints/probes/15x15_expanded_data_b6c64_public_benchmark_candidate.pt")
WEIGHTS = Path("weights/15x15_expanded_data_b6c64_public_benchmark_candidate_weights.bin")
WEIGHTS_MANIFEST = Path("weights/15x15_expanded_data_b6c64_public_benchmark_candidate_weights_manifest.json")


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def find_score_ladder(engine: str, baseline: str) -> dict[str, str]:
    rows = read_csv_rows(SCORE_LADDER)
    matches = [r for r in rows if r.get("engine") == engine and r.get("baseline") == baseline]
    if not matches:
        raise RuntimeError(f"missing score ladder row engine={engine!r} baseline={baseline!r}")
    # If duplicated rows exist, keep the first stable row.
    return matches[0]


def summarize_game_summary(path: Path) -> dict[str, object]:
    rows = read_csv_rows(path)
    counts = Counter(r["neural_result"] for r in rows)
    wins = counts.get("W", 0)
    losses = counts.get("L", 0)
    draws = counts.get("D", 0)
    games = len(rows)
    score = wins + 0.5 * draws
    rate = score / games if games else 0.0
    return {
        "games": games,
        "wins": wins,
        "losses": losses,
        "draws": draws,
        "score": score,
        "total": games,
        "score_rate": rate,
        "result_counts": dict(counts),
    }


def float_field(row: dict[str, str], key: str) -> float:
    return float(row[key])


def int_field(row: dict[str, str], key: str) -> int:
    return int(row[key])


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    dataset = json.loads(EXPANDED_DATASET.read_text(encoding="utf-8"))
    dataset_counts = {
        "samples": len(dataset.get("samples", [])),
        "protected_eval_samples": len(dataset.get("protected_eval_samples", [])),
        "tail_eval_samples": len(dataset.get("tail_eval_samples", [])),
        "quarantine_samples": len(dataset.get("quarantine_samples", [])),
    }

    before = find_score_ladder("neural_current_best_mcts16", "tactical_mid")
    strong = find_score_ladder("rapfi_full", "tactical_mid")
    after = summarize_game_summary(AFTER_GAME_SUMMARY)

    before_summary = {
        "engine": before["engine"],
        "baseline": before["baseline"],
        "games": int_field(before, "games"),
        "wins": int_field(before, "wins"),
        "losses": int_field(before, "losses"),
        "draws": int_field(before, "draws"),
        "score": float_field(before, "score"),
        "total": int_field(before, "total"),
        "score_rate": float_field(before, "score_rate"),
    }
    strong_summary = {
        "engine": strong["engine"],
        "baseline": strong["baseline"],
        "games": int_field(strong, "games"),
        "wins": int_field(strong, "wins"),
        "losses": int_field(strong, "losses"),
        "draws": int_field(strong, "draws"),
        "score": float_field(strong, "score"),
        "total": int_field(strong, "total"),
        "score_rate": float_field(strong, "score_rate"),
    }

    score_delta_vs_before = after["score"] - before_summary["score"]
    score_rate_delta_vs_before = after["score_rate"] - before_summary["score_rate"]
    score_delta_vs_strong = after["score"] - strong_summary["score"]
    score_rate_delta_vs_strong = after["score_rate"] - strong_summary["score_rate"]

    minimum_no_regression_score = before_summary["score"]
    improvement_target_score = before_summary["score"] + 1.0

    decision = "BENCHMARK_PRESERVING_REPAIR_REQUIRED"
    if after["score"] >= improvement_target_score:
        decision = "PUBLIC_BENCHMARK_IMPROVED"
    elif after["score"] >= minimum_no_regression_score:
        decision = "PUBLIC_BENCHMARK_NO_REGRESSION"
    else:
        decision = "BENCHMARK_PRESERVING_REPAIR_REQUIRED"

    run_prefix = AFTER_RUN_PREFIX_TXT.read_text(encoding="utf-8").strip() if AFTER_RUN_PREFIX_TXT.exists() else ""

    summary = {
        "decision": decision,
        "promotion_readiness": "NOT_PROMOTION_READY",
        "route": "expanded_data_b6c64_benchmark_preserving_preflight",
        "benchmark": {
            "suite": "gomocup2026_freestyle15_public_openings",
            "baseline": "tactical_mid",
            "games_per_pair": 24,
            "rule": "freestyle Gomoku rule 0",
            "board_size": 15,
        },
        "dataset_counts": dataset_counts,
        "before_model": before_summary,
        "after_expanded_model": {
            "engine": "expanded_data_b6c64_mcts16",
            "baseline": "tactical_mid",
            **after,
        },
        "strong_model": strong_summary,
        "deltas": {
            "after_minus_before_score": score_delta_vs_before,
            "after_minus_before_score_rate": score_rate_delta_vs_before,
            "after_minus_strong_score": score_delta_vs_strong,
            "after_minus_strong_score_rate": score_rate_delta_vs_strong,
        },
        "thresholds": {
            "minimum_no_regression_score": minimum_no_regression_score,
            "improvement_target_score": improvement_target_score,
        },
        "candidate_artifacts": {
            "checkpoint": str(CHECKPOINT),
            "weights": str(WEIGHTS),
            "weights_manifest": str(WEIGHTS_MANIFEST),
            "train_report": str(TRAIN_REPORT),
            "train_group_metrics": str(TRAIN_GROUP_METRICS),
            "tactical_mid_game_summary_csv": str(AFTER_GAME_SUMMARY),
            "tactical_mid_run_prefix": run_prefix,
        },
        "recommended_next_step": {
            "name": "benchmark_preserving_anchor_dryrun",
            "description": (
                "Build a dry-run anchor set from public benchmark/tactical_mid positions and existing protected/tail rows. "
                "Use teacher-divergence rows for CE, and use public/protected/tail rows as KL anchors before another candidate train."
            ),
            "required_gate": (
                "Any next candidate must score at least 7.0/24 on tactical_mid to avoid public benchmark regression; "
                "target improvement is >7.0/24."
            ),
        },
        "safety": {
            "not_current_best": True,
            "not_promotion": True,
            "not_c_export_for_promotion": True,
            "benchmark_result_is_candidate_only": True,
        },
    }

    OUT_JSON.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    lines = []
    lines.append("# Expanded b6c64 benchmark-preserving preflight")
    lines.append("")
    lines.append(f"- decision: `{decision}`")
    lines.append("- promotion_readiness: `NOT_PROMOTION_READY`")
    lines.append("- route: `exp/15x15-expanded-data-capacity-real-public-benchmark`")
    lines.append("")
    lines.append("## Purpose")
    lines.append("")
    lines.append(
        "This preflight records why the expanded-capacity/data candidate must move to benchmark-preserving training before any further candidate attempt."
    )
    lines.append("")
    lines.append("## Inputs")
    lines.append("")
    lines.append(f"- expanded dataset: `{EXPANDED_DATASET}`")
    lines.append(f"- candidate checkpoint: `{CHECKPOINT}`")
    lines.append(f"- candidate C weights: `{WEIGHTS}`")
    lines.append(f"- tactical-mid game summary: `{AFTER_GAME_SUMMARY}`")
    lines.append(f"- public score ladder: `{SCORE_LADDER}`")
    lines.append("")
    lines.append("## Dataset counts")
    lines.append("")
    lines.append("| bucket | count |")
    lines.append("|---|---:|")
    for k, v in dataset_counts.items():
        lines.append(f"| `{k}` | {v} |")
    lines.append("")
    lines.append("## Public benchmark comparison")
    lines.append("")
    lines.append("| Model | Engine | Opponent | W | L | D | Score | Score rate |")
    lines.append("|---|---|---|---:|---:|---:|---:|---:|")
    lines.append(
        f"| Before model | `{before_summary['engine']}` | `{before_summary['baseline']}` | "
        f"{before_summary['wins']} | {before_summary['losses']} | {before_summary['draws']} | "
        f"{before_summary['score']:.1f}/{before_summary['total']} | {before_summary['score_rate']:.3f} |"
    )
    lines.append(
        f"| After expanded candidate | `expanded_data_b6c64_mcts16` | `tactical_mid` | "
        f"{after['wins']} | {after['losses']} | {after['draws']} | "
        f"{after['score']:.1f}/{after['total']} | {after['score_rate']:.3f} |"
    )
    lines.append(
        f"| Strong reference | `{strong_summary['engine']}` | `{strong_summary['baseline']}` | "
        f"{strong_summary['wins']} | {strong_summary['losses']} | {strong_summary['draws']} | "
        f"{strong_summary['score']:.1f}/{strong_summary['total']} | {strong_summary['score_rate']:.3f} |"
    )
    lines.append("")
    lines.append("## Regression")
    lines.append("")
    lines.append(f"- after_minus_before_score: `{score_delta_vs_before:.1f}`")
    lines.append(f"- after_minus_before_score_rate: `{score_rate_delta_vs_before:.3f}`")
    lines.append(f"- after_minus_strong_score: `{score_delta_vs_strong:.1f}`")
    lines.append(f"- after_minus_strong_score_rate: `{score_rate_delta_vs_strong:.3f}`")
    lines.append("")
    lines.append("## Gate thresholds for next attempt")
    lines.append("")
    lines.append(f"- no-regression threshold: `>= {minimum_no_regression_score:.1f}/24`")
    lines.append(f"- improvement target: `> {minimum_no_regression_score:.1f}/24`, operational target `>= {improvement_target_score:.1f}/24`")
    lines.append("")
    lines.append("## Recommended next step")
    lines.append("")
    lines.append(
        "Build a benchmark-preserving anchor dry-run before another train. "
        "The next candidate should train teacher-divergence rows with CE, while using public benchmark, protected, and tail rows as KL anchors."
    )
    lines.append("")
    lines.append("Required next-candidate gate:")
    lines.append("")
    lines.append("- tactical_mid public benchmark must be at least `7.0/24` to avoid regression.")
    lines.append("- protected/tail guard metrics must not regress.")
    lines.append("- no promotion/current_best overwrite from this candidate route.")
    lines.append("")
    lines.append("## Safety")
    lines.append("")
    lines.append("- This report does not promote any checkpoint.")
    lines.append("- This report does not overwrite `current_best`.")
    lines.append("- The candidate benchmark is evidence only.")
    lines.append("")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("decision:", decision)
    print("before_score:", before_summary["score"], "before_rate:", before_summary["score_rate"])
    print("after_score:", after["score"], "after_rate:", after["score_rate"])
    print("strong_score:", strong_summary["score"], "strong_rate:", strong_summary["score_rate"])
    print("after_minus_before_score:", score_delta_vs_before)
    print("wrote:", OUT_JSON)
    print("wrote:", OUT_MD)


if __name__ == "__main__":
    main()
