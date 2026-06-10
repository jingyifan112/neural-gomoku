from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path


BOARD_SIZE = 15


@dataclass(frozen=True)
class TeacherSpec:
    case_id: str
    game_id: int
    ply: int
    side_to_move: str
    last_move_xy: tuple[int, int]
    policy_targets: tuple[tuple[tuple[int, int], float], ...]
    sample_weight: float
    role: str
    notes: str
    black: tuple[tuple[int, int], ...]
    white: tuple[tuple[int, int], ...]


BASE_SPECS: tuple[TeacherSpec, ...] = (
    TeacherSpec(
        case_id="candidate_g_g2_p13_teacher_anchor_8_8",
        game_id=2,
        ply=13,
        side_to_move="white",
        last_move_xy=(9, 8),
        policy_targets=(((8, 8), 1.0),),
        sample_weight=0.5,
        role="nearby_teacher_anchor",
        notes="Pre-divergence anchor where Rapfi and Candidate D agree.",
        black=((4, 6), (5, 7), (6, 7), (7, 7), (6, 8), (7, 8), (9, 8)),
        white=((3, 5), (5, 6), (6, 6), (7, 6), (8, 7), (5, 9)),
    ),
    TeacherSpec(
        case_id="candidate_g_g2_p15_teacher_7_9_preserve_7_10",
        game_id=2,
        ply=15,
        side_to_move="white",
        last_move_xy=(8, 9),
        policy_targets=(((7, 9), 0.70), ((7, 10), 0.30)),
        sample_weight=2.0,
        role="strong_teacher_divergence",
        notes="Main ply15 teacher target while keeping Candidate D repaired move 7,10 policy-visible.",
        black=((4, 6), (5, 7), (6, 7), (7, 7), (6, 8), (7, 8), (9, 8), (8, 9)),
        white=((3, 5), (5, 6), (6, 6), (7, 6), (8, 7), (8, 8), (5, 9)),
    ),
    TeacherSpec(
        case_id="candidate_g_g2_p17_teacher_9_9",
        game_id=2,
        ply=17,
        side_to_move="white",
        last_move_xy=(8, 6),
        policy_targets=(((9, 9), 1.0),),
        sample_weight=3.0,
        role="strong_teacher_divergence",
        notes="Main ply17 teacher target; census rank was 70.",
        black=((4, 6), (8, 6), (5, 7), (6, 7), (7, 7), (6, 8), (7, 8), (9, 8), (8, 9)),
        white=((3, 5), (5, 6), (6, 6), (7, 6), (8, 7), (8, 8), (5, 9), (7, 10)),
    ),
    TeacherSpec(
        case_id="candidate_g_g2_p19_teacher_continuation_10_11",
        game_id=2,
        ply=19,
        side_to_move="white",
        last_move_xy=(9, 10),
        policy_targets=(((10, 11), 1.0),),
        sample_weight=1.0,
        role="nearby_teacher_continuation",
        notes="Teacher-aligned MCTS continuation after the divergent segment.",
        black=((4, 6), (8, 6), (5, 7), (6, 7), (7, 7), (6, 8), (7, 8), (9, 8), (8, 9), (9, 10)),
        white=((3, 5), (9, 5), (5, 6), (6, 6), (7, 6), (8, 7), (8, 8), (5, 9), (7, 10)),
    ),
    TeacherSpec(
        case_id="candidate_g_g2_p21_teacher_continuation_8_10",
        game_id=2,
        ply=21,
        side_to_move="white",
        last_move_xy=(7, 9),
        policy_targets=(((8, 10), 1.0),),
        sample_weight=1.0,
        role="nearby_teacher_continuation",
        notes="Teacher-aligned MCTS continuation after the divergent segment.",
        black=((4, 6), (8, 6), (5, 7), (6, 7), (7, 7), (6, 8), (7, 8), (9, 8), (7, 9), (8, 9), (9, 10)),
        white=((3, 5), (9, 5), (5, 6), (6, 6), (7, 6), (8, 7), (8, 8), (5, 9), (7, 10), (10, 11)),
    ),
)


