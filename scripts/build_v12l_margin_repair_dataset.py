from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


BOARD_SIZE = 15

# Coordinates here are from live/C/Rapfi logs: x,y = col,row.
# The neural model uses row,col internally, so we convert xy -> rc.
MARGIN_CASES = [
    {
        "case_id": "v12l_g2_m13_target_8_6_over_9_4",
        "game_number": "2",
        "move_count": "13",
        "target_xy": [8, 6],
        "suppress_xy": [9, 4],
        "source": "v12i_failure_board_snapshots",
        "reason": "CE-only v12k raised target rank/prob but live C final stayed 9,4",
    },
    {
        "case_id": "v12l_g2_m15_target_8_6_over_6_6",
        "game_number": "2",
        "move_count": "15",
        "target_xy": [8, 6],
        "suppress_xy": [6, 6],
        "source": "v12i_failure_board_snapshots",
        "reason": "CE-only v12k raised target rank/prob but live C final stayed 6,6",
    },
]


def xy_to_rc(xy: list[int]) -> list[int]:
    x, y = xy
    return [y, x]


def parse_board_snapshot(snapshot: str) -> list[list[int]]:
    rows: list[list[int]] = []

    for raw_line in snapshot.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if set(line) <= {"-"}:
            continue

        tokens = line.split()
        if len(tokens) != BOARD_SIZE:
            continue
        if not all(tok in {".", "X", "O"} for tok in tokens):
            continue

        row = []
        for tok in tokens:
            if tok == ".":
                row.append(0)
            elif tok == "X":
                row.append(1)
            elif tok == "O":
                row.append(-1)
            else:
                raise ValueError(f"unexpected token {tok!r}")
        rows.append(row)

    if len(rows) != BOARD_SIZE:
        raise ValueError(f"expected {BOARD_SIZE} board rows, found {len(rows)}")

    return rows


def parse_side_to_move(side: str) -> int:
    side_l = side.strip().lower()
    if side_l == "black":
        return 1
    if side_l == "white":
        return -1
    raise ValueError(f"unknown side_to_move: {side!r}")


def assert_empty(board: list[list[int]], rc: list[int], label: str, case_id: str) -> None:
    r, c = rc
    if not (0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE):
        raise ValueError(f"{case_id}: {label} rc={rc} outside board")
    if board[r][c] != 0:
        raise ValueError(
            f"{case_id}: {label} rc={rc} is occupied with value={board[r][c]}. "
            "Check coordinate order. Logs are expected to be xy=col,row."
        )


def find_snapshot(data: list[dict[str, Any]], game_number: str, move_count: str) -> dict[str, Any]:
    matches = [
        item
        for item in data
        if str(item.get("game_number")) == str(game_number)
        and str(item.get("move_count")) == str(move_count)
    ]
    if len(matches) != 1:
        raise ValueError(
            f"expected exactly one snapshot for game={game_number}, move={move_count}, "
            f"found {len(matches)}"
        )
    return matches[0]


def build_dataset(snapshot_path: Path) -> dict[str, Any]:
    data = json.loads(snapshot_path.read_text())
    if not isinstance(data, list):
        raise ValueError("snapshot JSON must be a list")

    samples = []
    for spec in MARGIN_CASES:
        item = find_snapshot(data, spec["game_number"], spec["move_count"])
        board = parse_board_snapshot(item["board_snapshot_before_decision"])
        current_player = parse_side_to_move(item["side_to_move"])

        target_rc = xy_to_rc(spec["target_xy"])
        suppress_rc = xy_to_rc(spec["suppress_xy"])

        assert_empty(board, target_rc, "target", spec["case_id"])
        assert_empty(board, suppress_rc, "suppress", spec["case_id"])

        sample = {
            "case_id": spec["case_id"],
            "source": spec["source"],
            "reason": spec["reason"],
            "game_number": str(item["game_number"]),
            "move_count": str(item["move_count"]),
            "board_size": BOARD_SIZE,
            "win_length": 5,
            "side_to_move": item["side_to_move"],
            "current_player": current_player,
            "target_xy": spec["target_xy"],
            "target_rc": target_rc,
            "suppress_xy": spec["suppress_xy"],
            "suppress_rc": suppress_rc,
            "old_final_xy": [int(x) for x in str(item["final"]).split(",")],
            "old_final": item["final"],
            "board": board,
            "board_snapshot_before_decision": item["board_snapshot_before_decision"],
        }
        samples.append(sample)

    return {
        "name": "v12l_margin_repair_dataset",
        "coordinate_convention": {
            "xy": "external live/C/Rapfi logs: x,y = col,row",
            "rc": "model/Python internal: row,col",
        },
        "samples": samples,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--snapshots",
        type=Path,
        default=Path("analysis/v12i_failure_board_snapshots.json"),
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("analysis/v12l_margin_repair_dataset.json"),
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    dataset = build_dataset(args.snapshots)

    print(f"built {len(dataset['samples'])} v12l margin samples")
    for sample in dataset["samples"]:
        print("-" * 80)
        print("case_id:", sample["case_id"])
        print("game/move:", sample["game_number"], sample["move_count"])
        print("side_to_move:", sample["side_to_move"], "current_player:", sample["current_player"])
        print("target_xy:", sample["target_xy"], "target_rc:", sample["target_rc"])
        print("suppress_xy:", sample["suppress_xy"], "suppress_rc:", sample["suppress_rc"])
        print("old_final:", sample["old_final"])

    if args.dry_run:
        print("dry-run only; not writing output")
        return

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(dataset, indent=2) + "\n")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
