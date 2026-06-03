from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import dataclass, field
from pathlib import Path


COORD_RE = re.compile(
    r"(?P<name>direct|policy_safety|mcts_raw|mcts_safety|final)="
    r"\(x=(?P<x>-?\d+),y=(?P<y>-?\d+),row=(?P<row>-?\d+),col=(?P<col>-?\d+)\)"
)
DECISION_MARKER_RE = re.compile(r"(?:DEBUG_DECISION|debug:_DECISION)\s+(?P<fields>.*)")
KV_RE = re.compile(r"(?P<key>[A-Za-z_]+)=(?P<value>\S+)")
ENGINE_RE = re.compile(r"engine\s+(?P<engine>\S+)\s+output")
START_RE = re.compile(r"Started game (?P<game>\d+) of (?P<total>\d+) \((?P<black>.+?) vs (?P<white>.+?)\)")
FINISH_RE = re.compile(
    r"Finished game (?P<game>\d+) \((?P<black>.+?) vs (?P<white>.+?)\): "
    r"(?P<black_score>\d+)-(?P<white_score>\d+) \{(?P<reason>.+?)\}"
)
BESTLINE_RE = re.compile(r"engine\s+(?P<engine>\S+)\s+output message:\s+Bestline\s*(?P<bestline>.*)")


@dataclass
class Decision:
    line_no: int
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
    previous_rapfi_bestline: str = ""
    next_rapfi_bestline: str = ""


@dataclass
class Game:
    log_path: Path
    game_index: int
    black: str
    white: str
    decisions: list[Decision] = field(default_factory=list)
    rapfi_bestlines: list[str] = field(default_factory=list)
    result_score: str = ""
    result_reason: str = ""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract Rapfi-loss DEBUG_DECISION positions and Bestline context from eval logs into CSV."
    )
    parser.add_argument("logs", type=Path, nargs="+")
    parser.add_argument("--output-csv", type=Path, default=Path("analysis/rapfi_failure_positions.csv"))
    parser.add_argument("--output-json", type=Path, default=Path("analysis/rapfi_failure_positions.json"))
    parser.add_argument(
        "--near-end-count",
        type=int,
        default=8,
        help="Number of final neural decisions to include as near-end move context per game.",
    )
    parser.add_argument(
        "--include-all-games",
        action="store_true",
        help="Include wins/draws/non-Rapfi games instead of only games where a neural engine lost to Rapfi.",
    )
    parser.add_argument("--rapfi-substring", default="rapfi")
    parser.add_argument("--neural-substring", default="neural")
    return parser.parse_args()


def coord_string(match: re.Match[str]) -> str:
    return f"{match.group('x')},{match.group('y')}"


def parse_decision_fields(line: str, line_no: int) -> dict[str, str] | None:
    marker_match = DECISION_MARKER_RE.search(line)
    if not marker_match:
        return None

    fields = {match.group("key"): match.group("value") for match in KV_RE.finditer(marker_match.group("fields"))}
    missing = {"move_count", "value"} - set(fields)
    if missing:
        raise ValueError(f"line {line_no}: missing decision fields: {', '.join(sorted(missing))}")
    return fields


