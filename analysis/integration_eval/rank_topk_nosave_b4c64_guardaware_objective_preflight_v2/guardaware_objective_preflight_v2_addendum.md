# guard-aware objective preflight v2 addendum

## Purpose

The initial v2 run identified that the wrapper delegates training to `scripts/train_rapfi_teacher_policy_rank_topk_probe.py`, but the next patch needs the true loss helper body as well.

## Source

- `scripts/train_rapfi_teacher_policy_rank_topk_probe.py`

## Extracted functions

| function | lines | args | extract |
|---|---:|---|---|
| `make_multisuppress_tensors` | 92-144 | `['samples', 'device']` | `analysis/integration_eval/rank_topk_nosave_b4c64_guardaware_objective_preflight_v2/train_rapfi_teacher_policy_rank_topk_probe__make_multisuppress_tensors__L92_144.txt` |
| `compute_loss_terms` | 147-197 | `['model', 'reference_model', 'tensors', 'anchor_tensors', 'ref_anchor_probs', 'args']` | `analysis/integration_eval/rank_topk_nosave_b4c64_guardaware_objective_preflight_v2/train_rapfi_teacher_policy_rank_topk_probe__compute_loss_terms__L147_197.txt` |
| `assert_finite_terms` | 200-207 | `['terms', 'label']` | `analysis/integration_eval/rank_topk_nosave_b4c64_guardaware_objective_preflight_v2/train_rapfi_teacher_policy_rank_topk_probe__assert_finite_terms__L200_207.txt` |
| `diagnose_summary` | 211-265 | `['model', 'samples', 'device']` | `analysis/integration_eval/rank_topk_nosave_b4c64_guardaware_objective_preflight_v2/train_rapfi_teacher_policy_rank_topk_probe__diagnose_summary__L211_265.txt` |
| `train` | 268-322 | `['model', 'reference_model', 'tensors', 'anchor_tensors', 'args']` | `analysis/integration_eval/rank_topk_nosave_b4c64_guardaware_objective_preflight_v2/train_rapfi_teacher_policy_rank_topk_probe__train__L268_322.txt` |

## Missing wanted functions

- `['configure_policy_head_trainable', 'make_anchor_tensors', 'masked_log_softmax', 'masked_softmax', 'rank_of_action', 'set_policy_head_training_mode']`

## Patch implication

- The guard-aware objective patch should not modify an unrelated trainer.
- It should either create a wrapper-local `train_guardaware(...)` copied from the imported rank/top-k training path, or patch the wrapper to call a new local loss path.
- Required loss patch point is `compute_loss_terms(...)`, not just `train(...)`.
