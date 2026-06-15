from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import torch
from torch.nn import functional as F

from gomoku_agent.checkpoint import load_compatible_checkpoint
from gomoku_agent.model import PolicyValueNet


COORD_RE = re.compile(r"-?\d+")


@dataclass
class PreparedRow:
    raw: dict[str, Any]
    row_id: str
    split: str
    role: str
    label_type: str
    source_id: str
    side_to_move: str
    state: np.ndarray
    legal_mask: np.ndarray
    target_action: int
    target_xy: tuple[int, int]
    weight: float


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Anchored policy-focused teacher-divergence probe. "
            "This trains only train_candidate rows and writes Python-only probe artifacts."
        )
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_retention_safety_v3_dataset.json"),
    )
    parser.add_argument(
        "--base-checkpoint",
        type=Path,
        default=Path("checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt"),
    )
    parser.add_argument(
        "--out-checkpoint",
        type=Path,
        default=Path("checkpoints/15x15_teacher_divergence_policy_anchor_probe.pt"),
    )
    parser.add_argument(
        "--eval-csv",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_policy_anchor_probe_eval.csv"),
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("analysis/integration_eval/teacher_divergence_policy_anchor_probe_report.md"),
    )
    parser.add_argument("--board-size", type=int, default=15)
    parser.add_argument("--win-length", type=int, default=5)
    parser.add_argument("--channels", type=int, default=64)
    parser.add_argument("--blocks", type=int, default=4)
    parser.add_argument("--epochs", type=int, default=80)
    parser.add_argument("--lr", type=float, default=3e-5)
    parser.add_argument("--kl-weight", type=float, default=0.35)
    parser.add_argument(
        "--anchor-kl-splits",
        default="train_candidate,train_teacher_divergence",
        help=(
            "Comma-separated splits used for KL anchoring against the base model. "
            "heldout_retention should normally stay evaluation-only."
        ),
    )
    parser.add_argument("--weight-decay", type=float, default=1e-4)
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument("--print-every", type=int, default=10)
    parser.add_argument(
        "--train-scope",
        choices=("policy_head", "policy_and_tower", "all"),
        default="policy_head",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-save", action="store_true")
    parser.add_argument("--no-strict-splits", action="store_true")
    parser.add_argument("--device", choices=("auto", "cpu", "cuda"), default="auto")
    return parser.parse_args()


def parse_coord_xy(value: Any) -> tuple[int, int] | None:
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
        if "x" in value and "y" in value:
            return int(value["x"]), int(value["y"])
        if "col" in value and "row" in value:
            return int(value["col"]), int(value["row"])
        if "c" in value and "r" in value:
            return int(value["c"]), int(value["r"])
    return None


def xy_to_action(xy: tuple[int, int], board_size: int) -> int:
    x, y = xy
    if not (0 <= x < board_size and 0 <= y < board_size):
        raise ValueError(f"xy out of bounds: {xy} for board_size={board_size}")
    return y * board_size + x


def action_to_xy(action: int, board_size: int) -> tuple[int, int]:
    return action % board_size, action // board_size


def xy_to_str(xy: tuple[int, int]) -> str:
    return f"{xy[0]},{xy[1]}"


def side_to_player(side: str) -> int:
    s = str(side).strip().lower()
    if s in ("black", "b", "x", "1", "+1"):
        return 1
    if s in ("white", "w", "o", "-1", "2"):
        return -1
    raise ValueError(f"unsupported side_to_move: {side!r}")


def cell_to_int(value: Any) -> int:
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


def parse_board(board_value: Any, board_size: int) -> np.ndarray:
    if isinstance(board_value, dict):
        if "board" in board_value:
            return parse_board(board_value["board"], board_size)
        if "grid" in board_value:
            return parse_board(board_value["grid"], board_size)

    if isinstance(board_value, str):
        text_value = board_value.strip()

        # Accepted safety_v3 stores board as a stringified list-of-lists.
        # Example: "[[0, 0, ...], [0, 0, ...], ...]"
        if text_value.startswith("["):
            import ast

            try:
                parsed = ast.literal_eval(text_value)
            except (SyntaxError, ValueError) as exc:
                raise ValueError(
                    f"could not parse stringified board list: {text_value[:240]!r}"
                ) from exc
            return parse_board(parsed, board_size)

        # Some JSON rows may store literal backslash-n instead of real newlines.
        if "\\n" in text_value and "\n" not in text_value:
            text_value = text_value.replace("\\n", "\n")

        if "/" in text_value and "\n" not in text_value:
            raw_lines = text_value.split("/")
        elif (
            len([ch for ch in text_value if ch in ".XOxo012+-"])
            == board_size * board_size
            and "\n" not in text_value
        ):
            compact = [ch for ch in text_value if ch in ".XOxo012+-"]
            raw_lines = [
                "".join(compact[i : i + board_size])
                for i in range(0, len(compact), board_size)
            ]
        else:
            raw_lines = text_value.splitlines()

        parsed_lines: list[list[str]] = []
        for raw in raw_lines:
            line = raw.strip()
            if not line:
                continue
            if set(line) <= {"-"}:
                continue

            tokens = line.split()
            if len(tokens) == board_size:
                parsed_lines.append(tokens)
                continue

            compact = [ch for ch in line if ch in ".XOxo"]
            if len(compact) == board_size:
                parsed_lines.append(compact)
                continue

            compact_numeric = []
            for ch in line:
                if ch == ".":
                    compact_numeric.append(".")
                elif ch in "Xx1+":
                    compact_numeric.append("X")
                elif ch in "Oo2-":
                    compact_numeric.append("O")
            if len(compact_numeric) == board_size:
                parsed_lines.append(compact_numeric)

        if len(parsed_lines) != board_size:
            raise ValueError(
                f"text-grid board row count {len(parsed_lines)} != board_size {board_size}; "
                f"raw_lines={len(raw_lines)} repr={board_value[:240]!r}"
            )

        board = np.zeros((board_size, board_size), dtype=np.int8)
        for r, tokens in enumerate(parsed_lines):
            for c, token in enumerate(tokens):
                board[r, c] = cell_to_int(token)
        return board

    if not isinstance(board_value, list):
        raise ValueError(f"board must be list/grid/text-grid, got {type(board_value).__name__}")

    if len(board_value) != board_size:
        raise ValueError(f"board row count {len(board_value)} != board_size {board_size}")

    board = np.zeros((board_size, board_size), dtype=np.int8)
    for r, line in enumerate(board_value):
        if isinstance(line, str):
            tokens = line.split() if " " in line else list(line)
        else:
            tokens = list(line)
        if len(tokens) != board_size:
            raise ValueError(f"board col count at row {r}: {len(tokens)} != {board_size}")
        for c, token in enumerate(tokens):
            board[r, c] = cell_to_int(token)
    return board

def find_last_move_rc(row: dict[str, Any], board_size: int) -> tuple[int, int] | None:
    candidates: list[Any] = [
        row.get("last_move_rc"),
        row.get("last_move_xy"),
    ]

    metadata = row.get("metadata")
    if isinstance(metadata, dict):
        candidates.extend(
            [
                metadata.get("last_move_rc"),
                metadata.get("last_move_xy"),
                metadata.get("last_move"),
            ]
        )

    for value in candidates:
        xy = parse_coord_xy(value)
        if xy is None:
            continue

        # If key was explicitly rc, parse_coord_xy returns the two numbers;
        # old datasets mostly use xy strings, but rc lists also appear.
        if value is row.get("last_move_rc") or (
            isinstance(metadata, dict) and value is metadata.get("last_move_rc")
        ):
            r, c = xy
            if 0 <= r < board_size and 0 <= c < board_size:
                return r, c
        else:
            x, y = xy
            if 0 <= x < board_size and 0 <= y < board_size:
                return y, x

    return None


def encode_state(row: dict[str, Any], board_size: int) -> tuple[np.ndarray, np.ndarray]:
    board = parse_board(row["board"], board_size)
    current_player = side_to_player(row["side_to_move"])

    current = (board == current_player).astype(np.float32)
    opponent = (board == -current_player).astype(np.float32)
    last = np.zeros((board_size, board_size), dtype=np.float32)

    last_rc = find_last_move_rc(row, board_size)
    if last_rc is not None:
        last[last_rc] = 1.0

    state = np.stack([current, opponent, last], axis=0).astype(np.float32)
    legal = (board.reshape(-1) == 0).astype(np.float32)
    return state, legal


def choose_policy_target(row: dict[str, Any]) -> str:
    for key in ("policy_target", "teacher_move", "target_move"):
        value = row.get(key)
        if value is not None and str(value).strip():
            return str(value)
    raise ValueError(f"{row.get('id')}: no policy target")


def prepare_rows(dataset_path: Path, board_size: int, strict_splits: bool) -> tuple[dict[str, Any], list[PreparedRow]]:
    data = json.loads(dataset_path.read_text(encoding="utf-8"))
    rows = data["rows"]

    split_counts = Counter(str(r.get("split")) for r in rows)
    role_counts = Counter(str(r.get("role")) for r in rows)
    label_counts = Counter(str(r.get("label_type")) for r in rows)

    print(f"dataset={dataset_path}")
    print(f"rows={len(rows)}")
    print(f"split_counts={dict(split_counts)}")
    print(f"role_counts={dict(role_counts)}")
    print(f"label_type_counts={dict(label_counts)}")

    if strict_splits:
        expected = {
            "train_teacher_divergence": 25,
            "train_candidate": 8,
            "heldout_retention": 11,
        }
        if len(rows) != 44 or dict(split_counts) != expected:
            raise ValueError(f"strict split check failed: rows={len(rows)} split_counts={dict(split_counts)}")

    prepared: list[PreparedRow] = []
    for row in rows:
        row_id = str(row.get("id", ""))
        state, legal = encode_state(row, board_size)
        target_xy = parse_coord_xy(choose_policy_target(row))
        if target_xy is None:
            raise ValueError(f"{row_id}: could not parse policy target {row.get('policy_target')!r}")
        target_action = xy_to_action(target_xy, board_size)
        if legal[target_action] <= 0:
            raise ValueError(f"{row_id}: target {xy_to_str(target_xy)} is not legal/empty")

        prepared.append(
            PreparedRow(
                raw=row,
                row_id=row_id,
                split=str(row.get("split", "")),
                role=str(row.get("role", "")),
                label_type=str(row.get("label_type", "")),
                source_id=str(row.get("source_id", "")),
                side_to_move=str(row.get("side_to_move", "")),
                state=state,
                legal_mask=legal,
                target_action=target_action,
                target_xy=target_xy,
                weight=float(row.get("suggested_weight", 1.0)),
            )
        )

    return data, prepared


def masked_log_softmax(logits: torch.Tensor, masks: torch.Tensor) -> torch.Tensor:
    return F.log_softmax(logits.masked_fill(masks <= 0, -1e9), dim=-1)


def load_model(args: argparse.Namespace, checkpoint: Path, device: torch.device) -> PolicyValueNet:
    model = PolicyValueNet(args.board_size, channels=args.channels, blocks=args.blocks).to(device)
    loaded = load_compatible_checkpoint(
        model,
        checkpoint,
        device,
        board_size=args.board_size,
        channels=args.channels,
        blocks=args.blocks,
    )
    if not loaded:
        raise RuntimeError(f"could not load compatible checkpoint: {checkpoint}")
    return model


def configure_trainable(model: PolicyValueNet, train_scope: str) -> list[torch.nn.Parameter]:
    for name, parameter in model.named_parameters():
        if train_scope == "all":
            parameter.requires_grad = True
        elif train_scope == "policy_head":
            parameter.requires_grad = name.startswith("policy")
        elif train_scope == "policy_and_tower":
            parameter.requires_grad = name.startswith(("stem", "tower", "policy"))
        else:
            raise ValueError(train_scope)

    trainable = [(name, parameter) for name, parameter in model.named_parameters() if parameter.requires_grad]
    if not trainable:
        raise ValueError("no trainable parameters selected")

    print(f"train_scope={train_scope}")
    print(f"trainable_parameters={sum(p.numel() for _, p in trainable)}")
    for name, _ in trainable:
        print(f"  trainable: {name}")
    return [p for _, p in trainable]


def set_training_mode(model: PolicyValueNet, train_scope: str) -> None:
    model.eval()
    if train_scope == "all":
        model.train()
    elif train_scope == "policy_head":
        model.policy.train()
    elif train_scope == "policy_and_tower":
        model.stem.train()
        model.tower.train()
        model.policy.train()
    else:
        raise ValueError(train_scope)


@torch.no_grad()
def evaluate_model(
    phase: str,
    model: PolicyValueNet,
    rows: list[PreparedRow],
    states: torch.Tensor,
    masks: torch.Tensor,
    device: torch.device,
) -> list[dict[str, Any]]:
    model.eval()
    logits, values = model(states.to(device))
    log_probs = masked_log_softmax(logits, masks.to(device))
    probs = torch.exp(log_probs).cpu()
    values_cpu = values.detach().cpu().reshape(-1)

    out: list[dict[str, Any]] = []
    for i, row in enumerate(rows):
        legal_actions = torch.nonzero(masks[i].cpu() > 0, as_tuple=False).flatten()
        legal_probs = probs[i, legal_actions]
        order = torch.argsort(legal_probs, descending=True)
        ranked = [int(legal_actions[j].item()) for j in order]
        top_action = ranked[0]
        board_size = int(math.sqrt(int(masks.shape[-1])))
        top_xy = action_to_xy(top_action, board_size)

        target_rank = ranked.index(row.target_action) + 1
        target_prob = float(probs[i, row.target_action].item())
        top_prob = float(probs[i, top_action].item())
        ce = -math.log(max(target_prob, 1e-12))

        out.append(
            {
                "phase": phase,
                "id": row.row_id,
                "split": row.split,
                "role": row.role,
                "label_type": row.label_type,
                "source_id": row.source_id,
                "side_to_move": row.side_to_move,
                "policy_target": xy_to_str(row.target_xy),
                "target_rank": target_rank,
                "target_prob": f"{target_prob:.8f}",
                "target_ce": f"{ce:.8f}",
                "top_move": xy_to_str(top_xy),
                "top_prob": f"{top_prob:.8f}",
                "top_matches_target": str(top_action == row.target_action),
                "value": f"{float(values_cpu[i].item()):.8f}",
                "used_for_training": str(row.split == "train_candidate"),
                "suggested_weight": f"{row.weight:.4f}",
            }
        )

    return out


def summarize_eval(records: list[dict[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for r in records:
        groups[(r["phase"], r["split"])].append(r)
        groups[(r["phase"], "ALL")].append(r)

    summary: dict[tuple[str, str], dict[str, Any]] = {}
    for key, items in groups.items():
        ranks = [int(x["target_rank"]) for x in items]
        probs = [float(x["target_prob"]) for x in items]
        ces = [float(x["target_ce"]) for x in items]
        top1 = sum(x["top_matches_target"] == "True" for x in items)
        summary[key] = {
            "rows": len(items),
            "top1": top1,
            "top1_rate": top1 / len(items) if items else 0.0,
            "mean_rank": sum(ranks) / len(ranks) if ranks else float("nan"),
            "mean_target_prob": sum(probs) / len(probs) if probs else float("nan"),
            "mean_target_ce": sum(ces) / len(ces) if ces else float("nan"),
        }
    return summary


def compare_before_after(before: list[dict[str, Any]], after: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    before_by_id = {r["id"]: r for r in before}
    after_by_id = {r["id"]: r for r in after}
    result: dict[str, Counter[str]] = defaultdict(Counter)

    for row_id, b in before_by_id.items():
        a = after_by_id[row_id]
        split = b["split"]
        b_rank = int(b["target_rank"])
        a_rank = int(a["target_rank"])
        b_prob = float(b["target_prob"])
        a_prob = float(a["target_prob"])

        if a_rank < b_rank:
            result[split]["rank_improved"] += 1
        elif a_rank > b_rank:
            result[split]["rank_regressed"] += 1
        else:
            result[split]["rank_same"] += 1

        if a_prob > b_prob:
            result[split]["prob_improved"] += 1
        elif a_prob < b_prob:
            result[split]["prob_regressed"] += 1
        else:
            result[split]["prob_same"] += 1

    return {k: dict(v) for k, v in result.items()}


def write_eval_csv(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "phase",
        "id",
        "split",
        "role",
        "label_type",
        "source_id",
        "side_to_move",
        "policy_target",
        "target_rank",
        "target_prob",
        "target_ce",
        "top_move",
        "top_prob",
        "top_matches_target",
        "value",
        "used_for_training",
        "suggested_weight",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for r in records:
            writer.writerow(r)


def write_report(
    path: Path,
    args: argparse.Namespace,
    dataset_meta: dict[str, Any],
    rows: list[PreparedRow],
    before: list[dict[str, Any]],
    after: list[dict[str, Any]],
    saved_checkpoint: bool,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    all_records = before + after
    summary = summarize_eval(all_records)
    comparison = compare_before_after(before, after)

    split_counts = Counter(r.split for r in rows)
    label_counts = Counter(r.label_type for r in rows)
    role_counts = Counter(r.role for r in rows)

    lines: list[str] = []
    lines.append("# Teacher-divergence anchored policy probe report")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append("- Anchored policy-focused signal probe only.")
    lines.append("- Cross-entropy trains only `split == train_candidate` rows.")
    lines.append("- KL anchors `train_candidate` and `train_teacher_divergence` to the base policy distribution.")
    lines.append("- `heldout_retention` is evaluation-only and is not used in the loss.")
    lines.append("- Value head has no explicit loss in this probe.")
    lines.append("- No C export.")
    lines.append("- No benchmark.")
    lines.append("- No promotion or current-best overwrite.")
    lines.append("- No model-capacity conclusion.")
    lines.append("")
    lines.append("## Inputs")
    lines.append("")
    lines.append(f"- dataset: `{args.dataset}`")
    lines.append(f"- base_checkpoint: `{args.base_checkpoint}`")
    lines.append(f"- out_checkpoint: `{args.out_checkpoint}`")
    lines.append(f"- eval_csv: `{args.eval_csv}`")
    lines.append(f"- rows: {len(rows)}")
    lines.append(f"- split_counts: `{dict(split_counts)}`")
    lines.append(f"- role_counts: `{dict(role_counts)}`")
    lines.append(f"- label_type_counts: `{dict(label_counts)}`")
    lines.append("")
    lines.append("## Training config")
    lines.append("")
    lines.append(f"- train_scope: `{args.train_scope}`")
    lines.append(f"- epochs: {args.epochs}")
    lines.append(f"- lr: {args.lr}")
    lines.append(f"- kl_weight: {args.kl_weight}")
    lines.append(f"- anchor_kl_splits: `{args.anchor_kl_splits}`")
    lines.append(f"- weight_decay: {args.weight_decay}")
    lines.append(f"- seed: {args.seed}")
    lines.append(f"- saved_checkpoint: {saved_checkpoint}")
    lines.append("")
    lines.append("## Summary by split")
    lines.append("")
    lines.append("| phase | split | rows | top1 | top1_rate | mean_rank | mean_target_prob | mean_target_ce |")
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|")
    for phase in ("before", "after"):
        for split in ("train_candidate", "train_teacher_divergence", "heldout_retention", "ALL"):
            item = summary.get((phase, split))
            if not item:
                continue
            lines.append(
                f"| {phase} | {split} | {item['rows']} | {item['top1']} | "
                f"{item['top1_rate']:.3f} | {item['mean_rank']:.2f} | "
                f"{item['mean_target_prob']:.6f} | {item['mean_target_ce']:.6f} |"
            )
    lines.append("")
    lines.append("## Before/after movement")
    lines.append("")
    lines.append("| split | rank_improved | rank_same | rank_regressed | prob_improved | prob_same | prob_regressed |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|")
    for split in ("train_candidate", "train_teacher_divergence", "heldout_retention"):
        c = comparison.get(split, {})
        lines.append(
            f"| {split} | {c.get('rank_improved', 0)} | {c.get('rank_same', 0)} | "
            f"{c.get('rank_regressed', 0)} | {c.get('prob_improved', 0)} | "
            f"{c.get('prob_same', 0)} | {c.get('prob_regressed', 0)} |"
        )
    lines.append("")
    lines.append("## Train candidate rows")
    lines.append("")
    lines.append("| id | label_type | side | target | weight |")
    lines.append("|---|---|---|---|---:|")
    for r in rows:
        if r.split == "train_candidate":
            lines.append(
                f"| `{r.row_id}` | `{r.label_type}` | {r.side_to_move} | "
                f"{xy_to_str(r.target_xy)} | {r.weight:.2f} |"
            )
    lines.append("")
    lines.append("## Decision")
    lines.append("")
    lines.append(
        "This artifact only measures whether the accepted 8-row candidate subset can move "
        "policy mass toward its targets while tracking retention/teacher-divergence side effects. "
        "It is not an export, benchmark, promotion, or capacity decision."
    )
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def train(args: argparse.Namespace) -> None:
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)

    if args.device == "cuda":
        device = torch.device("cuda")
    elif args.device == "cpu":
        device = torch.device("cpu")
    else:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    dataset_meta, rows = prepare_rows(
        args.dataset,
        args.board_size,
        strict_splits=not args.no_strict_splits,
    )

    train_indices = [i for i, r in enumerate(rows) if r.split == "train_candidate"]
    if len(train_indices) != 8 and not args.no_strict_splits:
        raise ValueError(f"expected exactly 8 train_candidate rows, got {len(train_indices)}")

    anchor_kl_splits = tuple(
        item.strip()
        for item in str(args.anchor_kl_splits).split(",")
        if item.strip()
    )
    if "heldout_retention" in anchor_kl_splits and not args.no_strict_splits:
        raise ValueError("heldout_retention must remain evaluation-only in strict mode")
    anchor_indices = [i for i, r in enumerate(rows) if r.split in anchor_kl_splits]
    if not anchor_indices:
        raise ValueError(f"no KL anchor rows selected by anchor_kl_splits={anchor_kl_splits}")

    print(f"device={device}")
    print(f"base_checkpoint={args.base_checkpoint}")
    print(f"out_checkpoint={args.out_checkpoint}")
    print(f"ce_training_rows={len(train_indices)}")
    print(f"anchor_kl_splits={anchor_kl_splits}")
    print(f"anchor_kl_rows={len(anchor_indices)}")
    print("IMPORTANT: no C export, no benchmark, no promotion/current-best overwrite.")

    states_np = np.stack([r.state for r in rows])
    masks_np = np.stack([r.legal_mask for r in rows])
    target_actions_np = np.asarray([r.target_action for r in rows], dtype=np.int64)
    weights_np = np.asarray([r.weight for r in rows], dtype=np.float32)

    states = torch.tensor(states_np, dtype=torch.float32, device=device)
    masks = torch.tensor(masks_np, dtype=torch.float32, device=device)
    target_actions = torch.tensor(target_actions_np, dtype=torch.long, device=device)
    weights = torch.tensor(weights_np, dtype=torch.float32, device=device)

    train_index_tensor = torch.tensor(train_indices, dtype=torch.long, device=device)
    anchor_index_tensor = torch.tensor(anchor_indices, dtype=torch.long, device=device)

    model = load_model(args, args.base_checkpoint, device)
    reference = load_model(args, args.base_checkpoint, device)
    reference.eval()
    for p in reference.parameters():
        p.requires_grad = False

    before = evaluate_model("before", model, rows, states.detach().cpu(), masks.detach().cpu(), device)

    if args.dry_run:
        print("dry-run: no training, no checkpoint, no eval/report writes")
        for r in before:
            if r["split"] == "train_candidate":
                print(
                    f"BEFORE {r['id']} target={r['policy_target']} "
                    f"rank={r['target_rank']} prob={r['target_prob']} "
                    f"top={r['top_move']}"
                )
        return

    optimizer = torch.optim.AdamW(
        configure_trainable(model, args.train_scope),
        lr=args.lr,
        weight_decay=args.weight_decay,
    )

    with torch.no_grad():
        ref_logits, _ = reference(states)
        ref_probs = torch.exp(masked_log_softmax(ref_logits, masks))

    for epoch in range(1, args.epochs + 1):
        set_training_mode(model, args.train_scope)

        logits, _values = model(states)
        log_probs = masked_log_softmax(logits, masks)

        train_log_probs = log_probs[train_index_tensor]
        train_target_actions = target_actions[train_index_tensor]
        train_weights = weights[train_index_tensor]
        ce_per_row = -train_log_probs.gather(1, train_target_actions[:, None]).squeeze(1)
        ce_loss = (ce_per_row * train_weights).sum() / train_weights.sum()

        anchor_log_probs = log_probs[anchor_index_tensor]
        anchor_ref_probs = ref_probs[anchor_index_tensor]
        anchor_weights = weights[anchor_index_tensor]
        anchor_kl = (
            anchor_ref_probs
            * (torch.log(anchor_ref_probs.clamp_min(1e-12)) - anchor_log_probs)
        ).sum(dim=-1)
        kl_loss = (anchor_kl * anchor_weights).sum() / anchor_weights.sum()

        loss = ce_loss + args.kl_weight * kl_loss

        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()

        if epoch == 1 or epoch == args.epochs or epoch % args.print_every == 0:
            print(
                f"epoch {epoch:03d}/{args.epochs} "
                f"loss={float(loss.item()):.6f} "
                f"train_ce={float(ce_loss.item()):.6f} "
                f"anchor_kl={float(kl_loss.item()):.6f}",
                flush=True,
            )

    after = evaluate_model("after", model, rows, states.detach().cpu(), masks.detach().cpu(), device)
    records = before + after

    saved_checkpoint = False
    if not args.no_save:
        args.out_checkpoint.parent.mkdir(parents=True, exist_ok=True)
        torch.save(
            {
                "model": model.state_dict(),
                "board_size": args.board_size,
                "win_length": args.win_length,
                "channels": args.channels,
                "blocks": args.blocks,
                "teacher_divergence_policy_anchor_probe": {
                    "scope": "anchored policy-focused signal probe only; no C export/no benchmark/no promotion",
                    "dataset": str(args.dataset),
                    "base_checkpoint": str(args.base_checkpoint),
                    "ce_train_split": "train_candidate",
                    "ce_train_rows": len(train_indices),
                    "anchor_kl_splits": list(anchor_kl_splits),
                    "anchor_kl_rows": len(anchor_indices),
                    "eval_rows": len(rows),
                    "epochs": args.epochs,
                    "lr": args.lr,
                    "kl_weight": args.kl_weight,
                    "weight_decay": args.weight_decay,
                    "train_scope": args.train_scope,
                    "seed": args.seed,
                },
            },
            args.out_checkpoint,
        )
        saved_checkpoint = True

    write_eval_csv(args.eval_csv, records)
    write_report(args.report, args, dataset_meta, rows, before, after, saved_checkpoint)

    print(f"wrote eval csv: {args.eval_csv}")
    print(f"wrote report: {args.report}")
    if saved_checkpoint:
        print(f"wrote checkpoint: {args.out_checkpoint}")
    else:
        print("no checkpoint saved due to --no-save")


def main() -> None:
    args = parse_args()
    train(args)


if __name__ == "__main__":
    main()
