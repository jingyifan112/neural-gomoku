# v12 stage2 internal gate summary

v12_stage2 was trained from v11 current_best using targeted Rapfi failure repair.

Failure-set result:
- v10 direct block accuracy: 0/5
- v11 direct block accuracy: 0/5
- v12_stage1 direct block accuracy: 1/5
- v12_stage2 direct block accuracy: 5/5

Internal gate:
- vs greedy: 10-10, avg_moves=58.00
- vs random: 20-0, avg_moves=21.20
- vs mixed_v5: 20-0, avg_moves=39.50
- vs current_best/v11: 10-10, avg_moves=149.00
- vs v10_frozen: 0-20, avg_moves=68.50

Decision:
- Do not promote v12_stage2.
- Do not run Rapfi benchmark yet.
- Treat v12_stage2 as a repair-specialist checkpoint.
- Next step: interpolate v11 current_best with v12_stage2 and search for a smaller repair strength that preserves internal strength while improving Rapfi failure-set accuracy.
