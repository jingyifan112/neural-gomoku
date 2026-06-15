# Tactical-mid Preterminal Actionable Evaluation

- checkpoint: `checkpoints/15x15_current_best_margin_g2m13_m15_3pair_b.pt`
- cases: `analysis/public_benchmark_eval/tactical_mid_preterminal_actionable_cases.json`
- total cases: `2`
- interpretation: these are the small actionable subset where a neural prevention move exists.

## Summary

| Metric | Count | Rate |
|---|---:|---:|
| direct selects target prevention | 0/2 | 0.000 |
| policy_safety selects target prevention | 0/2 | 0.000 |
| direct leaves zero opponent double-threat replies | 0/2 | 0.000 |
| policy_safety leaves zero opponent double-threat replies | 0/2 | 0.000 |

## Case details

| Case | Target | Observed | Direct | Safety | Target rank | Observed rank | Direct target | Safety target | Direct reply count | Safety reply count |
|---|---|---|---|---|---:|---:|---|---|---:|---:|
| `tactical_mid_g3_block_4_9_preterminal_back2` | `4,6` | `3,5` | `4,4` | `3,5` | 15 | 16 | False | False | 2 | 1 |
| `tactical_mid_g11_block_7_14_preterminal_back2` | `10,11` | `8,14` | `6,0` | `8,14` | 70 | 81 | False | False | 3 | 1 |
