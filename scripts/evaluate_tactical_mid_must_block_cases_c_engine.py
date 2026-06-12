#!/usr/bin/env python3
import argparse
import csv
import json
import os
import re
import subprocess
from pathlib import Path


DEBUG_RE = re.compile(
    r"DEBUG_DECISION .*?"
    r"direct=\(x=(?P<direct_x>-?\d+),y=(?P<direct_y>-?\d+),row=(?P<direct_r>-?\d+),col=(?P<direct_c>-?\d+)\) "
    r"policy_safety=\(x=(?P<safe_x>-?\d+),y=(?P<safe_y>-?\d+),row=(?P<safe_r>-?\d+),col=(?P<safe_c>-?\d+)\) "
    r"mcts_raw=\(x=(?P<mcts_raw_x>-?\d+),y=(?P<mcts_raw_y>-?\d+),row=(?P<mcts_raw_r>-?\d+),col=(?P<mcts_raw_c>-?\d+)\) "
    r"mcts_safety=\(x=(?P<mcts_safe_x>-?\d+),y=(?P<mcts_safe_y>-?\d+),row=(?P<mcts_safe_r>-?\d+),col=(?P<mcts_safe_c>-?\d+)\) "
    r"final=\(x=(?P<final_x>-?\d+),y=(?P<final_y>-?\d+),row=(?P<final_r>-?\d+),col=(?P<final_c>-?\d+)\)"
)


def xy_to_str(x: int, y: int) -> str:
    return f"{x},{y}"


def xy_debug_to_str(x: str, y: str) -> str:
    x_i = int(x)
    y_i = int(y)
    if x_i < 0 or y_i < 0:
        return ""
    return f"{x_i},{y_i}"


def parse_engine_stdout(stdout: str) -> str:
    # Last coordinate-looking stdout line is the engine move.
    move = ""
    for line in stdout.splitlines():
        s = line.strip()
        if re.fullmatch(r"\d+,\d+", s):
            move = s
    return move


def parse_debug(stderr: str) -> dict[str, str]:
    m = None
    for line in stderr.splitlines():
        mm = DEBUG_RE.search(line)
        if mm:
            m = mm
    if not m:
        return {
            "c_direct": "",
            "c_policy_safety": "",
            "c_mcts_raw": "",
            "c_mcts_safety": "",
            "c_final": "",
            "debug_found": "False",
        }

    g = m.groupdict()
    return {
        "c_direct": xy_debug_to_str(g["direct_x"], g["direct_y"]),
        "c_policy_safety": xy_debug_to_str(g["safe_x"], g["safe_y"]),
        "c_mcts_raw": xy_debug_to_str(g["mcts_raw_x"], g["mcts_raw_y"]),
        "c_mcts_safety": xy_debug_to_str(g["mcts_safe_x"], g["mcts_safe_y"]),
        "c_final": xy_debug_to_str(g["final_x"], g["final_y"]),
        "debug_found": "True",
    }


DIRECTIONS = [(1, 0), (0, 1), (1, 1), (1, -1)]


def move_wins(grid: list[list[int]], x: int, y: int, player: int, board_size: int) -> bool:
    if grid[y][x] != 0:
        return False

    for dx, dy in DIRECTIONS:
        count = 1
        for sign in (1, -1):
            nx = x + sign * dx
            ny = y + sign * dy
            while 0 <= nx < board_size and 0 <= ny < board_size and grid[ny][nx] == player:
                count += 1
                nx += sign * dx
                ny += sign * dy
        if count >= 5:
            return True

    return False


def opponent_immediate_winning_moves(case: dict) -> list[str]:
    board_size = int(case["board_size"])
    neural_color = case["neural_color"]
    grid = [[0 for _ in range(board_size)] for _ in range(board_size)]

    for move in case["moves_before_blunder"]:
        x = int(move["x"])
        y = int(move["y"])
        color = move["color"]
        grid[y][x] = 1 if color == neural_color else -1

    opponent = -1
    wins = []
    for y in range(board_size):
        for x in range(board_size):
            if move_wins(grid, x, y, opponent, board_size):
                wins.append(xy_to_str(x, y))

    return wins


def board_lines_for_case(case: dict) -> list[str]:
    neural_color = case["neural_color"]

    lines = []
    for move in case["moves_before_blunder"]:
        x = int(move["x"])
        y = int(move["y"])
        color = move["color"]

        # Piskvork BOARD convention: 1 = our engine stone, 2 = opponent stone.
        player = 1 if color == neural_color else 2
        lines.append(f"{x},{y},{player}")

    return lines


