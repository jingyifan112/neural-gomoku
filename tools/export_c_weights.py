from __future__ import annotations

from pathlib import Path

import numpy as np
import torch

from gomoku_agent.model import PolicyValueNet


ROOT = Path(__file__).resolve().parents[1]
CHECKPOINT = ROOT / "checkpoints" / "9x9.pt"
OUT_DIR = ROOT / "c_inference" / "weights"
WEIGHTS_BIN = OUT_DIR / "9x9_weights.bin"
MANIFEST = OUT_DIR / "9x9_weights_manifest.txt"


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
    payload = torch.load(CHECKPOINT, map_location="cpu")
    board_size = int(payload.get("board_size", 9))
    channels = int(payload.get("channels", 64))
    blocks = int(payload.get("blocks", 4))
    if board_size != 9:
        raise ValueError(f"expected a 9x9 checkpoint, got board_size={board_size}")

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

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    offset = 0
    with WEIGHTS_BIN.open("wb") as weights_file, MANIFEST.open("w", encoding="utf-8") as manifest:
        manifest.write("Neural Gomoku C inference weights manifest\n")
        manifest.write("format: raw little-endian float32 tensors concatenated in the order below\n")
        manifest.write("batchnorm: folded into the immediately preceding convolution using eval-mode running stats\n")
        manifest.write(f"board_size: {board_size}\n")
        manifest.write(f"input_shape: [3, {board_size}, {board_size}]\n")
        manifest.write("input_channels: [current_player_stones, opponent_stones, last_move]\n")
        manifest.write(f"channels: {channels}\n")
        manifest.write(f"residual_blocks: {blocks}\n")
        manifest.write("tensor_order:\n")
        for name, array in tensors:
            flat = np.ascontiguousarray(array, dtype="<f4").ravel()
            weights_file.write(flat.tobytes())
            manifest.write(
                f"{len(name):02d} {name} shape={list(array.shape)} "
                f"offset_floats={offset} count={flat.size}\n"
            )
            offset += int(flat.size)
        manifest.write(f"total_floats: {offset}\n")
        manifest.write(f"total_bytes: {offset * 4}\n")

    print(f"wrote {WEIGHTS_BIN}")
    print(f"wrote {MANIFEST}")


if __name__ == "__main__":
    main()
