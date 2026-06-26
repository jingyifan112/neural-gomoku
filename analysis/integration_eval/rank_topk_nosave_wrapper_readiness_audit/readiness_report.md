# Rank/top-k no-save wrapper readiness audit

## Scope

- Branch: `exp/15x15-rank-topk-nosave-wrapper-readiness-audit`
- Read-only readiness audit for the next route after top3-sensitive CE closeout.
- No training, checkpoint save, C export, public benchmark, promotion, or current-best overwrite was performed.

## Script readiness

| script | exists | no-save text | mentions b4c96 | channels arg | init ckpt | reference ckpt |
|---|---:|---:|---:|---:|---:|---:|
| `scripts/probe_policy_rank_topk_protected_nosave_b4c96.py` | True | True | True | True | True | True |
| `scripts/evaluate_policy_rank_topk_gate_b4c96.py` | True | False | True | False | False | False |
| `scripts/train_teacher_divergence_policy_probe.py` | True | True | False | True | False | False |

## Dataset readiness

| path | exists | sample-like count | top keys |
|---|---:|---:|---|
| `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected.json` | True | 25 | `['checkpoint', 'description', 'margin', 'max_suppress', 'name', 'samples', 'skipped', 'source_dataset', 'summary', 'top_k']` |
| `analysis/public_benchmark_eval/rapfi_teacher_policy_multisuppress_dataset_corpus8_selected_protected_train_11_50_weightcap3.json` | True | 7 | `['description', 'name', 'protected_eval_samples', 'samples', 'selection_rule', 'source_dataset', 'summary', 'tail_eval_samples', 'weight_cap']` |
| `analysis/integration_eval/top3_sensitive_tiny_nosave_probe_preflight/primary_positive_ce_dataset.json` | True | 3 | `['metadata', 'samples']` |
| `analysis/integration_eval/top3_sensitive_tiny_nosave_probe_preflight/protected_anchor_gate_dataset.json` | True | 15 | `['metadata', 'samples']` |
| `analysis/integration_eval/top3_sensitive_tiny_nosave_probe_preflight/tail_eval_guard_dataset.json` | True | 3 | `['metadata', 'samples']` |
| `analysis/public_benchmark_eval/corpus8_selected_board_snapshots.json` | True | 32 | `['<list>']` |

## Checkpoint readiness

| path | exists | size |
|---|---:|---:|
| `checkpoints/15x15_current_best.pt` | True | 1684421 |
| `checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt` | True | 1687043 |
| `checkpoints/probes/15x15_capacity_data_pairing_b4c96_probe_candidate.pt` | True | 3199895 |

## Preliminary decision

Existing b4c96 no-save rank/top-k wrapper is useful as a reference, but must be audited before direct use. If it hardcodes b4c96 or candidate/reference semantics, create a b4c64/current-best-safe wrapper instead of reusing it blindly.

## Outputs

- `analysis/integration_eval/rank_topk_nosave_wrapper_readiness_audit/readiness_report.md`
- `analysis/integration_eval/rank_topk_nosave_wrapper_readiness_audit/readiness_summary.json`
- `analysis/integration_eval/rank_topk_nosave_wrapper_readiness_audit/script_extracts.json`
