# Capacity Candidate A b6c64 train_v2 benchmark probe

## Scope

This was a stabilization probe for Capacity Candidate A b6c64.

It was not a promotion attempt.
No current-best checkpoint was changed.
No formal Rapfi smoke was run.
No committed C weights or local binaries are intended.

## Candidate

- Candidate: Capacity Candidate A
- Model shape: 15x15, 64 channels, 6 residual blocks
- Training checkpoint: `checkpoints/15x15_capacity_a_b6c64_train_v2.pt`
- Exported probe weights: `weights/15x15_capacity_a_b6c64_train_v2_weights.bin`
- C engine: locally compiled with `-DGOMOKU_BLOCKS=6`

## Benchmark probe

Baseline:

- opponent: `tactical_mid`
- games: 24
- neural MCTS sims: 16
- rule: freestyle
- board size: 15

Result:

- Capacity A b6c64 train_v2 vs tactical_mid: 2 - 22 - 0
- Score: 2 / 24
- Score rate: 8.3%

Reference:

- current-best mcts16 vs tactical_mid: 7 / 24
- Capacity A b6c64 train_v1 vs tactical_mid: 2 / 24

## Interpretation

Capacity Candidate A b6c64 train_v2 did not recover from the train_v1 regression.

The result remains clearly below the current-best tactical_mid reference. This is a negative signal for the depth-only b6c64 path under the tested warm-start and short stabilization training setup.

## Decision

Stop Capacity Candidate A b6c64 for now.

Do not promote.
Do not run tactical_plus or rapfi_fast_depth1 for this checkpoint.
Do not commit the train_v2 checkpoint, exported weights, or local b6c64 binary.

## Recommended next action

Move to a separate capacity experiment rather than continuing this depth-only path.

Recommended next candidate:

- Capacity Candidate B: 4 residual blocks, 96 channels

This tests width-only capacity while avoiding the same depth-only failure mode seen in b6c64.
