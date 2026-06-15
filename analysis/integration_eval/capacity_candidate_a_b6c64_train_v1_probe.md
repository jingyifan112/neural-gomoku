# Capacity Candidate A b6c64 train_v1 benchmark probe

## Scope

This was an early capacity probe for a larger 15x15 policy-value model.

It was not a promotion attempt.
No current-best checkpoint was changed.
No formal Rapfi smoke was run.
No C weights or local binaries are intended to be committed.

## Candidate

- Candidate: Capacity Candidate A
- Model shape: 15x15, 64 channels, 6 residual blocks
- Source shape: 15x15, 64 channels, 4 residual blocks
- Training checkpoint: `checkpoints/15x15_capacity_a_b6c64_train_v1.pt`
- Exported probe weights: `weights/15x15_capacity_a_b6c64_train_v1_weights.bin`
- C engine: locally compiled with `-DGOMOKU_BLOCKS=6`

## Training

`train_v1` was initialized from the b6c64 warm-start checkpoint and trained with a short controlled run:

- iterations: 1
- self-play games: 20
- epochs: 2
- MCTS sims during training: 16
- allow_immediate_loss: true
- seed: 31

The checkpoint metadata after training remained valid:

- board_size: 15
- channels: 64
- blocks: 6
- model payload present: true

## Export / C support

The PyTorch checkpoint exported successfully:

- board_size: 15
- channels: 64
- residual_blocks: 6
- total_floats: 561127
- total_bytes: 2244508
- tensor_count: 36

The existing C inference code originally used a fixed `GOMOKU_BLOCKS=4`, so the local probe used a b6c64-specific C build with `-DGOMOKU_BLOCKS=6`.

## Benchmark probe

Baseline:

- opponent: `tactical_mid`
- games: 24
- neural MCTS sims: 16
- rule: freestyle
- board size: 15

Result:

- Capacity A b6c64 train_v1 vs tactical_mid: 2 - 22 - 0
- Score: 2 / 24
- Score rate: 8.3%

Reference current-best result:

- current-best mcts16 vs tactical_mid: 7 / 24

## Interpretation

Capacity Candidate A b6c64 train_v1 regressed on tactical_mid compared with current-best.

This result does not prove that larger capacity is bad, because `train_v1` was only a short training run and the added residual blocks were newly initialized. However, the early probe does not justify promotion or broader benchmark expansion.

## Decision

Do not promote Capacity Candidate A b6c64 train_v1.

Do not run tactical_plus or rapfi_fast_depth1 for this train_v1 checkpoint unless there is a specific diagnostic reason. The tactical_mid result is already below the current-best reference.

## Recommended next action

The next capacity experiment should avoid treating this short b6c64 run as a candidate improvement.

Reasonable follow-up options:

1. Try a stabilization phase for b6c64, such as lower learning rate or more training before benchmark.
2. Try width-only capacity Candidate B, such as 4 blocks and 96 channels, to isolate whether width is more helpful than depth.
3. Add a small held-out fixed-position policy/value probe before spending time on full public benchmark runs.
