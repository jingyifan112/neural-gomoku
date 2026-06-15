# Capacity Candidate A b6c64 initialization report

## Scope

This step initializes a larger 15x15 policy-value model for a capacity experiment.

It is not a promotion attempt.
No C export was performed.
No formal Rapfi smoke was run.
No current-best checkpoint was changed.

## Candidate

- Name: Capacity Candidate A
- Board size: 15x15
- Channels: 64
- Blocks: 6
- Baseline/current-best shape: 64 channels, 4 blocks
- Capacity change: increase residual depth from 4 blocks to 6 blocks while keeping channel width fixed

## Motivation

Recent public benchmark results suggest that increasing MCTS simulations alone does not reliably improve performance on stronger tactical baselines. This points to policy/value model quality and model capacity as likely bottlenecks.

Candidate A tests a conservative capacity increase by adding depth only, while preserving channel width.

## Warm-start

Warm-start source:

- `checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt`

Warm-start output:

- `checkpoints/15x15_capacity_a_b6c64_warmstart.pt`

Initialization script:

- `scripts/init_capacity_candidate_a_b6c64.py`

Warm-start result:

- Source checkpoint loaded successfully
- Target model metadata:
  - board_size: 15
  - channels: 64
  - blocks: 6
- Copied tensors: 72
- Skipped tensors: 0

The first 4 residual blocks and compatible stem/policy/value tensors were copied from the 4-block current-best checkpoint. The added residual blocks were left randomly initialized.

## Tiny training smoke

A separate smoke checkpoint was created from the warm-start checkpoint:

- `checkpoints/15x15_capacity_a_b6c64_smoke.pt`

The tiny smoke training run completed successfully with:

- iterations: 1
- games: 2
- epochs: 1
- mcts_sims: 8
- allow_immediate_loss: true

The saved smoke checkpoint retained the expected metadata:

- board_size: 15
- channels: 64
- blocks: 6
- model payload present: true

## Decision

Capacity Candidate A b6c64 passes initialization and tiny training smoke.

This only validates that the larger model can be initialized and trained without shape or metadata errors. It does not establish playing strength.

## Recommended next action

Run a controlled capacity training experiment using the b6c64 warm-start checkpoint, then evaluate against the same public benchmark ladder used for current-best.

Suggested evaluation focus:

- tactical_mid: compare against current-best 7/24
- tactical_plus: compare against current-best best run 3/24
- rapfi_fast_depth1: check whether score remains 0/24 or improves

Do not promote Candidate A unless it improves benchmark performance and passes retention checks.
