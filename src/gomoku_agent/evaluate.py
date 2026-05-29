from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import torch

from .board import BLACK, WHITE, Board
from .checkpoint import load_compatible_checkpoint
from .mcts import MCTSConfig, run_mcts
from .model import PolicyValueNet, masked_policy
from .search_safety import filter_unavoidable_terminal_replies, forced_terminal_policy


PLAYER_NAMES = {
    BLACK: "black",
    WHITE: "white",
    None: "draw",
}


@dataclass(frozen=True)
class GameResult:
    game_index: int
    neural_player: int
    first_player: int
    winner: int | None
    moves: int

    @property
    def outcome(self) -> str:
        if self.winner is None:
            return "draw"
        if self.winner == self.neural_player:
            return "win"
        return "loss"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run automated 9x9 Gomoku evaluation matches.")
    parser.add_argument("--checkpoint", type=Path, default=Path("checkpoints/9x9_tactical_v2.pt"))
    parser.add_argument("--board-size", type=int, default=9)
    parser.add_argument("--win-length", type=int, default=5)
    parser.add_argument("--channels", type=int, default=64)
    parser.add_argument("--blocks", type=int, default=4)
    parser.add_argument("--games", type=int, default=20)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--agent", choices=["neural_mcts", "policy_only"], default="neural_mcts")
    parser.add_argument("--opponent", choices=["random", "greedy_win_block"], default="greedy_win_block")
    parser.add_argument("--mcts-sims", type=int, default=256)
    parser.add_argument("--c-puct", type=float, default=1.5)
    parser.add_argument("--json-log", type=Path, default=None, help="Optional path for a JSON evaluation log.")
    return parser.parse_args()


def choose_random_move(board: Board, rng: np.random.Generator) -> int:
    legal = board.legal_moves()
    return int(rng.choice(legal))


def choose_greedy_win_block_move(board: Board, rng: np.random.Generator) -> int:
    own_wins = board.immediate_winning_moves(board.current_player)
    if own_wins:
        return int(own_wins[0])

    opponent_wins = board.immediate_winning_moves(-board.current_player)
    if opponent_wins:
        return int(opponent_wins[0])

    legal = board.legal_moves()
    center = (board.size - 1) / 2.0
    distances = np.array(
        [
            (divmod(int(action), board.size)[0] - center) ** 2
            + (divmod(int(action), board.size)[1] - center) ** 2
            for action in legal
        ],
        dtype=np.float32,
    )
    best_distance = float(distances.min())
    center_near = legal[np.flatnonzero(distances == best_distance)]
    return int(rng.choice(center_near))


@torch.no_grad()
def choose_policy_only_move(model: PolicyValueNet, board: Board, device: torch.device) -> int:
    forced = forced_terminal_policy(board, temperature=0.0)
    if forced is not None:
        action, _ = forced
        return int(action)

    state = torch.tensor(board.encode()[None, ...], dtype=torch.float32, device=device)
    legal = torch.tensor(board.legal_mask()[None, ...], dtype=torch.float32, device=device)
    logits, _ = model(state)
    probs = masked_policy(logits, legal, temperature=1.0)[0].cpu().numpy()
    filtered = filter_unavoidable_terminal_replies(board, probs)
    if filtered.sum() > 0:
        probs = filtered / filtered.sum()
    return int(np.argmax(probs))


def choose_neural_mcts_move(
    model: PolicyValueNet,
    board: Board,
    device: torch.device,
    mcts_sims: int,
    c_puct: float,
) -> int:
    config = MCTSConfig(
        simulations=mcts_sims,
        c_puct=c_puct,
        temperature=0.0,
        avoid_immediate_loss=True,
    )
    action, probs = run_mcts(model, board, device, config, add_noise=False)
    filtered = filter_unavoidable_terminal_replies(board, probs)
    if filtered.sum() > 0:
        return int(np.argmax(filtered))
    return int(action)


