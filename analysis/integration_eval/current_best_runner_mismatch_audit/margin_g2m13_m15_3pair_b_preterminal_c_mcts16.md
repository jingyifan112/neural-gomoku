# Tactical-mid Preterminal Actionable C Engine Evaluation

- engine: `c_inference/pbrain-neural-gomoku`
- weights: `weights/15x15_current_best_margin_g2m13_m15_3pair_b_weights.bin`
- move mode: `mcts_safe`
- mcts sims: `16`
- cases: `analysis/public_benchmark_eval/tactical_mid_preterminal_actionable_cases.json`
- total cases: `2`

## Summary

| Metric | Count | Rate |
|---|---:|---:|
| C policy_safety selects target prevention | 0/2 | 0.000 |
| C final selects target prevention | 0/2 | 0.000 |
| C policy_safety leaves zero opponent double-threat replies | 0/2 | 0.000 |
| C final leaves zero opponent double-threat replies | 0/2 | 0.000 |

## Case details

| Case | Target | Observed | C direct | C safety | C mcts_raw | C mcts_safety | C final | Final target | Final reply count | Safety reply count |
|---|---|---|---|---|---|---|---|---|---:|---:|
| `tactical_mid_g3_block_4_9_preterminal_back2` | `4,6` | `3,5` | `4,4` | `3,5` | `3,5` | `3,5` | `3,5` | False | 1 | 1 |
| `tactical_mid_g11_block_7_14_preterminal_back2` | `10,11` | `8,14` | `6,0` | `8,14` | `8,14` | `8,14` | `8,14` | False | 1 | 1 |
