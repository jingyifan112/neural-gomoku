# v12 candidate robustness summary

Candidate:
- checkpoints/15x15_v12_candidate.pt
- Source: interpolation alpha=0.30 between v11 current_best and v12_stage2 repair-specialist checkpoint

Failure-set result:
- v11 direct block accuracy: 0/5
- v12_stage2 direct block accuracy: 5/5
- v12_candidate direct block accuracy: 4/5

Robustness results:

vs current_best:
- seed 3401: 20-0, avg_moves=113.50
- seed 3402: 20-0, avg_moves=113.50
- seed 3403: 20-0, avg_moves=113.50

vs greedy:
- seed 3421: 10-10, avg_moves=58.00
- seed 3422: 10-10, avg_moves=58.00
- seed 3423: 10-10, avg_moves=58.00

vs v10_frozen:
- seed 3411: 10-10, avg_moves=88.00
- seed 3412: 10-10, avg_moves=88.00
- seed 3413: 10-10, avg_moves=88.00

Decision:
- v12_candidate passes robustness checks.
- Do not promote yet.
- Next step: export C weights and run Rapfi depth=1 smoke test.
