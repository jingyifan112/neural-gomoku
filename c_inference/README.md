# C CPU Inference

This directory contains first-stage direct CNN policy/value inference for the
9x9 Gomoku model. It intentionally does not implement neural MCTS in C yet.

## Architecture

The C forward pass mirrors `src/gomoku_agent/model.py` in eval mode:

- input shape: `3 x 9 x 9`
- input channel order:
  - current player's stones
  - opponent stones
  - last move
- stem: `Conv2d(3, 64, 3x3, padding=1, bias=False) + BatchNorm + ReLU`
- tower: 4 residual blocks, each with:
  - `Conv2d(64, 64, 3x3, padding=1, bias=False) + BatchNorm + ReLU`
  - `Conv2d(64, 64, 3x3, padding=1, bias=False) + BatchNorm`
  - residual add + ReLU
- policy head:
  - `Conv2d(64, 2, 1x1, bias=False) + BatchNorm + ReLU`
  - flatten to 162 features
  - linear to 81 policy logits
- value head:
  - `Conv2d(64, 1, 1x1, bias=False) + BatchNorm + ReLU`
  - flatten to 81 features
  - linear 81 -> 64 + ReLU
  - linear 64 -> 1 + tanh

BatchNorm is folded into the preceding convolution during export, so C only
loads fused convolution weights and biases.

## Export Weights

From the repository root:

```bash
PYTHONPATH=src python tools/export_c_weights.py
```

This writes:

- `c_inference/weights/9x9_weights.bin`
- `c_inference/weights/9x9_weights_manifest.txt`

The manifest documents the exact deterministic tensor order and float offsets.

## Dump Python Reference

From the repository root:

```bash
PYTHONPATH=src python tools/dump_c_inference_reference.py
```

This writes fixed-board reference data under:

```text
c_inference/reference/case0/
```

The reference includes:

- input tensor
- legal mask
- PyTorch policy logits
- masked policy probabilities
- value output
- top legal move

## Build

From this directory:

```bash
make
```

## Consistency Test

From this directory:

```bash
make test
```

or explicitly:

```bash
./test_infer weights/9x9_weights.bin reference/case0
```

The test reports max absolute differences for policy logits, policy
probabilities, and value, and verifies that the C top legal move matches the
Python top legal move.

## C Command-Line Play

Build and run direct CNN CPU play:

```bash
make play_c
./play_c weights/9x9_weights.bin
```

The C player masks illegal moves and chooses the highest-policy legal move.
This is direct policy/value inference only; it does not run neural MCTS.

Because this mode is direct CNN inference only, weak tactical play is expected.
It does not include the Python neural MCTS search or terminal-safety layer yet.

## Tactical Benchmark

Build and run the direct-policy tactical benchmark:

```bash
make benchmark
```

or explicitly:

```bash
./benchmark_c weights/9x9_weights.bin
```

The benchmark creates fixed 9x9 tactical positions and measures whether the
direct CNN top legal move matches the expected tactical move. Current cases:

- opponent has four in a row with one empty endpoint
- opponent has open three
- model has four in a row and can win
- model has a broken-four gap to fill

This benchmark is for measurement only. It does not add rule-based move
selection to C play.
