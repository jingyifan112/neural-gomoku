# Capacity Candidate B b4c96 train_v2 fixed-position probe

## Scope

This was a PyTorch-only stabilization probe for Capacity Candidate B b4c96 train_v2.

It was not a promotion attempt.
No C export was run.
No public benchmark or Rapfi smoke was run.
No current-best checkpoint was changed.

## Candidate

- Candidate: Capacity Candidate B
- Model shape: 15x15, 4 residual blocks, 96 channels
- Training checkpoint: `checkpoints/15x15_capacity_b_b4c96_train_v2.pt`
- Source warm-start: `checkpoints/15x15_capacity_b_b4c96_warmstart.pt`

## Fixed-position probe

Two tactical-mid diagnostic sets were evaluated:

1. `analysis/public_benchmark_eval/tactical_mid_must_block_cases.json`
2. `analysis/public_benchmark_eval/tactical_mid_preterminal_actionable_cases.json`

Reference model:

- `checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt`

## Results

### Must-block cases

| Model | direct_target | policy_safety_target | direct_blocks | policy_safety_blocks | too_late_double_threat |
|---|---:|---:|---:|---:|---:|
| current-best b4c64 | 0/16 | 7/16 | 3/16 | 16/16 | 16/16 |
| Candidate B b4c96 train_v1 | 0/16 | 7/16 | 2/16 | 16/16 | 16/16 |
| Candidate B b4c96 train_v2 | 0/16 | 7/16 | 3/16 | 16/16 | 16/16 |

### Preterminal actionable cases

| Model | direct_target | policy_safety_target | direct_zero_double_threat_replies | policy_safety_zero_double_threat_replies |
|---|---:|---:|---:|---:|
| current-best b4c64 | 0/2 | 0/2 | 0/2 | 0/2 |
| Candidate B b4c96 train_v1 | 0/2 | 0/2 | 0/2 | 0/2 |
| Candidate B b4c96 train_v2 | 0/2 | 0/2 | 0/2 | 0/2 |

## Interpretation

Candidate B b4c96 train_v2 recovered the minor train_v1 direct-block regression, but it did not improve over current-best on the fixed-position tactical probes.

The policy-safety must-block metric remained stable at 16/16, but direct policy did not improve beyond current-best, and the preterminal actionable subset remained unsolved.

## Decision

Stop Capacity Candidate B b4c96 for now.

Do not promote.
Do not update C inference for `GOMOKU_CHANNELS=96`.
Do not export C weights.
Do not run public benchmark or Rapfi smoke for this checkpoint.

## Recommended next action

The current capacity-only probes do not provide a positive signal:

- Capacity A b6c64 train_v1: tactical_mid 2/24
- Capacity A b6c64 train_v2: tactical_mid 2/24
- Capacity B b4c96 train_v1: no fixed-position improvement
- Capacity B b4c96 train_v2: matches current-best fixed-position probes but does not improve

The next step should shift away from isolated capacity changes and toward better training signal: larger teacher-divergence data, held-out retention checks, or a more targeted tactical/teacher repair dataset.
