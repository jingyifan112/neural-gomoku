# b4c64 hard guard tensor/gradient semantics audit v2

## Scope

- Corrected audit under `set_policy_head_training_mode(model)`.
- Audit only.
- No checkpoint save, C export, public benchmark, promotion, or current-best overwrite was performed.

## Loss terms

- `loss`: `10.33517837524414`
- `reference_kl_masked_softmax`: `-8.046946220474638e-09`
- `reference_kl_from_log`: `0.0`
- `target_ce`: `6.366309642791748`
- `beats_hinge`: `0.9922170639038086`
- `kl_inconsistency_abs`: `8.046946220474638e-09`

## Key audit findings

- `masked_softmax_kl_nonzero_with_identical_models`: `False`
- `masked_log_softmax_kl_nonzero_with_identical_models`: `False`
- `any_target_grad_wrong_sign_for_ce_increase`: `False`
- `any_rank_regressed_after_one_step`: `False`
- `any_target_prob_decreased_after_one_step`: `False`

## Gradient rows

| case_id | role | target rc | target grad | expected target-logit step | grad sign ok | worst gap before | CE | KL masked_softmax | KL from log | worst hinge |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `legacy_g1_m40` | `hard_protected_beats_guard` | `6,12` | -4.282991409301758 | 2.1414957046508787e-07 | True | -0.9922170639038086 | 1.8951802253723145 | -2.4161739275996297e-08 | 0.0 | 0.9922170639038086 |
| `legacy_g1_m8` | `hard_rank_le50_preservation_guard` | `5,8` | -0.6668320894241333 | 3.3341604471206666e-08 | True | -7.888444900512695 | 8.59897518157959 | 0.0 | 0.0 | 7.888444900512695 |

## One-step compare

| case_id | rank before→after | target prob delta | target logit delta | worst gap delta |
|---|---:|---:|---:|---:|
| `legacy_g1_m40` | 3→3 | 5.4389238357543945e-06 | 1.52587890625e-05 | 4.291534423828125e-05 |
| `legacy_g1_m8` | 102→102 | 6.3300831243395805e-09 | 1.1444091796875e-05 | 3.528594970703125e-05 |

## Decision

- Gradient signs and one-step behavior are safe under policy-head mode.
- The earlier hardguard-only failure likely comes from wrapper train/eval sequencing or post-update diagnostics mode; patch wrapper to force policy-head mode before after-diagnostics.

## Outputs

- `analysis/integration_eval/rank_topk_nosave_b4c64_hardguard_gradient_semantics_audit_v2/audit.log`
- `analysis/integration_eval/rank_topk_nosave_b4c64_hardguard_gradient_semantics_audit_v2/hardguard_gradient_rows.csv`
- `analysis/integration_eval/rank_topk_nosave_b4c64_hardguard_gradient_semantics_audit_v2/hardguard_gradient_semantics_v2_report.md`
- `analysis/integration_eval/rank_topk_nosave_b4c64_hardguard_gradient_semantics_audit_v2/hardguard_gradient_semantics_v2_summary.json`
- `analysis/integration_eval/rank_topk_nosave_b4c64_hardguard_gradient_semantics_audit_v2/hardguard_one_step_compare.csv`
