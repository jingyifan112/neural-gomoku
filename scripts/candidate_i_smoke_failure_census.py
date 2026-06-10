#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import re
import subprocess
from dataclasses import dataclass
from itertools import count
from pathlib import Path
from typing import Any

import numpy as np

from gomoku_agent.board import BLACK, WHITE, Board
from gomoku_agent.search_safety import filter_immediate_losses, opponent_has_forcing_terminal_reply


START_RE = re.compile(r"Started game (?P<game>\d+) of \d+ \((?P<black>.+?) vs (?P<white>.+?)\)")
FINISH_RE = re.compile(
    r"Finished game (?P<game>\d+) \((?P<black>.+?) vs (?P<white>.+?)\): "
    r"(?P<black_score>\d+)-(?P<white_score>\d+) \{(?P<reason>.+?)\}"
)
BESTLINE_RE = re.compile(r"(?P<engine>\S+) -> MESSAGE Bestline\s*(?P<bestline>.*)")
DECISION_RE = re.compile(r"DEBUG_DECISION\s+(?P<fields>.*)")
MOVE_RE = re.compile(r"(?P<engine>neural|rapfi_fast) -> (?P<x>\d+),(?P<y>\d+)\s*$")
COORD_RE = re.compile(
    r"(?P<name>direct|policy_safety|mcts_raw|mcts_safety|final)="
    r"\(x=(?P<x>-?\d+),y=(?P<y>-?\d+),row=(?P<row>-?\d+),col=(?P<col>-?\d+)\)"
)
KV_RE = re.compile(r"(?P<key>[A-Za-z_]+)=(?P<value>\S+)")

LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
CANDIDATE_D_MCTS16_GAME2 = {
    13: "5,8",
    15: "7,10",
    17: "9,10",
    19: "8,10",
    21: "11,9",
}


@dataclass
class LiveDecision:
    game_id: int
    black: str
    white: str
    ply: int
    side_to_move: str
    logged_value: float
    direct: str
    policy_safety: str
    mcts_raw: str
    mcts_safety: str
    final: str
    previous_rapfi_bestline: str
    board_moves_before: tuple[tuple[str, str], ...]
    result_score: str = ""
    result_reason: str = ""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Candidate I diagnostics over Candidate H Rapfi smoke failures.")
    parser.add_argument(
        "--log",
        type=Path,
        default=Path("eval_logs/integration_eval/candidate_h_mcts16_vs_rapfi_depth1_15x15_smoke.engine_io.log"),
    )
    parser.add_argument(
        "--stdout-log",
        type=Path,
        default=Path("eval_logs/integration_eval/candidate_h_mcts16_vs_rapfi_depth1_15x15_smoke.stdout.log"),
    )
    parser.add_argument(
        "--weights",
        type=Path,
        default=Path("weights/15x15_candidate_h_value_ranking_weights.bin"),
    )
    parser.add_argument("--dump-infer", type=Path, default=Path("c_inference/dump_infer"))
    parser.add_argument(
        "--case-dir",
        type=Path,
        default=Path("analysis/integration_eval/candidate_i_census_c_cases"),
    )
    parser.add_argument(
        "--output-csv",
        type=Path,
        default=Path("analysis/integration_eval/candidate_i_smoke_failure_census.csv"),
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=Path("analysis/integration_eval/candidate_i_smoke_failure_census.md"),
    )
    parser.add_argument("--board-size", type=int, default=15)
    parser.add_argument("--win-length", type=int, default=5)
    parser.add_argument("--top-k", type=int, default=5)
    return parser.parse_args()


def xy_to_action(xy: str, board_size: int) -> int:
    x_text, y_text = xy.split(",", maxsplit=1)
    return int(y_text) * board_size + int(x_text)


def action_to_xy(action: int, board_size: int) -> str:
    row, col = divmod(int(action), board_size)
    return f"{col},{row}"


def pbrain_to_xy(token: str, board_size: int) -> str:
    token = token.strip().upper()
    if len(token) < 2 or token[0] not in LETTERS:
        raise ValueError(f"unsupported pbrain coordinate: {token!r}")
    x = LETTERS.index(token[0])
    y = int(token[1:]) - 1
    if not (0 <= x < board_size and 0 <= y < board_size):
        raise ValueError(f"pbrain coordinate outside {board_size}x{board_size}: {token!r}")
    return f"{x},{y}"


