# Rapfi Teacher Score-Gap Model Comparison: corpus8 selected

## Inputs

- `current_best`: `analysis/public_benchmark_eval/rapfi_teacher_scoregap_corpus8_selected.csv`
- `candidate_g`: `analysis/public_benchmark_eval/rapfi_teacher_scoregap_candidate_g_corpus8_selected.csv`
- `candidate_h`: `analysis/public_benchmark_eval/rapfi_teacher_scoregap_candidate_h_corpus8_selected.csv`

## Summary

| model | rows | concrete before | matches Rapfi best | match rate | numeric gaps | gap mean | gap median | gap max |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| current_best | 32 | 32 | 7 | 0.219 | 15 | 312.800 | 275.000 | 801.000 |
| candidate_g | 32 | 32 | 6 | 0.188 | 13 | 334.154 | 275.000 | 801.000 |
| candidate_h | 32 | 32 | 6 | 0.188 | 13 | 334.154 | 275.000 | 801.000 |

## Interpretation

- Best by direct Rapfi-best match count is `current_best`.
- `current_best` remains ahead of both candidate G and candidate H on this benchmark.
- Candidate G and candidate H each match the Rapfi re-query best move on 6/32 positions, below current_best at 7/32.
- Candidate G/H also have a worse numeric provisional gap mean than current_best on the rows where numeric gaps are defined.
- Mate-style scores such as `+M3` / `-M4` and NA rows are preserved in the source CSVs and are not forced into numeric gap statistics.

## Promotion decision

Do **not** promote candidate G or candidate H based on this corpus8 selected Rapfi teacher score-gap comparison.

## Next training-data direction

Use the Rapfi teacher rows as candidate supervision data only after filtering and labeling them carefully:

1. Prefer rows with concrete Rapfi teacher moves and stable re-query behavior.
2. Keep mate-score rows, but do not mix them blindly into numeric gap regression.
3. Build a small teacher-policy dataset first, then validate against both the 7-row fixed failure set and the 32-row corpus8 selected set.
4. Require no regression versus current_best before considering any promotion.

Per-position comparison CSV: `analysis/public_benchmark_eval/rapfi_teacher_scoregap_model_comparison_corpus8_selected.csv`

