#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

DATASET = Path("analysis/integration_eval/teacher_divergence_retention_safety_v3_dataset.json")
MANIFEST = Path("analysis/integration_eval/teacher_divergence_retention_manifest.csv")
AUDIT_SUMMARY = Path("analysis/integration_eval/teacher_divergence_policy_mixed_ce_heldout_regression_audit_summary.csv")
BLOCKER_REVIEW = Path("analysis/integration_eval/teacher_divergence_policy_mixed_ce_heldout_blocker_position_review.csv")

OUT_ROWS = Path("analysis/integration_eval/teacher_divergence_retention_family_split_design_rows.csv")
OUT_FAMILIES = Path("analysis/integration_eval/teacher_divergence_retention_family_split_design_families.csv")
OUT_REPORT = Path("analysis/integration_eval/teacher_divergence_retention_family_split_design_report.md")


def read_json_rows(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text())
    if isinstance(data, dict):
        rows = data.get("rows")
        if not isinstance(rows, list):
            raise ValueError(f"{path} has no list rows")
        return rows
    if isinstance(data, list):
        return data
    raise ValueError(f"unexpected json root in {path}: {type(data).__name__}")


def read_csv_by_key(path: Path, key: str) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    if not path.exists():
        return out
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            val = row.get(key, "")
            if val:
                out[val] = row
    return out


def get_board_digest(row: dict[str, Any], manifest_row: dict[str, str]) -> str:
    md = row.get("metadata")
    if isinstance(md, dict) and md.get("board_digest"):
        return str(md["board_digest"])
    if manifest_row.get("board_digest"):
        return manifest_row["board_digest"]
    return ""


def family_id_for(row: dict[str, Any], board_digest: str) -> str:
    source_path = row.get("source_path", "unknown")
    game = row.get("game_number", "na")
    move = row.get("move_count", "na")
    side = row.get("side_to_move", "na")
    if board_digest:
        return f"bd:{board_digest}"
    return f"fallback:{source_path}:g{game}:m{move}:{side}"


