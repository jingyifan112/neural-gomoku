# Teacher-divergence mixed-CE anchor probe scale sweep closeout

## Scope

This closeout records the corrected mixed-CE anchor weight-scale sweep under the regression-gated policy runner.

This was a gated probe only:

- no checkpoint saved
- no C export
- no benchmark
- no promotion
- no current-best overwrite
- no model-capacity conclusion

## Implementation correction

The initial mixed-CE implementation scaled per-row weights inside a normalized weighted CE term. That made the scale cancel out between numerator and denominator.

The corrected implementation computes:

- unscaled mixed CE over selected anchor rows
- scaled mixed CE as `mixed_ce_anchor_weight_scale * mixed_ce_unscaled_loss`
- final CE loss as `main_ce_loss + mixed_ce_loss`

The runner was also extended to pass mixed-CE parameters through to the anchor script:

- `--mixed-ce-anchor-splits`
- `--mixed-ce-anchor-label-types`
- `--mixed-ce-anchor-weight-scale`
- `--mixed-ce-anchor-max-rows`

## Configurations

All runs used:

- main CE: `train_candidate`
- mixed CE split: `train_teacher_divergence`
- KL anchor splits: `train_candidate,train_teacher_divergence`
- train scope: `policy_head`
- epochs: 80
- lr: 3e-05
- kl_weight: 0.35
- heldout_retention: evaluation-only

Swept mixed CE scales:

- 0.10
- 0.05
- 0.025

## Corrected results

### Scale 0.10

Decision:

- FAIL
- saved_checkpoint: False

Failures:

- heldout_retention prob_regressed 6 > 4
- heldout_retention rank_regressed 4 > 3

Split effects:

- train_candidate: rank 8/0/0, prob 8/0/0
- train_teacher_divergence: rank 15/9/1, prob 18/0/7, top1 0 -> 1
- heldout_retention: rank 3/4/4, prob 5/0/6, top1 3 -> 4

### Scale 0.05

Decision:

- FAIL
- saved_checkpoint: False

Failures:

- heldout_retention prob_regressed 7 > 4
- heldout_retention rank_regressed 4 > 3

Split effects:

- train_candidate: rank 8/0/0, prob 8/0/0
- train_teacher_divergence: rank 14/9/2, prob 17/0/8, top1 0 -> 1
- heldout_retention: rank 3/4/4, prob 4/0/7, top1 3 -> 4

### Scale 0.025

Decision:

- FAIL
- saved_checkpoint: False

Failures:

- heldout_retention prob_regressed 7 > 4
- heldout_retention rank_regressed 4 > 3

Split effects:

- train_candidate: rank 8/0/0, prob 8/0/0
- train_teacher_divergence: rank 14/9/2, prob 17/0/8, top1 0 -> 0
- heldout_retention: rank 3/4/4, prob 4/0/7, top1 3 -> 4

## Interpretation

The corrected scale sweep shows that mixed CE anchors do help the teacher-divergence split, especially at scale 0.10, but they still fail heldout-retention gates.

Lowering the scale from 0.10 to 0.05 or 0.025 did not repair heldout-retention regressions and weakened the teacher-divergence improvement.

The best corrected configuration in this sweep is scale 0.10, but it is still gate-failed and must not be saved or promoted.

## Decision

Close this step as: corrected mixed-CE scale sweep failed gates.

No checkpoint should be saved from these configurations.

## Recommended next step

Do not continue simple global scale tuning on the same loss.

The next safer direction is to change the mixed-CE selection, not just its scalar weight. Candidate follow-ups:

- mixed CE only on higher-confidence teacher labels
- mixed CE only on safety-block teacher labels
- per-row regression audit to identify which heldout rows regress repeatedly
- add heldout-style anchors only if they are explicitly moved out of heldout and into a new training split

Any future configuration must still pass regression gates before saving a checkpoint.
