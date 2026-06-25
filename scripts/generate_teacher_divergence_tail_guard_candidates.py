#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import numpy as np
import torch

from scripts.evaluate_policy_rank_topk_gate_b4c96 import (
    action_to_rc,
    encode_state,
    legal_mask_from_board,
    load_model,
    rc_to_action,
)


OUT_DIR = Path("analysis/integration_eval/teacher_divergence_tail_guard_candidate_generation")
OUT_CSV = OUT_DIR / "tail_guard_candidate_manifest.csv"
OUT_JSON = OUT_DIR / "tail_guard_candidate_source.json"
OUT_SUMMARY = OUT_DIR / "tail_guard_candidate_generation_summary.json"
OUT_MD = OUT_DIR / "tail_guard_candidate_generation_report.md"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=(
            "Generate guarded teacher-divergence tail candidate source rows. "
            "This is source/review generation only: no training and no checkpoint save."
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
        default=Path("analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected.json"),
    )
    p.add_argument(
        "--model-checkpoint",
        type=Path,
        default=Path("checkpoints/probes/15x15_capacity_data_pairing_b4c96_probe_candidate.pt"),
    )
    p.add_argument("--board-size", type=int, default=15)
    p.add_argument("--win-length", type=int, default=5)
    p.add_argument("--channels", type=int, default=96)
    p.add_argument("--blocks", type=int, default=4)
    p.add_argument("--top-suppress", type=int, default=5)
    p.add_argument("--tail-rank-threshold", type=int, default=50)
    p.add_argument("--near-tail-rank-threshold", type=int, default=31)
    p.add_argument("--min-tail-target", type=int, default=12)
    p.add_argument("--device", default="cpu")
    return p.parse_args()


def read_json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_side(side: Any) -> int:
    if isinstance(side, int):
        if side in [1, -1]:
            return side
        if side == 2:
            return -1
    s = str(side).strip().lower()
    if s in ["black", "b", "1", "x"]:
        return 1
    if s in ["white", "w", "-1", "2", "o"]:
        return -1
    raise ValueError(f"cannot normalize side_to_move/current_player: {side!r}")


def parse_ascii_board_snapshot(text: str, board_size: int) -> list[list[int]]:
    """Parse board snapshots like 15 rows of '. . X O ...' bounded by dashed lines."""
    rows: list[list[int]] = []

    token_map = {
        ".": 0,
        "_": 0,
        "-": 0,
        "X": 1,
        "x": 1,
        "B": 1,
        "b": 1,
        "1": 1,
        "O": -1,
        "o": -1,
        "W": -1,
        "w": -1,
        "2": -1,
    }

    for raw in text.splitlines():
        stripped = raw.strip()
        if not stripped:
            continue
        if set(stripped) <= {"-"}:
            continue

        tokens = stripped.split()
        if len(tokens) != board_size:
            continue
        if not all(tok in token_map for tok in tokens):
            continue

        rows.append([token_map[tok] for tok in tokens])

    if len(rows) != board_size:
        raise ValueError(
            f"ASCII board parse failed: expected {board_size} rows, got {len(rows)}"
        )

    return rows


def validate_board(board: Any, board_size: int) -> list[list[int]]:
    if isinstance(board, str):
        return parse_ascii_board_snapshot(board, board_size)

    if not isinstance(board, list) or len(board) != board_size:
        raise ValueError("board is not a board_size x board_size list")

    out: list[list[int]] = []
    for row in board:
        if not isinstance(row, list) or len(row) != board_size:
            raise ValueError("board row has wrong length")
        out.append([int(x) for x in row])
    return out


def is_legal_rc(board: list[list[int]], rc: tuple[int, int]) -> bool:
    r, c = rc
    return 0 <= r < len(board) and 0 <= c < len(board) and int(board[r][c]) == 0


def xy_to_rc(xy: tuple[int, int]) -> tuple[int, int]:
    x, y = xy
    return (y, x)


