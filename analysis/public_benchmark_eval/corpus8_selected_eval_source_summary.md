# Corpus8 Selected Evaluation Source Summary

## Source

- Input CSV: `analysis/integration_eval/15x15_failure_corpus_corpus8_selected_census.csv`
- Total rows: 105
- Selected enriched rows: 32

## Selected-row game coverage

- `baseline_mcts16_rapfi_depth1_corpus8.stdout:g1`: 5
- `baseline_mcts16_rapfi_depth1_corpus8.stdout:g2`: 6
- `baseline_mcts16_rapfi_depth1_corpus8.stdout:g3`: 4
- `baseline_mcts16_rapfi_depth1_corpus8.stdout:g4`: 5
- `baseline_mcts16_rapfi_depth1_corpus8.stdout:g5`: 8
- `baseline_mcts16_rapfi_depth1_corpus8.stdout:g6`: 4

## Enrichment reasons

- `neighbor`: 12
- `late_loss_window`: 10
- `first_direct_vs_mcts_divergence`: 4
- `first_losing_value`: 2
- `first_direct_vs_mcts_divergence;neighbor`: 1
- `first_losing_value;neighbor`: 1
- `first_direct_vs_mcts_divergence;late_loss_window`: 1
- `neighbor;late_loss_window`: 1

## Safety / forcing signals

- `neural_move_safety_pass` true count: 22 / 32
- `direct_move_safety_pass` true count: 17 / 32
- `opponent_forcing_reply_exists_before` true count: 6 / 32
- `opponent_forcing_reply_after_neural_move` true count: 10 / 32
- `already_forced_loss_signal` true count: 11 / 32
- `board_terminal_before` true count: 0 / 32

## Policy-rank availability

- `neural_move_policy_rank` non-NA: 32 / 32
- `direct_policy_rank` non-NA: 32 / 32
- `neural_move_policy_prob` non-NA: 32 / 32
- `direct_policy_prob` non-NA: 32 / 32
- `c_value` non-NA: 32 / 32

## Important limitation

This CSV is a useful larger candidate source for fixed position evaluation, but it does not contain full 15x15 board snapshots. It cannot yet be directly used by `scripts/evaluate_rapfi_failure_set.py` without reconstructing board snapshots from logs or another source.
