# Next step: 15x15 greedy sparring v9

Current best:
- 15x15_current_best.pt
- copied from 15x15_mixed_v5.pt

Reason for v9:
- v8 slightly improved greedy survival from avg_moves=22.50 to avg_moves=24.50.
- But v8 still lost 0W / 0D / 6L to greedy_win_block.
- v8 also lost 0W / 0D / 6L to current_best/v5.
- Therefore v8 should not replace v5.

Planned v9:
- Start from 15x15_current_best.pt.
- Let model play full games against greedy_win_block.
- Collect full trajectory samples from model turns.
- Use teacher targets that include immediate win, immediate block, and avoiding moves that create opponent immediate wins.
- Train on full greedy sparring trajectories.
- Evaluate:
  - v9 vs greedy_win_block
  - v9 vs random
  - v9 vs current_best/v5

Do this when Colab GPU is available again.
