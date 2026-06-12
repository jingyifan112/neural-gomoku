from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F
from torch.utils.data import DataLoader, TensorDataset

from gomoku_agent.model import PolicyValueNet


COORD_RE = re.compile(r"-?\d+")


@dataclass
class Sample:
    row_id: str
    role: str
    state: np.ndarray
    legal_mask: np.ndarray
    target_idx: int
    target_rc: tuple[int, int]
    model_idx: int | None
    model_rc: tuple[int, int] | None
    weight: float
    raw: dict[str, Any]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Candidate G conservative policy-first distillation dry run."
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        default=Path("analysis/integration_eval/candidate_g_teacher_seed_dataset.json"),
    )
    parser.add_argument(
        "--base-checkpoint",
        type=Path,
        default=Path("checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt"),
    )
    parser.add_argument(
        "--out-checkpoint",
        type=Path,
        default=Path("checkpoints/15x15_candidate_g_policy_first_dry_run.pt"),
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("analysis/integration_eval/candidate_g_policy_first_dry_run_report.md"),
    )
    parser.add_argument("--board-size", type=int, default=15)
    parser.add_argument("--channels", type=int, default=64)
    parser.add_argument("--blocks", type=int, default=4)
    parser.add_argument("--epochs", type=int, default=80)
    parser.add_argument("--batch-size", type=int, default=14)
    parser.add_argument("--lr", type=float, default=3e-5)
    parser.add_argument("--weight-decay", type=float, default=1e-4)
    parser.add_argument("--kl-anchor", type=float, default=0.25)
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument("--min-seed-improved", type=int, default=2)
    parser.add_argument("--policy-head-only", action="store_true")
    parser.add_argument("--no-save", action="store_true")
    parser.add_argument("--strict-g2-move15", action="store_true")
    parser.add_argument("--device", default="auto", choices=["auto", "cpu", "cuda"])
    return parser.parse_args()


def load_rows(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text())
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("rows", "dataset", "samples", "items"):
            if key in data and isinstance(data[key], list):
                return data[key]
    raise ValueError(f"unsupported dataset JSON shape in {path}")


def parse_coord(value: Any) -> tuple[int, int] | None:
    if value is None:
        return None
    if isinstance(value, str):
        nums = [int(x) for x in COORD_RE.findall(value)]
        if len(nums) >= 2:
            return nums[0], nums[1]
        return None
    if isinstance(value, (list, tuple)) and len(value) >= 2:
        return int(value[0]), int(value[1])
    if isinstance(value, dict):
        r = value.get("row", value.get("r", value.get("y")))
        c = value.get("col", value.get("c", value.get("x")))
        if r is not None and c is not None:
            return int(r), int(c)
    return None


def first_present(row: dict[str, Any], keys: tuple[str, ...]) -> Any:
    for key in keys:
        if key in row and row[key] is not None:
            return row[key]
    return None


def parse_side(row: dict[str, Any]) -> int:
    value = first_present(
        row,
        (
            "side",
            "side_to_move",
            "manifest_side",
            "to_move",
            "current_side",
            "current_player_side",
            "player",
            "current_player",
        ),
    )

    if isinstance(value, (int, float)):
        iv = int(value)
        if iv == 1:
            return 1
        if iv == -1:
            return -1

    if isinstance(value, str):
        s = value.strip().lower()
        if s in ("black", "b", "x", "1", "+1"):
            return 1
        if s in ("white", "w", "o", "-1"):
            return -1

    raise ValueError(
        "cannot infer side/current player "
        f"from side_to_move={row.get('side_to_move')!r} "
        f"manifest_side={row.get('manifest_side')!r} "
        f"keys={sorted(row)}"
    )


def char_to_cell(value: Any) -> int:
    if isinstance(value, (int, float)):
        iv = int(value)
        if iv == 1:
            return 1
        if iv in (-1, 2):
            return -1
        return 0

    s = str(value).strip().lower()
    if s in ("x", "b", "black", "1", "+1"):
        return 1
    if s in ("o", "w", "white", "-1", "2"):
        return -1
    return 0


