# 2026-06-08 v12l margin repair summary

Branch: exp/15x15-v12l-margin-repair

## Goal

v12k CE-only repair improved target rank/probability but did not flip live C/Rapfi final decisions.

v12l switched from CE-only repair to pairwise logit margin repair.

## Baseline problem

From v12i snapshots:

- g2 m13:
  - target: 8,6
  - old final / suppress: 9,4
  - before repair logit_gap target-suppress: -5.653970

- g2 m15:
  - target: 8,6
  - old final / suppress: 6,6
  - before repair logit_gap target-suppress: -4.196625

Coordinate note:
- external logs use xy = col,row
- Python/C internal code uses rc = row,col
- target xy 8,6 = rc (6,8)

## v12l stage 1: frozen-BN margin repair

Best stage-1 checkpoint:

- checkpoints/15x15_v12l_margin_candidate_frozenbn.pt

Results:

- g2 m13:
  - target 8,6 rank 1
  - suppress 9,4 rank 2
  - logit_gap = 1.062665

- g2 m15:
  - target 8,6 rank 1
  - suppress 6,6 rank 4
  - logit_gap = 1.070575

C snapshot check showed direct policy repair succeeded, but MCTS16 still failed on g2 m15 by selecting 11,0.

## v12l stage 2: MCTS suppress refinement

Added an extra margin sample:

- g2 m15:
  - target: 8,6
  - new MCTS suppress: 11,0

Best refined checkpoint:

- checkpoints/15x15_v12l_margin_candidate_frozenbn_mcts_suppress.pt

Best exported C weights:

- weights/15x15_v12l_margin_frozenbn_mcts_suppress_weights.bin
- weights/15x15_v12l_margin_frozenbn_mcts_suppress_manifest.json

C snapshot MCTS16 result:

- g2 m13:
  - direct -> 8,6 PASS
  - safety -> 8,6 PASS
  - mcts_raw -> 8,6 PASS
  - mcts_safety -> 8,6 PASS
  - target vs 9,4 gap = 0.999162

- g2 m15:
  - direct -> 8,6 PASS
  - safety -> 8,6 PASS
  - mcts_raw -> 8,6 PASS
  - mcts_safety -> 8,6 PASS
  - target vs 6,6 gap = 1.188274
  - target vs 11,0 gap ≈ 1.159673

## C tactical benchmark

Using weights/15x15_v12l_margin_frozenbn_mcts_suppress_weights.bin:

- direct_policy_accuracy: 6/7 85.71%
- policy_plus_safety_accuracy: 7/7 100.00%
- mcts_raw_accuracy: 6/7 85.71%
- mcts_plus_safety_accuracy: 7/7 100.00%

The remaining raw failure is the known human_play_prevent_open_four_fork case; safety and MCTS+safety still pass.

## Internal direct sanity

- v12l vs random direct: 5W / 0D / 0L
- v12l vs greedy_win_block direct: 0W / 0D / 5L
- v12i vs greedy_win_block direct: 0W / 0D / 5L
- current_best vs greedy_win_block direct: 5W / 0D / 0L

Interpretation:

v12l fixed the targeted C/MCTS failure snapshots, but it is still not an overall stronger checkpoint than current_best.

## Decision

Do not promote.

Do not overwrite:

- checkpoints/15x15_current_best.pt

Keep v12l as a targeted repair candidate and use it to understand how margin repair affects C/MCTS final decisions.
