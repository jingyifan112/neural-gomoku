# b4c64/current-best guard-aware objective preflight v2

## Scope

- Branch: `exp/15x15-rank-topk-nosave-b4c64-guardaware-objective-preflight-v2`
- Corrective source-map/preflight only.
- No training, checkpoint save, C export, public benchmark, promotion, or current-best overwrite was performed.

## Why v2

- The v1 preflight assumed `train()` was defined inside the wrapper.
- The wrapper source-map indicates the training/loss logic is imported or delegated.
- This v2 resolves imports and extracts the actual candidate training helper definitions before patching objective loss.

## Wrapper local functions

| function | lines | args |
|---|---:|---|
| `_stable_json` | 184-189 | `['value']` |
| `_trace_float` | 351-358 | `['row', 'key']` |
| `apply_hard_guard_verdict` | 456-462 | `['base_verdict', 'hard_guard_rows']` |
| `diagnose_row_trace` | 192-230 | `['model', 'groups', 'device']` |
| `evaluate_hard_guards` | 361-453 | `['data', 'row_trace_rows']` |
| `load_model_b4c64_current_best` | 123-146 | `['checkpoint', 'device', 'board_size', 'win_length', 'channels', 'blocks']` |
| `load_protected_dataset` | 149-157 | `['path']` |
| `main` | 676-781 | `[]` |
| `parse_args` | 28-106 | `[]` |
| `summarize_delta` | 160-180 | `['before', 'after']` |
| `summarize_row_trace_delta` | 233-293 | `['before_rows', 'after_rows']` |
| `validate_args` | 109-119 | `['args']` |
| `verdict` | 501-524 | `['group_rows']` |
| `write_csv` | 527-568 | `['path', 'rows']` |
| `write_hard_guard_csv` | 465-497 | `['path', 'rows']` |
| `write_report` | 571-673 | `['path', 'args', 'data', 'rows', 'history', 'final_verdict', 'hard_guard_rows']` |
| `write_row_csv` | 296-346 | `['path', 'rows']` |

## Resolved imports

| line | module | names | resolved files |
|---:|---|---|---|
| 6 | `__future__` | `['annotations']` | `[]` |
| 8 | `argparse` | `argparse` | `[]` |
| 9 | `csv` | `csv` | `[]` |
| 10 | `json` | `json` | `[]` |
| 11 | `pathlib` | `['Path']` | `[]` |
| 12 | `typing` | `['Any']` | `[]` |
| 14 | `numpy` | `np` | `[]` |
| 15 | `torch` | `torch` | `[]` |
| 17 | `gomoku_agent.checkpoint` | `['load_compatible_checkpoint']` | `['src/gomoku_agent/checkpoint.py']` |
| 18 | `gomoku_agent.model` | `['PolicyValueNet']` | `['src/gomoku_agent/model.py']` |
| 19 | `train_rapfi_teacher_policy_rank_topk_probe` | `['load_anchor_samples', 'make_anchor_tensors', 'make_multisuppress_tensors', 'diagnose_summary', 'train']` | `['scripts/train_rapfi_teacher_policy_rank_topk_probe.py']` |

## Extracted helper functions