def parse_board_grid(board: Any, board_size: int) -> np.ndarray:
    arr = np.zeros((board_size, board_size), dtype=np.int8)

    if isinstance(board, dict):
        if "board" in board:
            return parse_board_grid(board["board"], board_size)
        if "grid" in board:
            return parse_board_grid(board["grid"], board_size)

    if not isinstance(board, list):
        raise ValueError("board must be a list/grid or dict containing board/grid")

    if len(board) != board_size:
        raise ValueError(f"board row count {len(board)} != board_size {board_size}")

    for r, line in enumerate(board):
        if isinstance(line, str):
            tokens = line.split() if " " in line else list(line)
        else:
            tokens = list(line)
        if len(tokens) != board_size:
            raise ValueError(f"board col count at row {r}: {len(tokens)} != {board_size}")
        for c, token in enumerate(tokens):
            arr[r, c] = char_to_cell(token)
    return arr


def board_from_stones(row: dict[str, Any], board_size: int) -> np.ndarray | None:
    black = first_present(row, ("black_stones", "black", "black_moves"))
    white = first_present(row, ("white_stones", "white", "white_moves"))
    if black is None and white is None:
        return None

    board = np.zeros((board_size, board_size), dtype=np.int8)
    for coord in black or []:
        rc = parse_coord(coord)
        if rc is not None:
            board[rc] = 1
    for coord in white or []:
        rc = parse_coord(coord)
        if rc is not None:
            board[rc] = -1
    return board


def board_from_moves(row: dict[str, Any], board_size: int) -> np.ndarray | None:
    moves = first_present(row, ("moves", "move_history", "replay_moves", "history"))
    if not moves:
        return None

    board = np.zeros((board_size, board_size), dtype=np.int8)
    for i, move in enumerate(moves):
        rc = parse_coord(move)
        if rc is None:
            continue
        board[rc] = 1 if i % 2 == 0 else -1
    return board


def direct_state_from_row(row: dict[str, Any], board_size: int) -> np.ndarray | None:
    for key in (
        "state",
        "input",
        "input_state",
        "planes",
        "features",
        "tensor",
        "model_input",
        "encoded_state",
    ):
        if key not in row:
            continue
        value = row[key]
        if isinstance(value, dict):
            continue
        arr = np.asarray(value, dtype=np.float32)
        if arr.shape == (3, board_size, board_size):
            return arr
        if arr.shape == (board_size, board_size, 3):
            return np.transpose(arr, (2, 0, 1)).astype(np.float32)
    return None


def encoded_state_from_board(row: dict[str, Any], board_size: int) -> np.ndarray:
    board_value = first_present(row, ("board", "grid", "position", "board_grid"))
    if board_value is not None:
        board = parse_board_grid(board_value, board_size)
    else:
        board = board_from_stones(row, board_size)
        if board is None:
            board = board_from_moves(row, board_size)
    if board is None:
        raise ValueError(f"cannot reconstruct board for row {row.get('id', row.get('row_id'))}")

    side = parse_side(row)
    current = (board == side).astype(np.float32)
    opponent = (board == -side).astype(np.float32)

    last = np.zeros((board_size, board_size), dtype=np.float32)
    last_move = first_present(row, ("last_move", "previous_move", "prev_move"))
    rc = parse_coord(last_move)
    if rc is not None:
        last[rc] = 1.0

    return np.stack([current, opponent, last]).astype(np.float32)


def state_from_row(row: dict[str, Any], board_size: int) -> np.ndarray:
    state = direct_state_from_row(row, board_size)
    if state is not None:
        return state

    board_state = first_present(row, ("board_state", "position_state", "state_dict"))
    if isinstance(board_state, dict):
        merged = {**board_state, **row}
        state = direct_state_from_row(merged, board_size)
        if state is not None:
            return state
        return encoded_state_from_board(merged, board_size)

    return encoded_state_from_board(row, board_size)


def legal_mask_from_state(state: np.ndarray) -> np.ndarray:
    occupied = (state[0] > 0.5) | (state[1] > 0.5)
    return (~occupied).reshape(-1).astype(np.float32)


def coord_to_idx(rc: tuple[int, int], board_size: int) -> int:
    return rc[0] * board_size + rc[1]


def idx_to_coord(idx: int, board_size: int) -> str:
    return f"{idx // board_size},{idx % board_size}"


