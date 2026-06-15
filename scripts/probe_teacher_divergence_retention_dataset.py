from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np
import torch

from evaluate_candidate_g_policy import action_to_xy, load_model, policy_probs, rank_of_action
from gomoku_agent.board import BLACK, WHITE, Board


DATASET_DEFAULT = Path("analysis/integration_eval/teacher_divergence_retention_dataset.json")
OUT_CSV_DEFAULT = Path("analysis/integration_eval/teacher_divergence_retention_probe.csv")
OUT_MD_DEFAULT = Path("analysis/integration_eval/teacher_divergence_retention_probe_report.md")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Probe current-best policy ranks on teacher-divergence / held-out retention dataset."
    )
    parser.add_argument("--dataset", type=Path, default=DATASET_DEFAULT)
    parser.add_argument("--checkpoint", type=Path, default=Path("checkpoints/15x15_current_best.pt"))
    parser.add_argument("--output-csv", type=Path, default=OUT_CSV_DEFAULT)
    parser.add_argument("--output-md", type=Path, default=OUT_MD_DEFAULT)
    parser.add_argument("--board-size", type=int, default=15)
    parser.add_argument("--win-length", type=int, default=5)
    parser.add_argument("--channels", type=int, default=64)
    parser.add_argument("--blocks", type=int, default=4)
    return parser.parse_args()


def clean_markdown_lines(lines: list[str]) -> str:
    cleaned = [line.rstrip() for line in lines]
    while cleaned and cleaned[-1] == "":
        cleaned.pop()
    return "\n".join(cleaned) + "\n"


def parse_xy_text(xy: Any) -> tuple[int, int]:
    if isinstance(xy, str):
        x, y = xy.split(",", maxsplit=1)
        return int(x), int(y)
    if isinstance(xy, (list, tuple)) and len(xy) == 2:
        return int(xy[0]), int(xy[1])
    raise ValueError(f"unsupported xy format: {xy!r}")


def xy_to_action_text(xy: Any, board_size: int) -> int:
    x, y = parse_xy_text(xy)
    return y * board_size + x


def side_to_player(side: Any) -> int:
    s = str(side).strip().lower()
    if s in {"black", "b", "x", "1"}:
        return BLACK
    if s in {"white", "w", "o", "-1", "2"}:
        return WHITE
    raise ValueError(f"unknown side_to_move: {side!r}")


def parse_text_grid(text: str, board_size: int) -> list[list[int]]:
    token_map = {
        ".": 0,
        "_": 0,
        "0": 0,
        "X": BLACK,
        "x": BLACK,
        "B": BLACK,
        "b": BLACK,
        "O": WHITE,
        "o": WHITE,
        "W": WHITE,
        "w": WHITE,
    }
    rows: list[list[int]] = []
    for line in text.splitlines():
        tokens = line.strip().split()
        if len(tokens) != board_size:
            continue
        if not all(t in token_map for t in tokens):
            continue
        rows.append([token_map[t] for t in tokens])

    if len(rows) != board_size:
        raise ValueError(f"text board did not parse as {board_size}x{board_size}; parsed rows={len(rows)}")
    return rows


def normalize_cell(v: Any) -> int:
    if isinstance(v, str):
        s = v.strip()
        if s in {"", ".", "_", "0"}:
            return 0
        if s in {"X", "x", "B", "b", "1", "black"}:
            return BLACK
        if s in {"O", "o", "W", "w", "2", "-1", "white"}:
            return WHITE
        return int(s)
    iv = int(v)
    if iv == 2:
        # Some generated anchor matrices encode white as 2; Board uses WHITE.
        return WHITE
    return iv


def normalize_matrix(grid: list[Any], board_size: int) -> list[list[int]]:
    if len(grid) != board_size:
        raise ValueError(f"matrix board row count mismatch: {len(grid)} != {board_size}")
    rows: list[list[int]] = []
    for row in grid:
        if not isinstance(row, list) or len(row) != board_size:
            raise ValueError("matrix board is not rectangular board_size x board_size")
        rows.append([normalize_cell(v) for v in row])
    return rows


def board_grid_from_row(row: dict[str, Any], board_size: int) -> list[list[int]]:
    board = row["board"]
    if isinstance(board, str):
        return parse_text_grid(board, board_size)
    if isinstance(board, list):
        return normalize_matrix(board, board_size)
    raise ValueError(f"unsupported board type: {type(board).__name__}")


