# 15x15 failure corpus census

## Scope

- corpus source: existing debug logs passed to the census script
- logs parsed: 1
- baseline C weights for policy/value census: `/Users/jing1fan/neural-gomoku/weights/15x15_current_best_margin_candidate_d_move15_lastmove_weights.bin`
- lightweight parse mode: `False`
- selected enrichment mode: `True`
- enriched positions: 32
- max enriched positions: 32
- no training, C export, promotion, or Rapfi smoke was run by this census step.

## Summary Metrics

- total games parsed: 8
- neural wins: 0
- neural losses: 8
- neural draws: 0
- censused neural loss decisions: 105
- safety/forcing and C-policy enrichment were enabled for selected rows only.

## Per-Game Summary

| game | result | neural result | decisions | first losing value | first safety issue | first direct-vs-MCTS divergence | first forcing reply before |
|---|---|---|---:|---:|---:|---:|---:|
| baseline_mcts16_rapfi_depth1_corpus8.stdout:g1 | 0-1 | loss | 20 | NA | 38 | 6 | 38 |
| baseline_mcts16_rapfi_depth1_corpus8.stdout:g2 | 1-0 | loss | 10 | 9 | 19 | 7 | 21 |
| baseline_mcts16_rapfi_depth1_corpus8.stdout:g3 | 0-1 | loss | 13 | NA | 24 | 2 | NA |
| baseline_mcts16_rapfi_depth1_corpus8.stdout:g4 | 1-0 | loss | 11 | NA | 21 | 15 | 21 |
| baseline_mcts16_rapfi_depth1_corpus8.stdout:g5 | 0-1 | loss | 15 | 14 | 28 | 8 | NA |
| baseline_mcts16_rapfi_depth1_corpus8.stdout:g6 | 1-0 | loss | 9 | 5 | NA | 17 | 19 |
| baseline_mcts16_rapfi_depth1_corpus8.stdout:g7 | 0-1 | loss | 17 | NA | NA | 20 | NA |
| baseline_mcts16_rapfi_depth1_corpus8.stdout:g8 | 1-0 | loss | 10 | 5 | NA | 13 | NA |

## Repeated Move Clusters

| neural move | count |
|---:|---:|
| 6,6 | 4 |
| 6,5 | 4 |
| 8,8 | 4 |
| 6,7 | 4 |
| 5,6 | 4 |
| 7,8 | 3 |
| 10,7 | 3 |
| 4,7 | 3 |

## Repeated Local Pattern Clusters

| rank | count | pattern |
|---:|---:|---|
| 1 | 5 | `...../...../...../...../...../` |
| 2 | 2 | `...../...../...../...O./...../` |
| 3 | 2 | `...../...../...../...O./....O/` |
| 4 | 2 | `...../...../...../.O.../...../` |
| 5 | 1 | `...../....O/...C./...../...../` |
| 6 | 1 | `..CCO/...../...../...../...../` |
| 7 | 1 | `...../...O./...CC/...../...C./` |
| 8 | 1 | `...../...../OO.../CO.../...../` |

## Selected Enrichment

- enriched rows: 32 across 6 games
- selected rows with safety/forcing issue: 10
- selected rows with policy rank > 10: 8
- the enrichment cap may leave later games parse-only; raise `--max-enriched-positions` for a broader second pass.

