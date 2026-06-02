from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import torch
from torch.nn import functional as F
from torch.utils.data import DataLoader, TensorDataset

from gomoku_agent.board import Board
from gomoku_agent.checkpoint import load_compatible_checkpoint
from gomoku_agent.model import PolicyValueNet, masked_policy
from gomoku_agent.self_play import GameSample


def parse_args():
    p = argparse.ArgumentParser(description="v10 greedy sparring + tactical teacher training for 15x15 Gomoku.")
    p.add_argument("--init-checkpoint", type=Path, required=True)
    p.add_argument("--out-checkpoint", type=Path, required=True)

    p.add_argument("--board-size", type=int, default=15)
    p.add_argument("--win-length", type=int, default=5)
    p.add_argument("--channels", type=int, default=64)
    p.add_argument("--blocks", type=int, default=4)

    p.add_argument("--drill-samples", type=int, default=4000)
    p.add_argument("--teacher-games", type=int, default=120)
    p.add_argument("--sparring-games", type=int, default=80)

    p.add_argument("--pretrain-epochs", type=int, default=4)
    p.add_argument("--sparring-epochs", type=int, default=2)

    p.add_argument("--batch-size", type=int, default=64)
    p.add_argument("--lr", type=float, default=3e-4)
    p.add_argument("--value-weight", type=float, default=0.25)

    p.add_argument("--seed", type=int, default=10)
    return p.parse_args()


def one_hot_policy(board: Board, action: int) -> np.ndarray:
    policy = np.zeros(board.size * board.size, dtype=np.float32)
    policy[int(action)] = 1.0
    return policy


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


def extension_score(board: Board, action: int, player: int) -> float:
    count, open_ends = line_info_after_move(board, action, player)
    return 100.0 * count + 10.0 * open_ends + center_bonus(board, action)


def strongest_extension_action(board: Board, player: int) -> tuple[int, int, int]:
    legal = [int(a) for a in board.legal_moves()]
    best_action = legal[0]
    best_score = -1e18
    best_count = 0
    best_open_ends = 0

    for action in legal:
        count, open_ends = line_info_after_move(board, action, player)
        score = 100.0 * count + 10.0 * open_ends + center_bonus(board, action)
        if score > best_score:
            best_score = score
            best_action = action
            best_count = count
            best_open_ends = open_ends

    return int(best_action), int(best_count), int(best_open_ends)


def greedy_win_block_action(board: Board) -> int:
    player = board.current_player
    opponent = -player

    wins = board.immediate_winning_moves(player)
    if wins:
        return int(wins[0])

    blocks = board.immediate_winning_moves(opponent)
    if blocks:
        return int(blocks[0])

    action, _, _ = strongest_extension_action(board, player)
    return int(action)


def tactical_teacher_action(board: Board) -> int:
    """
    Stronger than greedy:
    1. win immediately
    2. block opponent immediate win
    3. block opponent from extending to a strong 4
    4. extend own strongest line
    """
    player = board.current_player
    opponent = -player

    wins = board.immediate_winning_moves(player)
    if wins:
        return int(wins[0])

    blocks = board.immediate_winning_moves(opponent)
    if blocks:
        return int(blocks[0])

    opponent_action, opponent_count, opponent_open_ends = strongest_extension_action(board, opponent)

    # Key v10 change:
    # If opponent can create or extend a dangerous 4, occupy that point now.
    if opponent_count >= 4:
        return int(opponent_action)

    # Also block open/extendable 3 earlier.
    if opponent_count >= 3 and opponent_open_ends >= 1:
        return int(opponent_action)

    own_action, _, _ = strongest_extension_action(board, player)
    return int(own_action)


@torch.no_grad()
def model_action(model, board: Board, device: torch.device, temperature: float = 1.0, sample: bool = True) -> int:
    state = torch.tensor(board.encode()[None, ...], dtype=torch.float32, device=device)
    legal = torch.tensor(board.legal_mask()[None, ...], dtype=torch.float32, device=device)
    logits, _ = model(state)
    probs = masked_policy(logits, legal, temperature=temperature)[0].cpu().numpy()

    if sample:
        return int(np.random.choice(np.arange(board.size * board.size), p=probs))
    return int(np.argmax(probs))


def random_empty_cell(rng: np.random.Generator, board_size: int) -> tuple[int, int]:
    return int(rng.integers(0, board_size)), int(rng.integers(0, board_size))