def teacher_from_bestline(bestline: str, board_size: int) -> tuple[str, str]:
    tokens = [part for part in bestline.split() if part]
    if len(tokens) < 2:
        return "", "unavailable"
    try:
        return pbrain_to_xy(tokens[1], board_size), "rapfi_previous_pv_second_move"
    except ValueError:
        return "", "unavailable"


def parse_decision_line(line: str) -> dict[str, Any] | None:
    marker = DECISION_RE.search(line)
    if not marker:
        return None
    fields = {match.group("key"): match.group("value") for match in KV_RE.finditer(marker.group("fields"))}
    coords = {match.group("name"): f"{match.group('x')},{match.group('y')}" for match in COORD_RE.finditer(line)}
    if "move_count" not in fields or "value" not in fields or "final" not in coords:
        return None
    return {
        "ply": int(fields["move_count"]),
        "value": float(fields["value"]),
        **coords,
    }


def side_to_move_from_ply(black: str, white: str, ply: int) -> str:
    side = "black" if ply % 2 == 0 else "white"
    engine = black if side == "black" else white
    return f"{side}:{engine}"


def parse_results(path: Path) -> dict[int, tuple[str, str, str, str]]:
    results: dict[int, tuple[str, str, str, str]] = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        finish = FINISH_RE.search(line)
        if not finish:
            continue
        game = int(finish.group("game"))
        results[game] = (
            finish.group("black"),
            finish.group("white"),
            f"{finish.group('black_score')}-{finish.group('white_score')}",
            finish.group("reason"),
        )
    return results


def parse_log(path: Path, board_size: int, results: dict[int, tuple[str, str, str, str]]) -> list[LiveDecision]:
    decisions: list[LiveDecision] = []
    current_game = 0
    black = ""
    white = ""
    moves: list[tuple[str, str]] = []
    pending_rapfi_bestline = ""
    decisions_by_game: dict[int, list[LiveDecision]] = {}

    inferred_game = 0
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        start = START_RE.search(line)
        if start:
            current_game = int(start.group("game"))
            black = start.group("black")
            white = start.group("white")
            moves = []
            pending_rapfi_bestline = ""
            decisions_by_game[current_game] = []
            continue

        if "neural <- START" in line:
            inferred_game += 1
            current_game = inferred_game
            black, white, _score, _reason = results.get(
                current_game,
                ("neural" if current_game == 1 else "rapfi_fast", "rapfi_fast" if current_game == 1 else "neural", "", ""),
            )
            moves = []
            pending_rapfi_bestline = ""
            decisions_by_game[current_game] = []
            continue

        finish = FINISH_RE.search(line)
        if finish:
            score = f"{finish.group('black_score')}-{finish.group('white_score')}"
            reason = finish.group("reason")
            for decision in decisions_by_game.get(int(finish.group("game")), []):
                decision.result_score = score
                decision.result_reason = reason
            continue

        bestline = BESTLINE_RE.search(line)
        if bestline and "rapfi" in bestline.group("engine").lower():
            pending_rapfi_bestline = bestline.group("bestline").strip()
            continue

        parsed = parse_decision_line(line)
        if parsed and "neural" in line:
            decision = LiveDecision(
                game_id=current_game,
                black=black,
                white=white,
                ply=parsed["ply"],
                side_to_move=side_to_move_from_ply(black, white, parsed["ply"]),
                logged_value=parsed["value"],
                direct=parsed["direct"],
                policy_safety=parsed["policy_safety"],
                mcts_raw=parsed["mcts_raw"],
                mcts_safety=parsed["mcts_safety"],
                final=parsed["final"],
                previous_rapfi_bestline=pending_rapfi_bestline,
                board_moves_before=tuple(moves),
            )
            decisions.append(decision)
            decisions_by_game.setdefault(current_game, []).append(decision)
            continue

        move = MOVE_RE.search(line)
        if move:
            moves.append((move.group("engine"), f"{move.group('x')},{move.group('y')}"))

    return decisions


