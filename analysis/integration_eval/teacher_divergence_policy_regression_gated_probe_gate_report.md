# Teacher-divergence regression-gated policy probe report

## Scope

This runner trains/evaluates the anchored policy probe in no-save mode first, applies regression gates, and saves a checkpoint only if gates pass and `--save-on-pass` is set.

It does not export C weights, run benchmarks, promote a model, overwrite current-best, or make a model-capacity conclusion.

## Probe config

- anchor_script: `scripts/train_teacher_divergence_policy_anchor_probe.py`
- epochs: 80
- lr: 3e-05
- kl_weight: 0.35
- anchor_kl_splits: `train_candidate,train_teacher_divergence`
- train_scope: `policy_head`
- eval_csv: `analysis/integration_eval/teacher_divergence_policy_regression_gated_probe_eval.csv`
- train_report: `analysis/integration_eval/teacher_divergence_policy_regression_gated_probe_train_report.md`
- out_checkpoint: `checkpoints/15x15_teacher_divergence_policy_regression_gated_probe.pt`
- save_on_pass: True
- saved_checkpoint: False

## Gate thresholds

- min train_candidate rank improved: 8
- min train_candidate probability improved: 8
- max train_candidate probability regressed: 0
- max train_teacher_divergence probability regressed: 10
- max train_teacher_divergence rank regressed: 5
- max heldout_retention probability regressed: 4
- max heldout_retention rank regressed: 3
- allow heldout top-1 loss: False

## Decision

- decision: **FAIL**
- failure_count: 4

Failures:

- train_teacher_divergence prob_regressed 15 > 10
- train_teacher_divergence rank_regressed 6 > 5
- heldout_retention prob_regressed 7 > 4
- heldout_retention rank_regressed 4 > 3

## Split summary

| split | rows | rank improved/same/regressed | prob improved/same/regressed | top1 before->after | mean rank before->after | mean prob before->after |
|---|---:|---:|---:|---:|---:|---:|
| train_candidate | 8 | 8/0/0 | 8/0/0 | 0->0 | 30.75->16.00 | 0.016975->0.088470 |
| train_teacher_divergence | 25 | 8/11/6 | 10/0/15 | 0->0 | 17.32->15.76 | 0.025559->0.024962 |
| heldout_retention | 11 | 2/5/4 | 4/0/7 | 3->4 | 21.82->21.27 | 0.163256->0.191187 |

## Boundary

Failing gates means no checkpoint should be saved for this configuration and no export/benchmark/promotion should be run.
