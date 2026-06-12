#!/usr/bin/env python3
import argparse
import csv
import re
from collections import Counter
from pathlib import Path

DIRS = [(1, 0), (0, 1), (1, 1), (1, -1)]


def split_sgf_trees(text: str) -> list[str]:
    trees = []
    start = None
    depth = 0
    for i, ch in enumerate(text):
        if ch == "(":
            if depth == 0:
                start = i
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0 and start is not None:
                trees.append(text[start : i + 1])
                start = None
    return trees


def sgf_coord_to_xy(coord: str):
    if not coord or len(coord) < 2:
        return None
    return ord(coord[0].lower()) - ord("a"), ord(coord[1].lower()) - ord("a")


def parse_sgf_moves(tree: str):
    moves = []
    for color, coord in re.findall(r";\s*([BW])\[([A-Za-z]{2})\]", tree):
        xy = sgf_coord_to_xy(coord)
        if xy is not None:
            moves.append((color, xy[0], xy[1]))
    return moves


def parse_log(log_path: Path, neural_name: str):
    pat = re.compile(r"Finished game (\d+) \(([^)]+)\): ([^\s]+) \{(.+)\}")
    rows = {}

    for line in log_path.read_text().splitlines():
        m = pat.search(line)
        if not m:
            continue

        game = int(m.group(1))
        pairing = m.group(2)
        raw_result = m.group(3)
        reason = m.group(4)

        left, right = [x.strip() for x in pairing.split(" vs ")]
        neural_is_left = left == neural_name
        neural_is_right = right == neural_name

        if not (neural_is_left or neural_is_right):
            raise ValueError(f"neural engine {neural_name!r} not found in pairing: {pairing}")

        neural_color = "B" if neural_is_left else "W"

        if raw_result == "1/2-1/2":
            neural_result = "D"
        elif raw_result == "1-0":
            neural_result = "W" if neural_is_left else "L"
        elif raw_result == "0-1":
            neural_result = "W" if neural_is_right else "L"
        else:
            neural_result = "?"

        if reason.startswith("Black win"):
            winner_color = "B"
        elif reason.startswith("White win"):
            winner_color = "W"
        else:
            winner_color = ""

        rows[game] = {
            "game": game,
            "pairing": pairing,
            "raw_result": raw_result,
            "reason": reason,
            "neural_color": neural_color,
            "neural_result": neural_result,
            "winner_color": winner_color,
        }

    return rows


def find_winning_line(moves, winner_color: str):
    if winner_color not in {"B", "W"}:
        return ""

    board = {}
    for color, x, y in moves:
        board[(x, y)] = color

    for y in range(15):
        for x in range(15):
            if board.get((x, y)) != winner_color:
                continue
            for dx, dy in DIRS:
                prev = (x - dx, y - dy)
                if board.get(prev) == winner_color:
                    continue

                line = []
                nx, ny = x, y
                while board.get((nx, ny)) == winner_color:
                    line.append((nx, ny))
                    nx += dx
                    ny += dy

                if len(line) >= 5:
                    return " ".join(f"{px},{py}" for px, py in line[:5])

    return ""


def summarize_last_moves(moves, n=12):
    out = []
    start = max(0, len(moves) - n)
    for i, (color, x, y) in enumerate(moves[start:], start=start + 1):
        out.append(f"{i}:{color}@{x},{y}")
    return " ".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-prefix", type=Path, required=True)
    ap.add_argument("--neural-name", default="neural_current_best_mcts16")
    ap.add_argument("--out-csv", type=Path, required=True)
    ap.add_argument("--out-md", type=Path, required=True)
    args = ap.parse_args()

    log_path = Path(str(args.run_prefix) + ".log")
    sgf_path = Path(str(args.run_prefix) + ".sgf")

    log_rows = parse_log(log_path, args.neural_name)
    sgf_trees = split_sgf_trees(sgf_path.read_text())

    if len(sgf_trees) != len(log_rows):
        print(f"WARNING: SGF tree count {len(sgf_trees)} != log game count {len(log_rows)}")

    output_rows = []
    for game in sorted(log_rows):
        info = log_rows[game]
        moves = parse_sgf_moves(sgf_trees[game - 1]) if game - 1 < len(sgf_trees) else []

        winning_line = find_winning_line(moves, info["winner_color"])
        final_move = ""
        if moves:
            c, x, y = moves[-1]
            final_move = f"{c}@{x},{y}"

        output_rows.append({
            "game": game,
            "neural_color": info["neural_color"],
            "neural_result": info["neural_result"],
            "raw_result": info["raw_result"],
            "reason": info["reason"],
            "ply_count_from_sgf": len(moves),
            "winner_color": info["winner_color"],
            "final_move": final_move,
            "winning_line": winning_line,
            "last_12_moves": summarize_last_moves(moves, 12),
        })

    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.out_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(output_rows[0].keys()))
        writer.writeheader()
        writer.writerows(output_rows)

    counts = Counter(r["neural_result"] for r in output_rows)
    loss_rows = [r for r in output_rows if r["neural_result"] == "L"]
    draw_rows = [r for r in output_rows if r["neural_result"] == "D"]
    win_rows = [r for r in output_rows if r["neural_result"] == "W"]

    lines = []
    lines.append("# Tactical-mid Failure Summary")
    lines.append("")
    lines.append(f"- run prefix: `{args.run_prefix}`")
    lines.append(f"- neural engine: `{args.neural_name}`")
    lines.append(f"- total games: `{len(output_rows)}`")
    lines.append(f"- wins: `{counts.get('W', 0)}`")
    lines.append(f"- losses: `{counts.get('L', 0)}`")
    lines.append(f"- draws: `{counts.get('D', 0)}`")
    lines.append("")
    lines.append("## Loss games")
    lines.append("")
    lines.append("| Game | Neural color | Reason | Ply count | Winner line | Final move |")
    lines.append("|---:|---|---|---:|---|---|")
    for r in loss_rows:
        lines.append(
            f"| {r['game']} | {r['neural_color']} | {r['reason']} | "
            f"{r['ply_count_from_sgf']} | `{r['winning_line']}` | `{r['final_move']}` |"
        )

    lines.append("")
    lines.append("## Draw games")
    lines.append("")
    lines.append("| Game | Neural color | Reason | Ply count | Final move |")
    lines.append("|---:|---|---|---:|---|")
    for r in draw_rows:
        lines.append(
            f"| {r['game']} | {r['neural_color']} | {r['reason']} | "
            f"{r['ply_count_from_sgf']} | `{r['final_move']}` |"
        )

    lines.append("")
    lines.append("## Win games")
    lines.append("")
    lines.append("| Game | Neural color | Reason | Ply count | Winner line | Final move |")
    lines.append("|---:|---|---|---:|---|---|")
    for r in win_rows:
        lines.append(
            f"| {r['game']} | {r['neural_color']} | {r['reason']} | "
            f"{r['ply_count_from_sgf']} | `{r['winning_line']}` | `{r['final_move']}` |"
        )

    args.out_md.write_text("\n".join(lines) + "\n")

    print(f"wrote {args.out_csv}")
    print(f"wrote {args.out_md}")
    print("summary:", dict(counts))


if __name__ == "__main__":
    main()