| function | source | lines | extract | args |
|---|---|---:|---|---|
| `load_compatible_checkpoint` | `src/gomoku_agent/checkpoint.py` | 11-39 | `analysis/integration_eval/rank_topk_nosave_b4c64_guardaware_objective_preflight_v2/checkpoint__load_compatible_checkpoint__L11_39.txt` | `['model', 'checkpoint', 'device', 'board_size', 'channels', 'blocks']` |
| `make_multisuppress_tensors` | `scripts/train_rapfi_teacher_policy_rank_topk_probe.py` | 92-144 | `analysis/integration_eval/rank_topk_nosave_b4c64_guardaware_objective_preflight_v2/train_rapfi_teacher_policy_rank_topk_probe__make_multisuppress_tensors__L92_144.txt` | `['samples', 'device']` |
| `diagnose_summary` | `scripts/train_rapfi_teacher_policy_rank_topk_probe.py` | 211-265 | `analysis/integration_eval/rank_topk_nosave_b4c64_guardaware_objective_preflight_v2/train_rapfi_teacher_policy_rank_topk_probe__diagnose_summary__L211_265.txt` | `['model', 'samples', 'device']` |
| `train` | `scripts/train_rapfi_teacher_policy_rank_topk_probe.py` | 268-322 | `analysis/integration_eval/rank_topk_nosave_b4c64_guardaware_objective_preflight_v2/train_rapfi_teacher_policy_rank_topk_probe__train__L268_322.txt` | `['model', 'reference_model', 'tensors', 'anchor_tensors', 'args']` |
| `train` | `scripts/train_teacher_divergence_policy_probe.py` | 665-808 | `analysis/integration_eval/rank_topk_nosave_b4c64_guardaware_objective_preflight_v2/train_teacher_divergence_policy_probe__train__L665_808.txt` | `['args']` |
| `train` | `scripts/train_teacher_divergence_policy_mixed_ce_anchor_probe.py` | 704-972 | `analysis/integration_eval/rank_topk_nosave_b4c64_guardaware_objective_preflight_v2/train_teacher_divergence_policy_mixed_ce_anchor_probe__train__L704_972.txt` | `['args']` |
| `train` | `scripts/train_rapfi_teacher_policy_rank_topk_b4c96_probe.py` | 451-505 | `analysis/integration_eval/rank_topk_nosave_b4c64_guardaware_objective_preflight_v2/train_rapfi_teacher_policy_rank_topk_b4c96_probe__train__L451_505.txt` | `['model', 'reference_model', 'tensors', 'anchor_tensors', 'args']` |
| `train` | `scripts/train_teacher_divergence_policy_anchor_probe.py` | 676-837 | `analysis/integration_eval/rank_topk_nosave_b4c64_guardaware_objective_preflight_v2/train_teacher_divergence_policy_anchor_probe__train__L676_837.txt` | `['args']` |
| `train` | `scripts/train_v12l_margin_repair.py` | 279-332 | `analysis/integration_eval/rank_topk_nosave_b4c64_guardaware_objective_preflight_v2/train_v12l_margin_repair__train__L279_332.txt` | `['model', 'reference_model', 'margin_tensors', 'anchor_tensors', 'args']` |
| `train` | `scripts/train_candidate_g_teacher_policy.py` | 189-265 | `analysis/integration_eval/rank_topk_nosave_b4c64_guardaware_objective_preflight_v2/train_candidate_g_teacher_policy__train__L189_265.txt` | `['args']` |
| `train` | `scripts/train_candidate_h_value_ranking.py` | 196-283 | `analysis/integration_eval/rank_topk_nosave_b4c64_guardaware_objective_preflight_v2/train_candidate_h_value_ranking__train__L196_283.txt` | `['args']` |
| `train` | `scripts/train_rapfi_teacher_policy_margin.py` | 253-310 | `analysis/integration_eval/rank_topk_nosave_b4c64_guardaware_objective_preflight_v2/train_rapfi_teacher_policy_margin__train__L253_310.txt` | `['model', 'reference_model', 'margin_tensors', 'anchor_tensors', 'args']` |
| `train` | `scripts/train_candidate_g_policy_first_dry_run.py` | 522-597 | `analysis/integration_eval/rank_topk_nosave_b4c64_guardaware_objective_preflight_v2/train_candidate_g_policy_first_dry_run__train__L522_597.txt` | `['model', 'base_model', 'samples', 'args', 'device']` |

## Decision

- Do not patch guard-aware objective until the actual `train()` helper source is reviewed.
- Next patch should modify the true training helper or create a copied no-save wrapper-local training function.
- Keep hard guard evaluator intact.

## Outputs

- `analysis/integration_eval/rank_topk_nosave_b4c64_guardaware_objective_preflight_v2/checkpoint__load_compatible_checkpoint__L11_39.txt`
- `analysis/integration_eval/rank_topk_nosave_b4c64_guardaware_objective_preflight_v2/guardaware_objective_preflight_v2_summary.json`
- `analysis/integration_eval/rank_topk_nosave_b4c64_guardaware_objective_preflight_v2/train_candidate_g_policy_first_dry_run__train__L522_597.txt`
- `analysis/integration_eval/rank_topk_nosave_b4c64_guardaware_objective_preflight_v2/train_candidate_g_teacher_policy__train__L189_265.txt`
- `analysis/integration_eval/rank_topk_nosave_b4c64_guardaware_objective_preflight_v2/train_candidate_h_value_ranking__train__L196_283.txt`
- `analysis/integration_eval/rank_topk_nosave_b4c64_guardaware_objective_preflight_v2/train_rapfi_teacher_policy_margin__train__L253_310.txt`
- `analysis/integration_eval/rank_topk_nosave_b4c64_guardaware_objective_preflight_v2/train_rapfi_teacher_policy_rank_topk_b4c96_probe__train__L451_505.txt`
- `analysis/integration_eval/rank_topk_nosave_b4c64_guardaware_objective_preflight_v2/train_rapfi_teacher_policy_rank_topk_probe__diagnose_summary__L211_265.txt`
- `analysis/integration_eval/rank_topk_nosave_b4c64_guardaware_objective_preflight_v2/train_rapfi_teacher_policy_rank_topk_probe__make_multisuppress_tensors__L92_144.txt`
- `analysis/integration_eval/rank_topk_nosave_b4c64_guardaware_objective_preflight_v2/train_rapfi_teacher_policy_rank_topk_probe__train__L268_322.txt`
- `analysis/integration_eval/rank_topk_nosave_b4c64_guardaware_objective_preflight_v2/train_teacher_divergence_policy_anchor_probe__train__L676_837.txt`
- `analysis/integration_eval/rank_topk_nosave_b4c64_guardaware_objective_preflight_v2/train_teacher_divergence_policy_mixed_ce_anchor_probe__train__L704_972.txt`
- `analysis/integration_eval/rank_topk_nosave_b4c64_guardaware_objective_preflight_v2/train_teacher_divergence_policy_probe__train__L665_808.txt`
- `analysis/integration_eval/rank_topk_nosave_b4c64_guardaware_objective_preflight_v2/train_v12l_margin_repair__train__L279_332.txt`
