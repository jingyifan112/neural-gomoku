# b4c64/current-best guard-aware objective wrapper v1

## Scope

- Branch: `exp/15x15-rank-topk-nosave-b4c64-guardaware-objective-wrapper-v1`
- Wrapper patch only.
- Added wrapper-local `train_guardaware()`; did not modify the shared rank/top-k trainer.
- No training, checkpoint save, C export, public benchmark, promotion, or current-best overwrite was performed.

## Static checks

| check | value |
|---|---:|
| `contains_train_guardaware` | `False` |
| `contains_compute_guardaware_loss_terms` | `False` |
| `contains_make_hard_guard_beats_mask` | `False` |
| `contains_hard_guard_reference_kl_arg` | `False` |
| `contains_hard_guard_target_ce_arg` | `False` |
| `contains_hard_guard_beats_arg` | `False` |
| `help_contains_hard_guard_args` | `False` |
| `contains_torch_save` | `False` |
| `contains_out_checkpoint` | `False` |
| `call_path_uses_train_guardaware` | `False` |
| `call_path_still_uses_imported_train_directly` | `False` |

## Objective v1

- Main train loss still uses CE + pair hinge + worst hinge, but weights are CLI-controlled.
- Hard guard rows can receive:
  - reference KL preservation via `--hard-guard-reference-kl-weight`
  - target CE via `--hard-guard-target-ce-weight`
  - beats-worst hinge via `--hard-guard-beats-weight`
- Existing hard guard evaluator remains active and can return `FAIL_HARD_GUARD_ROW_DAMAGE`.

## Recommended first run

- dataset: `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_guarded_split_v1.json`
- epochs: `1`
- lr: `5e-8`
- ce/pair/worst: `0.5 / 0.5 / 0.25`
- anchor KL: `1.0`
- hard guard KL / CE / beats: `4.0 / 1.0 / 4.0`

## Outputs

- `analysis/integration_eval/rank_topk_nosave_b4c64_guardaware_objective_wrapper_v1/guardaware_objective_wrapper_v1_summary.json`
- `analysis/integration_eval/rank_topk_nosave_b4c64_guardaware_objective_wrapper_v1/wrapper_help_guardaware_v1.txt`
