# b4c64 hard guard BN / mode semantics audit

## Scope

- Audit only.
- No checkpoint save, C export, public benchmark, promotion, or current-best overwrite was performed.

## Summary

- `max_abs_train_minus_eval_target_prob_delta`: `0.026625797152519226`
- `max_abs_policy_head_training_minus_eval_target_prob_delta`: `0.0`
- `any_train_rank_differs_from_eval`: `True`
- `any_policy_head_training_rank_differs_from_eval`: `False`

## Mode compare

| case_id | compare | rank eval→mode | target prob eval→mode | target logit delta | worst gap delta |
|---|---|---:|---:|---:|---:|
| `legacy_g1_m40` | `train_minus_eval` | 3→3 | 0.15029124915599823→0.17691704630851746 | -0.628382682800293 | 0.2109537124633789 |
| `legacy_g1_m8` | `train_minus_eval` | 102→73 | 0.00018429456395097077→0.0003218080091755837 | 0.38509368896484375 | 0.5218038558959961 |
| `legacy_g1_m40` | `policy_head_training_mode_minus_eval` | 3→3 | 0.15029124915599823→0.15029124915599823 | 0.0 | 0.0 |
| `legacy_g1_m8` | `policy_head_training_mode_minus_eval` | 102→102 | 0.00018429456395097077→0.00018429456395097077 | 0.0 | 0.0 |

## Module mode rows

| mode | module | class | training |
|---|---|---|---:|
| `eval` | `stem.1` | `BatchNorm2d` | `False` |
| `eval` | `tower.0.bn1` | `BatchNorm2d` | `False` |
| `eval` | `tower.0.bn2` | `BatchNorm2d` | `False` |
| `eval` | `tower.1.bn1` | `BatchNorm2d` | `False` |
| `eval` | `tower.1.bn2` | `BatchNorm2d` | `False` |
| `eval` | `tower.2.bn1` | `BatchNorm2d` | `False` |
| `eval` | `tower.2.bn2` | `BatchNorm2d` | `False` |
| `eval` | `tower.3.bn1` | `BatchNorm2d` | `False` |
| `eval` | `tower.3.bn2` | `BatchNorm2d` | `False` |
| `eval` | `policy` | `Sequential` | `False` |
| `eval` | `policy.0` | `Conv2d` | `False` |
| `eval` | `policy.1` | `BatchNorm2d` | `False` |
| `eval` | `policy.2` | `ReLU` | `False` |
| `eval` | `policy.3` | `Flatten` | `False` |
| `eval` | `policy.4` | `Linear` | `False` |
| `eval` | `value_conv.1` | `BatchNorm2d` | `False` |
| `train` | `stem.1` | `BatchNorm2d` | `True` |
| `train` | `tower.0.bn1` | `BatchNorm2d` | `True` |
| `train` | `tower.0.bn2` | `BatchNorm2d` | `True` |
| `train` | `tower.1.bn1` | `BatchNorm2d` | `True` |
| `train` | `tower.1.bn2` | `BatchNorm2d` | `True` |
| `train` | `tower.2.bn1` | `BatchNorm2d` | `True` |
| `train` | `tower.2.bn2` | `BatchNorm2d` | `True` |
| `train` | `tower.3.bn1` | `BatchNorm2d` | `True` |
| `train` | `tower.3.bn2` | `BatchNorm2d` | `True` |
| `train` | `policy` | `Sequential` | `True` |
| `train` | `policy.0` | `Conv2d` | `True` |
| `train` | `policy.1` | `BatchNorm2d` | `True` |
| `train` | `policy.2` | `ReLU` | `True` |
| `train` | `policy.3` | `Flatten` | `True` |
| `train` | `policy.4` | `Linear` | `True` |
| `train` | `value_conv.1` | `BatchNorm2d` | `True` |
| `policy_head_training_mode` | `stem.1` | `BatchNorm2d` | `False` |
| `policy_head_training_mode` | `tower.0.bn1` | `BatchNorm2d` | `False` |
| `policy_head_training_mode` | `tower.0.bn2` | `BatchNorm2d` | `False` |
| `policy_head_training_mode` | `tower.1.bn1` | `BatchNorm2d` | `False` |
| `policy_head_training_mode` | `tower.1.bn2` | `BatchNorm2d` | `False` |
| `policy_head_training_mode` | `tower.2.bn1` | `BatchNorm2d` | `False` |
| `policy_head_training_mode` | `tower.2.bn2` | `BatchNorm2d` | `False` |
| `policy_head_training_mode` | `tower.3.bn1` | `BatchNorm2d` | `False` |
| `policy_head_training_mode` | `tower.3.bn2` | `BatchNorm2d` | `False` |
| `policy_head_training_mode` | `policy` | `Sequential` | `False` |
| `policy_head_training_mode` | `policy.0` | `Conv2d` | `False` |
| `policy_head_training_mode` | `policy.1` | `BatchNorm2d` | `False` |
| `policy_head_training_mode` | `policy.2` | `ReLU` | `False` |
| `policy_head_training_mode` | `policy.3` | `Flatten` | `False` |
| `policy_head_training_mode` | `policy.4` | `Linear` | `False` |
| `policy_head_training_mode` | `value_conv.1` | `BatchNorm2d` | `False` |

## Decision

- Output semantics differ across eval/train modes for hard guard rows.
- Next patch should keep non-policy modules in eval mode during policy-head-only optimization and diagnostics.

## Outputs

- `analysis/integration_eval/rank_topk_nosave_b4c64_bn_mode_semantics_audit/audit.log`
- `analysis/integration_eval/rank_topk_nosave_b4c64_bn_mode_semantics_audit/bn_mode_compare.csv`
- `analysis/integration_eval/rank_topk_nosave_b4c64_bn_mode_semantics_audit/bn_mode_modules.csv`
- `analysis/integration_eval/rank_topk_nosave_b4c64_bn_mode_semantics_audit/bn_mode_outputs.csv`
- `analysis/integration_eval/rank_topk_nosave_b4c64_bn_mode_semantics_audit/bn_mode_semantics_report.md`
- `analysis/integration_eval/rank_topk_nosave_b4c64_bn_mode_semantics_audit/bn_mode_semantics_summary.json`