def as_int(x: str) -> int:
    if x == "" or x is None:
        return 0
    return int(float(x))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"no rows to write: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0].keys())
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    dataset_rows = read_json_rows(DATASET)
    manifest_by_id = read_csv_by_key(MANIFEST, "dataset_id")
    audit_by_id = read_csv_by_key(AUDIT_SUMMARY, "id")
    blocker_review_by_id = read_csv_by_key(BLOCKER_REVIEW, "id")

    heldout_rows = [
        r for r in dataset_rows
        if r.get("split") == "heldout_retention" or r.get("heldout") is True
    ]

    row_records: list[dict[str, Any]] = []

    for row in heldout_rows:
        row_id = row.get("id", "")
        manifest_row = manifest_by_id.get(row_id, {})
        audit_row = audit_by_id.get(row_id, {})
        blocker_review = blocker_review_by_id.get(row_id, {})

        board_digest = get_board_digest(row, manifest_row)
        family_id = family_id_for(row, board_digest)

        source_path = row.get("source_path", "")
        source_id = row.get("source_id", "")
        target = row.get("policy_target") or row.get("teacher_move") or ""
        game = row.get("game_number", "")
        move = row.get("move_count", "")
        side = row.get("side_to_move", "")

        variant_count = as_int(audit_row.get("variant_count", "0"))
        rank_regress = as_int(audit_row.get("rank_regression_count", "0"))
        prob_regress = as_int(audit_row.get("prob_regression_count", "0"))
        rank_improve = as_int(audit_row.get("rank_improvement_count", "0"))
        prob_improve = as_int(audit_row.get("prob_improvement_count", "0"))
        top_gain = as_int(audit_row.get("top_match_gained_count", "0"))

        is_repeated_blocker = audit_row.get("regressed_rank_or_prob_all_variants") == "True"
        is_prob_only_or_rank_improve_prob_regress = (
            variant_count > 0
            and prob_regress == variant_count
            and rank_regress < variant_count
        )
        is_stable_top1_gain = top_gain == variant_count and variant_count > 0

        row_records.append(
            {
                "family_id": family_id,
                "id": row_id,
                "source_id": source_id,
                "source_path": source_path,
                "game_number": game,
                "move_count": move,
                "side_to_move": side,
                "board_digest": board_digest,
                "policy_target": target,
                "teacher_move": row.get("teacher_move", ""),
                "label_type": row.get("label_type", ""),
                "role": row.get("role", ""),
                "bucket": row.get("bucket", "") or manifest_row.get("bucket", ""),
                "manifest_notes": manifest_row.get("notes", ""),
                "variant_count": variant_count,
                "rank_regression_count": rank_regress,
                "prob_regression_count": prob_regress,
                "rank_improvement_count": rank_improve,
                "prob_improvement_count": prob_improve,
                "top_match_gained_count": top_gain,
                "is_repeated_blocker": is_repeated_blocker,
                "is_prob_only_or_rank_improve_prob_regress": is_prob_only_or_rank_improve_prob_regress,
                "is_stable_top1_gain": is_stable_top1_gain,
                "rank_delta_by_scale": audit_row.get("rank_delta_by_scale", ""),
                "prob_delta_by_scale": audit_row.get("prob_delta_by_scale", ""),
                "top_match_by_scale": audit_row.get("top_match_by_scale", ""),
                "reviewed_as_blocker": bool(blocker_review),
            }
        )

    by_family: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for rec in row_records:
        by_family[rec["family_id"]].append(rec)

    family_records: list[dict[str, Any]] = []

    for family_id, rows in sorted(by_family.items()):
        rows_sorted = sorted(rows, key=lambda r: (str(r["game_number"]), str(r["move_count"]), r["id"]))
        targets = sorted({str(r["policy_target"]) for r in rows_sorted if r["policy_target"]})
        source_paths = sorted({str(r["source_path"]) for r in rows_sorted if r["source_path"]})
        game_moves = sorted({f"g{r['game_number']}_m{r['move_count']}" for r in rows_sorted})
        blocker_count = sum(bool(r["is_repeated_blocker"]) for r in rows_sorted)
        prob_mass_loss_count = sum(bool(r["is_prob_only_or_rank_improve_prob_regress"]) for r in rows_sorted)
        stable_gain_count = sum(bool(r["is_stable_top1_gain"]) for r in rows_sorted)

        sibling_target_conflict = len(targets) >= 2 and blocker_count > 0
        has_mixed_signal_conflict = blocker_count > 0 and stable_gain_count > 0

        if has_mixed_signal_conflict:
            recommendation = "split_sibling_targets_and_add_nonheldout_retention_anchor"
        elif sibling_target_conflict:
            recommendation = "split_sibling_targets_by_board_family"
        elif prob_mass_loss_count > 0:
            recommendation = "keep_probability_gate_and_review_low_prob_future_block"
        elif blocker_count > 0:
            recommendation = "add_family_specific_retention_anchor_or_exclude_from_mixed_ce"
        else:
            recommendation = "ordinary_heldout_family"

        family_records.append(
            {
                "family_id": family_id,
                "row_count": len(rows_sorted),
                "targets": ";".join(targets),
                "target_count": len(targets),
                "source_paths": ";".join(source_paths),
                "game_moves": ";".join(game_moves),
                "repeated_blocker_count": blocker_count,
                "prob_mass_loss_count": prob_mass_loss_count,
                "stable_top1_gain_count": stable_gain_count,
                "sibling_target_conflict": sibling_target_conflict,
                "mixed_signal_conflict": has_mixed_signal_conflict,
                "recommendation": recommendation,
                "row_ids": ";".join(r["id"] for r in rows_sorted),
            }
        )

    family_records.sort(
        key=lambda r: (
            -int(r["repeated_blocker_count"]),
            -int(r["mixed_signal_conflict"]),
            -int(r["sibling_target_conflict"]),
            -int(r["prob_mass_loss_count"]),
            r["family_id"],
        )
    )

    row_records.sort(
        key=lambda r: (
            r["family_id"],
            -int(r["is_repeated_blocker"]),
            r["id"],
        )
    )

    write_csv(OUT_ROWS, row_records)
    write_csv(OUT_FAMILIES, family_records)

    lines: list[str] = []
    lines.append("# Retention family split design")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append("- read-only split-design audit over heldout retention families")
    lines.append("- no training")
    lines.append("- no checkpoint")
    lines.append("- no C export")
    lines.append("- no benchmark")
    lines.append("- no promotion")
    lines.append("")
    lines.append("## Outputs")
    lines.append("")
    lines.append(f"- row detail: `{OUT_ROWS}`")
    lines.append(f"- family summary: `{OUT_FAMILIES}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- heldout rows reviewed: {len(row_records)}")
    lines.append(f"- heldout families: {len(family_records)}")
    lines.append(f"- families with repeated blockers: {sum(int(r['repeated_blocker_count']) > 0 for r in family_records)}")
    lines.append(f"- families with sibling target conflict: {sum(bool(r['sibling_target_conflict']) for r in family_records)}")
    lines.append(f"- families with mixed signal conflict: {sum(bool(r['mixed_signal_conflict']) for r in family_records)}")
    lines.append("")
    lines.append("## High-priority families")
    lines.append("")
    lines.append("| family | rows | targets | blockers | prob-mass-loss | stable top1 gains | recommendation |")
    lines.append("|---|---:|---|---:|---:|---:|---|")
    for fam in family_records:
        if int(fam["repeated_blocker_count"]) == 0 and not bool(fam["mixed_signal_conflict"]):
            continue
        lines.append(
            f"| `{fam['family_id']}` | {fam['row_count']} | `{fam['targets']}` | "
            f"{fam['repeated_blocker_count']} | {fam['prob_mass_loss_count']} | "
            f"{fam['stable_top1_gain_count']} | `{fam['recommendation']}` |"
        )

    lines.append("")
    lines.append("## High-priority row details")
    lines.append("")
    for fam in family_records:
        if int(fam["repeated_blocker_count"]) == 0 and not bool(fam["mixed_signal_conflict"]):
            continue
        lines.append(f"### `{fam['family_id']}`")
        lines.append("")
        lines.append(f"- targets: `{fam['targets']}`")
        lines.append(f"- source_paths: `{fam['source_paths']}`")
        lines.append(f"- game_moves: `{fam['game_moves']}`")
        lines.append(f"- recommendation: `{fam['recommendation']}`")
        lines.append("")
        lines.append("| id | target | blocker | prob-mass-loss | stable top1 gain | rank delta | prob delta | top match |")
        lines.append("|---|---|---:|---:|---:|---|---|---|")
        for row in row_records:
            if row["family_id"] != fam["family_id"]:
                continue
            lines.append(
                f"| `{row['id']}` | `{row['policy_target']}` | {row['is_repeated_blocker']} | "
                f"{row['is_prob_only_or_rank_improve_prob_regress']} | {row['is_stable_top1_gain']} | "
                f"`{row['rank_delta_by_scale']}` | `{row['prob_delta_by_scale']}` | `{row['top_match_by_scale']}` |"
            )
        lines.append("")

    lines.append("## Proposed split rules")
    lines.append("")
    lines.append("1. Do not use a sibling target from the same board digest as the only heldout check while training another sibling target in mixed CE.")
    lines.append("2. For board families with repeated blockers, create a small non-heldout retention-anchor subset and keep a separate family-level heldout subset.")
    lines.append("3. Preserve probability regression gates; rank-only gates miss low-probability future-block mass loss.")
    lines.append("4. Condition mixed-CE row selection by board family/source family, not by label_type alone.")
    lines.append("5. Any future training variant must use the regression-gated runner and must not save unless gates pass.")
    lines.append("")
    lines.append("## Decision")
    lines.append("")
    lines.append("This branch should remain a design/audit branch. It should not promote any model artifact.")

    OUT_REPORT.write_text("\n".join(lines) + "\n")

    print(f"wrote rows: {OUT_ROWS}")
    print(f"wrote families: {OUT_FAMILIES}")
    print(f"wrote report: {OUT_REPORT}")
    print("")
    print("high priority families:")
    for fam in family_records:
        if int(fam["repeated_blocker_count"]) > 0 or bool(fam["mixed_signal_conflict"]):
            print(
                fam["family_id"],
                "rows=",
                fam["row_count"],
                "targets=",
                fam["targets"],
                "blockers=",
                fam["repeated_blocker_count"],
                "recommendation=",
                fam["recommendation"],
            )


if __name__ == "__main__":
    main()