def board_from_teacher_row(row: dict[str, Any], board_size: int, win_length: int) -> Board:
    board = Board(size=board_size, win_length=win_length)
    grid = board_grid_from_row(row, board_size)

    for y in range(board_size):
        for x in range(board_size):
            board.grid[y, x] = int(grid[y][x])

    board.current_player = side_to_player(row["side_to_move"])
    board.move_count = int((board.grid != 0).sum())

    # last_move is not required for plain policy ranking.
    last_move = row.get("last_move_rc")
    if last_move:
        board.last_move = (int(last_move[0]), int(last_move[1]))

    return board


def summarize(rows: list[dict[str, str]], split: str | None = None) -> dict[str, Any]:
    subset = [r for r in rows if split is None or r["split"] == split]
    if not subset:
        return {
            "rows": 0,
            "top1": 0,
            "top3": 0,
            "top5": 0,
            "top10": 0,
            "mean_rank": None,
            "median_rank": None,
            "mean_target_prob": None,
        }

    ranks = np.array([int(r["target_rank"]) for r in subset], dtype=np.float64)
    probs = np.array([float(r["target_prob"]) for r in subset], dtype=np.float64)

    return {
        "rows": len(subset),
        "top1": int(np.sum(ranks <= 1)),
        "top3": int(np.sum(ranks <= 3)),
        "top5": int(np.sum(ranks <= 5)),
        "top10": int(np.sum(ranks <= 10)),
        "mean_rank": float(np.mean(ranks)),
        "median_rank": float(np.median(ranks)),
        "mean_target_prob": float(np.mean(probs)),
    }


def fmt_rate(num: int, den: int) -> str:
    return f"{num}/{den} ({num / den:.3f})" if den else "0/0"


