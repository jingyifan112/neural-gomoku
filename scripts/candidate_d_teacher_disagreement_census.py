from __future__ import annotations

import argparse
import csv
import json
import math
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import torch

from gomoku_agent.board import BLACK, EMPTY, WHITE, Board
from gomoku_agent.model import PolicyValueNet, masked_policy


BOARD_SIZE = 15
WIN_LENGTH = 5
COORD_RE = re.compile(r"^(?P<x>\d+),(?P<y>\d+)$")
START_RE = re.compile(r"Started game (?P<game>\d+) of \d+ \((?P<black>.+?) vs (?P<white>.+?)\)")
FINISH_RE = re.compile(
    r"Finished game (?P<game>\d+) \((?P<black>.+?) vs (?P<white>.+?)\): "
    r"(?P<black_score>\d+)-(?P<white_score>\d+) \{(?P<reason>.+?)\}"
)
ENGINE_OUTPUT_RE = re.compile(r"(?P<engine>\S+)\s+->\s+(?P<body>.*)$")
ENGINE_DEBUG_RE = re.compile(r"engine\s+(?P<engine>\S+)\s+output\s+(?P<body>.*)$")
DECISION_RE = re.compile(r"(?:DEBUG_DECISION|debug:_DECISION)\s+.*?\bmove_count=(?P<move_count>\d+)\b")
EVAL_RE = re.compile(r"\bEval\s+(?P<eval>[+-]?M\d+|[+-]?\d+)\b")
SEPARATOR_RE = re.compile(r"^\s*-{10,}\s*$")
BOARD_ROW_RE = re.compile(r"^\s*(?:[.XO]\s+){14}[.XO]\s*$")


@dataclass(frozen=True)
class ReplayedDecision:
    game_number: int
    move_count: int
    side_to_move: str
    board: list[list[int]]
    last_move_rc: list[int] | None


@dataclass(frozen=True)
class RapfiResult:
    move_xy: str
    eval_raw: str
    eval_score: float
    bestline: str
    raw_tail: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build a teacher-disagreement census for Candidate D Rapfi mcts32 losses. "
            "This script reads logs/checkpoints and writes analysis artifacts only."
        )
    )
    parser.add_argument(
        "--failure-positions-json",
        type=Path,
        default=Path("analysis/integration_eval/candidate_d_mcts32_debug_failure_positions.json"),
    )
    parser.add_argument(
        "--debug-log",
        type=Path,
        default=Path("eval_logs/rapfi_smoke/candidate_d_move15_mcts32_debug_vs_rapfi_fast_g2.log"),
        help="c-gomoku-cli analysis log with board diagrams, used to replay boards and last moves.",
    )
    parser.add_argument(
        "--checkpoint",
        type=Path,
        default=Path("checkpoints/15x15_current_best_margin_candidate_d_move15_lastmove.pt"),
    )
    parser.add_argument(
        "--rapfi-command",
        default="/Users/jing1fan/gomoku_public_benchmark/run_rapfi.sh",
        help="Rapfi pbrain command used for read-only teacher queries.",
    )
    parser.add_argument("--out-csv", type=Path, default=Path("analysis/integration_eval/candidate_d_teacher_disagreement_census.csv"))
    parser.add_argument("--out-md", type=Path, default=Path("analysis/integration_eval/candidate_d_teacher_disagreement_census.md"))
    parser.add_argument("--max-positions", type=int, default=0, help="Optional debugging limit; 0 means all positions.")
    parser.add_argument("--strong-eval-threshold", type=float, default=200.0)
    parser.add_argument("--timeout-sec", type=float, default=5.0)
    return parser.parse_args()


def xy_to_action(xy: str, board_size: int = BOARD_SIZE) -> int:
    match = COORD_RE.match(xy.strip())
    if not match:
        raise ValueError(f"bad xy coordinate: {xy!r}")
    x = int(match.group("x"))
    y = int(match.group("y"))
    return y * board_size + x


