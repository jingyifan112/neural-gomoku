from __future__ import annotations

import argparse
import csv
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import torch

from gomoku_agent.board import BLACK, WHITE, Board
from gomoku_agent.checkpoint import load_compatible_checkpoint
from gomoku_agent.model import PolicyValueNet, masked_policy


SIDE_TO_PLAYER = {"black": BLACK, "white": WHITE}


@dataclass(frozen=True)
class CensusPosition:
    game_id: int
    ply: int
    side_to_move: str
    last_move: str
    model_move: str
    teacher_move: str
    logged_value: float
    teacher_continuation: str
    notes: str
    black: tuple[str, ...]
    white: tuple[str, ...]


POSITIONS: tuple[CensusPosition, ...] = (
    CensusPosition(
        game_id=2,
        ply=13,
        side_to_move="white",
        last_move="9,8",
        model_move="8,8",
        teacher_move="8,8",
        logged_value=-0.674789,
        teacher_continuation="teacher_aligned",
        notes="Rapfi agrees with Candidate D; included as the pre-divergence anchor.",
        black=("4,6", "5,7", "6,7", "7,7", "6,8", "7,8", "9,8"),
        white=("3,5", "5,6", "6,6", "7,6", "8,7", "5,9"),
    ),
    CensusPosition(
        game_id=2,
        ply=15,
        side_to_move="white",
        last_move="8,9",
        model_move="7,10",
        teacher_move="7,9",
        logged_value=-0.114186,
        teacher_continuation="strong_teacher_preference",
        notes="First major teacher divergence after the Candidate D move15 repair.",
        black=("4,6", "5,7", "6,7", "7,7", "6,8", "7,8", "9,8", "8,9"),
        white=("3,5", "5,6", "6,6", "7,6", "8,7", "8,8", "5,9"),
    ),
    CensusPosition(
        game_id=2,
        ply=17,
        side_to_move="white",
        last_move="8,6",
        model_move="9,5",
        teacher_move="9,9",
        logged_value=-0.401256,
        teacher_continuation="strong_teacher_preference",
        notes="Second major teacher divergence; no simple one-ply fork explains it.",
        black=("4,6", "8,6", "5,7", "6,7", "7,7", "6,8", "7,8", "9,8", "8,9"),
        white=("3,5", "5,6", "6,6", "7,6", "8,7", "8,8", "5,9", "7,10"),
    ),
    CensusPosition(
        game_id=2,
        ply=19,
        side_to_move="white",
        last_move="9,10",
        model_move="10,11",
        teacher_move="10,11",
        logged_value=-0.587536,
        teacher_continuation="teacher_aligned",
        notes="Direct policy diverged in the smoke log, but Candidate D MCTS matched Rapfi.",
        black=("4,6", "8,6", "5,7", "6,7", "7,7", "6,8", "7,8", "9,8", "8,9", "9,10"),
        white=("3,5", "9,5", "5,6", "6,6", "7,6", "8,7", "8,8", "5,9", "7,10"),
    ),
    CensusPosition(
        game_id=2,
        ply=21,
        side_to_move="white",
        last_move="7,9",
        model_move="8,10",
        teacher_move="8,10",
        logged_value=-0.395404,
        teacher_continuation="teacher_aligned",
        notes="Direct policy diverged in the smoke log, but Candidate D MCTS matched Rapfi.",
        black=("4,6", "8,6", "5,7", "6,7", "7,7", "6,8", "7,8", "9,8", "7,9", "8,9", "9,10"),
        white=("3,5", "9,5", "5,6", "6,6", "7,6", "8,7", "8,8", "5,9", "7,10", "10,11"),
    ),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Census Candidate D policy/value disagreement against Rapfi teacher moves."
    )
    parser.add_argument("--checkpoint", type=Path, default=None)
    parser.add_argument(
        "--output-csv",
        type=Path,
        default=Path("analysis/integration_eval/candidate_d_teacher_disagreement_census.csv"),
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=Path("analysis/integration_eval/candidate_d_teacher_disagreement_census.md"),
    )
    parser.add_argument("--board-size", type=int, default=15)
    parser.add_argument("--win-length", type=int, default=5)
    parser.add_argument("--channels", type=int, default=64)
    parser.add_argument("--blocks", type=int, default=4)
    parser.add_argument("--top-k", type=int, default=5)
    return parser.parse_args()


