from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


BOARD_SIZE = 15
SIDE_TO_STONE = {"black": "X", "white": "O"}
STONE_TO_SIDE = {"X": "black", "O": "white"}
DIRECTIONS = ((1, 0), (0, 1), (1, 1), (1, -1))
CANDIDATE_FIELDS = ("direct", "policy_safety", "mcts_raw", "mcts_safety", "final")

OUTPUT_FIELDS = [
    "game_number",
    "move_count",
    "side_to_move",
    "opponent",
    "value",
    "direct",
    "policy_safety",
    "mcts_raw",
    "mcts_safety",
    "final",
    "current_player_immediate_winning_moves",
    "opponent_immediate_winning_moves",
    "final_blocks_immediate_win",
    "direct_blocks_immediate_win",
    "mcts_raw_blocks_immediate_win",
    "mcts_safety_blocks_immediate_win",
    "preliminary_failure_type",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Classify selected Rapfi failure snapshots by immediate win/block threats."
    )
    parser.add_argument("--input-json", type=Path, default=Path("analysis/rapfi_failure_board_snapshots.json"))
    parser.add_argument("--output-csv", type=Path, default=Path("analysis/rapfi_failure_threat_analysis.csv"))
    parser.add_argument("--output-md", type=Path, default=Path("analysis/rapfi_failure_threat_analysis.md"))
    return parser.parse_args()


def load_positions(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a JSON list")
    return data


def parse_board(snapshot: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in snapshot.splitlines():
        tokens = line.strip().split()
        if len(tokens) == BOARD_SIZE and all(token in {".", "X", "O"} for token in tokens):
            rows.append(tokens)

    if len(rows) != BOARD_SIZE:
        raise ValueError(f"expected {BOARD_SIZE} board rows, found {len(rows)}")
    return rows


def opponent_side(side_to_move: str) -> str:
    if side_to_move == "black":
        return "white"
    if side_to_move == "white":
        return "black"
    raise ValueError(f"unknown side_to_move: {side_to_move!r}")


def in_bounds(x: int, y: int) -> bool:
    return 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE


def count_direction(board: list[list[str]], x: int, y: int, dx: int, dy: int, stone: str) -> int:
    count = 0
    x += dx
    y += dy
    while in_bounds(x, y) and board[y][x] == stone:
        count += 1
        x += dx
        y += dy
    return count


def creates_five(board: list[list[str]], x: int, y: int, stone: str) -> bool:
    if board[y][x] != ".":
        return False

    board[y][x] = stone
    try:
        for dx, dy in DIRECTIONS:
            total = 1
            total += count_direction(board, x, y, dx, dy, stone)
            total += count_direction(board, x, y, -dx, -dy, stone)
            if total >= 5:
                return True
        return False
    finally:
        board[y][x] = "."


def immediate_winning_moves(board: list[list[str]], side: str) -> list[str]:
    stone = SIDE_TO_STONE[side]
    moves: list[str] = []
    for y in range(BOARD_SIZE):
        for x in range(BOARD_SIZE):
            if creates_five(board, x, y, stone):
                moves.append(format_coord(x, y))
    return moves


def format_coord(x: int, y: int) -> str:
    return f"{x},{y}"


def parse_coord(raw: str) -> str:
    raw = str(raw).strip()
    if not raw:
        return ""
    x_text, y_text = raw.split(",", maxsplit=1)
    return format_coord(int(x_text), int(y_text))


def blocks_immediate_win(candidate: str, opponent_wins: list[str]) -> bool:
    if not opponent_wins:
        return False
    return parse_coord(candidate) in set(opponent_wins)


def preliminary_failure_type(row: dict[str, str], opponent_wins: list[str]) -> str:
    final_blocks = blocks_immediate_win(row["final"], opponent_wins)
    direct_blocks = blocks_immediate_win(row["direct"], opponent_wins)
    mcts_safety_blocks = blocks_immediate_win(row["mcts_safety"], opponent_wins)
    value = float(row["value"])

    if len(opponent_wins) > 1:
        return "forced_loss_or_double_threat"
    if direct_blocks and (not mcts_safety_blocks or not final_blocks):
        return "safety_or_mcts_override_failure"
    if opponent_wins and not final_blocks:
        return "missed_immediate_block"
    if value > 0 and opponent_wins:
        return "value_miscalibration"
    return "needs_manual_review"


def analyze_position(position: dict[str, str]) -> dict[str, str]:
    board = parse_board(position.get("board_snapshot_before_decision", ""))
    side = position["side_to_move"]
    opponent = opponent_side(side)
    current_wins = immediate_winning_moves(board, side)
    opponent_wins = immediate_winning_moves(board, opponent)

    analyzed = {
        "game_number": str(position["game_number"]),
        "move_count": str(position["move_count"]),
        "side_to_move": side,
        "opponent": opponent,
        "value": str(position["value"]),
        "direct": position["direct"],
        "policy_safety": position["policy_safety"],
        "mcts_raw": position["mcts_raw"],
        "mcts_safety": position["mcts_safety"],
        "final": position["final"],
        "current_player_immediate_winning_moves": " ".join(current_wins),
        "opponent_immediate_winning_moves": " ".join(opponent_wins),
        "final_blocks_immediate_win": str(blocks_immediate_win(position["final"], opponent_wins)),
        "direct_blocks_immediate_win": str(blocks_immediate_win(position["direct"], opponent_wins)),
        "mcts_raw_blocks_immediate_win": str(blocks_immediate_win(position["mcts_raw"], opponent_wins)),
        "mcts_safety_blocks_immediate_win": str(blocks_immediate_win(position["mcts_safety"], opponent_wins)),
    }
    analyzed["preliminary_failure_type"] = preliminary_failure_type(position, opponent_wins)
    return analyzed


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# Rapfi failure threat analysis", ""]
    for row in rows:
        lines.extend(
            [
                f"## Game {row['game_number']} move_count {row['move_count']}",
                "",
                f"- side_to_move: {row['side_to_move']}",
                f"- opponent: {row['opponent']}",
                f"- value: {row['value']}",
                f"- direct: {row['direct']} blocks={row['direct_blocks_immediate_win']}",
                f"- policy_safety: {row['policy_safety']}",
                f"- mcts_raw: {row['mcts_raw']} blocks={row['mcts_raw_blocks_immediate_win']}",
                f"- mcts_safety: {row['mcts_safety']} blocks={row['mcts_safety_blocks_immediate_win']}",
                f"- final: {row['final']} blocks={row['final_blocks_immediate_win']}",
                f"- current_player_immediate_winning_moves: {row['current_player_immediate_winning_moves'] or '(none)'}",
                f"- opponent_immediate_winning_moves: {row['opponent_immediate_winning_moves'] or '(none)'}",
                f"- preliminary_failure_type: {row['preliminary_failure_type']}",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    args = parse_args()
    positions = load_positions(args.input_json)
    rows = [analyze_position(position) for position in positions]
    write_csv(args.output_csv, rows)
    write_markdown(args.output_md, rows)
    print(f"read {args.input_json}")
    print(f"analyzed positions: {len(rows)}")
    print(f"wrote {args.output_csv}")
    print(f"wrote {args.output_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