def parse_decision(line: str, line_no: int) -> Decision | None:
    fields = parse_decision_fields(line, line_no)
    if fields is None:
        return None

    coords = {coord.group("name"): coord_string(coord) for coord in COORD_RE.finditer(line)}
    missing = {"direct", "policy_safety", "mcts_raw", "mcts_safety", "final"} - set(coords)
    if missing:
        raise ValueError(f"line {line_no}: missing coordinate fields: {', '.join(sorted(missing))}")

    engine_match = ENGINE_RE.search(line)
    return Decision(
        line_no=line_no,
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


def parse_games(path: Path) -> list[Game]:
    games: list[Game] = []
    current: Game | None = None
    pending_rapfi_bestline = ""

    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line_no, line in enumerate(handle, start=1):
            start_match = START_RE.search(line)
            if start_match:
                current = Game(
                    log_path=path,
                    game_index=int(start_match.group("game")),
                    black=start_match.group("black"),
                    white=start_match.group("white"),
                )
                games.append(current)
                pending_rapfi_bestline = ""
                continue

            if current is None:
                continue

            bestline_match = BESTLINE_RE.search(line)
            if bestline_match and "rapfi" in bestline_match.group("engine").lower():
                bestline = bestline_match.group("bestline").strip()
                current.rapfi_bestlines.append(bestline)
                pending_rapfi_bestline = bestline
                if current.decisions:
                    current.decisions[-1].next_rapfi_bestline = bestline
                continue

            decision = parse_decision(line, line_no)
            if decision:
                decision.previous_rapfi_bestline = pending_rapfi_bestline
                current.decisions.append(decision)
                continue

            finish_match = FINISH_RE.search(line)
            if finish_match:
                current.result_score = f"{finish_match.group('black_score')}-{finish_match.group('white_score')}"
                current.result_reason = finish_match.group("reason")

    return games


def side_result(game: Game, engine: str) -> str:
    if not game.result_score:
        return "unknown"
    black_score, white_score = (int(part) for part in game.result_score.split("-", maxsplit=1))
    if black_score == white_score:
        return "draw"
    winner = game.black if black_score > white_score else game.white
    return "win" if engine == winner else "loss"


def engine_side(game: Game, engine: str) -> str:
    if engine == game.black:
        return "black"
    if engine == game.white:
        return "white"
    return ""


def side_to_move(game: Game, decision: Decision) -> str:
    side = engine_side(game, decision.engine)
    if side:
        return side
    return {1: "black", -1: "white", 2: "white"}.get(decision.player, str(decision.player))


def final_neural_moves_near_end(game: Game, args: argparse.Namespace) -> list[str]:
    neural_token = args.neural_substring.lower()
    neural_decisions = [decision for decision in game.decisions if neural_token in decision.engine.lower()]
    return [f"{decision.move_count}:{decision.final}" for decision in neural_decisions[-args.near_end_count :]]


def decision_to_json(game: Game, decision: Decision) -> dict[str, object]:
    return {
        "line_no": decision.line_no,
        "engine": decision.engine,
        "side_to_move": side_to_move(game, decision),
        "move_count": decision.move_count,
        "player": decision.player,
        "sims": decision.sims,
        "mode": decision.mode,
        "value": decision.value,
        "direct": decision.direct,
        "policy_safety": decision.policy_safety,
        "mcts_raw": decision.mcts_raw,
        "mcts_safety": decision.mcts_safety,
        "final": decision.final,
        "previous_rapfi_bestline": decision.previous_rapfi_bestline,
        "next_rapfi_bestline": decision.next_rapfi_bestline,
        "debug_decision_line": decision.raw_line,
    }


def is_rapfi_failure(game: Game, decision: Decision, args: argparse.Namespace) -> bool:
    rapfi_token = args.rapfi_substring.lower()
    neural_token = args.neural_substring.lower()

    if rapfi_token not in game.black.lower() and rapfi_token not in game.white.lower():
        return False
    if neural_token not in decision.engine.lower():
        return False
    return side_result(game, decision.engine) == "loss"


def game_to_json(game: Game, args: argparse.Namespace) -> dict[str, object]:
    kept_decisions = [
        decision
        for decision in game.decisions
        if args.include_all_games or is_rapfi_failure(game, decision, args)
    ]
    return {
        "log_path": str(game.log_path),
        "game_number": game.game_index,
        "black": game.black,
        "white": game.white,
        "game_result": game.result_score,
        "loss_reason": game.result_reason,
        "rapfi_bestlines": game.rapfi_bestlines,
        "final_neural_moves_near_end": final_neural_moves_near_end(game, args),
        "debug_decisions": [decision_to_json(game, decision) for decision in kept_decisions],
    }


def rows_for_game(game: Game, args: argparse.Namespace) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for decision in game.decisions:
        if not args.include_all_games and not is_rapfi_failure(game, decision, args):
            continue
        rows.append(
            {
                "log_path": str(game.log_path),
                "game_number": str(game.game_index),
                "black": game.black,
                "white": game.white,
                "side_to_move": side_to_move(game, decision),
                "game_result": game.result_score,
                "loss_reason": game.result_reason,
                "decision_engine": decision.engine,
                "decision_engine_result": side_result(game, decision.engine),
                "line_no": str(decision.line_no),
                "move_count": str(decision.move_count),
                "player": str(decision.player),
                "sims": str(decision.sims),
                "mode": decision.mode,
                "value": f"{decision.value:.6f}",
                "direct": decision.direct,
                "policy_safety": decision.policy_safety,
                "mcts_raw": decision.mcts_raw,
                "mcts_safety": decision.mcts_safety,
                "final": decision.final,
                "previous_rapfi_bestline": decision.previous_rapfi_bestline,
                "next_rapfi_bestline": decision.next_rapfi_bestline,
                "all_rapfi_bestlines": " | ".join(game.rapfi_bestlines),
                "final_neural_moves_near_end": " | ".join(final_neural_moves_near_end(game, args)),
                "debug_decision_line": decision.raw_line,
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = [
        "log_path",
        "game_number",
        "black",
        "white",
        "side_to_move",
        "game_result",
        "loss_reason",
        "decision_engine",
        "decision_engine_result",
        "line_no",
        "move_count",
        "player",
        "sims",
        "mode",
        "value",
        "direct",
        "policy_safety",
        "mcts_raw",
        "mcts_safety",
        "final",
        "previous_rapfi_bestline",
        "next_rapfi_bestline",
        "all_rapfi_bestlines",
        "final_neural_moves_near_end",
        "debug_decision_line",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, games: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(games, handle, indent=2)
        handle.write("\n")


def main() -> int:
    args = parse_args()
    rows: list[dict[str, str]] = []
    json_games: list[dict[str, object]] = []
    game_count = 0

    for log_path in args.logs:
        games = parse_games(log_path)
        game_count += len(games)
        for game in games:
            rows.extend(rows_for_game(game, args))
            game_json = game_to_json(game, args)
            if args.include_all_games or game_json["debug_decisions"]:
                json_games.append(game_json)

    write_csv(args.output_csv, rows)
    write_json(args.output_json, json_games)
    print(f"parsed logs: {len(args.logs)}")
    print(f"parsed games: {game_count}")
    print(f"wrote rows: {len(rows)}")
    print(f"wrote {args.output_csv}")
    print(f"wrote {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
