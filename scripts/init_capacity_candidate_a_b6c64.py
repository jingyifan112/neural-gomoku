from __future__ import annotations

import argparse
from pathlib import Path

import torch

from gomoku_agent.model import PolicyValueNet


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Initialize 15x15 capacity Candidate A b6c64 from current-best b4c64."
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=Path("checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("checkpoints/15x15_capacity_a_b6c64_warmstart.pt"),
    )
    parser.add_argument("--board-size", type=int, default=15)
    parser.add_argument("--channels", type=int, default=64)
    parser.add_argument("--source-blocks", type=int, default=4)
    parser.add_argument("--target-blocks", type=int, default=6)
    parser.add_argument("--win-length", type=int, default=5)
    parser.add_argument("--seed", type=int, default=23)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    torch.manual_seed(args.seed)

    if not args.source.exists():
        raise FileNotFoundError(args.source)

    payload = torch.load(args.source, map_location="cpu")
    source_meta = {
        "board_size": payload.get("board_size"),
        "channels": payload.get("channels"),
        "blocks": payload.get("blocks"),
    }
    expected = {
        "board_size": args.board_size,
        "channels": args.channels,
        "blocks": args.source_blocks,
    }
    if source_meta != expected:
        raise ValueError(f"source checkpoint meta mismatch: expected={expected}, found={source_meta}")

    source_model = PolicyValueNet(
        board_size=args.board_size,
        channels=args.channels,
        blocks=args.source_blocks,
    )
    source_model.load_state_dict(payload["model"])

    target_model = PolicyValueNet(
        board_size=args.board_size,
        channels=args.channels,
        blocks=args.target_blocks,
    )

    source_state = source_model.state_dict()
    target_state = target_model.state_dict()

    copied = []
    skipped = []

    for name, tensor in source_state.items():
        if name in target_state and target_state[name].shape == tensor.shape:
            target_state[name] = tensor.clone()
            copied.append(name)
        else:
            skipped.append(name)

    target_model.load_state_dict(target_state)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "model": target_model.state_dict(),
            "board_size": args.board_size,
            "win_length": args.win_length,
            "channels": args.channels,
            "blocks": args.target_blocks,
            "capacity_candidate": "A_b6c64",
            "source_checkpoint": str(args.source),
            "source_blocks": args.source_blocks,
            "target_blocks": args.target_blocks,
            "warmstart_copied_tensors": len(copied),
            "warmstart_skipped_tensors": skipped,
        },
        args.output,
    )

    print(f"loaded source: {args.source}")
    print(f"wrote output: {args.output}")
    print(f"copied tensors: {len(copied)}")
    print(f"skipped tensors: {len(skipped)}")
    if skipped:
        print("skipped:")
        for name in skipped:
            print(f"  {name}")


if __name__ == "__main__":
    main()
