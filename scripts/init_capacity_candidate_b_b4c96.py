from __future__ import annotations

import argparse
from pathlib import Path

import torch

from gomoku_agent.model import PolicyValueNet


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Initialize 15x15 capacity Candidate B b4c96 from current-best b4c64."
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=Path("checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("checkpoints/15x15_capacity_b_b4c96_warmstart.pt"),
    )
    parser.add_argument("--board-size", type=int, default=15)
    parser.add_argument("--source-channels", type=int, default=64)
    parser.add_argument("--target-channels", type=int, default=96)
    parser.add_argument("--blocks", type=int, default=4)
    parser.add_argument("--win-length", type=int, default=5)
    parser.add_argument("--seed", type=int, default=29)
    return parser.parse_args()


def copy_prefix(target: torch.Tensor, source: torch.Tensor) -> tuple[torch.Tensor, bool]:
    """Copy source into the overlapping leading slice of target.

    Examples:
    - [96, 3, 3, 3] <- [64, 3, 3, 3] copies target[:64]
    - [96, 96, 3, 3] <- [64, 64, 3, 3] copies target[:64, :64]
    - [1, 96] <- [1, 64] copies target[:, :64]
    """
    if target.shape == source.shape:
        return source.clone(), True

    if len(target.shape) != len(source.shape):
        return target, False

    if any(s > t for s, t in zip(source.shape, target.shape)):
        return target, False

    out = target.clone()
    slices = tuple(slice(0, int(s)) for s in source.shape)
    out[slices] = source
    return out, True


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
        "channels": args.source_channels,
        "blocks": args.blocks,
    }
    if source_meta != expected:
        raise ValueError(f"source checkpoint meta mismatch: expected={expected}, found={source_meta}")

    source_model = PolicyValueNet(
        board_size=args.board_size,
        channels=args.source_channels,
        blocks=args.blocks,
    )
    source_model.load_state_dict(payload["model"])

    target_model = PolicyValueNet(
        board_size=args.board_size,
        channels=args.target_channels,
        blocks=args.blocks,
    )

    source_state = source_model.state_dict()
    target_state = target_model.state_dict()

    copied_exact: list[str] = []
    copied_prefix: list[str] = []
    skipped: list[str] = []

    for name, source_tensor in source_state.items():
        if name not in target_state:
            skipped.append(name)
            continue

        target_tensor = target_state[name]

        # BatchNorm num_batches_tracked is a scalar int tensor; copy directly.
        if target_tensor.shape == source_tensor.shape:
            target_state[name] = source_tensor.clone()
            copied_exact.append(name)
            continue

        copied_tensor, ok = copy_prefix(target_tensor, source_tensor)
        if ok:
            target_state[name] = copied_tensor
            copied_prefix.append(name)
        else:
            skipped.append(name)

    target_model.load_state_dict(target_state)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "model": target_model.state_dict(),
            "board_size": args.board_size,
            "win_length": args.win_length,
            "channels": args.target_channels,
            "blocks": args.blocks,
            "capacity_candidate": "B_b4c96",
            "source_checkpoint": str(args.source),
            "source_channels": args.source_channels,
            "target_channels": args.target_channels,
            "blocks_preserved": args.blocks,
            "warmstart_copied_exact_tensors": len(copied_exact),
            "warmstart_copied_prefix_tensors": len(copied_prefix),
            "warmstart_skipped_tensors": skipped,
        },
        args.output,
    )

    print(f"loaded source: {args.source}")
    print(f"wrote output: {args.output}")
    print(f"copied exact tensors: {len(copied_exact)}")
    print(f"copied prefix tensors: {len(copied_prefix)}")
    print(f"skipped tensors: {len(skipped)}")

    if copied_prefix:
        print("prefix-copied tensors:")
        for name in copied_prefix:
            print(f"  {name}")

    if skipped:
        print("skipped tensors:")
        for name in skipped:
            print(f"  {name}")


if __name__ == "__main__":
    main()
