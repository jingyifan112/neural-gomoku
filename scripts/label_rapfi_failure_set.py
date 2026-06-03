from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


LABELS: dict[tuple[int, int], tuple[str, str]] = {
    (
        1,
        38,
    ): (
        "pre_threat_setup_review",
        "no immediate win detected, but Rapfi soon creates forcing line; review open-four/double-threat setup",
    ),
    (
        1,
        44,
    ): (
        "value_miscalibration_and_direct_policy_missed_immediate_block",
        "opponent immediate win at 2,10; direct did not block; final blocked via MCTS/safety while value remained near neutral",
    ),
    (
        1,
        46,
    ): (
        "value_miscalibration_and_direct_policy_missed_immediate_block",
        "opponent immediate win at 4,12; direct did not block; final blocked via MCTS/safety while value remained near neutral",
    ),
    (
        1,
        48,
    ): (
        "forced_loss_or_double_threat",
        "opponent had two immediate winning moves 3,11 and 8,11; final blocked only one",
    ),
    (
        2,
        29,
    ): (
        "direct_policy_missed_immediate_block",
        "opponent immediate win at 4,9; direct did not block; final blocked via MCTS/safety; value was already strongly negative",
    ),
    (
        2,
        31,
    ): (
        "pre_double_threat_setup_review",
        "no immediate win detected, but next Rapfi bestline suggests transition into forcing line J8 J12",
    ),
    (
        2,
        33,
    ): (
        "forced_loss_or_double_threat",
        "opponent had two immediate winning moves 9,6 and 9,11; final blocked only one",
    ),
}


OUTPUT_FIELDS = [
    "game_number",
    "move_count",
    "side_to_move",
    "value",
    "direct",
    "policy_safety",
    "mcts_raw",
    "mcts_safety",
    "final",
    "previous_rapfi_bestline",
    "next_rapfi_bestline",
    "opponent_immediate_winning_moves",
    "final_blocks_immediate_win",
    "direct_blocks_immediate_win",
    "mcts_raw_blocks_immediate_win",
    "mcts_safety_blocks_immediate_win",
    "preliminary_failure_type",
    "failure_type",
    "notes",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Apply hand-review labels to the selected Rapfi failure set."
    )
    parser.add_argument("--failure-set-csv", type=Path, default=Path("analysis/rapfi_failure_set.csv"))
    parser.add_argument(
        "--threat-analysis-csv",
        type=Path,
        default=Path("analysis/rapfi_failure_threat_analysis.csv"),
    )
    parser.add_argument("--output-csv", type=Path, default=Path("analysis/rapfi_failure_set_labeled.csv"))
    parser.add_argument("--output-json", type=Path, default=Path("analysis/rapfi_failure_set_labeled.json"))
    parser.add_argument("--summary-md", type=Path, default=Path("analysis/rapfi_failure_label_summary.md"))
    return parser.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def key_for(row: dict[str, str]) -> tuple[int, int]:
    return int(row["game_number"]), int(row["move_count"])


def build_labeled_rows(
    failure_rows: list[dict[str, str]],
    threat_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    threats = {key_for(row): row for row in threat_rows}
    labeled_rows: list[dict[str, str]] = []
    missing_labels: list[tuple[int, int]] = []
    missing_threats: list[tuple[int, int]] = []

    for failure_row in failure_rows:
        key = key_for(failure_row)
        label = LABELS.get(key)
        threat_row = threats.get(key)
        if label is None:
            missing_labels.append(key)
            continue
        if threat_row is None:
            missing_threats.append(key)
            continue

        failure_type, notes = label
        labeled_rows.append(
            {
                "game_number": failure_row["game_number"],
                "move_count": failure_row["move_count"],
                "side_to_move": failure_row["side_to_move"],
                "value": failure_row["value"],
                "direct": failure_row["direct"],
                "policy_safety": failure_row["policy_safety"],
                "mcts_raw": failure_row["mcts_raw"],
                "mcts_safety": failure_row["mcts_safety"],
                "final": failure_row["final"],
                "previous_rapfi_bestline": failure_row["previous_rapfi_bestline"],
                "next_rapfi_bestline": failure_row["next_rapfi_bestline"],
                "opponent_immediate_winning_moves": threat_row["opponent_immediate_winning_moves"],
                "final_blocks_immediate_win": threat_row["final_blocks_immediate_win"],
                "direct_blocks_immediate_win": threat_row["direct_blocks_immediate_win"],
                "mcts_raw_blocks_immediate_win": threat_row["mcts_raw_blocks_immediate_win"],
                "mcts_safety_blocks_immediate_win": threat_row["mcts_safety_blocks_immediate_win"],
                "preliminary_failure_type": threat_row["preliminary_failure_type"],
                "failure_type": failure_type,
                "notes": notes,
            }
        )

    if missing_labels:
        raise ValueError(f"missing hand labels for: {format_keys(missing_labels)}")
    if missing_threats:
        raise ValueError(f"missing threat rows for: {format_keys(missing_threats)}")

    return labeled_rows


def format_keys(keys: list[tuple[int, int]]) -> str:
    return ", ".join(f"{game}:{move}" for game, move in keys)


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(rows, handle, indent=2)
        handle.write("\n")


def write_summary(path: Path, rows: list[dict[str, str]]) -> None:
    counts = Counter(row["failure_type"] for row in rows)
    lines = ["# Rapfi failure label summary", ""]
    lines.append(f"Total labeled positions: {len(rows)}")
    lines.append("")
    lines.append("## Label counts")
    lines.append("")
    for label, count in sorted(counts.items()):
        lines.append(f"- {label}: {count}")
    lines.append("")
    lines.append("## Labeled positions")
    lines.append("")
    for row in rows:
        lines.extend(
            [
                f"### Game {row['game_number']} move_count {row['move_count']}",
                "",
                f"- failure_type: {row['failure_type']}",
                f"- notes: {row['notes']}",
                f"- opponent_immediate_winning_moves: {row['opponent_immediate_winning_moves'] or '(none)'}",
                f"- preliminary_failure_type: {row['preliminary_failure_type']}",
                "",
            ]
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    args = parse_args()
    failure_rows = read_csv(args.failure_set_csv)
    threat_rows = read_csv(args.threat_analysis_csv)
    labeled_rows = build_labeled_rows(failure_rows, threat_rows)

    write_csv(args.output_csv, labeled_rows)
    write_json(args.output_json, labeled_rows)
    write_summary(args.summary_md, labeled_rows)

    print(f"read {args.failure_set_csv}")
    print(f"read {args.threat_analysis_csv}")
    print(f"labeled positions: {len(labeled_rows)}")
    print(f"wrote {args.output_csv}")
    print(f"wrote {args.output_json}")
    print(f"wrote {args.summary_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
