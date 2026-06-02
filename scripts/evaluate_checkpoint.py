from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import torch

from gomoku_agent.board import Board
from gomoku_agent.checkpoint import load_compatible_checkpoint
from gomoku_agent.model import PolicyValueNet, masked_policy


def parse_args():
    p = argparse.ArgumentParser(description="Evaluate a Gomoku checkpoint against greedy/random/checkpoint opponent.")
    p.add_argument("--checkpoint", type=Path, required=True)
    p.add_argument("--opponent", choices=["greedy", "random", "checkpoint"], required=True)
    p.add_argument("--opponent-checkpoint", type=Path, default=None)

    p.add_argument("--board-size", type=int, default=15)
    p.add_argument("--win-length", type=int, default=5)
    p.add_argument("--channels", type=int, default=64)
    p.add_argument("--blocks", type=int, default=4)

    p.add_argument("--games", type=int, default=20)
    p.add_argument("--seed", type=int, default=123)
    p.add_argument("--sample", action="store_true")
    return p.parse_args()


def center_bonus(board: Board, action: int) -> float:
    row, col = divmod(int(action), board.size)
    center = (board.size - 1) / 2.0
    dist = abs(row - center) + abs(col - center)
    return -0.01 * dist


def line_info_after_move(board: Board, action: int, player: int) -> tuple[int, int]:
    row, col = divmod(int(action), board.size)
    if board.grid[row, col] != 0:
        return -999, 0

    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
    best_count = 0
    best_open_ends = 0

    board.grid[row, col] = player
    try:
        for dr, dc in directions:
            count = 1
            open_ends = 0

            r, c = row + dr, col + dc
            while 0 <= r < board.size and 0 <= c < board.size and board.grid[r, c] == player:
                count += 1
                r += dr
                c += dc
            if 0 <= r < board.size and 0 <= c < board.size and board.grid[r, c] == 0:
                open_ends += 1

            r, c = row - dr, col - dc
            while 0 <= r < board.size and 0 <= c < board.size and board.grid[r, c] == player:
                count += 1
                r -= dr
                c -= dc
            if 0 <= r < board.size and 0 <= c < board.size and board.grid[r, c] == 0:
                open_ends += 1

            if count > best_count or (count == best_count and open_ends > best_open_ends):
                best_count = count
                best_open_ends = open_ends
    finally:
        board.grid[row, col] = 0

    return best_count, best_open_ends


def strongest_extension_action(board: Board, player: int) -> int:
    legal = [int(a) for a in board.legal_moves()]
    best_action = legal[0]
    best_score = -1e18

    for action in legal:
        count, open_ends = line_info_after_move(board, action, player)
        score = 100.0 * count + 10.0 * open_ends + center_bonus(board, action)
        if score > best_score:
            best_score = score
            best_action = action

    return int(best_action)


def greedy_action(board: Board) -> int:
    player = board.current_player
    opponent = -player

    wins = board.immediate_winning_moves(player)
    if wins:
        return int(wins[0])

    blocks = board.immediate_winning_moves(opponent)
    if blocks:
        return int(blocks[0])

    return strongest_extension_action(board, player)


def random_action(board: Board, rng: np.random.Generator) -> int:
    legal = board.legal_moves()
    return int(rng.choice(legal))


@torch.no_grad()
def model_action(
    model: PolicyValueNet,
    board: Board,
    device: torch.device,
    sample: bool,
    rng: np.random.Generator,
) -> int:
    state = torch.tensor(board.encode()[None, ...], dtype=torch.float32, device=device)
    legal = torch.tensor(board.legal_mask()[None, ...], dtype=torch.float32, device=device)

    logits, _ = model(state)
    probs = masked_policy(logits, legal, temperature=1.0)[0].cpu().numpy()

    if sample:
        return int(rng.choice(np.arange(board.size * board.size), p=probs))

    return int(np.argmax(probs))


def load_model(path: Path, args, device: torch.device) -> PolicyValueNet:
    model = PolicyValueNet(args.board_size, args.channels, args.blocks).to(device)
    load_compatible_checkpoint(
        model,
        path,
        device,
        board_size=args.board_size,
        channels=args.channels,
        blocks=args.blocks,
    )
    model.eval()
    return model


def play_game(
    model_a: PolicyValueNet,
    opponent_type: str,
    args,
    device: torch.device,
    rng: np.random.Generator,
    model_a_player: int,
    model_b: PolicyValueNet | None = None,
) -> tuple[int | None, int]:
    board = Board(size=args.board_size, win_length=args.win_length)

    while True:
        current = board.current_player

        if current == model_a_player:
            action = model_action(model_a, board, device, sample=args.sample, rng=rng)
        else:
            if opponent_type == "greedy":
                action = greedy_action(board)
            elif opponent_type == "random":
                action = random_action(board, rng)
            elif opponent_type == "checkpoint":
                assert model_b is not None
                action = model_action(model_b, board, device, sample=args.sample, rng=rng)
            else:
                raise ValueError(opponent_type)

        result = board.play_flat(action)

        if result.done:
            return result.winner, board.move_count


def main():
    args = parse_args()

    rng = np.random.default_rng(args.seed)
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"device={device}", flush=True)

    model_a = load_model(args.checkpoint, args, device)

    model_b = None
    if args.opponent == "checkpoint":
        if args.opponent_checkpoint is None:
            raise ValueError("--opponent-checkpoint is required when --opponent checkpoint")
        model_b = load_model(args.opponent_checkpoint, args, device)

    wins = 0
    losses = 0
    draws = 0
    moves = []

    for g in range(args.games):
        model_a_player = 1 if g % 2 == 0 else -1

        winner, move_count = play_game(
            model_a=model_a,
            opponent_type=args.opponent,
            args=args,
            device=device,
            rng=rng,
            model_a_player=model_a_player,
            model_b=model_b,
        )

        moves.append(move_count)

        if winner is None:
            draws += 1
            outcome = "draw"
        elif winner == model_a_player:
            wins += 1
            outcome = "win"
        else:
            losses += 1
            outcome = "loss"

        print(
            f"game {g + 1}/{args.games}: {outcome}, moves={move_count}, "
            f"model_player={'black' if model_a_player == 1 else 'white'}",
            flush=True,
        )

    print(
        f"summary: checkpoint={args.checkpoint}, opponent={args.opponent}, "
        f"wins={wins}, losses={losses}, draws={draws}, "
        f"avg_moves={np.mean(moves):.2f}",
        flush=True,
    )


if __name__ == "__main__":
    main()
