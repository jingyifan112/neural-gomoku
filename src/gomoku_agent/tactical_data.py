from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np

from .board import BLACK, WHITE, Board
from .self_play import GameSample


@dataclass(frozen=True)
class TacticalCase:
    name: str
    board: Board
    target_moves: tuple[int, ...]
    value: float


Coord = tuple[int, int]
Transform = Callable[[Coord, int], Coord]


def identity(coord: Coord, size: int) -> Coord:
    return coord


def rot90(coord: Coord, size: int) -> Coord:
    row, col = coord
    return col, size - 1 - row


def rot180(coord: Coord, size: int) -> Coord:
    return rot90(rot90(coord, size), size)


def rot270(coord: Coord, size: int) -> Coord:
    return rot90(rot180(coord, size), size)


def flip_horizontal(coord: Coord, size: int) -> Coord:
    row, col = coord
    return row, size - 1 - col


TRANSFORMS: tuple[Transform, ...] = (
    identity,
    rot90,
    rot180,
    rot270,
    flip_horizontal,
    lambda coord, size: rot90(flip_horizontal(coord, size), size),
    lambda coord, size: rot180(flip_horizontal(coord, size), size),
    lambda coord, size: rot270(flip_horizontal(coord, size), size),
)


def make_immediate_win_case(board_size: int = 9, transform: Transform = identity) -> TacticalCase:
    center = board_size // 2
    stones = [
        ((center, 1), BLACK),
        ((center, 2), BLACK),
        ((center, 3), BLACK),
        ((center, 4), BLACK),
        ((center - 2, 0), WHITE),
        ((center - 1, 1), WHITE),
    ]
    return _make_case(
        "immediate_win",
        board_size,
        BLACK,
        stones,
        [(center, 5)],
        value=1.0,
        last_move=(center, 4),
        transform=transform,
    )


def make_block_immediate_win_case(board_size: int = 9, transform: Transform = identity) -> TacticalCase:
    center = board_size // 2
    stones = [
        ((center, 0), BLACK),
        ((center, 1), WHITE),
        ((center, 2), WHITE),
        ((center, 3), WHITE),
        ((center, 4), WHITE),
        ((center + 2, 0), BLACK),
    ]
    return _make_case(
        "block_immediate_win",
        board_size,
        BLACK,
        stones,
        [(center, 5)],
        value=0.0,
        last_move=(center, 4),
        transform=transform,
    )


def make_open_four_case(board_size: int = 9, transform: Transform = identity) -> TacticalCase:
    center = board_size // 2
    stones = [
        ((center, 2), BLACK),
        ((center, 3), BLACK),
        ((center, 4), BLACK),
        ((center, 5), BLACK),
        ((center - 2, 2), WHITE),
        ((center + 2, 6), WHITE),
    ]
    return _make_case(
        "open_four",
        board_size,
        BLACK,
        stones,
        [(center, 1), (center, 6)],
        value=1.0,
        last_move=(center, 5),
        transform=transform,
    )


