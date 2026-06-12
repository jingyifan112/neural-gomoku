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

DIRECTIONS = [(1, 0), (0, 1), (1, 1), (1, -1)]


def other_color(color: str) -> str:
    if color == "B":
        return "W"
    if color == "W":
        return "B"
    raise ValueError(f"bad color: {color}")


def xy_to_str(x: int, y: int) -> str:
    return f"{x},{y}"


def xy_debug_to_str(x: str, y: str) -> str:
    x_i = int(x)
    y_i = int(y)
    if x_i < 0 or y_i < 0:
        return ""
    return xy_to_str(x_i, y_i)


def move_to_str(move: dict) -> str:
    return xy_to_str(int(move["x"]), int(move["y"]))


def parse_engine_stdout(stdout: str) -> str:
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


def board_lines_for_case(case: dict) -> list[str]:
    neural_color = case["neural_color"]
    lines = []
    for move in case["moves_before_decision"]:
        x = int(move["x"])
        y = int(move["y"])
        color = move["color"]
        player = 1 if color == neural_color else 2
        lines.append(f"{x},{y},{player}")
    return lines


def board_after(moves: list[dict]) -> dict[tuple[int, int], str]:
    board = {}
    for m in moves:
        x = int(m["x"])
        y = int(m["y"])
        key = (x, y)
        if key in board:
            raise ValueError(f"duplicate move at {key}")
        board[key] = m["color"]
    return board


def legal_xy(board: dict[tuple[int, int], str], board_size: int) -> list[tuple[int, int]]:
    return [
        (x, y)
        for y in range(board_size)
        for x in range(board_size)
        if (x, y) not in board
    ]


def play_xy(board: dict[tuple[int, int], str], x: int, y: int, color: str) -> dict[tuple[int, int], str]:
    if (x, y) in board:
        raise ValueError(f"occupied move: {(x, y)}")
    out = dict(board)
    out[(x, y)] = color
    return out


def move_wins(board: dict[tuple[int, int], str], board_size: int, x: int, y: int, color: str) -> bool:
    if (x, y) in board:
        return False

    for dx, dy in DIRECTIONS:
        count = 1
        for sign in (1, -1):
            nx = x + sign * dx
            ny = y + sign * dy
            while 0 <= nx < board_size and 0 <= ny < board_size and board.get((nx, ny)) == color:
                count += 1
                nx += sign * dx
                ny += sign * dy
        if count >= 5:
            return True

    return False


def immediate_winning_moves(board: dict[tuple[int, int], str], board_size: int, color: str) -> list[str]:
    wins = []
    for x, y in legal_xy(board, board_size):
        if move_wins(board, board_size, x, y, color):
            wins.append(xy_to_str(x, y))
    return wins


def opponent_double_threat_replies_after_move(case: dict, move_s: str) -> list[dict[str, object]]:
    if not move_s or "," not in move_s:
        return []

    board_size = int(case["board_size"])
    neural_color = case["neural_color"]
    opponent_color = other_color(neural_color)

    x, y = [int(v) for v in move_s.split(",")]
    board = board_after(case["moves_before_decision"])
    if (x, y) in board:
        return [{"move": move_s, "error": "illegal_or_occupied"}]

    after_neural = play_xy(board, x, y, neural_color)

    replies = []
    for rx, ry in legal_xy(after_neural, board_size):
        after_reply = play_xy(after_neural, rx, ry, opponent_color)
        wins = immediate_winning_moves(after_reply, board_size, opponent_color)
        if len(wins) >= 2:
            replies.append({
                "move": xy_to_str(rx, ry),
                "immediate_win_count_after": len(wins),
                "immediate_wins_after": wins,
            })

    replies.sort(key=lambda r: (-int(r.get("immediate_win_count_after", 0)), str(r["move"])))
    return replies


