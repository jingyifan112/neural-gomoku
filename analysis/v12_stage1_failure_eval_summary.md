# v12 stage1 Rapfi failure-set evaluation

v12_stage1 was trained from v11 current_best using a small targeted Rapfi failure repair set.

Result:
- v10 direct block accuracy: 0/5
- v11 direct block accuracy: 0/5
- v12_stage1 direct block accuracy: 1/5

Observed improvement:
- v12_stage1 repaired Game 2 move_count 33, changing direct policy to one of the expected blocking moves.
- Value estimates became more negative on several Game 1 forced-line positions.

Limitation:
- v12_stage1 is not sufficient for promotion.
- It still misses 4/5 immediate-block positions.
- Do not run Rapfi or promote this checkpoint yet.

Next step:
- Try a stronger v12_stage2 targeted repair with more epochs / slightly higher learning rate.
