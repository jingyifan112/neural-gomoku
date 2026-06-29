# b4c64 hard guard tensor/gradient semantics audit

## Scope

- Audit only.
- No checkpoint save, C export, public benchmark, promotion, or current-best overwrite was performed.

## Loss terms

- `loss`: `9.376431465148926`
- `reference_kl_masked_softmax`: `0.03889548033475876`
- `reference_kl_from_log`: `0.038895487785339355`
- `target_ce`: `5.940214157104492`
- `beats_hinge`: `0.7812633514404297`
- `kl_inconsistency_abs`: `7.450580596923828e-09`

## Key audit findings

- `masked_softmax_kl_nonzero_with_identical_models`: `True`
- `masked_log_softmax_kl_nonzero_with_identical_models`: `True`
- `any_target_grad_wrong_sign_for_ce_increase`: `False`
- `any_rank_regressed_after_one_step`: `False`
- `any_target_prob_decreased_after_one_step`: `False`

## Gradient rows

| case_id | role | target rc | target grad | expected target-logit step | grad sign ok | worst gap before | CE | KL masked_softmax | KL from log | worst hinge |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `legacy_g1_m40` | `hard_protected_beats_guard` | `6,12` | -4.203183174133301 | 2.1015915870666502e-07 | True | -0.7812633514404297 | 1.73207426071167 | 0.027214325964450836 | 0.027214350178837776 | 0.7812633514404297 |
| `legacy_g1_m8` | `hard_rank_le50_preservation_guard` | `5,8` | -0.6660066843032837 | 3.3300334215164184e-08 | True | -7.366641044616699 | 8.041555404663086 | 0.04472848400473595 | 0.04472848400473595 | 7.366641044616699 |

## One-step compare

| case_id | rank before→after | target prob delta | target logit delta | worst gap delta |
|---|---:|---:|---:|---:|
| `legacy_g1_m40` | 3→3 | 0.00027066469192504883 | 0.0012445449829101562 | 0.0025987625122070312 |
| `legacy_g1_m8` | 73→73 | 1.4519901014864445e-07 | 0.000263214111328125 | 0.0005893707275390625 |

## Decision

- The reference KL path is suspect: `masked_softmax` KL is non-zero even when model and reference checkpoints are identical.
- Next patch should replace KL reference probabilities with `masked_log_softmax(...).exp()` or otherwise make masked probability semantics consistent.

## Outputs

- `analysis/integration_eval/rank_topk_nosave_b4c64_hardguard_gradient_semantics_audit/audit.log`
- `analysis/integration_eval/rank_topk_nosave_b4c64_hardguard_gradient_semantics_audit/hardguard_gradient_rows.csv`
- `analysis/integration_eval/rank_topk_nosave_b4c64_hardguard_gradient_semantics_audit/hardguard_gradient_semantics_report.md`
- `analysis/integration_eval/rank_topk_nosave_b4c64_hardguard_gradient_semantics_audit/hardguard_gradient_semantics_summary.json`
- `analysis/integration_eval/rank_topk_nosave_b4c64_hardguard_gradient_semantics_audit/hardguard_one_step_compare.csv`