def place_line_drill(
    rng: np.random.Generator,
    board_size: int,
    win_length: int,
    mode: str,
) -> GameSample:
    board = Board(size=board_size, win_length=win_length)
    player = 1
    opponent = -1
    board.current_player = player

    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
    dr, dc = directions[int(rng.integers(0, len(directions)))]

    while True:
        row = int(rng.integers(0, board_size))
        col = int(rng.integers(0, board_size))

        cells = []
        ok = True
        for i in range(win_length):
            r = row + dr * i
            c = col + dc * i
            if not (0 <= r < board_size and 0 <= c < board_size):
                ok = False
                break
            cells.append((r, c))

        if ok:
            break

    target_idx = int(rng.integers(0, win_length))
    target_cell = cells[target_idx]

    if mode == "win_four":
        stone_owner = player
        value = 0.0
    elif mode == "block_four":
        stone_owner = opponent
        value = 0.0
    elif mode == "block_three":
        stone_owner = opponent
        value = 0.0
    elif mode == "extend_three":
        stone_owner = player
        value = 0.0
    else:
        raise ValueError(f"unknown drill mode: {mode}")

    if mode in {"win_four", "block_four"}:
        fill_count = 4
    else:
        fill_count = 3

    available_indices = [i for i in range(win_length) if i != target_idx]
    rng.shuffle(available_indices)
    fill_indices = available_indices[:fill_count]

    for idx in fill_indices:
        r, c = cells[idx]
        board.grid[r, c] = stone_owner

    # Add a few random irrelevant stones so the network does not only see clean toy boards.
    extra_stones = int(rng.integers(0, 8))
    for _ in range(extra_stones):
        for _try in range(100):
            r, c = random_empty_cell(rng, board_size)
            if board.grid[r, c] == 0 and (r, c) != target_cell:
                board.grid[r, c] = player if rng.random() < 0.5 else opponent
                break

    board.move_count = int(np.count_nonzero(board.grid))
    board.last_move = None

    action = tactical_teacher_action(board)
    return GameSample(
        state=board.encode(),
        policy=one_hot_policy(board, action),
        value=float(value),
    )


def generate_drill_samples(rng: np.random.Generator, board_size: int, win_length: int, n: int) -> list[GameSample]:
    samples = []
    modes = ["win_four", "block_four", "block_three", "extend_three"]

    for i in range(n):
        mode = modes[i % len(modes)]
        samples.append(place_line_drill(rng, board_size, win_length, mode))

    return samples


def play_teacher_vs_greedy_game(
    board_size: int,
    win_length: int,
    teacher_player: int,
) -> tuple[list[GameSample], int | None, int]:
    board = Board(size=board_size, win_length=win_length)
    trajectory = []

    while True:
        teacher_action = tactical_teacher_action(board)
        teacher_policy = one_hot_policy(board, teacher_action)

        current_player = board.current_player
        trajectory.append((board.encode(), teacher_policy, current_player))

        if current_player == teacher_player:
            action = teacher_action
        else:
            action = greedy_win_block_action(board)

        result = board.play_flat(action)
        if result.done:
            winner = result.winner
            break

    samples = []
    for state, policy, player in trajectory:
        if winner is None:
            value = 0.0
        else:
            value = 1.0 if player == winner else -1.0
        samples.append(GameSample(state=state, policy=policy, value=value))

    return samples, winner, board.move_count


def generate_teacher_game_samples(board_size: int, win_length: int, games: int) -> list[GameSample]:
    all_samples = []
    teacher_wins = 0
    greedy_wins = 0
    draws = 0
    moves = []

    for g in range(games):
        teacher_player = 1 if g % 2 == 0 else -1
        samples, winner, move_count = play_teacher_vs_greedy_game(
            board_size=board_size,
            win_length=win_length,
            teacher_player=teacher_player,
        )
        all_samples.extend(samples)
        moves.append(move_count)

        if winner is None:
            draws += 1
        elif winner == teacher_player:
            teacher_wins += 1
        else:
            greedy_wins += 1

    print(
        f"teacher games: teacher_wins={teacher_wins}, greedy_wins={greedy_wins}, "
        f"draws={draws}, avg_moves={np.mean(moves):.2f}, samples={len(all_samples)}",
        flush=True,
    )

    return all_samples


def play_model_vs_greedy_corrective_game(
    model,
    board_size: int,
    win_length: int,
    device: torch.device,
    model_player: int,
) -> tuple[list[GameSample], int | None, int]:
    board = Board(size=board_size, win_length=win_length)
    trajectory = []

    while True:
        current_player = board.current_player

        # Policy label is always teacher action, even if actual move is model/greedy.
        # This turns bad sparring states into corrective supervised samples.
        teacher_action = tactical_teacher_action(board)
        teacher_policy = one_hot_policy(board, teacher_action)
        trajectory.append((board.encode(), teacher_policy, current_player))

        if current_player == model_player:
            action = model_action(model, board, device, temperature=1.0, sample=True)
        else:
            action = greedy_win_block_action(board)

        result = board.play_flat(action)
        if result.done:
            winner = result.winner
            break

    samples = []
    for state, policy, player in trajectory:
        if winner is None:
            value = 0.0
        else:
            value = 1.0 if player == winner else -1.0
        samples.append(GameSample(state=state, policy=policy, value=value))

    return samples, winner, board.move_count


