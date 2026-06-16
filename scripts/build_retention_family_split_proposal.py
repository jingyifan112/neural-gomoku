#!/usr/bin/env python3
"""
Build a heldout-retention family split proposal.

Purpose:
- Label every heldout_retention row with a family_id.
- Mark repeated blockers, sibling target conflicts, and stable top1 gains.
- Emit CSV/MD proposal for the next split-design step.

This is analysis/proposal only:
- no training
- no checkpoint save
- no C export
- no benchmark
- no promotion
"""

from __future__ import annotations

import argparse
import csv
import glob
import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


DEFAULT_DATASET_JSON = Path("analysis/integration_eval/teacher_divergence_retention_safety_v3_dataset.json")
DEFAULT_OUT_CSV = Path("analysis/integration_eval/retention_family_split_proposal.csv")
DEFAULT_OUT_MD = Path("analysis/integration_eval/retention_family_split_proposal.md")

DEFAULT_EVAL_GLOBS = [
    "analysis/integration_eval/*mixed*ce*eval*.csv",
    "analysis/integration_eval/*mixed_ce*anchor*probe*.csv",
    "analysis/integration_eval/*regression*gated*eval*.csv",
    "analysis/integration_eval/*heldout*regression*.csv",
]

EXCLUDE_EVAL_PATTERNS = [
    "retention_family_split_proposal",
    "family_split_proposal",
]

# Design-stage manual signals from exp/15x15-retention-family-split-design.
# These are proposal labels only; they do not authorize training/promotion.
#
# The critical sibling-conflict family was manually reviewed in the design closeout:
# - family_id: bd:ea22cc14729b88fd
# - sibling targets: 10,7; 7,10; 7,9
# - 7,9 showed stable top1 gain
# - 7,10 and 10,7 showed stable regression
# Therefore sibling targets in this family must not serve as each other's only heldout check.
DESIGN_SIGNAL_BY_SOURCE_TARGET = {
    ("candidate_d_g2_m15_white_last_8_9_target_live_direct_7_10_over_live_final_8_8", "7,10"): {
        "family_id": "bd:ea22cc14729b88fd",
        "repeated_blocker": True,
        "stable_top1_gain": False,
        "forced_outcome": "regression",
        "design_note": "sibling target stable regression from design closeout",
    },
    ("candidate_d_g2_m15_white_last_8_9_target_safe_10_7_over_live_final_8_8", "10,7"): {
        "family_id": "bd:ea22cc14729b88fd",
        "repeated_blocker": True,
        "stable_top1_gain": False,
        "forced_outcome": "regression",
        "design_note": "sibling target stable regression from design closeout",
    },
    ("candidate_d_g2_m15_white_last_8_9_target_safe_7_9_over_live_final_8_8", "7,9"): {
        "family_id": "bd:ea22cc14729b88fd",
        "repeated_blocker": False,
        "stable_top1_gain": True,
        "forced_outcome": "top1_gain",
        "design_note": "sibling target stable top1 gain from design closeout",
    },
}


def is_blank(v: Any) -> bool:
    return v is None or str(v).strip() == "" or str(v).strip().lower() in {"none", "nan", "null"}


def clean_str(v: Any) -> str:
    if is_blank(v):
        return ""
    return str(v).strip()


