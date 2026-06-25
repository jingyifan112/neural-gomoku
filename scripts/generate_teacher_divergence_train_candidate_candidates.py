#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import torch


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))


from scripts import generate_teacher_divergence_tail_guard_candidates as tailgen  # noqa: E402


OUT_DIR = Path("analysis/integration_eval/teacher_divergence_train_candidate_generation")
OUT_CSV = OUT_DIR / "train_candidate_manifest.csv"
OUT_JSON = OUT_DIR / "train_candidate_source.json"
OUT_SUMMARY = OUT_DIR / "train_candidate_generation_summary.json"
OUT_MD = OUT_DIR / "train_candidate_generation_report.md"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=(
            "Generate teacher-divergence train candidate source rows from board snapshots. "
            "Source generation only: no training and no checkpoint save."
        )
    )
    p.add_argument(
        "--board-snapshots",
        type=Path,
        default=Path("analysis/public_benchmark_eval/corpus8_selected_board_snapshots.json"),
    )
    p.add_argument(
        "--reference-dataset",
        type=Path,
        default=Path(
            "analysis/public_benchmark_eval/"
            "rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_conservative_plus_generated_tail_guards_dryrun.json"
        ),
    )
    p.add_argument(
        "--model-checkpoint",
        type=Path,
        default=Path("checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt"),
    )
    p.add_argument("--board-size", type=int, default=15)
    p.add_argument("--win-length", type=int, default=5)
    p.add_argument("--channels", type=int, default=64)
    p.add_argument("--blocks", type=int, default=4)
    p.add_argument("--top-suppress", type=int, default=5)
    p.add_argument("--train-rank-min", type=int, default=11)
    p.add_argument("--train-rank-max", type=int, default=50)
    p.add_argument("--protected-rank-max", type=int, default=10)
    p.add_argument("--tail-rank-threshold", type=int, default=50)
    p.add_argument("--min-train-target", type=int, default=12)
    p.add_argument("--device", default="cpu")
    return p.parse_args()


def read_json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def load_existing_identities(reference_dataset: Path, board_size: int) -> tuple[set[str], set[str]]:
    existing_case_ids: set[str] = set()
    existing_board_targets: set[str] = set()

    if not reference_dataset.exists():
        return existing_case_ids, existing_board_targets

    data = read_json(reference_dataset)
    if not isinstance(data, dict):
        return existing_case_ids, existing_board_targets

    for key in ["samples", "protected_eval_samples", "tail_eval_samples", "quarantine_samples"]:
        for row in data.get(key, []) or []:
            if not isinstance(row, dict):
                continue
            if row.get("case_id"):
                existing_case_ids.add(str(row["case_id"]))
            try:
                board = tailgen.validate_board(row["board"], board_size)
                rc = tailgen.validate_board  # keep linter quiet for module import style
                del rc
                target = tuple(int(x) for x in row["target_rc"])
                board_key = json.dumps(board, separators=(",", ":"), sort_keys=False)
                existing_board_targets.add(f"{board_key}:{target[0]}:{target[1]}")
            except Exception:
                pass

    return existing_case_ids, existing_board_targets


def board_target_identity(board: list[list[int]], target_rc: tuple[int, int]) -> str:
    board_key = json.dumps(board, separators=(",", ":"), sort_keys=False)
    return f"{board_key}:{target_rc[0]}:{target_rc[1]}"


