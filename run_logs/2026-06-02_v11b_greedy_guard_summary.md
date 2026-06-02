# 15x15 v11b greedy guard evaluation

Base checkpoint:
- v10 frozen: checkpoints/15x15_v10_frozen.pt

Candidate:
- v11b: checkpoints/15x15_mixed_v11b_greedy_guard.pt

v11 stage1 result:
- vs greedy: 0-20, avg_moves=9.50
- vs v10_frozen: 0-20, avg_moves=50.50
- decision: failed, not promoted

v11b result:
- vs greedy: 10-10, avg_moves=58.00
- vs v10_frozen: 0-20, avg_moves=52.50

Decision:
- Do not promote v11b.
- Keep checkpoints/15x15_current_best.pt unchanged as v10.

Interpretation:
- Greedy-sparring repair restored the greedy baseline from 0-20 back to 10-10.
- However, v11b still lost all games against v10_frozen.
- This means v11b recovered the specific greedy-defense behavior but did not preserve the broader policy strength of v10.
- Further v11 training needs a v10 anchor / distillation component, not only greedy repair.