def maybe_coord_pair(obj: Any, board_size: int) -> tuple[int, int] | None:
    if not (
        isinstance(obj, (list, tuple))
        and len(obj) == 2
        and all(isinstance(v, int) for v in obj)
    ):
        return None
    a, b = int(obj[0]), int(obj[1])
    if 0 <= a < board_size and 0 <= b < board_size:
        return (a, b)
    return None


def extract_coords_from_string(text: str, board_size: int) -> list[tuple[int, int]]:
    coords: list[tuple[int, int]] = []
    seen: set[tuple[int, int]] = set()

    # Patterns like [r,c], (r,c), r,c, rc=7,10, x=10 y=7.
    for m in re.finditer(r"(?<!\d)(1[0-4]|[0-9])\s*[,，]\s*(1[0-4]|[0-9])(?!\d)", text):
        rc = (int(m.group(1)), int(m.group(2)))
        if rc not in seen:
            seen.add(rc)
            coords.append(rc)

    # Patterns like H8, K10. Treat as Gomoku x-letter/y-number, convert to rc.
    # This is intentionally secondary because numeric rc is less ambiguous.
    for m in re.finditer(r"\b([A-Oa-o])\s*(1[0-5]|[1-9])\b", text):
        col = ord(m.group(1).upper()) - ord("A")
        row = int(m.group(2)) - 1
        if 0 <= row < board_size and 0 <= col < board_size:
            rc = (row, col)
            if rc not in seen:
                seen.add(rc)
                coords.append(rc)

    return coords


def extract_candidate_target_rcs(snapshot: dict[str, Any], board: list[list[int]], board_size: int) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    seen: set[tuple[int, int]] = set()

    priority_fields = [
        "next_rapfi_bestline",
        "previous_rapfi_bestline",
        "direct",
        "policy_safety",
        "mcts_safety",
        "mcts_raw",
        "value",
        "notes",
    ]

    def add(rc: tuple[int, int], source_field: str, source_kind: str, raw: Any) -> None:
        if rc in seen:
            return
        if not is_legal_rc(board, rc):
            return
        seen.add(rc)
        candidates.append(
            {
                "target_rc": list(rc),
                "target_source_field": source_field,
                "target_source_kind": source_kind,
                "target_source_preview": str(raw)[:240],
            }
        )

    for field in priority_fields:
        if field not in snapshot:
            continue
        raw = snapshot[field]

        # Direct list pair.
        pair = maybe_coord_pair(raw, board_size)
        if pair is not None:
            add(pair, field, "direct_pair_rc", raw)

        # Dict/list recursive search.
        stack = [raw]
        while stack:
            cur = stack.pop()
            if isinstance(cur, dict):
                for k, v in cur.items():
                    lk = str(k).lower()
                    pair = maybe_coord_pair(v, board_size)
                    if pair is not None:
                        # Prefer rc semantics for rc/row/col keys, xy semantics for xy keys.
                        if "xy" in lk:
                            add(xy_to_rc(pair), f"{field}.{k}", "nested_pair_xy", v)
                        else:
                            add(pair, f"{field}.{k}", "nested_pair_rc", v)
                    elif isinstance(v, (dict, list)):
                        stack.append(v)
                    elif isinstance(v, str):
                        for rc in extract_coords_from_string(v, board_size):
                            add(rc, f"{field}.{k}", "nested_string_coord", v)
            elif isinstance(cur, list):
                pair = maybe_coord_pair(cur, board_size)
                if pair is not None:
                    add(pair, field, "list_pair_rc", cur)
                else:
                    stack.extend(cur)
            elif isinstance(cur, str):
                for rc in extract_coords_from_string(cur, board_size):
                    add(rc, field, "string_coord", cur)

    return candidates


