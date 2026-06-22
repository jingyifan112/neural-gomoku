# Policy-only rank/top-k protected no-save probe report

## Scope

- No-save probe only.
- Optimizer runs in memory.
- No checkpoint is saved.
- No C export, no public benchmark, no promotion.

## Inputs

- dataset: `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_protected_train_11_50_weightcap3.json`
- dataset_name: `rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_protected_train_11_50_weightcap3`
- init_checkpoint: `checkpoints/15x15_current_best.pt`
- reference_checkpoint: `checkpoints/15x15_current_best.pt`
- epochs: 3
- lr: 1e-06
- margin: 0.25
- ce_weight: 1.0
- pair_weight: 0.0
- worst_weight: 0.0
- anchor_kl_weight: 0.05

## Group metrics

| group | rows | top3 delta | top5 delta | top10 delta | rank_gt50 delta | mean_rank delta | target_prob delta | mean_worst_gap delta | hinge delta | beats_worst delta | beats_all delta |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| train_main_rank_11_50 | 7 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | -1.857143 | 0.00049504 | 0.041463 | -0.238577 | 0.000000 | 0.000000 |
| protected_eval_top10 | 15 | 0.000000 | 0.000000 | 1.000000 | 0.000000 | -0.466667 | -0.01282100 | 0.735103 | -0.185786 | -1.000000 | -1.000000 |
| tail_eval_rank_gt50 | 3 | 0.000000 | 0.000000 | 0.000000 | 1.000000 | 37.333333 | -0.00009595 | 0.497262 | 0.558160 | 0.000000 | 0.000000 |

## Final training terms

| term | value |
|---|---:|
| loss | 7.59326220 |
| ce_loss | 7.58472824 |
| pair_hinge_loss | 4.71788025 |
| worst_hinge_loss | 7.36578846 |
| anchor_kl | 0.17068361 |
| mean_gap | -4.36015368 |
| mean_worst_gap | -6.97390795 |

## Verdict

FAIL_NO_SAVE_PROBE

## Decision

Do not save a checkpoint from this branch.
If the no-save probe fails, the next step should be another audit/design change, not a saved run.
