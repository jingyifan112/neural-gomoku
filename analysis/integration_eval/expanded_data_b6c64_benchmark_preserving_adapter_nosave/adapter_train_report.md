# Expanded b6c64 benchmark-preserving adapter no-save report

- scope: benchmark-preserving adapter sanity run
- no_save: `True`
- saved_checkpoint: `False`
- no C export
- no public benchmark
- no promotion/current_best overwrite

## Input counts

| group | count |
|---|---:|
| `teacher_divergence_ce_train` | 12 |
| `public_tactical_mid_kl_anchor_train` | 48 |
| `protected_top10_kl_guard` | 15 |
| `tail_rank_kl_guard` | 15 |

## Loss weights

| term | weight |
|---|---:|
| CE teacher-divergence | 1 |
| public tactical_mid KL | 0.2 |
| protected KL | 0.35 |
| tail KL | 0.35 |

## Initial loss

| term | value |
|---|---:|
| `loss` | 5.343636 |
| `ce_loss` | 5.332779 |
| `public_kl` | 0.005263 |
| `protected_kl` | 0.015888 |
| `tail_kl` | 0.012125 |

## Final epoch

| term | value |
|---|---:|
| `epoch` | 1.000000 |
| `loss` | 5.342257 |
| `ce_loss` | 5.336319 |
| `public_kl` | 0.007217 |
| `protected_kl` | 0.006494 |
| `tail_kl` | 0.006345 |

## Teacher-divergence CE diagnostics

| phase | rows | top3 | top5 | top10 | rank_gt50 | mean_rank | mean_target_prob |
|---|---:|---:|---:|---:|---:|---:|---:|
| before | 12 | 0 | 0 | 1 | 6 | 91.833 | 0.005186 |
| after | 12 | 0 | 0 | 1 | 9 | 98.167 | 0.005000 |

## Baseline policy

- current-local tactical_mid no-regression gate: `>= 2.0/24 on tactical_mid`
- aspirational recovery target: `recover toward archived 7.0/24 on tactical_mid`

## Next step

If this no-save run is finite and teacher-divergence diagnostics improve without large KL movement, the next route can run a guarded saved candidate. Public benchmark must still be run separately after export.
