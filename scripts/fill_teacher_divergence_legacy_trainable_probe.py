#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any

import torch

from fill_teacher_divergence_current_best_probe_round2 import (
    BOARD_SOURCE_PATHS,
    bucket_for_rank,
    load_board_map,
    load_model,
    parse_current_player,
    parse_rc,
    probe_board,
    rc_to_action,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run current_best probe for legacy trainable rows that need suppress schema normalization."
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_expanded_candidate_manifest_with_suppress_round2.csv"),
    )
    parser.add_argument(
        "--plan-csv",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_legacy_trainable_normalization_plan.csv"),
    )
    parser.add_argument(
        "--checkpoint",
        type=Path,
        default=Path("checkpoints/15x15_current_best.pt"),
    )
    parser.add_argument(
        "--out-csv",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_legacy_trainable_current_best_probe_fill.csv"),
    )
    parser.add_argument(
        "--out-report",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_legacy_trainable_current_best_probe_fill_report.md"),
    )
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--expected-rows", type=int, default=9)
    return parser.parse_args()


def is_blank(value: Any) -> bool:
    if value is None:
        return True
    s = str(value).strip()
    return s == "" or s.lower() in {"none", "nan", "na", "null"}


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def ready_bucket(row: dict[str, str]) -> str:
    return row.get("ready_bucket") or row.get("bucket") or ""


def index_by_manifest_id(rows: list[dict[str, str]], label: str) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for row in rows:
        mid = row.get("manifest_id", "").strip()
        if not mid:
            raise RuntimeError(f"{label}: row missing manifest_id")
        if mid in out:
            raise RuntimeError(f"{label}: duplicate manifest_id {mid}")
        out[mid] = row
    return out


def output_fields() -> list[str]:
    return [
        "manifest_id",
        "status_before",
        "status_after",
        "bucket_before",
        "bucket_after",
        "primary_source_path",
        "source_class",
        "case_id",
        "game_number",
        "move_count",
        "current_player",
        "target_rc",
        "target_action",
        "target_legal",
        "before_target_rank",
        "before_target_prob",
        "current_best_direct_rc",
        "current_best_direct_prob",
        "current_best_top_policy_rcs",
        "current_best_top_policy_probs",
        "board_hash",
        "probe_source",
        "excluded",
        "exclude_reason",
        "needs_current_best_probe_after",
        "needs_suppress_build_after",
        "notes",
    ]


