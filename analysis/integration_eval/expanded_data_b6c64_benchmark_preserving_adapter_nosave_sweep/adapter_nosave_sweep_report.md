# Expanded b6c64 benchmark-preserving adapter no-save sweep

- decision: `NO_SAVE_SWEEP_COMPLETE`
- no checkpoint
- no export
- no public benchmark
- no promotion/current_best overwrite

## Results

| config | status | top3 Δ | top5 Δ | top10 Δ | rank>50 Δ | mean_rank Δ | target_prob Δ | train public KL |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `ce_only_lr5e7_wd0` | `PASS_SOFT_TOP3_WARNING_NO_SAVE` | -1 | 0 | 0 | 0 | -4.000 | 0.00004553 | 0.001856 |
| `ce_only_lr1e7_wd0` | `PASS_SOFT_TOP3_WARNING_NO_SAVE` | -1 | 0 | 0 | 0 | -4.000 | 0.00004496 | 0.001856 |
| `balanced_lr1e7_wd0` | `PASS_SOFT_TOP3_WARNING_NO_SAVE` | -1 | 0 | 0 | 0 | -4.000 | 0.00004496 | 0.001856 |
| `balanced_lr5e8_wd0` | `PASS_SOFT_TOP3_WARNING_NO_SAVE` | -1 | 0 | 0 | 0 | -4.000 | 0.00004488 | 0.001856 |
| `strong_kl_lr5e7_wd0` | `PASS_SOFT_TOP3_WARNING_NO_SAVE` | -1 | 0 | 0 | 0 | -4.000 | 0.00004553 | 0.001856 |

## Selection rule

- Hard pass requires no top3/top5/top10 regression, no rank>50 increase, mean rank not worse, and target probability not worse.
- Soft pass allows only top3 warning if all broader metrics improve.
- No saved candidate should be created unless at least one no-save sweep config passes.

## Artifacts

- summary CSV: `analysis/integration_eval/expanded_data_b6c64_benchmark_preserving_adapter_nosave_sweep/adapter_nosave_sweep_summary.csv`
- summary JSON: `analysis/integration_eval/expanded_data_b6c64_benchmark_preserving_adapter_nosave_sweep/adapter_nosave_sweep_summary.json`