def action_to_xy(action: int, board_size: int = BOARD_SIZE) -> str:
    row, col = divmod(int(action), board_size)
    return f"{col},{row}"


def side_to_player(side: str) -> int:
    side_l = side.lower()
    if side_l == "black":
        return BLACK
    if side_l == "white":
        return WHITE
    raise ValueError(f"unknown side {side!r}")


def player_to_side(player: int) -> str:
    if player == BLACK:
        return "black"
    if player == WHITE:
        return "white"
    raise ValueError(f"unknown player {player}")


def engine_side(game: dict[str, Any], engine: str) -> str:
    if engine == game["black"]:
        return "black"
    if engine == game["white"]:
        return "white"
    return ""


def empty_board_state() -> tuple[np.ndarray, int | None, int]:
    return np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=np.int8), None, 0


def parse_board_block(lines: list[str], start_index: int) -> tuple[np.ndarray, int] | None:
    if not SEPARATOR_RE.match(lines[start_index]):
        return None
    row_start = start_index + 1
    row_end = row_start + BOARD_SIZE
    if row_end >= len(lines):
        return None
    row_lines = lines[row_start:row_end]
    if not all(BOARD_ROW_RE.match(line) for line in row_lines):
        return None
    if not SEPARATOR_RE.match(lines[row_end]):
        return None

    grid = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=np.int8)
    for row, line in enumerate(row_lines):
        for col, token in enumerate(line.strip().split()):
            if token == "X":
                grid[row, col] = BLACK
            elif token == "O":
                grid[row, col] = WHITE
    return grid, row_end


def infer_last_move(previous: np.ndarray, current: np.ndarray) -> int | None:
    changed = np.argwhere(previous != current)
    added = [(int(row), int(col)) for row, col in changed if previous[row, col] == EMPTY and current[row, col] != EMPTY]
    if len(added) == 1:
        row, col = added[0]
        return row * BOARD_SIZE + col
    return None


