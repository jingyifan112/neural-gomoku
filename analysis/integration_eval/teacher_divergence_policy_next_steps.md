# Teacher-divergence policy next steps

## Current branch status

This branch completed the teacher-divergence retention data build and a sequence of policy-focused probes.

The committed artifacts show:

- clean teacher-divergence retention dataset built
- safety-block teacher-divergence dataset built
- unanchored policy probe completed
- anchored policy probe completed
- e40/kl0.75 parameter variant completed as a negative variant
- fixed regression gates applied across all probe CSVs

## Current decision

No existing probe should be exported, benchmarked, promoted, or used as a current-best replacement.

Reason:

- all evaluated probes fail the policy probe regression gates
- train_candidate rows show policy signal
- broader teacher-divergence and heldout-retention side effects remain too large

## Best failed baseline

The best failed baseline is:

- `anchored_e80_kl035`

Reason:

- keeps train_candidate rank/probability movement at 8/8
- reduces train_teacher_divergence regressions relative to the unanchored probe
- still fails regression gates, especially on teacher-divergence and heldout-retention regressions

## What not to do next

Do not continue by blindly sweeping:

- epoch count
- KL weight
- learning rate

The e40/kl0.75 no-save variant showed that simply increasing KL weight and reducing epochs did not improve the tradeoff.

## Recommended next direction

The next training design should be regression-gated before checkpoint saving.

Recommended properties:

- keep heldout_retention strictly evaluation-only
- train CE on train_candidate rows
- add KL anchor on train_candidate and train_teacher_divergence rows
- optionally add low-weight CE anchors on selected train_teacher_divergence rows
- compute before/after split metrics before saving
- save checkpoint only if all gates pass

Minimum gates should include:

- train_candidate rank_improved == 8
- train_candidate prob_improved == 8
- train_candidate prob_regressed == 0
- train_teacher_divergence prob_regressed <= 10
- train_teacher_divergence rank_regressed <= 5
- heldout_retention prob_regressed <= 4
- heldout_retention rank_regressed <= 3
- heldout_retention top1 must not decrease

## Boundary

The next stage is still research/probe work.

It should not perform:

- C export
- public benchmark
- promotion
- current-best overwrite
- capacity conclusion

until a probe passes the regression gates.
