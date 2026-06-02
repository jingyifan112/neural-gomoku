
## Final evaluation

v10 vs greedy:
- wins=10
- losses=10
- draws=0
- avg_moves=58.00

v10 vs random:
- wins=20
- losses=0
- draws=0
- avg_moves=19.00

v10 vs current_best/mixed_v5:
- wins=20
- losses=0
- draws=0
- avg_moves=25.50

## Decision

Promoted v10.

New current best:
- checkpoints/15x15_current_best.pt
- source checkpoint: checkpoints/15x15_greedy_sparring_v10.pt

Previous current best backed up as:
- checkpoints/15x15_mixed_v5_before_v10.pt

Reason:
v10 improved strongly against greedy, remained perfect against random, and defeated previous current_best/mixed_v5 by 20-0.
