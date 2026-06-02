# 15x15 v11 final summary

Current best before v11:
- v10: checkpoints/15x15_v10_frozen.pt
- baseline:
  - vs greedy: 10-10, avg_moves=58.00
  - vs random: 20-0
  - vs mixed_v5: 20-0

Failed attempts:
- v11 stage1 self-play:
  - vs greedy: 0-20
  - vs v10_frozen: 0-20
  - decision: failed, not promoted

- v11b greedy guard:
  - vs greedy: 10-10
  - vs v10_frozen: 0-20
  - decision: failed, not promoted

- v11c micro guard:
  - vs greedy: 10-10
  - vs v10_frozen: 0-20
  - decision: failed, not promoted

Invalid experiment:
- First v11d interpolation was invalid because the supposed failed source checkpoint was later found to be equivalent to v10.

True failed source:
- checkpoints/15x15_v11_true_failed_selfplay.pt
- reproduced behavior:
  - vs greedy: 0-20
  - vs v10_frozen: 0-20

Successful method:
- v11e interpolation between:
  - base: checkpoints/15x15_v10_frozen.pt
  - candidate: checkpoints/15x15_v11_true_failed_selfplay.pt

Best candidates:
- a0.05: checkpoints/15x15_v11e_interp_truefailed_a0.05.pt
- a0.10: checkpoints/15x15_v11e_interp_truefailed_a0.10.pt

Final evaluation:
- a0.05 vs v10_frozen: 20-0
- v10_frozen vs a0.05: 0-20
- a0.05 vs greedy: 10-10
- a0.05 vs random: 20-0, avg_moves=16.60
- a0.05 vs mixed_v5: 20-0, avg_moves=11.50

- a0.10 vs v10_frozen: 20-0
- v10_frozen vs a0.10: 0-20
- a0.10 vs greedy: 10-10
- a0.10 vs random: 20-0, avg_moves=17.70
- a0.10 vs mixed_v5: 20-0, avg_moves=16.50

Head-to-head:
- a0.05 vs a0.10: 10-10, avg_moves=96.00
- a0.10 vs a0.05: 10-10, avg_moves=96.00

Decision:
- Promote a0.05 to v11.
- Reason: a0.05 and a0.10 are equal head-to-head, but a0.05 is more conservative and keeps slightly faster wins against random and mixed_v5.
- checkpoints/15x15_current_best.pt is now updated to v11.
