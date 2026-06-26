# Expanded b6c64 benchmark-preserving adapter closeout

- decision: `CLOSEOUT_NO_SAVED_CANDIDATE_TOP3_WARNING`
- promotion_readiness: `NOT_PROMOTION_READY`
- saved adapter candidate: `False`
- C export after adapter: `False`
- public benchmark after adapter: `False`
- promotion/current_best overwrite: `False`

## Baseline correction

| baseline | score | role |
|---|---:|---|
| archived current-best | 7.0/24 | aspirational recovery target |
| current local b6c64 baseline | 2.0/24 | reproducible local no-regression gate |
| expanded public candidate | 2.0/24 | actual candidate public benchmark result |

The current local b6c64 runner does not reproduce the archived `7.0/24` current-best score. The reproducible local b6c64 baseline is `2.0/24`, and the expanded public candidate also scored `2.0/24`.

## Training input dry-run

| group | count |
|---|---:|
| teacher-divergence CE rows | 12 |
| selected public tactical_mid KL anchors | 48 |
| protected KL guard rows | 15 |
| tail KL guard rows | 15 |
| total training records | 90 |
| diagnostic-only records | 192 |

## No-save sweep result

| metric | value |
|---|---:|
| configs tested | 5 |
| hard pass configs | 0 |
| soft pass configs | 5 |
| fail configs | 0 |
| observed top3 deltas | `[-1]` |
| observed rank>50 deltas | `[0]` |
| mean_rank delta range | -4.000 to -4.000 |
| target_prob delta range | 0.00004488 to 0.00004553 |

All tested configs were soft passes only. They improved broad metrics but retained `top3_delta = -1`, so this route does not qualify for saved candidate creation.

## Decision

Do **not** create a saved adapter candidate from this route.

Reasons:

- No no-save config achieved `PASS_HARD_NO_SAVE`.
- Every no-save config retained top3 regression.
- Current local b6c64 baseline is only `2.0/24`, so public-benchmark recovery remains unresolved.
- The archived `7.0/24` current-best score is not currently reproduced by the local b6c64 runner.

## Recommended next route

Either:

1. Add targeted positive supervision for the top3-sensitive teacher-divergence row and repeat no-save only; or
2. Audit/recover the archived current-best runner that produced `7.0/24`, then restart benchmark-preserving training from that reproducible baseline.

No checkpoint, C export, public benchmark, promotion, or current-best overwrite should be performed from this soft-pass-only adapter route.
