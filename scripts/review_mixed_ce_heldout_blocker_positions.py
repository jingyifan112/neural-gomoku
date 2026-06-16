#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

BLOCKERS = [
    "holdout_b_mcts16_g2_m19_target_10_7_over_7_11",
    "holdout_candidate_d_g2_m15_white_last_8_9_target_live_direct_7_10_over_live_final_8_8",
    "holdout_candidate_d_g2_m15_white_last_8_9_target_safe_10_7_over_live_final_8_8",
    "holdout_candidate_e_g2_m13_white_target_5_8_over_8_8",
    "holdout_candidate_e_g2_m17_white_last_9_9_target_block_right_10_9_over_live_final_9_10",
    "holdout_candidate_e_g2_m17_white_last_9_9_target_future_block_8_10_over_live_final_9_10",
]

VARIANTS = [
    (
        "w010",
        "0.10",
        Path("analysis/integration_eval/teacher_divergence_policy_mixed_ce_anchor_probe_gated_eval.csv"),
    ),
    (
        "w005",
        "0.05",
        Path("analysis/integration_eval/teacher_divergence_policy_mixed_ce_anchor_probe_w005_gated_eval.csv"),
    ),
    (
        "w0025",
        "0.025",
        Path("analysis/integration_eval/teacher_divergence_policy_mixed_ce_anchor_probe_w0025_gated_eval.csv"),
    ),
]

DATASET = Path("analysis/integration_eval/teacher_divergence_retention_safety_v3_dataset.json")
MANIFEST = Path("analysis/integration_eval/teacher_divergence_retention_manifest.csv")
PROBE = Path("analysis/integration_eval/teacher_divergence_retention_probe.csv")
AUDIT_SUMMARY = Path("analysis/integration_eval/teacher_divergence_policy_mixed_ce_heldout_regression_audit_summary.csv")

OUT_DETAIL = Path("analysis/integration_eval/teacher_divergence_policy_mixed_ce_heldout_blocker_position_review.csv")
OUT_REPORT = Path("analysis/integration_eval/teacher_divergence_policy_mixed_ce_heldout_blocker_position_review.md")


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


def read_eval(path: Path) -> dict[str, dict[str, dict[str, str]]]:
    out: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("id") in BLOCKERS:
                out[row["id"]][row["phase"]] = row
    return dict(out)


def board_to_ascii(board: list[list[int]], target: str) -> str:
    target_xy: tuple[int, int] | None = None
    if target and "," in target:
        x, y = [int(v) for v in target.split(",")]
        target_xy = (x, y)

    chars = {0: ".", 1: "X", -1: "O", 2: "X", -2: "O"}
    lines: list[str] = []
    for y, row in enumerate(board):
        cells: list[str] = []
        for x, val in enumerate(row):
            if target_xy == (x, y):
                cells.append("*")
            else:
                cells.append(chars.get(int(val), "?"))
        lines.append(f"{y:02d} " + " ".join(cells))
    header = "   " + " ".join(f"{x % 10}" for x in range(len(board[0])))
    return header + "\n" + "\n".join(lines)


def get_nested(d: dict[str, Any], key: str) -> Any:
    md = d.get("metadata")
    if isinstance(md, dict):
        return md.get(key, "")
    return ""


