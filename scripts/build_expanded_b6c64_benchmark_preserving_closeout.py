#!/usr/bin/env python3
import json
from pathlib import Path

OUT_DIR = Path("analysis/integration_eval/expanded_data_b6c64_benchmark_preserving_closeout")
OUT_JSON = OUT_DIR / "closeout_summary.json"
OUT_MD = OUT_DIR / "closeout_report.md"

PREFLIGHT = Path("analysis/integration_eval/expanded_data_b6c64_benchmark_preserving_preflight/benchmark_preserving_preflight_summary.json")
BASELINE_MISMATCH = Path("analysis/integration_eval/expanded_data_b6c64_baseline_mismatch_audit/baseline_mismatch_audit.json")
ANCHOR = Path("analysis/integration_eval/expanded_data_b6c64_benchmark_anchor_dryrun/benchmark_anchor_dryrun_summary.json")
TRAINING_INPUT = Path("analysis/integration_eval/expanded_data_b6c64_benchmark_preserving_training_input_dryrun/benchmark_preserving_training_input_summary.json")
SWEEP = Path("analysis/integration_eval/expanded_data_b6c64_benchmark_preserving_adapter_nosave_sweep/adapter_nosave_sweep_summary.json")

ADAPTER_CKPT = Path("checkpoints/probes/15x15_expanded_b6c64_benchmark_preserving_adapter_candidate.pt")
PUBLIC_CANDIDATE_CKPT = Path("checkpoints/probes/15x15_expanded_data_b6c64_public_benchmark_candidate.pt")
PUBLIC_CANDIDATE_WEIGHTS = Path("weights/15x15_expanded_data_b6c64_public_benchmark_candidate_weights.bin")


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    preflight = load(PREFLIGHT)
    mismatch = load(BASELINE_MISMATCH)
    anchor = load(ANCHOR)
    training_input = load(TRAINING_INPUT)
    sweep = load(SWEEP)

    sweep_rows = sweep["rows"]
    hard_pass = [r for r in sweep_rows if r.get("status") == "PASS_HARD_NO_SAVE"]
    soft_pass = [r for r in sweep_rows if r.get("status") == "PASS_SOFT_TOP3_WARNING_NO_SAVE"]
    fail = [r for r in sweep_rows if r.get("status") == "FAIL_NO_SAVE"]

    top3_deltas = sorted(set(int(r["top3_delta"]) for r in sweep_rows if r.get("top3_delta") not in ("", None)))
    rank_gt50_deltas = sorted(set(int(r["rank_gt50_delta"]) for r in sweep_rows if r.get("rank_gt50_delta") not in ("", None)))
    mean_rank_deltas = [float(r["mean_rank_delta"]) for r in sweep_rows if r.get("mean_rank_delta") not in ("", None)]
    prob_deltas = [float(r["mean_target_prob_delta"]) for r in sweep_rows if r.get("mean_target_prob_delta") not in ("", None)]

    decision = "CLOSEOUT_NO_SAVED_CANDIDATE_TOP3_WARNING"
    promotion_readiness = "NOT_PROMOTION_READY"

    summary = {
        "decision": decision,
        "promotion_readiness": promotion_readiness,
        "route": "expanded_data_b6c64_benchmark_preserving_adapter",
        "not_saved_candidate": True,
        "not_export": True,
        "not_public_benchmark_after_adapter": True,
        "not_promotion": True,
        "adapter_candidate_checkpoint_exists": ADAPTER_CKPT.exists(),
        "public_candidate_checkpoint_exists": PUBLIC_CANDIDATE_CKPT.exists(),
        "public_candidate_weights_exists": PUBLIC_CANDIDATE_WEIGHTS.exists(),
        "baseline_policy": {
            "archived_current_best_score": mismatch["archived_before"]["score"],
            "current_local_b6c64_baseline_score": mismatch["local_before_rerun"]["score"],
            "expanded_public_candidate_score": mismatch["local_after_candidate"]["score"],
            "interpretation": (
                "The current local b6c64 baseline reproduces 2.0/24, not the archived current-best 7.0/24. "
                "The expanded public candidate also scored 2.0/24, so it did not improve over current local b6c64 baseline."
            ),
        },
        "input_summary": {
            "teacher_samples": training_input["source_counts"]["teacher_samples"],
            "public_kl_anchor_selected": training_input["source_counts"]["before_public_kl_anchor_selected"],
            "protected_eval_samples": training_input["source_counts"]["protected_eval_samples"],
            "tail_eval_samples": training_input["source_counts"]["tail_eval_samples"],
            "total_training_records": training_input["total_training_records"],
            "total_diagnostic_records": training_input["total_diagnostic_records"],
        },
        "anchor_summary": {
            "before_public_kl_anchors": anchor["anchor_counts"]["before_public_kl_anchors"],
            "after_regression_diagnostic_anchors": anchor["anchor_counts"]["after_regression_diagnostic_anchors"],
            "total": anchor["anchor_counts"]["total"],
        },
        "sweep_summary": {
            "configs": len(sweep_rows),
            "hard_pass_count": len(hard_pass),
            "soft_pass_count": len(soft_pass),
            "fail_count": len(fail),
            "top3_deltas": top3_deltas,
            "rank_gt50_deltas": rank_gt50_deltas,
            "mean_rank_delta_min": min(mean_rank_deltas) if mean_rank_deltas else None,
            "mean_rank_delta_max": max(mean_rank_deltas) if mean_rank_deltas else None,
            "target_prob_delta_min": min(prob_deltas) if prob_deltas else None,
            "target_prob_delta_max": max(prob_deltas) if prob_deltas else None,
            "recommended_configs": [r["name"] for r in sweep.get("recommended_configs", [])],
        },
        "artifact_inputs": {
            "preflight": str(PREFLIGHT),
            "baseline_mismatch": str(BASELINE_MISMATCH),
            "anchor": str(ANCHOR),
            "training_input": str(TRAINING_INPUT),
            "sweep": str(SWEEP),
        },
        "recommendation": (
            "Do not create a saved adapter candidate from this route. "
            "The no-save sweep found only soft passes with persistent top3 regression. "
            "Next work should either add stronger positive supervision for the top3-sensitive row or revisit the archived-current-best runner mismatch."
        ),
    }

    OUT_JSON.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    lines = []
    lines.append("# Expanded b6c64 benchmark-preserving adapter closeout")
    lines.append("")
    lines.append(f"- decision: `{decision}`")
    lines.append(f"- promotion_readiness: `{promotion_readiness}`")
    lines.append("- saved adapter candidate: `False`")
    lines.append("- C export after adapter: `False`")
    lines.append("- public benchmark after adapter: `False`")
    lines.append("- promotion/current_best overwrite: `False`")
    lines.append("")
    lines.append("## Baseline correction")
    lines.append("")
    lines.append("| baseline | score | role |")
    lines.append("|---|---:|---|")
    lines.append(f"| archived current-best | {summary['baseline_policy']['archived_current_best_score']:.1f}/24 | aspirational recovery target |")
    lines.append(f"| current local b6c64 baseline | {summary['baseline_policy']['current_local_b6c64_baseline_score']:.1f}/24 | reproducible local no-regression gate |")
    lines.append(f"| expanded public candidate | {summary['baseline_policy']['expanded_public_candidate_score']:.1f}/24 | actual candidate public benchmark result |")
    lines.append("")
    lines.append("The current local b6c64 runner does not reproduce the archived `7.0/24` current-best score. The reproducible local b6c64 baseline is `2.0/24`, and the expanded public candidate also scored `2.0/24`.")
    lines.append("")
    lines.append("## Training input dry-run")
    lines.append("")
    lines.append("| group | count |")
    lines.append("|---|---:|")
    lines.append(f"| teacher-divergence CE rows | {summary['input_summary']['teacher_samples']} |")
    lines.append(f"| selected public tactical_mid KL anchors | {summary['input_summary']['public_kl_anchor_selected']} |")
    lines.append(f"| protected KL guard rows | {summary['input_summary']['protected_eval_samples']} |")
    lines.append(f"| tail KL guard rows | {summary['input_summary']['tail_eval_samples']} |")
    lines.append(f"| total training records | {summary['input_summary']['total_training_records']} |")
    lines.append(f"| diagnostic-only records | {summary['input_summary']['total_diagnostic_records']} |")
    lines.append("")
    lines.append("## No-save sweep result")
    lines.append("")
    lines.append("| metric | value |")
    lines.append("|---|---:|")
    lines.append(f"| configs tested | {summary['sweep_summary']['configs']} |")
    lines.append(f"| hard pass configs | {summary['sweep_summary']['hard_pass_count']} |")
    lines.append(f"| soft pass configs | {summary['sweep_summary']['soft_pass_count']} |")
    lines.append(f"| fail configs | {summary['sweep_summary']['fail_count']} |")
    lines.append(f"| observed top3 deltas | `{summary['sweep_summary']['top3_deltas']}` |")
    lines.append(f"| observed rank>50 deltas | `{summary['sweep_summary']['rank_gt50_deltas']}` |")
    lines.append(f"| mean_rank delta range | {summary['sweep_summary']['mean_rank_delta_min']:.3f} to {summary['sweep_summary']['mean_rank_delta_max']:.3f} |")
    lines.append(f"| target_prob delta range | {summary['sweep_summary']['target_prob_delta_min']:.8f} to {summary['sweep_summary']['target_prob_delta_max']:.8f} |")
    lines.append("")
    lines.append("All tested configs were soft passes only. They improved broad metrics but retained `top3_delta = -1`, so this route does not qualify for saved candidate creation.")
    lines.append("")
    lines.append("## Decision")
    lines.append("")
    lines.append("Do **not** create a saved adapter candidate from this route.")
    lines.append("")
    lines.append("Reasons:")
    lines.append("")
    lines.append("- No no-save config achieved `PASS_HARD_NO_SAVE`.")
    lines.append("- Every no-save config retained top3 regression.")
    lines.append("- Current local b6c64 baseline is only `2.0/24`, so public-benchmark recovery remains unresolved.")
    lines.append("- The archived `7.0/24` current-best score is not currently reproduced by the local b6c64 runner.")
    lines.append("")
    lines.append("## Recommended next route")
    lines.append("")
    lines.append("Either:")
    lines.append("")
    lines.append("1. Add targeted positive supervision for the top3-sensitive teacher-divergence row and repeat no-save only; or")
    lines.append("2. Audit/recover the archived current-best runner that produced `7.0/24`, then restart benchmark-preserving training from that reproducible baseline.")
    lines.append("")
    lines.append("No checkpoint, C export, public benchmark, promotion, or current-best overwrite should be performed from this soft-pass-only adapter route.")
    lines.append("")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("decision:", decision)
    print("promotion_readiness:", promotion_readiness)
    print("adapter_candidate_checkpoint_exists:", ADAPTER_CKPT.exists())
    print("public_candidate_checkpoint_exists:", PUBLIC_CANDIDATE_CKPT.exists())
    print("public_candidate_weights_exists:", PUBLIC_CANDIDATE_WEIGHTS.exists())
    print("sweep_summary:", summary["sweep_summary"])
    print("wrote:", OUT_JSON)
    print("wrote:", OUT_MD)


if __name__ == "__main__":
    main()
