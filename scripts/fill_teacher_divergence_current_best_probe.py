from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

import torch

from build_teacher_divergence_expanded_manifest import (
    SOURCE_SPECS,
    board_from_row,
    load_rows,
    normalize_board,
    normalize_row,
    parse_rc,
)

from train_rapfi_teacher_policy_margin import (
    BOARD_SIZE,
    encode_state,
    load_model,
    rc_to_action,
)


OUT_FIELDS = [
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
    "needs_current_best_probe_after",
    "needs_suppress_build_after",
    "notes",
]


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Fill current_best rank/prob/direct move for manifest rows marked needs_current_best_probe."
    )
    ap.add_argument(
        "--manifest",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_expanded_candidate_manifest.csv"),
    )
    ap.add_argument(
        "--checkpoint",
        type=Path,
        default=Path("checkpoints/15x15_current_best.pt"),
    )
    ap.add_argument(
        "--out-csv",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_current_best_probe_fill.csv"),
    )
    ap.add_argument(
        "--out-report",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_current_best_probe_fill_report.md"),
    )
    ap.add_argument("--top-k", type=int, default=10)
    return ap.parse_args()


def read_manifest(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def reconstruct_raw_rows_by_manifest_id() -> dict[str, dict[str, Any]]:
    raw_by_manifest_id: dict[str, dict[str, Any]] = {}
    idx = 1
    for spec in SOURCE_SPECS:
        path = Path(spec["path"])
        raw_rows = load_rows(path)
        for raw in raw_rows:
            norm = normalize_row(raw, spec, idx)
            raw_by_manifest_id[norm["manifest_id"]] = raw
            idx += 1
    return raw_by_manifest_id


def int_cell(value: Any) -> int:
    if isinstance(value, bool):
        return int(value)
    return int(float(value))


def call_encode_state(board: list[list[int]], current_player: int) -> torch.Tensor:
    try:
        encoded = encode_state(board, current_player)
    except TypeError:
        encoded = encode_state(board, current_player, BOARD_SIZE)

    if not torch.is_tensor(encoded):
        encoded = torch.tensor(encoded, dtype=torch.float32)
    else:
        encoded = encoded.float()

    if encoded.ndim == 3:
        encoded = encoded.unsqueeze(0)
    return encoded


def policy_logits_from_model(model: torch.nn.Module, x: torch.Tensor) -> torch.Tensor:
    out = model(x)
    if isinstance(out, dict):
        for key in ["policy_logits", "policy", "logits"]:
            if key in out:
                logits = out[key]
                break
        else:
            raise ValueError(f"model output dict missing policy logits keys: {sorted(out.keys())}")
    elif isinstance(out, (tuple, list)):
        logits = out[0]
    else:
        logits = out

    if logits.ndim == 2:
        logits = logits[0]
    return logits.reshape(-1)


def action_from_rc(rc: tuple[int, int]) -> int:
    r, c = rc
    try:
        return int(rc_to_action(r, c))
    except TypeError:
        return int(rc_to_action(rc))


def rc_from_action(action: int) -> list[int]:
    return [int(action // BOARD_SIZE), int(action % BOARD_SIZE)]


def legal_mask_from_board_local(board: list[list[int]], device: torch.device) -> torch.Tensor:
    flat = []
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            flat.append(int_cell(board[r][c]) == 0)
    return torch.tensor(flat, dtype=torch.bool, device=device)


def rank_bucket(rank: int | None) -> str:
    if rank is None:
        return "unknown_rank"
    if rank <= 10:
        return "protected_top10"
    if rank <= 50:
        return "trainable_rank_11_50"
    return "tail_rank_gt50"


def compute_policy_probe(
    model: torch.nn.Module,
    board: list[list[int]],
    current_player: int,
    target_rc: tuple[int, int],
    top_k: int,
    device: torch.device,
) -> dict[str, Any]:
    x = call_encode_state(board, current_player).to(device)
    legal = legal_mask_from_board_local(board, device)

    target_action = action_from_rc(target_rc)
    target_legal = bool(legal[target_action].item())

    with torch.no_grad():
        logits = policy_logits_from_model(model, x)
        logits = logits.to(device)
        masked_logits = logits.clone()
        masked_logits[~legal] = -1e30
        probs = torch.softmax(masked_logits, dim=0)

    target_prob = float(probs[target_action].item()) if target_legal else 0.0

    legal_probs = probs[legal]
    if target_legal:
        target_rank = int((legal_probs > target_prob).sum().item()) + 1
    else:
        target_rank = None

    k = min(top_k, int(legal.sum().item()))
    top_probs, top_actions = torch.topk(probs, k=k)
    top_rcs = [rc_from_action(int(a.item())) for a in top_actions]
    top_prob_values = [float(p.item()) for p in top_probs]

    direct_action = int(top_actions[0].item())
    direct_prob = float(top_probs[0].item())

    return {
        "target_action": target_action,
        "target_legal": target_legal,
        "target_rank": target_rank,
        "target_prob": target_prob,
        "direct_rc": rc_from_action(direct_action),
        "direct_prob": direct_prob,
        "top_rcs": top_rcs,
        "top_probs": top_prob_values,
    }


def status_after_fill(manifest_row: dict[str, str]) -> tuple[str, int, int, str]:
    suppress_available = manifest_row.get("suppress_available", "0") == "1"
    teacher_eval_available = manifest_row.get("teacher_eval_available", "0") == "1"
    board_available = manifest_row.get("board_available", "0") == "1"
    side_available = manifest_row.get("side_available", "0") == "1"
    target_available = manifest_row.get("target_available", "0") == "1"

    if not side_available or not target_available:
        return "skipped_invalid", 1, int(not suppress_available), "missing_side_or_target"
    if not board_available:
        return "needs_board_join", 1, int(not suppress_available), "missing_board"
    if not teacher_eval_available:
        return "needs_rapfi_requery", 1, int(not suppress_available), "missing_teacher_eval"
    if not suppress_available:
        return "needs_suppress_build", 0, 1, "rank_prob_filled_but_suppress_missing"
    return "ready_full_schema", 0, 0, "rank_prob_filled"


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=OUT_FIELDS, lineterminator="\n")
        w.writeheader()
        for row in rows:
            w.writerow({field: row.get(field, "") for field in OUT_FIELDS})


def count_by(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
    out: dict[str, int] = {}
    for row in rows:
        value = str(row.get(key, ""))
        out[value] = out.get(value, 0) + 1
    return dict(sorted(out.items(), key=lambda kv: (-kv[1], kv[0])))


def write_report(
    path: Path,
    args: argparse.Namespace,
    selected: list[dict[str, str]],
    rows: list[dict[str, Any]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    lines += ["# Teacher-divergence current_best probe fill report", ""]
    lines += ["## Branch", "", "`exp/15x15-teacher-divergence-current-best-probe-fill`", ""]
    lines += ["## Scope", ""]
    lines += [
        "- Fill current_best rank/prob/direct move only.",
        "- Selected manifest rows with status `needs_current_best_probe`.",
        "- No training.",
        "- No checkpoint save.",
        "- No C export.",
        "- No public benchmark.",
        "- No promotion.",
        "",
    ]

    lines += ["## Inputs", ""]
    lines += [
        f"- manifest: `{args.manifest}`",
        f"- checkpoint used for inference: `{args.checkpoint}`",
        f"- selected rows: {len(selected)}",
        "",
    ]

    lines += ["## Summary", ""]
    lines += ["| metric | value |", "|---|---:|"]
    lines += [
        f"| rows selected | {len(selected)} |",
        f"| rows filled | {len(rows)} |",
        f"| target legal rows | {sum(1 for r in rows if str(r['target_legal']) == 'True')} |",
        "",
    ]

    lines += ["## Status after fill", ""]
    lines += ["| status_after | rows |", "|---|---:|"]
    for key, n in count_by(rows, "status_after").items():
        lines.append(f"| {key} | {n} |")
    lines.append("")

    lines += ["## Bucket after fill", ""]
    lines += ["| bucket_after | rows |", "|---|---:|"]
    for key, n in count_by(rows, "bucket_after").items():
        lines.append(f"| {key} | {n} |")
    lines.append("")

    lines += ["## Filled rows", ""]
    lines += [
        "| manifest_id | status_after | bucket_after | target_rc | rank | prob | direct_rc | notes |",
        "|---|---|---|---|---:|---:|---|---|",
    ]
    for r in rows:
        rank = r["before_target_rank"] if r["before_target_rank"] != "" else "NA"
        prob = r["before_target_prob"] if r["before_target_prob"] != "" else "NA"
        lines.append(
            f"| {r['manifest_id']} | {r['status_after']} | {r['bucket_after']} | "
            f"`{r['target_rc']}` | {rank} | {prob} | `{r['current_best_direct_rc']}` | {r['notes']} |"
        )
    lines.append("")

    lines += ["## Interpretation", ""]
    lines += [
        "This branch only fills current_best policy diagnostics for rows that already had board, side, and target fields.",
        "",
        "Rows that become `needs_suppress_build` are not ready for training yet. They need suppress candidates and suppress-gap diagnostics before any dataset build.",
        "",
    ]

    lines += ["## Decision", ""]
    lines += [
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
    ]

    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    args = parse_args()

    manifest = read_manifest(args.manifest)
    selected = [
        r for r in manifest
        if r.get("status") == "needs_current_best_probe"
        and r.get("duplicate_of", "") == ""
    ]

    raw_by_manifest_id = reconstruct_raw_rows_by_manifest_id()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = load_model(args.checkpoint, device)
    model.eval()

    out_rows: list[dict[str, Any]] = []

    for row in selected:
        manifest_id = row["manifest_id"]
        raw = raw_by_manifest_id.get(manifest_id)
        if raw is None:
            raise RuntimeError(f"could not reconstruct raw row for {manifest_id}")

        board = normalize_board(board_from_row(raw))
        if board is None:
            raise RuntimeError(f"selected row missing board after reconstruction: {manifest_id}")

        target = parse_rc(row["target_rc"])
        if target is None:
            raise RuntimeError(f"selected row missing target_rc: {manifest_id}")

        current_player = int(row["current_player"])
        probe = compute_policy_probe(
            model=model,
            board=board,
            current_player=current_player,
            target_rc=target,
            top_k=args.top_k,
            device=device,
        )

        rank = probe["target_rank"]
        status_after, needs_current_best_probe_after, needs_suppress_build_after, note = status_after_fill(row)
        bucket_after = rank_bucket(rank)

        out_rows.append(
            {
                "manifest_id": manifest_id,
                "status_before": row["status"],
                "status_after": status_after,
                "bucket_before": row["bucket"],
                "bucket_after": bucket_after,
                "primary_source_path": row["primary_source_path"],
                "source_class": row["source_class"],
                "case_id": row["case_id"],
                "game_number": row["game_number"],
                "move_count": row["move_count"],
                "current_player": current_player,
                "target_rc": row["target_rc"],
                "target_action": probe["target_action"],
                "target_legal": probe["target_legal"],
                "before_target_rank": "" if rank is None else rank,
                "before_target_prob": probe["target_prob"],
                "current_best_direct_rc": json.dumps(probe["direct_rc"]),
                "current_best_direct_prob": probe["direct_prob"],
                "current_best_top_policy_rcs": json.dumps(probe["top_rcs"]),
                "current_best_top_policy_probs": json.dumps(probe["top_probs"]),
                "needs_current_best_probe_after": needs_current_best_probe_after,
                "needs_suppress_build_after": needs_suppress_build_after,
                "notes": note,
            }
        )

    write_csv(args.out_csv, out_rows)
    write_report(args.out_report, args, selected, out_rows)

    print("device:", device)
    print("selected_rows:", len(selected))
    print("filled_rows:", len(out_rows))
    print("status_after_counts:", json.dumps(count_by(out_rows, "status_after"), sort_keys=True))
    print("bucket_after_counts:", json.dumps(count_by(out_rows, "bucket_after"), sort_keys=True))
    print("out_csv:", args.out_csv)
    print("out_report:", args.out_report)
    print("no training; no checkpoint saved")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