def main() -> None:
    dataset_rows = read_json_rows(DATASET)
    by_id = {r["id"]: r for r in dataset_rows if r.get("id") in BLOCKERS}

    missing = [x for x in BLOCKERS if x not in by_id]
    if missing:
        raise ValueError(f"missing blocker rows from dataset: {missing}")

    manifest_by_dataset_id = read_csv_by_key(MANIFEST, "dataset_id")
    probe_by_id = read_csv_by_key(PROBE, "id")
    audit_by_id = read_csv_by_key(AUDIT_SUMMARY, "id")
    evals = {variant: (scale, read_eval(path)) for variant, scale, path in VARIANTS}

    detail_rows: list[dict[str, Any]] = []

    for row_id in BLOCKERS:
        r = by_id[row_id]
        source_id = r.get("source_id", "")
        manifest_row = manifest_by_dataset_id.get(row_id, {})
        probe_row = probe_by_id.get(row_id, {})
        audit_row = audit_by_id.get(row_id, {})

        base = {
            "id": row_id,
            "source_id": source_id,
            "source_path": r.get("source_path", ""),
            "game_number": r.get("game_number", ""),
            "move_count": r.get("move_count", ""),
            "side_to_move": r.get("side_to_move", ""),
            "policy_target": r.get("policy_target", ""),
            "teacher_move": r.get("teacher_move", ""),
            "bucket": r.get("bucket", ""),
            "label_type": r.get("label_type", ""),
            "board_digest": get_nested(r, "board_digest") or manifest_row.get("board_digest", ""),
            "current_best_direct_move": get_nested(r, "current_best_direct_move")
            or manifest_row.get("current_best_direct_move", ""),
            "current_best_matches_teacher": get_nested(r, "current_best_matches_teacher")
            or manifest_row.get("current_best_matches_teacher", ""),
            "labeled_failure_type": get_nested(r, "labeled_failure_type")
            or manifest_row.get("labeled_failure_type", ""),
            "teacher_eval_before": get_nested(r, "teacher_eval_before"),
            "teacher_eval_kind": get_nested(r, "teacher_eval_kind"),
            "teacher_pv_before": get_nested(r, "teacher_pv_before"),
            "teacher_query_status": get_nested(r, "teacher_query_status"),
            "manifest_notes": manifest_row.get("notes", ""),
            "manifest_bucket": manifest_row.get("bucket", ""),
            "probe_reason": probe_row.get("reason", ""),
            "audit_rank_delta_by_scale": audit_row.get("rank_delta_by_scale", ""),
            "audit_prob_delta_by_scale": audit_row.get("prob_delta_by_scale", ""),
            "audit_top_match_by_scale": audit_row.get("top_match_by_scale", ""),
        }

        for variant, (scale, data) in evals.items():
            before = data.get(row_id, {}).get("before", {})
            after = data.get(row_id, {}).get("after", {})
            if before and after:
                base[f"{variant}_scale"] = scale
                base[f"{variant}_before_rank"] = before.get("target_rank", "")
                base[f"{variant}_after_rank"] = after.get("target_rank", "")
                base[f"{variant}_before_prob"] = before.get("target_prob", "")
                base[f"{variant}_after_prob"] = after.get("target_prob", "")
                base[f"{variant}_before_top"] = before.get("top_move", "")
                base[f"{variant}_after_top"] = after.get("top_move", "")
                base[f"{variant}_before_top_prob"] = before.get("top_prob", "")
                base[f"{variant}_after_top_prob"] = after.get("top_prob", "")
                base[f"{variant}_before_top_match"] = before.get("top_matches_target", "")
                base[f"{variant}_after_top_match"] = after.get("top_matches_target", "")

        detail_rows.append(base)

    OUT_DETAIL.parent.mkdir(parents=True, exist_ok=True)
    with OUT_DETAIL.open("w", newline="") as f:
        fields = list(detail_rows[0].keys())
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(detail_rows)

    lines: list[str] = []
    lines.append("# Mixed-CE heldout blocker position review")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append("- read-only review of six repeated heldout blockers")
    lines.append("- no training")
    lines.append("- no checkpoint")
    lines.append("- no C export")
    lines.append("- no benchmark")
    lines.append("- no promotion")
    lines.append("")
    lines.append("## Executive summary")
    lines.append("")
    lines.append("The six repeated blockers cluster into three source families:")
    lines.append("")
    lines.append("- candidate C / B mcts16 game2 move19 retention target: `10,7`")
    lines.append("- candidate D game2 move15 fork-prevention retention targets: `7,10` and `10,7`")
    lines.append("- candidate E game2 move13/move17 retention targets: `5,8`, `10,9`, and `8,10`")
    lines.append("")
    lines.append("All six are heldout `policy_target` rows. Filtering only by label_type is therefore not enough.")
    lines.append("")
    lines.append("## Blocker table")
    lines.append("")
    lines.append(
        "| id | game/move | target | source_path | reason/bucket | rank delta by scale | prob delta by scale |"
    )
    lines.append("|---|---:|---|---|---|---|---|")
    for r in detail_rows:
        lines.append(
            f"| `{r['id']}` | {r['game_number']}/{r['move_count']} | `{r['policy_target']}` | "
            f"`{r['source_path']}` | {r['bucket']} | "
            f"`{r['audit_rank_delta_by_scale']}` | `{r['audit_prob_delta_by_scale']}` |"
        )

    lines.append("")
    lines.append("## Per-position details")
    lines.append("")
    for r in detail_rows:
        lines.append(f"### `{r['id']}`")
        lines.append("")
        lines.append(f"- source_id: `{r['source_id']}`")
        lines.append(f"- source_path: `{r['source_path']}`")
        lines.append(f"- game/move: {r['game_number']} / {r['move_count']}")
        lines.append(f"- side_to_move: `{r['side_to_move']}`")
        lines.append(f"- target: `{r['policy_target']}`")
        lines.append(f"- teacher_move: `{r['teacher_move']}`")
        lines.append(f"- current_best_direct_move: `{r['current_best_direct_move']}`")
        lines.append(f"- current_best_matches_teacher: `{r['current_best_matches_teacher']}`")
        lines.append(f"- board_digest: `{r['board_digest']}`")
        lines.append(f"- bucket: {r['bucket']}")
        if r["manifest_notes"]:
            lines.append(f"- manifest_notes: {r['manifest_notes']}")
        if r["probe_reason"]:
            lines.append(f"- probe_reason: {r['probe_reason']}")
        if r["teacher_eval_before"]:
            lines.append(f"- teacher_eval_before: `{r['teacher_eval_before']}`")
        if r["teacher_pv_before"]:
            lines.append(f"- teacher_pv_before: `{r['teacher_pv_before']}`")
        lines.append("")
        lines.append("| scale | rank before->after | prob before->after | top before->after | top_match before->after |")
        lines.append("|---:|---:|---:|---|---|")
        for variant in ["w010", "w005", "w0025"]:
            lines.append(
                f"| {r.get(variant + '_scale', '')} | "
                f"{r.get(variant + '_before_rank', '')}->{r.get(variant + '_after_rank', '')} | "
                f"{r.get(variant + '_before_prob', '')}->{r.get(variant + '_after_prob', '')} | "
                f"`{r.get(variant + '_before_top', '')}`->`{r.get(variant + '_after_top', '')}` | "
                f"{r.get(variant + '_before_top_match', '')}->{r.get(variant + '_after_top_match', '')} |"
            )
        board = by_id[r["id"]].get("board")
        if isinstance(board, list) and board:
            lines.append("")
            lines.append("Board view (`*` marks target; `X/O` are stones as encoded by dataset):")
            lines.append("")
            lines.append("```text")
            lines.append(board_to_ascii(board, r["policy_target"]))
            lines.append("```")
        lines.append("")

    lines.append("## Interpretation")
    lines.append("")
    lines.append("These blockers are not a single label-type problem. They are concentrated in a few tactical-retention families.")
    lines.append("")
    lines.append("The candidate D move15 rows are especially important because one nearby heldout row gained top-1 under all mixed-CE scales, while two sibling targets regressed. This suggests a local target conflict rather than a global inability to retain the position family.")
    lines.append("")
    lines.append("The candidate E move17 rows have extremely low target probability. One row improves rank while still losing probability, so row-level probability gates are catching a real mass-allocation issue that rank-only metrics would miss.")
    lines.append("")
    lines.append("## Recommendation")
    lines.append("")
    lines.append("Do not train another global mixed-CE scale variant yet.")
    lines.append("")
    lines.append("Next useful experiment should either:")
    lines.append("")
    lines.append("- separate conflicting sibling targets from the same board family, or")
    lines.append("- add explicit retention anchors for these blocker families outside the heldout split, or")
    lines.append("- make mixed-CE selection conditional on source family instead of label_type alone.")
    lines.append("")
    lines.append("Any such variant must still run through the regression-gated runner before saving a checkpoint.")

    OUT_REPORT.write_text("\n".join(lines) + "\n")

    print(f"wrote detail csv: {OUT_DETAIL}")
    print(f"wrote report: {OUT_REPORT}")
    print("")
    print("blockers reviewed:", len(detail_rows))
    by_source = defaultdict(int)
    for r in detail_rows:
        by_source[r["source_path"]] += 1
    print("source_path counts:")
    for k, v in sorted(by_source.items()):
        print(v, k)


if __name__ == "__main__":
    main()