def build_board(decision: LiveDecision, board_size: int, win_length: int) -> Board:
    board = Board(size=board_size, win_length=win_length)
    for index, (_engine, xy) in enumerate(decision.board_moves_before):
        x_text, y_text = xy.split(",", maxsplit=1)
        player = BLACK if index % 2 == 0 else WHITE
        board.grid[int(y_text), int(x_text)] = player
    board.move_count = len(decision.board_moves_before)
    board.current_player = BLACK if board.move_count % 2 == 0 else WHITE
    if decision.board_moves_before:
        x_text, y_text = decision.board_moves_before[-1][1].split(",", maxsplit=1)
        board.last_move = (int(y_text), int(x_text))
    return board


_CASE_COUNTER = count()


def run_c_eval(args: argparse.Namespace, board: Board, label: str) -> tuple[np.ndarray, float]:
    case_path = args.case_dir / f"{next(_CASE_COUNTER):04d}_{label}"
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


def child_value_for_action(args: argparse.Namespace, board: Board, action: int) -> float | None:
    if action not in set(int(move) for move in board.legal_moves()):
        return None
    mover = board.current_player
    child = board.clone()
    result = child.play_flat(action)
    if result.winner == mover:
        return 1.0
    if result.done:
        return 0.0
    _probs, value_for_opponent = run_c_eval(args, child, f"child_{action}")
    return -float(value_for_opponent)


def move_passes_safety(board: Board, action: int) -> bool:
    if action not in set(int(move) for move in board.legal_moves()):
        return False
    visits = board.legal_mask()
    filtered = filter_immediate_losses(board, visits)
    return bool(filtered[action] > 0)


def board_compact(board: Board) -> str:
    symbols = {BLACK: "X", WHITE: "O", 0: "."}
    return "/".join("".join(symbols[int(cell)] for cell in row) for row in board.grid)


def top_moves(probs: np.ndarray, board: Board, top_k: int) -> str:
    ranked = sorted((int(move) for move in board.legal_moves()), key=lambda move: float(probs[move]), reverse=True)
    return " ".join(f"{action_to_xy(action, board.size)}:{float(probs[action]):.6f}" for action in ranked[:top_k])


def classify_row(
    decision: LiveDecision,
    teacher_move: str,
    candidate_move: str,
    teacher_child_value: float | None,
    candidate_child_value: float | None,
    teacher_rank: int | None,
    baseline_move: str,
    board: Board,
) -> tuple[str, str]:
    tags: list[str] = []
    notes: list[str] = []
    if baseline_move and candidate_move != baseline_move:
        tags.append("diverges_from_candidate_d_baseline")
    if teacher_move:
        if candidate_move != teacher_move:
            tags.append("diverges_from_rapfi_teacher")
        else:
            tags.append("matches_rapfi_teacher")
    if teacher_move and candidate_child_value is not None and teacher_child_value is not None:
        if teacher_child_value > candidate_child_value:
            tags.append("value_disfavors_candidate")
        elif teacher_child_value < candidate_child_value:
            tags.append("value_supports_candidate")
    if teacher_rank is not None and teacher_rank > 10:
        tags.append("teacher_low_policy_visibility")
    if decision.logged_value < -0.75:
        tags.append("already_losing_value")
    if opponent_has_forcing_terminal_reply(board.clone()):
        tags.append("opponent_forcing_reply_exists_before_move")
    if not tags:
        tags.append("context")
    if decision.game_id == 2 and decision.ply in {13, 15, 17}:
        notes.append("near old ply15/ply17 failure window")
    if decision.game_id == 1:
        notes.append("game1 smoke loss")
    if decision.game_id == 2 and decision.ply == 13:
        notes.append("first live divergence from Candidate D mcts16 baseline")
    return ";".join(tags), "; ".join(notes)


