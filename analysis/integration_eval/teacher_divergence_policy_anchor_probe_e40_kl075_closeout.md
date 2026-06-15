# Teacher-divergence anchored policy probe e40 kl0.75 closeout

## Scope

This closeout records a no-save parameter variant of the anchored teacher-divergence policy probe.

This was a signal probe only:

- no checkpoint saved
- no C export
- no benchmark
- no promotion
- no current-best overwrite
- no model-capacity conclusion

## Variant

Compared with the committed anchored probe:

- previous anchored probe: 80 epochs, KL weight 0.35
- this variant: 40 epochs, KL weight 0.75

Loss design stayed the same:

- CE target loss used only `split == train_candidate`
- KL anchor used `train_candidate` and `train_teacher_divergence`
- `heldout_retention` stayed evaluation-only

## Result comparison

### Previous anchored probe: e80 kl0.35

- train_candidate: rank improved 8/8, probability improved 8/8
- train_teacher_divergence: probability regressed 15/25
- heldout_retention: probability regressed 7/11
- heldout_retention top-1: 3 -> 4

### This variant: e40 kl0.75

- train_candidate: rank improved 8/8, probability improved 6/8, probability regressed 2/8
- train_teacher_divergence: probability regressed 18/25
- heldout_retention: probability regressed 7/11
- heldout_retention top-1: 3 -> 3

## Decision

Close as: negative parameter variant.

Increasing KL weight while reducing epochs did not improve the tradeoff. It weakened the candidate-row probability signal and increased broader teacher-divergence probability regressions.

This variant should not be used for:

- C export
- benchmark
- promotion
- current-best replacement
- capacity conclusion

## Recommended next step

Do not continue with the e40/kl0.75 direction.

A better next probe should use explicit regression gates or mixed low-weight CE anchors, rather than only increasing KL weight. Candidate directions:

- keep the anchored e80/kl0.35 result as the better baseline
- add pre-save gates for train_teacher_divergence and heldout_retention regressions
- try low-weight CE on selected train_teacher_divergence rows
- keep heldout_retention strictly evaluation-only
