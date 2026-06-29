# b4c64/current-best guard-aware objective wrapper v1 corrected

## Scope

- Branch: `exp/15x15-rank-topk-nosave-b4c64-guardaware-objective-wrapper-v1-corrected`
- Corrected wrapper patch only.
- No training, checkpoint save, C export, public benchmark, promotion, or current-best overwrite was performed.

## Correction

- Prior branch `exp/15x15-rank-topk-nosave-b4c64-guardaware-objective-wrapper-v1` did not patch the wrapper and should not be used for runs.
- This corrected branch patches the wrapper script itself and verifies the new CLI/help surfaces.

## Static checks

| check | value |
|---|---:|
| `contains_train_guardaware` | `True` |
| `contains_compute_guardaware_loss_terms` | `True` |
| `contains_make_hard_guard_beats_mask` | `True` |
| `contains_hard_guard_reference_kl_arg` | `True` |
| `contains_hard_guard_target_ce_arg` | `True` |
| `contains_hard_guard_beats_arg` | `True` |
| `help_contains_hard_guard_args` | `True` |
| `contains_torch_save` | `False` |
| `contains_out_checkpoint` | `False` |
| `call_path_uses_train_guardaware` | `True` |
| `call_path_still_uses_imported_train_directly` | `False` |

## Objective v1

- Added wrapper-local `train_guardaware()`.
- Main train loss uses weighted CE + pair hinge + worst hinge.
- Hard guards can use reference KL, target CE, and beats-worst hinge terms.
- Existing hard guard evaluator remains active and can return `FAIL_HARD_GUARD_ROW_DAMAGE`.

## Recommended first run

- epochs: `1`
- lr: `5e-8`
- ce/pair/worst: `0.5 / 0.5 / 0.25`
- anchor KL: `1.0`
- hard guard KL / CE / beats: `4.0 / 1.0 / 4.0`

## Outputs

- `analysis/integration_eval/rank_topk_nosave_b4c64_guardaware_objective_wrapper_v1_corrected/guardaware_objective_wrapper_v1_corrected_summary.json`
- `analysis/integration_eval/rank_topk_nosave_b4c64_guardaware_objective_wrapper_v1_corrected/wrapper_help_guardaware_v1_corrected.txt`