def run_case(case: dict, args: argparse.Namespace) -> dict[str, str]:
    env = os.environ.copy()
    env["NEURAL_GOMOKU_WEIGHTS"] = str(args.weights)
    env["NEURAL_GOMOKU_MCTS_SIMS"] = str(args.mcts_sims)
    env["NEURAL_GOMOKU_MOVE_MODE"] = args.move_mode
    env["NEURAL_GOMOKU_DEBUG_DECISION"] = "1"

    proc = subprocess.run(
        [str(args.engine)],
        input="\n".join(
            [
                f"START {case['board_size']}",
                "BOARD",
                *board_lines_for_case(case),
                "DONE",
                "END",
                "",
            ]
        ),
        text=True,
        capture_output=True,
        env=env,
        timeout=args.timeout_sec,
    )

    target = xy_to_str(
        int(case["target_block_move"]["x"]),
        int(case["target_block_move"]["y"]),
    )
    actual = xy_to_str(
        int(case["actual_neural_move"]["x"]),
        int(case["actual_neural_move"]["y"]),
    )

    debug = parse_debug(proc.stderr)
    stdout_move = parse_engine_stdout(proc.stdout)
    c_final = debug["c_final"] or stdout_move

    opponent_wins = opponent_immediate_winning_moves(case)
    opponent_win_count = len(opponent_wins)
    too_late_double_threat = opponent_win_count >= 2
    if too_late_double_threat:
        diagnostic_label = "too_late_double_threat"
    elif opponent_win_count == 1:
        diagnostic_label = "single_terminal_must_block"
    else:
        diagnostic_label = "non_terminal_or_extractor_mismatch"

    return {
        "case_id": case["case_id"],
        "game": str(case["game"]),
        "category": case["category"],
        "neural_color": case["neural_color"],
        "diagnostic_label": diagnostic_label,
        "opponent_immediate_win_count": str(opponent_win_count),
        "too_late_double_threat": str(too_late_double_threat),
        "opponent_immediate_winning_moves": " ".join(opponent_wins),
        "target_block_move": target,
        "actual_neural_move": actual,
        "stdout_move": stdout_move,
        **debug,
        "c_final_or_stdout": c_final,
        "c_final_exact_target": str(c_final == target),
        "c_final_same_as_match_blunder": str(c_final == actual),
        "returncode": str(proc.returncode),
        "stdout": proc.stdout.replace("\n", "\\n"),
        "stderr_tail": "\\n".join(proc.stderr.splitlines()[-6:]),
    }


def write_md(path: Path, rows: list[dict[str, str]], args: argparse.Namespace) -> None:
    n = len(rows)
    exact = sum(r["c_final_exact_target"] == "True" for r in rows)
    same_blunder = sum(r["c_final_same_as_match_blunder"] == "True" for r in rows)
    debug_found = sum(r["debug_found"] == "True" for r in rows)
    too_late = sum(r["too_late_double_threat"] == "True" for r in rows)
    single_terminal = sum(r["diagnostic_label"] == "single_terminal_must_block" for r in rows)

    lines = []
    lines.append("# Tactical-mid Too-late Double-threat C Engine Evaluation")
    lines.append("")
    lines.append(f"- engine: `{args.engine}`")
    lines.append(f"- weights: `{args.weights}`")
    lines.append(f"- move mode: `{args.move_mode}`")
    lines.append(f"- mcts sims: `{args.mcts_sims}`")
    lines.append(f"- cases: `{args.cases}`")
    lines.append(f"- total cases: `{n}`")
    lines.append("- diagnostic: `too_late_double_threat` means the opponent already has at least two immediate winning moves before the recorded neural move.")
    lines.append("- interpretation: C final repeating the match blunder confirms engine parity with the public match, but these cases are too late for single-target block training.")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Metric | Count | Rate |")
    lines.append("|---|---:|---:|")
    lines.append(f"| debug line found | {debug_found}/{n} | {debug_found/n:.3f} |")
    lines.append(f"| too_late_double_threat positions | {too_late}/{n} | {too_late/n:.3f} |")
    lines.append(f"| single-terminal must-block positions | {single_terminal}/{n} | {single_terminal/n:.3f} |")
    lines.append(f"| C final selects exact target endpoint | {exact}/{n} | {exact/n:.3f} |")
    lines.append(f"| C final repeats match blunder | {same_blunder}/{n} | {same_blunder/n:.3f} |")
    lines.append("")
    lines.append("## Case details")
    lines.append("")
    lines.append("| Case | Label | Opp win count | Opponent immediate wins | Target | Match blunder | C direct | C safety | C mcts_raw | C mcts_safety | C final/stdout | Exact target | Same blunder |")
    lines.append("|---|---|---:|---|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        lines.append(
            f"| `{r['case_id']}` | `{r['diagnostic_label']}` | {r['opponent_immediate_win_count']} | "
            f"`{r['opponent_immediate_winning_moves']}` | `{r['target_block_move']}` | `{r['actual_neural_move']}` | "
            f"`{r['c_direct']}` | `{r['c_policy_safety']}` | `{r['c_mcts_raw']}` | "
            f"`{r['c_mcts_safety']}` | `{r['c_final_or_stdout']}` | "
            f"{r['c_final_exact_target']} | {r['c_final_same_as_match_blunder']} |"
        )

    path.write_text("\n".join(lines) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", type=Path, required=True)
    ap.add_argument("--engine", type=Path, default=Path("c_inference/pbrain-neural-gomoku"))
    ap.add_argument("--weights", type=Path, default=Path("weights/15x15_current_best_weights.bin"))
    ap.add_argument("--mcts-sims", type=int, default=16)
    ap.add_argument("--move-mode", default="mcts_safe")
    ap.add_argument("--timeout-sec", type=float, default=20.0)
    ap.add_argument("--out-csv", type=Path, required=True)
    ap.add_argument("--out-md", type=Path, required=True)
    args = ap.parse_args()

    cases = json.loads(args.cases.read_text())
    rows = [run_case(case, args) for case in cases]

    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.out_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    write_md(args.out_md, rows, args)

    n = len(rows)
    print(f"wrote {args.out_csv}")
    print(f"wrote {args.out_md}")
    print(f"cases={n}")
    print(f"debug_found={sum(r['debug_found'] == 'True' for r in rows)}/{n}")
    print(f"c_final_exact_target={sum(r['c_final_exact_target'] == 'True' for r in rows)}/{n}")
    print(f"c_final_same_as_match_blunder={sum(r['c_final_same_as_match_blunder'] == 'True' for r in rows)}/{n}")
    print(f"too_late_double_threat={sum(r['too_late_double_threat'] == 'True' for r in rows)}/{n}")


if __name__ == "__main__":
    main()
