from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path


BOARD_SIZE = 15
SEPARATOR_RE = re.compile(r"^\s*-{10,}\s*$")
BOARD_ROW_RE = re.compile(r"^\s*(?:[.XO]\s+){14}[.XO]\s*$")
START_RE = re.compile(r"Started game (?P<game>\d+) of \d+ \((?P<black>.+?) vs (?P<white>.+?)\)")
FINISH_RE = re.compile(
    r"Finished game (?P<game>\d+) \((?P<black>.+?) vs (?P<white>.+?)\): "
    r"(?P<black_score>\d+)-(?P<white_score>\d+) \{(?P<reason>.+?)\}"
)
DECISION_RE = re.compile(r"(?:DEBUG_DECISION|debug:_DECISION)\s+.*?\bmove_count=(?P<move_count>\d+)\b")

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
    "board_snapshot_before_decision",
    "board_snapshot_after_decision",
    "loss_reason",
    "failure_type",
    "notes",
]


@dataclass(frozen=True)
class BoardBlock:
    start_line: int
    end_line: int
    text: str


@dataclass(frozen=True)
class DecisionLocation:
    game_number: int
    move_count: int
    line_no: int
    before_board: str
    after_board: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Attach nearest c-gomoku-cli board snapshots to the selected Rapfi failure set."
    )
    parser.add_argument("--failure-set-csv", type=Path, default=Path("analysis/rapfi_failure_set.csv"))
    parser.add_argument("--debug-log", type=Path, default=Path("eval_logs/2026-06-02_v11_mcts32_debug_vs_rapfi_g2.log"))
    parser.add_argument("--output-md", type=Path, default=Path("analysis/rapfi_failure_board_snapshots.md"))
    parser.add_argument("--output-json", type=Path, default=Path("analysis/rapfi_failure_board_snapshots.json"))
    return parser.parse_args()


def load_failure_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def parse_board_block(lines: list[str], start_index: int) -> BoardBlock | None:
    if not SEPARATOR_RE.match(lines[start_index]):
        return None
    row_start = start_index + 1
    row_end = row_start + BOARD_SIZE
    separator_end = row_end
    if separator_end >= len(lines):
        return None
    rows = lines[row_start:row_end]
    if len(rows) != BOARD_SIZE or not all(BOARD_ROW_RE.match(row) for row in rows):
        return None
    if not SEPARATOR_RE.match(lines[separator_end]):
        return None
    return BoardBlock(
        start_line=start_index + 1,
        end_line=separator_end + 1,
        text="".join(lines[start_index : separator_end + 1]).rstrip(),
    )


def find_next_board(blocks: list[BoardBlock], line_no: int) -> str:
    for block in blocks:
        if block.start_line > line_no:
            return block.text
    return ""


def find_previous_board(blocks: list[BoardBlock], line_no: int) -> str:
    previous = ""
    for block in blocks:
        if block.end_line >= line_no:
            return previous
        previous = block.text
    return previous


def parse_debug_log(path: Path) -> tuple[dict[tuple[int, int], DecisionLocation], dict[int, str]]:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)
    board_blocks: list[BoardBlock] = []
    for index in range(len(lines)):
        block = parse_board_block(lines, index)
        if block is not None:
            board_blocks.append(block)

    current_game = 0
    decisions: dict[tuple[int, int], DecisionLocation] = {}
    loss_reasons: dict[int, str] = {}
    for index, line in enumerate(lines):
        line_no = index + 1
        start_match = START_RE.search(line)
        if start_match:
            current_game = int(start_match.group("game"))
            continue

        finish_match = FINISH_RE.search(line)
        if finish_match:
            loss_reasons[int(finish_match.group("game"))] = finish_match.group("reason")
            continue

        decision_match = DECISION_RE.search(line)
        if not decision_match:
            continue

        move_count = int(decision_match.group("move_count"))
        decisions[(current_game, move_count)] = DecisionLocation(
            game_number=current_game,
            move_count=move_count,
            line_no=line_no,
            before_board=find_previous_board(board_blocks, line_no),
            after_board=find_next_board(board_blocks, line_no),
        )

    return decisions, loss_reasons


def enrich_rows(
    failure_rows: list[dict[str, str]],
    decisions: dict[tuple[int, int], DecisionLocation],
    loss_reasons: dict[int, str],
) -> list[dict[str, str]]:
    enriched: list[dict[str, str]] = []
    missing: list[tuple[int, int]] = []

    for row in failure_rows:
        game_number = int(row["game_number"])
        move_count = int(row["move_count"])
        location = decisions.get((game_number, move_count))
        if location is None:
            missing.append((game_number, move_count))
            continue

        enriched.append(
            {
                "game_number": row["game_number"],
                "move_count": row["move_count"],
                "side_to_move": row["side_to_move"],
                "value": row["value"],
                "direct": row["direct"],
                "policy_safety": row["policy_safety"],
                "mcts_raw": row["mcts_raw"],
                "mcts_safety": row["mcts_safety"],
                "final": row["final"],
                "previous_rapfi_bestline": row["previous_rapfi_bestline"],
                "next_rapfi_bestline": row["next_rapfi_bestline"],
                "board_snapshot_before_decision": location.before_board,
                "board_snapshot_after_decision": location.after_board,
                "loss_reason": loss_reasons.get(game_number, ""),
                "failure_type": row.get("failure_type", "needs_review") or "needs_review",
                "notes": row.get("notes", "needs_review") or "needs_review",
            }
        )

    if missing:
        missing_text = ", ".join(f"{game}:{move}" for game, move in missing)
        raise ValueError(f"missing decision lines for selected positions: {missing_text}")

    return enriched


def write_json(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(rows, handle, indent=2)
        handle.write("\n")


def write_markdown(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# Rapfi failure board snapshots", ""]
    for row in rows:
        title = f"Game {row['game_number']} move_count {row['move_count']}"
        lines.extend(
            [
                f"## {title}",
                "",
                f"- side_to_move: {row['side_to_move']}",
                f"- value: {row['value']}",
                f"- direct: {row['direct']}",
                f"- policy_safety: {row['policy_safety']}",
                f"- mcts_raw: {row['mcts_raw']}",
                f"- mcts_safety: {row['mcts_safety']}",
                f"- final: {row['final']}",
                f"- previous_rapfi_bestline: {row['previous_rapfi_bestline']}",
                f"- next_rapfi_bestline: {row['next_rapfi_bestline']}",
                f"- loss_reason: {row['loss_reason']}",
                f"- failure_type: {row['failure_type']}",
                f"- notes: {row['notes']}",
                "",
                "Before decision:",
                "",
                "```text",
                row["board_snapshot_before_decision"] or "(not available)",
                "```",
                "",
                "After decision:",
                "",
                "```text",
                row["board_snapshot_after_decision"] or "(not available)",
                "```",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    args = parse_args()
    failure_rows = load_failure_rows(args.failure_set_csv)
    decisions, loss_reasons = parse_debug_log(args.debug_log)
    enriched_rows = enrich_rows(failure_rows, decisions, loss_reasons)

    write_json(args.output_json, enriched_rows)
    write_markdown(args.output_md, enriched_rows)
    print(f"read {args.failure_set_csv}")
    print(f"read {args.debug_log}")
    print(f"selected positions: {len(enriched_rows)}")
    print(f"wrote {args.output_md}")
    print(f"wrote {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
