# 15x15 public benchmark score ladder summary

## Scope

This benchmark uses the Gomocup 2026 freestyle 15x15 public openings ladder:

- 12 public openings
- repeat both colors
- 24 games per pair
- rule 0 / freestyle
- board size 15x15

The purpose of this step was public benchmarking only. No training was run.

## Existing score-table anchors

Completed baseline and anchor comparisons include:

- random
- tactical_lite
- tactical_mid
- tactical_plus
- rapfi_fast_depth1
- rapfi_full
- neural_current_best

Key known scores:

| Pair / anchor | Neural setting | Score |
|---|---:|---:|
| tactical_mid | neural_current_best_mcts16 | 7.0 / 24 |
| tactical_mid | rapfi_full | 24.0 / 24 |
| tactical_plus | neural_current_best_mcts16 | 3.0 / 24 |
| rapfi_fast_depth1 | neural_current_best_mcts32 | 0.0 / 24 |

These results show that neural_current_best is well below rapfi_full and also struggles against stronger tactical/search anchors.

## Public engine expansion attempt

A public Gomocup engine expansion was attempted to add more middle-strength public engines to the same score table.

Candidate tested:

- PentaZen21_20

Local setup result:

- PentaZen21_20 downloaded successfully from GomocupDownload.
- The resolved binary was `pbrain-PentaZen21_20.exe`.
- The binary type was Windows PE32+ x86-64 executable.
- On this macOS machine, running it required Wine.
- Wine Stable was installed through Homebrew, but macOS blocked/killed Wine Stable.
- PentaZen21_20 could not be smoke-tested locally.

Decision:

- Do not include PentaZen21_20 in the main public benchmark score table.
- Reason: local macOS/Wine runtime incompatibility, not an engine or gameplay failure.
- No new score-table row was added from this candidate.

## Conclusion

Public engine expansion was stopped here.

The current benchmark table is already sufficient to support the main conclusion: neural_current_best is not close to rapfi_full on the Gomocup 2026 freestyle 15x15 public-opening ladder. Further public engine expansion may be useful later, but it should not block model-side work.