def run_case(case: dict, args: argparse.Namespace) -> dict[str, str]:
    env = os.environ.copy()
    env["NEURAL_GOMOKU_WEIGHTS"] = str(args.weights)
    env["NEURAL_GOMOKU_MCTS_SIMS"] = str(args.mcts_sims)
    env["NEURAL_GOMOKU_MOVE_MODE"] = args.move_mode
    env["NEURAL_GOMOKU_DEBUG_DECISION"] = "1"

    proc = subprocess.run(
        [str(args.engine)],
        input="\n".join([
            f"START {case['board_size']}",
            "BOARD",
            *board_lines_for_case(case),
            "DONE",
            "END",
            "",
        ]),
        text=True,
        capture_output=True,
        env=env,
        timeout=args.timeout_sec,
    )

    debug = parse_debug(proc.stderr)
    stdout_move = parse_engine_stdout(proc.stdout)
    c_final = debug["c_final"] or stdout_move

    targets = [move_to_str(m) for m in case["target_prevention_moves"]]
    target_s = " ".join(targets)
    observed_s = move_to_str(case["observed_neural_move"])

    out = {
        "case_id": case["case_id"],
        "source_case_id": case["source_case_id"],
        "game": str(case["game"]),
        "category": case["category"],
        "back_ply": str(case["back_ply"]),
        "prefix_ply": str(case["prefix_ply"]),
        "neural_color": case["neural_color"],
        "target_prevention_moves": target_s,
        "observed_neural_move": observed_s,
        "stdout_move": stdout_move,
        **debug,
        "c_final_or_stdout": c_final,
        "returncode": str(proc.returncode),
        "stdout": proc.stdout.replace("\n", "\\n"),
        "stderr_tail": "\\n".join(proc.stderr.splitlines()[-6:]),
    }

    for key in ["c_direct", "c_policy_safety", "c_mcts_raw", "c_mcts_safety", "c_final_or_stdout"]:
        move_s = out[key]
        replies = opponent_double_threat_replies_after_move(case, move_s)
        out[f"{key}_in_target_prevention"] = str(move_s in targets)
        out[f"{key}_same_as_observed"] = str(move_s == observed_s)
        out[f"{key}_opponent_double_threat_reply_count"] = str(len(replies))
        out[f"{key}_opponent_double_threat_replies_sample"] = json.dumps(replies[: args.sample_limit])

    observed_replies = opponent_double_threat_replies_after_move(case, observed_s)
    out["observed_opponent_double_threat_reply_count"] = str(len(observed_replies))
    out["observed_opponent_double_threat_replies_sample"] = json.dumps(observed_replies[: args.sample_limit])

    return out


def write_md(path: Path, rows: list[dict[str, str]], args: argparse.Namespace) -> None:
    n = len(rows)
    final_target = sum(r["c_final_or_stdout_in_target_prevention"] == "True" for r in rows)
    safety_target = sum(r["c_policy_safety_in_target_prevention"] == "True" for r in rows)
    final_safe = sum(int(r["c_final_or_stdout_opponent_double_threat_reply_count"]) == 0 for r in rows)
    safety_safe = sum(int(r["c_policy_safety_opponent_double_threat_reply_count"]) == 0 for r in rows)

    lines = []
    lines.append("# Tactical-mid Preterminal Actionable C Engine Evaluation")
    lines.append("")
    lines.append(f"- engine: `{args.engine}`")
    lines.append(f"- weights: `{args.weights}`")
    lines.append(f"- move mode: `{args.move_mode}`")
    lines.append(f"- mcts sims: `{args.mcts_sims}`")
    lines.append(f"- cases: `{args.cases}`")
    lines.append(f"- total cases: `{n}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Metric | Count | Rate |")
    lines.append("|---|---:|---:|")
    lines.append(f"| C policy_safety selects target prevention | {safety_target}/{n} | {safety_target/n:.3f} |")
    lines.append(f"| C final selects target prevention | {final_target}/{n} | {final_target/n:.3f} |")
    lines.append(f"| C policy_safety leaves zero opponent double-threat replies | {safety_safe}/{n} | {safety_safe/n:.3f} |")
    lines.append(f"| C final leaves zero opponent double-threat replies | {final_safe}/{n} | {final_safe/n:.3f} |")
    lines.append("")
    lines.append("## Case details")
    lines.append("")
    lines.append("| Case | Target | Observed | C direct | C safety | C mcts_raw | C mcts_safety | C final | Final target | Final reply count | Safety reply count |")
    lines.append("|---|---|---|---|---|---|---|---|---|---:|---:|")
    for r in rows:
        lines.append(
            f"| `{r['case_id']}` | `{r['target_prevention_moves']}` | `{r['observed_neural_move']}` | "
            f"`{r['c_direct']}` | `{r['c_policy_safety']}` | `{r['c_mcts_raw']}` | "
            f"`{r['c_mcts_safety']}` | `{r['c_final_or_stdout']}` | "
            f"{r['c_final_or_stdout_in_target_prevention']} | "
            f"{r['c_final_or_stdout_opponent_double_threat_reply_count']} | "
            f"{r['c_policy_safety_opponent_double_threat_reply_count']} |"
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
    ap.add_argument("--sample-limit", type=int, default=12)
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
    print(f"c_policy_safety_target={sum(r['c_policy_safety_in_target_prevention'] == 'True' for r in rows)}/{n}")
    print(f"c_final_target={sum(r['c_final_or_stdout_in_target_prevention'] == 'True' for r in rows)}/{n}")
    print(f"c_policy_safety_zero_double_threat_replies={sum(int(r['c_policy_safety_opponent_double_threat_reply_count']) == 0 for r in rows)}/{n}")
    print(f"c_final_zero_double_threat_replies={sum(int(r['c_final_or_stdout_opponent_double_threat_reply_count']) == 0 for r in rows)}/{n}")


if __name__ == "__main__":
    main()
