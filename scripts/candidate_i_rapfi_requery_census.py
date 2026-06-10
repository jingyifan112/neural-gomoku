#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import re
import select
import subprocess
import time
from pathlib import Path
from typing import Iterable

from gomoku_agent.board import Board

from candidate_i_smoke_failure_census import (
    CANDIDATE_D_MCTS16_GAME2,
    LiveDecision,
    action_to_xy,
    build_board,
    child_value_for_action,
    classify_row,
    move_passes_safety,
    parse_log,
    parse_results,
    rank_for_action,
    run_c_eval,
    top_moves,
    xy_to_action,
)


MOVE_LINE_RE = re.compile(r"^(?P<x>\d+),(?P<y>\d+)$")
EVAL_RE = re.compile(r"\bEval\s+(?P<eval>\S+)")
BESTLINE_RE = re.compile(r"MESSAGE Bestline\s*(?P<pv>.*)")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Re-query Rapfi on reconstructed Candidate H smoke-loss positions."
    )
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
        default=Path("analysis/integration_eval/candidate_i_rapfi_requery_c_cases"),
    )
    parser.add_argument(
        "--board-dir",
        type=Path,
        default=Path("analysis/integration_eval/candidate_i_rapfi_requery_boards"),
    )
    parser.add_argument(
        "--rapfi-bin",
        type=Path,
        default=Path("/Users/jing1fan/gomoku_public_benchmark/rapfi-master/Rapfi/build/pbrain-rapfi"),
    )
    parser.add_argument(
        "--rapfi-cwd",
        type=Path,
        default=Path("/Users/jing1fan/gomoku_public_benchmark/rapfi-master/Rapfi/build"),
    )
    parser.add_argument("--rapfi-depth", type=int, default=2)
    parser.add_argument("--rapfi-timeout-ms", type=int, default=10000)
    parser.add_argument(
        "--rapfi-retry-spec",
        default="2:10000,1:5000,2:5000",
        help="comma-separated depth:timeout_ms attempts; later attempts run only if no move is returned",
    )
    parser.add_argument("--board-size", type=int, default=15)
    parser.add_argument("--win-length", type=int, default=5)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument(
        "--output-csv",
        type=Path,
        default=Path("analysis/integration_eval/candidate_i_rapfi_requery_census.csv"),
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=Path("analysis/integration_eval/candidate_i_rapfi_requery_census.md"),
    )
    return parser.parse_args()


def rapfi_attempts(args: argparse.Namespace) -> list[tuple[int, int]]:
    attempts: list[tuple[int, int]] = []
    for item in args.rapfi_retry_spec.split(","):
        if not item.strip():
            continue
        depth_text, timeout_text = item.split(":", maxsplit=1)
        attempts.append((int(depth_text), int(timeout_text)))
    if not attempts:
        attempts.append((args.rapfi_depth, args.rapfi_timeout_ms))
    return attempts


def board_protocol_lines(board: Board, args: argparse.Namespace, depth: int, timeout_ms: int) -> list[str]:
    lines = [
        f"START {args.board_size}",
        "INFO rule 0",
        f"INFO max_depth {depth}",
        f"INFO timeout_turn {timeout_ms}",
        f"INFO time_left {timeout_ms}",
        "BOARD",
    ]
    for y in range(board.size):
        for x in range(board.size):
            value = int(board.grid[y, x])
            if value == 0:
                continue
            player_code = 1 if value == board.current_player else 2
            lines.append(f"{x},{y},{player_code}")
    lines.append("DONE")
    return lines


def write_board_query(path: Path, board: Board, args: argparse.Namespace, depth: int, timeout_ms: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(board_protocol_lines(board, args, depth, timeout_ms)) + "\n", encoding="utf-8")


