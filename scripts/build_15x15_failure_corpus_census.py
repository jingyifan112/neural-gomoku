#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import re
import subprocess
from collections import Counter
from dataclasses import dataclass, field
from itertools import count
from pathlib import Path

import numpy as np

from gomoku_agent.board import BLACK, WHITE, Board
from gomoku_agent.search_safety import filter_immediate_losses, opponent_has_forcing_terminal_reply


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WEIGHTS = Path("/Users/jing1fan/neural-gomoku/weights/15x15_current_best_margin_candidate_d_move15_lastmove_weights.bin")

START_RE = re.compile(r"Started game (?P<game>\d+) of (?P<total>\d+) \((?P<black>.+?) vs (?P<white>.+?)\)")
FINISH_RE = re.compile(
    r"Finished game (?P<game>\d+) \((?P<black>.+?) vs (?P<white>.+?)\): "
    r"(?P<black_score>\d+)-(?P<white_score>\d+) \{(?P<reason>.+?)\}"
)
COMBINED_DECISION_RE = re.compile(r"engine\s+(?P<engine>\S+)\s+output\s+(?:debug:_DECISION|DEBUG_DECISION)\s+(?P<fields>.*)")
ENGINE_IO_DECISION_RE = re.compile(r"(?P<engine>\S+)\s+->\s+DEBUG_DECISION\s+(?P<fields>.*)")
COMBINED_BESTLINE_RE = re.compile(r"engine\s+(?P<engine>\S+)\s+output message:\s+Bestline\s*(?P<bestline>.*)")
ENGINE_IO_BESTLINE_RE = re.compile(r"(?P<engine>\S+)\s+->\s+MESSAGE Bestline\s*(?P<bestline>.*)")
ENGINE_IO_MOVE_RE = re.compile(r"(?P<engine>\S+)\s+->\s+(?P<x>\d+),(?P<y>\d+)\s*$")
COORD_RE = re.compile(
    r"(?P<name>direct|policy_safety|mcts_raw|mcts_safety|final)="
    r"\(x=(?P<x>-?\d+),y=(?P<y>-?\d+),row=(?P<row>-?\d+),col=(?P<col>-?\d+)\)"
)
KV_RE = re.compile(r"(?P<key>[A-Za-z_]+)=(?P<value>\S+)")
LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


@dataclass
class Decision:
    line_no: int
    engine: str
    game_number: int
    black: str
    white: str
    ply: int
    player: int
    sims: int
    mode: str
    logged_value: float
    direct: str
    policy_safety: str
    mcts_raw: str
    mcts_safety: str
    final: str
    board_moves_before: tuple[tuple[str, str], ...]
    previous_rapfi_bestline: str
    raw_line: str


@dataclass
class Game:
    log_path: Path
    game_number: int
    black: str
    white: str
    moves: list[tuple[str, str]] = field(default_factory=list)
    decisions: list[Decision] = field(default_factory=list)
    rapfi_bestlines: list[str] = field(default_factory=list)
    result_score: str = ""
    result_reason: str = ""
    parse_warnings: list[str] = field(default_factory=list)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a 15x15 full-game Rapfi-loss failure census from debug logs.")
    parser.add_argument("logs", type=Path, nargs="+")
    parser.add_argument("--weights", type=Path, default=DEFAULT_WEIGHTS)
    parser.add_argument("--dump-infer", type=Path, default=ROOT / "c_inference/dump_infer")
    parser.add_argument("--case-dir", type=Path, default=ROOT / "analysis/integration_eval/15x15_failure_corpus_c_cases")
    parser.add_argument("--output-csv", type=Path, default=ROOT / "analysis/integration_eval/15x15_failure_corpus_census.csv")
    parser.add_argument("--summary-csv", type=Path, default=ROOT / "analysis/integration_eval/15x15_failure_corpus_summary.csv")
    parser.add_argument("--output-md", type=Path, default=ROOT / "analysis/integration_eval/15x15_failure_corpus_report.md")
    parser.add_argument("--board-size", type=int, default=15)
    parser.add_argument("--win-length", type=int, default=5)
    parser.add_argument("--neural-substring", default="neural")
    parser.add_argument("--rapfi-substring", default="rapfi")
    parser.add_argument("--losing-value-threshold", type=float, default=-0.50)
    parser.add_argument("--top-k-clusters", type=int, default=8)
    parser.add_argument("--include-non-losses", action="store_true")
    parser.add_argument(
        "--skip-safety",
        action="store_true",
        help="Light parse mode: skip safety/forcing scans and C inference; mark enriched fields as NA.",
    )
    parser.add_argument("--max-games", type=int, default=0, help="Debug limit; 0 means no limit.")
    parser.add_argument("--max-decisions", type=int, default=0, help="Debug limit over censused decisions; 0 means no limit.")
    return parser.parse_args()