| game | ply | reason | move | rank | prob | value | safety | after-move forcing |
|---|---:|---|---:|---:|---:|---:|---|---|
| baseline_mcts16_rapfi_depth1_corpus8.stdout:g1 | 4 | neighbor | 7,6 | 24 | 0.001401 | 0.194954 | True | False |
| baseline_mcts16_rapfi_depth1_corpus8.stdout:g1 | 6 | first_direct_vs_mcts_divergence | 7,8 | 9 | 0.000797 | 0.042264 | True | False |
| baseline_mcts16_rapfi_depth1_corpus8.stdout:g1 | 8 | neighbor | 6,6 | 2 | 0.015775 | 0.029119 | True | False |
| baseline_mcts16_rapfi_depth1_corpus8.stdout:g1 | 38 | late_loss_window | 12,8 | 1 | 0.722655 | -0.072800 | False | True |
| baseline_mcts16_rapfi_depth1_corpus8.stdout:g1 | 40 | late_loss_window | 12,6 | 3 | 0.054793 | -0.036660 | False | True |
| baseline_mcts16_rapfi_depth1_corpus8.stdout:g2 | 5 | neighbor | 7,8 | 5 | 0.003225 | 0.093849 | True | False |
| baseline_mcts16_rapfi_depth1_corpus8.stdout:g2 | 7 | first_direct_vs_mcts_divergence;neighbor | 9,6 | 1 | 0.998378 | 0.043940 | True | False |
| baseline_mcts16_rapfi_depth1_corpus8.stdout:g2 | 9 | first_losing_value;neighbor | 9,5 | 4 | 0.001989 | -0.022700 | True | False |
| baseline_mcts16_rapfi_depth1_corpus8.stdout:g2 | 11 | neighbor | 7,4 | 11 | 0.001501 | 0.138243 | True | False |
| baseline_mcts16_rapfi_depth1_corpus8.stdout:g2 | 19 | late_loss_window | 5,6 | 1 | 0.999901 | -0.335186 | False | True |
| baseline_mcts16_rapfi_depth1_corpus8.stdout:g2 | 21 | late_loss_window | 2,4 | 1 | 0.515940 | -0.531131 | False | True |
| baseline_mcts16_rapfi_depth1_corpus8.stdout:g3 | 2 | first_direct_vs_mcts_divergence | 6,6 | 16 | 0.000396 | 0.319652 | True | False |
| baseline_mcts16_rapfi_depth1_corpus8.stdout:g3 | 4 | neighbor | 8,8 | 46 | 0.000014 | 0.040226 | True | False |
| baseline_mcts16_rapfi_depth1_corpus8.stdout:g3 | 24 | late_loss_window | 3,7 | 11 | 0.007063 | -0.067985 | False | True |
| baseline_mcts16_rapfi_depth1_corpus8.stdout:g3 | 26 | late_loss_window | 6,3 | 2 | 0.138041 | -0.099022 | False | True |
| baseline_mcts16_rapfi_depth1_corpus8.stdout:g4 | 13 | neighbor | 8,4 | 2 | 0.048305 | -0.091947 | True | False |
| baseline_mcts16_rapfi_depth1_corpus8.stdout:g4 | 15 | first_direct_vs_mcts_divergence | 6,4 | 2 | 0.309385 | 0.039381 | True | False |
| baseline_mcts16_rapfi_depth1_corpus8.stdout:g4 | 17 | neighbor | 10,6 | 3 | 0.017901 | 0.262013 | True | False |
| baseline_mcts16_rapfi_depth1_corpus8.stdout:g4 | 21 | late_loss_window | 10,8 | 1 | 0.813518 | 0.333943 | False | True |
| baseline_mcts16_rapfi_depth1_corpus8.stdout:g4 | 23 | late_loss_window | 12,9 | 1 | 0.632920 | -0.105756 | False | True |
| baseline_mcts16_rapfi_depth1_corpus8.stdout:g5 | 6 | neighbor | 9,8 | 18 | 0.002893 | -0.117984 | True | False |
| baseline_mcts16_rapfi_depth1_corpus8.stdout:g5 | 8 | first_direct_vs_mcts_divergence | 8,5 | 1 | 0.958359 | -0.327685 | True | False |
| baseline_mcts16_rapfi_depth1_corpus8.stdout:g5 | 10 | neighbor | 10,7 | 14 | 0.001953 | -0.432555 | True | False |
| baseline_mcts16_rapfi_depth1_corpus8.stdout:g5 | 12 | neighbor | 7,6 | 1 | 0.996139 | -0.321221 | True | False |
| baseline_mcts16_rapfi_depth1_corpus8.stdout:g5 | 14 | first_losing_value | 6,6 | 3 | 0.018886 | -0.765032 | True | False |
| baseline_mcts16_rapfi_depth1_corpus8.stdout:g5 | 16 | neighbor | 7,5 | 3 | 0.066424 | -0.686751 | True | False |
| baseline_mcts16_rapfi_depth1_corpus8.stdout:g5 | 28 | late_loss_window | 5,11 | 6 | 0.019522 | -0.607046 | False | True |
| baseline_mcts16_rapfi_depth1_corpus8.stdout:g5 | 30 | late_loss_window | 4,9 | 9 | 0.005865 | -0.229517 | False | True |
| baseline_mcts16_rapfi_depth1_corpus8.stdout:g6 | 5 | first_losing_value | 8,8 | 3 | 0.012065 | -0.055032 | True | False |
| baseline_mcts16_rapfi_depth1_corpus8.stdout:g6 | 15 | neighbor | 4,8 | 1 | 0.338997 | -0.088081 | True | False |
| baseline_mcts16_rapfi_depth1_corpus8.stdout:g6 | 17 | first_direct_vs_mcts_divergence;late_loss_window | 4,9 | 1 | 0.518564 | 0.134861 | True | False |
| baseline_mcts16_rapfi_depth1_corpus8.stdout:g6 | 19 | neighbor;late_loss_window | 9,5 | 21 | 0.000134 | 0.107356 | True | False |

Selected reason counts:
- neighbor: 15
- late_loss_window: 12
- first_direct_vs_mcts_divergence: 6
- first_losing_value: 3

## Opening Diversity

The corpus runner supports c-gomoku-cli opening diversity through `-openings`, `-repeat`, and `-transform`.
A small default 15x15 offset-opening file is provided at `analysis/integration_eval/15x15_corpus_openings_offset.txt`.
If the runner is invoked with `--no-openings` or the opening file is missing, collection can fall back to deterministic empty-board starts.

## Recommendation

Recommendation D: Need more diverse corpus before training. The current census is a pipeline seed, not enough evidence for Candidate K.

Do not train Candidate K yet unless this recommendation changes after a larger, diverse corpus is collected.

## Outputs

- failure census CSV: `analysis/integration_eval/15x15_failure_corpus_corpus8_selected_census.csv`
- game summary CSV: `analysis/integration_eval/15x15_failure_corpus_corpus8_selected_summary.csv`
