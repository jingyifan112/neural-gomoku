#!/usr/bin/env python3
import argparse
import csv
from collections import Counter
from pathlib import Path


def parse_line(line: str):
    if not line.strip():
        return []
    pts = []
    for item in line.split():
        x, y = item.split(",")
        pts.append((int(x), int(y)))
    return pts


def direction_of_line(line: str):
    pts = parse_line(line)
    if len(pts) < 2:
        return "none"

    x0, y0 = pts[0]
    x1, y1 = pts[-1]
    dx = x1 - x0
    dy = y1 - y0

    if dx == 0:
        return "vertical"
    if dy == 0:
        return "horizontal"
    if abs(dx) == abs(dy):
        return "diagonal"
    return "other"


def phase_from_ply(ply: int):
    if ply <= 55:
        return "fast"
    if ply <= 120:
        return "mid"
    return "long"


def category(row):
    result = row["neural_result"]
    reason = row["reason"]
    ply = int(row["ply_count_from_sgf"])

    if result == "D":
        return "draw_full_board"
    if result == "W":
        return "win"

    direction = direction_of_line(row["winning_line"])
    phase = phase_from_ply(ply)

    if direction == "diagonal":
        shape = "diagonal"
    elif direction in {"horizontal", "vertical"}:
        shape = "straight"
    else:
        shape = direction

    return f"{phase}_{shape}_loss"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-csv", type=Path, required=True)
    ap.add_argument("--out-csv", type=Path, required=True)
    ap.add_argument("--out-md", type=Path, required=True)
    args = ap.parse_args()

    with args.input_csv.open() as f:
        rows = list(csv.DictReader(f))

    out_rows = []
    for row in rows:
        row = dict(row)
        row["line_direction"] = direction_of_line(row["winning_line"])
        row["phase"] = phase_from_ply(int(row["ply_count_from_sgf"]))
        row["category"] = category(row)
        out_rows.append(row)

    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.out_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        writer.writeheader()
        writer.writerows(out_rows)

    category_counts = Counter(r["category"] for r in out_rows)
    loss_direction_counts = Counter(
        r["line_direction"] for r in out_rows if r["neural_result"] == "L"
    )
    loss_phase_counts = Counter(
        r["phase"] for r in out_rows if r["neural_result"] == "L"
    )

    lines = []
    lines.append("# Tactical-mid Failure Category Report")
    lines.append("")
    lines.append(f"- source: `{args.input_csv}`")
    lines.append(f"- total games: `{len(out_rows)}`")
    lines.append("")
    lines.append("## Category counts")
    lines.append("")
    lines.append("| Category | Count |")
    lines.append("|---|---:|")
    for k, v in category_counts.most_common():
        lines.append(f"| `{k}` | {v} |")

    lines.append("")
    lines.append("## Loss direction counts")
    lines.append("")
    lines.append("| Direction | Count |")
    lines.append("|---|---:|")
    for k, v in loss_direction_counts.most_common():
        lines.append(f"| `{k}` | {v} |")

    lines.append("")
    lines.append("## Loss phase counts")
    lines.append("")
    lines.append("| Phase | Count |")
    lines.append("|---|---:|")
    for k, v in loss_phase_counts.most_common():
        lines.append(f"| `{k}` | {v} |")

    lines.append("")
    lines.append("## Loss details")
    lines.append("")
    lines.append("| Game | Neural color | Category | Ply | Direction | Winner line | Final move |")
    lines.append("|---:|---|---|---:|---|---|---|")
    for r in out_rows:
        if r["neural_result"] != "L":
            continue
        lines.append(
            f"| {r['game']} | {r['neural_color']} | `{r['category']}` | "
            f"{r['ply_count_from_sgf']} | `{r['line_direction']}` | "
            f"`{r['winning_line']}` | `{r['final_move']}` |"
        )

    lines.append("")
    lines.append("## Recommendation")
    lines.append("")
    lines.append(
        "Prioritize tactical defense data where the opponent has a direct line threat, "
        "especially diagonal threats in early and midgame positions. "
        "Use this report as a fixed diagnostic target before promoting any new model."
    )

    args.out_md.write_text("\n".join(lines) + "\n")

    print(f"wrote {args.out_csv}")
    print(f"wrote {args.out_md}")
    print("category_counts:", dict(category_counts))
    print("loss_direction_counts:", dict(loss_direction_counts))
    print("loss_phase_counts:", dict(loss_phase_counts))


if __name__ == "__main__":
    main()