def pbrain_to_xy(token: str, board_size: int) -> str:
    token = token.strip().upper()
    if len(token) < 2 or token[0] not in LETTERS:
        raise ValueError(f"unsupported pbrain coordinate: {token!r}")
    x = LETTERS.index(token[0])
    y = int(token[1:]) - 1
    if not (0 <= x < board_size and 0 <= y < board_size):
        raise ValueError(f"coordinate outside {board_size}x{board_size}: {token!r}")
    return f"{x},{y}"


def xy_to_action(xy: str, board_size: int) -> int:
    x_text, y_text = xy.split(",", maxsplit=1)
    return int(y_text) * board_size + int(x_text)


def action_to_xy(action: int, board_size: int) -> str:
    row, col = divmod(int(action), board_size)
    return f"{col},{row}"


def parse_decision_line(line: str, line_no: int) -> tuple[str, dict[str, str], dict[str, str]] | None:
    match = COMBINED_DECISION_RE.search(line) or ENGINE_IO_DECISION_RE.search(line)
    if not match:
        return None
    fields = {item.group("key"): item.group("value") for item in KV_RE.finditer(match.group("fields"))}
    coords = {
        item.group("name"): f"{item.group('x')},{item.group('y')}"
        for item in COORD_RE.finditer(line)
    }
    required = {"move_count", "value"}
    if not required <= fields.keys() or not {"direct", "policy_safety", "mcts_raw", "mcts_safety", "final"} <= coords.keys():
        raise ValueError(f"line {line_no}: incomplete DEBUG_DECISION line")
    return match.group("engine"), fields, coords


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