def softmax_masked(logits: np.ndarray, legal_mask: np.ndarray) -> np.ndarray:
    masked = logits.astype(np.float64).copy()
    masked[~legal_mask.astype(bool)] = -np.inf
    finite = np.isfinite(masked)
    if not finite.any():
        raise ValueError("no finite legal logits")
    m = np.max(masked[finite])
    exp = np.zeros_like(masked, dtype=np.float64)
    exp[finite] = np.exp(masked[finite] - m)
    denom = exp.sum()
    if denom <= 0 or not math.isfinite(float(denom)):
        raise ValueError("invalid softmax denominator")
    return exp / denom


def score_board_policy(
    model: torch.nn.Module,
    board: list[list[int]],
    current_player: int,
    board_size: int,
    device: torch.device,
) -> tuple[np.ndarray, np.ndarray, list[int]]:
    state = encode_state(board, current_player, board_size)
    x = torch.tensor(state, dtype=torch.float32, device=device).unsqueeze(0)

    model.eval()
    with torch.no_grad():
        out = model(x)

    if isinstance(out, tuple):
        policy_logits = out[0]
    elif isinstance(out, dict):
        policy_logits = out.get("policy_logits") or out.get("policy") or out.get("logits")
    else:
        policy_logits = out

    if policy_logits is None:
        raise ValueError("model output does not contain policy logits")

    logits = policy_logits.detach().cpu().numpy().reshape(-1)
    legal_mask = legal_mask_from_board(board, board_size).astype(bool)
    probs = softmax_masked(logits, legal_mask)

    legal_actions = [int(a) for a in np.where(legal_mask)[0]]
    legal_actions.sort(key=lambda a: float(logits[a]), reverse=True)
    return logits, probs, legal_actions


def rank_of_action(action: int, legal_actions_sorted: list[int]) -> int:
    try:
        return legal_actions_sorted.index(action) + 1
    except ValueError:
        return 10**9


def load_existing_case_ids(reference_dataset: Path) -> set[str]:
    if not reference_dataset.exists():
        return set()
    data = read_json(reference_dataset)
    ids = set()
    if isinstance(data, dict):
        for key in ["samples", "protected_eval_samples", "tail_eval_samples", "quarantine_samples"]:
            for row in data.get(key, []) or []:
                if isinstance(row, dict) and row.get("case_id"):
                    ids.add(str(row["case_id"]))
    return ids