def sample_from_row(row: dict[str, Any], board_size: int, i: int) -> Sample:
    row_id = str(first_present(row, ("id", "row_id", "name", "case_id")) or f"row_{i}")
    role = str(first_present(row, ("role", "anchor_role", "candidate_role", "kind")) or "")

    target_value = first_present(
        row,
        (
            "policy_target_move",
            "policy_target",
            "target",
            "target_move",
            "move_target",
            "expected",
            "expected_move",
            "teacher_move",
            "teacher",
            "teacher_coord",
        ),
    )
    target_rc = parse_coord(target_value)
    if target_rc is None:
        raise ValueError(f"{row_id}: cannot parse teacher/target move from {target_value!r}")

    model_value = first_present(
        row,
        (
            "model",
            "model_move",
            "baseline_move",
            "before_move",
            "old_final",
            "candidate_move",
        ),
    )
    model_rc = parse_coord(model_value)

    state = state_from_row(row, board_size)
    legal_mask = legal_mask_from_state(state)
    target_idx = coord_to_idx(target_rc, board_size)

    if target_idx < 0 or target_idx >= board_size * board_size:
        raise ValueError(f"{row_id}: target out of range: {target_rc}")

    if legal_mask[target_idx] <= 0:
        swapped_rc = (target_rc[1], target_rc[0])
        swapped_idx = coord_to_idx(swapped_rc, board_size)
        if (
            0 <= swapped_rc[0] < board_size
            and 0 <= swapped_rc[1] < board_size
            and legal_mask[swapped_idx] > 0
        ):
            print(
                f"warning: {row_id}: target {target_rc} occupied; "
                f"using swapped coordinate {swapped_rc}",
                flush=True,
            )
            target_rc = swapped_rc
            target_idx = swapped_idx
        else:
            occ_current = float(state[0, target_rc[0], target_rc[1]])
            occ_opponent = float(state[1, target_rc[0], target_rc[1]])
            raise ValueError(
                f"{row_id}: target {target_rc} is not legal in encoded state "
                f"(occupied current={occ_current}, opponent={occ_opponent}); "
                f"swapped {swapped_rc} legal={legal_mask[swapped_idx] > 0}"
            )

    model_idx = None
    if model_rc is not None:
        model_idx = coord_to_idx(model_rc, board_size)

    weight = float(row.get("weight", 1.0))

    return Sample(
        row_id=row_id,
        role=role,
        state=state,
        legal_mask=legal_mask,
        target_idx=target_idx,
        target_rc=target_rc,
        model_idx=model_idx,
        model_rc=model_rc,
        weight=weight,
        raw=row,
    )


def load_checkpoint_model(
    checkpoint: Path,
    device: torch.device,
    fallback_board_size: int,
    fallback_channels: int,
    fallback_blocks: int,
) -> tuple[PolicyValueNet, dict[str, Any]]:
    if not checkpoint.exists():
        raise FileNotFoundError(
            f"base checkpoint not found: {checkpoint}. "
            "Pass --base-checkpoint to the intended 15x15 checkpoint."
        )

    payload = torch.load(checkpoint, map_location=device)
    if not isinstance(payload, dict):
        raise ValueError(f"unsupported checkpoint payload type: {type(payload)}")

    board_size = int(payload.get("board_size", fallback_board_size))
    channels = int(payload.get("channels", fallback_channels))
    blocks = int(payload.get("blocks", fallback_blocks))

    model = PolicyValueNet(board_size=board_size, channels=channels, blocks=blocks).to(device)

    state_dict = payload.get("model", payload.get("state_dict", payload))
    model.load_state_dict(state_dict)
    return model, {
        "board_size": board_size,
        "channels": channels,
        "blocks": blocks,
        "win_length": int(payload.get("win_length", 5)),
    }


def freeze_batchnorm(model: nn.Module) -> None:
    for module in model.modules():
        if isinstance(module, nn.modules.batchnorm._BatchNorm):
            module.eval()
            for param in module.parameters(recurse=False):
                param.requires_grad_(False)


def configure_trainable_params(model: PolicyValueNet, policy_head_only: bool) -> None:
    for name, param in model.named_parameters():
        if name.startswith("value_conv.") or name.startswith("value_fc."):
            param.requires_grad_(False)
        elif policy_head_only:
            param.requires_grad_(name.startswith("policy."))
        else:
            param.requires_grad_(True)
    freeze_batchnorm(model)


def masked_logits(logits: torch.Tensor, legal_mask: torch.Tensor) -> torch.Tensor:
    return logits.masked_fill(legal_mask <= 0, -1e9)


