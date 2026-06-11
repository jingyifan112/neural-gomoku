# Gomocup Public Opening Score Ladder

## Setup

- Opening suite: Gomocup freestyle 15x15 public openings
- Opening count: 12
- Match mode: `-repeat`, so each opening is played with both color assignments
- Games per engine/baseline pair: 24
- Rule: freestyle Gomoku, rule 0
- Board size: 15
- Neural engine: `neural_current_best_mcts32`
- Reference engine: `rapfi_full`

## Results

| Baseline | Engine | W | L | D | Score | Score rate |
|---|---|---:|---:|---:|---:|---:|
| random | neural_current_best_mcts32 | 24 | 0 | 0 | 24.0 / 24 | 1.000 |
| random | rapfi_full | 24 | 0 | 0 | 24.0 / 24 | 1.000 |
| tactical_lite | neural_current_best_mcts32 | 23 | 1 | 0 | 23.0 / 24 | 0.958 |
| tactical_lite | rapfi_full | 24 | 0 | 0 | 24.0 / 24 | 1.000 |
| rapfi_fast_depth1 | neural_current_best_mcts32 | 0 | 24 | 0 | 0.0 / 24 | 0.000 |
| rapfi_fast_depth1 | rapfi_full | 24 | 0 | 0 | 24.0 / 24 | 1.000 |

## Interpretation

The public opening suite is useful, but baseline strength controls the resolution.

- `random` is too weak: both neural and Rapfi score perfectly.
- `tactical_lite` gives minimal resolution: neural drops one game while Rapfi scores perfectly.
- `rapfi_fast_depth1` is too strong: neural scores zero while Rapfi scores perfectly.

The current neural engine is clearly stronger than random and tactical_lite, but far below Rapfi depth-1 on this public opening suite. The next scoring target should be an intermediate baseline between `tactical_lite` and `rapfi_fast_depth1`.