def replay_decision_boards(debug_log: Path) -> dict[tuple[int, int], ReplayedDecision]:
    lines = debug_log.read_text(encoding="utf-8", errors="replace").splitlines()
    current_game = 0
    black_engine = ""
    white_engine = ""
    grid, last_move, move_count = empty_board_state()
    decisions: dict[tuple[int, int], ReplayedDecision] = {}

    index = 0
    while index < len(lines):
        line = lines[index]
        start = START_RE.search(line)
        if start:
            current_game = int(start.group("game"))
            black_engine = start.group("black")
            white_engine = start.group("white")
            grid, last_move, move_count = empty_board_state()
            index += 1
            continue

        if FINISH_RE.search(line):
            current_game = 0
            index += 1
            continue

        if current_game == 0:
            index += 1
            continue

        block = parse_board_block(lines, index)
        if block is not None:
            next_grid, end_index = block
            inferred = infer_last_move(grid, next_grid)
            if inferred is not None:
                last_move = inferred
            grid = next_grid
            move_count = int((grid != EMPTY).sum())
            index = end_index + 1
            continue

        decision = DECISION_RE.search(line)
        output = ENGINE_OUTPUT_RE.search(line) or ENGINE_DEBUG_RE.search(line)
        if decision and output:
            engine = output.group("engine")
            side = "black" if engine == black_engine else "white" if engine == white_engine else ""
            if side:
                decisions[(current_game, int(decision.group("move_count")))] = ReplayedDecision(
                    game_number=current_game,
                    move_count=int(decision.group("move_count")),
                    side_to_move=side,
                    board=grid.astype(int).tolist(),
                    last_move_rc=None if last_move is None else [last_move // BOARD_SIZE, last_move % BOARD_SIZE],
                )
            index += 1
            continue

        if output:
            engine = output.group("engine")
            body = output.group("body").strip()
            coord = COORD_RE.match(body)
            if coord and engine in {black_engine, white_engine}:
                player = BLACK if engine == black_engine else WHITE
                x = int(coord.group("x"))
                y = int(coord.group("y"))
                if not (0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE):
                    raise ValueError(f"out-of-range move in log: {body}")
                if grid[y, x] != EMPTY:
                    raise ValueError(f"illegal replay move in game {current_game}: {body}")
                grid[y, x] = player
                last_move = y * BOARD_SIZE + x
                move_count += 1
        index += 1

    return decisions


def make_board(board_rows: list[list[int]], current_player: int, last_move_rc: list[int] | None) -> Board:
    board = Board(size=BOARD_SIZE, win_length=WIN_LENGTH)
    board.grid = np.asarray(board_rows, dtype=np.int8)
    board.current_player = current_player
    board.move_count = int((board.grid != 0).sum())
    board.last_move = None if last_move_rc is None else (int(last_move_rc[0]), int(last_move_rc[1]))
    return board


def load_model(checkpoint: Path, device: torch.device) -> PolicyValueNet:
    payload = torch.load(checkpoint, map_location=device)
    model = PolicyValueNet(
        board_size=int(payload.get("board_size", BOARD_SIZE)),
        channels=int(payload.get("channels", 64)),
        blocks=int(payload.get("blocks", 4)),
    ).to(device)
    model.load_state_dict(payload["model"])
    model.eval()
    return model


@torch.no_grad()
def model_policy_value(model: PolicyValueNet, board: Board, device: torch.device) -> tuple[torch.Tensor, torch.Tensor, float]:
    state = torch.tensor(board.encode()[None, ...], dtype=torch.float32, device=device)
    legal = torch.tensor(board.legal_mask()[None, ...], dtype=torch.float32, device=device)
    logits, value = model(state)
    probs = masked_policy(logits, legal, temperature=1.0)[0]
    return logits[0].detach().cpu(), probs.detach().cpu(), float(value[0].item())


def rank_of_action(probs: torch.Tensor, legal_mask: np.ndarray, action: int) -> int:
    legal_actions = [int(a) for a in np.flatnonzero(legal_mask > 0)]
    ranked = sorted(legal_actions, key=lambda a: float(probs[a].item()), reverse=True)
    return ranked.index(int(action)) + 1


def value_after_move_for_mover(model: PolicyValueNet, board: Board, action: int, device: torch.device) -> float:
    if board.grid[action // BOARD_SIZE, action % BOARD_SIZE] != EMPTY:
        return float("nan")

    after = board.clone()
    mover = after.current_player
    result = after.play_flat(action)
    if result.winner == mover:
        return 1.0
    if result.done:
        return 0.0
    _logits, _probs, next_value = model_policy_value(model, after, device)
    return -next_value


def parse_rapfi_eval(raw: str) -> float:
    if not raw:
        return float("nan")
    sign = -1.0 if raw.startswith("-") else 1.0
    text = raw[1:] if raw.startswith(("+", "-")) else raw
    if text.startswith("M"):
        # Keep mate scores comfortably above any centipawn-like numeric eval.
        ply = int(text[1:] or "0")
        return sign * (100000.0 - ply)
    return float(raw)


def board_entries_for_rapfi(board: Board) -> list[str]:
    entries: list[str] = []
    for row in range(board.size):
        for col in range(board.size):
            stone = int(board.grid[row, col])
            if stone == EMPTY:
                continue
            # Gomocup BOARD fields are from the queried engine's perspective:
            # 1 = side to move / own stones, 2 = opponent stones.
            field = 1 if stone == board.current_player else 2
            entries.append(f"{col},{row},{field}")
    return entries


def query_rapfi(command: str, board: Board, timeout_sec: float) -> RapfiResult:
    proc = subprocess.run(
        [command],
        input="\n".join(
            [
                "START 15",
                "INFO rule 0",
                "INFO timeout_turn 1000",
                "INFO timeout_match 1000",
                "INFO max_depth 1",
                "BOARD",
                *board_entries_for_rapfi(board),
                "DONE",
            ]
        )
        + "\n",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=timeout_sec,
        check=False,
    )
    lines = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    move = ""
    eval_raw = ""
    bestline = ""
    for line in lines:
        eval_match = EVAL_RE.search(line)
        if eval_match:
            eval_raw = eval_match.group("eval")
        if "Bestline" in line:
            bestline = line.split("Bestline", maxsplit=1)[1].strip()
        if COORD_RE.match(line):
            move = line
    if not move:
        raise RuntimeError(f"Rapfi did not return a move; tail={lines[-10:]}")
    return RapfiResult(
        move_xy=move,
        eval_raw=eval_raw,
        eval_score=parse_rapfi_eval(eval_raw),
        bestline=bestline,
        raw_tail=lines[-6:],
    )


def query_after_forced_move(command: str, board: Board, action: int, timeout_sec: float) -> RapfiResult | None:
    if board.grid[action // BOARD_SIZE, action % BOARD_SIZE] != EMPTY:
        return None
    after = board.clone()
    result = after.play_flat(action)
    if result.done:
        return None
    return query_rapfi(command, after, timeout_sec)


def is_strong_teacher_preference(original_after: RapfiResult | None, teacher_after: RapfiResult | None, threshold: float) -> bool:
    if original_after is None or teacher_after is None:
        return False
    original = original_after.eval_score
    teacher = teacher_after.eval_score
    if math.isnan(original) or math.isnan(teacher):
        return False
    # After our forced move, Rapfi evaluates from the opponent-to-move
    # perspective. If the opponent sees a mate/numeric advantage after the
    # model move but not after the teacher move, the teacher is strongly better
    # for Candidate D's side.
    if original > 90000 and teacher < 90000:
        return True
    return (original - teacher) >= threshold


def load_failure_games(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a list")
    return data


def build_rows(args: argparse.Namespace) -> list[dict[str, Any]]:
    games = load_failure_games(args.failure_positions_json)
    replayed = replay_decision_boards(args.debug_log)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = load_model(args.checkpoint, device)

    rows: list[dict[str, Any]] = []
    for game in games:
        for decision in game["debug_decisions"]:
            key = (int(game["game_number"]), int(decision["move_count"]))
            replay = replayed.get(key)
            if replay is None:
                raise ValueError(f"missing replayed board for game/move {key}")
            if replay.side_to_move != decision["side_to_move"]:
                raise ValueError(f"side mismatch for {key}: replay={replay.side_to_move} json={decision['side_to_move']}")

            board = make_board(replay.board, side_to_player(replay.side_to_move), replay.last_move_rc)
            logits, probs, value = model_policy_value(model, board, device)
            legal_mask = board.legal_mask()

            model_xy = str(decision["final"])
            model_action = xy_to_action(model_xy)
            teacher = query_rapfi(args.rapfi_command, board, args.timeout_sec)
            teacher_action = xy_to_action(teacher.move_xy)

            model_prob = float(probs[model_action].item()) if legal_mask[model_action] > 0 else float("nan")
            teacher_prob = float(probs[teacher_action].item()) if legal_mask[teacher_action] > 0 else float("nan")
            model_rank = rank_of_action(probs, legal_mask, model_action) if legal_mask[model_action] > 0 else 0
            teacher_rank = rank_of_action(probs, legal_mask, teacher_action) if legal_mask[teacher_action] > 0 else 0
            model_logit = float(logits[model_action].item()) if legal_mask[model_action] > 0 else float("nan")
            teacher_logit = float(logits[teacher_action].item()) if legal_mask[teacher_action] > 0 else float("nan")

            value_original = value_after_move_for_mover(model, board, model_action, device)
            value_teacher = value_after_move_for_mover(model, board, teacher_action, device)
            original_after = query_after_forced_move(args.rapfi_command, board, model_action, args.timeout_sec)
            teacher_after = query_after_forced_move(args.rapfi_command, board, teacher_action, args.timeout_sec)
            strong_teacher = is_strong_teacher_preference(original_after, teacher_after, args.strong_eval_threshold)

            rows.append(
                {
                    "game": int(game["game_number"]),
                    "ply": int(decision["move_count"]),
                    "side": replay.side_to_move,
                    "model_move": model_xy,
                    "teacher_move": teacher.move_xy,
                    "teacher_move_policy_rank": teacher_rank,
                    "model_move_policy_rank": model_rank,
                    "teacher_policy_prob": teacher_prob,
                    "model_policy_prob": model_prob,
                    "policy_probability_gap_teacher_minus_model": teacher_prob - model_prob,
                    "policy_logit_gap_teacher_minus_model": teacher_logit - model_logit,
                    "value_current_position": value,
                    "value_original_move": value_original,
                    "value_teacher_move": value_teacher,
                    "teacher_value_disfavored": value_teacher < value_original,
                    "teacher_top3_policy": teacher_rank <= 3,
                    "teacher_eval_current": teacher.eval_raw,
                    "teacher_bestline_current": teacher.bestline,
                    "rapfi_after_original_eval": "" if original_after is None else original_after.eval_raw,
                    "rapfi_after_original_move": "" if original_after is None else original_after.move_xy,
                    "rapfi_after_original_bestline": "" if original_after is None else original_after.bestline,
                    "rapfi_after_teacher_eval": "" if teacher_after is None else teacher_after.eval_raw,
                    "rapfi_after_teacher_move": "" if teacher_after is None else teacher_after.move_xy,
                    "rapfi_after_teacher_bestline": "" if teacher_after is None else teacher_after.bestline,
                    "strong_teacher_continuation_preference": strong_teacher,
                    "diverges": teacher.move_xy != model_xy,
                    "logged_direct": decision["direct"],
                    "logged_mcts_raw": decision["mcts_raw"],
                    "logged_mcts_safety": decision["mcts_safety"],
                    "logged_value": decision["value"],
                    "loss_reason": game["loss_reason"],
                }
            )

            if args.max_positions and len(rows) >= args.max_positions:
                return rows

    return rows


def fmt_float(value: Any, digits: int = 6) -> str:
    if value is None:
        return ""
    try:
        f = float(value)
    except (TypeError, ValueError):
        return str(value)
    if math.isnan(f):
        return ""
    return f"{f:.{digits}f}"


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "game",
        "ply",
        "side",
        "model_move",
        "teacher_move",
        "teacher_move_policy_rank",
        "model_move_policy_rank",
        "teacher_policy_prob",
        "model_policy_prob",
        "policy_probability_gap_teacher_minus_model",
        "policy_logit_gap_teacher_minus_model",
        "value_current_position",
        "value_original_move",
        "value_teacher_move",
        "teacher_value_disfavored",
        "teacher_top3_policy",
        "teacher_eval_current",
        "teacher_bestline_current",
        "rapfi_after_original_eval",
        "rapfi_after_original_move",
        "rapfi_after_original_bestline",
        "rapfi_after_teacher_eval",
        "rapfi_after_teacher_move",
        "rapfi_after_teacher_bestline",
        "strong_teacher_continuation_preference",
        "diverges",
        "logged_direct",
        "logged_mcts_raw",
        "logged_mcts_safety",
        "logged_value",
        "loss_reason",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    divergences = [row for row in rows if row["diverges"]]
    strong = [row for row in divergences if row["strong_teacher_continuation_preference"]]
    top3 = [row for row in divergences if row["teacher_top3_policy"]]
    value_disfavored = [row for row in divergences if row["teacher_value_disfavored"]]
    first_major: dict[int, dict[str, Any]] = {}
    for row in sorted(strong, key=lambda r: (r["game"], r["ply"])):
        first_major.setdefault(int(row["game"]), row)
    return {
        "positions": len(rows),
        "divergences": len(divergences),
        "strong_divergences": len(strong),
        "teacher_top3_among_divergences": len(top3),
        "teacher_value_disfavored_among_divergences": len(value_disfavored),
        "first_major": first_major,
    }


def write_markdown(path: Path, rows: list[dict[str, Any]], args: argparse.Namespace) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    summary = summarize(rows)
    divergences = [row for row in rows if row["diverges"]]
    strong = [row for row in divergences if row["strong_teacher_continuation_preference"]]

    lines: list[str] = [
        "# Candidate D teacher disagreement census",
        "",
        "## Scope",
        "",
        "This is a read-only diagnostic census over Candidate D mcts32 Rapfi losses.",
        "It does not train, save, export, promote, or alter smoke/Rapfi settings.",
        "",
        "Inputs:",
        "",
        f"- failure positions: `{args.failure_positions_json}`",
        f"- replay log: `{args.debug_log}`",
        f"- checkpoint: `{args.checkpoint}`",
        f"- Rapfi command: `{args.rapfi_command}`",
        "",
        "Method:",
        "",
        "- Replay the raw smoke protocol log to recover each Candidate D decision board and last-move plane.",
        "- Query Rapfi from the same pre-decision board using `START 15`, `INFO rule 0`, `INFO timeout_turn 1000`, `INFO timeout_match 1000`, `INFO max_depth 1`, and `BOARD ... DONE`.",
        "- Evaluate Candidate D policy rank/probability for the model move and teacher move.",
        "- Force each move once, then evaluate Candidate D value from the mover perspective.",
        "- Query Rapfi after each forced move and mark strong teacher continuation preference when Candidate D's move gives the opponent a mate while the teacher move does not, or when the opponent eval drops by at least the configured threshold.",
        "",
        "## Summary",
        "",
        f"- positions evaluated: {summary['positions']}",
        f"- teacher/model divergences: {summary['divergences']}",
        f"- strong teacher continuation divergences: {summary['strong_divergences']}",
        f"- teacher top-3 policy among divergences: {summary['teacher_top3_among_divergences']}/{max(summary['divergences'], 1)}",
        f"- teacher value-disfavored among divergences: {summary['teacher_value_disfavored_among_divergences']}/{max(summary['divergences'], 1)}",
        "",
        "## Implementation Plan",
        "",
        "1. Replay the Candidate D mcts32 smoke loss log instead of using only the curated five-position ledger, so both Rapfi losses are covered.",
        "2. Recover the exact model-input last-move plane from consecutive board diagrams.",
        "3. Query Rapfi as a same-position teacher for each Candidate D decision.",
        "4. Score the teacher move in Candidate D policy space and compare one-ply Candidate D value after the model move versus after the teacher move.",
        "5. Query Rapfi after each forced first move to identify divergences where the teacher continuation is materially better than Candidate D's continuation.",
        "",
        "One important correction from this active census: game2 move17's same-position Rapfi teacher query returns `9,10` with bestline `J11 K12 H10 I11`. Earlier Candidate E notes used `9,9` as a teacher target, but in this log `9,9` is the Rapfi continuation reply after Candidate D's original move, not the same-position teacher move.",
        "",
        "## First Major Divergences",
        "",
        "| game | ply | side | model_move | teacher_move | teacher_rank | prob_gap | value_original | value_teacher | original_after | teacher_after | diagnosis |",
        "| ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | --- | --- | --- |",
    ]

    if summary["first_major"]:
        for game in sorted(summary["first_major"]):
            row = summary["first_major"][game]
            diagnosis = "teacher top-3 but value-disfavored" if row["teacher_top3_policy"] and row["teacher_value_disfavored"] else (
                "teacher policy-distant and value-disfavored" if row["teacher_value_disfavored"] else "teacher policy/value mixed"
            )
            lines.append(
                "| "
                + " | ".join(
                    [
                        str(row["game"]),
                        str(row["ply"]),
                        row["side"],
                        row["model_move"],
                        row["teacher_move"],
                        str(row["teacher_move_policy_rank"]),
                        fmt_float(row["policy_probability_gap_teacher_minus_model"]),
                        fmt_float(row["value_original_move"]),
                        fmt_float(row["value_teacher_move"]),
                        f"{row['rapfi_after_original_eval']} {row['rapfi_after_original_bestline']}".strip(),
                        f"{row['rapfi_after_teacher_eval']} {row['rapfi_after_teacher_bestline']}".strip(),
                        diagnosis,
                    ]
                )
                + " |"
            )
    else:
        lines.append("|  |  |  |  |  |  |  |  |  |  |  | no strong divergences found |")

    lines.extend(
        [
            "",
            "## Strong Teacher Divergence Rows",
            "",
            "| game | ply | side | model | teacher | teacher_rank | teacher_prob | model_prob | value_original | value_teacher | teacher_eval | after_model | after_teacher |",
            "| ---: | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |",
        ]
    )
    for row in sorted(strong, key=lambda r: (r["game"], r["ply"])):
        lines.append(
            "| "
            + " | ".join(
                [
                    str(row["game"]),
                    str(row["ply"]),
                    row["side"],
                    row["model_move"],
                    row["teacher_move"],
                    str(row["teacher_move_policy_rank"]),
                    fmt_float(row["teacher_policy_prob"], 8),
                    fmt_float(row["model_policy_prob"], 8),
                    fmt_float(row["value_original_move"]),
                    fmt_float(row["value_teacher_move"]),
                    f"{row['teacher_eval_current']} {row['teacher_bestline_current']}".strip(),
                    f"{row['rapfi_after_original_eval']} {row['rapfi_after_original_bestline']}".strip(),
                    f"{row['rapfi_after_teacher_eval']} {row['rapfi_after_teacher_bestline']}".strip(),
                ]
            )
            + " |"
        )

    top3_strong = [row for row in strong if row["teacher_top3_policy"]]
    value_disfavored_strong = [row for row in strong if row["teacher_value_disfavored"]]
    policy_distant_strong = [row for row in strong if not row["teacher_top3_policy"]]

    if len(top3_strong) >= len(policy_distant_strong):
        dominant = "A. Value/search is suppressing already-known policy options."
    else:
        dominant = "B. Missing policy knowledge requiring broader teacher distillation."

    lines.extend(
        [
            "",
            "## Conclusions",
            "",
            f"- Strong divergences with teacher already top-3: {len(top3_strong)}/{max(len(strong), 1)}.",
            f"- Strong divergences where Candidate D value prefers the original move: {len(value_disfavored_strong)}/{max(len(strong), 1)}.",
            f"- Strong divergences where the teacher is outside top-3: {len(policy_distant_strong)}/{max(len(strong), 1)}.",
            f"- Dominant observed mode: {dominant}",
            "",
            "Recommendation for the next training experiment: do not run another single-position margin repair. The next candidate should be a small teacher-distillation dataset over strong same-position Rapfi divergences and nearby non-divergent anchors, with value/continuation labels added only after the policy target is no longer far outside Candidate D's top policy mass. The first seed targets from this census are game1 ply22 `4,8` and game2 ply17 `9,10`, with Candidate D retention anchors around game2 move15 and the already teacher-aligned/recovered later blocks.",
            "",
            f"Full row data: `{args.out_csv}`",
            "",
        ]
    )

    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    args = parse_args()
    rows = build_rows(args)
    write_csv(args.out_csv, rows)
    write_markdown(args.out_md, rows, args)
    print(f"positions: {len(rows)}")
    print(f"wrote {args.out_csv}")
    print(f"wrote {args.out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