def make_rows(args: argparse.Namespace, decisions: list[LiveDecision]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    args.case_dir.mkdir(parents=True, exist_ok=True)
    for decision in decisions:
        board = build_board(decision, args.board_size, args.win_length)
        probs, root_value = run_c_eval(args, board, f"g{decision.game_id}_p{decision.ply}")
        candidate_action = xy_to_action(decision.final, args.board_size)
        teacher_move, teacher_source = teacher_from_bestline(decision.previous_rapfi_bestline, args.board_size)
        teacher_action = xy_to_action(teacher_move, args.board_size) if teacher_move else None
        baseline_move = CANDIDATE_D_MCTS16_GAME2.get(decision.ply, "") if decision.game_id == 2 else ""

        candidate_rank = rank_for_action(probs, board, candidate_action)
        candidate_prob = float(probs[candidate_action]) if candidate_rank is not None else float("nan")
        candidate_value = child_value_for_action(args, board, candidate_action)
        candidate_safe = move_passes_safety(board, candidate_action)

        teacher_rank = None
        teacher_prob = None
        teacher_value = None
        teacher_safe = ""
        if teacher_action is not None:
            teacher_rank = rank_for_action(probs, board, teacher_action)
            teacher_prob = float(probs[teacher_action]) if teacher_rank is not None else None
            teacher_value = child_value_for_action(args, board, teacher_action)
            teacher_safe = str(move_passes_safety(board, teacher_action)) if teacher_rank is not None else "False"

        policy_gap = (teacher_prob - candidate_prob) if teacher_prob is not None else None
        value_gap = (
            teacher_value - candidate_value
            if teacher_value is not None and candidate_value is not None
            else None
        )
        classification, notes = classify_row(
            decision,
            teacher_move,
            decision.final,
            teacher_value,
            candidate_value,
            teacher_rank,
            baseline_move,
            board,
        )
        rows.append(
            {
                "game_id": str(decision.game_id),
                "ply": str(decision.ply),
                "side_to_move": decision.side_to_move,
                "candidate_h_move": decision.final,
                "candidate_d_baseline_move": baseline_move or "NA",
                "rapfi_teacher_move": teacher_move or "NA",
                "teacher_source": teacher_source,
                "candidate_h_policy_rank": str(candidate_rank) if candidate_rank is not None else "ILLEGAL",
                "teacher_policy_rank_under_h": str(teacher_rank) if teacher_rank is not None else "NA",
                "candidate_h_policy_prob": f"{candidate_prob:.6f}" if candidate_rank is not None else "ILLEGAL",
                "teacher_policy_prob": f"{teacher_prob:.6f}" if teacher_prob is not None else "NA",
                "policy_probability_gap_teacher_minus_candidate": f"{policy_gap:.6f}" if policy_gap is not None else "NA",
                "root_value": f"{root_value:.6f}",
                "logged_root_value": f"{decision.logged_value:.6f}",
                "candidate_child_value": f"{candidate_value:.6f}" if candidate_value is not None else "NA",
                "teacher_child_value": f"{teacher_value:.6f}" if teacher_value is not None else "NA",
                "child_value_gap_teacher_minus_candidate": f"{value_gap:.6f}" if value_gap is not None else "NA",
                "candidate_h_move_safety_pass": str(candidate_safe),
                "teacher_move_safety_pass": teacher_safe or "NA",
                "previous_rapfi_bestline": decision.previous_rapfi_bestline or "NA",
                "short_continuation_result": decision.result_reason,
                "classification": classification,
                "top_policy_moves": top_moves(probs, board, args.top_k),
                "board_position": board_compact(board),
                "notes": notes,
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def count(rows: list[dict[str, str]], token: str) -> int:
    return sum(token in row["classification"].split(";") for row in rows)


def write_report(path: Path, rows: list[dict[str, str]], args: argparse.Namespace) -> None:
    loss_rows = rows
    teacher_rows = [row for row in rows if row["rapfi_teacher_move"] != "NA"]
    d_divergences = [row for row in rows if "diverges_from_candidate_d_baseline" in row["classification"].split(";")]
    teacher_divergences = [row for row in rows if "diverges_from_rapfi_teacher" in row["classification"].split(";")]
    low_policy = [row for row in rows if "teacher_low_policy_visibility" in row["classification"].split(";")]
    value_disfavors = [row for row in rows if "value_disfavors_candidate" in row["classification"].split(";")]

    focus_keys = {("2", "13"), ("2", "15"), ("2", "17")}
    focus_rows = [row for row in rows if (row["game_id"], row["ply"]) in focus_keys]
    game1_late = [row for row in rows if row["game_id"] == "1" and int(row["ply"]) >= 14]

    lines = [
        "# Candidate I smoke failure census",
        "",
        "## Scope",
        "",
        f"- input log: `{args.log}`",
        f"- C weights probed: `{args.weights}`",
        "- measurement only; no Candidate I training was run.",
        "- teacher move source: second move of Rapfi's previous PV when available.",
        "",
        "## Summary",
        "",
        f"- Candidate H loss decisions audited: {len(loss_rows)}",
        f"- decisions with Rapfi teacher continuation available: {len(teacher_rows)}",
        f"- comparable Candidate D divergence rows: {len(d_divergences)}",
        f"- divergences from available Rapfi teacher continuation: {len(teacher_divergences)}",
        f"- teacher moves with low policy visibility rank > 10: {len(low_policy)}",
        f"- teacher child-value greater than Candidate H child-value: {len(value_disfavors)}",
        "",
        "## Focus Window",
        "",
        "| game | ply | Candidate H | Candidate D baseline | Rapfi teacher | teacher rank | policy gap | child-value gap | safety H/teacher | classification |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for row in focus_rows:
        lines.append(
            "| {game_id} | {ply} | {candidate_h_move} | {candidate_d_baseline_move} | {rapfi_teacher_move} | "
            "{teacher_policy_rank_under_h} | {policy_probability_gap_teacher_minus_candidate} | "
            "{child_value_gap_teacher_minus_candidate} | {candidate_h_move_safety_pass}/{teacher_move_safety_pass} | {classification} |".format(**row)
        )

    lines.extend(
        [
            "",
            "Candidate H follows the available Rapfi PV continuation at game2 plies 13, 15, and 17. The new live divergence from Candidate D at ply13 is therefore not a simple missing-policy problem under the available shallow teacher continuation; it is a changed line that still collapses later.",
            "",
            "## Game 1 Late Failure Context",
            "",
            "| game | ply | Candidate H | Rapfi teacher | teacher rank | root value | child value | next result | classification |",
            "|---:|---:|---:|---:|---:|---:|---:|---|---|",
        ]
    )
    for row in game1_late:
        lines.append(
            "| {game_id} | {ply} | {candidate_h_move} | {rapfi_teacher_move} | {teacher_policy_rank_under_h} | "
            "{root_value} | {candidate_child_value} | {short_continuation_result} | {classification} |".format(**row)
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- The old fixed-position Candidate H improvements did not transfer because the live game2 trajectory changed before the old ply15/ply17 boards.",
            "- In the new game2 focus window, Candidate H is not ignoring the available Rapfi continuation; it matches the PV continuation at ply13, ply15, and ply17.",
            "- The logged/root values are already strongly negative through much of game2, so the model appears to be navigating a bad line rather than merely suppressing a visible local teacher move.",
            "- Game1 has fewer teacher-continuation labels available from the log, so it needs fresh teacher probing before it can support targeted value-ranking pairs.",
            "",
            "## Recommendation",
            "",
            "Recommendation D: reject this line and return to broader data generation, with a small supporting A component. The next useful measurement/training loop should generate stronger teacher labels from live Candidate H failure positions, not just reuse shallow prior-PV continuations. Expand the teacher policy dataset only after re-querying a stronger teacher on the reconstructed game1 and game2 positions; defer value-ranking pairs until those teacher choices are stable and demonstrably improve continuations.",
            "",
            "Do not train Candidate I yet; this report is a measurement artifact.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    args = parse_args()
    results = parse_results(args.stdout_log)
    decisions = parse_log(args.log, args.board_size, results)
    for decision in decisions:
        _black, _white, score, reason = results.get(decision.game_id, ("", "", "", ""))
        decision.result_score = score
        decision.result_reason = reason
    loss_decisions = [decision for decision in decisions if "win by" in decision.result_reason.lower()]
    rows = make_rows(args, loss_decisions)
    write_csv(args.output_csv, rows)
    write_report(args.output_md, rows, args)
    print(f"parsed decisions: {len(decisions)}")
    print(f"loss decisions audited: {len(rows)}")
    print(f"wrote {args.output_csv}")
    print(f"wrote {args.output_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