def play_game(
    game_index: int,
    model: PolicyValueNet,
    device: torch.device,
    board_size: int,
    win_length: int,
    neural_player: int,
    agent: str,
    opponent: str,
    mcts_sims: int,
    c_puct: float,
    rng: np.random.Generator,
) -> GameResult:
    board = Board(size=board_size, win_length=win_length)

    while True:
        if board.current_player == neural_player:
            if agent == "neural_mcts":
                action = choose_neural_mcts_move(model, board, device, mcts_sims, c_puct)
            elif agent == "policy_only":
                action = choose_policy_only_move(model, board, device)
            else:
                raise ValueError(f"unknown neural agent: {agent}")
        elif opponent == "random":
            action = choose_random_move(board, rng)
        elif opponent == "greedy_win_block":
            action = choose_greedy_win_block_move(board, rng)
        else:
            raise ValueError(f"unknown opponent: {opponent}")

        result = board.play_flat(action)
        if result.done:
            return GameResult(
                game_index=game_index,
                neural_player=neural_player,
                first_player=BLACK,
                winner=result.winner,
                moves=board.move_count,
            )


def summarize(results: list[GameResult]) -> dict:
    wins = sum(result.outcome == "win" for result in results)
    draws = sum(result.outcome == "draw" for result in results)
    losses = sum(result.outcome == "loss" for result in results)
    avg_moves = float(np.mean([result.moves for result in results])) if results else 0.0

    by_seat = {}
    for neural_player in (BLACK, WHITE):
        seat_results = [result for result in results if result.neural_player == neural_player]
        by_seat[PLAYER_NAMES[neural_player]] = {
            "games": len(seat_results),
            "wins": sum(result.outcome == "win" for result in seat_results),
            "draws": sum(result.outcome == "draw" for result in seat_results),
            "losses": sum(result.outcome == "loss" for result in seat_results),
        }

    return {
        "games": len(results),
        "wins": wins,
        "draws": draws,
        "losses": losses,
        "win_rate": wins / len(results) if results else 0.0,
        "average_moves": avg_moves,
        "by_neural_player": by_seat,
    }


def main() -> None:
    args = parse_args()
    if args.games <= 0:
        raise ValueError("--games must be positive")

    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    rng = np.random.default_rng(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

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
        raise FileNotFoundError(f"could not load compatible checkpoint: {args.checkpoint}")
    model.eval()

    results: list[GameResult] = []
    for game_idx in range(args.games):
        neural_player = BLACK if game_idx % 2 == 0 else WHITE
        result = play_game(
            game_index=game_idx + 1,
            model=model,
            device=device,
            board_size=args.board_size,
            win_length=args.win_length,
            neural_player=neural_player,
            agent=args.agent,
            opponent=args.opponent,
            mcts_sims=args.mcts_sims,
            c_puct=args.c_puct,
            rng=rng,
        )
        results.append(result)
        print(
            f"game={result.game_index} "
            f"first_player={PLAYER_NAMES[result.first_player]} "
            f"neural_player={PLAYER_NAMES[result.neural_player]} "
            f"winner={PLAYER_NAMES[result.winner]} "
            f"outcome={result.outcome} "
            f"moves={result.moves}",
            flush=True,
        )

    summary = summarize(results)
    print(
        "summary: "
        f"wins={summary['wins']} draws={summary['draws']} losses={summary['losses']} "
        f"win_rate={summary['win_rate']:.3f} "
        f"average_moves={summary['average_moves']:.1f}",
        flush=True,
    )
    for player_name, seat_summary in summary["by_neural_player"].items():
        print(
            f"neural_as_{player_name}: "
            f"games={seat_summary['games']} wins={seat_summary['wins']} "
            f"draws={seat_summary['draws']} losses={seat_summary['losses']}",
            flush=True,
        )

    if args.json_log is not None:
        args.json_log.parent.mkdir(parents=True, exist_ok=True)
        args.json_log.write_text(
            json.dumps(
                {
                    "config": {
                        "checkpoint": str(args.checkpoint),
                        "board_size": args.board_size,
                        "win_length": args.win_length,
                        "agent": args.agent,
                        "opponent": args.opponent,
                        "mcts_sims": args.mcts_sims,
                        "seed": args.seed,
                    },
                    "games": [asdict(result) | {"outcome": result.outcome} for result in results],
                    "summary": summary,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        print(f"wrote {args.json_log}", flush=True)


if __name__ == "__main__":
    main()
