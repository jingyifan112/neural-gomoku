# 15x15 v10-vs-v10 checkpoint sanity check

Purpose:
- Verify whether checkpoint-vs-checkpoint evaluation is reliable before using v10_frozen as a promotion gate.

Results:
- current_best vs v10_frozen: 10-10, avg_moves=55.00
- v10_frozen vs current_best: 10-10, avg_moves=55.00

Conclusion:
- The checkpoint-vs-checkpoint evaluation is valid.
- v11b and v11c losing 0-20 against v10_frozen reflects real regression, not an evaluation artifact.
- v10 remains the current best checkpoint.
- Next step should use a v10 anchor / distillation method instead of more greedy-sparring-only training.
