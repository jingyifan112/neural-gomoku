#!/usr/bin/env python3
import argparse
import csv
import json
from collections import Counter
from pathlib import Path


DIRECTIONS = [(1, 0), (0, 1), (1, 1), (1, -1)]


def other_color(color: str) -> str:
    if color == "B":
        return "W"
    if color == "W":
        return "B"
    raise ValueError(f"bad color: {color}")


def xy_to_str(x: int, y: int) -> str:
    return f"{x},{y}"


def move_to_str(move: dict | None) -> str:
    if move is None:
        return ""
    return xy_to_str(int(move["x"]), int(move["y"]))


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


def legal_moves(board: dict[tuple[int, int], str], board_size: int) -> list[tuple[int, int]]:
    return [
        (x, y)
        for y in range(board_size)
        for x in range(board_size)
        if (x, y) not in board
    ]


def play(board: dict[tuple[int, int], str], x: int, y: int, color: str) -> dict[tuple[int, int], str]:
    if (x, y) in board:
        raise ValueError(f"occupied move: {(x, y)}")
    nxt = dict(board)
    nxt[(x, y)] = color
    return nxt


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


def immediate_winning_moves(
    board: dict[tuple[int, int], str],
    board_size: int,
    color: str,
) -> list[str]:
    wins = []
    for x, y in legal_moves(board, board_size):
        if move_wins(board, board_size, x, y, color):
            wins.append(xy_to_str(x, y))
    return wins


def double_threat_creating_moves(
    board: dict[tuple[int, int], str],
    board_size: int,
    color: str,
) -> list[dict[str, object]]:
    rows = []
    for x, y in legal_moves(board, board_size):
        after = play(board, x, y, color)
        wins = immediate_winning_moves(after, board_size, color)
        if len(wins) >= 2:
            rows.append({
                "move": xy_to_str(x, y),
                "immediate_win_count_after": len(wins),
                "immediate_wins_after": wins,
            })
    rows.sort(key=lambda r: (-int(r["immediate_win_count_after"]), str(r["move"])))
    return rows


def count_opponent_double_threat_replies_after_neural_move(
    board: dict[tuple[int, int], str],
    board_size: int,
    neural_move: tuple[int, int],
    neural_color: str,
) -> tuple[int, list[dict[str, object]]]:
    opponent = other_color(neural_color)
    after_neural = play(board, neural_move[0], neural_move[1], neural_color)
    replies = double_threat_creating_moves(after_neural, board_size, opponent)
    return len(replies), replies


