# Gomocup Public Opening Score: current_best vs Rapfi

## Setup

- Opening suite: Gomocup public freestyle 15x15 openings
- Opening count: 12
- Match mode: repeat openings, so both engines play both colors
- Total games per tested engine: 24
- Rule: freestyle Gomoku, rule 0
- Board size: 15
- Baseline opponent: `rapfi_fast_depth1`
- Neural engine: `neural_current_best_mcts32`
- Rapfi reference: `rapfi_full`

## Results

| Engine | Opponent | W | L | D | Score | Score rate |
|---|---|---:|---:|---:|---:|---:|
| neural_current_best_mcts32 | rapfi_fast_depth1 | 0 | 24 | 0 | 0.0 / 24 | 0.000 |
| rapfi_full | rapfi_fast_depth1 | 24 | 0 | 0 | 24.0 / 24 | 1.000 |

## Gap

`rapfi_full_score - neural_current_best_score = 24.0 - 0.0 = 24.0 points`

## Interpretation

This public opening benchmark is valid as a shared match-score comparison, but it is saturated:
`rapfi_full` scores perfectly against the baseline, while `neural_current_best_mcts32` scores zero.

The result shows a large strength gap, but it does not provide fine-grained resolution for neural model progress. For future measurement, use an easier baseline than `rapfi_fast_depth1`, lower Rapfi strength further if possible, or add weaker public engines/random-greedy baselines to avoid a floor result.
