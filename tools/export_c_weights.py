from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch

from gomoku_agent.model import PolicyValueNet


ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export PyTorch Gomoku checkpoint to raw C-readable float32 weights.")
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, default=None)
    return parser.parse_args()


def fold_conv_bn(conv: torch.nn.Conv2d, bn: torch.nn.BatchNorm2d) -> tuple[np.ndarray, np.ndarray]:
    weight = conv.weight.detach().cpu().numpy().astype(np.float32)
    gamma = bn.weight.detach().cpu().numpy().astype(np.float32)
    beta = bn.bias.detach().cpu().numpy().astype(np.float32)
    mean = bn.running_mean.detach().cpu().numpy().astype(np.float32)
    var = bn.running_var.detach().cpu().numpy().astype(np.float32)
    scale = gamma / np.sqrt(var + float(bn.eps))
    folded_weight = weight * scale[:, None, None, None]
    folded_bias = beta - mean * scale
    return folded_weight.astype(np.float32), folded_bias.astype(np.float32)


def add_tensor(items: list[tuple[str, np.ndarray]], name: str, array: np.ndarray) -> None:
    items.append((name, np.ascontiguousarray(array, dtype=np.float32)))


def main() -> None:
    args = parse_args()

    checkpoint = args.checkpoint
    out_path = args.out
    manifest_path = args.manifest
    if manifest_path is None:
        manifest_path = out_path.with_name(out_path.stem + "_manifest.txt")

    payload = torch.load(checkpoint, map_location="cpu")
    board_size = int(payload.get("board_size", 9))
    channels = int(payload.get("channels", 64))
    blocks = int(payload.get("blocks", 4))
    win_length = int(payload.get("win_length", 5))

    model = PolicyValueNet(board_size=board_size, channels=channels, blocks=blocks)
    model.load_state_dict(payload["model"])
    model.eval()

    tensors: list[tuple[str, np.ndarray]] = []

    weight, bias = fold_conv_bn(model.stem[0], model.stem[1])
    add_tensor(tensors, "stem.conv3x3_bn_fused.weight", weight)
    add_tensor(tensors, "stem.conv3x3_bn_fused.bias", bias)

    for block_idx, block in enumerate(model.tower):
        weight, bias = fold_conv_bn(block.conv1, block.bn1)
        add_tensor(tensors, f"tower.{block_idx}.conv1_3x3_bn_fused.weight", weight)
        add_tensor(tensors, f"tower.{block_idx}.conv1_3x3_bn_fused.bias", bias)

        weight, bias = fold_conv_bn(block.conv2, block.bn2)
        add_tensor(tensors, f"tower.{block_idx}.conv2_3x3_bn_fused.weight", weight)
        add_tensor(tensors, f"tower.{block_idx}.conv2_3x3_bn_fused.bias", bias)

    weight, bias = fold_conv_bn(model.policy[0], model.policy[1])
    add_tensor(tensors, "policy.conv1x1_bn_fused.weight", weight)
    add_tensor(tensors, "policy.conv1x1_bn_fused.bias", bias)
    add_tensor(tensors, "policy.linear.weight", model.policy[4].weight.detach().cpu().numpy())
    add_tensor(tensors, "policy.linear.bias", model.policy[4].bias.detach().cpu().numpy())

    weight, bias = fold_conv_bn(model.value_conv[0], model.value_conv[1])
    add_tensor(tensors, "value.conv1x1_bn_fused.weight", weight)
    add_tensor(tensors, "value.conv1x1_bn_fused.bias", bias)
    add_tensor(tensors, "value.fc1.weight", model.value_fc[0].weight.detach().cpu().numpy())
    add_tensor(tensors, "value.fc1.bias", model.value_fc[0].bias.detach().cpu().numpy())
    add_tensor(tensors, "value.fc2.weight", model.value_fc[2].weight.detach().cpu().numpy())
    add_tensor(tensors, "value.fc2.bias", model.value_fc[2].bias.detach().cpu().numpy())

    out_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    offset = 0
    manifest_tensors = []
    with out_path.open("wb") as weights_file:
        for name, array in tensors:
            flat = np.ascontiguousarray(array, dtype="<f4").ravel()
            weights_file.write(flat.tobytes())
            manifest_tensors.append(
                {
                    "name": name,
                    "shape": list(array.shape),
                    "offset_floats": offset,
                    "count": int(flat.size),
                }
            )
            offset += int(flat.size)

    if manifest_path.suffix == ".json":
        manifest = {
            "format": "raw little-endian float32 tensors concatenated in tensor_order",
            "batchnorm": "folded into the immediately preceding convolution using eval-mode running stats",
            "source_checkpoint": str(checkpoint),
            "weights_path": str(out_path),
            "board_size": board_size,
            "win_length": win_length,
            "input_shape": [3, board_size, board_size],
            "input_channels": ["current_player_stones", "opponent_stones", "last_move"],
            "channels": channels,
            "residual_blocks": blocks,
            "tensor_order": manifest_tensors,
            "total_floats": offset,
            "total_bytes": offset * 4,
        }
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    else:
        with manifest_path.open("w", encoding="utf-8") as manifest:
            manifest.write("Neural Gomoku C inference weights manifest\n")
            manifest.write("format: raw little-endian float32 tensors concatenated in the order below\n")
            manifest.write("batchnorm: folded into the immediately preceding convolution using eval-mode running stats\n")
            manifest.write(f"source_checkpoint: {checkpoint}\n")
            manifest.write(f"board_size: {board_size}\n")
            manifest.write(f"win_length: {win_length}\n")
            manifest.write(f"input_shape: [3, {board_size}, {board_size}]\n")
            manifest.write("input_channels: [current_player_stones, opponent_stones, last_move]\n")
            manifest.write(f"channels: {channels}\n")
            manifest.write(f"residual_blocks: {blocks}\n")
            manifest.write("tensor_order:\n")
            for item in manifest_tensors:
                manifest.write(
                    f"{len(item['name']):02d} {item['name']} shape={item['shape']} "
                    f"offset_floats={item['offset_floats']} count={item['count']}\n"
                )
            manifest.write(f"total_floats: {offset}\n")
            manifest.write(f"total_bytes: {offset * 4}\n")

    print(f"checkpoint: {checkpoint}")
    print(f"board_size: {board_size}")
    print(f"channels: {channels}")
    print(f"blocks: {blocks}")
    print(f"total_floats: {offset}")
    print(f"wrote {out_path}")
    print(f"wrote {manifest_path}")


if __name__ == "__main__":
    main()
