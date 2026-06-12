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
| tactical_mid | neural_current_best_mcts16 | 6 | 16 | 2 | 7.0 / 24 | 0.292 |
| tactical_mid | rapfi_full | 24 | 0 | 0 | 24.0 / 24 | 1.000 |
| tactical_plus | neural_current_best_mcts32 | 1 | 23 | 0 | 1.0 / 24 | 0.042 |
| tactical_plus | neural_current_best_mcts16 | 2 | 20 | 2 | 3.0 / 24 | 0.125 |
| tactical_plus | neural_current_best_mcts8 | 0 | 22 | 2 | 1.0 / 24 | 0.042 |
| tactical_plus | rapfi_full | 24 | 0 | 0 | 24.0 / 24 | 1.000 |
| tactical_plus | neural_current_best_mcts32 | 1 | 23 | 0 | 1.0 / 24 | 0.042 |
| tactical_plus | rapfi_full | 24 | 0 | 0 | 24.0 / 24 | 1.000 |
| rapfi_fast_depth1 | neural_current_best_mcts32 | 0 | 24 | 0 | 0.0 / 24 | 0.000 |
| rapfi_fast_depth1 | rapfi_full | 24 | 0 | 0 | 24.0 / 24 | 1.000 |

## Interpretation

The public opening suite is useful, but baseline strength controls the resolution.

- `random` is too weak: both neural and Rapfi score perfectly.
- `tactical_lite` gives minimal resolution: neural drops one game while Rapfi scores perfectly.
- `tactical_plus` is much harder: neural scores only one game and several losses are time forfeits under `mcts32`.
- `rapfi_fast_depth1` is too strong: neural scores zero while Rapfi scores perfectly.

The current neural engine is clearly stronger than random and tactical_lite, but falls sharply against tactical_plus and Rapfi depth-1 on this public opening suite. The next scoring target should be an intermediate baseline between `tactical_lite` and `tactical_plus`, or a speed-adjusted neural setting such as lower MCTS simulations.


## Speed-adjusted tactical_plus result

`neural_current_best_mcts16` improves over `neural_current_best_mcts32` on `tactical_plus`:

- `mcts32`: 1.0 / 24, score rate 0.042
- `mcts16`: 3.0 / 24, score rate 0.125

This indicates that part of the `mcts32` tactical_plus loss comes from time pressure, but the main gap is still tactical strength rather than only search speed.


## MCTS simulation sweep on tactical_plus

| Neural setting | W | L | D | Score | Score rate |
|---|---:|---:|---:|---:|---:|
| mcts32 | 1 | 23 | 0 | 1.0 / 24 | 0.042 |
| mcts16 | 2 | 20 | 2 | 3.0 / 24 | 0.125 |
| mcts8 | 0 | 22 | 2 | 1.0 / 24 | 0.042 |

`mcts16` is the best speed-quality tradeoff in this tactical_plus benchmark. `mcts8` confirms that lowering simulations too far loses search quality, while `mcts32` suffers from time pressure.


## Tactical-mid result

`tactical_mid` is the best current main benchmark for model iteration.

| Engine | W | L | D | Score | Score rate |
|---|---:|---:|---:|---:|---:|
| neural_current_best_mcts16 | 6 | 16 | 2 | 7.0 / 24 | 0.292 |
| rapfi_full | 24 | 0 | 0 | 24.0 / 24 | 1.000 |

This baseline sits between `tactical_lite` and `tactical_plus`. It gives enough resolution to track neural model improvements without saturating at either 0% or 100%.
