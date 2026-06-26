#!/usr/bin/env python3
import csv
import json
from collections import defaultdict, Counter
from pathlib import Path


EXPANDED_DATASET = Path(
    "analysis/public_benchmark_eval/"
    "rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_conservative_plus_generated_tail_guards_plus_generated_train_candidates_dryrun.json"
)
ANCHOR_SOURCE = Path(
    "analysis/integration_eval/expanded_data_b6c64_benchmark_anchor_dryrun/benchmark_anchor_source.json"
)
BASELINE_MISMATCH = Path(
    "analysis/integration_eval/expanded_data_b6c64_baseline_mismatch_audit/baseline_mismatch_audit.json"
)

OUT_DIR = Path("analysis/integration_eval/expanded_data_b6c64_benchmark_preserving_training_input_dryrun")
OUT_JSON = OUT_DIR / "benchmark_preserving_training_input_dryrun.json"
OUT_CSV = OUT_DIR / "benchmark_preserving_training_input_manifest.csv"
OUT_SUMMARY = OUT_DIR / "benchmark_preserving_training_input_summary.json"
OUT_MD = OUT_DIR / "benchmark_preserving_training_input_report.md"


def row_id(row: dict, prefix: str, i: int) -> str:
    for k in ["sample_id", "id", "position_id", "source_id", "anchor_id"]:
        if row.get(k):
            return str(row[k])
    return f"{prefix}_{i:04d}"


def has_board_like_payload(row: dict) -> bool:
    if isinstance(row.get("board_rows"), list) and len(row["board_rows"]) == 15:
        return True
    if isinstance(row.get("board"), list):
        return True
    if isinstance(row.get("stones"), list):
        return True
    if isinstance(row.get("moves"), list):
        return True
    return False


def select_public_kl_anchors(before_anchors: list[dict], per_game: int = 2) -> list[dict]:
    by_game = defaultdict(list)
    for a in before_anchors:
        by_game[a["game"]].append(a)

    selected = []
    for game in sorted(by_game):
        rows = sorted(by_game[game], key=lambda x: int(x.get("ply_before_move", -1)))
        # Select latest neural-move anchors per game. These represent later tactical-mid behavior
        # while keeping KL volume bounded.
        selected.extend(rows[-per_game:])
    return selected


