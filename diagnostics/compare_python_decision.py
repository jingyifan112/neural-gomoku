from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch

from gomoku_agent.board import BLACK, WHITE, Board
from gomoku_agent.mcts import MCTSConfig, run_mcts
from gomoku_agent.model import PolicyValueNet, masked_policy
from gomoku_agent.search_safety import filter_unavoidable_terminal_replies, forced_terminal_policy


ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Report Python decision stages for one diagnostic Gomoku position.")
    parser.add_argument("--position", type=Path, default=ROOT / "diagnostics" / "positions" / "human_play_cross_center_reference.json")
    parser.add_argument("--checkpoint", type=Path, default=ROOT / "checkpoints" / "9x9.pt")
    parser.add_argument("--mcts-sims", type=int, default=256)
    parser.add_argument("--c-puct", type=float, default=1.5)
    return parser.parse_args()


def player_from_text(text: str) -> int:
    if text == "X":
        return BLACK
    if text == "O":
        return WHITE
    raise ValueError(f"unknown player {text!r}")


def move_text(action: int | None, board_size: int) -> str:
    if action is None or action < 0:
        return "none"
    row, col = divmod(int(action), board_size)
    return f"({row},{col})"


def load_position(path: Path) -> tuple[dict, Board]:
    data = json.loads(path.read_text(encoding="utf-8"))
    board = Board(size=int(data["board_size"]), win_length=int(data["win_length"]))
    board.current_player = player_from_text(data["current_player"])
    board.move_count = 0

    for row, line in enumerate(data["board"]):
        if len(line) != board.size:
            raise ValueError(f"row {row} has length {len(line)}, expected {board.size}")
        for col, ch in enumerate(line):
            if ch == ".":
                continue
            board.grid[row, col] = player_from_text(ch)
            board.move_count += 1

    last_move = data.get("last_move")
    board.last_move = tuple(last_move) if last_move is not None else None
    return data, board


def load_model(checkpoint_path: Path, board_size: int) -> PolicyValueNet:
    payload = torch.load(checkpoint_path, map_location="cpu")
    channels = int(payload.get("channels", 64))
    blocks = int(payload.get("blocks", 4))
    model = PolicyValueNet(board_size=board_size, channels=channels, blocks=blocks)
    model.load_state_dict(payload["model"])
    model.eval()
    return model


@torch.no_grad()
def direct_policy(model: PolicyValueNet, board: Board) -> tuple[int, float, np.ndarray]:
    state = torch.tensor(board.encode()[None, ...], dtype=torch.float32)
    legal = torch.tensor(board.legal_mask()[None, ...], dtype=torch.float32)
    logits, value = model(state)
    probs = masked_policy(logits, legal)[0].cpu().numpy().astype(np.float32)
    return int(np.argmax(probs)), float(value.item()), probs


def main() -> None:
    args = parse_args()
    data, board = load_position(args.position)
    model = load_model(args.checkpoint, board.size)

    direct_move, value, _ = direct_policy(model, board)
    raw_move: int | None = None
    safety_move: int | None = None
    final_move: int | None = None

    if args.mcts_sims > 0:
        raw_config = MCTSConfig(
            simulations=args.mcts_sims,
            c_puct=args.c_puct,
            temperature=0.0,
            avoid_immediate_loss=False,
        )
        raw_move, _ = run_mcts(model, board, torch.device("cpu"), raw_config, add_noise=False)

        forced = forced_terminal_policy(board, temperature=0.0)
        if forced is not None:
            safety_move, safety_probs = forced
        else:
            safe_config = MCTSConfig(
                simulations=args.mcts_sims,
                c_puct=args.c_puct,
                temperature=0.0,
                avoid_immediate_loss=True,
            )
            safety_move, safety_probs = run_mcts(model, board, torch.device("cpu"), safe_config, add_noise=False)
        filtered = filter_unavoidable_terminal_replies(board, safety_probs)
        if filtered.sum() > 0:
            final_move = int(np.argmax(filtered))
        else:
            final_move = safety_move
    else:
        final_move = direct_move

    print(f"case_name={data['name']}")
    print(f"board_size={board.size}")
    print(f"current_player={data['current_player']}")
    print(f"legal_move_count={len(board.legal_moves())}")
    print(f"direct_policy_top={move_text(direct_move, board.size)}")
    print(f"value={value:.6f}")
    print(f"raw_mcts_selected={move_text(raw_move, board.size)}")
    print(f"safety_adjusted_selected={move_text(safety_move, board.size)}")
    print(f"final_selected={move_text(final_move, board.size)}")
    print(f"checkpoint_path={args.checkpoint}")
    print(f"mcts_sims={args.mcts_sims}")


if __name__ == "__main__":
    main()