def coord_to_xy(coord: str) -> tuple[int, int]:
    x_text, y_text = coord.split(",", maxsplit=1)
    return int(x_text), int(y_text)


def coord_to_action(coord: str, board_size: int) -> int:
    x, y = coord_to_xy(coord)
    return y * board_size + x


def action_to_coord(action: int, board_size: int) -> str:
    row, col = divmod(int(action), board_size)
    return f"{col},{row}"


def build_board(position: CensusPosition, board_size: int, win_length: int) -> Board:
    board = Board(size=board_size, win_length=win_length)
    for coord in position.black:
        x, y = coord_to_xy(coord)
        board.grid[y, x] = BLACK
    for coord in position.white:
        x, y = coord_to_xy(coord)
        board.grid[y, x] = WHITE
    board.current_player = SIDE_TO_PLAYER[position.side_to_move]
    board.move_count = len(position.black) + len(position.white)
    if position.last_move:
        x, y = coord_to_xy(position.last_move)
        board.last_move = (y, x)
    return board


def load_model(args: argparse.Namespace, device: torch.device) -> PolicyValueNet | None:
    if args.checkpoint is None:
        return None

    model = PolicyValueNet(args.board_size, channels=args.channels, blocks=args.blocks).to(device)
    loaded = load_compatible_checkpoint(
        model,
        args.checkpoint,
        device,
        board_size=args.board_size,
        channels=args.channels,
        blocks=args.blocks,
    )
    if not loaded:
        raise RuntimeError(f"could not load compatible checkpoint: {args.checkpoint}")
    model.eval()
    return model


@torch.no_grad()
def eval_policy(model: PolicyValueNet, board: Board, device: torch.device, top_k: int) -> dict[str, Any]:
    state = torch.tensor(board.encode()[None, ...], dtype=torch.float32, device=device)
    legal_mask = torch.tensor(board.legal_mask()[None, ...], dtype=torch.float32, device=device)
    logits, value = model(state)
    probs = masked_policy(logits, legal_mask, temperature=1.0)[0]
    legal_actions = [int(action) for action in board.legal_moves()]
    ranked = sorted(
        ((action, float(probs[action].item())) for action in legal_actions),
        key=lambda item: item[1],
        reverse=True,
    )
    return {
        "value": float(value[0].item()),
        "ranked": ranked,
        "top_moves": " ".join(
            f"{action_to_coord(action, board.size)}:{prob:.6f}"
            for action, prob in ranked[:top_k]
        ),
    }


@torch.no_grad()
def value_after_move(
    model: PolicyValueNet,
    board: Board,
    move: str,
    device: torch.device,
) -> float:
    action = coord_to_action(move, board.size)
    child = board.clone()
    result = child.play_flat(action)
    if result.winner == board.current_player:
        return 1.0
    if result.done:
        return 0.0

    state = torch.tensor(child.encode()[None, ...], dtype=torch.float32, device=device)
    _, child_value = model(state)
    return -float(child_value[0].item())


def rank_and_prob(ranked: list[tuple[int, float]], move: str, board_size: int) -> tuple[int, float]:
    action = coord_to_action(move, board_size)
    for index, (candidate, prob) in enumerate(ranked, start=1):
        if candidate == action:
            return index, prob
    raise ValueError(f"move is not legal: {move}")


def empty_probe_fields() -> dict[str, str]:
    return {
        "policy_top_moves": "NA",
        "teacher_policy_rank": "NA",
        "model_move_policy_prob": "NA",
        "teacher_move_policy_prob": "NA",
        "policy_probability_gap_teacher_minus_model": "NA",
        "root_value": "NA",
        "value_model_move": "NA",
        "value_teacher_move": "NA",
        "value_gap_teacher_minus_model": "NA",
        "teacher_top3_policy": "NA",
        "teacher_value_disfavored": "NA",
    }


