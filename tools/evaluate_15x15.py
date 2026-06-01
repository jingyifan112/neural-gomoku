from __future__ import annotations

import argparse
import random
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch

from gomoku_agent.board import BLACK, Board
from gomoku_agent.checkpoint import load_compatible_checkpoint
from gomoku_agent.mcts import MCTSConfig, run_mcts
from gomoku_agent.model import PolicyValueNet
from gomoku_agent.self_play import choose_action


@dataclass
class EvalResult:
    wins: int = 0
    draws: int = 0
    losses: int = 0
    total_moves: int = 0

    def record(self, outcome: int, moves: int) -> None:
        if outcome > 0:
            self.wins += 1
        elif outcome < 0:
            self.losses += 1
        else:
            self.draws += 1
        self.total_moves += moves

    @property
    def avg_moves(self) -> float:
        games = self.wins + self.draws + self.losses
        return self.total_moves / games if games else 0.0


class RandomAgent:
    def __init__(self, rng: random.Random):
        self.rng = rng

    def select(self, board: Board) -> int:
        legal = list(map(int, board.legal_moves()))
        return self.rng.choice(legal)


class GreedyWinBlockAgent:
    """Simple tactical baseline: win now, else block opponent win, else play near center."""

    def select(self, board: Board) -> int:
        own_wins = board.immediate_winning_moves(board.current_player)
        if own_wins:
            return self._closest_to_center(board, own_wins)

        opponent_wins = board.immediate_winning_moves(-board.current_player)
        if opponent_wins:
            return self._closest_to_center(board, opponent_wins)

        return self._closest_to_center(board, list(map(int, board.legal_moves())))

    @staticmethod
    def _closest_to_center(board: Board, moves: list[int]) -> int:
        center = (board.size - 1) / 2.0

        def score(action: int) -> tuple[float, int]:
            row, col = divmod(action, board.size)
            dist = (row - center) ** 2 + (col - center) ** 2
            return dist, action

        return min(moves, key=score)


class CheckpointAgent:
    def __init__(
        self,
        checkpoint: Path,
        board_size: int,
        win_length: int,
        channels: int,
        blocks: int,
        mcts_sims: int,
        use_safety: bool,
        device: torch.device,
    ):
        self.model = PolicyValueNet(board_size=board_size, channels=channels, blocks=blocks).to(device)
        loaded = load_compatible_checkpoint(
            self.model,
            checkpoint,
            device,
            board_size=board_size,
            channels=channels,
            blocks=blocks,
        )
        if not loaded:
            raise RuntimeError(f"failed to load checkpoint: {checkpoint}")
        self.model.eval()
        self.device = device
        self.mcts_sims = mcts_sims
        self.use_safety = use_safety

    @torch.no_grad()
    def select(self, board: Board) -> int:
        if self.mcts_sims > 0:
            config = MCTSConfig(
                simulations=self.mcts_sims,
                c_puct=1.5,
                temperature=0.0,
                avoid_immediate_loss=self.use_safety,
            )
            action, _ = run_mcts(self.model, board, self.device, config, add_noise=False)
            return int(action)

        action, _ = choose_action(
            self.model,
            board,
            self.device,
            temperature=1.0,
            sample=False,
        )
        return int(action)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate a 15x15 checkpoint against simple baselines.")
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--opponent", choices=["random", "greedy_win_block", "checkpoint"], required=True)
    parser.add_argument("--opponent-checkpoint", type=Path, default=None)
    parser.add_argument("--board-size", type=int, default=15)
    parser.add_argument("--win-length", type=int, default=5)
    parser.add_argument("--channels", type=int, default=64)
    parser.add_argument("--blocks", type=int, default=4)
    parser.add_argument("--games", type=int, default=10)
    parser.add_argument("--mcts-sims", type=int, default=8)
    parser.add_argument("--opponent-mcts-sims", type=int, default=0)
    parser.add_argument("--use-safety", action="store_true")
    parser.add_argument("--seed", type=int, default=1515)
    return parser.parse_args()


def make_opponent(args: argparse.Namespace, rng: random.Random, device: torch.device):
    if args.opponent == "random":
        return RandomAgent(rng)
    if args.opponent == "greedy_win_block":
        return GreedyWinBlockAgent()
    if args.opponent == "checkpoint":
        if args.opponent_checkpoint is None:
            raise ValueError("--opponent-checkpoint is required when --opponent checkpoint")
        return CheckpointAgent(
            checkpoint=args.opponent_checkpoint,
            board_size=args.board_size,
            win_length=args.win_length,
            channels=args.channels,
            blocks=args.blocks,
            mcts_sims=args.opponent_mcts_sims,
            use_safety=args.use_safety,
            device=device,
        )
    raise ValueError(args.opponent)


def play_one_game(board_size: int, win_length: int, black_agent, white_agent) -> tuple[int | None, int]:
    board = Board(size=board_size, win_length=win_length)

    while True:
        agent = black_agent if board.current_player == BLACK else white_agent
        action = int(agent.select(board))
        result = board.play_flat(action)
        if result.done:
            return result.winner, board.move_count


def main() -> None:
    args = parse_args()

    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)

    rng = random.Random(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"device: {device}")

    eval_agent = CheckpointAgent(
        checkpoint=args.checkpoint,
        board_size=args.board_size,
        win_length=args.win_length,
        channels=args.channels,
        blocks=args.blocks,
        mcts_sims=args.mcts_sims,
        use_safety=args.use_safety,
        device=device,
    )
    opponent_agent = make_opponent(args, rng, device)

    result = EvalResult()

    for game_idx in range(args.games):
        eval_is_black = game_idx % 2 == 0
        black_agent = eval_agent if eval_is_black else opponent_agent
        white_agent = opponent_agent if eval_is_black else eval_agent

        winner, moves = play_one_game(args.board_size, args.win_length, black_agent, white_agent)

        if winner is None:
            outcome = 0
        elif eval_is_black and winner == BLACK:
            outcome = 1
        elif (not eval_is_black) and winner == -BLACK:
            outcome = 1
        else:
            outcome = -1

        result.record(outcome, moves)

        print(
            f"game {game_idx + 1}/{args.games}: "
            f"eval_color={'black' if eval_is_black else 'white'} "
            f"winner={'draw' if winner is None else ('black' if winner == BLACK else 'white')} "
            f"moves={moves} "
            f"score_so_far={result.wins}-{result.draws}-{result.losses}",
            flush=True,
        )

    print()
    print("summary")
    print(f"checkpoint: {args.checkpoint}")
    print(f"opponent: {args.opponent}")
    if args.opponent_checkpoint:
        print(f"opponent_checkpoint: {args.opponent_checkpoint}")
    print(f"board_size: {args.board_size}")
    print(f"mcts_sims: {args.mcts_sims}")
    print(f"use_safety: {args.use_safety}")
    print(f"score: {result.wins}W / {result.draws}D / {result.losses}L")
    print(f"avg_moves: {result.avg_moves:.2f}")


if __name__ == "__main__":
    main()
