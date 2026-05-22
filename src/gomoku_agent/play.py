from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import torch

from .board import BLACK, Board
from .checkpoint import load_compatible_checkpoint
from .mcts import MCTSConfig, run_mcts
from .model import PolicyValueNet
from .search_safety import filter_unavoidable_terminal_replies, forced_terminal_policy
from .self_play import choose_action


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Play Gomoku against the neural model.")
    parser.add_argument("--checkpoint", type=Path, default=Path("checkpoints/latest.pt"))
    parser.add_argument("--board-size", type=int, default=15)
    parser.add_argument("--win-length", type=int, default=5)
    parser.add_argument("--channels", type=int, default=64)
    parser.add_argument("--blocks", type=int, default=4)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--mcts-sims", type=int, default=128)
    parser.add_argument("--c-puct", type=float, default=1.5)
    parser.add_argument("--allow-immediate-loss", action="store_true")
    parser.add_argument("--debug-safety", action="store_true")
    parser.add_argument("--sample", action="store_true", help="sample moves instead of choosing the highest-probability legal move")
    parser.add_argument("--human", choices=["black", "white"], default="black")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    board = Board(args.board_size, args.win_length)
    model = PolicyValueNet(args.board_size, args.channels, args.blocks).to(device)

    loaded = load_compatible_checkpoint(
        model,
        args.checkpoint,
        device,
        board_size=args.board_size,
        channels=args.channels,
        blocks=args.blocks,
    )
    if not loaded:
        print("warning: checkpoint not found; playing against an untrained network")

    model.eval()
    human_player = BLACK if args.human == "black" else -BLACK

    while True:
        print()
        print(board.render())
        if board.current_player == human_player:
            raw = input("your move row col> ").strip()
            try:
                row_text, col_text = raw.split()
                result = board.play(int(row_text), int(col_text))
            except Exception as exc:
                print(f"invalid move: {exc}")
                continue
        else:
            if args.debug_safety:
                opponent_wins = [divmod(action, board.size) for action in board.immediate_winning_moves(-board.current_player)]
                own_wins = [divmod(action, board.size) for action in board.immediate_winning_moves(board.current_player)]
                print(f"debug: model immediate wins={own_wins} opponent immediate wins={opponent_wins}")
            forced = None
            if not args.allow_immediate_loss:
                forced = forced_terminal_policy(board, args.temperature)
            if forced is not None:
                action, probs = forced
                if args.debug_safety:
                    row, col = divmod(action, board.size)
                    print(f"debug: forced terminal move=({row}, {col})")
            elif args.mcts_sims > 0:
                config = MCTSConfig(
                    simulations=args.mcts_sims,
                    c_puct=args.c_puct,
                    temperature=args.temperature,
                    avoid_immediate_loss=not args.allow_immediate_loss,
                )
                action, probs = run_mcts(model, board, device, config, add_noise=False)
            else:
                action, probs = choose_action(model, board, device, temperature=args.temperature, sample=args.sample)
            if not args.allow_immediate_loss:
                filtered = filter_unavoidable_terminal_replies(board, probs)
                if filtered.sum() > 0:
                    probs = filtered / filtered.sum()
                    action = int(np.argmax(probs))
            row, col = divmod(action, board.size)
            print(f"model plays: {row} {col} p={probs[action]:.3f}")
            result = board.play_flat(action)

        if result.done:
            print()
            print(board.render())
            if result.winner is None:
                print("draw")
            elif result.winner == human_player:
                print("you win")
            else:
                print("model wins")
            return


if __name__ == "__main__":
    main()
