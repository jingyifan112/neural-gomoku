# Teacher-divergence mixed-CE anchor probe closeout

## Scope

This closeout records the first mixed low-weight CE anchor probe under the regression-gated policy runner.

This was a gated probe only:

- no checkpoint saved
- no C export
- no benchmark
- no promotion
- no current-best overwrite
- no model-capacity conclusion

## Configuration

Training script:

- `scripts/train_teacher_divergence_policy_mixed_ce_anchor_probe.py`

Gated outputs:

- eval CSV: `analysis/integration_eval/teacher_divergence_policy_mixed_ce_anchor_probe_gated_eval.csv`
- train report: `analysis/integration_eval/teacher_divergence_policy_mixed_ce_anchor_probe_gated_train_report.md`
- gate report: `analysis/integration_eval/teacher_divergence_policy_mixed_ce_anchor_probe_gated_gate_report.md`

Loss design:

- main CE: `train_candidate`
- mixed low-weight CE: `train_teacher_divergence`
- mixed CE weight scale: 0.10
- KL anchor: `train_candidate,train_teacher_divergence`
- heldout_retention: evaluation-only

## Result

Gate decision:

- FAIL
- saved_checkpoint: False

Failure reasons:

- heldout_retention prob_regressed 6 > 4
- heldout_retention rank_regressed 4 > 3

Split effects:

### train_candidate

- rank improved: 8/8
- probability improved: 8/8
- top-1: 0 -> 0

Interpretation: candidate signal was preserved.

### train_teacher_divergence

- rank improved/same/regressed: 20/5/0
- probability improved/same/regressed: 23/0/2
- top-1: 0 -> 1
- mean rank: 17.32 -> 8.00
- mean target probability: 0.025559 -> 0.069953

Interpretation: mixed CE strongly improved teacher-divergence retention/control compared with the previous anchored-only probe.

### heldout_retention

- rank improved/same/regressed: 3/4/4
- probability improved/same/regressed: 5/0/6
- top-1: 3 -> 4
- mean rank: 21.82 -> 20.55
- mean target probability: 0.163256 -> 0.243324

Interpretation: heldout mean metrics improved, but row-level regressions still exceeded gates. The configuration is not safe for checkpoint saving.

## Decision

Close as: promising but gate-failed mixed CE probe.

Mixed low-weight CE anchors are a better direction than pure KL anchoring, but this specific 0.10 weight-scale configuration still fails heldout-retention gates.

No checkpoint should be saved from this configuration.

## Recommended next step

Try lower mixed CE weight scales under the same regression-gated runner, for example:

- 0.05
- 0.025

The goal is to preserve the teacher-divergence improvement while reducing heldout-retention row-level regressions.

Any future configuration must still pass gates before saving a checkpoint.
