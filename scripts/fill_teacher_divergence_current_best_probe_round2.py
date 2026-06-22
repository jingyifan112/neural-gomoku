#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
import torch
import torch.nn.functional as F

from gomoku_agent.checkpoint import load_compatible_checkpoint
from gomoku_agent.model import PolicyValueNet


BOARD_SIZE = 15
CHANNELS = 64
BLOCKS = 4

BOARD_SOURCE_PATHS = [
    Path("analysis/integration_eval/teacher_divergence_retention_clean_v2_dataset.json"),
    Path("analysis/integration_eval/teacher_divergence_retention_dataset.json"),
    Path("analysis/integration_eval/teacher_divergence_retention_safety_v3_dataset.json"),
    Path("analysis/integration_eval/teacher_divergence_retention_expanded_dataset.json"),
    Path("analysis/public_benchmark_eval/rapfi_teacher_policy_candidates_corpus8_selected.csv"),
    Path("analysis/public_benchmark_eval/rapfi_teacher_policy_margin_dataset_corpus8_selected.json"),
    Path("analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected.json"),
    Path("analysis/public_benchmark_eval/corpus8_selected_board_snapshots.json"),
    Path("analysis/rapfi_failure_board_snapshots.json"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fill current_best policy probe diagnostics for round2 teacher-divergence manifest rows."
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_expanded_candidate_manifest_with_board_joins.csv"),
    )
    parser.add_argument(
        "--checkpoint",
        type=Path,
        default=Path("checkpoints/15x15_current_best.pt"),
    )
    parser.add_argument(
        "--out-csv",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_current_best_probe_fill_round2.csv"),
    )
    parser.add_argument(
        "--out-report",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_current_best_probe_fill_round2_report.md"),
    )
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--expected-selected", type=int, default=140)
    parser.add_argument(
        "--illegal-status",
        default="skipped_invalid",
        choices=["skipped_invalid", "excluded_target_illegal"],
    )
    return parser.parse_args()


def is_blank(value: Any) -> bool:
    if value is None:
        return True
    s = str(value).strip()
    return s == "" or s.lower() in {"none", "nan", "na", "null"}


def is_true(value: Any) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def is_false_or_blank(value: Any) -> bool:
    return is_blank(value) or str(value).strip().lower() in {"0", "false", "no", "n"}


def parse_rc(value: Any) -> list[int] | None:
    if isinstance(value, (list, tuple)) and len(value) == 2:
        return [int(value[0]), int(value[1])]

    if is_blank(value):
        return None

    s = str(value).strip()
    try:
        obj = json.loads(s)
        if isinstance(obj, (list, tuple)) and len(obj) == 2:
            return [int(obj[0]), int(obj[1])]
    except Exception:
        pass

    nums = re.findall(r"-?\d+", s)
    if len(nums) >= 2:
        return [int(nums[0]), int(nums[1])]

    return None


def rc_to_action(rc: list[int]) -> int:
    r, c = int(rc[0]), int(rc[1])
    if not (0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE):
        raise ValueError(f"rc out of range: {rc}")
    return r * BOARD_SIZE + c


def action_to_rc(action: int) -> list[int]:
    return [int(action) // BOARD_SIZE, int(action) % BOARD_SIZE]


def parse_current_player(value: Any) -> int | None:
    if is_blank(value):
        return None

    s = str(value).strip().lower()
    if s in {"black", "b", "x", "1"}:
        return 1
    if s in {"white", "w", "o", "-1", "2"}:
        return -1

    try:
        v = int(float(s))
        if v == 1:
            return 1
        if v in {-1, 2}:
            return -1
    except Exception:
        return None

    return None


def infer_current_player_from_board(board: list[list[int]]) -> int:
    arr = np.asarray(board)
    black = int(np.sum(arr == 1))
    white = int(np.sum(arr == -1))
    return 1 if black == white else -1


def normalize_cell(value: Any) -> int:
    if isinstance(value, bool):
        return int(value)

    if isinstance(value, (int, float)):
        iv = int(value)
        if iv == 2:
            return -1
        if iv in {-1, 0, 1}:
            return iv

    s = str(value).strip()
    if s in {"1", "X", "x", "B", "b", "black"}:
        return 1
    if s in {"-1", "2", "O", "o", "W", "w", "white"}:
        return -1
    if s in {"0", ".", "_", "-", "empty"}:
        return 0

    raise ValueError(f"unknown board cell: {value!r}")


def normalize_board(obj: Any) -> list[list[int]]:
    if isinstance(obj, str):
        return parse_board_snapshot(obj)

    if not isinstance(obj, list) or len(obj) != BOARD_SIZE:
        raise ValueError(f"expected {BOARD_SIZE} board rows, got {type(obj)}")

    board: list[list[int]] = []
    for row in obj:
        if isinstance(row, str):
            parsed = parse_board_snapshot("\n".join([row]))
            if len(parsed) != 1:
                raise ValueError("string row expanded to unexpected row count")
            board.append(parsed[0])
        else:
            if not isinstance(row, list) or len(row) != BOARD_SIZE:
                raise ValueError(f"expected board row length {BOARD_SIZE}, got {row!r}")
            board.append([normalize_cell(x) for x in row])

    return board


def parse_board_snapshot(raw: str) -> list[list[int]]:
    s = str(raw).strip()
    if not s:
        raise ValueError("empty board snapshot")

    try:
        obj = json.loads(s)
        if isinstance(obj, list):
            return normalize_board(obj)
    except Exception:
        pass

    if "\\n" in s and "\n" not in s:
        s = s.replace("\\n", "\n")

    candidate_lines = [line.strip() for line in re.split(r"[\n;/]+", s) if line.strip()]
    rows: list[list[int]] = []

    for line in candidate_lines:
        tokens = [tok for tok in re.split(r"[\s,]+", line) if tok]
        if len(tokens) == BOARD_SIZE:
            rows.append([normalize_cell(tok) for tok in tokens])
            continue

        compact = line.replace(" ", "").replace(",", "")
        char_row = []
        for ch in compact:
            if ch in "XxBb1":
                char_row.append(1)
            elif ch in "OoWw2":
                char_row.append(-1)
            elif ch in "._0-":
                char_row.append(0)
            else:
                continue

        if len(char_row) == BOARD_SIZE:
            rows.append(char_row)

    if len(rows) != BOARD_SIZE:
        raise ValueError(f"could not parse {BOARD_SIZE}x{BOARD_SIZE} board snapshot; parsed_rows={len(rows)}")

    return rows


def extract_board(record: dict[str, Any]) -> list[list[int]] | None:
    for key in (
        "board",
        "board_before",
        "board_snapshot",
        "board_snapshot_before_decision",
        "position",
        "state_board",
    ):
        if key in record and not is_blank(record.get(key)):
            try:
                return normalize_board(record[key])
            except Exception:
                continue
    return None


def extract_current_player(record: dict[str, Any], board: list[list[int]]) -> int:
    for key in ("current_player", "side_to_move", "player", "turn"):
        if key in record:
            cp = parse_current_player(record.get(key))
            if cp in {1, -1}:
                return cp
    return infer_current_player_from_board(board)


def board_hash_variants(board: list[list[int]]) -> set[str]:
    grid = [[int(x) for x in row] for row in board]
    payloads = [
        json.dumps(grid, separators=(",", ":"), ensure_ascii=False),
        json.dumps(grid, ensure_ascii=False),
        "\n".join("".join("X" if x == 1 else "O" if x == -1 else "." for x in row) for row in grid),
        "".join(",".join(str(x) for x in row) for row in grid),
    ]
    return {hashlib.sha1(p.encode("utf-8")).hexdigest() for p in payloads}


def iter_json_records(obj: Any):
    if isinstance(obj, list):
        for item in obj:
            yield from iter_json_records(item)
        return

    if not isinstance(obj, dict):
        return

    if any(k in obj for k in ("board", "board_snapshot_before_decision", "board_snapshot", "board_before")):
        yield obj

    for key in ("samples", "positions", "rows", "records", "data"):
        value = obj.get(key)
        if isinstance(value, (list, dict)):
            yield from iter_json_records(value)


def add_board_record(
    board_map: dict[str, dict[str, Any]],
    record: dict[str, Any],
    source_path: Path,
) -> None:
    board = extract_board(record)
    if board is None:
        return

    cp = extract_current_player(record, board)
    hashes = set(board_hash_variants(board))

    for key in ("board_hash", "matched_board_hash", "position_hash"):
        value = record.get(key)
        if not is_blank(value):
            hashes.add(str(value).strip())

    for h in hashes:
        if not h:
            continue
        if h not in board_map:
            board_map[h] = {
                "board": board,
                "current_player": cp,
                "source": str(source_path),
            }


def load_board_map(paths: list[Path]) -> dict[str, dict[str, Any]]:
    board_map: dict[str, dict[str, Any]] = {}

    for path in paths:
        if not path.exists():
            continue

        if path.suffix.lower() == ".csv":
            with path.open(newline="", encoding="utf-8") as f:
                for record in csv.DictReader(f):
                    add_board_record(board_map, record, path)
            continue

        if path.suffix.lower() == ".json":
            obj = json.loads(path.read_text(encoding="utf-8"))
            for record in iter_json_records(obj):
                add_board_record(board_map, record, path)

    return board_map


def encode_state(board: list[list[int]], current_player: int) -> np.ndarray:
    grid = np.asarray(board, dtype=np.int8)
    if grid.shape != (BOARD_SIZE, BOARD_SIZE):
        raise ValueError(f"expected {BOARD_SIZE}x{BOARD_SIZE} board, got {grid.shape}")
    current = (grid == current_player).astype(np.float32)
    opponent = (grid == -current_player).astype(np.float32)
    last = np.zeros_like(current, dtype=np.float32)
    return np.stack([current, opponent, last], axis=0)


def legal_mask_from_board(board: list[list[int]]) -> np.ndarray:
    grid = np.asarray(board, dtype=np.int8)
    if grid.shape != (BOARD_SIZE, BOARD_SIZE):
        raise ValueError(f"expected {BOARD_SIZE}x{BOARD_SIZE} board, got {grid.shape}")
    return (grid.reshape(-1) == 0).astype(np.float32)


def load_model(checkpoint: Path, device: torch.device) -> PolicyValueNet:
    model = PolicyValueNet(board_size=BOARD_SIZE, channels=CHANNELS, blocks=BLOCKS).to(device)
    loaded = load_compatible_checkpoint(
        model,
        checkpoint,
        device,
        board_size=BOARD_SIZE,
        channels=CHANNELS,
        blocks=BLOCKS,
    )
    if not loaded:
        raise RuntimeError(f"could not load compatible checkpoint: {checkpoint}")
    model.eval()
    return model


@torch.no_grad()
def probe_board(
    model: PolicyValueNet,
    board: list[list[int]],
    current_player: int,
    target_rc: list[int],
    device: torch.device,
    top_k: int,
) -> dict[str, Any]:
    state = torch.tensor(encode_state(board, current_player), dtype=torch.float32, device=device).unsqueeze(0)
    legal_np = legal_mask_from_board(board)
    legal = torch.tensor(legal_np, dtype=torch.float32, device=device).unsqueeze(0)

    logits, _value = model(state)
    probs = F.softmax(logits.masked_fill(legal <= 0, -1e9), dim=-1)[0].detach().cpu().numpy()

    target_action = rc_to_action(target_rc)
    legal_actions = np.flatnonzero(legal_np > 0)
    target_legal = bool(legal_np[target_action] > 0)

    ranked = legal_actions[np.argsort(probs[legal_actions])[::-1]]
    top_actions = [int(x) for x in ranked[:top_k]]
    top_probs = [float(probs[x]) for x in top_actions]

    rank = None
    target_prob = 0.0
    if target_legal:
        where = np.where(ranked == target_action)[0]
        if len(where):
            rank = int(where[0]) + 1
        target_prob = float(probs[target_action])

    return {
        "target_action": int(target_action),
        "target_legal": target_legal,
        "before_target_rank": rank,
        "before_target_prob": target_prob,
        "current_best_direct_rc": action_to_rc(top_actions[0]) if top_actions else "",
        "current_best_direct_prob": top_probs[0] if top_probs else "",
        "current_best_top_policy_rcs": [action_to_rc(a) for a in top_actions],
        "current_best_top_policy_probs": top_probs,
    }


def bucket_for_rank(rank: int | None, legal: bool) -> str:
    if not legal or rank is None:
        return "unknown_rank"
    if rank <= 10:
        return "protected_top10"
    if rank <= 50:
        return "trainable_rank_11_50"
    return "tail_rank_gt50"


def select_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    selected = []
    for row in rows:
        if row.get("status") != "needs_current_best_probe":
            continue
        if not is_blank(row.get("duplicate_of")):
            continue
        if not is_true(row.get("board_available")):
            continue
        if is_blank(row.get("board_hash")):
            continue
        if not is_true(row.get("target_available")):
            continue
        if not is_true(row.get("side_available")):
            continue
        if not is_true(row.get("teacher_eval_available")):
            continue
        if not is_false_or_blank(row.get("rank_prob_available")):
            continue
        selected.append(row)
    return selected


def output_fields() -> list[str]:
    return [
        "manifest_id",
        "status_before",
        "status_after",
        "bucket_before",
        "bucket_after",
        "primary_source_path",
        "source_class",
        "case_id",
        "game_number",
        "move_count",
        "current_player",
        "target_rc",
        "target_action",
        "target_legal",
        "before_target_rank",
        "before_target_prob",
        "current_best_direct_rc",
        "current_best_direct_prob",
        "current_best_top_policy_rcs",
        "current_best_top_policy_probs",
        "board_hash",
        "probe_source",
        "excluded",
        "exclude_reason",
        "needs_current_best_probe_after",
        "needs_suppress_build_after",
        "notes",
    ]


def write_report(args: argparse.Namespace, rows: list[dict[str, Any]], board_source_count: int) -> None:
    status_counts = Counter(r["status_after"] for r in rows)
    bucket_counts = Counter(r["bucket_after"] for r in rows)
    legal_rows = [r for r in rows if r["target_legal"] == "1"]
    illegal_rows = [r for r in rows if r["target_legal"] == "0"]

    lines = [
        "# Teacher-divergence current_best probe fill round2 report",
        "",
        "## Branch",
        "",
        "`exp/15x15-teacher-divergence-current-best-probe-fill-round2`",
        "",
        "## Scope",
        "",
        "- Fill current_best rank/prob/direct move only.",
        "- Selected manifest rows with status `needs_current_best_probe`.",
        "- Does not process `needs_rapfi_requery` rows.",
        "- Does not process `needs_board_join` rows.",
        "- No training.",
        "- No checkpoint save.",
        "- No C export.",
        "- No public benchmark.",
        "- No promotion.",
        "",
        "## Inputs",
        "",
        f"- manifest: `{args.manifest}`",
        f"- checkpoint used for inference: `{args.checkpoint}`",
        f"- board source records indexed by hash: {board_source_count}",
        f"- selected rows: {len(rows)}",
        "",
        "## Summary",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| rows selected | {len(rows)} |",
        f"| legal target rows | {len(legal_rows)} |",
        f"| illegal target rows | {len(illegal_rows)} |",
        "",
        "## Status after fill",
        "",
        "| status_after | rows |",
        "|---|---:|",
    ]

    for key, value in status_counts.most_common():
        lines.append(f"| {key} | {value} |")

    lines.extend([
        "",
        "## Bucket after fill",
        "",
        "| bucket_after | rows |",
        "|---|---:|",
    ])

    for key, value in bucket_counts.most_common():
        lines.append(f"| {key} | {value} |")

    lines.extend([
        "",
        "## Filled rows preview",
        "",
        "| manifest_id | status_after | bucket_after | target_rc | rank | prob | direct_rc | excluded | notes |",
        "|---|---|---|---|---:|---:|---|---:|---|",
    ])

    for r in rows[:80]:
        rank = r["before_target_rank"] if r["before_target_rank"] != "" else "NA"
        prob = r["before_target_prob"] if r["before_target_prob"] != "" else "NA"
        lines.append(
            "| {manifest_id} | {status_after} | {bucket_after} | `{target_rc}` | {rank} | {prob} | `{direct}` | {excluded} | {notes} |".format(
                manifest_id=r["manifest_id"],
                status_after=r["status_after"],
                bucket_after=r["bucket_after"],
                target_rc=r["target_rc"],
                rank=rank,
                prob=prob,
                direct=r["current_best_direct_rc"],
                excluded=r["excluded"],
                notes=r["notes"],
            )
        )

    if len(rows) > 80:
        lines.append(f"| . | . | . | . | . | . | . | . | {len(rows) - 80} more rows in CSV |")

    lines.extend([
        "",
        "## Interpretation",
        "",
        "Legal probed rows now have current_best policy rank/prob/direct-move diagnostics and should proceed to suppress candidate build.",
        "",
        "Illegal target rows are excluded/skipped invalid and must not enter suppress build or training.",
        "",
        "## Decision",
        "",
        "No training.",
        "",
        "No checkpoint.",
        "",
        "No C export.",
        "",
        "No public benchmark.",
        "",
        "No promotion.",
        "",
    ])

    args.out_report.parent.mkdir(parents=True, exist_ok=True)
    args.out_report.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()

    manifest_rows = list(csv.DictReader(args.manifest.open(newline="", encoding="utf-8")))
    selected = select_rows(manifest_rows)

    if len(selected) != args.expected_selected:
        raise RuntimeError(f"expected {args.expected_selected} selected rows, got {len(selected)}")

    board_map = load_board_map(BOARD_SOURCE_PATHS)

    device = torch.device(args.device)
    model = load_model(args.checkpoint, device)

    print(f"loaded {args.checkpoint}")
    print(f"device: {device}")
    print(f"selected_rows: {len(selected)}")
    print(f"board_hash_records: {len(board_map)}")

    out_rows: list[dict[str, Any]] = []

    for row in selected:
        manifest_id = row.get("manifest_id", "")
        board_hash = str(row.get("board_hash", "")).strip()
        target_rc = parse_rc(row.get("target_rc"))
        bucket_before = row.get("bucket", "")

        base = {
            "manifest_id": manifest_id,
            "status_before": row.get("status", ""),
            "bucket_before": bucket_before,
            "primary_source_path": row.get("primary_source_path", ""),
            "source_class": row.get("source_class", ""),
            "case_id": row.get("case_id", ""),
            "game_number": row.get("game_number", ""),
            "move_count": row.get("move_count", ""),
            "target_rc": json.dumps(target_rc) if target_rc is not None else "",
            "board_hash": board_hash,
        }

        if target_rc is None:
            out_rows.append({
                **base,
                "status_after": args.illegal_status,
                "bucket_after": "unknown_rank",
                "current_player": row.get("current_player", ""),
                "target_action": "",
                "target_legal": "0",
                "before_target_rank": "",
                "before_target_prob": "",
                "current_best_direct_rc": "",
                "current_best_direct_prob": "",
                "current_best_top_policy_rcs": "[]",
                "current_best_top_policy_probs": "[]",
                "probe_source": "",
                "excluded": "1",
                "exclude_reason": "target_rc_parse_failed",
                "needs_current_best_probe_after": "0",
                "needs_suppress_build_after": "0",
                "notes": "excluded_target_invalid",
            })
            continue

        board_record = board_map.get(board_hash)
        if board_record is None:
            out_rows.append({
                **base,
                "status_after": "needs_board_repair",
                "bucket_after": "unknown_rank",
                "current_player": row.get("current_player", ""),
                "target_action": rc_to_action(target_rc),
                "target_legal": "",
                "before_target_rank": "",
                "before_target_prob": "",
                "current_best_direct_rc": "",
                "current_best_direct_prob": "",
                "current_best_top_policy_rcs": "[]",
                "current_best_top_policy_probs": "[]",
                "probe_source": "",
                "excluded": "1",
                "exclude_reason": "board_hash_not_reconstructed",
                "needs_current_best_probe_after": "1",
                "needs_suppress_build_after": "0",
                "notes": "board_repair_needed",
            })
            continue

        board = board_record["board"]
        cp = parse_current_player(row.get("current_player"))
        if cp is None:
            cp = int(board_record["current_player"])

        probe = probe_board(
            model=model,
            board=board,
            current_player=cp,
            target_rc=target_rc,
            device=device,
            top_k=args.top_k,
        )

        target_legal = bool(probe["target_legal"])
        rank = probe["before_target_rank"]
        bucket_after = bucket_for_rank(rank, target_legal)

        if target_legal and rank is not None:
            status_after = "needs_suppress_build"
            excluded = "0"
            exclude_reason = ""
            needs_current_best_probe_after = "0"
            needs_suppress_build_after = "1"
            notes = "rank_prob_filled_but_suppress_missing"
        else:
            status_after = args.illegal_status
            excluded = "1"
            exclude_reason = "target_illegal"
            needs_current_best_probe_after = "0"
            needs_suppress_build_after = "0"
            notes = "excluded_target_illegal"

        out_rows.append({
            **base,
            "status_after": status_after,
            "bucket_after": bucket_after,
            "current_player": str(cp),
            "target_action": str(probe["target_action"]),
            "target_legal": "1" if target_legal else "0",
            "before_target_rank": "" if rank is None else str(rank),
            "before_target_prob": str(probe["before_target_prob"]),
            "current_best_direct_rc": json.dumps(probe["current_best_direct_rc"]),
            "current_best_direct_prob": str(probe["current_best_direct_prob"]),
            "current_best_top_policy_rcs": json.dumps(probe["current_best_top_policy_rcs"]),
            "current_best_top_policy_probs": json.dumps(probe["current_best_top_policy_probs"]),
            "probe_source": board_record["source"],
            "excluded": excluded,
            "exclude_reason": exclude_reason,
            "needs_current_best_probe_after": needs_current_best_probe_after,
            "needs_suppress_build_after": needs_suppress_build_after,
            "notes": notes,
        })

    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=output_fields(), lineterminator="\n")
        writer.writeheader()
        writer.writerows(out_rows)

    write_report(args, out_rows, len(board_map))

    print(f"filled_rows: {len(out_rows)}")
    print(f"status_after_counts: {json.dumps(dict(Counter(r['status_after'] for r in out_rows)), sort_keys=True)}")
    print(f"bucket_after_counts: {json.dumps(dict(Counter(r['bucket_after'] for r in out_rows)), sort_keys=True)}")
    print(f"out_csv: {args.out_csv}")
    print(f"out_report: {args.out_report}")
    print("no training; no checkpoint saved")


if __name__ == "__main__":
    main()
