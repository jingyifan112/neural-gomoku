from __future__ import annotations

import argparse
import csv
import re
from dataclasses import dataclass
from pathlib import Path


COORD_RE = re.compile(
    r"(?P<name>direct|policy_safety|mcts_raw|mcts_safety|final)="
    r"\(x=(?P<x>-?\d+),y=(?P<y>-?\d+),row=(?P<row>-?\d+),col=(?P<col>-?\d+)\)"
)
DECISION_MARKER_RE = re.compile(r"(?:DEBUG_DECISION|debug:_DECISION)\s+(?P<fields>.*)")
KV_RE = re.compile(r"(?P<key>[A-Za-z_]+)=(?P<value>\S+)")
ENGINE_RE = re.compile(r"engine\s+(?P<engine>\S+)\s+output")
START_RE = re.compile(r"Started game (?P<game>\d+) of \d+ \((?P<black>.+?) vs (?P<white>.+?)\)")


@dataclass(frozen=True)
class Decision:
    path: Path
    line_no: int
    game_index: int
    engine: str
    move_count: int
    player: int
    sims: int
    value: float
    mode: str
    direct: str
    policy_safety: str
    mcts_raw: str
    mcts_safety: str
    final: str
    raw_line: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare pbrain DEBUG_DECISION lines from two logs by game and move_count."
    )
    parser.add_argument("left_log", type=Path)
    parser.add_argument("right_log", type=Path)
    parser.add_argument("--left-label", default="left")
    parser.add_argument("--right-label", default="right")
    parser.add_argument(
        "--key",
        choices=["game_move", "move_count"],
        default="game_move",
        help="Use game+move_count alignment by default; move_count is useful for single-game/fixed-board logs.",
    )
    parser.add_argument("--output-csv", type=Path, default=None)
    parser.add_argument("--all", action="store_true", help="Include matching rows as well as differences.")
    parser.add_argument("--max-rows", type=int, default=0, help="Limit rows printed to stdout; 0 means no limit.")
    return parser.parse_args()


def coord_string(match: re.Match[str]) -> str:
    return f"{match.group('x')},{match.group('y')}"


def parse_decision_fields(line: str, path: Path, line_no: int) -> dict[str, str] | None:
    marker_match = DECISION_MARKER_RE.search(line)
    if not marker_match:
        return None

    fields = {match.group("key"): match.group("value") for match in KV_RE.finditer(marker_match.group("fields"))}
    missing = {"move_count", "value"} - set(fields)
    if missing:
        raise ValueError(f"{path}:{line_no}: missing decision fields: {', '.join(sorted(missing))}")
    return fields


def parse_decisions(path: Path) -> list[Decision]:
    decisions: list[Decision] = []
    game_index = 0

    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line_no, line in enumerate(handle, start=1):
            if START_RE.search(line):
                game_index += 1

            fields = parse_decision_fields(line, path, line_no)
            if fields is None:
                continue

            coords = {match.group("name"): coord_string(match) for match in COORD_RE.finditer(line)}
            missing = {"direct", "policy_safety", "mcts_raw", "mcts_safety", "final"} - set(coords)
            if missing:
                raise ValueError(f"{path}:{line_no}: missing coordinate fields: {', '.join(sorted(missing))}")

            engine_match = ENGINE_RE.search(line)
            decisions.append(
                Decision(
                    path=path,
                    line_no=line_no,
                    game_index=game_index,
                    engine=engine_match.group("engine") if engine_match else "",
                    move_count=int(fields["move_count"]),
                    player=int(fields.get("player", "0")),
                    sims=int(fields.get("sims", "0")),
                    value=float(fields["value"]),
                    mode=fields.get("mode", ""),
                    direct=coords["direct"],
                    policy_safety=coords["policy_safety"],
                    mcts_raw=coords["mcts_raw"],
                    mcts_safety=coords["mcts_safety"],
                    final=coords["final"],
                    raw_line=line.strip(),
                )
            )

    return decisions


def decision_key(decision: Decision, key_mode: str) -> tuple[int, ...]:
    if key_mode == "move_count":
        return (decision.move_count,)
    return (decision.game_index, decision.move_count)


def index_decisions(decisions: list[Decision], key_mode: str, label: str) -> dict[tuple[int, ...], Decision]:
    indexed: dict[tuple[int, ...], Decision] = {}
    duplicates: set[tuple[int, ...]] = set()
    for decision in decisions:
        key = decision_key(decision, key_mode)
        if key in indexed:
            duplicates.add(key)
        indexed[key] = decision

    if duplicates:
        sample = ", ".join(str(key) for key in sorted(duplicates)[:5])
        raise ValueError(
            f"{label} has duplicate comparison keys ({sample}); rerun with --key game_move or split the log."
        )

    return indexed