def main() -> int:
    args = parse_args()
    device = torch.device(args.device)

    snapshots = read_json(args.board_snapshots)
    if not isinstance(snapshots, list):
        raise ValueError("board snapshots must be a list")

    existing_case_ids = load_existing_case_ids(args.reference_dataset)

    model = load_model(
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
            board = validate_board(snapshot["board_snapshot_before_decision"], args.board_size)
            current_player = normalize_side(snapshot.get("side_to_move"))
        except Exception:
            skipped["bad_snapshot_schema"] += 1
            continue

        try:
            logits, probs, legal_actions_sorted = score_board_policy(
                model, board, current_player, args.board_size, device
            )
        except Exception as exc:
            skipped[f"policy_score_error:{type(exc).__name__}"] += 1
            continue

        raw_targets = extract_candidate_target_rcs(snapshot, board, args.board_size)
        if not raw_targets:
            skipped["no_candidate_target_extracted"] += 1
            continue

        for t_i, target_info in enumerate(raw_targets):
            target_rc = tuple(target_info["target_rc"])
            try:
                target_action = rc_to_action(target_rc, args.board_size)
            except Exception:
                skipped["bad_target_action"] += 1
                continue

            if target_action not in legal_actions_sorted:
                skipped["target_not_legal"] += 1
                continue

            target_rank = rank_of_action(target_action, legal_actions_sorted)
            target_prob = float(probs[target_action])
            target_logit = float(logits[target_action])

            suppress_actions = [a for a in legal_actions_sorted if a != target_action][: args.top_suppress]
            if len(suppress_actions) < args.top_suppress:
                skipped["not_enough_suppress_actions"] += 1
                continue

            suppress_rcs = [action_to_rc(a, args.board_size) for a in suppress_actions]
            suppress_candidates = [
                {
                    "action": int(a),
                    "rc": action_to_rc(a, args.board_size),
                    "rank": rank_of_action(a, legal_actions_sorted),
                    "prob": float(probs[a]),
                    "gap": float(target_logit - float(logits[a])),
                }
                for a in suppress_actions
            ]

            case_id = (
                f"tailgen_g{snapshot.get('game_number', 'na')}"
                f"_m{snapshot.get('move_count', 'na')}"
                f"_t{t_i}_{target_rc[0]}_{target_rc[1]}"
            )

            if case_id in existing_case_ids:
                skipped["case_id_already_exists"] += 1
                continue

            if target_rank > args.tail_rank_threshold:
                candidate_bucket = "P0_tail_guard_candidate"
            elif target_rank >= args.near_tail_rank_threshold:
                candidate_bucket = "near_tail_review_candidate"
            else:
                candidate_bucket = "non_tail_reference_candidate"

            row = {
                "case_id": case_id,
                "candidate_bucket": candidate_bucket,
                "source": "board_snapshot_before_decision_manual_schema_patch",
                "board_size": args.board_size,
                "win_length": args.win_length,
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
                "label_type": "tail_guard_candidate_source",
                "suggested_split": "tail_eval_rank_gt50_heldout_only" if candidate_bucket == "P0_tail_guard_candidate" else "review_only",
                "training_allowed": False,
                "notes": (
                    "Generated as tail guard candidate source only. "
                    "Requires human/schema review before any materialized dataset."
                ),
            }
            candidate_rows.append(row)

    # Sort strongest tail first, then near-tail.
    candidate_rows.sort(
        key=lambda r: (
            0 if r["candidate_bucket"] == "P0_tail_guard_candidate" else 1,
            -int(r["before_target_rank"]),
            float(r["before_target_prob"]),
        )
    )

    tail_rows = [r for r in candidate_rows if r["candidate_bucket"] == "P0_tail_guard_candidate"]
    near_tail_rows = [r for r in candidate_rows if r["candidate_bucket"] == "near_tail_review_candidate"]

    decision = (
        "TAIL_GUARD_CANDIDATE_GENERATION_TARGET_MET"
        if len(tail_rows) >= args.min_tail_target
        else "TAIL_GUARD_CANDIDATE_GENERATION_PARTIAL"
        if len(tail_rows) > 0
        else "TAIL_GUARD_CANDIDATE_GENERATION_NO_TAIL"
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
        "name": "teacher_divergence_tail_guard_candidate_source",
        "description": "Candidate source only; not a training dataset.",
        "decision": decision,
        "scope": "candidate source generation only; no training/checkpoint save/export/benchmark/promotion",
        "model_checkpoint": str(args.model_checkpoint),
        "board_snapshots": str(args.board_snapshots),
        "reference_dataset": str(args.reference_dataset),
        "manual_schema_patch": {
            "snapshot_board_field": "board_snapshot_before_decision",
            "snapshot_after_field": "board_snapshot_after_decision",
            "side_field": "side_to_move",
            "game_id_field": "game_number",
            "move_id_field": "move_count",
        },
        "summary": {
            "snapshots": len(snapshots),
            "candidate_rows": len(candidate_rows),
            "tail_guard_candidates": len(tail_rows),
            "near_tail_review_candidates": len(near_tail_rows),
            "min_tail_target": args.min_tail_target,
            "tail_rank_threshold": args.tail_rank_threshold,
            "near_tail_rank_threshold": args.near_tail_rank_threshold,
            "skipped": dict(sorted(skipped.items())),
        },
        "tail_guard_candidates": tail_rows,
        "near_tail_review_candidates": near_tail_rows,
    }
    OUT_JSON.write_text(json.dumps(source_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    summary = {
        "decision": decision,
        "scope": "candidate source generation only; no training/checkpoint save/export/benchmark/promotion",
        "snapshots": len(snapshots),
        "candidate_rows": len(candidate_rows),
        "tail_guard_candidates": len(tail_rows),
        "near_tail_review_candidates": len(near_tail_rows),
        "min_tail_target": args.min_tail_target,
        "tail_rank_threshold": args.tail_rank_threshold,
        "near_tail_rank_threshold": args.near_tail_rank_threshold,
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
    lines += ["# Teacher-divergence tail guard candidate generation", ""]
    lines += ["## Scope", ""]
    lines += [
        "- Candidate source generation only.",
        "- No final dataset materialization.",
        "- No training.",
        "- No checkpoint save.",
        "- No C export, no public benchmark, no promotion.",
        "",
    ]

    lines += ["## Manual schema patch", ""]
    lines += [
        "- snapshot board field: `board_snapshot_before_decision`",
        "- optional after field: `board_snapshot_after_decision`",
        "- side field: `side_to_move`",
        "- game id field: `game_number`",
        "- move id field: `move_count`",
        "",
    ]

    lines += ["## Summary", ""]
    lines += [
        f"- snapshots scanned: `{len(snapshots)}`",
        f"- candidate rows: `{len(candidate_rows)}`",
        f"- P0 tail guard candidates: `{len(tail_rows)}` / `{args.min_tail_target}`",
        f"- near-tail review candidates: `{len(near_tail_rows)}`",
        f"- tail rank threshold: `>{args.tail_rank_threshold}`",
        "",
    ]

    lines += ["## Skipped counts", ""]
    lines += ["| reason | count |", "|---|---:|"]
    for k, v in sorted(skipped.items()):
        lines.append(f"| {k} | {v} |")
    lines.append("")

    lines += ["## Top tail candidates", ""]
    lines += [
        "| case_id | game | move | side | target_rc | rank | prob | source_field |",
        "|---|---:|---:|---|---|---:|---:|---|",
    ]
    for r in tail_rows[:30]:
        lines.append(
            f"| `{r['case_id']}` | {r['game_number']} | {r['move_count']} | "
            f"{r['side_to_move']} | `{r['target_rc']}` | {r['before_target_rank']} | "
            f"{r['before_target_prob']:.6g} | `{r['target_source_field']}` |"
        )
    if not tail_rows:
        lines.append("| _none_ |  |  |  |  |  |  |  |")
    lines.append("")

    lines += ["## Decision", ""]
    lines += [f"`{decision}`", ""]

    if decision == "TAIL_GUARD_CANDIDATE_GENERATION_TARGET_MET":
        lines += [
            "The P0 tail guard candidate target is met at source-review level.",
            "",
            "Next step should be review/materialization only. These rows must remain heldout tail guards.",
            "",
        ]
    elif decision == "TAIL_GUARD_CANDIDATE_GENERATION_PARTIAL":
        lines += [
            "Some P0 tail guard candidates were generated, but the minimum target is not met.",
            "",
            "Next step should expand snapshot/source coverage before materialization.",
            "",
        ]
    else:
        lines += [
            "No P0 tail guard candidates were generated from the inspected snapshots.",
            "",
            "Next step should add broader position enumeration or a direct Rapfi query source.",
            "",
        ]

    lines += ["## Final note", ""]
    lines += [
        "This output does not authorize training, checkpoint save, C export, public benchmark, promotion, or current_best overwrite.",
        "",
    ]

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("decision:", decision)
    print("snapshots:", len(snapshots))
    print("candidate_rows:", len(candidate_rows))
    print("tail_guard_candidates:", len(tail_rows))
    print("near_tail_review_candidates:", len(near_tail_rows))
    print("skipped:", dict(sorted(skipped.items())))
    print("out_csv:", OUT_CSV)
    print("out_json:", OUT_JSON)
    print("out_summary:", OUT_SUMMARY)
    print("out_report:", OUT_MD)
    print("status: candidate source generation only; no training/checkpoint save/export/benchmark/promotion")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
