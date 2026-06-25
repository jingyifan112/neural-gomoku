# Teacher-divergence final model scoring report

## Scope

- Final scoring report only.
- No training is run by this report.
- No checkpoint is saved.
- No C export, no public benchmark, no promotion.

## Final decision

- decision: `PROJECT_EVIDENCE_COMPLETE_MODEL_NOT_GATE_PASS`
- promotion readiness: `NOT_PROMOTION_READY`
- gate score: `55/100`

## Capacity model

- model label: `current increased-capacity b4c64 model`
- checkpoint: `checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt`
- architecture: board-size 15, channels 64, blocks 4, win-length 5

## Data expansion evidence

- data expansion pass: `True`
- dataset: `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_conservative_plus_generated_tail_guards_plus_generated_train_candidates_dryrun.json`

| group | count | evidence |
|---|---:|---|
| samples | 12 | 4 original + 8 generated train candidates |
| protected_eval_samples | 15 | unchanged guard set |
| tail_eval_samples | 15 | 3 original + 12 generated tail guards |
| quarantine_samples | 3 | unchanged quarantine set |

- train generation decision: `TRAIN_CANDIDATE_GENERATION_PARTIAL`
- train materialization decision: `GENERATED_TRAIN_CANDIDATE_MATERIALIZATION_DRYRUN_TARGET_MET`
- tail materialization decision: `TAIL_GUARD_MATERIALIZATION_DRYRUN_TARGET_MET`

## No-save gate score

| component | score | interpretation |
|---|---:|---|
| train signal | 40/40 | top10 improved; tail-count reduced inside train group; mean rank improved; target probability improved |
| protected guard | 15/30 | fail notes: target probability regressed; teacher-beats-worst regressed; teacher-beats-all regressed |
| tail guard | 0/30 | fail notes: tail rank>50 count increased; tail mean rank worsened; tail target probability regressed; tail hinge worsened |
| total | 55/100 | FAIL |

## Key no-save metrics

| group | rows | top10 delta | rank_gt50 delta | mean_rank delta | target_prob delta | hinge delta | beats_worst delta | beats_all delta |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| train_main_rank_11_50 | 12 | 1 | -1 | -1.33333 | 0.00126085 | -0.232748 | 0 | 0 |
| protected_eval_top10 | 15 | 0 | 0 | -0.133333 | -0.00861646 | -0.156378 | -1 | -1 |
| tail_eval_rank_gt50 | 15 | 0 | 3 | 15.6 | -7.8571e-06 | 0.161464 | 0 | 0 |

## Interpretation

- The data expansion objective is complete at dry-run/materialization level: train rows increased and tail guards increased while protected and quarantine groups remained separated.
- The no-save probe shows useful train-side signal: train top10 improves, train rank>50 count falls, mean rank improves, and target probability improves.
- The model is not gate-pass because protected teacher-beats metrics regress and the tail guard group worsens substantially.
- Therefore this route satisfies the capacity/data/scoring evidence requirement, but it does not authorize checkpoint-producing training, promotion, current_best overwrite, C export, or public benchmark.

## Source reports

- generated train materialization summary: `analysis/integration_eval/teacher_divergence_generated_train_candidate_materialization/generated_train_candidate_materialization_summary.json`
- generated train source summary: `analysis/integration_eval/teacher_divergence_train_candidate_generation/train_candidate_generation_summary.json`
- generated tail materialization summary: `analysis/integration_eval/teacher_divergence_tail_guard_materialization_dryrun/tail_guard_materialization_summary.json`
- b4c64 no-save csv: `analysis/integration_eval/b4c64_expanded_nosave_eval/b4c64_expanded_nosave_group_metrics.csv`
- b4c64 no-save report: `analysis/integration_eval/b4c64_expanded_nosave_eval/b4c64_expanded_nosave_report.md`

## Final note

This report is the final scoring artifact for the current route. It does not save a model and does not promote any checkpoint.
