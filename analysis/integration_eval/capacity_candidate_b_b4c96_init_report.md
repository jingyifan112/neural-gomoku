# Capacity Candidate B b4c96 init report

## Scope

This is the initialization and tiny-training smoke report for Capacity Candidate B.

It is not a promotion attempt.
No current-best checkpoint was changed.
No C export was run.
No public benchmark or Rapfi smoke was run.

## Candidate

- Candidate: Capacity Candidate B
- Board size: 15x15
- Source model shape: 4 residual blocks, 64 channels
- Target model shape: 4 residual blocks, 96 channels
- Source checkpoint: `checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt`
- Warm-start checkpoint: `checkpoints/15x15_capacity_b_b4c96_warmstart.pt`

## Initialization method

The target b4c96 model was initialized from the b4c64 current-best-family checkpoint.

Tensor copy policy:

- exact-shape tensors were copied directly
- widened tensors were prefix-copied into the overlapping channel slice
- newly added channels remained randomly initialized
- no tensors were skipped

Initialization result:

- board_size: 15
- channels: 96
- blocks: 4
- capacity_candidate: B_b4c96
- copied exact tensors: 22
- copied prefix tensors: 50
- skipped tensors: 0

## Tiny training smoke

A temporary smoke checkpoint was created from the warm-start checkpoint:

- `checkpoints/15x15_capacity_b_b4c96_smoke.pt`

The smoke run used:

- iterations: 1
- self-play games: 2
- epochs: 1
- batch size: 16
- MCTS sims: 8
- allow_immediate_loss: true
- seed: 37

The smoke checkpoint metadata remained valid:

- board_size: 15
- channels: 96
- blocks: 4
- model payload present: true

## Decision

Capacity Candidate B b4c96 passes the initialization and tiny-training smoke step.

This only validates that the widened PyTorch model can be initialized and trained. It does not establish benchmark strength.

## Next action

Proceed to a controlled b4c96 train_v1 run.

Do not export to C or run public benchmark yet. The current C inference path still assumes 64 channels unless separately updated for `GOMOKU_CHANNELS=96`.