def main() -> int:
    args = parse_args()
    device = torch.device(args.device)

    snapshots = read_json(args.board_snapshots)
    if not isinstance(snapshots, list):
        raise ValueError("board snapshots must be a list")

    existing_case_ids, existing_board_targets = load_existing_identities(
        args.reference_dataset,
        args.board_size,
    )

    model = tailgen.load_model(
        args.model_checkpoint,
        device,
        board_size=args.board_size,
        channels=args.channels,
        blocks=args.blocks,
        win_length=args.win_length,
    )

    candidate_rows: list[dict[str, Any]] = []
    skipped = Counter()

    for idx, snapshot in enumerate(snapshots):
        if not isinstance(snapshot, dict):
            skipped["snapshot_not_dict"] += 1
            continue

        try:
            board = tailgen.validate_board(snapshot["board_snapshot_before_decision"], args.board_size)
            current_player = tailgen.normalize_side(snapshot.get("side_to_move"))
        except Exception:
            skipped["bad_snapshot_schema"] += 1
            continue

        try:
            logits, probs, legal_actions_sorted = tailgen.score_board_policy(
                model,
                board,
                current_player,
                args.board_size,
                device,
            )
        except Exception as exc:
            skipped[f"policy_score_error:{type(exc).__name__}"] += 1
            continue

        raw_targets = tailgen.extract_candidate_target_rcs(snapshot, board, args.board_size)
        if not raw_targets:
            skipped["no_candidate_target_extracted"] += 1
            continue

        for t_i, target_info in enumerate(raw_targets):
            target_rc = tuple(target_info["target_rc"])
            try:
                target_action = tailgen.rc_to_action(target_rc, args.board_size)
            except Exception:
                skipped["bad_target_action"] += 1
                continue

            if target_action not in legal_actions_sorted:
                skipped["target_not_legal"] += 1
                continue

            target_rank = tailgen.rank_of_action(target_action, legal_actions_sorted)
            target_prob = float(probs[target_action])
            target_logit = float(logits[target_action])

            case_id = (
                f"traingen_g{snapshot.get('game_number', 'na')}"
                f"_m{snapshot.get('move_count', 'na')}"
                f"_t{t_i}_{target_rc[0]}_{target_rc[1]}"
            )

            if case_id in existing_case_ids:
                skipped["case_id_already_exists"] += 1
                continue

            identity = board_target_identity(board, target_rc)
            if identity in existing_board_targets:
                skipped["board_target_identity_already_exists"] += 1
                continue

            suppress_actions = [a for a in legal_actions_sorted if a != target_action][: args.top_suppress]
            if len(suppress_actions) < args.top_suppress:
                skipped["not_enough_suppress_actions"] += 1
                continue

            suppress_rcs = [tailgen.action_to_rc(a, args.board_size) for a in suppress_actions]
            suppress_candidates = [
                {
                    "action": int(a),
                    "rc": tailgen.action_to_rc(a, args.board_size),
                    "rank": tailgen.rank_of_action(a, legal_actions_sorted),
                    "prob": float(probs[a]),
                    "gap": float(target_logit - float(logits[a])),
                }
                for a in suppress_actions
            ]

            if args.train_rank_min <= target_rank <= args.train_rank_max:
                candidate_bucket = "P1_train_candidate"
                suggested_split = "train_candidate_review"
                training_allowed = True
                label_type = "train_candidate_source"
            elif target_rank <= args.protected_rank_max:
                candidate_bucket = "protected_reference_candidate"
                suggested_split = "protected_eval_review_only"
                training_allowed = False
                label_type = "protected_reference_source"
            elif target_rank > args.tail_rank_threshold:
                candidate_bucket = "tail_reference_candidate"
                suggested_split = "tail_eval_review_only"
                training_allowed = False
                label_type = "tail_reference_source"
            else:
                candidate_bucket = "gap_reference_candidate"
                suggested_split = "review_only"
                training_allowed = False
                label_type = "gap_reference_source"

            row = {
                "case_id": case_id,
                "candidate_bucket": candidate_bucket,
                "source": "board_snapshot_before_decision_train_candidate_generation",
                "board_size": args.board_size,
                "win_length": args.win_length,
                "model_checkpoint": str(args.model_checkpoint),
                "model_arch": {
                    "board_size": args.board_size,
                    "channels": args.channels,
                    "blocks": args.blocks,
                    "win_length": args.win_length,
                },
                "game_number": snapshot.get("game_number"),
                "move_count": snapshot.get("move_count"),
                "side_to_move": snapshot.get("side_to_move"),
                "current_player": current_player,
                "board": board,
                "target_rc": list(target_rc),
                "target_action": int(target_action),
                "target_source_field": target_info["target_source_field"],
                "target_source_kind": target_info["target_source_kind"],
                "target_source_preview": target_info["target_source_preview"],
                "before_target_rank": int(target_rank),
                "before_target_prob": target_prob,
                "before_target_logit": target_logit,
                "primary_suppress_rc": suppress_rcs[0],
                "suppress_rcs": suppress_rcs,
                "suppress_candidates": suppress_candidates,
                "before_primary_suppress_rank": int(suppress_candidates[0]["rank"]),
                "before_primary_gap": float(suppress_candidates[0]["gap"]),
                "before_worst_suppress_gap": float(min(c["gap"] for c in suppress_candidates)),
                "label_type": label_type,
                "suggested_split": suggested_split,
                "training_allowed": training_allowed,
                "sample_weight": 1.0,
                "effective_sample_weight": 1.0,
                "notes": (
                    "Generated as train-candidate source row. "
                    "Requires materialization review and no-save gate before any checkpoint-producing route."
                ),
            }
            candidate_rows.append(row)

    candidate_rows.sort(
        key=lambda r: (
            0 if r["candidate_bucket"] == "P1_train_candidate" else 1,
            -int(r["before_target_rank"]),
            float(r["before_target_prob"]),
            str(r["case_id"]),
        )
    )

    train_rows = [r for r in candidate_rows if r["candidate_bucket"] == "P1_train_candidate"]
    protected_reference_rows = [r for r in candidate_rows if r["candidate_bucket"] == "protected_reference_candidate"]
    tail_reference_rows = [r for r in candidate_rows if r["candidate_bucket"] == "tail_reference_candidate"]
    gap_reference_rows = [r for r in candidate_rows if r["candidate_bucket"] == "gap_reference_candidate"]

    decision = (
        "TRAIN_CANDIDATE_GENERATION_TARGET_MET"
        if len(train_rows) >= args.min_train_target
        else "TRAIN_CANDIDATE_GENERATION_PARTIAL"
        if train_rows
        else "TRAIN_CANDIDATE_GENERATION_NO_TRAIN_CANDIDATES"
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    csv_fields = [
        "case_id",
        "candidate_bucket",
        "game_number",
        "move_count",
        "side_to_move",
        "target_rc",
        "target_source_field",
        "target_source_kind",
        "before_target_rank",
        "before_target_prob",
        "before_primary_gap",
        "before_worst_suppress_gap",
        "primary_suppress_rc",
        "suppress_rcs",
        "suggested_split",
        "training_allowed",
    ]
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=csv_fields, lineterminator="\n")
        w.writeheader()
        for r in candidate_rows:
            flat = dict(r)
            for k in ["target_rc", "primary_suppress_rc", "suppress_rcs"]:
                flat[k] = json.dumps(flat[k], sort_keys=True)
            w.writerow({k: flat.get(k, "") for k in csv_fields})

    source_payload = {
        "name": "teacher_divergence_train_candidate_source",
        "description": "Candidate source only; not a training dataset.",
        "decision": decision,
        "scope": "candidate source generation only; no training/checkpoint save/export/benchmark/promotion",
        "model_checkpoint": str(args.model_checkpoint),
        "board_snapshots": str(args.board_snapshots),
        "reference_dataset": str(args.reference_dataset),
        "rank_policy": {
            "train_rank_min": args.train_rank_min,
            "train_rank_max": args.train_rank_max,
            "protected_rank_max": args.protected_rank_max,
            "tail_rank_threshold": args.tail_rank_threshold,
            "min_train_target": args.min_train_target,
        },
        "summary": {
            "snapshots": len(snapshots),
            "candidate_rows": len(candidate_rows),
            "train_candidates": len(train_rows),
            "protected_reference_candidates": len(protected_reference_rows),
            "tail_reference_candidates": len(tail_reference_rows),
            "gap_reference_candidates": len(gap_reference_rows),
            "skipped": dict(sorted(skipped.items())),
        },
        "train_candidates": train_rows,
        "protected_reference_candidates": protected_reference_rows,
        "tail_reference_candidates": tail_reference_rows,
        "gap_reference_candidates": gap_reference_rows,
    }
    OUT_JSON.write_text(json.dumps(source_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    summary = {
        "decision": decision,
        "scope": "candidate source generation only; no training/checkpoint save/export/benchmark/promotion",
        "model_checkpoint": str(args.model_checkpoint),
        "model_arch": {
            "board_size": args.board_size,
            "channels": args.channels,
            "blocks": args.blocks,
            "win_length": args.win_length,
        },
        "snapshots": len(snapshots),
        "candidate_rows": len(candidate_rows),
        "train_candidates": len(train_rows),
        "protected_reference_candidates": len(protected_reference_rows),
        "tail_reference_candidates": len(tail_reference_rows),
        "gap_reference_candidates": len(gap_reference_rows),
        "min_train_target": args.min_train_target,
        "train_rank_min": args.train_rank_min,
        "train_rank_max": args.train_rank_max,
        "protected_rank_max": args.protected_rank_max,
        "tail_rank_threshold": args.tail_rank_threshold,
        "skipped": dict(sorted(skipped.items())),
        "outputs": {
            "manifest_csv": str(OUT_CSV),
            "candidate_source_json": str(OUT_JSON),
            "summary_json": str(OUT_SUMMARY),
            "report_md": str(OUT_MD),
        },
    }
    OUT_SUMMARY.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines: list[str] = []
    lines += ["# Teacher-divergence train candidate generation", ""]
    lines += ["## Scope", ""]
    lines += [
        "- Candidate source generation only.",
        "- No final dataset materialization.",
        "- No training.",
        "- No checkpoint save.",
        "- No C export, no public benchmark, no promotion.",
        "",
    ]

    lines += ["## Inputs", ""]
    lines += [
        f"- board snapshots: `{args.board_snapshots}`",
        f"- reference dataset: `{args.reference_dataset}`",
        f"- model checkpoint: `{args.model_checkpoint}`",
        f"- model arch: `b{args.blocks}c{args.channels}`",
        "",
    ]

    lines += ["## Rank policy", ""]
    lines += [
        f"- train candidate rank band: `{args.train_rank_min}` to `{args.train_rank_max}`",
        f"- protected reference: `<= {args.protected_rank_max}`",
        f"- tail reference: `> {args.tail_rank_threshold}`",
        f"- min train target: `{args.min_train_target}`",
        "",
    ]

    lines += ["## Summary", ""]
    lines += [
        f"- snapshots scanned: `{len(snapshots)}`",
        f"- candidate rows: `{len(candidate_rows)}`",
        f"- P1 train candidates: `{len(train_rows)}` / `{args.min_train_target}`",
        f"- protected reference candidates: `{len(protected_reference_rows)}`",
        f"- tail reference candidates: `{len(tail_reference_rows)}`",
        f"- gap reference candidates: `{len(gap_reference_rows)}`",
        "",
    ]

    lines += ["## Skipped counts", ""]
    lines += ["| reason | count |", "|---|---:|"]
    for k, v in sorted(skipped.items()):
        lines.append(f"| {k} | {v} |")
    lines.append("")

    lines += ["## Top train candidates", ""]
    lines += [
        "| case_id | game | move | side | target_rc | rank | prob | source_field |",
        "|---|---:|---:|---|---|---:|---:|---|",
    ]
    for r in train_rows[:40]:
        lines.append(
            f"| `{r['case_id']}` | {r['game_number']} | {r['move_count']} | "
            f"{r['side_to_move']} | `{r['target_rc']}` | {r['before_target_rank']} | "
            f"{r['before_target_prob']:.6g} | `{r['target_source_field']}` |"
        )
    if not train_rows:
        lines.append("| _none_ |  |  |  |  |  |  |  |")
    lines.append("")

    lines += ["## Decision", ""]
    lines += [f"`{decision}`", ""]

    lines += ["## Final note", ""]
    lines += [
        "This output does not authorize training, checkpoint save, C export, public benchmark, promotion, or current_best overwrite.",
        "",
    ]

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("decision:", decision)
    print("snapshots:", len(snapshots))
    print("candidate_rows:", len(candidate_rows))
    print("train_candidates:", len(train_rows))
    print("protected_reference_candidates:", len(protected_reference_rows))
    print("tail_reference_candidates:", len(tail_reference_rows))
    print("gap_reference_candidates:", len(gap_reference_rows))
    print("skipped:", dict(sorted(skipped.items())))
    print("out_csv:", OUT_CSV)
    print("out_json:", OUT_JSON)
    print("out_summary:", OUT_SUMMARY)
    print("out_report:", OUT_MD)
    print("status: candidate source generation only; no training/checkpoint save/export/benchmark/promotion")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
