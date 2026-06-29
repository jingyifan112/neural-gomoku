# b4c64 guarded split v2 policy fix

## Scope

- Guarded split metadata/policy fix only.
- No training, checkpoint save, C export, public benchmark, promotion, or current-best overwrite was performed.

## Rationale

- `legacy_g1_m8` is already rank>50 under eval-consistent diagnostics after the diagnostics mode fix.
- Therefore `rank_after_max <= 50` is a repair objective, not a preservation guard.
- v2 changes this row to no-further-damage preservation.

## Changed gate

| case_id | old gate | new gate |
|---|---|---|
| `legacy_g1_m8` | `{"rank_after_max": 50, "rank_delta_max": 0, "rank_gt50_delta_max": 0, "target_prob_delta_min": 0}` | `{"rank_delta_max": 0, "rank_gt50_delta_max": 0, "target_prob_delta_min": 0}` |

## Hard guard manifest

| case_id | v1 role | v2 role | policy fix | effective gate | previous gate stored |
|---|---|---|---:|---|---|
| `legacy_g1_m40` | `hard_protected_beats_guard` | `` | `False` | `{"rank_delta_max": 0, "target_prob_delta_min": -0.02, "teacher_beats_all_delta_min": 0, "teacher_beats_worst_delta_min": 0}` | `{}` |
| `legacy_g1_m8` | `hard_rank_le50_preservation_guard` | `hard_rank_no_further_damage_guard` | `True` | `{"rank_delta_max": 0, "rank_gt50_delta_max": 0, "target_prob_delta_min": 0}` | `{"rank_after_max": 50, "rank_delta_max": 0, "rank_gt50_delta_max": 0, "target_prob_delta_min": 0}` |

## Decision

- Next step: rerun hardguard-only sanity no-save probe using `guarded_split_v2`.

## Outputs

- `analysis/integration_eval/rank_topk_nosave_b4c64_guarded_split_v2_policy_fix/guarded_split_v2_manifest.csv`
- `analysis/integration_eval/rank_topk_nosave_b4c64_guarded_split_v2_policy_fix/guarded_split_v2_summary.json`
- `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_guarded_split_v2.json`
