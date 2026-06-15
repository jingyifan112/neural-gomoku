#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import hashlib
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


OUT_DIR = Path("analysis/integration_eval")
CLEAN_V2_DATASET = OUT_DIR / "teacher_divergence_retention_clean_v2_dataset.json"

EVAL_CSVS = [
    Path("analysis/integration_eval/current_best_rapfi_failure_eval.csv"),
    Path("analysis/integration_eval/candidate_c_conservative_rapfi_failure_eval.csv"),
    Path("analysis/integration_eval/current_best_margin_3pair_b_rapfi_failure_eval.csv"),
]

SNAPSHOT_JSONS = [
    Path("analysis/integration_eval/b_mcts16_debug_failure_snapshots.json"),
    Path("analysis/integration_eval/candidate_c_mcts16_debug_failure_snapshots.json"),
    Path("analysis/integration_eval/candidate_d_mcts32_debug_failure_snapshots.json"),
    Path("analysis/integration_eval/candidate_d_mcts32_nearend_failure_snapshots.json"),
    Path("analysis/integration_eval/candidate_d_move15_mcts16_debug_failure_snapshots.json"),
]

OUT_CSV = OUT_DIR / "safety_block_candidate_manifest.csv"
OUT_JSON = OUT_DIR / "safety_block_candidate_manifest.json"
OUT_MD = OUT_DIR / "safety_block_candidate_report.md"


def stable_hash(obj: Any) -> str:
    s = json.dumps(obj, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:12]


def norm(x: Any) -> str:
    if x is None:
        return ""
    return str(x).strip()


def norm_move(x: Any) -> str:
    s = norm(x).replace(" ", "")
    return s


def is_move(x: Any) -> bool:
    s = norm_move(x).lower()
    if not s:
        return False
    return s not in {"na", "n/a", "nan", "none", "null", "unknown", "no_move", "no_move_or_na", "pass", "resign"}


def split_moves(x: Any) -> list[str]:
    s = norm(x)
    if not s:
        return []
    # Supports "2,10", "2,10 4,12", "2,10;4,12", or JSON-ish lists poorly but safely.
    s = s.replace(";", " ").replace("|", " ")
    parts = []
    for tok in s.split():
        tok = tok.strip().strip("[](){}")
        if is_move(tok):
            parts.append(norm_move(tok))
    if not parts and is_move(s):
        parts.append(norm_move(s))
    return parts


def key3(row: dict[str, Any]) -> tuple[str, str, str]:
    return (
        norm(row.get("game_number")),
        norm(row.get("move_count")),
        norm(row.get("side_to_move")),
    )


