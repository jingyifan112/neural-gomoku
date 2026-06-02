# 15x15 v11 robustness evaluation

Checkpoint:
- checkpoints/15x15_current_best.pt
- version: v11
- source: v11e interpolation alpha=0.05

Robustness results:

v11 vs v10_frozen:
- seed 2101: 20-0, avg_moves=63.50
- seed 2102: 20-0, avg_moves=63.50
- seed 2103: 20-0, avg_moves=63.50
- seed 2104: 20-0, avg_moves=63.50
- seed 2105: 20-0, avg_moves=63.50

v11 vs greedy:
- seed 2111: 10-10, avg_moves=58.00
- seed 2112: 10-10, avg_moves=58.00
- seed 2113: 10-10, avg_moves=58.00
- seed 2114: 10-10, avg_moves=58.00
- seed 2115: 10-10, avg_moves=58.00

v11 vs random:
- seed 2121: 20-0, avg_moves=18.80
- seed 2122: 20-0, avg_moves=17.80
- seed 2123: 20-0, avg_moves=16.90

v11 vs mixed_v5:
- seed 2131: 20-0, avg_moves=17.50
- seed 2132: 20-0, avg_moves=18.50
- seed 2133: 20-0, avg_moves=11.50

Conclusion:
- v11 is stable across multiple seeds.
- v11 consistently beats v10_frozen 20-0.
- v11 preserves the greedy baseline at 10-10.
- v11 preserves 20-0 performance against random and mixed_v5.
- Next step: external benchmark against stronger engines such as Rapfi / C benchmark.