TACTICAL_ANCHORS: tuple[TeacherSpec, ...] = (
    TeacherSpec(
        case_id="candidate_g_tactical_opponent_four_one_endpoint",
        game_id=0,
        ply=0,
        side_to_move="black",
        last_move_xy=(4, 4),
        policy_targets=(((5, 4), 1.0),),
        sample_weight=0.8,
        role="tactical_regression_anchor",
        notes="C tactical benchmark anchor: block opponent four.",
        black=((0, 4),),
        white=((1, 4), (2, 4), (3, 4), (4, 4)),
    ),
    TeacherSpec(
        case_id="candidate_g_tactical_opponent_open_three",
        game_id=0,
        ply=0,
        side_to_move="black",
        last_move_xy=(4, 4),
        policy_targets=(((1, 4), 0.5), ((5, 4), 0.5)),
        sample_weight=0.5,
        role="tactical_regression_anchor",
        notes="C tactical benchmark anchor: either open-three endpoint is acceptable.",
        black=((2, 2), (6, 6)),
        white=((2, 4), (3, 4), (4, 4)),
    ),
    TeacherSpec(
        case_id="candidate_g_tactical_model_four_can_win",
        game_id=0,
        ply=0,
        side_to_move="black",
        last_move_xy=(3, 3),
        policy_targets=(((4, 3), 1.0),),
        sample_weight=0.8,
        role="tactical_regression_anchor",
        notes="C tactical benchmark anchor: play immediate winning move.",
        black=((0, 3), (1, 3), (2, 3), (3, 3)),
        white=((0, 0), (1, 1)),
    ),
    TeacherSpec(
        case_id="candidate_g_tactical_broken_four_pattern",
        game_id=0,
        ply=0,
        side_to_move="black",
        last_move_xy=(4, 5),
        policy_targets=(((3, 5), 1.0),),
        sample_weight=0.8,
        role="tactical_regression_anchor",
        notes="C tactical benchmark anchor: fill broken-four gap.",
        black=((1, 5), (2, 5), (4, 5), (5, 5)),
        white=((8, 0), (8, 1)),
    ),
    TeacherSpec(
        case_id="candidate_g_tactical_mcts_safety_must_block_four",
        game_id=0,
        ply=0,
        side_to_move="black",
        last_move_xy=(5, 2),
        policy_targets=(((6, 2), 1.0),),
        sample_weight=0.8,
        role="tactical_regression_anchor",
        notes="C tactical benchmark anchor: block opponent four.",
        black=((1, 2), (7, 7)),
        white=((2, 2), (3, 2), (4, 2), (5, 2)),
    ),
    TeacherSpec(
        case_id="candidate_g_tactical_human_play_vertical_four_must_block",
        game_id=0,
        ply=0,
        side_to_move="white",
        last_move_xy=(3, 6),
        policy_targets=(((3, 7), 1.0),),
        sample_weight=1.5,
        role="tactical_regression_anchor",
        notes="C tactical benchmark anchor that regressed in the first Candidate G run.",
        black=((3, 3), (2, 4), (3, 4), (4, 4), (3, 5), (3, 6)),
        white=((3, 2), (6, 2), (4, 5), (6, 6), (0, 7), (6, 8)),
    ),
    TeacherSpec(
        case_id="candidate_g_tactical_human_play_prevent_open_four_fork",
        game_id=0,
        ply=0,
        side_to_move="white",
        last_move_xy=(4, 7),
        policy_targets=(((7, 4), 1.0),),
        sample_weight=0.4,
        role="tactical_regression_anchor",
        notes="Known difficult tactical case; low-weight anchor to avoid worsening it.",
        black=((3, 2), (2, 3), (3, 3), (4, 3), (2, 4), (3, 4), (4, 4), (1, 5), (3, 5), (5, 5), (6, 5), (0, 6), (5, 6), (4, 7)),
        white=((3, 1), (5, 1), (4, 2), (6, 2), (1, 3), (1, 4), (2, 5), (4, 5), (2, 6), (3, 6), (6, 6), (0, 7), (5, 8)),
    ),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Candidate G teacher policy-distillation dataset.")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("analysis/integration_eval/candidate_g_teacher_policy_dataset.json"),
    )
    parser.add_argument("--no-symmetry-augment", action="store_true")
    parser.add_argument("--no-tactical-anchors", action="store_true")
    return parser.parse_args()


