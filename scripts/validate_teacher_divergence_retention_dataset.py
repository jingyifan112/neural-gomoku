from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

DATASET = Path("analysis/integration_eval/teacher_divergence_retention_dataset.json")
MANIFEST = Path("analysis/integration_eval/teacher_divergence_retention_manifest.csv")
OUT_CSV = Path("analysis/integration_eval/teacher_divergence_retention_validation.csv")
OUT_MD = Path("analysis/integration_eval/teacher_divergence_retention_validation.md")

EMPTY_VALUES = {None, "", ".", "_", "-", "0", 0}
BLACK_VALUES = {"black", "b", "B", "x", "X", "1", 1}
WHITE_VALUES = {"white", "w", "W", "o", "O", "-1", -1, "2", 2}


def parse_xy(v: Any) -> tuple[int, int] | None:
    if v is None:
        return None
    if isinstance(v, str):
        s = v.strip()
        if not s:
            return None
        if "," in s:
            a, b = [p.strip() for p in s.split(",", 1)]
            if a.lstrip("-").isdigit() and b.lstrip("-").isdigit():
                return int(a), int(b)
        return None
    if isinstance(v, (list, tuple)) and len(v) >= 2:
        try:
            return int(v[0]), int(v[1])
        except Exception:
            return None
    if isinstance(v, dict):
        if "x" in v and "y" in v:
            return int(v["x"]), int(v["y"])
        if "col" in v and "row" in v:
            return int(v["col"]), int(v["row"])
    return None


def classify_cell(v: Any) -> str:
    if v in EMPTY_VALUES:
        return "empty"
    if v in BLACK_VALUES:
        return "black"
    if v in WHITE_VALUES:
        return "white"

    s = str(v).strip()
    if s in EMPTY_VALUES:
        return "empty"
    if s in BLACK_VALUES:
        return "black"
    if s in WHITE_VALUES:
        return "white"
    return "unknown"


def color_from_any(v: Any) -> str | None:
    c = classify_cell(v)
    if c in {"black", "white"}:
        return c

    s = str(v).strip().lower()
    if s in {"black", "b", "x", "1"}:
        return "black"
    if s in {"white", "w", "o", "2", "-1"}:
        return "white"
    return None


def board_size_from_row(row: dict[str, Any]) -> int:
    try:
        return int(row.get("board_size") or 15)
    except Exception:
        return 15


def empty_matrix(n: int) -> list[list[int]]:
    return [[0 for _ in range(n)] for _ in range(n)]


def place(matrix: list[list[int]], xy: Any, color: str, warnings: list[str]) -> None:
    parsed = parse_xy(xy)
    if parsed is None:
        warnings.append(f"could not parse stone coordinate: {xy!r}")
        return
    x, y = parsed
    n = len(matrix)
    if not (0 <= x < n and 0 <= y < n):
        warnings.append(f"stone coordinate out of bounds: {xy!r}")
        return
    matrix[y][x] = 1 if color == "black" else 2


def normalize_board(board: Any, row: dict[str, Any], warnings: list[str]) -> tuple[list[list[Any]] | None, str]:
    n = board_size_from_row(row)

    # Matrix: list[list[...]]
    if isinstance(board, list) and board and all(isinstance(r, list) for r in board):
        if all(len(r) == len(board[0]) for r in board):
            return board, "matrix_list"

    # Matrix: list[str]
    if isinstance(board, list) and board and all(isinstance(r, str) for r in board):
        return [list(r) for r in board], "matrix_strings"

    # Text grid: pretty board with border lines and 15 token rows.
    # Example rows:
    #   ------------------------------
    #   . . . . . . . X O . . . . . .
    #   ------------------------------
    if isinstance(board, str):
        s = board.strip()

        # Some sources may store JSON as a string. Try that first.
        if s.startswith("{") or s.startswith("["):
            try:
                parsed = json.loads(s)
                m, fmt = normalize_board(parsed, row, warnings)
                if m is not None:
                    return m, f"json_string_{fmt}"
            except Exception:
                pass

        valid_tokens = {".", "X", "O", "x", "o", "B", "W", "b", "w", "0", "1", "2", "_"}
        parsed_rows: list[list[str]] = []
        for line in board.splitlines():
            tokens = line.strip().split()
            if not tokens:
                continue
            if all(t in valid_tokens for t in tokens):
                parsed_rows.append(tokens)

        expected_n = board_size_from_row(row)
        if (
            len(parsed_rows) == expected_n
            and parsed_rows
            and all(len(r) == expected_n for r in parsed_rows)
        ):
            return parsed_rows, "text_grid"

        warnings.append(
            f"text board did not parse as {expected_n}x{expected_n}: "
            f"rows={len(parsed_rows)} lens={[len(r) for r in parsed_rows[:5]]}"
        )
        return None, "str_text_unparsed"

    # Dict wrappers.
    if isinstance(board, dict):
        for key in ["board", "grid", "matrix", "cells", "position"]:
            val = board.get(key)
            if val is not None and val is not board:
                m, fmt = normalize_board(val, row, warnings)
                if m is not None:
                    return m, f"dict_{key}_{fmt}"

        matrix = empty_matrix(n)

        black_keys = ["black", "black_stones", "black_positions", "black_moves", "b"]
        white_keys = ["white", "white_stones", "white_positions", "white_moves", "w"]

        found_bw = False
        for key in black_keys:
            if isinstance(board.get(key), list):
                found_bw = True
                for xy in board[key]:
                    place(matrix, xy, "black", warnings)
        for key in white_keys:
            if isinstance(board.get(key), list):
                found_bw = True
                for xy in board[key]:
                    place(matrix, xy, "white", warnings)

        if found_bw:
            return matrix, "dict_black_white_stones"

        # Generic stones/moves list.
        for key in ["stones", "moves", "move_history", "placements"]:
            stones = board.get(key)
            if isinstance(stones, list):
                found = False
                for s in stones:
                    if isinstance(s, dict):
                        color = None
                        for ck in ["color", "player", "side", "stone", "value"]:
                            if ck in s:
                                color = color_from_any(s[ck])
                                if color:
                                    break
                        xy = parse_xy(s)
                        if xy is None:
                            xy = parse_xy(s.get("xy") or s.get("pos") or s.get("move"))
                        if color and xy:
                            found = True
                            place(matrix, xy, color, warnings)
                    elif isinstance(s, (list, tuple)) and len(s) >= 3:
                        xy = parse_xy(s[:2])
                        color = color_from_any(s[2])
                        if color and xy:
                            found = True
                            place(matrix, xy, color, warnings)
                if found:
                    return matrix, f"dict_{key}_stones"

    return None, type(board).__name__


