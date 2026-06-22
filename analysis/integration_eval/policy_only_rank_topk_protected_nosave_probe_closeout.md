# Policy-only rank/top-k protected no-save probe closeout

## Branch

`exp/15x15-policy-only-rank-topk-protected-nosave-probe`

## Scope

This branch ran a protected no-save probe only.

- Optimizer ran in memory.
- No checkpoint was saved.
- No C export was run.
- No public benchmark was run.
- No promotion was considered.

## Setup

The protected dataset split was:

- train_main_rank_11_50: 7 rows
- protected_eval_top10: 15 rows
- tail_eval_rank_gt50: 3 rows

The probe trained only the 7 `rank 11-50` rows and evaluated all three groups.

Configuration:

- epochs: 3
- lr: 1e-6
- margin: 0.25
- ce_weight: 1.0
- pair_weight: 0.0
- worst_weight: 0.0
- anchor_kl_weight: 0.05
- checkpoint save: disabled

## Result

Verdict: **FAIL_NO_SAVE_PROBE**

| group | rows | top3_delta | top5_delta | top10_delta | rank_gt50_delta | mean_rank_delta | target_prob_delta | mean_worst_gap_delta | hinge_delta | beats_worst_delta | beats_all_delta |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| train_main_rank_11_50 | 7 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | -1.857143 | 0.00049504 | 0.041463 | -0.238577 | 0.000000 | 0.000000 |
| protected_eval_top10 | 15 | 0.000000 | 0.000000 | 1.000000 | 0.000000 | -0.466667 | -0.01282100 | 0.735103 | -0.185786 | -1.000000 | -1.000000 |
| tail_eval_rank_gt50 | 3 | 0.000000 | 0.000000 | 0.000000 | 1.000000 | 37.333333 | -0.00009595 | 0.497262 | 0.558160 | 0.000000 | 0.000000 |

## Interpretation

The protected split partially improved the intended training group:

- train_main mean_rank improved by 1.857;
- train_main target probability improved slightly;
- train_main mean worst gap improved slightly;
- train_main hinge improved.

However, the evaluation-only groups were not protected:

- protected top10 target probability dropped by about 0.0128;
- protected top10 lost teacher_beats_worst and teacher_beats_all rows;
- tail rank_gt50 worsened by 1 row;
- tail mean_rank worsened sharply by 37.33;
- tail hinge worsened.

This means training only the rank 11-50 subset is not sufficient. Even a tiny CE-only policy-head update can damage held-out rank buckets.

## Decision

Reject this protected no-save probe.

Do not save a checkpoint.

Do not run gate evaluation from a saved checkpoint.

Do not export.

Do not run public benchmark.

Do not promote.

## Current overall conclusion

The policy-only rank/top-k chain has now failed three increasingly conservative attempts:

1. run1 full dataset saved-local gate: failed candidate gate.
2. run2 full dataset no-save ablations: failed; CE-only and weak-suppress both unstable.
3. protected no-save probe: failed; train group improved slightly but protected/tail groups regressed.

The current evidence suggests that policy-head-only rank/top-k repair on this 25-row dataset is too unstable to promote.

## Recommended next direction

Do not continue by tuning learning rate, epochs, or suppress weights on the same setup.

Recommended next branch:

`exp/15x15-policy-only-rank-topk-chain-closeout`

Purpose:

- summarize the full policy-only rank/top-k chain;
- document why no checkpoint should be exported or benchmarked;
- recommend returning to broader data construction or a non-policy-only strategy.

Possible next research directions:

1. Expand teacher-divergence data before training again.
2. Separate high-rank tail rows into a diagnostic-only bucket.
3. Add stronger anchor/evaluation gates before optimizer steps, not only after training.
4. Consider value/policy joint diagnostics instead of policy-head-only repair.
5. Revisit model capacity and public benchmark score gap rather than forcing local policy repair.

