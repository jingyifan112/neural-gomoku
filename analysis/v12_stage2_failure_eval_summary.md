# v12 stage2 Rapfi failure-set evaluation

v12_stage2 was trained from v11 current_best using targeted Rapfi failure repair data.

Failure-set direct block accuracy:
- v10: 0/5
- v11: 0/5
- v12_stage1: 1/5
- v12_stage2: 5/5

Value calibration:
- v11 avg value on 7 failure positions: -0.2741
- v12_stage1 avg value: -0.3142
- v12_stage2 avg value: -0.8949

Key improvement:
- v12_stage2 learned to select blocking moves for all five immediate-threat positions in the Rapfi failure set.
- It also assigns strongly negative values to forced-loss / double-threat positions.

Caution:
- Direct policy probabilities are very high, often near 0.999.
- This suggests possible overfitting to the small 7-position repair set.
- v12_stage2 must pass internal gates before any Rapfi benchmark or promotion.

Decision:
- Do not promote v12_stage2 yet.
- Next step: run internal evaluations against greedy, random, mixed_v5, v10_frozen, and current_best/v11.
