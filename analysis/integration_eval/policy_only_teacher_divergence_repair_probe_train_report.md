# Policy-only teacher-divergence repair probe training report

## Scope

- Branch: exp/15x15-policy-only-teacher-divergence-repair-train
- Dataset: analysis/public_benchmark_eval/rapfi_teacher_policy_margin_dataset_corpus8_selected.json
- Init/reference checkpoint: checkpoints/15x15_current_best.pt
- Output checkpoint: checkpoints/15x15_policy_only_teacher_divergence_repair_probe.pt
- Objective: policy-head-only pairwise margin with --ce-weight 0
- Non-goals: no value regression, no C export, no public benchmark, no promotion

## Training loss

| metric | first | last | delta |
|---|---:|---:|---:|
| loss | 5.958885 | 5.813773 | -0.145112 |
| margin_loss | 5.958885 | 5.813749 | -0.145136 |
| anchor_kl | 0.000000 | 0.000485 | 0.000485 |
| ce | 5.455975 | 5.329073 | -0.126902 |

## BEFORE to AFTER policy-gate summary

| metric | count/value |
|---|---:|
| cases parsed | 25 |
| target prob improved | 24 / 25 |
| suppress prob decreased | 24 / 25 |
| target rank improved | 8 / 25 |
| target rank regressed | 0 / 25 |
| target-vs-suppress logit gap improved | 24 / 25 |
| mean delta target prob | 0.00238099 |
| mean delta suppress prob | -0.00923236 |
| mean delta gap | 0.148287 |
| min delta gap | -0.032483 |
| max delta gap | 0.215282 |

## Largest gap improvements

| case_id | before_gap | after_gap | delta_gap | before_rank | after_rank |
|---|---:|---:|---:|---:|---:|
| legacy_g3_m24 | -5.701507 | -5.486225 | 0.215282 | 7 | 7 |
| legacy_g5_m14 | -5.492826 | -5.304506 | 0.188320 | 17 | 15 |
| legacy_g3_m26 | -5.395764 | -5.212775 | 0.182989 | 5 | 4 |
| legacy_g1_m8 | -7.888449 | -7.708438 | 0.180011 | 102 | 101 |
| legacy_g2_m11 | -7.170754 | -6.990972 | 0.179782 | 12 | 12 |
| legacy_g4_m17 | -5.318236 | -5.146485 | 0.171751 | 4 | 4 |
| legacy_g2_m21 | -8.742455 | -8.571234 | 0.171221 | 47 | 44 |
| legacy_g4_m23 | -5.669407 | -5.500234 | 0.169173 | 23 | 21 |
| legacy_g5_m16 | -1.550739 | -1.385647 | 0.165092 | 2 | 2 |
| legacy_g4_m13 | -7.601815 | -7.439025 | 0.162790 | 21 | 19 |

## Regressed or non-improved cases

| case_id | delta_prob | delta_gap | before_rank | after_rank | note |
|---|---:|---:|---:|---:|---|
| legacy_g6_m19 | -0.00045912 | -0.032483 | 7 | 7 | target_prob_not_improved, gap_not_improved |

## Interpretation

The probe moved the supervised pairwise margin in the intended direction on the training rows, but this remains a local policy-head-only probe. It is not a promoted candidate and should not be exported to C or evaluated on the public benchmark from this branch step.