def make_row(key: tuple[int, ...], left: Decision | None, right: Decision | None, args: argparse.Namespace) -> dict[str, str]:
    game_index = str(key[0] if args.key == "game_move" else (left or right).game_index)
    move_count = str(key[1] if args.key == "game_move" else key[0])

    row: dict[str, str] = {
        "game_index": game_index,
        "move_count": move_count,
        "status": "both" if left and right else ("left_only" if left else "right_only"),
    }

    for side_label, decision in ((args.left_label, left), (args.right_label, right)):
        prefix = side_label
        if decision is None:
            for field in ("line_no", "engine", "mode", "value", "direct", "policy_safety", "mcts_raw", "mcts_safety", "final"):
                row[f"{prefix}_{field}"] = ""
            continue

        row[f"{prefix}_line_no"] = str(decision.line_no)
        row[f"{prefix}_engine"] = decision.engine
        row[f"{prefix}_mode"] = decision.mode
        row[f"{prefix}_value"] = f"{decision.value:.6f}"
        row[f"{prefix}_direct"] = decision.direct
        row[f"{prefix}_policy_safety"] = decision.policy_safety
        row[f"{prefix}_mcts_raw"] = decision.mcts_raw
        row[f"{prefix}_mcts_safety"] = decision.mcts_safety
        row[f"{prefix}_final"] = decision.final

    if left and right:
        row["value_delta_right_minus_left"] = f"{right.value - left.value:.6f}"
        row["value_diff"] = str(left.value != right.value)
        row["direct_diff"] = str(left.direct != right.direct)
        row["policy_safety_diff"] = str(left.policy_safety != right.policy_safety)
        row["mcts_raw_diff"] = str(left.mcts_raw != right.mcts_raw)
        row["mcts_safety_diff"] = str(left.mcts_safety != right.mcts_safety)
        row["final_diff"] = str(left.final != right.final)
    else:
        row["value_delta_right_minus_left"] = ""
        for field in ("value_diff", "direct_diff", "policy_safety_diff", "mcts_raw_diff", "mcts_safety_diff", "final_diff"):
            row[field] = "True"

    return row


def is_difference(row: dict[str, str]) -> bool:
    if row["status"] != "both":
        return True
    return any(
        row[field] == "True"
        for field in ("value_diff", "direct_diff", "policy_safety_diff", "mcts_raw_diff", "mcts_safety_diff", "final_diff")
    )


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    args = parse_args()
    left_decisions = parse_decisions(args.left_log)
    right_decisions = parse_decisions(args.right_log)

    left_index = index_decisions(left_decisions, args.key, args.left_label)
    right_index = index_decisions(right_decisions, args.key, args.right_label)

    rows: list[dict[str, str]] = []
    for key in sorted(set(left_index) | set(right_index)):
        row = make_row(key, left_index.get(key), right_index.get(key), args)
        if args.all or is_difference(row):
            rows.append(row)

    if args.output_csv:
        write_csv(args.output_csv, rows)

    compared = len(set(left_index) & set(right_index))
    final_diffs = sum(1 for row in rows if row.get("final_diff") == "True")
    direct_diffs = sum(1 for row in rows if row.get("direct_diff") == "True")
    print(f"parsed {args.left_label}: {len(left_decisions)} decisions")
    print(f"parsed {args.right_label}: {len(right_decisions)} decisions")
    print(f"aligned decisions: {compared}")
    print(f"reported rows: {len(rows)}")
    print(f"direct diffs in reported rows: {direct_diffs}")
    print(f"final diffs in reported rows: {final_diffs}")

    display_rows = rows if args.max_rows <= 0 else rows[: args.max_rows]
    for row in display_rows:
        print(
            "game={game_index} move={move_count} "
            "direct {left_direct}->{right_direct} "
            "policy_safe {left_policy_safety}->{right_policy_safety} "
            "mcts_raw {left_mcts_raw}->{right_mcts_raw} "
            "mcts_safe {left_mcts_safety}->{right_mcts_safety} "
            "final {left_final}->{right_final} "
            "value_delta={value_delta_right_minus_left}".format(
                left_direct=row.get(f"{args.left_label}_direct", ""),
                right_direct=row.get(f"{args.right_label}_direct", ""),
                left_policy_safety=row.get(f"{args.left_label}_policy_safety", ""),
                right_policy_safety=row.get(f"{args.right_label}_policy_safety", ""),
                left_mcts_raw=row.get(f"{args.left_label}_mcts_raw", ""),
                right_mcts_raw=row.get(f"{args.right_label}_mcts_raw", ""),
                left_mcts_safety=row.get(f"{args.left_label}_mcts_safety", ""),
                right_mcts_safety=row.get(f"{args.right_label}_mcts_safety", ""),
                left_final=row.get(f"{args.left_label}_final", ""),
                right_final=row.get(f"{args.right_label}_final", ""),
                **row,
            )
        )

    if args.output_csv:
        print(f"wrote {args.output_csv}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
