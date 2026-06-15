# Capacity sweep A/B conclusion

## Scope

This document summarizes the early 15x15 capacity sweep after Candidate G.

The sweep tested whether increasing model capacity alone gives a clear improvement signal before committing to larger training, C export, or public benchmark expansion.

No current-best checkpoint was changed.
No promotion was made.
No formal Rapfi smoke was run.

## Reference

Current-best reference:

- Model shape: 15x15, 4 residual blocks, 64 channels
- tactical_mid public benchmark reference: 7 / 24 at MCTS16

## Capacity Candidate A: b6c64 depth-only

Candidate A increased depth while keeping channel width fixed:

- Source shape: 4 residual blocks, 64 channels
- Target shape: 6 residual blocks, 64 channels

### train_v1

Public benchmark probe:

- opponent: tactical_mid
- games: 24
- MCTS sims: 16
- result: 2 - 22 - 0
- score: 2 / 24

### train_v2

Stabilization probe:

- opponent: tactical_mid
- games: 24
- MCTS sims: 16
- result: 2 - 22 - 0
- score: 2 / 24

### Candidate A decision

Stop Candidate A b6c64.

Both short-training probes were clearly below the current-best tactical_mid reference of 7 / 24. This is a negative signal for the tested depth-only warm-start path.

Do not promote.
Do not run tactical_plus or rapfi_fast_depth1 for these checkpoints.
Do not commit b6c64 checkpoints, exported weights, or local binaries.

## Capacity Candidate B: b4c96 width-only

Candidate B increased width while keeping depth fixed:

- Source shape: 4 residual blocks, 64 channels
- Target shape: 4 residual blocks, 96 channels

The b4c96 checkpoint initialized successfully by prefix-copying the 64-channel weights into the widened 96-channel model.

### train_v1 fixed-position probe

Must-block tactical-mid cases:

| Model | direct_target | policy_safety_target | direct_blocks | policy_safety_blocks |
|---|---:|---:|---:|---:|
| current-best b4c64 | 0/16 | 7/16 | 3/16 | 16/16 |
| Candidate B b4c96 train_v1 | 0/16 | 7/16 | 2/16 | 16/16 |

Preterminal actionable cases:

| Model | direct_target | policy_safety_target | direct_zero_double_threat_replies | policy_safety_zero_double_threat_replies |
|---|---:|---:|---:|---:|
| current-best b4c64 | 0/2 | 0/2 | 0/2 | 0/2 |
| Candidate B b4c96 train_v1 | 0/2 | 0/2 | 0/2 | 0/2 |

### train_v2 fixed-position probe

Must-block tactical-mid cases:

| Model | direct_target | policy_safety_target | direct_blocks | policy_safety_blocks |
|---|---:|---:|---:|---:|
| current-best b4c64 | 0/16 | 7/16 | 3/16 | 16/16 |
| Candidate B b4c96 train_v2 | 0/16 | 7/16 | 3/16 | 16/16 |

Preterminal actionable cases:

| Model | direct_target | policy_safety_target | direct_zero_double_threat_replies | policy_safety_zero_double_threat_replies |
|---|---:|---:|---:|---:|
| current-best b4c64 | 0/2 | 0/2 | 0/2 | 0/2 |
| Candidate B b4c96 train_v2 | 0/2 | 0/2 | 0/2 | 0/2 |

### Candidate B decision

Stop Candidate B b4c96 for now.

train_v2 recovered the small train_v1 direct-block regression, but it did not improve over current-best. The fixed-position probe gives no positive reason to update C inference for 96 channels or run public benchmark.

Do not promote.
Do not export C weights.
Do not update C inference for `GOMOKU_CHANNELS=96`.
Do not run public benchmark or Rapfi smoke for b4c96.

## Overall conclusion

The capacity-only sweep did not produce a positive improvement signal.

- Candidate A depth-only b6c64 regressed on tactical_mid.
- Candidate B width-only b4c96 matched current-best fixed-position behavior after stabilization but did not improve it.

The current bottleneck is unlikely to be solved by isolated small capacity increases under these short warm-start training settings.

## Recommended next direction

Shift away from capacity-only experiments and toward better training signal.

Recommended next steps:

1. Build a broader teacher-divergence dataset from public benchmark failures and Rapfi teacher re-query.
2. Keep held-out retention checks to prevent regressions on current-best anchors.
3. Prefer policy/value repair from validated teacher disagreement rows over further blind capacity increases.
4. Only revisit larger capacity after the training target has stronger signal and a held-out validation set.
