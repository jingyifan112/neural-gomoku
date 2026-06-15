# Teacher-divergence policy probe gate report

## Scope

This report applies fixed regression gates to existing teacher-divergence policy probe CSVs.

It does not train, save checkpoints, export C weights, run benchmarks, promote a model, or make a capacity conclusion.

## Gate thresholds

- min train_candidate rank improved: 8
- min train_candidate probability improved: 8
- max train_candidate probability regressed: 0
- max train_teacher_divergence probability regressed: 10
- max train_teacher_divergence rank regressed: 5
- max heldout_retention probability regressed: 4
- max heldout_retention rank regressed: 3
- allow heldout top-1 loss: False

## Probe decisions

| probe | decision | failure count | failures |
|---|---|---:|---|
| `unanchored_e80_kl025` | FAIL | 3 | train_teacher_divergence prob_regressed 19 > 10<br>train_teacher_divergence rank_regressed 8 > 5<br>heldout_retention prob_regressed 7 > 4 |
| `anchored_e80_kl035` | FAIL | 4 | train_teacher_divergence prob_regressed 15 > 10<br>train_teacher_divergence rank_regressed 6 > 5<br>heldout_retention prob_regressed 7 > 4<br>heldout_retention rank_regressed 4 > 3 |
| `anchored_e40_kl075` | FAIL | 4 | train_candidate prob_improved 6 < 8<br>train_candidate prob_regressed 2 > 0<br>train_teacher_divergence prob_regressed 18 > 10<br>heldout_retention prob_regressed 7 > 4 |

## Split summary

| probe | split | rows | rank improved/same/regressed | prob improved/same/regressed | top1 before->after | mean rank before->after | mean prob before->after |
|---|---|---:|---:|---:|---:|---:|---:|
| `unanchored_e80_kl025` | train_candidate | 8 | 8/0/0 | 8/0/0 | 0->0 | 30.75->15.88 | 0.016975->0.087917 |
| `unanchored_e80_kl025` | train_teacher_divergence | 25 | 7/10/8 | 6/0/19 | 0->0 | 17.32->14.68 | 0.025559->0.023285 |
| `unanchored_e80_kl025` | heldout_retention | 11 | 2/6/3 | 4/0/7 | 3->4 | 21.82->21.45 | 0.163256->0.192500 |
| `anchored_e80_kl035` | train_candidate | 8 | 8/0/0 | 8/0/0 | 0->0 | 30.75->16.00 | 0.016975->0.088470 |
| `anchored_e80_kl035` | train_teacher_divergence | 25 | 8/11/6 | 10/0/15 | 0->0 | 17.32->15.76 | 0.025559->0.024962 |
| `anchored_e80_kl035` | heldout_retention | 11 | 2/5/4 | 4/0/7 | 3->4 | 21.82->21.27 | 0.163256->0.191187 |
| `anchored_e40_kl075` | train_candidate | 8 | 8/0/0 | 6/0/2 | 0->0 | 30.75->23.12 | 0.016975->0.040258 |
| `anchored_e40_kl075` | train_teacher_divergence | 25 | 8/12/5 | 7/0/18 | 0->0 | 17.32->16.60 | 0.025559->0.024789 |
| `anchored_e40_kl075` | heldout_retention | 11 | 2/6/3 | 4/0/7 | 3->3 | 21.82->21.09 | 0.163256->0.189584 |

## Decision

All evaluated probes fail the regression gates.

The anchored e80/kl0.35 probe remains the best failed baseline because it keeps train_candidate rank/probability movement at 8/8 while reducing train_teacher_divergence regressions versus the unanchored probe.

No existing probe should be exported, benchmarked, promoted, or used for a capacity conclusion.

## Recommended next step

Do not continue blindly sweeping KL weight and epoch count. The next probe should add explicit regression gates before checkpoint saving and should explore mixed low-weight CE anchors on selected train_teacher_divergence rows while keeping heldout_retention evaluation-only.