def write_report(args: argparse.Namespace, out_rows: list[dict[str, str]], board_source_count: int) -> None:
    status_counts = Counter(r["status_after"] for r in out_rows)
    bucket_counts = Counter(r["bucket_after"] for r in out_rows)
    legal_rows = [r for r in out_rows if r["target_legal"] == "1"]
    illegal_rows = [r for r in out_rows if r["target_legal"] == "0"]

    lines = [
        "# Teacher-divergence legacy trainable current_best probe fill",
        "",
        "## Branch",
        "",
        "`exp/15x15-teacher-divergence-legacy-trainable-probe-fill`",
        "",
        "## Scope",
        "",
        "- Runs current_best policy probe only for 9 legacy trainable rows missing suppress schema fields.",
        "- Does not process round2 already-exportable rows.",
        "- Does not process protected top10 rows.",
        "- Does not process tail rank > 50 rows.",
        "- Does not process needs_rapfi_requery rows.",
        "- Does not process needs_board_join rows.",
        "- No training.",
        "- No checkpoint save.",
        "- No C export.",
        "- No public benchmark.",
        "- No promotion.",
        "",
        "## Inputs",
        "",
        f"- manifest: `{args.manifest}`",
        f"- normalization plan CSV: `{args.plan_csv}`",
        f"- checkpoint used for inference: `{args.checkpoint}`",
        f"- board source records indexed by hash: {board_source_count}",
        "",
        "## Summary",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| selected legacy rows | {len(out_rows)} |",
        f"| legal target rows | {len(legal_rows)} |",
        f"| illegal target rows | {len(illegal_rows)} |",
        "",
        "## Status after probe",
        "",
        "| status_after | rows |",
        "|---|---:|",
    ]

    for key, value in status_counts.most_common():
        lines.append(f"| {key} | {value} |")

    lines.extend([
        "",
        "## Bucket after probe",
        "",
        "| bucket_after | rows |",
        "|---|---:|",
    ])

    for key, value in bucket_counts.most_common():
        lines.append(f"| {key} | {value} |")

    lines.extend([
        "",
        "## Row preview",
        "",
        "| manifest_id | status_after | bucket_after | target_rc | rank | prob | direct_rc | excluded | notes |",
        "|---|---|---|---|---:|---:|---|---:|---|",
    ])

    for r in out_rows:
        rank = r["before_target_rank"] if r["before_target_rank"] else "NA"
        prob = r["before_target_prob"] if r["before_target_prob"] else "NA"
        lines.append(
            f"| {r['manifest_id']} | {r['status_after']} | {r['bucket_after']} | `{r['target_rc']}` | {rank} | {prob} | `{r['current_best_direct_rc']}` | {r['excluded']} | {r['notes']} |"
        )

    lines.extend([
        "",
        "## Decision",
        "",
        "Continue to suppress build only for legal rows from this CSV.",
        "",
        "No training.",
        "",
        "No checkpoint.",
        "",
        "No C export.",
        "",
        "No public benchmark.",
        "",
        "No promotion.",
        "",
    ])

    args.out_report.parent.mkdir(parents=True, exist_ok=True)
    args.out_report.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()

    _manifest_fields, manifest_rows = read_csv(args.manifest)
    _plan_fields, plan_rows = read_csv(args.plan_csv)

    if len(plan_rows) != args.expected_rows:
        raise RuntimeError(f"expected {args.expected_rows} plan rows, got {len(plan_rows)}")

    manifest_by_id = index_by_manifest_id(manifest_rows, "manifest")

    selected_rows: list[dict[str, str]] = []
    for plan_row in plan_rows:
        mid = plan_row["manifest_id"].strip()
        row = manifest_by_id.get(mid)
        if row is None:
            raise RuntimeError(f"plan manifest_id not found in manifest: {mid}")
        if not is_blank(row.get("duplicate_of")):
            raise RuntimeError(f"selected row is duplicate: {mid}")
        if row.get("status") != "ready_full_schema":
            raise RuntimeError(f"{mid}: expected ready_full_schema, got {row.get('status')}")
        if ready_bucket(row) != "trainable_rank_11_50":
            raise RuntimeError(f"{mid}: expected trainable_rank_11_50, got {ready_bucket(row)}")
        selected_rows.append(row)

    board_map = load_board_map(BOARD_SOURCE_PATHS)
    device = torch.device(args.device)
    model = load_model(args.checkpoint, device)

    out_rows: list[dict[str, str]] = []

    for row in selected_rows:
        mid = row.get("manifest_id", "")
        board_hash = row.get("board_hash", "").strip()
        target_rc = parse_rc(row.get("target_rc"))
        bucket_before = ready_bucket(row)

        base = {
            "manifest_id": mid,
            "status_before": row.get("status", ""),
            "bucket_before": bucket_before,
            "primary_source_path": row.get("primary_source_path", ""),
            "source_class": row.get("source_class", ""),
            "case_id": row.get("case_id", ""),
            "game_number": row.get("game_number", ""),
            "move_count": row.get("move_count", ""),
            "target_rc": json.dumps(target_rc) if target_rc is not None else "",
            "board_hash": board_hash,
        }

        if target_rc is None:
            out_rows.append({
                **base,
                "status_after": "skipped_invalid",
                "bucket_after": "unknown_rank",
                "current_player": row.get("current_player", ""),
                "target_action": "",
                "target_legal": "0",
                "before_target_rank": row.get("before_target_rank", ""),
                "before_target_prob": row.get("before_target_prob", ""),
                "current_best_direct_rc": "",
                "current_best_direct_prob": "",
                "current_best_top_policy_rcs": "[]",
                "current_best_top_policy_probs": "[]",
                "probe_source": "",
                "excluded": "1",
                "exclude_reason": "target_rc_parse_failed",
                "needs_current_best_probe_after": "0",
                "needs_suppress_build_after": "0",
                "notes": "excluded_target_invalid",
            })
            continue

        board_record = board_map.get(board_hash)
        if board_record is None:
            out_rows.append({
                **base,
                "status_after": "needs_board_repair",
                "bucket_after": "unknown_rank",
                "current_player": row.get("current_player", ""),
                "target_action": str(rc_to_action(target_rc)),
                "target_legal": "",
                "before_target_rank": row.get("before_target_rank", ""),
                "before_target_prob": row.get("before_target_prob", ""),
                "current_best_direct_rc": "",
                "current_best_direct_prob": "",
                "current_best_top_policy_rcs": "[]",
                "current_best_top_policy_probs": "[]",
                "probe_source": "",
                "excluded": "1",
                "exclude_reason": "board_hash_not_reconstructed",
                "needs_current_best_probe_after": "1",
                "needs_suppress_build_after": "0",
                "notes": "board_repair_needed",
            })
            continue

        board = board_record["board"]
        cp = parse_current_player(row.get("current_player"))
        if cp is None:
            cp = int(board_record["current_player"])

        probe = probe_board(
            model=model,
            board=board,
            current_player=cp,
            target_rc=target_rc,
            device=device,
            top_k=args.top_k,
        )

        target_legal = bool(probe["target_legal"])
        rank = probe["before_target_rank"]
        bucket_after = bucket_for_rank(rank, target_legal)

        if target_legal and rank is not None:
            status_after = "needs_suppress_build"
            excluded = "0"
            exclude_reason = ""
            needs_suppress_build_after = "1"
            notes = "legacy_rank_prob_refilled_but_suppress_missing"
        else:
            status_after = "skipped_invalid"
            excluded = "1"
            exclude_reason = "target_illegal"
            needs_suppress_build_after = "0"
            notes = "legacy_excluded_target_illegal"

        out_rows.append({
            **base,
            "status_after": status_after,
            "bucket_after": bucket_after,
            "current_player": str(cp),
            "target_action": str(probe["target_action"]),
            "target_legal": "1" if target_legal else "0",
            "before_target_rank": "" if rank is None else str(rank),
            "before_target_prob": str(probe["before_target_prob"]),
            "current_best_direct_rc": json.dumps(probe["current_best_direct_rc"]),
            "current_best_direct_prob": str(probe["current_best_direct_prob"]),
            "current_best_top_policy_rcs": json.dumps(probe["current_best_top_policy_rcs"]),
            "current_best_top_policy_probs": json.dumps(probe["current_best_top_policy_probs"]),
            "probe_source": board_record["source"],
            "excluded": excluded,
            "exclude_reason": exclude_reason,
            "needs_current_best_probe_after": "0",
            "needs_suppress_build_after": needs_suppress_build_after,
            "notes": notes,
        })

    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=output_fields(), lineterminator="\n")
        writer.writeheader()
        writer.writerows(out_rows)

    write_report(args, out_rows, len(board_map))

    print("selected_rows:", len(selected_rows))
    print("output_rows:", len(out_rows))
    print("status_after_counts:", json.dumps(dict(Counter(r["status_after"] for r in out_rows)), sort_keys=True))
    print("bucket_after_counts:", json.dumps(dict(Counter(r["bucket_after"] for r in out_rows)), sort_keys=True))
    print("out_csv:", args.out_csv)
    print("out_report:", args.out_report)
    print("no training; no checkpoint saved")


if __name__ == "__main__":
    main()
