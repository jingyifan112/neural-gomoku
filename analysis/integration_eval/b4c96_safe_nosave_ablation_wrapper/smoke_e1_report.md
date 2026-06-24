# b4c96-safe protected no-save objective ablation wrapper report

## Scope

- b4c96-safe no-save probe only.
- Optimizer runs in memory.
- No checkpoint is saved.
- No C export, no public benchmark, no promotion.

## Architecture

- board_size: 15
- win_length: 5
- channels: 96
- blocks: 4

## Inputs

- dataset: `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_protected_train_11_50_weightcap3.json`
- dataset_name: `rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_protected_train_11_50_weightcap3`
- init_checkpoint: `checkpoints/probes/15x15_capacity_data_pairing_b4c96_probe_candidate.pt`
- reference_checkpoint: `checkpoints/probes/15x15_capacity_data_pairing_b4c96_probe_candidate.pt`
- epochs: 1
- lr: 1e-06
- margin: 0.25
- ce_weight: 1.0
- pair_weight: 0.0
- worst_weight: 0.0
- anchor_kl_weight: 0.05

## Group metrics

| group | rows | top3 delta | top5 delta | top10 delta | rank_gt50 delta | mean_rank delta | target_prob delta | mean_worst_gap delta | hinge delta | beats_worst delta | beats_all delta |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| train_main_rank_11_50 | 7 | 0.000000 | 0.000000 | 1.000000 | -1.000000 | -6.571429 | 0.00311335 | 0.293837 | -0.317029 | 0.000000 | 0.000000 |
| protected_eval_top10 | 15 | 0.000000 | -1.000000 | 2.000000 | 0.000000 | -0.666667 | -0.01157200 | 0.911482 | -0.108855 | -1.000000 | -1.000000 |
| tail_eval_rank_gt50 | 3 | 0.000000 | 0.000000 | -1.000000 | 2.000000 | 23.000000 | -0.00579487 | -1.014286 | 1.280641 | 0.000000 | 0.000000 |

## Final training terms

| term | value |
|---|---:|
| loss | 7.12899780 |
| ce_loss | 7.12246752 |
| pair_hinge_loss | 4.34403467 |
| worst_hinge_loss | 6.79207420 |
| anchor_kl | 0.13060468 |
| mean_gap | -3.69300938 |
| mean_worst_gap | -6.34299994 |

## Verdict

FAIL_B4C96_SAFE_NO_SAVE_PROBE

## Decision

No checkpoint was saved.
If the no-save probe fails, the next step should be another objective/data design change, not a saved run.