def transform_xy(xy: tuple[int, int], transform: str, size: int = BOARD_SIZE) -> tuple[int, int]:
    x, y = xy
    last = size - 1
    if transform == "identity":
        return x, y
    if transform == "rot90":
        return last - y, x
    if transform == "rot180":
        return last - x, last - y
    if transform == "rot270":
        return y, last - x
    if transform == "flip_x":
        return last - x, y
    if transform == "flip_y":
        return x, last - y
    if transform == "diag":
        return y, x
    if transform == "anti_diag":
        return last - y, last - x
    raise ValueError(f"unknown transform: {transform}")


def empty_board() -> list[list[int]]:
    return [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]


def board_from_stones(black: tuple[tuple[int, int], ...], white: tuple[tuple[int, int], ...]) -> list[list[int]]:
    board = empty_board()
    for x, y in black:
        board[y][x] = 1
    for x, y in white:
        board[y][x] = -1
    return board


def normalize_targets(targets: tuple[tuple[tuple[int, int], float], ...]) -> list[dict[str, object]]:
    total = sum(weight for _, weight in targets)
    if total <= 0:
        raise ValueError("policy target weights must be positive")
    return [
        {
            "xy": [int(xy[0]), int(xy[1])],
            "rc": [int(xy[1]), int(xy[0])],
            "weight": float(weight / total),
        }
        for xy, weight in targets
    ]


def make_sample(spec: TeacherSpec, transform: str) -> dict[str, object]:
    black = tuple(transform_xy(xy, transform) for xy in spec.black)
    white = tuple(transform_xy(xy, transform) for xy in spec.white)
    last_move_xy = transform_xy(spec.last_move_xy, transform)
    policy_targets = tuple(
        (transform_xy(xy, transform), weight)
        for xy, weight in spec.policy_targets
    )

    board = board_from_stones(black, white)
    for target, _ in policy_targets:
        x, y = target
        if board[y][x] != 0:
            raise ValueError(f"{spec.case_id}/{transform}: target {target} is occupied")

    return {
        "id": f"{spec.case_id}__{transform}",
        "base_case_id": spec.case_id,
        "transform": transform,
        "game_id": spec.game_id,
        "ply": spec.ply,
        "board_size": BOARD_SIZE,
        "win_length": 5,
        "side_to_move": spec.side_to_move,
        "current_player": -1 if spec.side_to_move == "white" else 1,
        "last_move_xy": [last_move_xy[0], last_move_xy[1]],
        "last_move_rc": [last_move_xy[1], last_move_xy[0]],
        "policy_targets": normalize_targets(policy_targets),
        "sample_weight": spec.sample_weight,
        "role": spec.role,
        "notes": spec.notes,
        "board": board,
    }


def build_dataset(use_symmetry: bool, include_tactical_anchors: bool) -> dict[str, object]:
    transforms = (
        "identity",
        "rot90",
        "rot180",
        "rot270",
        "flip_x",
        "flip_y",
        "diag",
        "anti_diag",
    ) if use_symmetry else ("identity",)

    specs = BASE_SPECS + (TACTICAL_ANCHORS if include_tactical_anchors else ())
    samples = [make_sample(spec, transform) for spec in specs for transform in transforms]
    return {
        "name": "candidate_g_teacher_policy_dataset",
        "coordinate_convention": "xy is zero-based x=col,y=row; rc is row,col",
        "purpose": "Policy-focused teacher distillation for Candidate D mcts32 game2 teacher disagreements.",
        "base_specs": [asdict(spec) for spec in BASE_SPECS],
        "tactical_anchors": [asdict(spec) for spec in TACTICAL_ANCHORS] if include_tactical_anchors else [],
        "symmetry_augmentations": list(transforms),
        "samples": samples,
    }


def main() -> int:
    args = parse_args()
    dataset = build_dataset(
        use_symmetry=not args.no_symmetry_augment,
        include_tactical_anchors=not args.no_tactical_anchors,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(dataset, indent=2) + "\n", encoding="utf-8")
    print(f"samples={len(dataset['samples'])}")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
