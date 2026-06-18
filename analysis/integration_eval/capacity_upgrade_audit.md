# 15x15 Capacity Upgrade Audit

## Scope

This audit reviews existing 15x15 capacity-upgrade artifacts before starting any new training.

It does not run training.
It does not create a checkpoint.
It does not export C weights.
It does not run a public benchmark.
It does not promote any model.

## Current reference

Current-best-family reference:

- checkpoint: `checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt`
- model shape: 15x15, 4 residual blocks, 64 channels
- total parameters: `415,163`
- float parameters: `415,152`
- tactical_mid public benchmark reference: `7 / 24` at MCTS16

## Existing capacity candidates

### Candidate A: b6c64 depth-only

Candidate A changed depth only:

- source shape: 4 blocks, 64 channels
- target shape: 6 blocks, 64 channels
- warm-start checkpoint: `checkpoints/15x15_capacity_a_b6c64_warmstart.pt`
- train_v1 checkpoint: `checkpoints/15x15_capacity_a_b6c64_train_v1.pt`
- train_v2 checkpoint: `checkpoints/15x15_capacity_a_b6c64_train_v2.pt`
- total parameters: `563,647`
- parameter ratio vs current-best-family: about `1.36x`

Warm-start result:

- copied tensors: `72`
- skipped tensors: `0`
- added residual blocks were newly initialized

Public benchmark probe:

| checkpoint | opponent | games | score | reference |
| --- | --- | ---: | ---: | ---: |
| `15x15_capacity_a_b6c64_train_v1.pt` | tactical_mid | 24 | 2 / 24 | 7 / 24 |
| `15x15_capacity_a_b6c64_train_v2.pt` | tactical_mid | 24 | 2 / 24 | 7 / 24 |

Decision:

- Stop Candidate A b6c64.
- Do not promote.
- Do not run tactical_plus or rapfi_fast_depth1 for these checkpoints.
- Do not commit b6c64 checkpoints, exported weights, or local binaries.
- Treat the depth-only warm-start path as negative under the tested short-training setup.

### Candidate B: b4c96 width-only

Candidate B changed width only:

- source shape: 4 blocks, 64 channels
- target shape: 4 blocks, 96 channels
- warm-start checkpoint: `checkpoints/15x15_capacity_b_b4c96_warmstart.pt`
- train_v1 checkpoint: `checkpoints/15x15_capacity_b_b4c96_train_v1.pt`
- train_v2 checkpoint: `checkpoints/15x15_capacity_b_b4c96_train_v2.pt`
- total parameters: `793,179`
- parameter ratio vs current-best-family: about `1.91x`

Warm-start result:

- copied exact tensors: `22`
- copied prefix tensors: `50`
- skipped tensors: `0`
- new widened channels were randomly initialized

Fixed-position probe summary:

| checkpoint | must-block direct_blocks | must-block policy_safety_blocks | preterminal prevention | conclusion |
| --- | ---: | ---: | ---: | --- |
| current-best-family b4c64 | 3 / 16 | 16 / 16 | 0 / 2 | reference |
| Candidate B train_v1 | 2 / 16 | 16 / 16 | 0 / 2 | minor direct regression |
| Candidate B train_v2 | 3 / 16 | 16 / 16 | 0 / 2 | recovered to reference, no improvement |

Decision:

- Stop Candidate B b4c96 for now.
- Do not promote.
- Do not update C inference for `GOMOKU_CHANNELS=96`.
- Do not export C weights.
- Do not run public benchmark or Rapfi smoke for b4c96.
- Width-only capacity did not produce a positive fixed-position signal.

## Export and local binary state

Observed local artifacts:

- `weights/15x15_capacity_a_b6c64_train_v1_weights.bin`
- `weights/15x15_capacity_a_b6c64_train_v1_weights_manifest.json`
- `weights/15x15_capacity_a_b6c64_train_v2_weights.bin`
- `weights/15x15_capacity_a_b6c64_train_v2_weights_manifest.json`
- `c_inference/pbrain-neural-gomoku-b6c64`

These are local capacity-probe artifacts and should not be promoted as current-best outputs.

No Candidate B C export should be done unless a future b4c96 checkpoint first shows a clear PyTorch-side improvement.

## Overall conclusion

The existing capacity-only sweep does not justify continuing with another blind capacity increase.

Candidate A increased depth and regressed on tactical_mid.

Candidate B increased width and matched current-best fixed-position behavior after stabilization, but did not improve it.

The bottleneck is more likely training signal quality than raw model capacity under the tested setup.

## Recommendation

Do not start Capacity Candidate C as another isolated capacity-only experiment.

The next work should shift to better training signal:

1. build or clean a broader teacher-divergence dataset from public benchmark failures and Rapfi re-query,
2. keep held-out retention checks to prevent anchor regressions,
3. prefer validated teacher disagreement rows over blind self-play capacity scaling,
4. revisit larger capacity only after the dataset/gate signal is stronger.

A future capacity experiment should be tied to a stronger supervised/teacher target, not just a bigger model initialized from current-best.

## Explicit non-actions

This audit made no changes to model state:

- no training,
- no checkpoint creation,
- no C export,
- no public benchmark,
- no promotion.
