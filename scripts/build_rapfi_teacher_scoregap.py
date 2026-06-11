#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
import select
import subprocess
import time
from pathlib import Path
from typing import Iterable

from gomoku_agent.board import BLACK, WHITE, Board


SIDE_TO_PLAYER = {"black": BLACK, "white": WHITE}
STONE_TO_PLAYER = {"X": BLACK, "O": WHITE, ".": 0}

MOVE_LINE_RE = re.compile(r"^(?P<x>\d+),(?P<y>\d+)$")
EVAL_RE = re.compile(r"\bEval\s+(?P<eval>\S+)")
BESTLINE_RE = re.compile(r"(?:MESSAGE|message:)\s+Bestline\s*(?P<pv>.*)")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a Rapfi teacher score-gap benchmark for fixed 15x15 positions."
    )
    parser.add_argument(
        "--positions-json",
        type=Path,
        default=Path("analysis/public_benchmark_eval/corpus8_selected_board_snapshots.json"),
    )
    parser.add_argument(
        "--model-eval-csv",
        type=Path,
        default=Path("analysis/public_benchmark_eval/current_best_corpus8_selected_eval.csv"),
    )
    parser.add_argument(
        "--output-csv",
        type=Path,
        default=Path("analysis/public_benchmark_eval/rapfi_teacher_scoregap_corpus8_selected.csv"),
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=Path("analysis/public_benchmark_eval/rapfi_teacher_scoregap_corpus8_selected_report.md"),
    )
    parser.add_argument(
        "--board-dir",
        type=Path,
        default=Path("analysis/public_benchmark_eval/rapfi_teacher_scoregap_boards"),
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
    parser.add_argument("--board-size", type=int, default=15)
    parser.add_argument("--win-length", type=int, default=5)
    parser.add_argument("--rapfi-retry-spec", default="2:3000,1:2000")
    parser.add_argument("--limit", type=int, default=0, help="Debug limit. 0 means all positions.")
    return parser.parse_args()


def read_json(path: Path) -> list[dict[str, object]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a JSON list")
    return data


def read_csv_index(path: Path) -> dict[str, dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return {row["sample_id"]: row for row in rows}


def sample_id_for(position: dict[str, object]) -> str:
    return f"legacy_g{position['game_number']}_m{position['move_count']}"


def parse_board(snapshot: str, board_size: int, win_length: int, side_to_move: str) -> Board:
    board = Board(size=board_size, win_length=win_length)
    rows: list[list[str]] = []
    for line in snapshot.splitlines():
        tokens = line.strip().split()
        if len(tokens) == board_size and all(token in STONE_TO_PLAYER for token in tokens):
            rows.append(tokens)

    if len(rows) != board_size:
        raise ValueError(f"expected {board_size} board rows, found {len(rows)}")

    for row_index, row in enumerate(rows):
        for col_index, token in enumerate(row):
            board.grid[row_index, col_index] = STONE_TO_PLAYER[token]

    board.current_player = SIDE_TO_PLAYER[side_to_move]
    board.move_count = int((board.grid != 0).sum())
    board.last_move = None
    return board


def clone_board(board: Board) -> Board:
    other = Board(size=board.size, win_length=board.win_length)
    other.grid[:, :] = board.grid
    other.current_player = board.current_player
    other.move_count = board.move_count
    other.last_move = board.last_move
    return other


def parse_xy(move: str) -> tuple[int, int] | None:
    text = str(move).strip().strip('"')
    if not text or text == "NA" or "," not in text:
        return None
    x_text, y_text = text.split(",", maxsplit=1)
    try:
        return int(x_text), int(y_text)
    except ValueError:
        return None


def apply_move(board: Board, move: str) -> tuple[Board | None, str]:
    xy = parse_xy(move)
    if xy is None:
        return None, "invalid_move_format"
    x, y = xy
    if not (0 <= x < board.size and 0 <= y < board.size):
        return None, "move_out_of_bounds"
    if int(board.grid[y, x]) != 0:
        return None, "move_occupied"

    after = clone_board(board)
    player = after.current_player
    after.grid[y, x] = player
    after.last_move = (y, x)
    after.move_count += 1
    after.current_player = WHITE if player == BLACK else BLACK
    return after, "ok"


def rapfi_attempts(spec: str) -> list[tuple[int, int]]:
    attempts: list[tuple[int, int]] = []
    for item in spec.split(","):
        item = item.strip()
        if not item:
            continue
        depth_text, timeout_text = item.split(":", maxsplit=1)
        attempts.append((int(depth_text), int(timeout_text)))
    if not attempts:
        attempts.append((2, 3000))
    return attempts


def board_protocol_lines(board: Board, board_size: int, depth: int, timeout_ms: int) -> list[str]:
    lines = [
        f"START {board_size}",
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


def write_board_query(path: Path, board: Board, board_size: int, depth: int, timeout_ms: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(board_protocol_lines(board, board_size, depth, timeout_ms)) + "\n",
        encoding="utf-8",
    )


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
    write_board_query(query_path, board, args.board_size, depth, timeout_ms)

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
    assert proc.stderr is not None

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
            ready, _, _ = select.select(
                [proc.stdout, proc.stderr],
                [],
                [],
                max(0.0, min(0.25, deadline - time.monotonic())),
            )
            if not ready:
                continue

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

        if not best_move:
            timed_out = True
    finally:
        more_stdout, more_stderr = read_available_lines(
            proc,
            [("stdout", proc.stdout), ("stderr", proc.stderr)],
            time.monotonic() + 0.1,
        )
        stdout_lines.extend(more_stdout)
        stderr_lines.extend(more_stderr)

        try:
            proc.stdin.write("END\n")
            proc.stdin.flush()
        except BrokenPipeError:
            pass

        # Rapfi may emit the final Bestline and coordinate only after END.
        # Drain briefly after END before terminating, otherwise we keep only Eval lines.
        end_deadline = time.monotonic() + 1.0
        while time.monotonic() < end_deadline and not best_move:
            ready, _, _ = select.select(
                [proc.stdout, proc.stderr],
                [],
                [],
                max(0.0, min(0.1, end_deadline - time.monotonic())),
            )
            if not ready:
                continue

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

    return {
        "best_move": best_move or "NA",
        "score": score or "NA",
        "pv": pv or "NA",
        "timed_out": str(timed_out and not best_move),
        "return_code": str(proc.returncode) if proc.returncode is not None else "NA",
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
    for attempt_index, (depth, timeout_ms) in enumerate(rapfi_attempts(args.rapfi_retry_spec), start=1):
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


def parse_int_score(raw: str) -> int | None:
    try:
        return int(str(raw).strip())
    except ValueError:
        return None


def provisional_root_gap(before_score: str, after_score_next_player: str) -> str:
    before = parse_int_score(before_score)
    after_next = parse_int_score(after_score_next_player)
    if before is None or after_next is None:
        return "NA"
    # If Rapfi eval is side-to-move relative, after-model score is from the opponent's perspective.
    # Root-perspective after score is therefore approximately -after_next.
    # gap = best-root-score - model-root-score = before - (-after_next)
    return str(before + after_next)


def build_rows(args: argparse.Namespace) -> list[dict[str, str]]:
    positions = read_json(args.positions_json)
    if args.limit and args.limit > 0:
        positions = positions[: args.limit]

    model_rows = read_csv_index(args.model_eval_csv)
    args.board_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, str]] = []
    for index, position in enumerate(positions):
        sample_id = sample_id_for(position)
        model_row = model_rows.get(sample_id)
        if model_row is None:
            raise ValueError(f"missing model eval row for {sample_id}")

        side_to_move = str(position["side_to_move"])
        board = parse_board(
            str(position["board_snapshot_before_decision"]),
            args.board_size,
            args.win_length,
            side_to_move,
        )

        model_move = model_row["direct_policy_top_move"]
        before = query_rapfi(board, args, f"{index:03d}_{sample_id}_before")

        after_board, apply_status = apply_move(board, model_move)
        if after_board is None:
            after = {
                "best_move": "NA",
                "score": "NA",
                "pv": "NA",
                "timed_out": "False",
                "return_code": "NA",
                "elapsed_ms": "0",
                "depth": "NA",
                "timeout_ms": "NA",
                "attempt_index": "NA",
                "query_file": "NA",
                "raw_output": "NA",
                "stderr_output": "NA",
                "stdout_line_count": "0",
                "stderr_line_count": "0",
                "stdout_excerpt": "NA",
                "stderr_excerpt": "NA",
                "attempts": "0",
                "attempt_plan": "NA",
                "recovered_by_retry": "False",
            }
        else:
            after = query_rapfi(after_board, args, f"{index:03d}_{sample_id}_after_model")

        rapfi_before_concrete = before["best_move"] != "NA"
        rapfi_after_concrete = after["best_move"] != "NA"

        rows.append(
            {
                "sample_id": sample_id,
                "game_number": str(position["game_number"]),
                "move_count": str(position["move_count"]),
                "side_to_move": side_to_move,
                "labeled_failure_type": str(position.get("failure_type", "")),
                "logged_final": str(position.get("final", "")),
                "model_direct_move": model_move,
                "model_direct_prob": model_row["direct_policy_top_prob"],
                "model_value_estimate": model_row["model_value_estimate"],
                "model_direct_apply_status": apply_status,
                "rapfi_best_move_before": before["best_move"],
                "rapfi_eval_before": before["score"],
                "rapfi_pv_before": before["pv"],
                "rapfi_query_status_before": "concrete_move" if rapfi_before_concrete else "no_move_or_na",
                "model_matches_rapfi_best_before": str(model_move == before["best_move"]),
                "rapfi_best_move_after_model": after["best_move"],
                "rapfi_eval_after_model_next_player_pov": after["score"],
                "rapfi_pv_after_model": after["pv"],
                "rapfi_query_status_after_model": "concrete_move" if rapfi_after_concrete else "no_move_or_na",
                "provisional_root_pov_gap_best_minus_model": provisional_root_gap(before["score"], after["score"]),
                "rapfi_before_attempts": before["attempts"],
                "rapfi_after_attempts": after["attempts"],
                "rapfi_before_elapsed_ms": before["elapsed_ms"],
                "rapfi_after_elapsed_ms": after["elapsed_ms"],
                "rapfi_before_depth": before["depth"],
                "rapfi_after_depth": after["depth"],
                "rapfi_before_query_file": before["query_file"],
                "rapfi_after_query_file": after["query_file"],
                "rapfi_before_raw_output": before["raw_output"],
                "rapfi_after_raw_output": after["raw_output"],
                "rapfi_before_stdout_excerpt": before["stdout_excerpt"],
                "rapfi_after_stdout_excerpt": after["stdout_excerpt"],
            }
        )

    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_report(path: Path, rows: list[dict[str, str]], args: argparse.Namespace) -> None:
    before_concrete = [r for r in rows if r["rapfi_query_status_before"] == "concrete_move"]
    after_concrete = [r for r in rows if r["rapfi_query_status_after_model"] == "concrete_move"]
    agreements = [r for r in rows if r["model_matches_rapfi_best_before"] == "True"]
    numeric_gap = [r for r in rows if r["provisional_root_pov_gap_best_minus_model"] != "NA"]

    lines = [
        "# Rapfi Teacher Score-Gap Benchmark",
        "",
        "## Scope",
        "",
        f"- positions: `{args.positions_json}`",
        f"- model eval: `{args.model_eval_csv}`",
        f"- Rapfi binary: `{args.rapfi_bin}`",
        f"- retry spec: `{args.rapfi_retry_spec}`",
        f"- rows: {len(rows)}",
        "",
        "## Summary",
        "",
        f"- Rapfi concrete best move before model move: {len(before_concrete)} / {len(rows)}",
        f"- Rapfi concrete reply after model direct move: {len(after_concrete)} / {len(rows)}",
        f"- model direct move matches Rapfi best-before move: {len(agreements)} / {len(rows)}",
        f"- numeric provisional root-pov gaps: {len(numeric_gap)} / {len(rows)}",
        "",
        "## Important interpretation note",
        "",
        "Rapfi `Eval` sign convention is treated conservatively here. The CSV includes raw before/after scores and a provisional root-perspective gap.",
        "The provisional gap assumes Rapfi eval is side-to-move-relative, so after the model move the returned score is from the opponent's perspective.",
        "This should be sanity-checked before using the gap as a training or promotion metric.",
        "",
        "## Rows",
        "",
        "| sample | side | type | model | Rapfi best | agree | Eval before | Eval after model | provisional gap | PV before |",
        "|---|---|---|---:|---:|---|---:|---:|---:|---|",
    ]

    for r in rows:
        lines.append(
            "| {sample_id} | {side_to_move} | {labeled_failure_type} | {model_direct_move} | "
            "{rapfi_best_move_before} | {model_matches_rapfi_best_before} | {rapfi_eval_before} | "
            "{rapfi_eval_after_model_next_player_pov} | {provisional_root_pov_gap_best_minus_model} | "
            "{rapfi_pv_before} |".format(**r)
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    rows = build_rows(args)
    write_csv(args.output_csv, rows)
    write_report(args.output_md, rows, args)
    print(f"positions queried: {len(rows)}")
    print(f"wrote {args.output_csv}")
    print(f"wrote {args.output_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
