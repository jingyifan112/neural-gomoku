#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
import torch

from fill_teacher_divergence_current_best_probe_round2 import BOARD_SOURCE_PATHS, load_board_map
from train_rapfi_teacher_policy_margin import (
    BOARD_SIZE,
    encode_state,
    legal_mask_from_board,
    load_model,
    masked_softmax,
    parse_board_snapshot,
    parse_side_to_move,
    rank_of_action,
    rc_to_action,
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Post-training guard audit for tiny teacher-divergence policy-margin probe."
    )
    p.add_argument("--baseline-checkpoint", type=Path, default=Path("checkpoints/15x15_current_best.pt"))
    p.add_argument("--candidate-checkpoint", type=Path, default=Path("checkpoints/15x15_teacher_divergence_round2_policy_margin_tiny_probe_e3.pt"))
    p.add_argument("--trainer-ready-dataset", type=Path, default=Path("analysis/integration_eval/teacher_divergence_round2_trainable_trainer_ready_dataset.json"))
    p.add_argument("--manifest", type=Path, default=Path("analysis/integration_eval/teacher_divergence_expanded_candidate_manifest_legacy_suppress_normalized.csv"))
    p.add_argument("--anchor-snapshots", type=Path, default=Path("analysis/public_benchmark_eval/corpus8_selected_board_snapshots.json"))
    p.add_argument("--out-trainable-csv", type=Path, default=Path("analysis/integration_eval/teacher_divergence_tiny_posttrain_trainable_gap_guard.csv"))
    p.add_argument("--out-bucket-csv", type=Path, default=Path("analysis/integration_eval/teacher_divergence_tiny_posttrain_manifest_bucket_guard.csv"))
    p.add_argument("--out-anchor-csv", type=Path, default=Path("analysis/integration_eval/teacher_divergence_tiny_posttrain_anchor_drift_guard.csv"))
    p.add_argument("--out-report", type=Path, default=Path("analysis/integration_eval/teacher_divergence_tiny_posttrain_guard_audit.md"))
    p.add_argument("--expected-trainable", type=int, default=44)
    return p.parse_args()


def is_blank(value: Any) -> bool:
    if value is None:
        return True
    s = str(value).strip()
    return s == "" or s.lower() in {"none", "nan", "na", "null"}


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def parse_json_rc(value: str) -> list[int] | None:
    if is_blank(value):
        return None
    try:
        obj = json.loads(value)
    except Exception:
        return None
    if not isinstance(obj, list) or len(obj) != 2:
        return None
    rc = [int(obj[0]), int(obj[1])]
    if not (0 <= rc[0] < BOARD_SIZE and 0 <= rc[1] < BOARD_SIZE):
        return None
    return rc


def ready_bucket(row: dict[str, str]) -> str:
    return row.get("ready_bucket") or row.get("bucket") or ""


def model_eval(
    model: torch.nn.Module,
    board: list[list[int]],
    current_player: int,
    rc: list[int],
    device: torch.device,
) -> dict[str, Any]:
    state = torch.tensor(encode_state(board, current_player), dtype=torch.float32, device=device).unsqueeze(0)
    mask_np = legal_mask_from_board(board)
    mask = torch.tensor(mask_np, dtype=torch.float32, device=device).unsqueeze(0)

    with torch.no_grad():
        logits, _values = model(state)
        probs = masked_softmax(logits, mask)[0]
        logits0 = logits[0]
        mask0 = mask[0]

    action = rc_to_action(rc)
    legal = bool(mask_np[action] > 0)
    if not legal:
        return {
            "legal": False,
            "action": action,
            "prob": float("nan"),
            "rank": -1,
            "logit": float("nan"),
        }

    return {
        "legal": True,
        "action": action,
        "prob": float(probs[action].item()),
        "rank": int(rank_of_action(probs, action, mask0)),
        "logit": float(logits0[action].item()),
    }


def model_pair_eval(
    model: torch.nn.Module,
    board: list[list[int]],
    current_player: int,
    target_rc: list[int],
    suppress_rc: list[int],
    device: torch.device,
) -> dict[str, Any]:
    t = model_eval(model, board, current_player, target_rc, device)
    s = model_eval(model, board, current_player, suppress_rc, device)
    return {
        "target": t,
        "suppress": s,
        "gap": float(t["logit"] - s["logit"]) if t["legal"] and s["legal"] else float("nan"),
    }


