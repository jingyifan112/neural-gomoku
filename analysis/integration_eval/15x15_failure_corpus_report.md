# 15x15 failure corpus census

## Scope

- corpus source: existing debug logs passed to the census script
- logs parsed: 1
- baseline C weights for policy/value census: `/Users/jing1fan/neural-gomoku/weights/15x15_current_best_margin_candidate_d_move15_lastmove_weights.bin`
- no training, C export, promotion, or Rapfi smoke was run by this census step.

## Summary Metrics

- total games parsed: 2
- neural wins: 0
- neural losses: 2
- neural draws: 0
- censused neural loss decisions: 34

## Per-Game Summary

| game | result | neural result | decisions | first losing value | first safety issue | first direct-vs-MCTS divergence | first forcing reply before |
|---|---|---|---:|---:|---:|---:|---:|
| candidate_d_move15_mcts16_debug_vs_rapfi_fast_g2:g1 | 0-1 | loss | 23 | NA | 42 | 2 | 32 |
| candidate_d_move15_mcts16_debug_vs_rapfi_fast_g2:g2 | 1-0 | loss | 11 | 1 | 19 | 13 | 21 |

## Repeated Move Clusters

| neural move | count |
|---:|---:|
| 5,6 | 2 |
| 5,8 | 2 |
| 6,6 | 2 |
| 7,7 | 1 |
| 4,3 | 1 |
| 2,6 | 1 |
| 3,3 | 1 |
| 5,4 | 1 |

## Repeated Local Pattern Clusters

| rank | count | pattern |
|---:|---:|---|
| 1 | 2 | `...../...../...../...../...../` |
| 2 | 1 | `...../...../...../..O../...../` |
| 3 | 1 | `....O/...O./...../...../...../` |
| 4 | 1 | `...../...../...C./..OO./..O../` |
| 5 | 1 | `...../CC.../OO.../O..../...../` |
| 6 | 1 | `O..../.O.../....C/...../...../` |
| 7 | 1 | `..O.O/.C.O./....C/...../...../` |
| 8 | 1 | `...CC/..OOO/...OO/..C.O/...C./` |

## Opening Diversity

The corpus runner supports c-gomoku-cli opening diversity through `-openings`, `-repeat`, and `-transform`.
A small default 15x15 offset-opening file is provided at `analysis/integration_eval/15x15_corpus_openings_offset.txt`.
If the runner is invoked with `--no-openings` or the opening file is missing, collection can fall back to deterministic empty-board starts.

## Recommendation

Recommendation D: Need more diverse corpus before training. The current census is a pipeline seed, not enough evidence for Candidate K.

Do not train Candidate K yet unless this recommendation changes after a larger, diverse corpus is collected.

## Outputs

- failure census CSV: `/Users/jing1fan/Documents/Codex/2026-06-09/you-are-working-in-the-neural/neural-gomoku/analysis/integration_eval/15x15_failure_corpus_census.csv`
- game summary CSV: `/Users/jing1fan/Documents/Codex/2026-06-09/you-are-working-in-the-neural/neural-gomoku/analysis/integration_eval/15x15_failure_corpus_summary.csv`
