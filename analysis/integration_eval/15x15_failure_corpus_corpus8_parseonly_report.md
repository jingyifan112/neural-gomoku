# 15x15 failure corpus census

## Scope

- corpus source: existing debug logs passed to the census script
- logs parsed: 1
- baseline C weights for policy/value census: `/Users/jing1fan/neural-gomoku/weights/15x15_current_best_margin_candidate_d_move15_lastmove_weights.bin`
- lightweight parse mode: `True`
- no training, C export, promotion, or Rapfi smoke was run by this census step.

## Summary Metrics

- total games parsed: 8
- neural wins: 0
- neural losses: 8
- neural draws: 0
- censused neural loss decisions: 105
- safety/forcing and C-policy enrichment were skipped; related fields are `NA`.

## Per-Game Summary

| game | result | neural result | decisions | first losing value | first safety issue | first direct-vs-MCTS divergence | first forcing reply before |
|---|---|---|---:|---:|---:|---:|---:|
| baseline_mcts16_rapfi_depth1_corpus8.stdout:g1 | 0-1 | loss | 20 | NA | NA | 6 | NA |
| baseline_mcts16_rapfi_depth1_corpus8.stdout:g2 | 1-0 | loss | 10 | 9 | NA | 7 | NA |
| baseline_mcts16_rapfi_depth1_corpus8.stdout:g3 | 0-1 | loss | 13 | NA | NA | 2 | NA |
| baseline_mcts16_rapfi_depth1_corpus8.stdout:g4 | 1-0 | loss | 11 | NA | NA | 15 | NA |
| baseline_mcts16_rapfi_depth1_corpus8.stdout:g5 | 0-1 | loss | 15 | 14 | NA | 8 | NA |
| baseline_mcts16_rapfi_depth1_corpus8.stdout:g6 | 1-0 | loss | 9 | 5 | NA | 17 | NA |
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

## Opening Diversity

The corpus runner supports c-gomoku-cli opening diversity through `-openings`, `-repeat`, and `-transform`.
A small default 15x15 offset-opening file is provided at `analysis/integration_eval/15x15_corpus_openings_offset.txt`.
If the runner is invoked with `--no-openings` or the opening file is missing, collection can fall back to deterministic empty-board starts.

## Recommendation

Recommendation D: Need more diverse corpus before training. The current census is a pipeline seed, not enough evidence for Candidate K.

Do not train Candidate K yet unless this recommendation changes after a larger, diverse corpus is collected.

## Outputs

- failure census CSV: `analysis/integration_eval/15x15_failure_corpus_corpus8_parseonly_census.csv`
- game summary CSV: `analysis/integration_eval/15x15_failure_corpus_corpus8_parseonly_summary.csv`
