# b4c64/current-best row-level trace baseline run1

## Scope

- Branch: `exp/15x15-rank-topk-nosave-b4c64-row-trace-baseline-run1`
- Row-level trace of known failing baseline config.
- No checkpoint save, C export, public benchmark, promotion, or current-best overwrite was performed.

## Trace status

- Status: `TRACE_COMPLETE_GATE_CULPRITS_IDENTIFIED`
- Checkpoint-like outputs: `[]`
- Group counts: `{'protected_eval_top10': 15, 'tail_eval_rank_gt50': 3, 'train_main_rank_11_50': 7}`

## Culprit counts

- Protected lost teacher_beats_worst: `1`
- Protected lost teacher_beats_all: `1`
- Protected target-prob regressions: `4`
- Tail crossed into rank_gt50: `1`
- Tail rank regressions: `3`
- Train target-prob improvements: `3`
- Train rank improvements: `3`

## Protected rows that lost beats-worst/all

| case_id | row | rank before→after | prob Δ | worst gap before→after | beats-worst before→after | beats-all before→after |
|---|---:|---:|---:|---:|---:|---:|
| `legacy_g1_m40` | 2 | 1.0→3.0 | -0.27682457119226456 | 0.44618988037109375→-1.6974773406982422 | 1→0 | 1→0 |

## Tail rows that regressed

| case_id | row | rank before→after | rank>50 before→after | prob Δ | worst gap before→after |
|---|---:|---:|---:|---:|---:|
| `legacy_g1_m8` | 0 | 19.0→107.0 | 0→1 | -0.0005092114006401971 | -7.113358020782471→-7.985973358154297 |
| `legacy_g5_m12` | 1 | 85.0→92.0 | 1→1 | 0.00015571898984489962 | -9.02094841003418→-7.429637908935547 |
| `legacy_g5_m30` | 2 | 64.0→78.0 | 1→1 | 3.068152000196278e-05 | -8.378555297851562→-8.03365707397461 |

## Train row movement

| case_id | row | rank before→after | prob Δ | worst gap before→after |
|---|---:|---:|---:|---:|
| `legacy_g2_m11` | 0 | 13.0→15.0 | -7.686241406190675e-05 | -9.101638317108154→-10.571034908294678 |
| `legacy_g2_m21` | 1 | 41.0→44.0 | -6.154639413580298e-05 | -9.32773208618164→-10.745892524719238 |
| `legacy_g4_m13` | 2 | 16.0→16.0 | -0.0009794175566639751 | -5.973781585693359→-7.671762943267822 |
| `legacy_g4_m23` | 3 | 26.0→11.0 | 0.0023981257691048086 | -7.353243827819824→-5.234453201293945 |
| `legacy_g5_m14` | 4 | 20.0→25.0 | 0.0006550776888616383 | -6.855896949768066→-5.750880241394043 |
| `legacy_g5_m28` | 5 | 23.0→15.0 | 0.0028733813669532537 | -6.380010604858398→-5.125337600708008 |
| `legacy_g6_m17` | 6 | 9.0→7.0 | -0.001457774080336094 | -4.109737396240234→-4.586860656738281 |

## Decision

- Do not save a candidate from this run.
- Do not run C export, public benchmark, promotion, or current-best overwrite.
- The next route should protect/anchor `legacy_g1_m40` and `legacy_g1_m8`, or change the train/eval split/objective so these rows are not damaged.

## Outputs

- `analysis/integration_eval/rank_topk_nosave_b4c64_row_trace_baseline_run1/group_eval.csv`
- `analysis/integration_eval/rank_topk_nosave_b4c64_row_trace_baseline_run1/group_report.md`
- `analysis/integration_eval/rank_topk_nosave_b4c64_row_trace_baseline_run1/row_trace.csv`
- `analysis/integration_eval/rank_topk_nosave_b4c64_row_trace_baseline_run1/row_trace_culprits.csv`
- `analysis/integration_eval/rank_topk_nosave_b4c64_row_trace_baseline_run1/row_trace_report.md`
- `analysis/integration_eval/rank_topk_nosave_b4c64_row_trace_baseline_run1/row_trace_summary.json`
- `analysis/integration_eval/rank_topk_nosave_b4c64_row_trace_baseline_run1/train.log`