def generate_corrective_sparring_samples(
    model,
    board_size: int,
    win_length: int,
    device: torch.device,
    games: int,
) -> list[GameSample]:
    all_samples = []
    model_wins = 0
    greedy_wins = 0
    draws = 0
    moves = []

    model.eval()
    for g in range(games):
        model_player = 1 if g % 2 == 0 else -1
        samples, winner, move_count = play_model_vs_greedy_corrective_game(
            model=model,
            board_size=board_size,
            win_length=win_length,
            device=device,
            model_player=model_player,
        )
        all_samples.extend(samples)
        moves.append(move_count)

        if winner is None:
            draws += 1
            outcome = "draw"
        elif winner == model_player:
            model_wins += 1
            outcome = "model_win"
        else:
            greedy_wins += 1
            outcome = "greedy_win"

        print(
            f"corrective sparring {g + 1}/{games}: {outcome}, moves={move_count}, "
            f"model_player={'black' if model_player == 1 else 'white'}",
            flush=True,
        )

    print(
        f"corrective sparring summary: model_wins={model_wins}, greedy_wins={greedy_wins}, "
        f"draws={draws}, avg_moves={np.mean(moves):.2f}, samples={len(all_samples)}",
        flush=True,
    )

    return all_samples


def train_on_samples(
    model,
    optimizer,
    samples: list[GameSample],
    batch_size: int,
    epochs: int,
    device: torch.device,
    value_weight: float,
    label: str,
) -> None:
    states = torch.tensor(np.stack([s.state for s in samples]), dtype=torch.float32)
    policies = torch.tensor(np.stack([s.policy for s in samples]), dtype=torch.float32)
    values = torch.tensor([s.value for s in samples], dtype=torch.float32)

    loader = DataLoader(
        TensorDataset(states, policies, values),
        batch_size=batch_size,
        shuffle=True,
    )

    model.train()
    for epoch in range(epochs):
        total_loss = 0.0
        total_policy_loss = 0.0
        total_value_loss = 0.0

        for batch_states, batch_policies, batch_values in loader:
            batch_states = batch_states.to(device)
            batch_policies = batch_policies.to(device)
            batch_values = batch_values.to(device)

            logits, predicted_values = model(batch_states)
            policy_loss = -(batch_policies * F.log_softmax(logits, dim=-1)).sum(dim=-1).mean()
            value_loss = F.mse_loss(predicted_values, batch_values)
            loss = policy_loss + value_weight * value_loss

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            batch_n = len(batch_states)
            total_loss += float(loss.item()) * batch_n
            total_policy_loss += float(policy_loss.item()) * batch_n
            total_value_loss += float(value_loss.item()) * batch_n

        n = len(samples)
        print(
            f"{label} epoch {epoch + 1}/{epochs}: "
            f"loss={total_loss / n:.4f}, "
            f"policy={total_policy_loss / n:.4f}, "
            f"value={total_value_loss / n:.4f}",
            flush=True,
        )


def main():
    args = parse_args()

    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    rng = np.random.default_rng(args.seed)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"device={device}", flush=True)

    model = PolicyValueNet(args.board_size, args.channels, args.blocks).to(device)

    load_compatible_checkpoint(
        model,
        args.init_checkpoint,
        device,
        board_size=args.board_size,
        channels=args.channels,
        blocks=args.blocks,
    )

    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)

    print("generating tactical drill samples...", flush=True)
    drill_samples = generate_drill_samples(
        rng=rng,
        board_size=args.board_size,
        win_length=args.win_length,
        n=args.drill_samples,
    )
    print(f"drill samples={len(drill_samples)}", flush=True)

    print("generating teacher-vs-greedy imitation samples...", flush=True)
    teacher_samples = generate_teacher_game_samples(
        board_size=args.board_size,
        win_length=args.win_length,
        games=args.teacher_games,
    )

    pretrain_samples = drill_samples + teacher_samples
    print(f"pretrain samples total={len(pretrain_samples)}", flush=True)

    train_on_samples(
        model=model,
        optimizer=optimizer,
        samples=pretrain_samples,
        batch_size=args.batch_size,
        epochs=args.pretrain_epochs,
        device=device,
        value_weight=args.value_weight,
        label="pretrain",
    )

    print("generating corrective model-vs-greedy sparring samples...", flush=True)
    sparring_samples = generate_corrective_sparring_samples(
        model=model,
        board_size=args.board_size,
        win_length=args.win_length,
        device=device,
        games=args.sparring_games,
    )

    mixed_samples = pretrain_samples + sparring_samples
    print(f"mixed samples total={len(mixed_samples)}", flush=True)

    train_on_samples(
        model=model,
        optimizer=optimizer,
        samples=mixed_samples,
        batch_size=args.batch_size,
        epochs=args.sparring_epochs,
        device=device,
        value_weight=args.value_weight,
        label="sparring-finetune",
    )

    args.out_checkpoint.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "model": model.state_dict(),
            "board_size": args.board_size,
            "win_length": args.win_length,
            "channels": args.channels,
            "blocks": args.blocks,
        },
        args.out_checkpoint,
    )
    print(f"saved {args.out_checkpoint}", flush=True)


if __name__ == "__main__":
    main()