def anchor_eval(
    model: torch.nn.Module,
    board: list[list[int]],
    current_player: int,
    device: torch.device,
) -> dict[str, Any]:
    state = torch.tensor(encode_state(board, current_player), dtype=torch.float32, device=device).unsqueeze(0)
    mask = torch.tensor(legal_mask_from_board(board), dtype=torch.float32, device=device).unsqueeze(0)
    with torch.no_grad():
        logits, _values = model(state)
        probs = masked_softmax(logits, mask)[0]
    legal_actions = torch.nonzero(mask[0] > 0, as_tuple=False).flatten()
    top_action = int(legal_actions[torch.argmax(probs[legal_actions])].item())
    top_prob = float(probs[top_action].item())
    return {
        "probs": probs.detach().cpu(),
        "top_action": top_action,
        "top_rc": [top_action // BOARD_SIZE, top_action % BOARD_SIZE],
        "top_prob": top_prob,
    }


def kl_divergence(ref_probs: torch.Tensor, cand_probs: torch.Tensor) -> float:
    ref = ref_probs.clamp_min(1e-12)
    cand = cand_probs.clamp_min(1e-12)
    return float((ref * (torch.log(ref) - torch.log(cand))).sum().item())


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    args = parse_args()

    for p in [
        args.baseline_checkpoint,
        args.candidate_checkpoint,
        args.trainer_ready_dataset,
        args.manifest,
        args.anchor_snapshots,
    ]:
        if not p.exists():
            raise FileNotFoundError(p)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    baseline = load_model(args.baseline_checkpoint, device)
    candidate = load_model(args.candidate_checkpoint, device)
    baseline.eval()
    candidate.eval()

    dataset = json.loads(args.trainer_ready_dataset.read_text(encoding="utf-8"))
    train_samples = dataset["samples"]
    if len(train_samples) != args.expected_trainable:
        raise RuntimeError(f"expected {args.expected_trainable} trainable samples, got {len(train_samples)}")

    trainable_rows: list[dict[str, Any]] = []
    for i, sample in enumerate(train_samples):
        case_id = sample["case_id"]
        board = sample["board"]
        current_player = int(sample["current_player"])
        target_rc = [int(x) for x in sample["target_rc"]]
        suppress_rc = [int(x) for x in sample["suppress_rc"]]

        b = model_pair_eval(baseline, board, current_player, target_rc, suppress_rc, device)
        c = model_pair_eval(candidate, board, current_player, target_rc, suppress_rc, device)

        if not b["target"]["legal"] or not b["suppress"]["legal"] or not c["target"]["legal"] or not c["suppress"]["legal"]:
            raise RuntimeError(f"{case_id}: illegal target/suppress during guard eval")

        trainable_rows.append({
            "row_index": i,
            "case_id": case_id,
            "manifest_id": sample.get("manifest_id", ""),
            "target_rc": json.dumps(target_rc),
            "suppress_rc": json.dumps(suppress_rc),
            "target_prob_before": f"{b['target']['prob']:.10f}",
            "target_prob_after": f"{c['target']['prob']:.10f}",
            "target_prob_delta": f"{c['target']['prob'] - b['target']['prob']:.10f}",
            "suppress_prob_before": f"{b['suppress']['prob']:.10f}",
            "suppress_prob_after": f"{c['suppress']['prob']:.10f}",
            "suppress_prob_delta": f"{c['suppress']['prob'] - b['suppress']['prob']:.10f}",
            "target_rank_before": b["target"]["rank"],
            "target_rank_after": c["target"]["rank"],
            "target_rank_delta": c["target"]["rank"] - b["target"]["rank"],
            "suppress_rank_before": b["suppress"]["rank"],
            "suppress_rank_after": c["suppress"]["rank"],
            "suppress_rank_delta": c["suppress"]["rank"] - b["suppress"]["rank"],
            "gap_before": f"{b['gap']:.10f}",
            "gap_after": f"{c['gap']:.10f}",
            "gap_delta": f"{c['gap'] - b['gap']:.10f}",
            "gap_improved": 1 if c["gap"] > b["gap"] else 0,
            "target_prob_improved": 1 if c["target"]["prob"] > b["target"]["prob"] else 0,
            "target_rank_improved": 1 if c["target"]["rank"] < b["target"]["rank"] else 0,
            "target_rank_regressed": 1 if c["target"]["rank"] > b["target"]["rank"] else 0,
        })

    _fields, manifest_rows = read_csv(args.manifest)
    nondup = [r for r in manifest_rows if is_blank(r.get("duplicate_of"))]
    guard_manifest_rows = [
        r for r in nondup
        if r.get("status") == "ready_full_schema"
        and ready_bucket(r) in {"protected_top10", "tail_rank_gt50"}
    ]

    board_map = load_board_map(BOARD_SOURCE_PATHS)
    bucket_rows: list[dict[str, Any]] = []

    for row in guard_manifest_rows:
        mid = row.get("manifest_id", "")
        bucket = ready_bucket(row)
        target_rc = parse_json_rc(row.get("target_rc", ""))
        board_hash = row.get("board_hash", "").strip()
        if target_rc is None:
            bucket_rows.append({
                "manifest_id": mid,
                "ready_bucket": bucket,
                "status": "skipped_missing_target_rc",
            })
            continue
        record = board_map.get(board_hash)
        if record is None:
            bucket_rows.append({
                "manifest_id": mid,
                "ready_bucket": bucket,
                "status": "skipped_missing_board",
            })
            continue

        cp_raw = row.get("current_player", "")
        current_player = int(float(cp_raw)) if not is_blank(cp_raw) else int(record["current_player"])

        b = model_eval(baseline, record["board"], current_player, target_rc, device)
        c = model_eval(candidate, record["board"], current_player, target_rc, device)

        if not b["legal"] or not c["legal"]:
            status = "target_illegal"
        else:
            status = "evaluated"

        bucket_rows.append({
            "manifest_id": mid,
            "ready_bucket": bucket,
            "case_id": row.get("case_id", ""),
            "target_rc": json.dumps(target_rc),
            "status": status,
            "target_prob_before": "" if not b["legal"] else f"{b['prob']:.10f}",
            "target_prob_after": "" if not c["legal"] else f"{c['prob']:.10f}",
            "target_prob_delta": "" if not b["legal"] or not c["legal"] else f"{c['prob'] - b['prob']:.10f}",
            "target_rank_before": "" if not b["legal"] else b["rank"],
            "target_rank_after": "" if not c["legal"] else c["rank"],
            "target_rank_delta": "" if not b["legal"] or not c["legal"] else c["rank"] - b["rank"],
            "target_prob_regressed": "" if not b["legal"] or not c["legal"] else (1 if c["prob"] < b["prob"] else 0),
            "target_rank_regressed": "" if not b["legal"] or not c["legal"] else (1 if c["rank"] > b["rank"] else 0),
        })

    anchors_raw = json.loads(args.anchor_snapshots.read_text(encoding="utf-8"))
    anchor_rows: list[dict[str, Any]] = []
    for i, item in enumerate(anchors_raw):
        board = parse_board_snapshot(item["board_snapshot_before_decision"])
        current_player = parse_side_to_move(item["side_to_move"])

        b = anchor_eval(baseline, board, current_player, device)
        c = anchor_eval(candidate, board, current_player, device)
        kl = kl_divergence(b["probs"], c["probs"])

        anchor_rows.append({
            "anchor_index": i,
            "case_id": f"anchor_g{item.get('game_number')}_m{item.get('move_count')}",
            "game_number": item.get("game_number", ""),
            "move_count": item.get("move_count", ""),
            "side_to_move": item.get("side_to_move", ""),
            "baseline_top_action": b["top_action"],
            "candidate_top_action": c["top_action"],
            "baseline_top_rc": json.dumps(b["top_rc"]),
            "candidate_top_rc": json.dumps(c["top_rc"]),
            "top1_changed": 1 if b["top_action"] != c["top_action"] else 0,
            "baseline_top_prob": f"{b['top_prob']:.10f}",
            "candidate_top_prob": f"{c['top_prob']:.10f}",
            "top_prob_delta": f"{c['top_prob'] - b['top_prob']:.10f}",
            "kl_ref_to_candidate": f"{kl:.10f}",
        })

    write_csv(args.out_trainable_csv, trainable_rows)
    write_csv(args.out_bucket_csv, bucket_rows)
    write_csv(args.out_anchor_csv, anchor_rows)

    train_gap_improved = sum(int(r["gap_improved"]) for r in trainable_rows)
    train_target_prob_improved = sum(int(r["target_prob_improved"]) for r in trainable_rows)
    train_rank_regressed = sum(int(r["target_rank_regressed"]) for r in trainable_rows)
    mean_gap_delta = sum(float(r["gap_delta"]) for r in trainable_rows) / len(trainable_rows)

    evaluated_bucket = [r for r in bucket_rows if r.get("status") == "evaluated"]
    bucket_prob_regressed = sum(int(r["target_prob_regressed"]) for r in evaluated_bucket)
    bucket_rank_regressed = sum(int(r["target_rank_regressed"]) for r in evaluated_bucket)
    bucket_counts = Counter(r.get("ready_bucket", "") for r in bucket_rows)
    bucket_status_counts = Counter(r.get("status", "") for r in bucket_rows)

    anchor_top1_changed = sum(int(r["top1_changed"]) for r in anchor_rows)
    mean_anchor_kl = sum(float(r["kl_ref_to_candidate"]) for r in anchor_rows) / len(anchor_rows)
    max_anchor_kl = max(float(r["kl_ref_to_candidate"]) for r in anchor_rows)

    lines = [
        "# Teacher-divergence tiny post-training guard audit",
        "",
        "## Branch",
        "",
        "`exp/15x15-teacher-divergence-tiny-posttrain-guard-audit`",
        "",
        "## Scope",
        "",
        "- Compares `checkpoints/15x15_current_best.pt` against local tiny probe checkpoint.",
        "- Evaluates 44 trainable teacher-divergence samples.",
        "- Evaluates protected_top10 and tail_rank_gt50 ready rows from the normalized manifest.",
        "- Evaluates corpus8 anchor snapshots for policy drift.",
        "- Does not overwrite current_best.",
        "- Does not C export.",
        "- Does not run public benchmark.",
        "- Does not promote.",
        "",
        "## Inputs",
        "",
        f"- baseline checkpoint: `{args.baseline_checkpoint}`",
        f"- candidate checkpoint: `{args.candidate_checkpoint}`",
        f"- trainer-ready dataset: `{args.trainer_ready_dataset}`",
        f"- normalized manifest: `{args.manifest}`",
        f"- anchor snapshots: `{args.anchor_snapshots}`",
        "",
        "## Summary",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| trainable rows evaluated | {len(trainable_rows)} |",
        f"| trainable gap improved rows | {train_gap_improved} |",
        f"| trainable target prob improved rows | {train_target_prob_improved} |",
        f"| trainable target rank regressed rows | {train_rank_regressed} |",
        f"| trainable mean gap delta | {mean_gap_delta:.10f} |",
        f"| protected/tail rows considered | {len(bucket_rows)} |",
        f"| protected/tail rows evaluated | {len(evaluated_bucket)} |",
        f"| protected/tail target prob regressed rows | {bucket_prob_regressed} |",
        f"| protected/tail target rank regressed rows | {bucket_rank_regressed} |",
        f"| anchor rows evaluated | {len(anchor_rows)} |",
        f"| anchor top1 changed rows | {anchor_top1_changed} |",
        f"| anchor mean KL ref->candidate | {mean_anchor_kl:.10f} |",
        f"| anchor max KL ref->candidate | {max_anchor_kl:.10f} |",
        "",
        "## Protected/tail bucket counts",
        "",
        "| bucket | rows |",
        "|---|---:|",
    ]

    for key, value in bucket_counts.most_common():
        lines.append(f"| {key} | {value} |")

    lines.extend([
        "",
        "## Protected/tail evaluation status",
        "",
        "| status | rows |",
        "|---|---:|",
    ])

    for key, value in bucket_status_counts.most_common():
        lines.append(f"| {key} | {value} |")

    lines.extend([
        "",
        "## Worst trainable gap deltas",
        "",
        "| row_index | case_id | gap_before | gap_after | gap_delta | target_prob_delta | target_rank_delta |",
        "|---:|---|---:|---:|---:|---:|---:|",
    ])

    for r in sorted(trainable_rows, key=lambda x: float(x["gap_delta"]))[:10]:
        lines.append(
            f"| {r['row_index']} | {r['case_id']} | {r['gap_before']} | {r['gap_after']} | {r['gap_delta']} | {r['target_prob_delta']} | {r['target_rank_delta']} |"
        )

    lines.extend([
        "",
        "## Largest protected/tail rank regressions",
        "",
        "| manifest_id | bucket | case_id | rank_before | rank_after | rank_delta | prob_delta |",
        "|---|---|---|---:|---:|---:|---:|",
    ])

    bucket_rank_rows = [r for r in evaluated_bucket if r["target_rank_delta"] != ""]
    for r in sorted(bucket_rank_rows, key=lambda x: int(x["target_rank_delta"]), reverse=True)[:15]:
        lines.append(
            f"| {r['manifest_id']} | {r['ready_bucket']} | {r['case_id']} | {r['target_rank_before']} | {r['target_rank_after']} | {r['target_rank_delta']} | {r['target_prob_delta']} |"
        )

    lines.extend([
        "",
        "## Largest anchor KL rows",
        "",
        "| anchor_index | case_id | top1_changed | KL | baseline_top_rc | candidate_top_rc | top_prob_delta |",
        "|---:|---|---:|---:|---|---|---:|",
    ])

    for r in sorted(anchor_rows, key=lambda x: float(x["kl_ref_to_candidate"]), reverse=True)[:10]:
        lines.append(
            f"| {r['anchor_index']} | {r['case_id']} | {r['top1_changed']} | {r['kl_ref_to_candidate']} | `{r['baseline_top_rc']}` | `{r['candidate_top_rc']}` | {r['top_prob_delta']} |"
        )

    lines.extend([
        "",
        "## Outputs",
        "",
        f"- trainable guard CSV: `{args.out_trainable_csv}`",
        f"- manifest bucket guard CSV: `{args.out_bucket_csv}`",
        f"- anchor drift guard CSV: `{args.out_anchor_csv}`",
        f"- report: `{args.out_report}`",
        "",
        "## Decision",
        "",
        "This is a post-training guard audit only.",
        "",
        "No C export.",
        "",
        "No public benchmark.",
        "",
        "No promotion.",
        "",
        "Use this audit to decide whether a larger gated training run is justified.",
        "",
    ])

    args.out_report.parent.mkdir(parents=True, exist_ok=True)
    args.out_report.write_text("\n".join(lines), encoding="utf-8")

    print("device:", device)
    print("trainable_rows:", len(trainable_rows))
    print("trainable_gap_improved_rows:", train_gap_improved)
    print("trainable_target_prob_improved_rows:", train_target_prob_improved)
    print("trainable_target_rank_regressed_rows:", train_rank_regressed)
    print("trainable_mean_gap_delta:", f"{mean_gap_delta:.10f}")
    print("bucket_rows:", len(bucket_rows))
    print("bucket_evaluated_rows:", len(evaluated_bucket))
    print("bucket_prob_regressed:", bucket_prob_regressed)
    print("bucket_rank_regressed:", bucket_rank_regressed)
    print("anchor_rows:", len(anchor_rows))
    print("anchor_top1_changed:", anchor_top1_changed)
    print("anchor_mean_kl:", f"{mean_anchor_kl:.10f}")
    print("anchor_max_kl:", f"{max_anchor_kl:.10f}")
    print("out_trainable_csv:", args.out_trainable_csv)
    print("out_bucket_csv:", args.out_bucket_csv)
    print("out_anchor_csv:", args.out_anchor_csv)
    print("out_report:", args.out_report)
    print("no C export; no public benchmark; no promotion")


if __name__ == "__main__":
    main()