def evaluate(
    model: PolicyValueNet,
    samples: list[Sample],
    device: torch.device,
    board_size: int,
) -> list[dict[str, Any]]:
    model.eval()
    states = torch.tensor(np.stack([s.state for s in samples]), dtype=torch.float32, device=device)
    masks = torch.tensor(np.stack([s.legal_mask for s in samples]), dtype=torch.float32, device=device)

    with torch.no_grad():
        logits, values = model(states)
        mlogits = masked_logits(logits, masks)
        probs = torch.softmax(mlogits, dim=-1)
        order = torch.argsort(mlogits, dim=-1, descending=True)

    rows: list[dict[str, Any]] = []
    for i, sample in enumerate(samples):
        target_idx = sample.target_idx
        rank_positions = (order[i] == target_idx).nonzero(as_tuple=False)
        rank = int(rank_positions[0].item()) + 1 if len(rank_positions) else 9999
        top_idx = int(order[i, 0].item())

        target_logit = float(logits[i, target_idx].item())
        model_gap = None
        if sample.model_idx is not None:
            model_gap = target_logit - float(logits[i, sample.model_idx].item())

        rows.append(
            {
                "row_id": sample.row_id,
                "role": sample.role,
                "target": f"{sample.target_rc[0]},{sample.target_rc[1]}",
                "model_move": (
                    None if sample.model_rc is None else f"{sample.model_rc[0]},{sample.model_rc[1]}"
                ),
                "top": idx_to_coord(top_idx, board_size),
                "top_idx": top_idx,
                "target_rank": rank,
                "target_prob": float(probs[i, target_idx].item()),
                "target_logit": target_logit,
                "target_model_logit_gap": model_gap,
                "value": float(values[i].item()),
            }
        )
    return rows


def row_improved(before: dict[str, Any], after: dict[str, Any]) -> bool:
    if after["target_rank"] < before["target_rank"]:
        return True
    if after["target_prob"] > before["target_prob"] + 1e-8:
        return True
    if after["target_logit"] > before["target_logit"] + 1e-8:
        return True
    bgap = before.get("target_model_logit_gap")
    agap = after.get("target_model_logit_gap")
    if bgap is not None and agap is not None and agap > bgap + 1e-8:
        return True
    return False


def is_seed_row(sample: Sample) -> bool:
    text = f"{sample.row_id} {sample.role}".lower()
    return "seed_teacher_divergence" in text or ("seed" in text and "diverg" in text)


def is_g2_move15_row(sample: Sample) -> bool:
    text = f"{sample.row_id} {sample.role}".lower()
    if sample.role == "retention_anchor":
        return True
    return bool(re.search(r"g2.*(?:p|m)15|(?:p|m)15.*g2", text))


def train(
    model: PolicyValueNet,
    base_model: PolicyValueNet,
    samples: list[Sample],
    args: argparse.Namespace,
    device: torch.device,
) -> None:
    states = torch.tensor(np.stack([s.state for s in samples]), dtype=torch.float32)
    targets = torch.tensor([s.target_idx for s in samples], dtype=torch.long)
    weights = torch.tensor([s.weight for s in samples], dtype=torch.float32)
    masks = torch.tensor(np.stack([s.legal_mask for s in samples]), dtype=torch.float32)

    base_model.eval()
    with torch.no_grad():
        base_logits, _ = base_model(states.to(device))
        base_log_probs = F.log_softmax(masked_logits(base_logits, masks.to(device)), dim=-1).cpu()
        base_probs = base_log_probs.exp()

    loader = DataLoader(
        TensorDataset(states, targets, weights, masks, base_log_probs, base_probs),
        batch_size=args.batch_size,
        shuffle=True,
    )

    optimizer = torch.optim.AdamW(
        [p for p in model.parameters() if p.requires_grad],
        lr=args.lr,
        weight_decay=args.weight_decay,
    )

    for epoch in range(args.epochs):
        model.train()
        freeze_batchnorm(model)

        total_loss = 0.0
        total_ce = 0.0
        total_kl = 0.0
        total_weight = 0.0

        for batch_states, batch_targets, batch_weights, batch_masks, batch_base_logp, batch_base_p in loader:
            batch_states = batch_states.to(device)
            batch_targets = batch_targets.to(device)
            batch_weights = batch_weights.to(device)
            batch_masks = batch_masks.to(device)
            batch_base_logp = batch_base_logp.to(device)
            batch_base_p = batch_base_p.to(device)

            logits, _ = model(batch_states)
            log_probs = F.log_softmax(masked_logits(logits, batch_masks), dim=-1)

            ce = F.nll_loss(log_probs, batch_targets, reduction="none")
            kl = (batch_base_p * (batch_base_logp - log_probs)).sum(dim=-1)

            denom = batch_weights.sum().clamp_min(1e-8)
            ce_loss = (batch_weights * ce).sum() / denom
            kl_loss = (batch_weights * kl).sum() / denom
            loss = ce_loss + args.kl_anchor * kl_loss

            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()

            total_loss += float(loss.item()) * float(denom.item())
            total_ce += float(ce_loss.item()) * float(denom.item())
            total_kl += float(kl_loss.item()) * float(denom.item())
            total_weight += float(denom.item())

        if epoch == 0 or (epoch + 1) % 10 == 0 or epoch + 1 == args.epochs:
            print(
                f"epoch {epoch + 1}/{args.epochs}: "
                f"loss={total_loss / total_weight:.6f} "
                f"ce={total_ce / total_weight:.6f} "
                f"kl={total_kl / total_weight:.6f}",
                flush=True,
            )