def parse_games(log_path: Path, board_size: int, rapfi_substring: str) -> list[Game]:
    games: list[Game] = []
    current: Game | None = None
    pending_rapfi_bestline = ""

    for line_no, line in enumerate(log_path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
        start = START_RE.search(line)
        if start:
            current = Game(
                log_path=log_path,
                game_number=int(start.group("game")),
                black=start.group("black"),
                white=start.group("white"),
            )
            games.append(current)
            pending_rapfi_bestline = ""
            continue

        if current is None:
            continue

        finish = FINISH_RE.search(line)
        if finish:
            current.result_score = f"{finish.group('black_score')}-{finish.group('white_score')}"
            current.result_reason = finish.group("reason")
            continue

        decision = parse_decision_line(line, line_no)
        if decision:
            engine, fields, coords = decision
            item = Decision(
                line_no=line_no,
                engine=engine,
                game_number=current.game_number,
                black=current.black,
                white=current.white,
                ply=int(fields["move_count"]),
                player=int(fields.get("player", "0")),
                sims=int(fields.get("sims", "0")),
                mode=fields.get("mode", ""),
                logged_value=float(fields["value"]),
                direct=coords["direct"],
                policy_safety=coords["policy_safety"],
                mcts_raw=coords["mcts_raw"],
                mcts_safety=coords["mcts_safety"],
                final=coords["final"],
                board_moves_before=tuple(current.moves),
                previous_rapfi_bestline=pending_rapfi_bestline,
                raw_line=line.strip(),
            )
            current.decisions.append(item)
            current.moves.append((engine, item.final))
            continue

        explicit_move = ENGINE_IO_MOVE_RE.search(line)
        if explicit_move:
            engine = explicit_move.group("engine")
            xy = f"{explicit_move.group('x')},{explicit_move.group('y')}"
            if not current.moves or current.moves[-1] != (engine, xy):
                current.moves.append((engine, xy))
            continue

        bestline = COMBINED_BESTLINE_RE.search(line) or ENGINE_IO_BESTLINE_RE.search(line)
        if bestline and rapfi_substring.lower() in bestline.group("engine").lower():
            pending_rapfi_bestline = bestline.group("bestline").strip()
            current.rapfi_bestlines.append(pending_rapfi_bestline)
            if COMBINED_BESTLINE_RE.search(line):
                token = pending_rapfi_bestline.split()[0] if pending_rapfi_bestline.split() else ""
                if token:
                    try:
                        current.moves.append((bestline.group("engine"), pbrain_to_xy(token, board_size)))
                    except ValueError as exc:
                        current.parse_warnings.append(f"line {line_no}: {exc}")
            continue

    return games


def build_board(decision: Decision, board_size: int, win_length: int) -> Board:
    board = Board(size=board_size, win_length=win_length)
    for index, (_engine, xy) in enumerate(decision.board_moves_before):
        action = xy_to_action(xy, board_size)
        row, col = divmod(action, board_size)
        if board.grid[row, col] != 0:
            continue
        board.grid[row, col] = BLACK if index % 2 == 0 else WHITE
    board.move_count = int(np.count_nonzero(board.grid))
    board.current_player = BLACK if board.move_count % 2 == 0 else WHITE
    if decision.board_moves_before:
        last_action = xy_to_action(decision.board_moves_before[-1][1], board_size)
        board.last_move = divmod(last_action, board_size)
    return board


_CASE_COUNTER = count()


def run_c_eval(args: argparse.Namespace, board: Board, label: str) -> tuple[np.ndarray, float]:
    case_path = args.case_dir / f"{next(_CASE_COUNTER):05d}_{label}"
    case_path.mkdir(parents=True, exist_ok=True)
    input_path = case_path / "input.bin"
    legal_path = case_path / "legal_mask.bin"
    prefix = case_path / "c"
    top_path = case_path / "top.txt"
    board.encode().astype("<f4").tofile(input_path)
    board.legal_mask().astype("<f4").tofile(legal_path)
    subprocess.run(
        [
            str(args.dump_infer),
            str(args.weights),
            str(input_path),
            str(legal_path),
            str(prefix),
            str(top_path),
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    probs = np.fromfile(case_path / "c_policy_probs.bin", dtype="<f4")
    value = float(np.fromfile(case_path / "c_value.bin", dtype="<f4")[0])
    return probs, value


def rank_for_action(probs: np.ndarray, board: Board, action: int) -> int | None:
    legal = [int(move) for move in board.legal_moves()]
    if action not in legal:
        return None
    ranked = sorted(legal, key=lambda move: float(probs[move]), reverse=True)
    return ranked.index(action) + 1


def move_passes_safety(board: Board, action: int) -> bool:
    if action not in set(int(move) for move in board.legal_moves()):
        return False
    visits = board.legal_mask()
    filtered = filter_immediate_losses(board, visits)
    return bool(filtered[action] > 0)


def immediate_fork_moves(board: Board, player: int) -> list[int]:
    forks: list[int] = []
    for action in board.legal_moves():
        scratch = board.clone()
        result = scratch.play_flat(int(action))
        if result.done:
            continue
        if len(scratch.immediate_winning_moves(player)) >= 2:
            forks.append(int(action))
    return forks


def board_terminal_status(board: Board) -> bool:
    if board.last_move is None:
        return False
    row, col = board.last_move
    player = int(board.grid[row, col])
    return bool(player and board._has_five_from(row, col, player))


def local_pattern(board: Board, action: int, radius: int = 2) -> str:
    row, col = divmod(action, board.size)
    chars: list[str] = []
    for r in range(row - radius, row + radius + 1):
        for c in range(col - radius, col + radius + 1):
            if not (0 <= r < board.size and 0 <= c < board.size):
                chars.append("#")
            else:
                value = int(board.grid[r, c])
                chars.append("C" if value == board.current_player else "O" if value == -board.current_player else ".")
        chars.append("/")
    return "".join(chars)


def rows_for_loss_game(args: argparse.Namespace, game: Game) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for decision in game.decisions:
        if args.max_decisions and args._decisions_processed >= args.max_decisions:
            break
        if args.neural_substring.lower() not in decision.engine.lower():
            continue
        if not args.include_non_losses and side_result(game, decision.engine) != "loss":
            continue

        board = build_board(decision, args.board_size, args.win_length)
        final_action = xy_to_action(decision.final, args.board_size)
        direct_action = xy_to_action(decision.direct, args.board_size)

        if args.skip_safety:
            c_value = None
            final_rank: int | None = None
            direct_rank: int | None = None
            final_rank_text = "NA"
            direct_rank_text = "NA"
            final_prob = "NA"
            direct_prob = "NA"
            final_safe = "NA"
            direct_safe = "NA"
            opponent_win_count = "NA"
            opponent_win_moves = "NA"
            opponent_fork_count = "NA"
            opponent_fork_moves = "NA"
            forced_before = "NA"
            after_final_forced = "NA"
        else:
            probs, c_value = run_c_eval(args, board, f"{game.log_path.stem}_g{game.game_number}_p{decision.ply}")
            opponent_wins = board.immediate_winning_moves(-board.current_player)
            opponent_forks = immediate_fork_moves(board, -board.current_player)
            opponent_win_count = str(len(opponent_wins))
            opponent_win_moves = " ".join(action_to_xy(action, args.board_size) for action in opponent_wins) or "NA"
            opponent_fork_count = str(len(opponent_forks))
            opponent_fork_moves = " ".join(action_to_xy(action, args.board_size) for action in opponent_forks) or "NA"
            forced_before = str(opponent_has_forcing_terminal_reply(board.clone()))
            final_safe = str(move_passes_safety(board, final_action))
            direct_safe = str(move_passes_safety(board, direct_action))
            after_final_forced = "NA"
            if final_action in set(int(move) for move in board.legal_moves()):
                child = board.clone()
                result = child.play_flat(final_action)
            after_final_forced = str(False if result.done else opponent_has_forcing_terminal_reply(child))
            final_rank = rank_for_action(probs, board, final_action)
            direct_rank = rank_for_action(probs, board, direct_action)
            final_rank_text = str(final_rank) if final_rank is not None else "ILLEGAL"
            direct_rank_text = str(direct_rank) if direct_rank is not None else "ILLEGAL"
            final_prob = f"{float(probs[final_action]):.6f}" if final_rank is not None else "ILLEGAL"
            direct_prob = f"{float(probs[direct_action]):.6f}" if direct_rank is not None else "ILLEGAL"

        args._decisions_processed += 1
        if args._decisions_processed % 25 == 0:
            print(f"processed decisions: {args._decisions_processed}", flush=True)

        rows.append(
            {
                "log_path": str(game.log_path),
                "game_id": f"{game.log_path.stem}:g{game.game_number}",
                "game_number": str(game.game_number),
                "black": game.black,
                "white": game.white,
                "game_result": game.result_score,
                "loss_reason": game.result_reason,
                "side_to_move": engine_side(game, decision.engine) or str(decision.player),
                "decision_engine": decision.engine,
                "decision_engine_result": side_result(game, decision.engine),
                "ply": str(decision.ply),
                "neural_move": decision.final,
                "direct_policy_top_move": decision.direct,
                "policy_safety_move": decision.policy_safety,
                "mcts_raw_move": decision.mcts_raw,
                "mcts_final_move": decision.mcts_safety,
                "direct_vs_mcts_divergence": str(decision.direct != decision.mcts_safety),
                "direct_vs_final_divergence": str(decision.direct != decision.final),
                "logged_value": f"{decision.logged_value:.6f}",
                "c_value": f"{c_value:.6f}" if c_value is not None else "NA",
                "neural_move_policy_rank": final_rank_text,
                "neural_move_policy_prob": final_prob,
                "direct_policy_rank": direct_rank_text,
                "direct_policy_prob": direct_prob,
                "neural_move_safety_pass": final_safe,
                "direct_move_safety_pass": direct_safe,
                "opponent_immediate_win_count_before": opponent_win_count,
                "opponent_immediate_win_moves_before": opponent_win_moves,
                "opponent_fork_count_before": opponent_fork_count,
                "opponent_fork_moves_before": opponent_fork_moves,
                "opponent_forcing_reply_exists_before": forced_before,
                "opponent_forcing_reply_after_neural_move": after_final_forced,
                "already_forced_loss_signal": (
                    "NA" if args.skip_safety else str(forced_before == "True" or decision.logged_value <= args.losing_value_threshold)
                ),
                "board_terminal_before": str(board_terminal_status(board)),
                "legal_moves_before": str(len(board.legal_moves())),
                "local_pattern_5x5_current_pov": local_pattern(board, final_action),
                "previous_rapfi_bestline": decision.previous_rapfi_bestline or "NA",
                "debug_decision_line": decision.raw_line,
            }
        )
    return rows


def first_value(rows: list[dict[str, str]], key: str, predicate) -> str:
    for row in rows:
        if predicate(row):
            return row[key]
    return "NA"


def make_summary_rows(args: argparse.Namespace, games: list[Game], census_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    rows_by_game: dict[str, list[dict[str, str]]] = {}
    for row in census_rows:
        rows_by_game.setdefault(row["game_id"], []).append(row)

    summary: list[dict[str, str]] = []
    for game in games:
        neural_decisions = [
            decision for decision in game.decisions
            if args.neural_substring.lower() in decision.engine.lower()
        ]
        neural_result = "unknown"
        if neural_decisions:
            neural_result = side_result(game, neural_decisions[0].engine)
        game_id = f"{game.log_path.stem}:g{game.game_number}"
        rows = rows_by_game.get(game_id, [])
        summary.append(
            {
                "log_path": str(game.log_path),
                "game_id": game_id,
                "game_number": str(game.game_number),
                "black": game.black,
                "white": game.white,
                "game_result": game.result_score or "NA",
                "loss_reason": game.result_reason or "NA",
                "neural_result": neural_result,
                "neural_decisions": str(len(neural_decisions)),
                "censused_loss_decisions": str(len(rows)),
                "first_losing_value_ply": first_value(
                    rows,
                    "ply",
                    lambda row: float(row["logged_value"]) <= args.losing_value_threshold,
                ),
                "first_safety_issue_ply": first_value(
                    rows,
                    "ply",
                    lambda row: row["neural_move_safety_pass"] == "False"
                    or row["opponent_forcing_reply_after_neural_move"] == "True",
                ),
                "first_direct_vs_mcts_divergence_ply": first_value(
                    rows,
                    "ply",
                    lambda row: row["direct_vs_mcts_divergence"] == "True",
                ),
                "first_opponent_forcing_reply_before_ply": first_value(
                    rows,
                    "ply",
                    lambda row: row["opponent_forcing_reply_exists_before"] == "True",
                ),
                "parse_warnings": " | ".join(game.parse_warnings) if game.parse_warnings else "NA",
            }
        )
    return summary


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def recommendation(census_rows: list[dict[str, str]], summary_rows: list[dict[str, str]]) -> tuple[str, str]:
    loss_games = [row for row in summary_rows if row["neural_result"] == "loss"]
    if len(loss_games) < 10:
        return (
            "D",
            "Need more diverse corpus before training. The current census is a pipeline seed, not enough evidence for Candidate K.",
        )
    safety_rows = [
        row for row in census_rows
        if row["neural_move_safety_pass"] == "False"
        or row["opponent_forcing_reply_after_neural_move"] == "True"
    ]
    low_policy_rows = [
        row for row in census_rows
        if row["neural_move_policy_rank"].isdigit() and int(row["neural_move_policy_rank"]) > 10
    ]
    losing_value_rows = [row for row in census_rows if float(row["logged_value"]) <= -0.50]
    if len(safety_rows) >= max(3, len(loss_games) // 2):
        return ("C", "Search/safety bug likely; safety failures recur across the loss corpus.")
    if len(low_policy_rows) >= max(5, len(loss_games)):
        return ("A", "Policy distillation dataset is warranted; chosen moves repeatedly have poor policy support.")
    if len(losing_value_rows) >= max(5, len(loss_games)):
        return ("B", "Value-ranking dataset is warranted; losses repeatedly enter strongly negative value states.")
    return ("D", "Need more diverse corpus before training; no single failure mode is dominant yet.")


def write_report(path: Path, args: argparse.Namespace, census_rows: list[dict[str, str]], summary_rows: list[dict[str, str]]) -> None:
    total_games = len(summary_rows)
    result_counts = Counter(row["neural_result"] for row in summary_rows)
    loss_rows = [row for row in census_rows if row["decision_engine_result"] == "loss"]
    move_clusters = Counter(row["neural_move"] for row in loss_rows)
    pattern_clusters = Counter(row["local_pattern_5x5_current_pov"] for row in loss_rows)
    rec_code, rec_text = recommendation(census_rows, summary_rows)

    lines = [
        "# 15x15 failure corpus census",
        "",
        "## Scope",
        "",
        "- corpus source: existing debug logs passed to the census script",
        f"- logs parsed: {len(args.logs)}",
        f"- baseline C weights for policy/value census: `{args.weights}`",
        f"- lightweight parse mode: `{args.skip_safety}`",
        "- no training, C export, promotion, or Rapfi smoke was run by this census step.",
        "",
        "## Summary Metrics",
        "",
        f"- total games parsed: {total_games}",
        f"- neural wins: {result_counts.get('win', 0)}",
        f"- neural losses: {result_counts.get('loss', 0)}",
        f"- neural draws: {result_counts.get('draw', 0)}",
        f"- censused neural loss decisions: {len(loss_rows)}",
        "- safety/forcing and C-policy enrichment were skipped; related fields are `NA`." if args.skip_safety else "- safety/forcing and C-policy enrichment were enabled.",
        "",
        "## Per-Game Summary",
        "",
    ]
    if summary_rows:
        lines.extend(
            [
                "| game | result | neural result | decisions | first losing value | first safety issue | first direct-vs-MCTS divergence | first forcing reply before |",
                "|---|---|---|---:|---:|---:|---:|---:|",
            ]
        )
        for row in summary_rows:
            lines.append(
                "| {game_id} | {game_result} | {neural_result} | {censused_loss_decisions} | "
                "{first_losing_value_ply} | {first_safety_issue_ply} | {first_direct_vs_mcts_divergence_ply} | "
                "{first_opponent_forcing_reply_before_ply} |".format(**row)
            )
    else:
        lines.append("No games were parsed.")

    lines.extend(["", "## Repeated Move Clusters", ""])
    if move_clusters:
        lines.extend(["| neural move | count |", "|---:|---:|"])
        for move, amount in move_clusters.most_common(args.top_k_clusters):
            lines.append(f"| {move} | {amount} |")
    else:
        lines.append("No loss-decision move clusters yet.")

    lines.extend(["", "## Repeated Local Pattern Clusters", ""])
    if pattern_clusters:
        lines.extend(["| rank | count | pattern |", "|---:|---:|---|"])
        for idx, (pattern, amount) in enumerate(pattern_clusters.most_common(args.top_k_clusters), start=1):
            lines.append(f"| {idx} | {amount} | `{pattern}` |")
    else:
        lines.append("No local pattern clusters yet.")

    lines.extend(
        [
            "",
            "## Opening Diversity",
            "",
            "The corpus runner supports c-gomoku-cli opening diversity through `-openings`, `-repeat`, and `-transform`.",
            "A small default 15x15 offset-opening file is provided at `analysis/integration_eval/15x15_corpus_openings_offset.txt`.",
            "If the runner is invoked with `--no-openings` or the opening file is missing, collection can fall back to deterministic empty-board starts.",
            "",
            "## Recommendation",
            "",
            f"Recommendation {rec_code}: {rec_text}",
            "",
            "Do not train Candidate K yet unless this recommendation changes after a larger, diverse corpus is collected.",
            "",
            "## Outputs",
            "",
            f"- failure census CSV: `{args.output_csv}`",
            f"- game summary CSV: `{args.summary_csv}`",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    args._decisions_processed = 0
    if not args.skip_safety:
        args.case_dir.mkdir(parents=True, exist_ok=True)
    games: list[Game] = []
    for log in args.logs:
        games.extend(parse_games(log, args.board_size, args.rapfi_substring))
    if args.max_games:
        games = games[: args.max_games]
    print(f"parsed logs: {len(args.logs)}", flush=True)
    print(f"parsed games: {len(games)}", flush=True)

    census_rows: list[dict[str, str]] = []
    for game in games:
        game_id = f"{game.log_path.stem}:g{game.game_number}"
        print(f"processing {game_id} decisions={len(game.decisions)}", flush=True)
        census_rows.extend(rows_for_loss_game(args, game))
        print(f"finished {game_id}; total decisions processed={args._decisions_processed}", flush=True)
        if args.max_decisions and args._decisions_processed >= args.max_decisions:
            print(f"stopping at --max-decisions={args.max_decisions}", flush=True)
            break
    summary_rows = make_summary_rows(args, games, census_rows)

    write_csv(args.output_csv, census_rows)
    write_csv(args.summary_csv, summary_rows)
    write_report(args.output_md, args, census_rows, summary_rows)

    print(f"wrote census rows: {len(census_rows)}")
    print(f"wrote {args.output_csv}")
    print(f"wrote {args.summary_csv}")
    print(f"wrote {args.output_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
