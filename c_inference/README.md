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

C play has two modes:

- direct CNN policy only
- CNN policy plus terminal safety

Terminal safety is enabled by default. It checks only terminal win/loss
conditions and shallow lookahead:

- take an immediate winning move
- block an opponent immediate winning move
- avoid moves that allow an opponent immediate win
- avoid moves that allow the opponent to create multiple immediate winning
  moves next turn

It is not a full Gomoku strategy engine and does not implement neural MCTS.

Build and run C CPU play:

```bash
make play_c
./play_c weights/9x9_weights.bin
```

Disable terminal safety to measure direct CNN policy play:

```bash
./play_c weights/9x9_weights.bin --no-safety
```

The C player masks illegal moves and uses CNN policy logits as the ranking
signal. With safety enabled, terminal-safety filters adjust the candidate move
selection before the highest-policy move is chosen.

## Tactical Benchmark

Build and run the direct-policy tactical benchmark:

```bash
make benchmark
```

or explicitly:

```bash
./benchmark_c weights/9x9_weights.bin
```

The benchmark creates fixed 9x9 tactical positions and compares:

- direct CNN policy top legal move
- CNN policy plus terminal safety

Current cases:

- opponent has four in a row with one empty endpoint
- opponent has open three
- model has four in a row and can win
- model has a broken-four gap to fill

This benchmark is for measurement only. It does not add full rule-based shape
play or neural MCTS to C.