def expected_side_from_counts(black: int, white: int) -> str | None:
    if black == white:
        return "black"
    if black == white + 1:
        return "white"
    return None


def validate_row(row: dict[str, Any]) -> dict[str, Any]:
    result = {
        "id": row.get("id", ""),
        "split": row.get("split", ""),
        "role": row.get("role", ""),
        "source_id": row.get("source_id", ""),
        "side_to_move": str(row.get("side_to_move", "")).lower(),
        "policy_target": row.get("policy_target", ""),
        "board_size": row.get("board_size", ""),
        "board_format": "",
        "ok": True,
        "errors": [],
        "warnings": [],
        "target_cell_status": "",
        "black_count": "",
        "white_count": "",
        "empty_count": "",
        "unknown_count": "",
        "expected_side_from_counts": "",
    }

    def err(msg: str) -> None:
        result["ok"] = False
        result["errors"].append(msg)

    def warn(msg: str) -> None:
        result["warnings"].append(msg)

    split = result["split"]
    side = result["side_to_move"]

    if split == "heldout_retention" and not row.get("heldout"):
        err("heldout_retention row has false/missing heldout flag")
    if split == "train_teacher_divergence" and row.get("heldout"):
        err("train row has heldout flag")

    target = parse_xy(row.get("policy_target"))
    if target is None:
        err("invalid policy_target format")
        return result

    local_warnings: list[str] = []
    board, board_format = normalize_board(row.get("board"), row, local_warnings)
    result["board_format"] = board_format
    for msg in local_warnings:
        warn(msg)

    if board is None:
        err(f"unsupported or missing board format: {board_format}")
        return result

    n_rows = len(board)
    row_lengths = [len(r) for r in board]
    if not row_lengths or len(set(row_lengths)) != 1:
        err(f"ragged board row lengths: {row_lengths[:10]}")
        return result

    n_cols = row_lengths[0]
    try:
        bs = int(row.get("board_size") or n_rows)
        if bs != n_rows or bs != n_cols:
            err(f"board_size mismatch: board_size={bs}, shape={n_rows}x{n_cols}")
    except Exception:
        warn(f"non-integer board_size={row.get('board_size')!r}")

    x, y = target
    if not (0 <= x < n_cols and 0 <= y < n_rows):
        err(f"target out of bounds for shape={n_rows}x{n_cols}")
        return result

    target_status = classify_cell(board[y][x])
    result["target_cell_status"] = target_status
    if target_status != "empty":
        err(f"target is not empty: cell={board[y][x]!r} classified={target_status}")

    counts = Counter()
    for r in board:
        for cell in r:
            counts[classify_cell(cell)] += 1

    result["black_count"] = counts["black"]
    result["white_count"] = counts["white"]
    result["empty_count"] = counts["empty"]
    result["unknown_count"] = counts["unknown"]

    if counts["unknown"]:
        warn(f"unknown board cell encodings: {counts['unknown']} cells")

    expected = expected_side_from_counts(counts["black"], counts["white"])
    result["expected_side_from_counts"] = expected or ""
    if expected is None:
        warn(f"stone counts do not match normal black-first turn order: black={counts['black']} white={counts['white']}")
    elif side in {"black", "white"} and side != expected:
        # Keep this as warning for now because source schemas may count move_count differently.
        warn(f"side_to_move mismatch by counts: side={side}, expected_from_counts={expected}")
    elif side not in {"black", "white"}:
        warn(f"unexpected side_to_move={side!r}")

    return result