def norm_col_name(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", s.strip().lower()).strip("_")


def row_get(row: Dict[str, Any], names: Sequence[str], default: str = "") -> str:
    if not row:
        return default
    by_norm = {norm_col_name(k): k for k in row.keys()}
    for name in names:
        key = by_norm.get(norm_col_name(name))
        if key is not None and not is_blank(row.get(key)):
            return clean_str(row.get(key))
    return default


def parse_float(v: Any) -> Optional[float]:
    if is_blank(v):
        return None
    s = str(v).strip()
    if s.lower() in {"true", "false", "yes", "no"}:
        return None
    # Pull the first number from strings like "4 > 3" only when needed elsewhere.
    try:
        x = float(s)
        if math.isfinite(x):
            return x
    except Exception:
        return None
    return None


def truthy_flag(v: Any) -> bool:
    if is_blank(v):
        return False
    s = str(v).strip().lower()
    if s in {"1", "true", "yes", "y", "pass", "failed", "fail"}:
        return True
    if ">" in s:
        return True
    if s.startswith("regress"):
        return True
    try:
        return float(s) != 0.0
    except Exception:
        return False


def norm_move(v: Any) -> str:
    if is_blank(v):
        return ""
    s = str(v).strip()
    nums = re.findall(r"-?\d+", s)
    if len(nums) >= 2:
        return f"{int(nums[0])},{int(nums[1])}"
    return re.sub(r"\s+", "", s)


def load_json_rows(path: Path) -> List[Dict[str, Any]]:
    with path.open("r", encoding="utf-8") as f:
        obj = json.load(f)

    def walk(x: Any) -> Iterable[Dict[str, Any]]:
        if isinstance(x, list):
            for item in x:
                yield from walk(item)
        elif isinstance(x, dict):
            for key in ("rows", "data", "examples", "items", "records", "positions"):
                if key in x and isinstance(x[key], list):
                    yield from walk(x[key])
                    return
            # Treat dicts with common row-ish keys as a row.
            rowish_keys = {
                "split", "role", "policy_target", "teacher_move",
                "source_path", "side_to_move", "last_move", "board",
                "moves", "position_id", "row_id", "id",
            }
            if any(k in x for k in rowish_keys):
                yield x

    return list(walk(obj))


def load_csv_rows(path: Path) -> List[Dict[str, Any]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = []
        for r in reader:
            rr = dict(r)
            rr["__eval_source"] = str(path)
            rows.append(rr)
        return rows


def discover_eval_csvs(explicit_csvs: Sequence[Path], globs_: Sequence[str]) -> List[Path]:
    paths: List[Path] = []
    for p in explicit_csvs:
        if p.exists():
            paths.append(p)
    for pat in globs_:
        for s in glob.glob(pat):
            p = Path(s)
            if not p.exists() or not p.is_file():
                continue
            name = str(p)
            if any(excl in name for excl in EXCLUDE_EVAL_PATTERNS):
                continue
            if p.suffix.lower() != ".csv":
                continue
            paths.append(p)
    # Deduplicate while preserving sorted stable order.
    unique = sorted(set(paths), key=lambda x: str(x))
    return unique


def is_heldout_retention(row: Dict[str, Any]) -> bool:
    split = row_get(row, ["split"])
    role = row_get(row, ["role", "label_role", "label_type"])
    hay = f"{split} {role}".lower()
    return "heldout_retention" in hay or "heldout retention" in hay


def natural_row_id(row: Dict[str, Any]) -> str:
    explicit = row_get(row, [
        "row_id", "id", "case_id", "position_id", "example_id",
        "name", "label_id", "uid",
    ])
    if explicit:
        return explicit

    parts = [
        row_get(row, ["source_path"]),
        row_get(row, ["source_id", "source_name"]),
        row_get(row, ["game_id", "game"]),
        row_get(row, ["ply", "move_index", "move_number"]),
        row_get(row, ["side_to_move", "side"]),
        norm_move(row_get(row, ["last_move"])),
        norm_move(row_get(row, ["policy_target", "target", "target_move"])),
        norm_move(row_get(row, ["teacher_move"])),
    ]
    key = "|".join(p for p in parts if p)
    if key:
        return key

    raw = json.dumps(row, sort_keys=True, ensure_ascii=False, default=str)
    return "row:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def source_family_key(row: Dict[str, Any]) -> str:
    explicit = row_get(row, ["source_family", "source_family_id", "family_key"])
    if explicit:
        return explicit

    candidates = [
        row_get(row, ["source_id", "source_name", "case_id", "row_id", "id"]),
        Path(row_get(row, ["source_path"])).stem if row_get(row, ["source_path"]) else "",
    ]
    raw = "|".join(c for c in candidates if c)
    if not raw:
        raw = natural_row_id(row)

    s = raw.lower()

    # Remove target/over suffixes so sibling target rows from the same source position group together.
    s = re.sub(r"_target(?:_[a-z]+)?_\d+_\d+.*$", "", s)
    s = re.sub(r"_over(?:_[a-z]+)?_\d+_\d+.*$", "", s)
    s = re.sub(r"target(?:-[a-z]+)?-\d+-\d+.*$", "", s)
    s = re.sub(r"over(?:-[a-z]+)?-\d+-\d+.*$", "", s)

    # Keep useful game/ply/side/last-move information when present.
    return s.strip("_-| ")


def canonical_position_payload(row: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    boardish_keys = [
        "board", "board_rows", "grid", "position", "stones",
        "black_stones", "white_stones", "moves", "move_history",
        "history", "replay_moves", "played_moves",
    ]

    payload: Dict[str, Any] = {}
    for k in boardish_keys:
        if k in row and not is_blank(row.get(k)):
            payload[k] = row[k]

    # These define side/state but not the policy target.
    for k in ["board_size", "side_to_move", "side", "last_move"]:
        if k in row and not is_blank(row.get(k)):
            payload[k] = row[k]

    if not payload:
        return None
    return payload


def derive_family_id(row: Dict[str, Any]) -> str:
    explicit = row_get(row, ["family_id", "retention_family_id"])
    if explicit:
        if ":" in explicit:
            return explicit
        return "family:" + explicit

    digest = row_get(row, [
        "board_digest", "position_digest", "state_digest",
        "position_hash", "board_hash",
    ])
    if digest:
        digest = re.sub(r"[^a-fA-F0-9]", "", digest)
        if digest:
            return "bd:" + digest[:16].lower()

    payload = canonical_position_payload(row)
    if payload is not None:
        raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
        return "bd:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]

    skey = source_family_key(row)
    return "sf:" + hashlib.sha256(skey.encode("utf-8")).hexdigest()[:16]


def classify_eval(row: Dict[str, Any]) -> Dict[str, Any]:
    rank_before = parse_float(row_get(row, [
        "policy_rank_before", "target_rank_before", "rank_before",
        "before_rank", "base_rank", "old_rank", "pre_rank",
        "rank_old", "current_rank", "baseline_rank", "reference_rank",
    ]))
    rank_after = parse_float(row_get(row, [
        "policy_rank_after", "target_rank_after", "rank_after",
        "after_rank", "candidate_rank", "new_rank", "post_rank",
        "rank_new", "probe_rank",
    ]))

    prob_before = parse_float(row_get(row, [
        "policy_prob_before", "target_prob_before", "prob_before",
        "before_prob", "base_prob", "old_prob", "pre_prob",
        "prob_old", "current_prob", "baseline_prob", "reference_prob",
    ]))
    prob_after = parse_float(row_get(row, [
        "policy_prob_after", "target_prob_after", "prob_after",
        "after_prob", "candidate_prob", "new_prob", "post_prob",
        "prob_new", "probe_prob",
    ]))

    explicit_regression = any(
        truthy_flag(row_get(row, [name]))
        for name in [
            "regressed", "is_regression", "rank_regressed",
            "prob_regressed", "heldout_regressed", "gate_failed",
            "fail_reason",
        ]
    )

    rank_regression = (
        rank_before is not None and rank_after is not None and rank_after > rank_before
    )
    prob_regression = (
        prob_before is not None and prob_after is not None and prob_after + 1e-12 < prob_before
    )

    regression = explicit_regression or rank_regression or prob_regression

    rank_gain = (
        rank_before is not None and rank_after is not None and rank_after < rank_before
    )
    prob_gain = (
        prob_before is not None and prob_after is not None and prob_after > prob_before + 1e-12
    )
    top1_gain = (
        rank_before is not None
        and rank_after is not None
        and int(rank_after) == 1
        and int(rank_before) != 1
        and rank_after < rank_before
    )

    if regression:
        outcome = "regression"
    elif top1_gain:
        outcome = "top1_gain"
    elif rank_gain or prob_gain:
        outcome = "gain"
    else:
        outcome = "neutral_or_unknown"

    return {
        "rank_before": rank_before,
        "rank_after": rank_after,
        "prob_before": prob_before,
        "prob_after": prob_after,
        "regression": regression,
        "rank_regression": rank_regression,
        "prob_regression": prob_regression,
        "gain": rank_gain or prob_gain,
        "top1_gain": top1_gain,
        "outcome": outcome,
    }


def fmt_values(vals: Iterable[Any]) -> str:
    clean = []
    for v in vals:
        if v is None:
            continue
        if isinstance(v, float):
            if abs(v - int(v)) < 1e-9:
                clean.append(str(int(v)))
            else:
                clean.append(f"{v:.6g}")
        else:
            clean.append(str(v))
    return ";".join(dict.fromkeys(clean))


def yesno(x: bool) -> str:
    return "yes" if x else "no"


def compact_source(row: Dict[str, Any]) -> str:
    for k in ["source_id", "case_id", "row_id", "id", "position_id"]:
        v = row_get(row, [k])
        if v:
            return v
    sp = row_get(row, ["source_path"])
    if sp:
        return Path(sp).name
    return natural_row_id(row)


def make_markdown_table(headers: List[str], rows: List[List[Any]], max_rows: int = 200) -> str:
    rows = rows[:max_rows]
    out = []
    out.append("| " + " | ".join(headers) + " |")
    out.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for r in rows:
        cells = []
        for x in r:
            s = str(x).replace("\n", " ").replace("|", "\\|")
            cells.append(s)
        out.append("| " + " | ".join(cells) + " |")
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset-json", type=Path, default=DEFAULT_DATASET_JSON)
    ap.add_argument("--eval-csv", action="append", type=Path, default=[])
    ap.add_argument("--eval-glob", action="append", default=[])
    ap.add_argument("--out-csv", type=Path, default=DEFAULT_OUT_CSV)
    ap.add_argument("--out-md", type=Path, default=DEFAULT_OUT_MD)
    ap.add_argument("--min-repeated-regressions", type=int, default=2)
    args = ap.parse_args()

    eval_globs = args.eval_glob or DEFAULT_EVAL_GLOBS
    eval_paths = discover_eval_csvs(args.eval_csv, eval_globs)
    if not eval_paths:
        raise SystemExit(
            "No eval CSVs found. Pass --eval-csv explicitly or check analysis/integration_eval."
        )

    dataset_rows: List[Dict[str, Any]] = []
    dataset_by_id: Dict[str, Dict[str, Any]] = {}
    if args.dataset_json.exists():
        dataset_rows = load_json_rows(args.dataset_json)
        for r in dataset_rows:
            dataset_by_id[natural_row_id(r)] = r

    eval_rows: List[Dict[str, Any]] = []
    for p in eval_paths:
        eval_rows.extend(load_csv_rows(p))

    heldout_entries: List[Dict[str, Any]] = []
    for r in eval_rows:
        if not is_heldout_retention(r):
            continue
        key = natural_row_id(r)
        base = dataset_by_id.get(key, {})
        merged = dict(base)
        merged.update(r)
        merged["__row_key"] = key
        merged["__family_id"] = derive_family_id(merged)
        merged["__policy_target"] = norm_move(row_get(merged, [
            "policy_target", "target", "target_move", "label_move"
        ]))
        merged["__teacher_move"] = norm_move(row_get(merged, [
            "teacher_move", "teacher", "best_move"
        ]))
        merged["__source_compact"] = compact_source(merged)

        design_signal = DESIGN_SIGNAL_BY_SOURCE_TARGET.get(
            (merged["__source_compact"], merged["__policy_target"])
        )
        if design_signal:
            merged["__family_id"] = design_signal["family_id"]
            merged["__design_signal"] = design_signal
        else:
            merged["__design_signal"] = {}

        merged["__class"] = classify_eval(merged)
        if design_signal:
            forced = design_signal.get("forced_outcome", "")
            if forced == "regression":
                merged["__class"]["regression"] = True
                merged["__class"]["rank_regression"] = True
                merged["__class"]["top1_gain"] = False
                merged["__class"]["gain"] = False
                merged["__class"]["outcome"] = "regression"
            elif forced == "top1_gain":
                merged["__class"]["regression"] = False
                merged["__class"]["rank_regression"] = False
                merged["__class"]["prob_regression"] = False
                merged["__class"]["top1_gain"] = True
                merged["__class"]["gain"] = True
                merged["__class"]["outcome"] = "top1_gain"

        heldout_entries.append(merged)

    if not heldout_entries:
        raise SystemExit(
            f"Found {len(eval_rows)} eval rows from {len(eval_paths)} CSVs, "
            "but no heldout_retention rows. Check split/role column names."
        )

    by_row: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for e in heldout_entries:
        by_row[e["__row_key"]].append(e)

    row_summaries: List[Dict[str, Any]] = []
    for row_key, entries in sorted(by_row.items()):
        first = entries[0]
        classes = [e["__class"] for e in entries]
        outcomes = Counter(c["outcome"] for c in classes)

        regression_count = sum(1 for c in classes if c["regression"])
        gain_count = sum(1 for c in classes if c["gain"])
        top1_gain_count = sum(1 for c in classes if c["top1_gain"])

        explicit_repeated = any(
            truthy_flag(row_get(e, ["repeated_blocker", "is_repeated_blocker", "blocker_repeated"]))
            for e in entries
        )
        design_repeated = any(
            bool(e.get("__design_signal", {}).get("repeated_blocker", False))
            for e in entries
        )
        repeated_blocker = design_repeated or explicit_repeated or regression_count >= args.min_repeated_regressions

        eval_count = len(entries)
        design_stable_top1_gain = any(
            bool(e.get("__design_signal", {}).get("stable_top1_gain", False))
            for e in entries
        )
        stable_top1_gain = design_stable_top1_gain or (
            top1_gain_count > 0
            and regression_count == 0
            and top1_gain_count == eval_count
        )

        family_id = first["__family_id"]
        target = first["__policy_target"]

        row_summaries.append({
            "family_id": family_id,
            "row_key": row_key,
            "source": first["__source_compact"],
            "source_path": row_get(first, ["source_path"]),
            "policy_target": target,
            "teacher_move": first["__teacher_move"],
            "side_to_move": row_get(first, ["side_to_move", "side"]),
            "last_move": norm_move(row_get(first, ["last_move"])),
            "eval_count": eval_count,
            "eval_sources": fmt_values(Path(e["__eval_source"]).name for e in entries),
            "rank_before_values": fmt_values(c["rank_before"] for c in classes),
            "rank_after_values": fmt_values(c["rank_after"] for c in classes),
            "prob_before_values": fmt_values(c["prob_before"] for c in classes),
            "prob_after_values": fmt_values(c["prob_after"] for c in classes),
            "outcomes": ",".join(f"{k}:{v}" for k, v in sorted(outcomes.items())),
            "regression_count": regression_count,
            "gain_count": gain_count,
            "top1_gain_count": top1_gain_count,
            "repeated_blocker": repeated_blocker,
            "stable_top1_gain": stable_top1_gain,
        })

    by_family: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for r in row_summaries:
        by_family[r["family_id"]].append(r)

    family_info: Dict[str, Dict[str, Any]] = {}
    for fid, rows in sorted(by_family.items()):
        targets = sorted(t for t in {r["policy_target"] for r in rows} if t)
        any_repeated = any(r["repeated_blocker"] for r in rows)
        any_regression = any(r["regression_count"] > 0 for r in rows)
        any_stable_top1 = any(r["stable_top1_gain"] for r in rows)
        any_gain = any(r["gain_count"] > 0 or r["top1_gain_count"] > 0 for r in rows)

        sibling_conflict = len(targets) >= 2 and any_regression and any_stable_top1
        mixed_signal_conflict = any_regression and any_gain

        needs_nonheldout = any_repeated or sibling_conflict or mixed_signal_conflict

        if needs_nonheldout:
            heldout_gate_policy = "family_level_or_external_only"
            family_recommendation = "add_nonheldout_retention_anchor_for_family"
        elif any_stable_top1:
            heldout_gate_policy = "keep_heldout_gate"
            family_recommendation = "keep_as_heldout_gate_family"
        else:
            heldout_gate_policy = "keep_heldout_gate_review"
            family_recommendation = "manual_review_before_next_probe"

        important_family = set(["10,7", "7,10", "7,9"]).issubset(set(targets))

        family_info[fid] = {
            "family_id": fid,
            "row_count": len(rows),
            "targets": ";".join(targets),
            "repeated_blocker_family": any_repeated,
            "sibling_target_conflict": sibling_conflict,
            "mixed_signal_conflict": mixed_signal_conflict,
            "stable_top1_gain_family": any_stable_top1,
            "needs_nonheldout_retention_anchor": needs_nonheldout,
            "heldout_gate_policy": heldout_gate_policy,
            "family_recommendation": family_recommendation,
            "important_10_7_7_10_7_9_family": important_family,
        }

    proposal_rows: List[Dict[str, Any]] = []
    for r in row_summaries:
        finfo = family_info[r["family_id"]]

        if r["repeated_blocker"] or r["regression_count"] > 0:
            split_proposal = "nonheldout_retention_anchor_candidate"
            reason = "row regressed/repeated as heldout blocker"
        elif r["stable_top1_gain"]:
            split_proposal = "heldout_gate_candidate"
            reason = "stable top1 gain without regression in available evals"
        else:
            split_proposal = "heldout_gate_review"
            reason = "neutral or insufficient signal"

        out = dict(r)
        out.update({
            "sibling_target_conflict": finfo["sibling_target_conflict"],
            "mixed_signal_conflict": finfo["mixed_signal_conflict"],
            "family_targets": finfo["targets"],
            "needs_nonheldout_retention_anchor": finfo["needs_nonheldout_retention_anchor"],
            "heldout_gate_policy": finfo["heldout_gate_policy"],
            "family_recommendation": finfo["family_recommendation"],
            "important_10_7_7_10_7_9_family": finfo["important_10_7_7_10_7_9_family"],
            "split_proposal": split_proposal,
            "reason": reason,
        })
        proposal_rows.append(out)

    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "family_id",
        "row_key",
        "source",
        "policy_target",
        "teacher_move",
        "side_to_move",
        "last_move",
        "eval_count",
        "eval_sources",
        "rank_before_values",
        "rank_after_values",
        "prob_before_values",
        "prob_after_values",
        "outcomes",
        "regression_count",
        "gain_count",
        "top1_gain_count",
        "repeated_blocker",
        "stable_top1_gain",
        "sibling_target_conflict",
        "mixed_signal_conflict",
        "family_targets",
        "needs_nonheldout_retention_anchor",
        "heldout_gate_policy",
        "family_recommendation",
        "important_10_7_7_10_7_9_family",
        "split_proposal",
        "reason",
        "source_path",
    ]

    with args.out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        w.writeheader()
        for r in proposal_rows:
            rr = dict(r)
            for k in [
                "repeated_blocker", "stable_top1_gain", "sibling_target_conflict",
                "mixed_signal_conflict", "needs_nonheldout_retention_anchor",
                "important_10_7_7_10_7_9_family",
            ]:
                rr[k] = yesno(bool(rr[k]))
            w.writerow({k: rr.get(k, "") for k in fieldnames})

    family_rows = sorted(family_info.values(), key=lambda x: (not x["important_10_7_7_10_7_9_family"], x["family_id"]))

    md_lines: List[str] = []
    md_lines.append("# Retention family split proposal")
    md_lines.append("")
    md_lines.append("Scope: proposal builder only. No training, checkpoint save, C export, benchmark, or promotion was run.")
    md_lines.append("")
    md_lines.append("## Inputs")
    md_lines.append("")
    md_lines.append(f"- dataset_json: `{args.dataset_json}`")
    md_lines.append("- eval_csvs:")
    for p in eval_paths:
        md_lines.append(f"  - `{p}`")
    md_lines.append("")
    md_lines.append("## Summary")
    md_lines.append("")
    md_lines.append(f"- heldout rows: {len(row_summaries)}")
    md_lines.append(f"- families: {len(family_rows)}")
    md_lines.append(f"- repeated blocker rows: {sum(1 for r in row_summaries if r['repeated_blocker'])}")
    md_lines.append(f"- stable top1 gain rows: {sum(1 for r in row_summaries if r['stable_top1_gain'])}")
    md_lines.append(f"- families needing non-heldout retention anchor: {sum(1 for f in family_rows if f['needs_nonheldout_retention_anchor'])}")
    md_lines.append(f"- families keeping heldout gate directly/review: {sum(1 for f in family_rows if not f['needs_nonheldout_retention_anchor'])}")
    md_lines.append("")

    important = [f for f in family_rows if f["important_10_7_7_10_7_9_family"]]
    if important:
        md_lines.append("## High-priority sibling-conflict family")
        md_lines.append("")
        for f in important:
            md_lines.append(
                f"- `{f['family_id']}` has targets `{f['targets']}`; "
                f"recommendation: `{f['family_recommendation']}`; "
                f"heldout_gate_policy: `{f['heldout_gate_policy']}`."
            )
        md_lines.append("")

    md_lines.append("## Family-level proposal")
    md_lines.append("")
    md_lines.append(make_markdown_table(
        [
            "family_id",
            "rows",
            "targets",
            "repeated_blocker",
            "sibling_conflict",
            "mixed_signal",
            "stable_top1_gain",
            "needs_nonheldout_anchor",
            "heldout_gate_policy",
            "recommendation",
        ],
        [
            [
                f["family_id"],
                f["row_count"],
                f["targets"],
                yesno(f["repeated_blocker_family"]),
                yesno(f["sibling_target_conflict"]),
                yesno(f["mixed_signal_conflict"]),
                yesno(f["stable_top1_gain_family"]),
                yesno(f["needs_nonheldout_retention_anchor"]),
                f["heldout_gate_policy"],
                f["family_recommendation"],
            ]
            for f in family_rows
        ],
    ))
    md_lines.append("")

    md_lines.append("## Row-level proposal")
    md_lines.append("")
    md_lines.append(make_markdown_table(
        [
            "family_id",
            "source",
            "target",
            "evals",
            "outcomes",
            "repeated_blocker",
            "stable_top1_gain",
            "split_proposal",
            "reason",
        ],
        [
            [
                r["family_id"],
                r["source"],
                r["policy_target"],
                r["eval_count"],
                r["outcomes"],
                yesno(r["repeated_blocker"]),
                yesno(r["stable_top1_gain"]),
                r["split_proposal"],
                r["reason"],
            ]
            for r in proposal_rows
        ],
    ))
    md_lines.append("")

    md_lines.append("## Interpretation rule")
    md_lines.append("")
    md_lines.append(
        "- Families with sibling or mixed-signal conflict should not use one sibling target as the only heldout check for another sibling target."
    )
    md_lines.append(
        "- Rows proposed as `nonheldout_retention_anchor_candidate` are candidates for the next dataset split, not training actions in this branch."
    )
    md_lines.append(
        "- Rows proposed as `heldout_gate_candidate` can remain heldout gates unless a later manual review finds hidden source-family leakage."
    )
    md_lines.append("")

    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    print("wrote", args.out_csv)
    print("wrote", args.out_md)
    print("heldout rows:", len(row_summaries))
    print("families:", len(family_rows))
    print("families needing non-heldout retention anchor:", sum(1 for f in family_rows if f["needs_nonheldout_retention_anchor"]))
    print("families keeping heldout gate/review:", sum(1 for f in family_rows if not f["needs_nonheldout_retention_anchor"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
