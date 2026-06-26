# Expanded b6c64 benchmark anchor dry-run

- decision: `BENCHMARK_ANCHOR_DRYRUN_READY`
- no training
- no checkpoint
- no promotion/current_best overwrite

## Purpose

Build a public benchmark anchor plan before any benchmark-preserving repair training. The goal is to preserve the current local b6c64 tactical_mid behavior while applying teacher-divergence repair. The archived 7.0/24 current-best score is tracked separately because the current local runner does not reproduce it.

## Runs

| run | engine | W | L | D | score | score rate | anchors |
|---|---|---:|---:|---:|---:|---:|---:|
| `before_neural_current_best_mcts16` | `neural_current_best_mcts16` | 2 | 22 | 0 | 2.0/24 | 0.083 | 192 |
| `after_expanded_b6c64_mcts16` | `expanded_data_b6c64_mcts16` | 2 | 22 | 0 | 2.0/24 | 0.083 | 192 |

## Anchor counts

| anchor group | count | recommended use |
|---|---:|---|
| before public tactical_mid anchors | 192 | KL preserve old public benchmark behavior |
| after candidate regression anchors | 192 | diagnostic only; do not use as CE target |

## Next training policy

- CE: only teacher-divergence train rows.
- KL anchor: before-model public tactical_mid anchors.
- KL guard: protected/top10 and tail rows.
- current-local public benchmark no-regression gate: `>= 2.0/24` on tactical_mid.
- archived-current-best aspirational target: recover toward `>= 7.0/24` on tactical_mid.

## Artifacts

- source JSON: `analysis/integration_eval/expanded_data_b6c64_benchmark_anchor_dryrun/benchmark_anchor_source.json`
- manifest CSV: `analysis/integration_eval/expanded_data_b6c64_benchmark_anchor_dryrun/benchmark_anchor_manifest.csv`
- summary JSON: `analysis/integration_eval/expanded_data_b6c64_benchmark_anchor_dryrun/benchmark_anchor_dryrun_summary.json`
