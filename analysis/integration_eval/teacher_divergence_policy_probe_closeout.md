# Teacher-divergence policy probe closeout

## Scope

This closeout records the result of the small teacher-divergence policy probe.

This was a signal probe only:

- no C export
- no benchmark
- no promotion
- no current-best overwrite
- no model-capacity conclusion

## Inputs

- Dataset: `analysis/integration_eval/teacher_divergence_retention_safety_v3_dataset.json`
- Training script: `scripts/train_teacher_divergence_policy_probe.py`
- Eval CSV: `analysis/integration_eval/teacher_divergence_policy_probe_eval.csv`
- Report: `analysis/integration_eval/teacher_divergence_policy_probe_report.md`
- Base checkpoint: `checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt`
- Local-only ignored probe checkpoint: `checkpoints/15x15_teacher_divergence_policy_probe.pt`

## Dataset split

- total rows: 44
- train_candidate: 8
- train_teacher_divergence: 25
- heldout_retention: 11

The probe trained only `split == train_candidate`.

## Result summary

### train_candidate

- rows: 8
- rank improved: 8
- probability improved: 8
- target top-1 before: 0
- target top-1 after: 0

Interpretation: the accepted 8-row candidate subset has a real policy signal, but the signal is weak. It moved target moves upward but did not make any target become the direct policy top move.

### train_teacher_divergence

- rows: 25
- rank improved: 7
- rank same: 10
- rank regressed: 8
- probability improved: 6
- probability regressed: 19
- target top-1 after: 0

Interpretation: the probe created mixed side effects on the broader teacher-divergence set. The probability regression count is too high to treat this as a safe candidate.

### heldout_retention

- rows: 11
- rank improved: 2
- rank same: 6
- rank regressed: 3
- probability improved: 4
- probability regressed: 7
- target top-1 before: 3
- target top-1 after: 4

Interpretation: heldout retention did not catastrophically fail, but it showed enough probability regression that this probe should not be promoted.

## Decision

Close as: policy signal observed, not promotion-ready.

The result supports continuing with more conservative policy-focused training design, but does not justify:

- C export
- benchmark run
- promotion
- current-best replacement
- capacity conclusion

## Recommended next step

Design the next probe around stronger retention constraints before training, for example:

- lower learning rate or fewer epochs
- stronger KL anchor
- include train_teacher_divergence rows as retention/anchor rows instead of only evaluating them
- keep heldout_retention strictly held out
- continue reporting target rank, target probability, top-1 match, and retention side effects
