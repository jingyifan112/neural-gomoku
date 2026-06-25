# Teacher-divergence next conservative no-save probe summary

## Scope

- No-save probe only.
- No checkpoint save.
- No C export, no public benchmark, no promotion.

## Inputs

- dataset: `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_conservative_selection_next.json`
- wrapper: `scripts/probe_policy_rank_topk_protected_nosave_b4c96.py`
- consumer audit: `analysis/integration_eval/teacher_divergence_next_consumer_audit/consumer_schema_audit_summary.json`
- init/reference checkpoint: `checkpoints/probes/15x15_capacity_data_pairing_b4c96_probe_candidate.pt`

## Variant

| variant | epochs | lr | ce | pair | worst | anchor_kl | wrapper verdict | directional decision |
|---|---:|---:|---:|---:|---:|---:|---|---|
| conservative_selection_next | 3 | 1e-6 | 1.0 | 0.5 | 0.3 | 1.0 | FAIL_B4C96_SAFE_NO_SAVE_PROBE | CONSERVATIVE_NOSAVE_PROBE_FAILED_GUARDS |

## Group metrics

| group | top5 Δ | top10 Δ | rank>50 Δ | mean_rank Δ | target_prob Δ | worst_gap Δ | hinge Δ |
|---|---:|---:|---:|---:|---:|---:|---:|
| train_main_rank_11_50 | 0.000000 | 1.000000 | 0.000000 | -4.000000 | 0.00547780 | 0.504478 | -0.366303 |
| protected_eval_top10 | -1.000000 | 2.000000 | 0.000000 | -0.666667 | -0.01182741 | 0.919337 | -0.121074 |
| tail_eval_rank_gt50 | 0.000000 | -1.000000 | 2.000000 | 24.666667 | -0.00585572 | -1.021226 | 1.291925 |

## Guard interpretation

- protected_safe: `False`
- tail_safe: `False`
- train_not_worse_tail: `True`

The conservative dataset did not avoid the key protected/tail guard failures.

Do not proceed to checkpoint-producing training. Return to data expansion or row-level review.

## Final note

This summary records no-save behavior only and does not authorize checkpoint save, C export, public benchmark, promotion, or current_best overwrite.
