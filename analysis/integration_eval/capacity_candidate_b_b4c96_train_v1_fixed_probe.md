# Capacity Candidate B b4c96 train_v1 fixed-position probe

## Scope

This was a PyTorch-only fixed-position probe for Capacity Candidate B b4c96 train_v1.

It was not a promotion attempt.
No C export was run.
No public benchmark or Rapfi smoke was run.
No current-best checkpoint was changed.

## Candidate

- Candidate: Capacity Candidate B
- Model shape: 15x15, 4 residual blocks, 96 channels
- Training checkpoint: `checkpoints/15x15_capacity_b_b4c96_train_v1.pt`
- Source warm-start: `checkpoints/15x15_capacity_b_b4c96_warmstart.pt`

## Training

The checkpoint was trained with a short controlled run:

- iterations: 1
- self-play games: 20
- replay samples: 841
- epochs: 2
- batch size: 32
- MCTS sims: 16
- seed: 59

Training loss:

- epoch 1/2: 3.5978
- epoch 2/2: 2.3657

The checkpoint metadata remained valid:

- board_size: 15
- channels: 96
- blocks: 4
- model payload present: true

## Fixed-position probe

Two tactical-mid diagnostic sets were evaluated:

1. `analysis/public_benchmark_eval/tactical_mid_must_block_cases.json`
2. `analysis/public_benchmark_eval/tactical_mid_preterminal_actionable_cases.json`

The comparison reference was:

- `checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt`

## Results

### Must-block cases

| Model | direct_target | policy_safety_target | direct_blocks | policy_safety_blocks | too_late_double_threat |
|---|---:|---:|---:|---:|---:|
| current-best b4c64 | 0/16 | 7/16 | 3/16 | 16/16 | 16/16 |
| Candidate B b4c96 train_v1 | 0/16 | 7/16 | 2/16 | 16/16 | 16/16 |

### Preterminal actionable cases

| Model | direct_target | policy_safety_target | direct_zero_double_threat_replies | policy_safety_zero_double_threat_replies |
|---|---:|---:|---:|---:|
| current-best b4c64 | 0/2 | 0/2 | 0/2 | 0/2 |
| Candidate B b4c96 train_v1 | 0/2 | 0/2 | 0/2 | 0/2 |

## Interpretation

Candidate B b4c96 train_v1 does not show a clear improvement over current-best on these PyTorch fixed-position tactical probes.

The critical policy-safety must-block metric is preserved at 16/16, so the checkpoint does not show an obvious safety regression on this diagnostic set. However, direct policy behavior did not improve, and direct blocking decreased from 3/16 to 2/16 on the must-block set.

The preterminal actionable subset remains unsolved for both current-best and Candidate B.

## Decision

Do not promote Candidate B b4c96 train_v1.

Do not update C inference for `GOMOKU_CHANNELS=96` yet. The fixed-position probe does not provide enough positive signal to justify C export and public benchmark work.

## Recommended next action

Run a stabilization train_v2 for b4c96 before deciding whether width-only capacity is worth a C inference update.

If train_v2 improves fixed-position probes over current-best, then update C inference to support `GOMOKU_CHANNELS=96` and run public benchmark.
If train_v2 remains neutral or worse, stop Candidate B.