def make_double_threat_prevention_case(board_size: int = 9, transform: Transform = identity) -> TacticalCase:
    offset = (board_size - 9) // 2
    stones = [
        ((1 + offset, 3 + offset), WHITE),
        ((1 + offset, 5 + offset), WHITE),
        ((2 + offset, 3 + offset), BLACK),
        ((2 + offset, 4 + offset), WHITE),
        ((2 + offset, 6 + offset), WHITE),
        ((3 + offset, 1 + offset), WHITE),
        ((3 + offset, 2 + offset), BLACK),
        ((3 + offset, 3 + offset), BLACK),
        ((3 + offset, 4 + offset), BLACK),
        ((4 + offset, 1 + offset), WHITE),
        ((4 + offset, 2 + offset), BLACK),
        ((4 + offset, 3 + offset), BLACK),
        ((4 + offset, 4 + offset), BLACK),
        ((5 + offset, 1 + offset), BLACK),
        ((5 + offset, 2 + offset), WHITE),
        ((5 + offset, 3 + offset), BLACK),
        ((5 + offset, 4 + offset), WHITE),
        ((5 + offset, 5 + offset), BLACK),
        ((5 + offset, 6 + offset), BLACK),
        ((6 + offset, 0 + offset), BLACK),
        ((6 + offset, 2 + offset), WHITE),
        ((6 + offset, 3 + offset), WHITE),
        ((6 + offset, 5 + offset), BLACK),
        ((6 + offset, 6 + offset), WHITE),
        ((7 + offset, 0 + offset), WHITE),
        ((7 + offset, 4 + offset), BLACK),
        ((8 + offset, 5 + offset), WHITE),
    ]
    return _make_case(
        "double_threat_prevention",
        board_size,
        WHITE,
        stones,
        [(4 + offset, 7 + offset)],
        value=0.0,
        last_move=(7 + offset, 4 + offset),
        transform=transform,
    )


def make_diamond_cross_case(board_size: int = 9, transform: Transform = identity) -> TacticalCase:
    offset = (board_size - 9) // 2
    stones = [
        ((2 + offset, 6 + offset), WHITE),
        ((3 + offset, 3 + offset), BLACK),
        ((4 + offset, 2 + offset), BLACK),
        ((4 + offset, 4 + offset), BLACK),
        ((5 + offset, 3 + offset), BLACK),
        ((5 + offset, 4 + offset), WHITE),
        ((8 + offset, 6 + offset), WHITE),
    ]
    return _make_case(
        "diamond_to_cross_fork",
        board_size,
        WHITE,
        stones,
        [(4 + offset, 3 + offset)],
        value=0.0,
        last_move=(4 + offset, 4 + offset),
        transform=transform,
    )


CASE_BUILDERS: tuple[Callable[[int, Transform], TacticalCase], ...] = (
    make_immediate_win_case,
    make_block_immediate_win_case,
    make_open_four_case,
    make_double_threat_prevention_case,
    make_diamond_cross_case,
)


def generate_tactical_cases(count: int, board_size: int = 9, seed: int = 0) -> list[TacticalCase]:
    if board_size < 9:
        raise ValueError("tactical generator requires board_size >= 9")
    rng = np.random.default_rng(seed)
    cases: list[TacticalCase] = []
    for idx in range(count):
        builder = CASE_BUILDERS[idx % len(CASE_BUILDERS)]
        transform = TRANSFORMS[int(rng.integers(0, len(TRANSFORMS)))]
        cases.append(builder(board_size, transform))
    return cases


def generate_tactical_samples(count: int, board_size: int = 9, seed: int = 0) -> list[GameSample]:
    return [case_to_sample(case) for case in generate_tactical_cases(count, board_size, seed)]


def case_to_sample(case: TacticalCase) -> GameSample:
    policy = np.zeros(case.board.size * case.board.size, dtype=np.float32)
    for action in case.target_moves:
        policy[int(action)] = 1.0 / len(case.target_moves)
    return GameSample(state=case.board.encode(), policy=policy, value=case.value)


def _make_case(
    name: str,
    board_size: int,
    current_player: int,
    stones: list[tuple[Coord, int]],
    targets: list[Coord],
    value: float,
    last_move: Coord,
    transform: Transform,
) -> TacticalCase:
    board = Board(size=board_size, win_length=5)
    board.current_player = current_player
    for coord, player in stones:
        row, col = transform(coord, board_size)
        board.grid[row, col] = player
    board.move_count = int(np.count_nonzero(board.grid))
    board.last_move = transform(last_move, board_size)
    target_moves = tuple(_flat(transform(coord, board_size), board_size) for coord in targets)
    return TacticalCase(name=name, board=board, target_moves=target_moves, value=value)


def _flat(coord: Coord, board_size: int) -> int:
    row, col = coord
    return row * board_size + col
