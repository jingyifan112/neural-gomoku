from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


DEFAULT_TARGETS: tuple[tuple[int, int], ...] = (
    (1, 38),
    (1, 44),
    (1, 46),
    (1, 48),
    (2, 29),
    (2, 31),
    (2, 33),
)

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
    "failure_type",
    "notes",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a small position-level Rapfi failure review set from extracted failure positions."
    )
    parser.add_argument("--input-json", type=Path, default=Path("analysis/rapfi_failure_positions.json"))
    parser.add_argument("--output-csv", type=Path, default=Path("analysis/rapfi_failure_set.csv"))
    parser.add_argument("--output-json", type=Path, default=Path("analysis/rapfi_failure_set.json"))
    parser.add_argument(
        "--target",
        action="append",
        default=[],
        metavar="GAME:MOVE_COUNT",
        help="Select a position. Can be repeated. Defaults to the v11 late-game review set.",
    )
    parser.add_argument(
        "--placeholder",
        default="needs_review",
        help="Placeholder value for failure_type and notes.",
    )
    return parser.parse_args()


def parse_targets(raw_targets: list[str]) -> list[tuple[int, int]]:
    if not raw_targets:
        return list(DEFAULT_TARGETS)

    targets: list[tuple[int, int]] = []
    for raw_target in raw_targets:
        try:
            game_number, move_count = raw_target.split(":", maxsplit=1)
            targets.append((int(game_number), int(move_count)))
        except ValueError as exc:
            raise ValueError(f"invalid --target {raw_target!r}; expected GAME:MOVE_COUNT") from exc
    return targets


def load_games(path: Path) -> list[dict[str, object]]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a JSON list of games")
    return data


def index_decisions(games: list[dict[str, object]]) -> dict[tuple[int, int], dict[str, object]]:
    decisions: dict[tuple[int, int], dict[str, object]] = {}
    for game in games:
        game_number = int(game["game_number"])
        for decision in game.get("debug_decisions", []):
            if not isinstance(decision, dict):
                continue
            move_count = int(decision["move_count"])
            decisions[(game_number, move_count)] = decision
    return decisions


def build_row(
    game_number: int,
    move_count: int,
    decision: dict[str, object],
    placeholder: str,
) -> dict[str, object]:
    return {
        "game_number": game_number,
        "move_count": move_count,
        "side_to_move": decision.get("side_to_move", ""),
        "value": decision.get("value", ""),
        "direct": decision.get("direct", ""),
        "policy_safety": decision.get("policy_safety", ""),
        "mcts_raw": decision.get("mcts_raw", ""),
        "mcts_safety": decision.get("mcts_safety", ""),
        "final": decision.get("final", ""),
        "previous_rapfi_bestline": decision.get("previous_rapfi_bestline", ""),
        "next_rapfi_bestline": decision.get("next_rapfi_bestline", ""),
        "failure_type": placeholder,
        "notes": placeholder,
    }


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(rows, handle, indent=2)
        handle.write("\n")


def main() -> int:
    args = parse_args()
    targets = parse_targets(args.target)
    decisions = index_decisions(load_games(args.input_json))

    rows: list[dict[str, object]] = []
    missing: list[tuple[int, int]] = []
    for game_number, move_count in targets:
        decision = decisions.get((game_number, move_count))
        if decision is None:
            missing.append((game_number, move_count))
            continue
        rows.append(build_row(game_number, move_count, decision, args.placeholder))

    if missing:
        missing_text = ", ".join(f"{game}:{move}" for game, move in missing)
        raise ValueError(f"missing requested positions: {missing_text}")

    write_csv(args.output_csv, rows)
    write_json(args.output_json, rows)
    print(f"read {args.input_json}")
    print(f"selected positions: {len(rows)}")
    print(f"wrote {args.output_csv}")
    print(f"wrote {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
