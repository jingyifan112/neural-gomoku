#!/usr/bin/env python3
import argparse
import csv
import json
import re
from pathlib import Path


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
            moves.append({"color": color, "x": xy[0], "y": xy[1]})
    return moves


def parse_final_move(s: str):
    # Example: B@0,8
    color, xy = s.split("@")
    x, y = xy.split(",")
    return color, int(x), int(y)


def load_csv(path: Path):
    with path.open() as f:
        return list(csv.DictReader(f))


def board_after(moves):
    board = {}
    for m in moves:
        key = (m["x"], m["y"])
        if key in board:
            raise ValueError(f"duplicate move at {key}")
        board[key] = m["color"]
    return board


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-prefix", type=Path, required=True)
    ap.add_argument("--categories-csv", type=Path, required=True)
    ap.add_argument("--out-json", type=Path, required=True)
    ap.add_argument("--out-csv", type=Path, required=True)
    ap.add_argument("--out-md", type=Path, required=True)
    args = ap.parse_args()

    sgf_path = Path(str(args.run_prefix) + ".sgf")
    sgf_trees = split_sgf_trees(sgf_path.read_text())
    rows = load_csv(args.categories_csv)

    cases = []
    csv_rows = []

    for row in rows:
        if row["neural_result"] != "L":
            continue

        game = int(row["game"])
        moves = parse_sgf_moves(sgf_trees[game - 1])

        if len(moves) < 3:
            raise ValueError(f"game {game}: too few moves")

        final_color, final_x, final_y = parse_final_move(row["final_move"])
        final_move = moves[-1]
        actual_neural_move = moves[-2]

        if (final_move["color"], final_move["x"], final_move["y"]) != (final_color, final_x, final_y):
            raise ValueError(
                f"game {game}: final move mismatch, "
                f"sgf={final_move}, summary={row['final_move']}"
            )

        neural_color = row["neural_color"]
        if actual_neural_move["color"] != neural_color:
            raise ValueError(
                f"game {game}: previous move before final was not neural. "
                f"actual={actual_neural_move}, neural_color={neural_color}"
            )

        position_moves = moves[:-2]
        board = board_after(position_moves)
        if (final_x, final_y) in board:
            raise ValueError(f"game {game}: target block square occupied before blunder")

        case_id = f"tactical_mid_g{game}_block_{final_x}_{final_y}"
        target_move = {"x": final_x, "y": final_y}

        case = {
            "case_id": case_id,
            "source": "gomocup2026_freestyle15_public_openings_vs_tactical_mid",
            "board_size": 15,
            "game": game,
            "neural_color": neural_color,
            "side_to_move": neural_color,
            "category": row["category"],
            "line_direction": row["line_direction"],
            "phase": row["phase"],
            "ply_count_full_game": int(row["ply_count_from_sgf"]),
            "position_ply_before_blunder": len(position_moves),
            "target_block_move": target_move,
            "actual_neural_move": {
                "x": actual_neural_move["x"],
                "y": actual_neural_move["y"],
            },
            "opponent_winning_move_after_blunder": {
                "x": final_x,
                "y": final_y,
            },
            "winner_line_after_blunder": row["winning_line"],
            "moves_before_blunder": position_moves,
            "notes": (
                "Neural to move should block the opponent's direct five-completion square. "
                "In the original game, neural chose actual_neural_move, then the opponent "
                "played opponent_winning_move_after_blunder and won immediately."
            ),
        }
        cases.append(case)

        csv_rows.append({
            "case_id": case_id,
            "game": game,
            "neural_color": neural_color,
            "category": row["category"],
            "line_direction": row["line_direction"],
            "phase": row["phase"],
            "position_ply_before_blunder": len(position_moves),
            "target_block_move": f"{final_x},{final_y}",
            "actual_neural_move": f"{actual_neural_move['x']},{actual_neural_move['y']}",
            "winner_line_after_blunder": row["winning_line"],
        })

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(cases, indent=2) + "\n")

    with args.out_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(csv_rows[0].keys()))
        writer.writeheader()
        writer.writerows(csv_rows)

    lines = []
    lines.append("# Tactical-mid Must-block Cases")
    lines.append("")
    lines.append(f"- source run: `{args.run_prefix}`")
    lines.append(f"- source categories: `{args.categories_csv}`")
    lines.append(f"- total cases: `{len(cases)}`")
    lines.append("")
    lines.append("Each case is the position before neural's final defensive blunder in a tactical_mid loss.")
    lines.append("")
    lines.append("| Case | Game | Neural color | Category | Ply before blunder | Target block | Actual neural move | Threat line after blunder |")
    lines.append("|---|---:|---|---|---:|---|---|---|")
    for r in csv_rows:
        lines.append(
            f"| `{r['case_id']}` | {r['game']} | {r['neural_color']} | "
            f"`{r['category']}` | {r['position_ply_before_blunder']} | "
            f"`{r['target_block_move']}` | `{r['actual_neural_move']}` | "
            f"`{r['winner_line_after_blunder']}` |"
        )

    lines.append("")
    lines.append("## Use")
    lines.append("")
    lines.append(
        "These cases should be used first as a fixed regression test. "
        "A candidate model should select the target block move, or at minimum avoid allowing "
        "the opponent's immediate five-completion move."
    )

    args.out_md.write_text("\n".join(lines) + "\n")

    print(f"wrote {args.out_json}")
    print(f"wrote {args.out_csv}")
    print(f"wrote {args.out_md}")
    print(f"cases: {len(cases)}")


if __name__ == "__main__":
    main()