def build_row(
    position: CensusPosition,
    board: Board,
    model: PolicyValueNet | None,
    device: torch.device,
    top_k: int,
) -> dict[str, str]:
    row = {
        "game_id": str(position.game_id),
        "ply": str(position.ply),
        "side_to_move": position.side_to_move,
        "last_move": position.last_move,
        "model_move": position.model_move,
        "teacher_move": position.teacher_move,
        "model_teacher_diverge": str(position.model_move != position.teacher_move),
        "logged_root_value": f"{position.logged_value:.6f}",
        "teacher_continuation": position.teacher_continuation,
        "strong_teacher_preference": str(position.teacher_continuation == "strong_teacher_preference"),
        "notes": position.notes,
    }

    if model is None:
        row.update(empty_probe_fields())
        return row

    probe = eval_policy(model, board, device, top_k)
    ranked = probe["ranked"]
    model_rank, model_prob = rank_and_prob(ranked, position.model_move, board.size)
    teacher_rank, teacher_prob = rank_and_prob(ranked, position.teacher_move, board.size)
    model_value = value_after_move(model, board, position.model_move, device)
    teacher_value = value_after_move(model, board, position.teacher_move, device)

    row.update(
        {
            "policy_top_moves": str(probe["top_moves"]),
            "teacher_policy_rank": str(teacher_rank),
            "model_move_policy_prob": f"{model_prob:.6f}",
            "teacher_move_policy_prob": f"{teacher_prob:.6f}",
            "policy_probability_gap_teacher_minus_model": f"{teacher_prob - model_prob:.6f}",
            "root_value": f"{probe['value']:.6f}",
            "value_model_move": f"{model_value:.6f}",
            "value_teacher_move": f"{teacher_value:.6f}",
            "value_gap_teacher_minus_model": f"{teacher_value - model_value:.6f}",
            "teacher_top3_policy": str(teacher_rank <= 3),
            "teacher_value_disfavored": str(teacher_value < model_value),
        }
    )
    return row


def output_fields() -> list[str]:
    return [
        "game_id",
        "ply",
        "side_to_move",
        "last_move",
        "model_move",
        "teacher_move",
        "model_teacher_diverge",
        "teacher_policy_rank",
        "model_move_policy_prob",
        "teacher_move_policy_prob",
        "policy_probability_gap_teacher_minus_model",
        "logged_root_value",
        "root_value",
        "value_model_move",
        "value_teacher_move",
        "value_gap_teacher_minus_model",
        "teacher_top3_policy",
        "teacher_value_disfavored",
        "teacher_continuation",
        "strong_teacher_preference",
        "policy_top_moves",
        "notes",
    ]


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=output_fields(), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def count_true(rows: list[dict[str, str]], key: str) -> int:
    return sum(1 for row in rows if row[key] == "True")


def count_applicable(rows: list[dict[str, str]], key: str) -> int:
    return sum(1 for row in rows if row[key] != "NA")


