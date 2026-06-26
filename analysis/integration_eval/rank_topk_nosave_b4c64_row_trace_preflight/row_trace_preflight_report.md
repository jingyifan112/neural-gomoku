# b4c64/current-best rank/top-k row-level gate trace preflight

## Scope

- Branch: `exp/15x15-rank-topk-nosave-b4c64-row-trace-preflight`
- Preflight only.
- No training, checkpoint save, C export, public benchmark, promotion, or current-best overwrite was performed.

## Why this preflight exists

- Ablation v1 improved train rows but regressed protected/tail gates.
- Group metrics are insufficient to identify which exact rows caused protected/tail failures.
- Next implementation should add per-row before/after trace output, still no-save.

## Wrapper function inventory

| function | lines | args |
|---|---:|---|
| `parse_args` | 28-88 | `[]` |
| `validate_args` | 91-101 | `['args']` |
| `load_model_b4c64_current_best` | 105-128 | `['checkpoint', 'device', 'board_size', 'win_length', 'channels', 'blocks']` |
| `load_protected_dataset` | 131-139 | `['path']` |
| `summarize_delta` | 142-162 | `['before', 'after']` |
| `verdict` | 165-188 | `['group_rows']` |
| `write_csv` | 191-232 | `['path', 'rows']` |
| `write_report` | 235-319 | `['path', 'args', 'data', 'rows', 'history', 'final_verdict']` |
| `main` | 322-414 | `[]` |

## Dataset groups

| group key | rows | sample keys |
|---|---:|---|
| `samples` | 7 | `['before_primary_gap', 'before_primary_suppress_rank', 'before_target_prob', 'before_target_rank', 'before_worst_suppress_gap', 'board', 'board_size', 'case_id', 'current_player', 'effective_sample_weight', 'game_number', 'hardness_weight', 'label_type', 'move_count', 'notes', 'numeric_gap_available', 'numeric_gap_value', 'old_final', 'original_effective_sample_weight', 'primary_suppress_rc', 'protected_objective_role', 'protected_objective_weight_cap', 'sample_weight', 'side_to_move', 'source', 'suggested_bucket', 'suppress_actions_source', 'suppress_candidates', 'suppress_move', 'suppress_rc', 'suppress_rcs', 'suppress_xy', 'target_rc', 'target_xy', 'teacher_eval_before', 'teacher_eval_kind', 'teacher_move', 'validation_notes', 'win_length']` |
| `protected_eval_samples` | 15 | `['before_primary_gap', 'before_primary_suppress_rank', 'before_target_prob', 'before_target_rank', 'before_worst_suppress_gap', 'board', 'board_size', 'case_id', 'current_player', 'effective_sample_weight', 'game_number', 'hardness_weight', 'label_type', 'move_count', 'notes', 'numeric_gap_available', 'numeric_gap_value', 'old_final', 'original_effective_sample_weight', 'primary_suppress_rc', 'protected_objective_role', 'protected_objective_weight_cap', 'sample_weight', 'side_to_move', 'source', 'suggested_bucket', 'suppress_actions_source', 'suppress_candidates', 'suppress_move', 'suppress_rc', 'suppress_rcs', 'suppress_xy', 'target_rc', 'target_xy', 'teacher_eval_before', 'teacher_eval_kind', 'teacher_move', 'validation_notes', 'win_length']` |
| `tail_eval_samples` | 3 | `['before_primary_gap', 'before_primary_suppress_rank', 'before_target_prob', 'before_target_rank', 'before_worst_suppress_gap', 'board', 'board_size', 'case_id', 'current_player', 'effective_sample_weight', 'game_number', 'hardness_weight', 'label_type', 'move_count', 'notes', 'numeric_gap_available', 'numeric_gap_value', 'old_final', 'original_effective_sample_weight', 'primary_suppress_rc', 'protected_objective_role', 'protected_objective_weight_cap', 'sample_weight', 'side_to_move', 'source', 'suggested_bucket', 'suppress_actions_source', 'suppress_candidates', 'suppress_move', 'suppress_rc', 'suppress_rcs', 'suppress_xy', 'target_rc', 'target_xy', 'teacher_eval_before', 'teacher_eval_kind', 'teacher_move', 'validation_notes', 'win_length']` |

## Ablation v1 failure labels

| config | verdict | selection | protected beats-worst Δ | tail rank>50 Δ |
|---|---|---|---:|---:|
| `baseline_lr1e7_anchor035` | `FAIL_B4C64_CURRENT_BEST_SAFE_NO_SAVE_PROBE` | `train_improves_but_gate_regresses` | -1.0 | 1.0 |
| `lowlr_anchor100` | `FAIL_B4C64_CURRENT_BEST_SAFE_NO_SAVE_PROBE` | `train_improves_but_gate_regresses` | -1.0 | 1.0 |
| `pair_focus_lowlr_anchor100` | `FAIL_B4C64_CURRENT_BEST_SAFE_NO_SAVE_PROBE` | `train_improves_but_gate_regresses` | -1.0 | 1.0 |

## Proposed next implementation

- Add `--out-row-csv` to `scripts/probe_policy_rank_topk_protected_nosave_b4c64_current_best.py`.
- Emit one row per dataset row per group with before/after rank, target probability, worst gap, and beats-worst/all flags.
- Re-run only the known failing baseline config first.
- Do not save checkpoint, export C, run public benchmark, promote, or overwrite current-best.

## Outputs

- `analysis/integration_eval/rank_topk_nosave_b4c64_row_trace_preflight/row_trace_preflight_summary.json`
- `analysis/integration_eval/rank_topk_nosave_b4c64_row_trace_preflight/wrapper_relevant_extracts.json`
