# 15x15 neural-gomoku training summary

## Motivation

The previous best model was trained for 9x9. Public Gomoku/Piskvork benchmark environments usually use 15x15 or 20x20 boards, so the project moved toward 15x15 support and training.

## Public benchmark setup

Completed:
- Connected pbrain-neural-gomoku to the Gomocup/Piskvork protocol.
- Used c-gomoku-cli as a public benchmark manager.
- Used Rapfi as a public engine opponent.

9x9 result:
- The 9x9 model consistently lost against Rapfi.
- Increasing MCTS simulations, including sims=256, did not materially improve the result.
- This suggested that the main bottleneck was model strength and board-size mismatch, not just search settings.

## 15x15 pipeline

Completed:
- Python 15x15 training works.
- 15x15 checkpoints can be saved and loaded.
- C weights export was generalized beyond 9x9.
- C inference can be temporarily configured for 15x15.
- pbrain-neural-gomoku can accept START 15 in smoke tests.

## 15x15 checkpoint experiments

### v1: 15x15_mcts8_v1.pt
- v1 vs random: 1W / 0D / 3L
- v1 vs smoke: 2W / 0D / 2L
- v1 vs greedy_win_block: 0W / 0D / 4L, avg_moves=21.50

Interpretation:
- v1 was weak and not clearly better than smoke.

### v3: 15x15_mcts2_v3.pt
- v3 vs random: 5W / 0D / 1L, avg_moves=108.00
- v3 vs fast_v2: 3W / 0D / 3L, avg_moves=93.00
- v3 vs greedy_win_block: 0W / 0D / 6L, avg_moves=19.50

Interpretation:
- v3 became stable against random but still failed tactical defense.

### v4: 15x15_tactical_v4.pt
- v4 vs greedy_win_block: 0W / 0D / 6L, avg_moves=17.50
- v4 vs random: 6W / 0D / 0L, avg_moves=46.17
- v4 vs v3: 6W / 0D / 0L, avg_moves=40.50

Interpretation:
- Tactical fine-tuning improved some checkpoint-vs-checkpoint behavior but made greedy defense worse.

### v5: 15x15_mixed_v5.pt
- v5 vs random: 6W / 0D / 0L, avg_moves=93.83
- v5 vs v3: 3W / 0D / 3L, avg_moves=72.00
- v5 vs greedy_win_block: 0W / 0D / 6L, avg_moves=22.50

Interpretation:
- v5 was the most balanced checkpoint.
- It stayed strong against random and survived longer against greedy than v3/v4.

### v6: 15x15_defensive_v6.pt
- v6 vs greedy_win_block: 0W / 0D / 6L, avg_moves=17.50
- v6 vs random: 5W / 0D / 1L, avg_moves=110.33
- v6 vs v5: 0W / 0D / 6L, avg_moves=153.50

Interpretation:
- Synthetic defensive fine-tuning failed and should not replace v5.

### v7: 15x15_failure_mined_v7.pt
- v7 vs greedy_win_block: 0W / 0D / 6L, avg_moves=22.50
- v7 vs random: 6W / 0D / 0L, avg_moves=81.17
- v7 vs current_best/v5: 0W / 0D / 6L, avg_moves=94.50

Interpretation:
- Failure-mined fine-tuning did not improve over v5.
- v7 should not replace v5.

## Current best

Current best 15x15 checkpoint:
- 15x15_current_best.pt
- copied from 15x15_mixed_v5.pt

## Main limitation

The current 15x15 model can beat random consistently, but it still loses to a simple greedy_win_block tactical baseline. This shows that the model has not learned stable immediate-threat defense.

## Next direction

Recommended next steps:
- Keep v5 as the current best baseline.
- Improve data generation around real tactical threats, especially repeated blocking and open-four defense.
- Avoid adding more hard-coded C safety rules.
- Use stronger and more targeted training data before returning to Rapfi/public benchmark evaluation.
