# 15x15 v11 stage1 mixed self-play evaluation

Base checkpoint:
- v10 frozen: checkpoints/15x15_v10_frozen.pt
- candidate before training: copied from v10

Training:
- command: python -m gomoku_agent.train
- iterations: 3
- games per iteration: 20
- epochs: 1
- board size: 15
- win length: 5
- mcts sims: 64
- allow immediate loss: enabled
- output checkpoint: checkpoints/15x15_mixed_v11_candidate.pt

v10 baseline:
- vs greedy: 10-10, avg_moves=58.00
- vs random: 20-0
- vs previous mixed_v5: 20-0

v11 stage1 evaluation:
- vs greedy: 0-20, avg_moves=9.50
- vs random: 20-0, avg_moves=11.90
- vs mixed_v5: 20-0, avg_moves=13.50
- vs v10_frozen: 0-20, avg_moves=50.50

Decision:
- Do not promote v11 stage1.
- Keep checkpoints/15x15_current_best.pt unchanged as v10.
- Archive failed candidate as checkpoints/15x15_mixed_v11_failed_selfplay_stage1.pt.

Interpretation:
- The candidate preserved strong performance against weak/random-like opponents.
- However, it catastrophically regressed against the greedy win/block baseline.
- The model appears to have shifted toward fast attack patterns and lost the greedy-aware defensive behavior learned by v10.
- Future v11 training should mix self-play with greedy-sparring / teacher samples instead of pure continuation self-play.