def to_manifest_rows(records: list[dict]) -> list[dict]:
    rows = []
    for r in records:
        payload = r["payload"]
        rows.append(
            {
                "input_id": r["input_id"],
                "group": r["group"],
                "role": r["role"],
                "loss_type": r["loss_type"],
                "recommended_weight": r["recommended_weight"],
                "source": r["source"],
                "has_board_payload": str(has_board_like_payload(payload)),
                "game": payload.get("game", ""),
                "neural_result": payload.get("neural_result", ""),
                "side_to_move": payload.get("side_to_move", payload.get("side", "")),
                "target_rc": payload.get("target_rc", ""),
                "move_played_rc": payload.get("move_played_rc", ""),
            }
        )
    return rows


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    dataset = json.loads(EXPANDED_DATASET.read_text(encoding="utf-8"))
    anchor_doc = json.loads(ANCHOR_SOURCE.read_text(encoding="utf-8"))
    mismatch = json.loads(BASELINE_MISMATCH.read_text(encoding="utf-8"))

    teacher_samples = dataset.get("samples", [])
    protected = dataset.get("protected_eval_samples", [])
    tail = dataset.get("tail_eval_samples", [])
    quarantine = dataset.get("quarantine_samples", [])

    anchors = anchor_doc.get("anchors", [])
    before_anchors = [
        a for a in anchors
        if a.get("recommended_use") == "train_kl_anchor_preserve_before_public_benchmark"
    ]
    after_anchors = [
        a for a in anchors
        if a.get("recommended_use") == "diagnostic_regression_anchor_after_candidate"
    ]

    selected_before_anchors = select_public_kl_anchors(before_anchors, per_game=2)

    records = []

    for i, s in enumerate(teacher_samples):
        records.append(
            {
                "input_id": row_id(s, "teacher_ce", i),
                "group": "teacher_divergence_ce_train",
                "role": "teacher_divergence_repair",
                "loss_type": "cross_entropy_teacher_target",
                "recommended_weight": 1.0,
                "source": str(EXPANDED_DATASET),
                "payload": s,
            }
        )

    for i, a in enumerate(selected_before_anchors):
        records.append(
            {
                "input_id": row_id(a, "public_kl", i),
                "group": "public_tactical_mid_kl_anchor_train",
                "role": "preserve_current_local_b6c64_public_behavior",
                "loss_type": "kl_to_reference_b6c64_policy",
                "recommended_weight": 0.20,
                "source": str(ANCHOR_SOURCE),
                "payload": a,
            }
        )

    for i, s in enumerate(protected):
        records.append(
            {
                "input_id": row_id(s, "protected_kl", i),
                "group": "protected_top10_kl_guard",
                "role": "protected_eval_guard",
                "loss_type": "kl_to_reference_b6c64_policy",
                "recommended_weight": 0.35,
                "source": str(EXPANDED_DATASET),
                "payload": s,
            }
        )

    for i, s in enumerate(tail):
        records.append(
            {
                "input_id": row_id(s, "tail_kl", i),
                "group": "tail_rank_kl_guard",
                "role": "tail_eval_guard",
                "loss_type": "kl_to_reference_b6c64_policy",
                "recommended_weight": 0.35,
                "source": str(EXPANDED_DATASET),
                "payload": s,
            }
        )

    diagnostic_records = []
    for i, a in enumerate(after_anchors):
        diagnostic_records.append(
            {
                "input_id": row_id(a, "after_diag", i),
                "group": "after_candidate_regression_diagnostic_only",
                "role": "diagnostic_after_candidate_anchor",
                "loss_type": "none_diagnostic_only",
                "recommended_weight": 0.0,
                "source": str(ANCHOR_SOURCE),
                "payload": a,
            }
        )

    manifest_rows = to_manifest_rows(records + diagnostic_records)

    group_counts = Counter(r["group"] for r in records)
    diagnostic_counts = Counter(r["group"] for r in diagnostic_records)
    board_payload_counts = Counter(r["has_board_payload"] for r in manifest_rows)

    summary = {
        "decision": "BENCHMARK_PRESERVING_TRAINING_INPUT_DRYRUN_READY",
        "not_training": True,
        "not_checkpoint": True,
        "not_export": True,
        "not_promotion": True,
        "baseline_policy": {
            "current_local_baseline_score": mismatch["local_before_rerun"]["score"],
            "current_local_baseline_score_rate": mismatch["local_before_rerun"]["score_rate"],
            "expanded_candidate_score": mismatch["local_after_candidate"]["score"],
            "expanded_candidate_score_rate": mismatch["local_after_candidate"]["score_rate"],
            "archived_current_best_score": mismatch["archived_before"]["score"],
            "archived_current_best_score_rate": mismatch["archived_before"]["score_rate"],
            "local_no_regression_gate": ">= 2.0/24 on tactical_mid",
            "aspirational_recovery_target": "recover toward archived 7.0/24 on tactical_mid",
        },
        "source_counts": {
            "teacher_samples": len(teacher_samples),
            "protected_eval_samples": len(protected),
            "tail_eval_samples": len(tail),
            "quarantine_samples": len(quarantine),
            "before_public_kl_anchor_pool": len(before_anchors),
            "before_public_kl_anchor_selected": len(selected_before_anchors),
            "after_diagnostic_anchor_pool": len(after_anchors),
        },
        "training_input_counts": dict(group_counts),
        "diagnostic_counts": dict(diagnostic_counts),
        "total_training_records": len(records),
        "total_diagnostic_records": len(diagnostic_records),
        "manifest_rows": len(manifest_rows),
        "board_payload_counts": dict(board_payload_counts),
        "weight_policy": {
            "teacher_divergence_ce_train": 1.0,
            "public_tactical_mid_kl_anchor_train": 0.20,
            "protected_top10_kl_guard": 0.35,
            "tail_rank_kl_guard": 0.35,
            "after_candidate_regression_diagnostic_only": 0.0,
        },
        "recommended_next_step": {
            "name": "benchmark_preserving_training_adapter_dryrun",
            "description": (
                "Implement a trainer adapter that can read this dry-run input, compute CE on teacher-divergence rows, "
                "compute KL-to-reference on selected public/protected/tail anchors, and run with --no-save first."
            ),
            "first_run_mode": "dry_run_or_no_save_only",
        },
    }

    output = {
        "summary": summary,
        "training_records": records,
        "diagnostic_records": diagnostic_records,
    }
    OUT_JSON.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    OUT_SUMMARY.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "input_id",
            "group",
            "role",
            "loss_type",
            "recommended_weight",
            "source",
            "has_board_payload",
            "game",
            "neural_result",
            "side_to_move",
            "target_rc",
            "move_played_rc",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in manifest_rows:
            writer.writerow(row)

    lines = []
    lines.append("# Expanded b6c64 benchmark-preserving training input dry-run")
    lines.append("")
    lines.append("- decision: `BENCHMARK_PRESERVING_TRAINING_INPUT_DRYRUN_READY`")
    lines.append("- no training")
    lines.append("- no checkpoint")
    lines.append("- no export")
    lines.append("- no promotion/current_best overwrite")
    lines.append("")
    lines.append("## Baseline policy")
    lines.append("")
    lines.append("| baseline | score | score rate | role |")
    lines.append("|---|---:|---:|---|")
    lines.append(
        f"| current local b6c64 baseline | {summary['baseline_policy']['current_local_baseline_score']:.1f}/24 | "
        f"{summary['baseline_policy']['current_local_baseline_score_rate']:.3f} | no-regression gate |"
    )
    lines.append(
        f"| expanded candidate | {summary['baseline_policy']['expanded_candidate_score']:.1f}/24 | "
        f"{summary['baseline_policy']['expanded_candidate_score_rate']:.3f} | current candidate evidence |"
    )
    lines.append(
        f"| archived current-best | {summary['baseline_policy']['archived_current_best_score']:.1f}/24 | "
        f"{summary['baseline_policy']['archived_current_best_score_rate']:.3f} | aspirational recovery target |"
    )
    lines.append("")
    lines.append("## Training input groups")
    lines.append("")
    lines.append("| group | count | loss | weight |")
    lines.append("|---|---:|---|---:|")
    for group, count in group_counts.items():
        loss_type = next(r["loss_type"] for r in records if r["group"] == group)
        weight = next(r["recommended_weight"] for r in records if r["group"] == group)
        lines.append(f"| `{group}` | {count} | `{loss_type}` | {weight:.2f} |")
    lines.append("")
    lines.append("## Diagnostic-only groups")
    lines.append("")
    lines.append("| group | count | use |")
    lines.append("|---|---:|---|")
    for group, count in diagnostic_counts.items():
        lines.append(f"| `{group}` | {count} | not used for training |")
    lines.append("")
    lines.append("## Source counts")
    lines.append("")
    lines.append("| source bucket | count |")
    lines.append("|---|---:|")
    for k, v in summary["source_counts"].items():
        lines.append(f"| `{k}` | {v} |")
    lines.append("")
    lines.append("## Next step")
    lines.append("")
    lines.append(
        "Write a benchmark-preserving training adapter dry-run. It must first run in dry-run/no-save mode, "
        "using CE for teacher-divergence rows and KL-to-reference for selected public/protected/tail anchors."
    )
    lines.append("")
    lines.append("Required gates for any later saved candidate:")
    lines.append("")
    lines.append("- current-local tactical_mid score must remain `>= 2.0/24`.")
    lines.append("- archived-current-best `7.0/24` is an aspirational recovery target, not a currently reproduced local baseline.")
    lines.append("- no promotion/current_best overwrite from this route.")
    lines.append("")
    lines.append("## Artifacts")
    lines.append("")
    lines.append(f"- dry-run input JSON: `{OUT_JSON}`")
    lines.append(f"- manifest CSV: `{OUT_CSV}`")
    lines.append(f"- summary JSON: `{OUT_SUMMARY}`")
    lines.append("")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("decision:", summary["decision"])
    print("source_counts:", summary["source_counts"])
    print("training_input_counts:", summary["training_input_counts"])
    print("diagnostic_counts:", summary["diagnostic_counts"])
    print("total_training_records:", summary["total_training_records"])
    print("total_diagnostic_records:", summary["total_diagnostic_records"])
    print("board_payload_counts:", summary["board_payload_counts"])
    print("wrote:", OUT_JSON)
    print("wrote:", OUT_CSV)
    print("wrote:", OUT_SUMMARY)
    print("wrote:", OUT_MD)


if __name__ == "__main__":
    main()