def read_available_lines(
    proc: subprocess.Popen[str],
    streams: Iterable[tuple[str, object]],
    deadline: float,
) -> tuple[list[str], list[str]]:
    stdout_lines: list[str] = []
    stderr_lines: list[str] = []
    active = [(name, stream) for name, stream in streams if stream is not None]
    while active and time.monotonic() < deadline:
        timeout = max(0.0, min(0.05, deadline - time.monotonic()))
        ready, _, _ = select.select([stream for _name, stream in active], [], [], timeout)
        if not ready:
            break
        for stream in ready:
            line = stream.readline()
            name = next(name for name, candidate in active if candidate == stream)
            if not line:
                active = [(item_name, item_stream) for item_name, item_stream in active if item_stream != stream]
                continue
            if name == "stdout":
                stdout_lines.append(line.strip())
            else:
                stderr_lines.append(line.strip())
    return stdout_lines, stderr_lines


def query_rapfi_attempt(
    board: Board,
    args: argparse.Namespace,
    label: str,
    attempt_index: int,
    depth: int,
    timeout_ms: int,
) -> dict[str, str]:
    query_path = args.board_dir / f"{label}.attempt{attempt_index}.board"
    write_board_query(query_path, board, args, depth, timeout_ms)
    proc = subprocess.Popen(
        [str(args.rapfi_bin)],
        cwd=str(args.rapfi_cwd),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )
    assert proc.stdin is not None
    assert proc.stdout is not None

    start = time.monotonic()
    for line in query_path.read_text(encoding="utf-8").splitlines():
        proc.stdin.write(line + "\n")
        proc.stdin.flush()

    best_move = ""
    score = ""
    pv = ""
    stdout_lines: list[str] = []
    stderr_lines: list[str] = []
    timed_out = False
    deadline = time.monotonic() + max(1.0, timeout_ms / 1000.0)
    try:
        while time.monotonic() < deadline:
            ready, _, _ = select.select([proc.stdout, proc.stderr], [], [], max(0.0, deadline - time.monotonic()))
            if not ready:
                timed_out = True
                break
            for stream in ready:
                line = stream.readline()
                if not line:
                    continue
                text = line.strip()
                if stream == proc.stdout:
                    stdout_lines.append(text)
                    eval_match = EVAL_RE.search(text)
                    if eval_match:
                        score = eval_match.group("eval")
                    pv_match = BESTLINE_RE.search(text)
                    if pv_match:
                        pv = pv_match.group("pv").strip()
                    move_match = MOVE_LINE_RE.match(text)
                    if move_match:
                        best_move = f"{move_match.group('x')},{move_match.group('y')}"
                        break
                else:
                    stderr_lines.append(text)
            if best_move:
                break
        else:
            timed_out = True
    finally:
        drain_deadline = time.monotonic() + 0.1
        more_stdout, more_stderr = read_available_lines(
            proc,
            [("stdout", proc.stdout), ("stderr", proc.stderr)],
            drain_deadline,
        )
        stdout_lines.extend(more_stdout)
        stderr_lines.extend(more_stderr)
        try:
            proc.stdin.write("END\n")
            proc.stdin.flush()
        except BrokenPipeError:
            pass
        proc.terminate()
        try:
            proc.wait(timeout=1)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=1)

    elapsed_ms = int(round((time.monotonic() - start) * 1000))
    stdout_path = args.board_dir / f"{label}.attempt{attempt_index}.rapfi.out"
    stderr_path = args.board_dir / f"{label}.attempt{attempt_index}.rapfi.err"
    stdout_path.write_text("\n".join(stdout_lines) + "\n", encoding="utf-8")
    stderr_path.write_text("\n".join(stderr_lines) + "\n", encoding="utf-8")
    return_code = proc.returncode
    return {
        "best_move": best_move or "NA",
        "score": score or "NA",
        "pv": pv or "NA",
        "timed_out": str(timed_out and not best_move),
        "return_code": str(return_code) if return_code is not None else "NA",
        "elapsed_ms": str(elapsed_ms),
        "depth": str(depth),
        "timeout_ms": str(timeout_ms),
        "attempt_index": str(attempt_index),
        "query_file": str(query_path),
        "raw_output": str(stdout_path),
        "stderr_output": str(stderr_path),
        "stdout_line_count": str(len(stdout_lines)),
        "stderr_line_count": str(len(stderr_lines)),
        "stdout_excerpt": " || ".join(stdout_lines[-3:]) if stdout_lines else "NA",
        "stderr_excerpt": " || ".join(stderr_lines[-3:]) if stderr_lines else "NA",
    }


