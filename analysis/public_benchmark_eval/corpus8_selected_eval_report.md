# Corpus8 Selected Fixed Position Evaluation

## Purpose

This report records a larger fixed position-level evaluation after moving away from match-only neural-vs-Rapfi W/D/L evaluation.

This is still an internal fixed-position evaluation, not yet a true external public benchmark. The positions are extracted from the 15x15 corpus8 neural-vs-Rapfi failure logs.

## Position set

- Source census: `analysis/integration_eval/15x15_failure_corpus_corpus8_selected_census.csv`
- Selected source CSV: `analysis/public_benchmark_eval/corpus8_selected_eval_source.csv`
- Snapshot targets: `analysis/public_benchmark_eval/corpus8_selected_snapshot_targets.csv`
- Board snapshots: `analysis/public_benchmark_eval/corpus8_selected_board_snapshots.json`
- Number of positions: 32
- Board size: 15x15
- Win length: 5

The board snapshots were reconstructed from:

- `eval_logs/integration_eval/baseline_mcts16_rapfi_depth1_corpus8.stdout.log`

## Models evaluated

| Model | Output CSV |
|---|---|
| current_best | `analysis/public_benchmark_eval/current_best_corpus8_selected_eval.csv` |
| candidate_g_teacher_policy | `analysis/public_benchmark_eval/candidate_g_corpus8_selected_eval.csv` |
| candidate_h_value_ranking | `analysis/public_benchmark_eval/candidate_h_corpus8_selected_eval.csv` |

## Summary

| Model | Positions | Direct matches logged final | Rate | Direct matches logged direct | Rate | Avg model value | Min value | Max value |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| current_best | 32 | 16 | 0.5000 | 19 | 0.59375 | -0.104761 | -0.815701 | 0.413587 |
| candidate_g_teacher_policy | 32 | 10 | 0.3125 | 17 | 0.53125 | -0.483205 | -0.933976 | -0.007581 |
| candidate_h_value_ranking | 32 | 10 | 0.3125 | 17 | 0.53125 | -0.444342 | -0.918793 | 0.007389 |

## Interpretation

Candidate G/H previously improved the tiny 7-position labeled failure set from 0/5 direct immediate blocks to 2/5.

However, on this broader 32-position corpus8 selected set, candidate G/H match the logged final move less often than current_best:

- current_best: 16/32
- candidate G: 10/32
- candidate H: 10/32

They also match the logged direct move slightly less often:

- current_best: 19/32
- candidate G: 17/32
- candidate H: 17/32

This suggests that candidate G/H provide localized repair but do not generalize cleanly across the broader selected corpus8 positions.

## Decision

Do not promote candidate G or candidate H.

Recommended conclusion:

Candidate G/H show localized improvement on a tiny labeled failure set, but they regress on the broader 32-position corpus8 selected evaluation. They should remain diagnostic candidates only.

## Important limitation

The logged final move is the baseline neural MCTS+safety move, not a verified Rapfi teacher best move. Therefore this evaluation is useful as an internal fixed-position regression test, but it is not yet a true public/Rapfi teacher score benchmark.

## Next step

Build a Rapfi teacher score-gap benchmark for the same fixed positions:

1. For each position, query Rapfi for best move and score.
2. Evaluate the neural direct move.
3. Query or estimate Rapfi score after the neural move.
4. Compute score gap.
5. Track top-1 / top-3 / top-5 agreement and catastrophic mistakes.
