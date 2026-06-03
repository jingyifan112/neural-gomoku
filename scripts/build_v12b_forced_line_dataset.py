from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


OLD_SINGLE_BLOCKS = {("1", "44"), ("1", "46"), ("2", "29")}
OLD_DOUBLE_THREATS = {("1", "48"), ("2", "33")}
NEW_EARLY_FORCING = {
    ("1", "12"): -0.5,
    ("1", "14"): -0.5,
    ("1", "16"): -0.7,
    ("1", "18"): -0.7,
}
NEW_PRE_DOUBLE = {("2", "31"): -0.75}
NEW_DOUBLE_THREATS = {("2", "33")}

OUTPUT_FIELDS = [
    "id",
    "board_size",
    "side_to_move",
    "board",
    "source",
    "move_count",
    "label_type",
    "value_target",
    "policy_target",
    "notes",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build the explicit v12b forced-line repair dataset from existing Rapfi failure artifacts."
    )
    parser.add_argument("--old-snapshots-json", type=Path, default=Path("analysis/rapfi_failure_board_snapshots.json"))
    parser.add_argument("--old-threat-csv", type=Path, default=Path("analysis/rapfi_failure_threat_analysis.csv"))
    parser.add_argument("--old-labeled-csv", type=Path, default=Path("analysis/rapfi_failure_set_labeled.csv"))
    parser.add_argument(
        "--new-snapshots-json",
        type=Path,
        default=Path("analysis/v12_candidate_failure_board_snapshots.json"),
    )
    parser.add_argument(
        "--new-threat-csv",
        type=Path,
        default=Path("analysis/v12_candidate_failure_threat_analysis.csv"),
    )
    parser.add_argument("--output-json", type=Path, default=Path("analysis/v12b_forced_line_repair_dataset.json"))
    parser.add_argument("--output-csv", type=Path, default=Path("analysis/v12b_forced_line_repair_dataset.csv"))
    parser.add_argument("--board-size", type=int, default=15)
    return parser.parse_args()


def read_json(path: Path) -> list[dict[str, object]]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a JSON list")
    return data


def read_csv_index(path: Path) -> dict[tuple[str, str], dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return {(row["game_number"], row["move_count"]): row for row in rows}


def snapshot_index(rows: list[dict[str, object]]) -> dict[tuple[str, str], dict[str, object]]:
    return {(str(row["game_number"]), str(row["move_count"])): row for row in rows}


def parse_move_list(raw: str) -> list[str]:
    return [part.strip() for part in raw.split() if part.strip()]


def board_text(snapshot: str, board_size: int) -> str:
    board_rows: list[str] = []
    for line in snapshot.splitlines():
        tokens = line.strip().split()
        if len(tokens) == board_size and all(token in {".", "X", "O"} for token in tokens):
            board_rows.append(" ".join(tokens))
    if len(board_rows) != board_size:
        raise ValueError(f"expected {board_size} board rows, found {len(board_rows)}")
    return "\n".join(board_rows)


def make_row(
    *,
    row_id: str,
    board_size: int,
    snapshot: dict[str, object],
    source: str,
    label_type: str,
    value_target: float | None,
    policy_target: str,
    notes: str,
) -> dict[str, object]:
    return {
        "id": row_id,
        "board_size": board_size,
        "side_to_move": str(snapshot["side_to_move"]),
        "board": board_text(str(snapshot["board_snapshot_before_decision"]), board_size),
        "source": source,
        "move_count": str(snapshot["move_count"]),
        "label_type": label_type,
        "value_target": "" if value_target is None else value_target,
        "policy_target": policy_target,
        "notes": notes,
    }


def add_old_rows(args: argparse.Namespace, rows: list[dict[str, object]]) -> None:
    snapshots = snapshot_index(read_json(args.old_snapshots_json))
    threats = read_csv_index(args.old_threat_csv)
    labels = read_csv_index(args.old_labeled_csv)

    for key in sorted(OLD_SINGLE_BLOCKS | OLD_DOUBLE_THREATS):
        snapshot = snapshots[key]
        threat = threats[key]
        label = labels[key]
        opponent_wins = parse_move_list(threat.get("opponent_immediate_winning_moves", ""))
        policy_target = opponent_wins[0] if opponent_wins else ""

        if key in OLD_SINGLE_BLOCKS:
            label_type = "old_immediate_block_regression"
            value_target = -1.0 if "value_miscalibration" in label["failure_type"] else None
            notes = f"preserve original v12 direct-block repair; {label['notes']}"
        else:
            label_type = "verified_double_threat_loss"
            value_target = -1.0
            policy_target = ""
            notes = f"verified old double-threat loss; {label['notes']}"

        rows.append(
            make_row(
                row_id=f"old_g{key[0]}_m{key[1]}",
                board_size=args.board_size,
                snapshot=snapshot,
                source="v11_labeled_rapfi_failure_set",
                label_type=label_type,
                value_target=value_target,
                policy_target=policy_target,
                notes=notes,
            )
        )


def add_new_rows(args: argparse.Namespace, rows: list[dict[str, object]]) -> None:
    snapshots = snapshot_index(read_json(args.new_snapshots_json))
    threats = read_csv_index(args.new_threat_csv)

    for key, value_target in sorted(NEW_EARLY_FORCING.items()):
        snapshot = snapshots[key]
        rows.append(
            make_row(
                row_id=f"v12_g{key[0]}_m{key[1]}",
                board_size=args.board_size,
                snapshot=snapshot,
                source="v12_candidate_rapfi_forcing_line",
                label_type="early_forcing_value_negative",
                value_target=value_target,
                policy_target="",
                notes="value-focused early forcing-line repair; no policy target without manual safer-move audit",
            )
        )

    for key, value_target in sorted(NEW_PRE_DOUBLE.items()):
        snapshot = snapshots[key]
        rows.append(
            make_row(
                row_id=f"v12_g{key[0]}_m{key[1]}",
                board_size=args.board_size,
                snapshot=snapshot,
                source="v12_candidate_rapfi_pre_double_threat",
                label_type="pre_double_threat_warning",
                value_target=value_target,
                policy_target="",
                notes="moderate negative value for pre-double-threat warning; no policy target without audit",
            )
        )

    for key in sorted(NEW_DOUBLE_THREATS):
        snapshot = snapshots[key]
        threat = threats[key]
        opponent_wins = parse_move_list(threat.get("opponent_immediate_winning_moves", ""))
        rows.append(
            make_row(
                row_id=f"v12_g{key[0]}_m{key[1]}",
                board_size=args.board_size,
                snapshot=snapshot,
                source="v12_candidate_rapfi_double_threat",
                label_type="verified_double_threat_loss",
                value_target=-1.0,
                policy_target="",
                notes="verified v12 double-threat loss; value-only sample because blocking one listed win may still lose",
            )
        )


def write_json(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(rows, handle, indent=2)
        handle.write("\n")


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    args = parse_args()
    rows: list[dict[str, object]] = []
    add_old_rows(args, rows)
    add_new_rows(args, rows)
    write_json(args.output_json, rows)
    write_csv(args.output_csv, rows)
    print(f"dataset rows: {len(rows)}")
    print(f"wrote {args.output_json}")
    print(f"wrote {args.output_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
