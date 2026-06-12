#!/usr/bin/env python3

import argparse
import csv
import json
from pathlib import Path


def as_bool(v: str) -> bool:
    return str(v).strip().lower() == "true"


def as_int(v: str) -> int:
    return int(str(v).strip())


def as_float(v: str) -> float | None:
    s = str(v).strip()
    if s == "":
        return None
    return float(s)


def row_id(row: dict[str, str]) -> str:
    return f"g{row['game']}_p{row['ply']}_{row['side']}"


def compact_row(row: dict[str, str], role: str, reason: str, weight: float) -> dict:
    return {
        "id": row_id(row),
        "role": role,
        "reason": reason,
        "weight": weight,
        "game": as_int(row["game"]),
        "ply": as_int(row["ply"]),
        "side": row["side"],
        "model_move": row["model_move"],
        "teacher_move": row["teacher_move"],
        "teacher_move_policy_rank": as_int(row["teacher_move_policy_rank"]),
        "model_move_policy_rank": as_int(row["model_move_policy_rank"]),
        "teacher_policy_prob": as_float(row["teacher_policy_prob"]),
        "model_policy_prob": as_float(row["model_policy_prob"]),
        "policy_probability_gap_teacher_minus_model": as_float(row["policy_probability_gap_teacher_minus_model"]),
        "policy_logit_gap_teacher_minus_model": as_float(row["policy_logit_gap_teacher_minus_model"]),
        "value_current_position": as_float(row["value_current_position"]),
        "value_original_move": as_float(row["value_original_move"]),
        "value_teacher_move": as_float(row["value_teacher_move"]),
        "teacher_value_disfavored": as_bool(row["teacher_value_disfavored"]),
        "teacher_top3_policy": as_bool(row["teacher_top3_policy"]),
        "teacher_eval_current": row["teacher_eval_current"],
        "teacher_bestline_current": row["teacher_bestline_current"],
        "rapfi_after_original_eval": row["rapfi_after_original_eval"],
        "rapfi_after_original_move": row["rapfi_after_original_move"],
        "rapfi_after_original_bestline": row["rapfi_after_original_bestline"],
        "rapfi_after_teacher_eval": row["rapfi_after_teacher_eval"],
        "rapfi_after_teacher_move": row["rapfi_after_teacher_move"],
        "rapfi_after_teacher_bestline": row["rapfi_after_teacher_bestline"],
        "strong_teacher_continuation_preference": as_bool(row["strong_teacher_continuation_preference"]),
        "diverges": as_bool(row["diverges"]),
        "logged_direct": row["logged_direct"],
        "logged_mcts_raw": row["logged_mcts_raw"],
        "logged_mcts_safety": row["logged_mcts_safety"],
        "logged_value": as_float(row["logged_value"]),
        "loss_reason": row["loss_reason"],
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--input",
        default="analysis/integration_eval/candidate_d_teacher_disagreement_census.csv",
    )
    ap.add_argument(
        "--output-json",
        default="analysis/integration_eval/candidate_g_teacher_seed_manifest.json",
    )
    ap.add_argument(
        "--output-md",
        default="analysis/integration_eval/candidate_g_teacher_seed_manifest.md",
    )
    ap.add_argument("--anchor-window", type=int, default=4)
    args = ap.parse_args()

    in_path = Path(args.input)
    with in_path.open() as f:
        rows = list(csv.DictReader(f))

    # Main Candidate G seeds: strong same-position teacher divergences.
    seeds = [
        r for r in rows
        if as_bool(r["diverges"]) and as_bool(r["strong_teacher_continuation_preference"])
    ]

    seed_keys = {(as_int(r["game"]), as_int(r["ply"])) for r in seeds}

    selected: list[dict] = []
    seen: set[tuple[int, int, str]] = set()

    for r in seeds:
        key = (as_int(r["game"]), as_int(r["ply"]), "seed")
        seen.add(key)
        selected.append(
            compact_row(
                r,
                role="seed_teacher_divergence",
                reason="strong teacher continuation preference and model/teacher divergence",
                weight=2.0,
            )
        )

    # Explicit retention row around Candidate D move15 if present.
    for r in rows:
        if as_int(r["game"]) == 2 and as_int(r["ply"]) == 15:
            key = (as_int(r["game"]), as_int(r["ply"]), "retention")
            if key not in seen:
                seen.add(key)
                selected.append(
                    compact_row(
                        r,
                        role="retention_anchor",
                        reason="Candidate D move15 repair neighborhood anchor",
                        weight=1.5,
                    )
                )

    # Nearby non-divergent anchors around seed plies.
    for seed in seeds:
        sg = as_int(seed["game"])
        sp = as_int(seed["ply"])
        for r in rows:
            g = as_int(r["game"])
            p = as_int(r["ply"])
            if g != sg:
                continue
            if abs(p - sp) > args.anchor_window:
                continue
            if as_bool(r["diverges"]):
                continue
            key = (g, p, "retention")
            if key in seen:
                continue
            seen.add(key)
            selected.append(
                compact_row(
                    r,
                    role="nearby_nondivergent_anchor",
                    reason=f"non-divergent anchor within ±{args.anchor_window} plies of seed g{sg} p{sp}",
                    weight=1.0,
                )
            )

    # General teacher-aligned top-3 anchors, capped to avoid manifest bloat.
    general_anchor_count = 0
    for r in rows:
        if general_anchor_count >= 6:
            break
        if as_bool(r["diverges"]):
            continue
        if not as_bool(r["teacher_top3_policy"]):
            continue
        if r["model_move"] != r["teacher_move"]:
            continue
        key = (as_int(r["game"]), as_int(r["ply"]), "general")
        if key in seen:
            continue
        seen.add(key)
        general_anchor_count += 1
        selected.append(
            compact_row(
                r,
                role="general_teacher_aligned_anchor",
                reason="teacher-aligned top-3 policy retention anchor",
                weight=0.75,
            )
        )

    selected = sorted(selected, key=lambda x: (x["game"], x["ply"], x["role"]))

    manifest = {
        "name": "candidate_g_teacher_seed_manifest",
        "source_csv": str(in_path),
        "purpose": "dry-run selection manifest for Candidate G teacher distillation; not a trainable tensor dataset",
        "notes": [
            "No training was run.",
            "Rows contain teacher/model metadata but not full board tensors.",
            "Final trainable dataset still needs board state and last-move plane recovered from replay logs or census script.",
        ],
        "selection_counts": {
            "total_selected": len(selected),
            "seed_teacher_divergence": sum(1 for r in selected if r["role"] == "seed_teacher_divergence"),
            "retention_anchor": sum(1 for r in selected if r["role"] == "retention_anchor"),
            "nearby_nondivergent_anchor": sum(1 for r in selected if r["role"] == "nearby_nondivergent_anchor"),
            "general_teacher_aligned_anchor": sum(1 for r in selected if r["role"] == "general_teacher_aligned_anchor"),
        },
        "rows": selected,
    }

    out_json = Path(args.output_json)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(manifest, indent=2) + "\n")

    out_md = Path(args.output_md)
    lines = [
        "# Candidate G teacher seed manifest",
        "",
        "## Scope",
        "",
        "This is a dry-run selection manifest for Candidate G teacher distillation.",
        "",
        "- no training",
        "- no export",
        "- no promotion",
        "- no smoke match",
        "",
        "The manifest is not yet a trainable dataset because the source census CSV does not include full board tensors or last-move planes.",
        "",
        "## Selection counts",
        "",
    ]
    for k, v in manifest["selection_counts"].items():
        lines.append(f"- {k}: {v}")
    lines += [
        "",
        "## Selected rows",
        "",
        "| role | game | ply | side | model | teacher | teacher rank | teacher prob | model prob | weight | reason |",
        "|---|---:|---:|---|---|---|---:|---:|---:|---:|---|",
    ]
    for r in selected:
        lines.append(
            f"| {r['role']} | {r['game']} | {r['ply']} | {r['side']} | "
            f"{r['model_move']} | {r['teacher_move']} | {r['teacher_move_policy_rank']} | "
            f"{r['teacher_policy_prob']:.8f} | {r['model_policy_prob']:.8f} | "
            f"{r['weight']:.2f} | {r['reason']} |"
        )
    lines += [
        "",
        "## Next step",
        "",
        "Modify the replay/census pipeline to emit full board state and last-move plane for these selected rows before any training run.",
        "",
    ]
    out_md.write_text("\n".join(lines))

    print("wrote", out_json)
    print("wrote", out_md)
    print(json.dumps(manifest["selection_counts"], indent=2))


if __name__ == "__main__":
    main()