def evaluate_case(case: dict, max_back_ply: int, sample_limit: int) -> list[dict[str, object]]:
    board_size = int(case["board_size"])
    neural_color = case["neural_color"]
    opponent_color = other_color(neural_color)
    moves = case["moves_before_blunder"]
    full_len = len(moves)

    out = []

    for back_ply in range(1, max_back_ply + 1):
        prefix_ply = full_len - back_ply
        if prefix_ply < 0 or prefix_ply >= full_len:
            continue

        board = board_after(moves[:prefix_ply])
        observed_next = moves[prefix_ply]
        observed_next_color = observed_next["color"]
        observed_next_role = "neural" if observed_next_color == neural_color else "opponent"

        opponent_wins_before = immediate_winning_moves(board, board_size, opponent_color)
        neural_wins_before = immediate_winning_moves(board, board_size, neural_color)

        after_observed = play(
            board,
            int(observed_next["x"]),
            int(observed_next["y"]),
            observed_next_color,
        )
        opponent_wins_after_observed = immediate_winning_moves(
            after_observed,
            board_size,
            opponent_color,
        )

        row: dict[str, object] = {
            "case_id": case["case_id"],
            "preterminal_id": f"{case['case_id']}_back{back_ply}",
            "game": case["game"],
            "category": case["category"],
            "line_direction": case["line_direction"],
            "phase": case["phase"],
            "board_size": board_size,
            "neural_color": neural_color,
            "opponent_color": opponent_color,
            "back_ply": back_ply,
            "prefix_ply": prefix_ply,
            "observed_next_move": move_to_str(observed_next),
            "observed_next_color": observed_next_color,
            "observed_next_role": observed_next_role,
            "opponent_immediate_win_count_before": len(opponent_wins_before),
            "opponent_immediate_wins_before": opponent_wins_before,
            "neural_immediate_win_count_before": len(neural_wins_before),
            "neural_immediate_wins_before": neural_wins_before,
            "opponent_immediate_win_count_after_observed": len(opponent_wins_after_observed),
            "opponent_immediate_wins_after_observed": opponent_wins_after_observed,
            "observed_next_creates_too_late_double_threat": (
                observed_next_role == "opponent"
                and len(opponent_wins_before) < 2
                and len(opponent_wins_after_observed) >= 2
            ),
            "opponent_double_threat_replies_after_observed_neural_count": "",
            "opponent_double_threat_replies_after_observed_neural_sample": [],
            "observed_opponent_reply": "",
            "observed_opponent_reply_creates_double_threat": "",
            "observed_opponent_reply_immediate_wins_after": [],
            "neural_prevention_move_count": "",
            "neural_prevention_moves_sample": [],
            "observed_neural_move_prevents_all_double_threat_replies": "",
        }

        if observed_next_role == "neural":
            replies = double_threat_creating_moves(after_observed, board_size, opponent_color)
            row["opponent_double_threat_replies_after_observed_neural_count"] = len(replies)
            row["opponent_double_threat_replies_after_observed_neural_sample"] = replies[:sample_limit]

            observed_reply = moves[prefix_ply + 1] if prefix_ply + 1 < full_len else None
            if observed_reply is not None and observed_reply["color"] == opponent_color:
                after_reply = play(
                    after_observed,
                    int(observed_reply["x"]),
                    int(observed_reply["y"]),
                    opponent_color,
                )
                wins_after_reply = immediate_winning_moves(after_reply, board_size, opponent_color)
                row["observed_opponent_reply"] = move_to_str(observed_reply)
                row["observed_opponent_reply_creates_double_threat"] = len(wins_after_reply) >= 2
                row["observed_opponent_reply_immediate_wins_after"] = wins_after_reply

            prevention_moves = []
            for x, y in legal_moves(board, board_size):
                reply_count, reply_rows = count_opponent_double_threat_replies_after_neural_move(
                    board,
                    board_size,
                    (x, y),
                    neural_color,
                )
                if reply_count == 0:
                    prevention_moves.append(xy_to_str(x, y))

            observed_reply_count, _ = count_opponent_double_threat_replies_after_neural_move(
                board,
                board_size,
                (int(observed_next["x"]), int(observed_next["y"])),
                neural_color,
            )
            row["neural_prevention_move_count"] = len(prevention_moves)
            row["neural_prevention_moves_sample"] = prevention_moves[:sample_limit]
            row["observed_neural_move_prevents_all_double_threat_replies"] = observed_reply_count == 0

        out.append(row)

    return out


def csv_value(v: object) -> str:
    if isinstance(v, (list, dict)):
        return json.dumps(v, ensure_ascii=False)
    return str(v)