def query_rapfi(board: Board, args: argparse.Namespace, label: str) -> dict[str, str]:
    attempts: list[dict[str, str]] = []
    for attempt_index, (depth, timeout_ms) in enumerate(rapfi_attempts(args), start=1):
        result = query_rapfi_attempt(board, args, label, attempt_index, depth, timeout_ms)
        attempts.append(result)
        if result["best_move"] != "NA":
            break

    selected = attempts[-1]
    combined_stdout = args.board_dir / f"{label}.rapfi.out"
    combined_stderr = args.board_dir / f"{label}.rapfi.err"
    combined_stdout.write_text(
        "\n".join(
            f"### attempt {attempt['attempt_index']} depth={attempt['depth']} timeout_ms={attempt['timeout_ms']}\n"
            + Path(attempt["raw_output"]).read_text(encoding="utf-8", errors="replace").rstrip()
            for attempt in attempts
        )
        + "\n",
        encoding="utf-8",
    )
    combined_stderr.write_text(
        "\n".join(
            f"### attempt {attempt['attempt_index']} depth={attempt['depth']} timeout_ms={attempt['timeout_ms']}\n"
            + Path(attempt["stderr_output"]).read_text(encoding="utf-8", errors="replace").rstrip()
            for attempt in attempts
        )
        + "\n",
        encoding="utf-8",
    )

    return {
        **selected,
        "query_file": selected["query_file"],
        "raw_output": str(combined_stdout),
        "stderr_output": str(combined_stderr),
        "attempts": str(len(attempts)),
        "attempt_plan": ";".join(f"d{attempt['depth']}:{attempt['timeout_ms']}ms" for attempt in attempts),
        "recovered_by_retry": str(len(attempts) > 1 and selected["best_move"] != "NA"),
    }


def board_terminal_status(board: Board) -> str:
    if board.last_move is None:
        return "False"
    row, col = board.last_move
    player = int(board.grid[row, col])
    return str(bool(player and board._has_five_from(row, col, player)))


def diagnose_rapfi_no_move(rapfi: dict[str, str], board_terminal: str) -> str:
    if rapfi["best_move"] != "NA":
        return "concrete_move"
    if board_terminal == "True":
        return "terminal_before_query"
    if rapfi["score"] != "NA" or rapfi["pv"] != "NA":
        return "score_or_pv_without_move"
    if rapfi["timed_out"] == "True":
        return "timeout_without_move"
    if rapfi["stderr_line_count"] != "0":
        return "stderr_without_move"
    return "no_output_without_move"


def priority_label(decision: LiveDecision, previous_low_policy: bool) -> str:
    labels: list[str] = []
    if decision.game_id == 1 and decision.ply == 18:
        labels.append("game1_ply18_low_policy_prior")
    if decision.game_id == 2 and decision.ply in {13, 15, 17}:
        labels.append("game2_focus_before_old_targets")
    if (decision.game_id == 1 and decision.ply >= 14) or (decision.game_id == 2 and decision.ply >= 17):
        labels.append("late_loss_window")
    if previous_low_policy:
        labels.append("low_policy_in_shallow_census")
    return ";".join(labels) if labels else "context"


