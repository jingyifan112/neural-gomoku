# v12 interpolation failure-set summary

Goal:
- Mix v11 current_best with v12_stage2 repair-specialist checkpoint.
- Search for a checkpoint that preserves internal strength while improving Rapfi failure-set direct block accuracy.

Failure-set results:
- v11: direct_blocks=0/5, avg_value=-0.2741
- v12_stage2: direct_blocks=5/5, avg_value=-0.8949
- alpha 0.05: direct_blocks=0/5, avg_value=-0.3193
- alpha 0.10: direct_blocks=0/5, avg_value=-0.3677
- alpha 0.20: direct_blocks=3/5, avg_value=-0.4667
- alpha 0.30: direct_blocks=4/5, avg_value=-0.5592

Decision:
- Do not test alpha 0.05 or 0.10 further.
- Test alpha 0.20 and alpha 0.30 on internal gates.
- Do not run Rapfi until a candidate passes internal gates.
