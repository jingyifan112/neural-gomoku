# v12 interpolation internal gate summary

Purpose:
- Compare v12 interpolation checkpoints after mixing v11 current_best with v12_stage2 repair-specialist checkpoint.

Failure-set results:
- v11: direct_blocks=0/5
- v12_stage2: direct_blocks=5/5
- alpha 0.20: direct_blocks=3/5
- alpha 0.30: direct_blocks=4/5

Internal gate results:

## alpha 0.20
- vs greedy: 10-10, avg_moves=58.00
- vs random: 20-0, avg_moves=22.00
- vs mixed_v5: 20-0, avg_moves=12.50
- vs v10_frozen: 20-0, avg_moves=71.50
- vs current_best/v11: 0-20, avg_moves=89.50

Decision:
- Reject alpha 0.20 because it loses 0-20 against current_best.

## alpha 0.30
- vs greedy: 10-10, avg_moves=58.00
- vs random: 20-0, avg_moves=20.60
- vs mixed_v5: 20-0, avg_moves=9.50
- vs v10_frozen: 10-10, avg_moves=88.00
- vs current_best/v11: 20-0, avg_moves=113.50

Decision:
- alpha 0.30 is the current v12 candidate.
- It improves Rapfi failure-set direct block accuracy to 4/5 and passes most internal gates.
- However, it regresses vs v10_frozen from v11's 20-0 to 10-10.
- Do not promote yet. Run robustness checks before any Rapfi benchmark.