def clean_markdown_lines(lines: list[str]) -> str:
    cleaned = [line.rstrip() for line in lines]
    while cleaned and cleaned[-1] == "":
        cleaned.pop()
    return "\n".join(cleaned) + "\n"

def main() -> None:
    obj = json.loads(DATASET.read_text(encoding="utf-8"))
    rows = obj.get("rows", [])
    results = [validate_row(r) for r in rows]

    fields = [
        "id",
        "split",
        "role",
        "source_id",
        "side_to_move",
        "policy_target",
        "board_size",
        "board_format",
        "ok",
        "errors",
        "warnings",
        "target_cell_status",
        "black_count",
        "white_count",
        "empty_count",
        "unknown_count",
        "expected_side_from_counts",
    ]

    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for r in results:
            out = dict(r)
            out["errors"] = "; ".join(r["errors"])
            out["warnings"] = "; ".join(r["warnings"])
            writer.writerow(out)

    error_rows = [r for r in results if not r["ok"]]
    warning_rows = [r for r in results if r["warnings"]]
    split_counts = Counter(r["split"] for r in results)
    ok_by_split = defaultdict(Counter)
    for r in results:
        ok_by_split[r["split"]]["ok" if r["ok"] else "bad"] += 1

    lines = []
    lines.append("# Teacher divergence / retention validation")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append("Validate generated dataset rows only. This script does not train, export, or benchmark.")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Dataset: `{DATASET}`")
    lines.append(f"- Manifest: `{MANIFEST}`")
    lines.append(f"- Validation CSV: `{OUT_CSV}`")
    lines.append(f"- Total rows: {len(results)}")
    lines.append(f"- Error rows: {len(error_rows)}")
    lines.append(f"- Warning rows: {len(warning_rows)}")
    lines.append("")
    lines.append("### Split counts")
    lines.append("")
    lines.append("| split | rows | ok | bad |")
    lines.append("|---|---:|---:|---:|")
    for split, count in split_counts.most_common():
        lines.append(f"| `{split}` | {count} | {ok_by_split[split]['ok']} | {ok_by_split[split]['bad']} |")
    lines.append("")
    lines.append("### Board formats")
    lines.append("")
    lines.append("| board_format | rows |")
    lines.append("|---|---:|")
    for key, val in Counter(r["board_format"] for r in results).most_common():
        lines.append(f"| `{key}` | {val} |")
    lines.append("")
    lines.append("### Target cell status")
    lines.append("")
    lines.append("| status | rows |")
    lines.append("|---|---:|")
    for key, val in Counter(r["target_cell_status"] for r in results).most_common():
        lines.append(f"| `{key}` | {val} |")
    lines.append("")
    lines.append("## Errors")
    lines.append("")
    if error_rows:
        lines.append("| id | split | target | board_format | errors |")
        lines.append("|---|---|---|---|---|")
        for r in error_rows:
            lines.append(f"| `{r['id']}` | `{r['split']}` | `{r['policy_target']}` | `{r['board_format']}` | {'; '.join(r['errors'])} |")
    else:
        lines.append("No error rows.")
    lines.append("")
    lines.append("## Warnings")
    lines.append("")
    if warning_rows:
        lines.append("| id | split | target | board_format | warnings |")
        lines.append("|---|---|---|---|---|")
        for r in warning_rows[:80]:
            lines.append(f"| `{r['id']}` | `{r['split']}` | `{r['policy_target']}` | `{r['board_format']}` | {'; '.join(r['warnings'])} |")
        if len(warning_rows) > 80:
            lines.append(f"| ... | ... | ... | ... | {len(warning_rows) - 80} more warning rows |")
    else:
        lines.append("No warning rows.")
    lines.append("")

    OUT_MD.write_text(clean_markdown_lines(lines), encoding="utf-8")

    print(f"wrote {OUT_CSV}")
    print(f"wrote {OUT_MD}")
    print()
    print("=== validation summary ===")
    print("total rows:", len(results))
    print("error rows:", len(error_rows))
    print("warning rows:", len(warning_rows))
    print("split counts:", dict(split_counts))
    print("board formats:", dict(Counter(r["board_format"] for r in results)))
    print("target cell status:", dict(Counter(r["target_cell_status"] for r in results)))
    if error_rows:
        print()
        print("=== errors ===")
        for r in error_rows:
            print(r["id"], r["board_format"], r["errors"])
    if warning_rows:
        print()
        print("=== warnings head ===")
        for r in warning_rows[:20]:
            print(r["id"], r["board_format"], r["warnings"])


if __name__ == "__main__":
    main()