def write_report(
    path: Path,
    args: argparse.Namespace,
    meta: dict[str, Any],
    samples: list[Sample],
    before: list[dict[str, Any]],
    after: list[dict[str, Any]],
    summary: dict[str, Any],
) -> None:
    before_by_id = {r["row_id"]: r for r in before}
    after_by_id = {r["row_id"]: r for r in after}

    lines: list[str] = []
    lines.append("# Candidate G policy-first distillation dry run")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append("- Conservative dry run only.")
    lines.append("- Trains policy target behavior on the Candidate G board-state dataset.")
    lines.append("- Freezes BatchNorm and value head.")
    lines.append("- Does not export C weights.")
    lines.append("- Does not run formal Rapfi smoke.")
    lines.append("- Does not mark any checkpoint as promoted/current-best.")
    lines.append("")
    lines.append("## Inputs")
    lines.append("")
    lines.append(f"- dataset: `{args.dataset}`")
    lines.append(f"- base_checkpoint: `{args.base_checkpoint}`")
    lines.append(f"- out_checkpoint: `{args.out_checkpoint if not args.no_save else 'not saved (--no-save)'}`")
    lines.append(f"- rows: {len(samples)}")
    lines.append(f"- model_meta: `{json.dumps(meta, sort_keys=True)}`")
    lines.append(f"- epochs: {args.epochs}")
    lines.append(f"- lr: {args.lr}")
    lines.append(f"- kl_anchor: {args.kl_anchor}")
    lines.append(f"- policy_head_only: {args.policy_head_only}")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    for key, value in summary.items():
        lines.append(f"- {key}: {value}")
    lines.append("")
    lines.append("## Row metrics")
    lines.append("")
    lines.append(
        "| row_id | role | target | before_top | before_rank | before_prob | before_gap | "
        "after_top | after_rank | after_prob | after_gap | improved |"
    )
    lines.append(
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"
    )

    for sample in samples:
        b = before_by_id[sample.row_id]
        a = after_by_id[sample.row_id]
        improved = row_improved(b, a)
        bgap = b["target_model_logit_gap"]
        agap = a["target_model_logit_gap"]
        lines.append(
            f"| {sample.row_id} | {sample.role} | {a['target']} | "
            f"{b['top']} | {b['target_rank']} | {b['target_prob']:.6f} | "
            f"{'NA' if bgap is None else f'{bgap:.6f}'} | "
            f"{a['top']} | {a['target_rank']} | {a['target_prob']:.6f} | "
            f"{'NA' if agap is None else f'{agap:.6f}'} | {improved} |"
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def main() -> None:
    args = parse_args()
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)

    if args.device == "auto":
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    else:
        device = torch.device(args.device)

    model, meta = load_checkpoint_model(
        args.base_checkpoint,
        device,
        args.board_size,
        args.channels,
        args.blocks,
    )
    board_size = int(meta["board_size"])

    rows = load_rows(args.dataset)
    samples = [sample_from_row(row, board_size, i) for i, row in enumerate(rows)]

    role_counts: dict[str, int] = {}
    for sample in samples:
        role_counts[sample.role] = role_counts.get(sample.role, 0) + 1

    seed_rows = [s for s in samples if is_seed_row(s)]
    g2_rows = [s for s in samples if is_g2_move15_row(s)]

    print(f"loaded rows={len(samples)} role_counts={json.dumps(role_counts, sort_keys=True)}")
    print(f"seed_rows={len(seed_rows)} g2_move15_or_retention_rows={len(g2_rows)}")
    print("dry-run boundary: no C export, no formal smoke, no promotion")

    configure_trainable_params(model, policy_head_only=args.policy_head_only)
    base_model = copy.deepcopy(model).to(device)
    base_model.eval()

    before = evaluate(model, samples, device, board_size)
    train(model, base_model, samples, args, device)
    after = evaluate(model, samples, device, board_size)

    before_by_id = {r["row_id"]: r for r in before}
    after_by_id = {r["row_id"]: r for r in after}

    improved_ids = [
        s.row_id
        for s in samples
        if row_improved(before_by_id[s.row_id], after_by_id[s.row_id])
    ]
    seed_improved_ids = [
        s.row_id
        for s in seed_rows
        if row_improved(before_by_id[s.row_id], after_by_id[s.row_id])
    ]

    g2_no_regression = None
    g2_details = []
    if g2_rows:
        g2_no_regression = True
        for sample in g2_rows:
            b = before_by_id[sample.row_id]
            a = after_by_id[sample.row_id]

            before_gap = b.get("target_model_logit_gap")
            after_gap = a.get("target_model_logit_gap")

            rank_ok = a["target_rank"] <= b["target_rank"]
            prob_ok = a["target_prob"] + 1e-12 >= b["target_prob"]
            logit_ok = a["target_logit"] + 1e-12 >= b["target_logit"]
            gap_ok = (
                True
                if before_gap is None or after_gap is None
                else after_gap + 1e-12 >= before_gap
            )

            ok = rank_ok and prob_ok and logit_ok and gap_ok
            g2_no_regression = g2_no_regression and ok
            g2_details.append(
                {
                    "row_id": sample.row_id,
                    "target": a["target"],
                    "before_top": b["top"],
                    "after_top": a["top"],
                    "before_rank": b["target_rank"],
                    "after_rank": a["target_rank"],
                    "before_prob": b["target_prob"],
                    "after_prob": a["target_prob"],
                    "before_gap": before_gap,
                    "after_gap": after_gap,
                    "rank_ok": rank_ok,
                    "prob_ok": prob_ok,
                    "logit_ok": logit_ok,
                    "gap_ok": gap_ok,
                    "ok": ok,
                }
            )

    summary = {
        "rows": len(samples),
        "role_counts": role_counts,
        "seed_rows": len(seed_rows),
        "seed_improved": len(seed_improved_ids),
        "seed_improved_ids": seed_improved_ids,
        "all_improved": len(improved_ids),
        "g2_move15_no_regression": g2_no_regression,
        "g2_move15_details": g2_details,
        "saved_checkpoint": False,
    }

    if not args.no_save:
        args.out_checkpoint.parent.mkdir(parents=True, exist_ok=True)
        torch.save(
            {
                "model": model.state_dict(),
                "board_size": board_size,
                "win_length": meta.get("win_length", 5),
                "channels": meta["channels"],
                "blocks": meta["blocks"],
                "candidate": "G",
                "dry_run": True,
                "source_checkpoint": str(args.base_checkpoint),
                "dataset": str(args.dataset),
                "summary": summary,
            },
            args.out_checkpoint,
        )
        summary["saved_checkpoint"] = True

    write_report(args.report, args, meta, samples, before, after, summary)

    print("SUMMARY_JSON", json.dumps(summary, sort_keys=True))
    print(f"wrote report: {args.report}")
    if not args.no_save:
        print(f"wrote dry-run checkpoint: {args.out_checkpoint}")

    failures = []
    if len(seed_improved_ids) < args.min_seed_improved:
        failures.append(
            f"seed improvement check failed: {len(seed_improved_ids)} < {args.min_seed_improved}"
        )
    if args.strict_g2_move15:
        if g2_no_regression is None:
            failures.append("strict g2 move15 check failed: no g2/retention row found")
        elif not g2_no_regression:
            failures.append(f"strict g2 move15 check failed: {g2_details}")

    if failures:
        for failure in failures:
            print("FAIL:", failure, file=sys.stderr)
        sys.exit(1)

    print("PASS: Candidate G policy-first dry-run checks passed")


if __name__ == "__main__":
    main()
