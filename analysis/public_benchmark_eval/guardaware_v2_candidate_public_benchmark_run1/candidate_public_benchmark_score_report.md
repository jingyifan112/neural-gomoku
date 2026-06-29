# guard-aware v2 candidate public benchmark run1

## Scope

- 15x15 freestyle public benchmark score ladder.
- 24 games per baseline opponent.
- Candidate only; not promotion; current-best not overwritten.

## Score table

| baseline | config | score | W-L-D | score rate | Rapfi full ref | gap vs Rapfi | parse |
|---|---|---:|---:|---:|---:|---:|---|
| `random` | `MCTS32` | 24.0 | 24-0-0 | 1.0 | 24 | 0.0 | `OK` |
| `tactical_lite` | `MCTS32` | 23.0 | 23-1-0 | 0.958 | 24 | -1.0 | `OK` |
| `tactical_mid` | `MCTS16` | 7.0 | 6-16-2 | 0.292 | 24 | -17.0 | `OK` |
| `tactical_plus` | `MCTS16` | 3.0 | 2-20-2 | 0.125 | 24 | -21.0 | `OK` |
| `rapfi_fast_depth1` | `MCTS32` | 0.0 | 0-24-0 | 0.0 | 24 | -24.0 | `OK` |

## Conclusion

- Candidate matches the previous current-best public benchmark score ladder.
- No public benchmark improvement was observed in this run.
- Do not promote based on this score table.

Generated at: `2026-06-29T13:58:10`