def write_report(
    path: Path,
    *,
    args: argparse.Namespace,
    dataset_summary: dict[str, Any],
    rows: list[dict[str, str]],
) -> None:
    lines: list[str] = []
    lines.append("# Teacher divergence / retention current-best probe")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append(
        "Non-training probe only. This script loads current-best and computes policy rank/probability for each dataset target."
    )
    lines.append("")
    lines.append("## Inputs")
    lines.append("")
    lines.append(f"- Dataset: `{args.dataset}`")
    lines.append(f"- Checkpoint: `{args.checkpoint}`")
    lines.append(f"- Output CSV: `{args.output_csv}`")
    lines.append("")
    lines.append("## Dataset summary")
    lines.append("")
    lines.append(f"- Dataset rows: {dataset_summary.get('total_included_rows')}")
    lines.append(f"- Split counts: `{dataset_summary.get('split_counts')}`")
    lines.append(f"- Role counts: `{dataset_summary.get('role_counts')}`")
    lines.append("")
    lines.append("## Probe summary")
    lines.append("")
    lines.append("| split | rows | top1 | top3 | top5 | top10 | mean rank | median rank | mean target prob |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for split in ["ALL"] + sorted(Counter(r["split"] for r in rows)):
        summary = summarize(rows, None if split == "ALL" else split)
        den = int(summary["rows"])
        mean_rank = "" if summary["mean_rank"] is None else f"{summary['mean_rank']:.3f}"
        median_rank = "" if summary["median_rank"] is None else f"{summary['median_rank']:.3f}"
        mean_prob = "" if summary["mean_target_prob"] is None else f"{summary['mean_target_prob']:.6f}"
        lines.append(
            f"| `{split}` | {den} | "
            f"{fmt_rate(int(summary['top1']), den)} | "
            f"{fmt_rate(int(summary['top3']), den)} | "
            f"{fmt_rate(int(summary['top5']), den)} | "
            f"{fmt_rate(int(summary['top10']), den)} | "
            f"{mean_rank} | {median_rank} | {mean_prob} |"
        )
    lines.append("")
    lines.append("## Worst target ranks")
    lines.append("")
    lines.append("| id | split | side | target | rank | prob | top move | top prob | reference move | reference kind | bucket |")
    lines.append("|---|---|---|---|---:|---:|---|---:|---|---|---|")
    for r in sorted(rows, key=lambda x: int(x["target_rank"]), reverse=True)[:20]:
        lines.append(
            f"| `{r['id']}` | `{r['split']}` | {r['side_to_move']} | `{r['policy_target']}` | "
            f"{r['target_rank']} | {float(r['target_prob']):.6f} | `{r['top_move']}` | "
            f"{float(r['top_prob']):.6f} | `{r['reference_move']}` | `{r['reference_move_kind']}` | `{r['bucket']}` |"
        )
    lines.append("")
    lines.append("## Held-out retention rows")
    lines.append("")
    lines.append("| id | target | rank | prob | top move | top prob | top1 | top5 |")
    lines.append("|---|---|---:|---:|---|---:|---|---|")
    for r in [x for x in rows if x["split"] == "heldout_retention"]:
        rank = int(r["target_rank"])
        lines.append(
            f"| `{r['id']}` | `{r['policy_target']}` | {rank} | {float(r['target_prob']):.6f} | "
            f"`{r['top_move']}` | {float(r['top_prob']):.6f} | {rank <= 1} | {rank <= 5} |"
        )
    lines.append("")
    lines.append("## Interpretation guardrail")
    lines.append("")
    lines.append(
        "This report is descriptive only. It does not approve training. Held-out retention rows should remain excluded from train split."
    )
    path.write_text(clean_markdown_lines(lines), encoding="utf-8")


@torch.no_grad()
def main() -> None:
    args = parse_args()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    data = json.loads(args.dataset.read_text(encoding="utf-8"))
    dataset_rows = data["rows"]

    model = load_model(args.checkpoint, args, device)

    out_rows: list[dict[str, str]] = []
    for row in dataset_rows:
        board = board_from_teacher_row(row, args.board_size, args.win_length)
        probs, value = policy_probs(model, board, device)

        target_action = xy_to_action_text(row["policy_target"], args.board_size)
        target_rank = rank_of_action(probs, board, target_action)
        top_action = int(np.argmax(probs))

        metadata = row.get("metadata", {})
        reference_move = str(metadata.get("current_best_direct_move") or "")
        reference_move_kind = (
            "retention_anchor_target"
            if row.get("split") == "heldout_retention"
            or str(metadata.get("current_best_matches_teacher")) == "retention_anchor"
            else "current_best_direct_move"
        )

        out_rows.append(
            {
                "id": str(row["id"]),
                "split": str(row["split"]),
                "role": str(row["role"]),
                "bucket": str(row["bucket"]),
                "source_id": str(row.get("source_id", "")),
                "side_to_move": str(row["side_to_move"]),
                "policy_target": str(row["policy_target"]),
                "target_rank": str(target_rank),
                "target_prob": f"{float(probs[target_action]):.8f}",
                "top_move": action_to_xy(top_action, args.board_size),
                "top_prob": f"{float(probs[top_action]):.8f}",
                "value": f"{float(value):.8f}",
                "reference_move": reference_move,
                "reference_move_kind": reference_move_kind,
                "top_matches_target": str(top_action == target_action),
                "top_matches_reference": str(action_to_xy(top_action, args.board_size) == str(reference_move)),
                "heldout": str(bool(row.get("heldout"))),
            }
        )

    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.output_csv.open("w", newline="", encoding="utf-8") as f:
        fields = [
            "id",
            "split",
            "role",
            "bucket",
            "source_id",
            "side_to_move",
            "policy_target",
            "target_rank",
            "target_prob",
            "top_move",
            "top_prob",
            "value",
            "reference_move",
            "reference_move_kind",
            "top_matches_target",
            "top_matches_reference",
            "heldout",
        ]
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(out_rows)

    write_report(args.output_md, args=args, dataset_summary=data["summary"], rows=out_rows)

    print(f"wrote {args.output_csv}")
    print(f"wrote {args.output_md}")
    print()
    print("=== probe summary ===")
    for split in ["ALL"] + sorted(Counter(r["split"] for r in out_rows)):
        s = summarize(out_rows, None if split == "ALL" else split)
        den = int(s["rows"])
        print(
            split,
            "rows=", den,
            "top1=", fmt_rate(int(s["top1"]), den),
            "top3=", fmt_rate(int(s["top3"]), den),
            "top5=", fmt_rate(int(s["top5"]), den),
            "top10=", fmt_rate(int(s["top10"]), den),
            "mean_rank=", "" if s["mean_rank"] is None else f"{s['mean_rank']:.3f}",
            "median_rank=", "" if s["median_rank"] is None else f"{s['median_rank']:.3f}",
        )


if __name__ == "__main__":
    main()
