from __future__ import annotations

from pathlib import Path

import numpy as np
import torch

from gomoku_agent.board import Board
from gomoku_agent.model import PolicyValueNet, masked_policy


ROOT = Path(__file__).resolve().parents[1]
CHECKPOINT = ROOT / "checkpoints" / "9x9.pt"
OUT_DIR = ROOT / "c_inference" / "reference"


def build_case() -> Board:
    board = Board(size=9, win_length=5)
    moves = [
        (4, 4),
        (4, 3),
        (3, 4),
        (5, 4),
        (3, 3),
        (5, 5),
        (2, 4),
        (6, 4),
        (4, 5),
    ]
    for row, col in moves:
        board.play(row, col)
    return board


def main() -> None:
    payload = torch.load(CHECKPOINT, map_location="cpu")
    board_size = int(payload.get("board_size", 9))
    channels = int(payload.get("channels", 64))
    blocks = int(payload.get("blocks", 4))
    if board_size != 9:
        raise ValueError(f"expected a 9x9 checkpoint, got board_size={board_size}")

    model = PolicyValueNet(board_size=board_size, channels=channels, blocks=blocks)
    model.load_state_dict(payload["model"])
    model.eval()

    board = build_case()
    input_tensor = board.encode().astype(np.float32)
    legal_mask = board.legal_mask().astype(np.float32)

    with torch.no_grad():
        x = torch.tensor(input_tensor[None, ...], dtype=torch.float32)
        mask = torch.tensor(legal_mask[None, ...], dtype=torch.float32)
        logits, value = model(x)
        probs = masked_policy(logits, mask, temperature=1.0)

    logits_np = logits[0].cpu().numpy().astype(np.float32)
    probs_np = probs[0].cpu().numpy().astype(np.float32)
    value_np = np.array([float(value.item())], dtype=np.float32)
    masked_logits = np.where(legal_mask > 0, logits_np, -np.inf)
    top_legal_move = int(np.argmax(masked_logits))

    case_dir = OUT_DIR / "case0"
    case_dir.mkdir(parents=True, exist_ok=True)
    input_tensor.astype("<f4").tofile(case_dir / "input.bin")
    legal_mask.astype("<f4").tofile(case_dir / "legal_mask.bin")
    logits_np.astype("<f4").tofile(case_dir / "policy_logits.bin")
    probs_np.astype("<f4").tofile(case_dir / "policy_probs.bin")
    value_np.astype("<f4").tofile(case_dir / "value.bin")
    (case_dir / "top_legal_move.txt").write_text(f"{top_legal_move}\n", encoding="utf-8")
    (case_dir / "board.txt").write_text(board.render() + "\n", encoding="utf-8")
    (case_dir / "manifest.txt").write_text(
        "\n".join(
            [
                "case: case0",
                "input_shape: [3, 9, 9]",
                "input_channels: [current_player_stones, opponent_stones, last_move]",
                "policy_logits_shape: [81]",
                "policy_probs_shape: [81]",
                "value_shape: [1]",
                f"top_legal_move: {top_legal_move}",
                f"top_legal_move_row_col: {divmod(top_legal_move, 9)}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(f"wrote reference data to {case_dir}")
    print(f"top legal move: {top_legal_move} row_col={divmod(top_legal_move, 9)}")
    print(f"value: {value_np[0]:.8f}")


if __name__ == "__main__":
    main()
