# b4c64/current-best-safe protected no-save objective ablation wrapper report

## Scope

- b4c64/current-best-safe no-save probe only.
- Optimizer runs in memory.
- No checkpoint is saved.
- No C export, no public benchmark, no promotion.

## Architecture

- board_size: 15
- win_length: 5
- channels: 64
- blocks: 4

## Inputs

- dataset: `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_guarded_split_v1.json`
- dataset_name: `rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_guarded_split_v1`
- init_checkpoint: `checkpoints/15x15_current_best.pt`
- reference_checkpoint: `checkpoints/15x15_current_best.pt`
- epochs: 1
- lr: 5e-08
- margin: 1.0
- ce_weight: 0.0
- pair_weight: 0.0
- worst_weight: 0.0
- anchor_kl_weight: 0.0
- hard_guard_reference_kl_weight: 8.0
- hard_guard_target_ce_weight: 1.0
- hard_guard_beats_weight: 4.0
- hard_guard_beats_margin: 0.0

## Group metrics

| group | rows | top3 delta | top5 delta | top10 delta | rank_gt50 delta | mean_rank delta | target_prob delta | mean_worst_gap delta | hinge delta | beats_worst delta | beats_all delta |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| train_main_rank_11_50 | 7 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.00000000 | 0.000001 | -0.000001 | 0.000000 | 0.000000 |
| protected_eval_top10 | 15 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.00000062 | 0.000007 | -0.000004 | 0.000000 | 0.000000 |
| tail_eval_rank_gt50 | 3 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.00000000 | 0.000012 | -0.000010 | 0.000000 | 0.000000 |

## Final training terms

| term | value |
|---|---:|
| loss | 10.33517838 |
| ce_loss | 7.14386415 |
| pair_hinge_loss | 5.47290754 |
| worst_hinge_loss | 7.45749140 |
| anchor_kl | 0.00000000 |
| hard_guard_reference_kl | -0.00000001 |
| hard_guard_target_ce | 6.36630964 |
| hard_guard_beats_hinge | 0.99221706 |
| mean_gap | -4.41785383 |
| mean_worst_gap | -6.45749235 |

## Hard guard row verdicts

| case_id | role | pass | failure reasons | rank before→after | rank>50 before→after | beats-worst before→after | beats-all before→after |
|---|---|---:|---|---:|---:|---:|---:|
| legacy_g1_m40 | hard_protected_beats_guard | True |  | 3.0→3.0 | 0→0 | 0→0 | 0→0 |
| legacy_g1_m8 | hard_rank_le50_preservation_guard | False | rank_after=102.0 > 50.0 | 102.0→102.0 | 1→1 | 0→0 | 0→0 |

## Verdict

FAIL_HARD_GUARD_ROW_DAMAGE

## Decision

No checkpoint was saved.
If the no-save probe fails, the next step should be another objective/data design change, not a saved run.