def write_markdown(path: Path, rows: list[dict[str, str]], checkpoint: Path | None) -> None:
    divergence_rows = [row for row in rows if row["model_teacher_diverge"] == "True"]
    strong_rows = [row for row in rows if row["strong_teacher_preference"] == "True"]
    continuation_counts = Counter(row["teacher_continuation"] for row in rows)
    prob_applicable = count_applicable(divergence_rows, "teacher_top3_policy")
    value_applicable = count_applicable(divergence_rows, "teacher_value_disfavored")

    lines = [
        "# Candidate D teacher disagreement census",
        "",
        "## Implementation plan",
        "",
        "1. Use the audited Candidate D mcts32 game2 teacher ledger as the seed set.",
        "2. Reconstruct each board with side-to-move and last-move channel.",
        "3. Probe Candidate D direct policy for teacher rank, teacher/model probabilities, and top-k moves.",
        "4. Probe child-state value after the model move and after the teacher move, negating the child value back to the mover's perspective.",
        "5. Summarize whether teacher disagreements are already known to policy or require larger distillation.",
        "",
        "## Scope",
        "",
        f"- checkpoint: `{checkpoint}`" if checkpoint else "- checkpoint: not provided; model-probe fields are `NA`.",
        "- coordinate convention: `x,y` with zero-based `x=col,y=row`.",
        "- audited loss coverage in this checkout: Candidate D mcts32 game2 critical positions from the existing Rapfi teacher ledger.",
        "",
        "## Census table",
        "",
        "| game | ply | model | teacher | teacher rank | policy gap | value(model) | value(teacher) | teacher top-3 | value-disfavored | teacher continuation |",
        "| --- | ---: | --- | --- | ---: | ---: | ---: | ---: | --- | --- | --- |",
    ]

    for row in rows:
        lines.append(
            "| {game_id} | {ply} | {model_move} | {teacher_move} | {teacher_policy_rank} | "
            "{policy_probability_gap_teacher_minus_model} | {value_model_move} | "
            "{value_teacher_move} | {teacher_top3_policy} | {teacher_value_disfavored} | "
            "{teacher_continuation} |".format(**row)
        )

    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- positions audited: {len(rows)}",
            f"- model/teacher divergences: {len(divergence_rows)}",
            f"- strong teacher-continuation preferences: {len(strong_rows)}",
        ]
    )
    for label, count in sorted(continuation_counts.items()):
        lines.append(f"- {label}: {count}")

    if prob_applicable:
        lines.extend(
            [
                f"- divergent teacher moves already top-3 policy: {count_true(divergence_rows, 'teacher_top3_policy')}/{prob_applicable}",
                f"- divergent teacher moves value-disfavored: {count_true(divergence_rows, 'teacher_value_disfavored')}/{value_applicable}",
            ]
        )
    else:
        lines.append("- policy/value counts unavailable until the Candidate D checkpoint is supplied.")

    lines.extend(
        [
            "",
            "## Conclusions",
            "",
        ]
    )

    if prob_applicable:
        top3 = count_true(divergence_rows, "teacher_top3_policy")
        disfavored = count_true(divergence_rows, "teacher_value_disfavored")
        if top3 == len(divergence_rows) and disfavored >= max(1, len(divergence_rows) // 2):
            conclusion = (
                "The dominant failure mode is A: value/search is suppressing teacher-recommended "
                "moves that the policy already knows well enough to keep near the top."
            )
            recommendation = (
                "Run a value-aware teacher-counterfactual experiment: keep Candidate D's repaired "
                "move15 target, add teacher continuations for move15 and move17, and train with a "
                "child-value ranking or pairwise preference loss so teacher moves must overtake the "
                "model moves in both policy and value probes before any Rapfi smoke rerun."
            )
        elif top3 < len(divergence_rows):
            conclusion = (
                "The dominant failure mode is B: at least one strong teacher move is outside top-3 "
                "policy, so the model is missing policy knowledge rather than merely undervaluing "
                "an already available option."
            )
            recommendation = (
                "Run larger teacher distillation on the first-divergence positions and nearby "
                "teacher continuations, then gate on teacher rank/probability before value tuning."
            )
        else:
            conclusion = (
                "The census is mixed: teacher moves are policy-visible, but value does not "
                "consistently explain the suppression."
            )
            recommendation = (
                "Run a small combined policy/value distillation, then re-run this census before "
                "committing to a larger Rapfi smoke."
            )
    else:
        conclusion = (
            "The audited ledger still points at move15 and move17 as the first major disagreements, "
            "but the local checkout cannot decide A versus B without a compatible Candidate D checkpoint."
        )
        recommendation = (
            "Supply the Candidate D checkpoint and re-run this script; the report will then fill "
            "teacher rank, probability gap, and child-value comparisons automatically."
        )

    lines.extend(
        [
            conclusion,
            "",
            "## Recommendation",
            "",
            recommendation,
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    args = parse_args()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = load_model(args, device)

    rows: list[dict[str, str]] = []
    for position in POSITIONS:
        board = build_board(position, args.board_size, args.win_length)
        rows.append(build_row(position, board, model, device, args.top_k))

    write_csv(args.output_csv, rows)
    write_markdown(args.output_md, rows, args.checkpoint)
    print(f"device={device}")
    print(f"positions={len(rows)}")
    print(f"wrote {args.output_csv}")
    print(f"wrote {args.output_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