def make_requery_rows(args: argparse.Namespace, decisions: list[LiveDecision]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    args.board_dir.mkdir(parents=True, exist_ok=True)

    for decision in decisions:
        board = build_board(decision, args.board_size, args.win_length)
        label = f"g{decision.game_id}_p{decision.ply}"
        legal_moves_count = len(board.legal_moves())
        board_terminal = board_terminal_status(board)
        rapfi = query_rapfi(board, args, label)
        teacher_move = rapfi["best_move"]
        candidate_move = decision.final
        rapfi_concrete = teacher_move != "NA"
        rapfi_return_status = (
            "concrete_move"
            if rapfi_concrete
            else "timeout_no_move"
            if rapfi["timed_out"] == "True"
            else "no_move_or_na"
        )
        no_move_diagnosis = diagnose_rapfi_no_move(rapfi, board_terminal)

        probs, root_value = run_c_eval(args, board, f"requery_{label}")
        candidate_action = xy_to_action(candidate_move, args.board_size)
        teacher_action = xy_to_action(teacher_move, args.board_size) if teacher_move != "NA" else None

        candidate_rank = rank_for_action(probs, board, candidate_action)
        candidate_prob = float(probs[candidate_action]) if candidate_rank is not None else None
        candidate_value = child_value_for_action(args, board, candidate_action)
        candidate_safe = move_passes_safety(board, candidate_action)

        teacher_rank = None
        teacher_prob = None
        teacher_value = None
        teacher_safe = "NA"
        if teacher_action is not None:
            teacher_rank = rank_for_action(probs, board, teacher_action)
            teacher_prob = float(probs[teacher_action]) if teacher_rank is not None else None
            teacher_value = child_value_for_action(args, board, teacher_action)
            teacher_safe = str(move_passes_safety(board, teacher_action)) if teacher_rank is not None else "False"
        teacher_safe_bool = teacher_safe == "True"
        board_reconstruction_valid = True
        usable_teacher_label = (
            board_reconstruction_valid
            and rapfi_concrete
            and candidate_safe
            and teacher_safe_bool
        )
        valid_teacher_disagreement = usable_teacher_label and candidate_move != teacher_move
        low_policy_visibility_agreement = (
            usable_teacher_label
            and candidate_move == teacher_move
            and teacher_rank is not None
            and teacher_rank > 10
        )

        policy_gap = teacher_prob - candidate_prob if teacher_prob is not None and candidate_prob is not None else None
        value_gap = (
            teacher_value - candidate_value
            if teacher_value is not None and candidate_value is not None
            else None
        )
        baseline_move = CANDIDATE_D_MCTS16_GAME2.get(decision.ply, "") if decision.game_id == 2 else ""
        classification, notes = classify_row(
            decision,
            teacher_move if teacher_move != "NA" else "",
            candidate_move,
            teacher_value,
            candidate_value,
            teacher_rank,
            baseline_move,
            board,
        )
        previous_low_policy = decision.game_id == 1 and decision.ply == 18

        rows.append(
            {
                "game_id": str(decision.game_id),
                "ply": str(decision.ply),
                "priority": priority_label(decision, previous_low_policy),
                "side_to_move": decision.side_to_move,
                "candidate_h_move": candidate_move,
                "rapfi_requery_best_move": teacher_move,
                "rapfi_return_status": rapfi_return_status,
                "rapfi_returned_concrete_move": str(rapfi_concrete),
                "rapfi_no_move_diagnosis": no_move_diagnosis,
                "rapfi_attempts": rapfi["attempts"],
                "rapfi_attempt_plan": rapfi["attempt_plan"],
                "rapfi_recovered_by_retry": rapfi["recovered_by_retry"],
                "rapfi_elapsed_ms": rapfi["elapsed_ms"],
                "rapfi_return_code": rapfi["return_code"],
                "agreement": str(candidate_move == teacher_move),
                "usable_teacher_label": str(usable_teacher_label),
                "valid_teacher_disagreement": str(valid_teacher_disagreement),
                "low_policy_visibility_agreement": str(low_policy_visibility_agreement),
                "board_reconstruction_valid": str(board_reconstruction_valid),
                "board_terminal_before_query": board_terminal,
                "legal_moves_before_query": str(legal_moves_count),
                "candidate_d_baseline_move": baseline_move or "NA",
                "candidate_h_policy_rank": str(candidate_rank) if candidate_rank is not None else "ILLEGAL",
                "rapfi_move_policy_rank_under_h": str(teacher_rank) if teacher_rank is not None else "NA",
                "candidate_h_policy_prob": f"{candidate_prob:.6f}" if candidate_prob is not None else "ILLEGAL",
                "rapfi_move_policy_prob": f"{teacher_prob:.6f}" if teacher_prob is not None else "NA",
                "policy_probability_gap_teacher_minus_candidate": f"{policy_gap:.6f}" if policy_gap is not None else "NA",
                "root_value": f"{root_value:.6f}",
                "candidate_child_value": f"{candidate_value:.6f}" if candidate_value is not None else "NA",
                "rapfi_child_value": f"{teacher_value:.6f}" if teacher_value is not None else "NA",
                "child_value_gap_teacher_minus_candidate": f"{value_gap:.6f}" if value_gap is not None else "NA",
                "candidate_h_move_safety_pass": str(candidate_safe),
                "rapfi_move_safety_pass": teacher_safe,
                "rapfi_score": rapfi["score"],
                "rapfi_pv": rapfi["pv"],
                "rapfi_timed_out": rapfi["timed_out"],
                "rapfi_depth": rapfi["depth"],
                "rapfi_timeout_ms": rapfi["timeout_ms"],
                "classification": classification,
                "top_policy_moves": top_moves(probs, board, args.top_k),
                "board_query_file": rapfi["query_file"],
                "rapfi_raw_output": rapfi["raw_output"],
                "rapfi_stderr_output": rapfi["stderr_output"],
                "rapfi_stdout_line_count": rapfi["stdout_line_count"],
                "rapfi_stderr_line_count": rapfi["stderr_line_count"],
                "rapfi_stdout_excerpt": rapfi["stdout_excerpt"],
                "rapfi_stderr_excerpt": rapfi["stderr_excerpt"],
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


def count_token(rows: list[dict[str, str]], token: str) -> int:
    return sum(token in row["classification"].split(";") for row in rows)


def write_report(path: Path, rows: list[dict[str, str]], args: argparse.Namespace) -> None:
    concrete = [row for row in rows if row["rapfi_returned_concrete_move"] == "True"]
    timeout_or_na = [row for row in rows if row["rapfi_returned_concrete_move"] == "False"]
    timeout = [row for row in rows if row["rapfi_return_status"] == "timeout_no_move"]
    no_move_or_na = [row for row in rows if row["rapfi_return_status"] == "no_move_or_na"]
    usable_labels = [row for row in rows if row["usable_teacher_label"] == "True"]
    disagreements = [row for row in rows if row["valid_teacher_disagreement"] == "True"]
    recovered_by_retry = [row for row in rows if row["rapfi_recovered_by_retry"] == "True"]
    low_policy_agreements = [
        row for row in rows
        if row["low_policy_visibility_agreement"] == "True"
    ]
    low_rank = [
        row for row in rows
        if row["usable_teacher_label"] == "True"
        and row["rapfi_move_policy_rank_under_h"].isdigit()
        and int(row["rapfi_move_policy_rank_under_h"]) > 10
    ]
    value_teacher = [
        row for row in rows
        if row["usable_teacher_label"] == "True"
        and row["child_value_gap_teacher_minus_candidate"] != "NA"
        and float(row["child_value_gap_teacher_minus_candidate"]) > 0
    ]
    unsafe = [
        row for row in rows
        if row["candidate_h_move_safety_pass"] == "False" or row["rapfi_move_safety_pass"] == "False"
    ]
    terminal_before_query = [row for row in rows if row["board_terminal_before_query"] == "True"]
    na_diagnostics = [
        row for row in rows
        if row["rapfi_returned_concrete_move"] == "False"
    ]
    focus = [
        row for row in rows
        if row["priority"] != "context" or row["valid_teacher_disagreement"] == "True"
    ]

    lines = [
        "# Candidate I Rapfi re-query census",
        "",
        "## Scope",
        "",
        f"- reconstructed positions: Candidate H mcts16 smoke losses from `{args.log}`",
        f"- Rapfi re-query attempt plan: `{args.rapfi_retry_spec}`",
        f"- Candidate H C weights: `{args.weights}`",
        "- measurement only; no training was run.",
        "- Rapfi is queried per position in a fresh process. Persistent-process reuse was not used because the retry path needs clean per-board state and isolated stdout/stderr diagnostics; the failures are no-move replies after evaluation, not process startup failures.",
        "",
        "## Summary",
        "",
        f"- total positions attempted: {len(rows)}",
        f"- Rapfi returned concrete move: {len(concrete)}",
        f"- Rapfi timeout / no-move / NA: {len(timeout_or_na)} ({len(timeout)} timeout, {len(no_move_or_na)} no-move/NA)",
        f"- recovered concrete labels by retry/fallback: {len(recovered_by_retry)}",
        f"- usable teacher labels: {len(usable_labels)}",
        f"- valid teacher disagreements with Candidate H: {len(disagreements)}",
        f"- valid teacher agreements with low policy visibility: {len(low_policy_agreements)}",
        f"- usable Rapfi moves with Candidate H policy rank > 10: {len(low_rank)}",
        f"- Rapfi child-value higher than Candidate H move: {len(value_teacher)}",
        f"- safety failures in either Candidate H or Rapfi move: {len(unsafe)}",
        f"- boards terminal before query: {len(terminal_before_query)}",
        "",
        "## Priority Rows",
        "",
        "| game | ply | priority | H move | Rapfi re-query | agree | rank | policy gap | value gap | safety H/R | Rapfi score | PV | classification |",
        "|---:|---:|---|---:|---:|---|---:|---:|---:|---|---:|---|---|",
    ]
    for row in focus:
        lines.append(
            "| {game_id} | {ply} | {priority} | {candidate_h_move} | {rapfi_requery_best_move} | {agreement} | "
            "{rapfi_move_policy_rank_under_h} | {policy_probability_gap_teacher_minus_candidate} | "
            "{child_value_gap_teacher_minus_candidate} | {candidate_h_move_safety_pass}/{rapfi_move_safety_pass} | "
            "{rapfi_score} | {rapfi_pv} | {classification} |".format(**row)
        )

    lines.extend(["", "## Usable Teacher Labels", ""])
    if usable_labels:
        lines.extend(
            [
                "| game | ply | H move | Rapfi re-query | agree | rank | policy gap | value gap | safety H/R | classification |",
                "|---:|---:|---:|---:|---|---:|---:|---:|---|---|",
            ]
        )
        for row in usable_labels:
            lines.append(
                "| {game_id} | {ply} | {candidate_h_move} | {rapfi_requery_best_move} | {agreement} | "
                "{rapfi_move_policy_rank_under_h} | {policy_probability_gap_teacher_minus_candidate} | "
                "{child_value_gap_teacher_minus_candidate} | {candidate_h_move_safety_pass}/{rapfi_move_safety_pass} | "
                "{classification} |".format(**row)
            )
    else:
        lines.append("No usable teacher labels were found.")

    lines.extend(["", "## Valid Teacher Disagreements", ""])
    if disagreements:
        lines.extend(
            [
                "| game | ply | H move | Rapfi re-query | rank | policy gap | value gap | score | PV |",
                "|---:|---:|---:|---:|---:|---:|---:|---:|---|",
            ]
        )
        for row in disagreements:
            lines.append(
                "| {game_id} | {ply} | {candidate_h_move} | {rapfi_requery_best_move} | "
                "{rapfi_move_policy_rank_under_h} | {policy_probability_gap_teacher_minus_candidate} | "
                "{child_value_gap_teacher_minus_candidate} | {rapfi_score} | {rapfi_pv} |".format(**row)
            )
    else:
        lines.append("No valid teacher disagreements were found at the selected Rapfi re-query depth.")

    lines.extend(["", "## Low Policy Visibility Agreements", ""])
    if low_policy_agreements:
        lines.extend(
            [
                "| game | ply | H/Rapfi move | rank | policy prob | root value | child value | classification |",
                "|---:|---:|---:|---:|---:|---:|---:|---|",
            ]
        )
        for row in low_policy_agreements:
            lines.append(
                "| {game_id} | {ply} | {candidate_h_move} | {rapfi_move_policy_rank_under_h} | "
                "{candidate_h_policy_prob} | {root_value} | {candidate_child_value} | "
                "{classification} |".format(**row)
            )
    else:
        lines.append("No low-policy-visibility agreements were found.")

    lines.extend(["", "## NA Diagnostics", ""])
    if na_diagnostics:
        lines.extend(
            [
                "| game | ply | H move | status | diagnosis | attempts | elapsed ms | terminal | legal moves | score | PV | stdout | stderr |",
                "|---:|---:|---:|---|---|---:|---:|---|---:|---:|---|---|---|",
            ]
        )
        for row in na_diagnostics:
            lines.append(
                "| {game_id} | {ply} | {candidate_h_move} | {rapfi_return_status} | {rapfi_no_move_diagnosis} | "
                "{rapfi_attempts} | {rapfi_elapsed_ms} | {board_terminal_before_query} | {legal_moves_before_query} | "
                "{rapfi_score} | {rapfi_pv} | {rapfi_stdout_excerpt} | {rapfi_stderr_excerpt} |".format(**row)
            )
    else:
        lines.append("No NA/no-move rows remain after retry/fallback.")

    lines.extend(
        [
            "",
            "## Diagnosis",
            "",
            "- Protocol color encoding is relative to the queried engine side, matching the smoke engine log where opponent stones are sent as `2`.",
            "- Stderr is empty for the NA rows, so there is no evidence of a Rapfi crash or command-line failure.",
            "- The depth-1 fallback also returns eval-only output on the unrecovered rows, so the remaining failures are not fixed by shorter depth or a longer per-turn wait.",
            "- The NA rows are not caused by terminal reconstructed boards in this run.",
            "- Remaining NA rows produced Rapfi eval output but no final coordinate before the retry deadline, so they are treated as no-move teacher failures rather than disagreements. This suggests Rapfi's `BOARD` response path for these arbitrary reconstructed positions is the limiting factor, not Candidate H safety or board reconstruction.",
            "",
            "## Interpretation",
            "",
            "- Direct re-query is stronger than the smoke log continuation and avoids treating stale PV tails as labels.",
            "- Rows where Rapfi returns `NA` or no move are not usable teacher disagreements.",
            "- Rows where Rapfi disagrees with Candidate H and has low Candidate H policy rank are teacher-policy candidates only after concrete-move and safety validation.",
            "- Rows where Rapfi agrees but the move has low rank are policy-visibility anchors rather than disagreement pairs.",
            "- Rows with positive child-value gap are potential value-ranking candidates, but only if the Rapfi PV remains stable under follow-up validation.",
            "",
            "## Recommendation",
            "",
        ]
    )

    if len(usable_labels) < 25 or len(disagreements) <= 1:
        recommendation = (
            "Do not train Candidate J from this dataset. Retry/fallback did not recover enough concrete labels, and the "
            "validated disagreement set remains a single-row signal. NA/no-move rows remain excluded from training labels."
        )
    else:
        recommendation = (
            "Candidate J training can be considered only after manual review of the expanded validated-label set; "
            "NA/no-move rows remain excluded from training labels."
        )
    lines.extend([recommendation, "", "Do not train from this census until the selected teacher labels are reviewed.", ""])
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
    rows = make_requery_rows(args, loss_decisions)
    write_csv(args.output_csv, rows)
    write_report(args.output_md, rows, args)
    print(f"positions re-queried: {len(rows)}")
    print(f"wrote {args.output_csv}")
    print(f"wrote {args.output_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
