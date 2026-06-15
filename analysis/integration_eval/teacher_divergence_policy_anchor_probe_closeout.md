# Teacher-divergence anchored policy probe closeout

## Scope

This closeout records the result of the anchored teacher-divergence policy probe.

This was a signal probe only:

- no C export
- no benchmark
- no promotion
- no current-best overwrite
- no model-capacity conclusion

## Inputs

- Dataset: `analysis/integration_eval/teacher_divergence_retention_safety_v3_dataset.json`
- Training script: `scripts/train_teacher_divergence_policy_anchor_probe.py`
- Eval CSV: `analysis/integration_eval/teacher_divergence_policy_anchor_probe_eval.csv`
- Report: `analysis/integration_eval/teacher_divergence_policy_anchor_probe_report.md`
- Base checkpoint: `checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt`
- Local-only ignored probe checkpoint: `checkpoints/15x15_teacher_divergence_policy_anchor_probe.pt`

## Loss design

Cross-entropy target loss:

- used only `split == train_candidate`
- rows: 8

KL anchor loss:

- used `split == train_candidate`
- used `split == train_teacher_divergence`
- rows: 33 total

Heldout retention:

- `split == heldout_retention`
- rows: 11
- evaluation-only
- not used in the loss

## Result summary

### train_candidate

- rows: 8
- rank improved: 8
- probability improved: 8
- target top-1 before: 0
- target top-1 after: 0

Interpretation: the candidate rows again show a clear policy signal. However, no target became the top direct-policy move.

### train_teacher_divergence

- rows: 25
- rank improved: 8
- rank same: 11
- rank regressed: 6
- probability improved: 10
- probability regressed: 15
- target top-1 after: 0

Compared with the previous unanchored policy probe:

- probability regressions improved from 19/25 to 15/25
- rank regressions improved from 8/25 to 6/25

Interpretation: anchoring broader teacher-divergence rows helped reduce side effects, but the regression rate is still too high.

### heldout_retention

- rows: 11
- rank improved: 2
- rank same: 5
- rank regressed: 4
- probability improved: 4
- probability regressed: 7
- target top-1 before: 3
- target top-1 after: 4

Interpretation: heldout retention still shows notable probability regression. The probe is not safe for promotion.

## Decision

Close as: anchored policy signal observed, still not promotion-ready.

The anchored KL design improved side-effect control versus the unanchored probe, but not enough to justify:

- C export
- benchmark run
- promotion
- current-best replacement
- capacity conclusion

## Recommended next step

The next policy-focused probe should further reduce side effects before any export/benchmark work. Candidate options:

- increase KL weight further
- reduce epochs
- lower learning rate
- include selected teacher-divergence rows as mixed CE targets with lower weight
- keep heldout_retention strictly held out
- add explicit regression gates before saving a probe checkpoint
