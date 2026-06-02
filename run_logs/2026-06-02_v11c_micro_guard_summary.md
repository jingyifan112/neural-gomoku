# 15x15 v11c micro guard evaluation

Base checkpoint:
- v10 frozen: checkpoints/15x15_v10_frozen.pt

Candidate:
- v11c: checkpoints/15x15_mixed_v11c_micro_guard.pt

v11c result:
- vs v10_frozen: 0-20, avg_moves=45.50
- vs greedy: 10-10, avg_moves=58.00

Decision:
- Do not promote v11c.
- Keep checkpoints/15x15_current_best.pt unchanged as v10.

Interpretation:
- Micro greedy-guard training preserved the greedy baseline.
- However, the candidate still lost all games against v10_frozen.
- Further tuning of greedy_sparring alone is unlikely to produce a stronger v11.
- Next step: run v10-vs-v10 sanity checks, then add a v10 anchor/distillation component if checkpoint-vs-checkpoint evaluation is valid.