def read_csv(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return [dict(r) for r in csv.DictReader(f)]


def read_json_rows(path: Path) -> list[dict[str, Any]]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(obj, list):
        return [r for r in obj if isinstance(r, dict)]
    if isinstance(obj, dict):
        for k in ["rows", "records", "positions", "snapshots", "samples", "data"]:
            if isinstance(obj.get(k), list):
                return [r for r in obj[k] if isinstance(r, dict)]
    return []


def load_existing_source_ids() -> set[str]:
    if not CLEAN_V2_DATASET.exists():
        return set()
    obj = json.loads(CLEAN_V2_DATASET.read_text(encoding="utf-8"))
    out = set()
    for r in obj.get("rows", []):
        if isinstance(r, dict) and r.get("source_id"):
            out.add(str(r["source_id"]))
    return out


def board_from_snapshot(row: dict[str, Any]) -> str:
    for k in ["board_snapshot_before_decision", "board", "board_strings"]:
        v = row.get(k)
        if v:
            if isinstance(v, str):
                return v
            if isinstance(v, list):
                if all(isinstance(x, str) for x in v):
                    return "\n".join(v)
                return json.dumps(v, ensure_ascii=False)
            return json.dumps(v, ensure_ascii=False, sort_keys=True)
    return ""


def source_family(path: Path) -> str:
    name = path.name
    if name.startswith("b_mcts16"):
        return "b_mcts16"
    if name.startswith("candidate_c_mcts16"):
        return "candidate_c_mcts16"
    if name.startswith("candidate_d_mcts32_nearend"):
        return "candidate_d_mcts32_nearend"
    if name.startswith("candidate_d_mcts32"):
        return "candidate_d_mcts32"
    if name.startswith("candidate_d_move15"):
        return "candidate_d_move15_mcts16"
    return path.stem


def eval_family(path: Path) -> str:
    name = path.name
    if name.startswith("current_best_rapfi_failure_eval"):
        return "current_best"
    if name.startswith("candidate_c_conservative"):
        return "candidate_c_conservative"
    if name.startswith("current_best_margin_3pair_b"):
        return "current_best_margin_3pair_b"
    return path.stem


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    existing_source_ids = load_existing_source_ids()

    snapshots_by_key: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    snapshot_source_counts = Counter()

    for path in SNAPSHOT_JSONS:
        if not path.exists():
            continue
        rows = read_json_rows(path)
        fam = source_family(path)
        snapshot_source_counts[fam] += len(rows)
        for i, r in enumerate(rows):
            rr = dict(r)
            rr["_snapshot_path"] = path.as_posix()
            rr["_snapshot_family"] = fam
            rr["_snapshot_index"] = i
            rr["_board"] = board_from_snapshot(r)
            snapshots_by_key[key3(r)].append(rr)

    candidates = []
    source_audit = []

    for eval_path in EVAL_CSVS:
        if not eval_path.exists():
            source_audit.append({
                "eval_path": eval_path.as_posix(),
                "exists": False,
                "rows": 0,
                "rows_with_expected_block": 0,
                "joined_candidates": 0,
            })
            continue

        eval_rows = read_csv(eval_path)
        fam = eval_family(eval_path)
        rows_with_expected = 0
        joined = 0

        for i, erow in enumerate(eval_rows):
            expected_moves = split_moves(erow.get("expected_blocking_moves", ""))
            opponent_wins = split_moves(erow.get("opponent_immediate_winning_moves", ""))
            logged_direct = norm_move(erow.get("logged_direct", ""))
            logged_final = norm_move(erow.get("logged_final", ""))
            logged_mcts_safety = norm_move(erow.get("logged_mcts_safety", ""))
            direct_top = norm_move(erow.get("direct_policy_top_move", ""))
            sample_id = norm(erow.get("sample_id")) or f"{fam}_{i}"

            if expected_moves:
                rows_with_expected += 1

            if not expected_moves:
                continue

            key = key3(erow)
            matching_snapshots = snapshots_by_key.get(key, [])

            for snap in matching_snapshots:
                board = snap.get("_board", "")
                if not board:
                    continue

                # Target preference: if final or mcts_safety is one of the expected blocks, use that concrete move.
                # Otherwise use the first expected blocking move.
                if logged_final in expected_moves:
                    policy_target = logged_final
                    target_reason = "logged_final_is_expected_block"
                elif logged_mcts_safety in expected_moves:
                    policy_target = logged_mcts_safety
                    target_reason = "logged_mcts_safety_is_expected_block"
                else:
                    policy_target = expected_moves[0]
                    target_reason = "first_expected_blocking_move"

                direct_misses_block = logged_direct not in expected_moves if logged_direct else ""
                direct_top_misses_block = direct_top not in expected_moves if direct_top else ""

                # This is a candidate manifest, not final train data.
                # "train_candidate_candidate" means: structurally promising, still needs acceptance.
                if direct_misses_block is True or direct_top_misses_block is True:
                    suggested_split = "train_candidate_candidate"
                    role_guess = "safety_block_teacher_candidate"
                else:
                    suggested_split = "heldout_retention_candidate"
                    role_guess = "safety_block_retention_candidate"

                source_id = f"{fam}_{sample_id}_{snap['_snapshot_family']}_g{key[0]}_m{key[1]}_{key[2]}"
                already_in_clean_v2 = sample_id in existing_source_ids or source_id in existing_source_ids

                candidate = {
                    "include_hint": "maybe",
                    "source_id": source_id,
                    "sample_id": sample_id,
                    "already_in_clean_v2": already_in_clean_v2,
                    "suggested_split": suggested_split,
                    "role_guess": role_guess,
                    "eval_family": fam,
                    "eval_path": eval_path.as_posix(),
                    "eval_index": i,
                    "snapshot_family": snap["_snapshot_family"],
                    "snapshot_path": snap["_snapshot_path"],
                    "snapshot_index": snap["_snapshot_index"],
                    "game_number": key[0],
                    "move_count": key[1],
                    "side_to_move": key[2],
                    "policy_target": policy_target,
                    "teacher_move": policy_target,
                    "target_reason": target_reason,
                    "expected_blocking_moves": " ".join(expected_moves),
                    "opponent_immediate_winning_moves": " ".join(opponent_wins),
                    "logged_direct": logged_direct,
                    "direct_policy_top_move": direct_top,
                    "logged_policy_safety": norm_move(erow.get("logged_policy_safety", "")),
                    "logged_mcts_raw": norm_move(erow.get("logged_mcts_raw", "")),
                    "logged_mcts_safety": logged_mcts_safety,
                    "logged_final": logged_final,
                    "direct_misses_expected_block": direct_misses_block,
                    "direct_top_misses_expected_block": direct_top_misses_block,
                    "logged_final_blocks_immediate_win": norm(erow.get("logged_final_blocks_immediate_win")),
                    "labeled_failure_type": norm(erow.get("labeled_failure_type")),
                    "preliminary_failure_type": norm(erow.get("preliminary_failure_type")),
                    "model_value_estimate": norm(erow.get("model_value_estimate")),
                    "direct_policy_top_prob": norm(erow.get("direct_policy_top_prob")),
                    "board_digest": stable_hash(board),
                    "board": board,
                    "notes": "candidate only; requires manual/acceptance review before adding to training dataset",
                }
                candidates.append(candidate)
                joined += 1

        source_audit.append({
            "eval_path": eval_path.as_posix(),
            "exists": True,
            "rows": len(eval_rows),
            "rows_with_expected_block": rows_with_expected,
            "joined_candidates": joined,
        })

    # Deduplicate exact same board+target+eval_family+sample combination.
    deduped = []
    seen = set()
    for c in candidates:
        key = (
            c["eval_family"],
            c["sample_id"],
            c["snapshot_family"],
            c["board_digest"],
            c["policy_target"],
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(c)

    candidates = sorted(
        deduped,
        key=lambda r: (
            r["already_in_clean_v2"],
            r["suggested_split"],
            r["eval_family"],
            r["sample_id"],
            r["snapshot_family"],
        ),
    )

    out_obj = {
        "note": "Safety-block candidate manifest only. Not accepted training data.",
        "counts": {
            "candidates": len(candidates),
            "suggested_split_counts": dict(Counter(c["suggested_split"] for c in candidates)),
            "role_guess_counts": dict(Counter(c["role_guess"] for c in candidates)),
            "eval_family_counts": dict(Counter(c["eval_family"] for c in candidates)),
            "snapshot_family_counts": dict(Counter(c["snapshot_family"] for c in candidates)),
        },
        "source_audit": source_audit,
        "snapshot_source_counts": dict(snapshot_source_counts),
        "candidates": candidates,
    }

    OUT_JSON.write_text(json.dumps(out_obj, indent=2, ensure_ascii=False), encoding="utf-8")

    fields = [
        "include_hint", "source_id", "sample_id", "already_in_clean_v2",
        "suggested_split", "role_guess",
        "eval_family", "eval_path", "eval_index",
        "snapshot_family", "snapshot_path", "snapshot_index",
        "game_number", "move_count", "side_to_move",
        "policy_target", "teacher_move", "target_reason",
        "expected_blocking_moves", "opponent_immediate_winning_moves",
        "logged_direct", "direct_policy_top_move",
        "logged_policy_safety", "logged_mcts_raw", "logged_mcts_safety", "logged_final",
        "direct_misses_expected_block", "direct_top_misses_expected_block",
        "logged_final_blocks_immediate_win",
        "labeled_failure_type", "preliminary_failure_type",
        "model_value_estimate", "direct_policy_top_prob",
        "board_digest", "notes",
    ]

    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for c in candidates:
            writer.writerow({k: c.get(k, "") for k in fields})

    md = []
    md.append("# Safety-block candidate manifest report")
    md.append("")
    md.append("This is a candidate manifest only. It does not train, export, benchmark, or modify model weights.")
    md.append("")
    md.append("## Summary")
    md.append("")
    md.append(f"- candidate rows: {len(candidates)}")
    md.append("")
    md.append("### suggested split counts")
    md.append("")
    md.append("| suggested_split | count |")
    md.append("|---|---:|")
    for k, v in Counter(c["suggested_split"] for c in candidates).most_common():
        md.append(f"| {k} | {v} |")
    md.append("")
    md.append("### role guess counts")
    md.append("")
    md.append("| role_guess | count |")
    md.append("|---|---:|")
    for k, v in Counter(c["role_guess"] for c in candidates).most_common():
        md.append(f"| {k} | {v} |")
    md.append("")
    md.append("### eval family counts")
    md.append("")
    md.append("| eval_family | count |")
    md.append("|---|---:|")
    for k, v in Counter(c["eval_family"] for c in candidates).most_common():
        md.append(f"| {k} | {v} |")
    md.append("")
    md.append("### snapshot family counts")
    md.append("")
    md.append("| snapshot_family | count |")
    md.append("|---|---:|")
    for k, v in Counter(c["snapshot_family"] for c in candidates).most_common():
        md.append(f"| {k} | {v} |")
    md.append("")
    md.append("## Source audit")
    md.append("")
    md.append("| eval_path | rows | rows_with_expected_block | joined_candidates |")
    md.append("|---|---:|---:|---:|")
    for s in source_audit:
        md.append(
            f"| `{s['eval_path']}` | {s['rows']} | {s['rows_with_expected_block']} | {s['joined_candidates']} |"
        )
    md.append("")
    md.append("## Candidate rows")
    md.append("")
    md.append("| split_guess | eval | snapshot | sample | side | target | expected | direct | final | direct_miss | top_miss | already_clean_v2 |")
    md.append("|---|---|---|---|---|---|---|---|---|---:|---:|---:|")
    for c in candidates[:120]:
        md.append(
            f"| {c['suggested_split']} | {c['eval_family']} | {c['snapshot_family']} | "
            f"`{c['sample_id']}` | {c['side_to_move']} | `{c['policy_target']}` | "
            f"`{c['expected_blocking_moves']}` | `{c['logged_direct']}` | `{c['logged_final']}` | "
            f"{c['direct_misses_expected_block']} | {c['direct_top_misses_expected_block']} | {c['already_in_clean_v2']} |"
        )
    md.append("")
    md.append("## Interpretation")
    md.append("")
    md.append("- `train_candidate_candidate`: candidate row where direct/top policy appears to miss an immediate-block target.")
    md.append("- `heldout_retention_candidate`: candidate row where logged final already matches the block; likely better as retention/probe unless policy target is separately justified.")
    md.append("- These rows should not be merged into clean v2 automatically. The next step is an acceptance filter for a narrow v3 candidate dataset.")
    md.append("")

    OUT_MD.write_text("\n".join(md).rstrip() + "\n", encoding="utf-8")

    print("wrote", OUT_CSV)
    print("wrote", OUT_JSON)
    print("wrote", OUT_MD)
    print()
    print("candidate_rows", len(candidates))
    print("suggested_split_counts", dict(Counter(c["suggested_split"] for c in candidates)))
    print("role_guess_counts", dict(Counter(c["role_guess"] for c in candidates)))
    print("eval_family_counts", dict(Counter(c["eval_family"] for c in candidates)))
    print("snapshot_family_counts", dict(Counter(c["snapshot_family"] for c in candidates)))
    print("source_audit", source_audit)


if __name__ == "__main__":
    main()