def write_md(path: Path, rows: list[dict[str, object]], args: argparse.Namespace) -> None:
    n = len(rows)
    role_counts = Counter(str(r["observed_next_role"]) for r in rows)
    opponent_create_rows = [
        r for r in rows
        if r["observed_next_creates_too_late_double_threat"] is True
    ]
    neural_rows = [r for r in rows if r["observed_next_role"] == "neural"]
    neural_bad_rows = [
        r for r in neural_rows
        if int(r["opponent_double_threat_replies_after_observed_neural_count"]) > 0
    ]

    lines = []
    lines.append("# Tactical-mid Preterminal Case Extractor")
    lines.append("")
    lines.append(f"- source cases: `{args.cases}`")
    lines.append(f"- total source cases: `{len(set(r['case_id'] for r in rows))}`")
    lines.append(f"- max back ply: `{args.max_back_ply}`")
    lines.append(f"- total extracted rows: `{n}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Metric | Count | Rate |")
    lines.append("|---|---:|---:|")
    for role, count in role_counts.most_common():
        lines.append(f"| rows where observed next role is `{role}` | {count}/{n} | {count/n:.3f} |")
    lines.append(f"| opponent moves that create too-late double threat | {len(opponent_create_rows)}/{n} | {len(opponent_create_rows)/n:.3f} |")
    if neural_rows:
        lines.append(f"| neural rows with opponent double-threat replies after observed neural move | {len(neural_bad_rows)}/{len(neural_rows)} | {len(neural_bad_rows)/len(neural_rows):.3f} |")

    lines.append("")
    lines.append("## Case details")
    lines.append("")
    lines.append("| Case | Back ply | Prefix ply | Role | Observed next | Opp wins before | Opp wins after observed | Opp double-threat replies after observed neural | Neural prevention moves | Observed opponent reply | Reply creates double threat |")
    lines.append("|---|---:|---:|---|---|---:|---:|---:|---:|---|---|")
    for r in rows:
        lines.append(
            f"| `{r['case_id']}` | {r['back_ply']} | {r['prefix_ply']} | "
            f"`{r['observed_next_role']}` | `{r['observed_next_move']}` | "
            f"{r['opponent_immediate_win_count_before']} | "
            f"{r['opponent_immediate_win_count_after_observed']} | "
            f"{r['opponent_double_threat_replies_after_observed_neural_count']} | "
            f"{r['neural_prevention_move_count']} | "
            f"`{r['observed_opponent_reply']}` | "
            f"{r['observed_opponent_reply_creates_double_threat']} |"
        )

    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append(
        "Rows with `back_ply=1` show whether the opponent's previous move created the double-terminal threat. "
        "Rows with `back_ply=2` show whether neural's previous move allowed one or more opponent replies "
        "that create a double-terminal threat. These are diagnostic/preterminal candidates, not direct training targets yet."
    )

    path.write_text("\n".join(lines) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", type=Path, required=True)
    ap.add_argument("--out-json", type=Path, required=True)
    ap.add_argument("--out-csv", type=Path, required=True)
    ap.add_argument("--out-md", type=Path, required=True)
    ap.add_argument("--max-back-ply", type=int, default=2)
    ap.add_argument("--sample-limit", type=int, default=12)
    args = ap.parse_args()

    cases = json.loads(args.cases.read_text())

    rows = []
    for case in cases:
        rows.extend(evaluate_case(case, args.max_back_ply, args.sample_limit))

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n")

    fieldnames = [
        "case_id",
        "preterminal_id",
        "game",
        "category",
        "line_direction",
        "phase",
        "board_size",
        "neural_color",
        "opponent_color",
        "back_ply",
        "prefix_ply",
        "observed_next_move",
        "observed_next_color",
        "observed_next_role",
        "opponent_immediate_win_count_before",
        "opponent_immediate_wins_before",
        "neural_immediate_win_count_before",
        "neural_immediate_wins_before",
        "opponent_immediate_win_count_after_observed",
        "opponent_immediate_wins_after_observed",
        "observed_next_creates_too_late_double_threat",
        "opponent_double_threat_replies_after_observed_neural_count",
        "opponent_double_threat_replies_after_observed_neural_sample",
        "observed_opponent_reply",
        "observed_opponent_reply_creates_double_threat",
        "observed_opponent_reply_immediate_wins_after",
        "neural_prevention_move_count",
        "neural_prevention_moves_sample",
        "observed_neural_move_prevents_all_double_threat_replies",
    ]

    with args.out_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow({k: csv_value(r.get(k, "")) for k in fieldnames})

    write_md(args.out_md, rows, args)

    n = len(rows)
    opponent_create = sum(r["observed_next_creates_too_late_double_threat"] is True for r in rows)
    neural_rows = [r for r in rows if r["observed_next_role"] == "neural"]
    neural_bad = sum(
        int(r["opponent_double_threat_replies_after_observed_neural_count"]) > 0
        for r in neural_rows
    )

    print(f"wrote {args.out_json}")
    print(f"wrote {args.out_csv}")
    print(f"wrote {args.out_md}")
    print(f"rows={n}")
    print(f"opponent_create_double_threat_rows={opponent_create}/{n}")
    print(f"neural_rows_with_double_threat_replies={neural_bad}/{len(neural_rows)}")


if __name__ == "__main__":
    main()
